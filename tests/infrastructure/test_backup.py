"""Testes para o serviço de backup."""

import zipfile
from pathlib import Path

import pytest

from controle_obras.infrastructure.backup import BackupService
from controle_obras.infrastructure.database import DatabaseManager
from controle_obras.infrastructure.storage import AppStorage


@pytest.fixture
def temp_app(tmp_path: Path):
    storage = AppStorage(tmp_path)
    db = DatabaseManager(storage.db_path())
    db.init_schema()
    service = BackupService(storage, db)
    return storage, db, service


def test_gerar_backup_cria_zip_com_estrutura_correta(temp_app):
    storage, db, service = temp_app

    caminho_zip = service.gerar_backup(
        nome_empresa="Empresa Teste",
        versao_sistema="1.0.0",
        quantidade_obras=2,
        quantidade_anexos=3,
    )

    assert caminho_zip.exists()

    with zipfile.ZipFile(caminho_zip, "r") as zf:
        arquivos = zf.namelist()
        assert "manifest.json" in arquivos
        assert "database/app.db" in arquivos


def test_manifest_contem_metadados_esperados(temp_app):
    storage, db, service = temp_app

    caminho_zip = service.gerar_backup(
        nome_empresa="Empresa Teste",
        versao_sistema="1.0.0",
        quantidade_obras=5,
        quantidade_anexos=10,
    )

    with zipfile.ZipFile(caminho_zip, "r") as zf:
        import json

        manifest = json.loads(zf.read("manifest.json"))

    assert manifest["app_version"] == "1.0.0"
    assert manifest["company_name"] == "Empresa Teste"
    assert manifest["total_obras"] == 5
    assert manifest["total_attachments"] == 10
    assert manifest["hash_database"]
    assert "metadata/backup_info.json" in zf.namelist()


def test_restaurar_backup_recupera_estado(temp_app):
    storage, db, service = temp_app

    # Cria uma tabela simples para validar restauração
    with db.get_connection() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS validacao (id INTEGER PRIMARY KEY)")
        conn.execute("INSERT INTO validacao (id) VALUES (1)")

    caminho_zip = service.gerar_backup(
        nome_empresa="Empresa Teste",
        versao_sistema="1.0.0",
        quantidade_obras=1,
        quantidade_anexos=0,
    )

    db.close_all()
    manifest = service.restaurar_backup(caminho_zip)
    assert manifest["company_name"] == "Empresa Teste"

    with db.get_connection() as conn:
        row = conn.execute("SELECT id FROM validacao").fetchone()
        assert row["id"] == 1
