"""Testes para o serviço de backup."""

import json
import zipfile
from datetime import datetime
from pathlib import Path

import pytest

from controle_obras.infrastructure.backup import (
    BackupService,
    RestoreValidationError,
)
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


def test_restaurar_backup_com_empresa_e_logo(temp_app):
    """Regressão: _verificar_logos quebrava com empresa cadastrada (TypeError)."""
    storage, db, service = temp_app
    with db.get_connection() as conn:
        conn.execute("INSERT INTO empresa (razao_social) VALUES ('Empresa Logo')")
        conn.execute(
            "UPDATE empresa SET logo_path='C:/nao/mais/existe/logo.png'"
        )
        conn.commit()
    storage.logos_dir.mkdir(parents=True, exist_ok=True)
    (storage.logos_dir / "logo_empresa.png").write_bytes(b"logo")

    caminho_zip = service.gerar_backup(
        nome_empresa="Empresa Logo",
        versao_sistema="1.0.0",
        quantidade_obras=1,
        quantidade_anexos=0,
    )

    db.close_all()
    manifest = service.restaurar_backup(caminho_zip)
    assert manifest["company_name"] == "Empresa Logo"

    with db.get_connection() as conn:
        row = conn.execute("SELECT logo_path FROM empresa LIMIT 1").fetchone()
    assert "logo_empresa.png" in row["logo_path"]


def test_auto_backup_diario_cria_diretorio_se_inexistente(temp_app):
    """Regressão: FileNotFoundError quando data/backups não existia."""
    storage, db, service = temp_app
    backup_dir = storage.base_dir / "data" / "backups"
    assert not backup_dir.exists()

    caminho = service.auto_backup_diario("Empresa", "1.0.0", 0, 0)
    assert caminho is not None
    assert backup_dir.exists()
    assert caminho.exists()


def test_auto_backup_diario_ignora_backup_seguranca(temp_app):
    """Regressão: backup de segurança do dia não vale como backup diário."""
    storage, db, service = temp_app
    backup_dir = storage.base_dir / "data" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    hoje = datetime.now().strftime("%Y-%m-%d")
    (backup_dir / f"backup_seguranca_antes_restore_{hoje}_10-00-00.zip").write_bytes(b"x")

    caminho = service.auto_backup_diario("Empresa", "1.0.0", 0, 0)
    assert caminho is not None
    assert caminho.exists()


def test_auto_backup_diario_pula_quando_ja_existe_de_hoje(temp_app):
    storage, db, service = temp_app
    backup_dir = storage.base_dir / "data" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    hoje = datetime.now().strftime("%Y-%m-%d")
    (backup_dir / f"backup_{hoje}_10-00-00.zip").write_bytes(b"x")

    assert service.auto_backup_diario("Empresa", "1.0.0", 0, 0) is None


def test_restore_rejeita_banco_adulterado_antes_de_alterar_dados(temp_app, tmp_path):
    """Regressão: hash do banco validado antes de substituir o sistema."""
    storage, db, service = temp_app
    with db.get_connection() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS validacao (id INTEGER PRIMARY KEY)")
        conn.execute("INSERT INTO validacao (id) VALUES (1)")
        conn.commit()

    caminho_zip = service.gerar_backup(
        nome_empresa="Empresa",
        versao_sistema="1.0.0",
        quantidade_obras=0,
        quantidade_anexos=0,
        destino=tmp_path / "backups",
    )

    novo_zip = tmp_path / "backups" / "adulterado.zip"
    with zipfile.ZipFile(caminho_zip) as zin, zipfile.ZipFile(novo_zip, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "database/app.db":
                data = b"conteudo falsificado, nao e um sqlite valido"
            zout.writestr(item, data)

    db.close_all()
    with pytest.raises(RestoreValidationError, match="hash"):
        service.restaurar_backup(novo_zip)

    with db.get_connection() as conn:
        row = conn.execute("SELECT id FROM validacao").fetchone()
        assert row["id"] == 1


def test_gerar_backup_nao_sobrescreve_arquivo_existente(temp_app, tmp_path):
    """Regressão: dois backups no mesmo segundo não se sobrescrevem."""
    storage, db, service = temp_app
    destino = tmp_path / "backups"
    destino.mkdir(parents=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    (destino / f"backup_{timestamp}.zip").write_bytes(b"ocupado")
    (destino / f"backup_{timestamp}_2.zip").write_bytes(b"ocupado")

    caminho = service.gerar_backup(
        nome_empresa="Empresa",
        versao_sistema="1.0.0",
        quantidade_obras=0,
        quantidade_anexos=0,
        destino=destino,
    )
    assert caminho.exists()
    assert caminho.name != f"backup_{timestamp}.zip"
    assert caminho.name != f"backup_{timestamp}_2.zip"
