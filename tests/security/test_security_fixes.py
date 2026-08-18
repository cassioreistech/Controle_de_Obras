"""Testes de segurança para os fixes aplicados no Security Review.

Cobre:
1. Zip Slip: rejeita backup com membros path traversal (../)
2. Zip Slip: rejeita backup com membros de caminho absoluto
3. Path traversal em obra_codigo: sanitiza codigo ao montar caminho de anexo
"""

import json
import zipfile
from datetime import datetime
from pathlib import Path

import pytest

from controle_obras.infrastructure.backup import BackupService, RestoreValidationError
from controle_obras.infrastructure.database import DatabaseManager
from controle_obras.infrastructure.storage import AppStorage


@pytest.fixture
def temp_app(tmp_path: Path):
    storage = AppStorage(tmp_path)
    db = DatabaseManager(storage.db_path())
    db.init_schema()
    service = BackupService(storage, db)
    return storage, db, service


def _zip_com_manifesto_malicioso(caminho: Path, membro_malicioso: str) -> Path:
    """Cria um zip de backup com estrutura valida mas um membro malicioso."""
    caminho_zip = caminho / "malicioso.zip"

    manifest = {
        "backup_version": "1.0",
        "app_version": "1.0.0",
        "generated_at": datetime.now().isoformat(),
        "database_file": "app.db",
        "attachments_root": "storage/anexos",
        "company_name": "Teste",
        "total_obras": 0,
        "total_attachments": 0,
    }

    with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("database/app.db", "fake-db-content")
        zf.writestr("storage/anexos/", "")
        zf.writestr(membro_malicioso, "conteudo malicioso")

    return caminho_zip


class TestZipSlipProtection:
    """Valida que a restauracao rejeita zips com path traversal."""

    def test_rejeita_membro_com_dot_dot(self, temp_app, tmp_path: Path):
        storage, db, service = temp_app

        malicioso = _zip_com_manifesto_malicioso(
            tmp_path, "../../escape.txt"
        )

        with pytest.raises(RestoreValidationError, match="path traversal"):
            service.restaurar_backup(malicioso)

    def test_rejeita_membro_com_backslash_traversal(self, temp_app, tmp_path: Path):
        storage, db, service = temp_app

        malicioso = _zip_com_manifesto_malicioso(
            tmp_path, "..\\..\\escape.txt"
        )

        with pytest.raises(RestoreValidationError, match="path traversal"):
            service.restaurar_backup(malicioso)

    def test_rejeita_membro_com_caminho_absoluto(self, temp_app, tmp_path: Path):
        storage, db, service = temp_app

        malicioso = _zip_com_manifesto_malicioso(
            tmp_path, "/etc/passwd"
        )

        with pytest.raises(RestoreValidationError, match="absoluto"):
            service.restaurar_backup(malicioso)

    def test_aceita_backup_legitimo(self, temp_app, tmp_path: Path):
        storage, db, service = temp_app

        caminho_zip = service.gerar_backup(
            nome_empresa="Empresa Teste",
            versao_sistema="1.0.0",
            quantidade_obras=0,
            quantidade_anexos=0,
            destino=tmp_path / "backups",
        )

        db.close_all()
        manifest = service.restaurar_backup(caminho_zip)
        assert manifest["company_name"] == "Empresa Teste"


class TestPathTraversalObraCodigo:
    """Valida que o codigo da obra nao pode escapar do diretorio."""

    def test_codigo_com_traversal_e_sanitizado(self, temp_app):
        storage, db, service = temp_app

        relativo = storage.anexo_relative_path(
            obra_codigo="../../../../Windows",
            lancamento_id=None,
            original_name="arquivo.pdf",
        )

        assert ".." not in relativo
        assert "/Windows/" not in relativo

    def test_codigo_com_backslash_e_sanitizado(self, temp_app):
        storage, db, service = temp_app

        relativo = storage.anexo_relative_path(
            obra_codigo="..\\..\\Windows",
            lancamento_id=5,
            original_name="arquivo.pdf",
        )

        assert ".." not in relativo

    def test_codigo_vazio_usa_fallback(self, temp_app):
        storage, db, service = temp_app

        relativo = storage.anexo_relative_path(
            obra_codigo="../../",
            lancamento_id=None,
            original_name="arquivo.pdf",
        )

        assert "SEM_CODIGO" in relativo

    def test_codigo_normal_mantido(self, temp_app):
        storage, db, service = temp_app

        relativo = storage.anexo_relative_path(
            obra_codigo="OBRA-001",
            lancamento_id=None,
            original_name="arquivo.pdf",
        )

        assert "OBRA_OBRA-001" in relativo

    def test_nome_arquivo_com_traversal_sanitizado(self, temp_app):
        storage, db, service = temp_app

        relativo = storage.anexo_relative_path(
            obra_codigo="OBRA-001",
            lancamento_id=None,
            original_name="../../../../etc/passwd",
        )

        assert ".." not in relativo
        # Nome deve ser apenas o basename do arquivo
        assert relativo.endswith("passwd") or relativo.endswith("_passwd")
