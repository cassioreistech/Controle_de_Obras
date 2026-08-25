"""Módulo de backup e restauração completo do sistema."""

import json
import logging
import shutil
import sqlite3
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from controle_obras.infrastructure.database import DatabaseManager
from controle_obras.infrastructure.storage import AppStorage, FileHasher

logger = logging.getLogger(__name__)

BACKUP_VERSION = "1.0"
REQUIRED_PATHS = ["manifest.json", "database/app.db", "storage/anexos/"]


class BackupError(Exception):
    """Erro durante operação de backup ou restauração."""


class RestoreValidationError(BackupError):
    """Erro de validação durante restauração."""


class BackupService:
    """Serviço de backup completo: banco + anexos + relatórios + manifesto."""

    def __init__(self, storage: AppStorage, db: DatabaseManager) -> None:
        self.storage = storage
        self.db = db

    def gerar_backup(
        self,
        nome_empresa: str,
        versao_sistema: str,
        quantidade_obras: int,
        quantidade_anexos: int,
        destino: Path | str | None = None,
    ) -> Path:
        """Gera um arquivo ZIP com backup completo do sistema."""
        logger.info("Iniciando geração de backup completo.")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nome_arquivo = f"backup_{timestamp}.zip"
        if destino is None:
            destino = self.storage.base_dir / "data" / "backups"
        destino_path = Path(destino)
        destino_path.mkdir(parents=True, exist_ok=True)
        caminho_zip = destino_path / nome_arquivo

        try:
            with tempfile.TemporaryDirectory(prefix="controle_obras_backup_") as tmp:
                tmp_path = Path(tmp)
                db_dir = tmp_path / "database"
                storage_dir = tmp_path / "storage" / "anexos"
                reports_dir = tmp_path / "reports" / "obras"
                metadata_dir = tmp_path / "metadata"

                db_dir.mkdir(parents=True)
                storage_dir.mkdir(parents=True)
                reports_dir.mkdir(parents=True)
                metadata_dir.mkdir(parents=True)

                db_backup_path = db_dir / "app.db"
                self._backup_database(db_backup_path)

                storage_dir.mkdir(parents=True, exist_ok=True)
                if self.storage.anexos_dir.exists():
                    shutil.copytree(
                        self.storage.anexos_dir,
                        storage_dir,
                        dirs_exist_ok=True,
                    )

                logos_dir_backup = tmp_path / "storage" / "logos"
                logos_dir_backup.mkdir(parents=True, exist_ok=True)
                if self.storage.logos_dir.exists():
                    shutil.copytree(
                        self.storage.logos_dir,
                        logos_dir_backup,
                        dirs_exist_ok=True,
                    )

                if self.storage.obras_reports_dir.exists():
                    shutil.copytree(
                        self.storage.obras_reports_dir,
                        reports_dir,
                        dirs_exist_ok=True,
                    )

                manifest = self._gerar_manifest(
                    timestamp=timestamp,
                    versao_sistema=versao_sistema,
                    nome_empresa=nome_empresa,
                    quantidade_obras=quantidade_obras,
                    quantidade_anexos=quantidade_anexos,
                    db_path=db_backup_path,
                )
                manifest_path = tmp_path / "manifest.json"
                manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

                backup_info = {
                    "gerado_em": timestamp,
                    "versao_backup": BACKUP_VERSION,
                    "versao_app": versao_sistema,
                    "origem": str(self.storage.base_dir.resolve()),
                }
                (metadata_dir / "backup_info.json").write_text(
                    json.dumps(backup_info, indent=2, ensure_ascii=False)
                )

                with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                    for diretorio in tmp_path.rglob("*"):
                        if diretorio.is_dir():
                            arcname = diretorio.relative_to(tmp_path).as_posix() + "/"
                            zf.writestr(arcname, "")
                    for arquivo in tmp_path.rglob("*"):
                        if arquivo.is_file():
                            arcname = arquivo.relative_to(tmp_path).as_posix()
                            zf.write(arquivo, arcname)

            if not caminho_zip.exists():
                raise BackupError("Arquivo de backup não foi criado.")

            logger.info("Backup concluído: %s", caminho_zip)
            return caminho_zip
        except Exception as exc:
            logger.exception("Falha ao gerar backup.")
            raise BackupError(f"Falha ao gerar backup: {exc}") from exc

    def _backup_database(self, destino: Path) -> None:
        """Cria cópia consistente do SQLite usando a Backup API."""
        source = sqlite3.connect(str(self.db.db_path))
        target = sqlite3.connect(str(destino))
        try:
            with target:
                source.backup(target)
        finally:
            target.close()
            source.close()

    def _gerar_manifest(
        self,
        timestamp: str,
        versao_sistema: str,
        nome_empresa: str,
        quantidade_obras: int,
        quantidade_anexos: int,
        db_path: Path,
    ) -> dict[str, Any]:
        manifest: dict[str, Any] = {
            "backup_version": BACKUP_VERSION,
            "app_version": versao_sistema,
            "generated_at": timestamp,
            "company_name": nome_empresa,
            "database_file": "database/app.db",
            "attachments_root": "storage/anexos/",
            "reports_root": "reports/obras/",
            "total_obras": quantidade_obras,
            "total_attachments": quantidade_anexos,
            "hash_database": FileHasher.sha256_file(db_path),
            "notes": "Backup completo gerado pelo Controle de Obras",
        }
        return manifest

    def restaurar_backup(
        self,
        caminho_zip: Path | str,
        criar_backup_seguranca: bool = True,
    ) -> dict[str, Any]:
        """Restaura o sistema a partir de um arquivo ZIP de backup."""
        caminho_zip = Path(caminho_zip)
        if not caminho_zip.exists():
            raise BackupError(f"Arquivo de backup não encontrado: {caminho_zip}")

        logger.info("Iniciando restauração de backup: %s", caminho_zip)

        with zipfile.ZipFile(caminho_zip, "r") as zf:
            self._validar_estrutura_pacote(zf)
            self._validar_membros_seguros(zf)
            manifest = json.loads(zf.read("manifest.json"))
            self._validar_manifesto(manifest)

            if criar_backup_seguranca:
                seguranca = self._criar_backup_seguranca()
                logger.info("Backup de segurança criado: %s", seguranca)

            self._fechar_conexoes_sqlite()

            with tempfile.TemporaryDirectory(prefix="controle_obras_restore_") as tmp:
                tmp_path = Path(tmp)
                zf.extractall(tmp_path)

                db_backup = tmp_path / "database" / "app.db"
                self._restaurar_database(db_backup)

                storage_backup = tmp_path / "storage" / "anexos"
                if storage_backup.exists():
                    if self.storage.anexos_dir.exists():
                        shutil.rmtree(self.storage.anexos_dir)
                    shutil.copytree(storage_backup, self.storage.anexos_dir)

                reports_backup = tmp_path / "reports" / "obras"
                if reports_backup.exists():
                    if self.storage.obras_reports_dir.exists():
                        shutil.rmtree(self.storage.obras_reports_dir)
                    shutil.copytree(reports_backup, self.storage.obras_reports_dir)

                logos_backup = tmp_path / "storage" / "logos"
                if logos_backup.exists():
                    if self.storage.logos_dir.exists():
                        shutil.rmtree(self.storage.logos_dir)
                    shutil.copytree(logos_backup, self.storage.logos_dir)

                # Verificar se logo_path no DB aponta para arquivo antigo; se sim, atualizar
                self._verificar_logos()

                self._validar_pos_restauracao()

        logger.info("Restauração concluída com sucesso.")
        return manifest

    def _validar_estrutura_pacote(self, zf: zipfile.ZipFile) -> None:
        arquivos = zf.namelist()
        for required in REQUIRED_PATHS:
            if not any(name.startswith(required) or name == required for name in arquivos):
                raise RestoreValidationError(f"Backup inválido: '{required}' não encontrado.")

    def _validar_membros_seguros(self, zf: zipfile.ZipFile) -> None:
        """Rejeita membros com path traversal (zip slip).

        Impede que um backup malicioso com membros do tipo '../../algo'
        ou caminhos absolutos escreva fora do diretório de extração.
        """
        for name in zf.namelist():
            normalized = name.replace("\\", "/")
            if normalized.startswith("/"):
                raise RestoreValidationError(
                    f"Backup inválido: membro com caminho absoluto: {name}"
                )
            if ".." in normalized.split("/"):
                raise RestoreValidationError(
                    f"Backup inválido: membro com path traversal: {name}"
                )

    def _validar_manifesto(self, manifest: dict[str, Any]) -> None:
        campos_obrigatorios = [
            "backup_version",
            "app_version",
            "generated_at",
            "database_file",
            "attachments_root",
        ]
        for campo in campos_obrigatorios:
            if campo not in manifest:
                raise RestoreValidationError(f"Manifesto inválido: campo '{campo}' ausente.")

        if manifest.get("backup_version") != BACKUP_VERSION:
            versao = manifest.get("backup_version")
            logger.warning("Versão de backup diferente: %s (esperado: %s)", versao, BACKUP_VERSION)

    def _fechar_conexoes_sqlite(self) -> None:
        """Fecha conexões ativas com o banco antes da restauração."""
        logger.info("Fechando conexões SQLite ativas.")
        self.db.close_all()

    def _restaurar_database(self, origem: Path) -> None:
        """Restaura o banco a partir de uma cópia consistente."""
        destino = self.db.db_path
        destino.parent.mkdir(parents=True, exist_ok=True)

        # Remove banco atual e arquivos de runtime
        for suffix in ["", "-wal", "-shm"]:
            arquivo = destino.with_name(destino.name + suffix)
            if arquivo.exists():
                arquivo.unlink()
                logger.info("Removido arquivo de banco: %s", arquivo)

        source = sqlite3.connect(str(origem))
        target = sqlite3.connect(str(destino))
        try:
            with target:
                source.backup(target)
        finally:
            target.close()
            source.close()

    def _validar_pos_restauracao(self) -> None:
        """Executa validações mínimas após a restauração."""
        logger.info("Executando validações pós-restauração.")

        if not self.db.db_path.exists():
            raise RestoreValidationError("Banco de dados não encontrado após restauração.")

        self._verificar_logos()

        conn = sqlite3.connect(str(self.db.db_path))
        try:
            conn.execute("PRAGMA foreign_keys = ON")
            tabelas_esperadas = {
                "empresa",
                "obras",
                "aditivos",
                "tipos_lancamento",
                "lancamentos",
                "anexos",
                "configuracoes",
            }
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tabelas_encontradas = {row[0] for row in cursor.fetchall()}
            faltantes = tabelas_esperadas - tabelas_encontradas
            if faltantes:
                raise RestoreValidationError(
                    f"Tabelas principais ausentes no banco restaurado: {faltantes}"
                )

            conn.execute("SELECT COUNT(*) FROM obras").fetchone()
        finally:
            conn.close()

        if not self.storage.anexos_dir.exists():
            logger.warning("Diretório de anexos não encontrado após restauração.")

        logger.info("Validações pós-restauração concluídas.")

    def _verificar_logos(self) -> None:
        """Atualiza logo_path no DB caso aponte para origem antiga."""
        import os
        conn = sqlite3.connect(str(self.db.db_path))
        try:
            row = conn.execute("SELECT id, logo_path FROM empresa LIMIT 1").fetchone()
            if row and row["logo_path"]:
                old_path = row["logo_path"]
                # Se o arquivo não existe mais, tenta encontrar no logos_dir
                if old_path and not os.path.exists(old_path):
                    import glob
                    matches = glob.glob(str(self.storage.logos_dir / "logo*"))
                    if matches:
                        new_path = matches[0]
                        conn.execute(
                            "UPDATE empresa SET logo_path=? WHERE id=?",
                            (new_path, row["id"]),
                        )
                        conn.commit()
                        logger.info("Logo atualizado para: %s", new_path)
        finally:
            conn.close()

    def _criar_backup_seguranca(self) -> Path:
        """Cria backup automático do estado atual antes de restaurar."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        seguranca_dir = self.storage.base_dir / "data" / "backups"
        seguranca_dir.mkdir(parents=True, exist_ok=True)
        caminho = seguranca_dir / f"backup_seguranca_antes_restore_{timestamp}.zip"

        self._fechar_conexoes_sqlite()

        with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as zf:
            if self.db.db_path.exists():
                zf.write(self.db.db_path, "database/app.db")
            if self.storage.anexos_dir.exists():
                for arquivo in self.storage.anexos_dir.rglob("*"):
                    if arquivo.is_file():
                        arcname = "storage/anexos/" + arquivo.relative_to(
                            self.storage.anexos_dir
                        ).as_posix()
                        zf.write(arquivo, arcname)
            if self.storage.obras_reports_dir.exists():
                for arquivo in self.storage.obras_reports_dir.rglob("*"):
                    if arquivo.is_file():
                        arcname = "reports/obras/" + arquivo.relative_to(
                            self.storage.obras_reports_dir
                        ).as_posix()
                        zf.write(arquivo, arcname)

        return caminho
