"""Gerenciamento de diretórios e caminhos internos do sistema."""

import hashlib
import os
from pathlib import Path


class AppStorage:
    """Centraliza os caminhos internos usados pelo sistema.

    Os dados ficam em um diretório seguro do usuário (Windows: %APPDATA%),
    imune a permissões, sincronização em nuvem e instalação em Program Files.
    """

    def __init__(self, base_dir: Path | str | None = None) -> None:
        self.base_dir = Path(self._resolve_base_dir(base_dir)).resolve()
        self.data_dir = self.base_dir / "data"
        self.storage_dir = self.base_dir / "storage"
        self.anexos_dir = self.storage_dir / "anexos"
        self.reports_dir = self.base_dir / "reports"
        self.obras_reports_dir = self.reports_dir / "obras"
        self.logos_dir = self.storage_dir / "logos"

        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for directory in (
            self.data_dir,
            self.storage_dir,
            self.anexos_dir,
            self.obras_reports_dir,
            self.logos_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _resolve_base_dir(base_dir: Path | str | None) -> Path | str:
        """Resolve o diretório-base dos dados.

        Ordem de prioridade:
        1. ``base_dir`` explícito (testes/uso programático)
        2. Env ``CONTROLE_OBRAS_DATA_DIR`` (override de desenvolvimento)
        3. Windows: ``%APPDATA%\\ControleDeObras`` (distribuição segura)
        4. Fallback: diretório de trabalho ``.`` (Linux/CI/dev)
        """
        if base_dir is not None:
            return base_dir

        override = os.environ.get("CONTROLE_OBRAS_DATA_DIR")
        if override:
            return override

        if os.name == "nt":
            appdata = os.environ.get("APPDATA")
            if appdata:
                return Path(appdata) / "ControleDeObras"

        return Path(".")

    def db_path(self) -> Path:
        return self.data_dir / "app.db"

    def anexo_path(self, obra_codigo: str, relative_path: str) -> Path:
        return self.anexos_dir / relative_path

    def relatorio_path(self, filename: str) -> Path:
        return self.obras_reports_dir / filename

    def anexo_relative_path(
        self, obra_codigo: str, lancamento_id: int | None, original_name: str
    ) -> str:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_original = Path(original_name).name
        # Sanitiza o código da obra para impedir path traversal
        safe_codigo = "".join(
            c for c in obra_codigo if c.isalnum() or c in "._-"
        ).strip(".")
        if not safe_codigo:
            safe_codigo = "SEM_CODIGO"
        if lancamento_id:
            relative = f"OBRA_{safe_codigo}/lancamentos/LANC_{lancamento_id:04d}/{timestamp}_{safe_original}"
        else:
            relative = f"OBRA_{safe_codigo}/obra/{timestamp}_{safe_original}"
        return relative


class FileHasher:
    """Utilitário para calcular hash de arquivos."""

    @staticmethod
    def sha256_file(path: Path) -> str:
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def sha256_bytes(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
