"""Testes para o serviço de backup."""

import json
import tempfile
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


def test_restore_rejeita_versao_de_backup_incompativel(temp_app, tmp_path):
    """Regressão: versão antiga do backup gera erro claro, não warning silencioso."""
    storage, db, service = temp_app
    caminho = service.gerar_backup(
        nome_empresa="Empresa",
        versao_sistema="1.0.0",
        quantidade_obras=0,
        quantidade_anexos=0,
        destino=tmp_path / "backups",
    )
    alterado = tmp_path / "backups" / "versao_antiga.zip"
    with zipfile.ZipFile(caminho) as zin, zipfile.ZipFile(alterado, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "manifest.json":
                manifest = json.loads(data)
                manifest["backup_version"] = "1.0"
                data = json.dumps(manifest).encode("utf-8")
            zout.writestr(item, data)

    with pytest.raises(RestoreValidationError, match="incompat"):
        service.restaurar_backup(alterado)


def test_restore_falha_reverte_do_backup_seguranca(temp_app, monkeypatch):
    """Regressão: falha durante a restauração reverte banco/anexos ao estado anterior."""
    import shutil

    import controle_obras.infrastructure.backup as backup_mod

    storage, db, service = temp_app

    with db.get_connection() as conn:
        conn.execute("CREATE TABLE marcador_original (id INTEGER PRIMARY KEY)")
        conn.execute("INSERT INTO marcador_original (id) VALUES (7)")
        conn.commit()
    storage.anexos_dir.mkdir(parents=True, exist_ok=True)
    (storage.anexos_dir / "original.txt").write_text("dado original")

    caminho_zip = service.gerar_backup(
        nome_empresa="Empresa",
        versao_sistema="1.0.0",
        quantidade_obras=0,
        quantidade_anexos=1,
    )
    db.close_all()

    with db.get_connection() as conn:
        conn.execute("DROP TABLE marcador_original")
        conn.commit()
    (storage.anexos_dir / "original.txt").unlink()
    (storage.anexos_dir / "novo.txt").write_text("dado novo")

    real_copytree = shutil.copytree
    chamadas = {"n": 0}

    def copytree_com_falha_primeira(src, dst, **kwargs):
        chamadas["n"] += 1
        if chamadas["n"] == 1:
            raise OSError("falha simulada de disco")
        return real_copytree(src, dst, **kwargs)

    monkeypatch.setattr(backup_mod.shutil, "copytree", copytree_com_falha_primeira)

    with pytest.raises(OSError, match="falha simulada"):
        service.restaurar_backup(caminho_zip)

    with db.get_connection() as conn:
        tabelas = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    assert "marcador_original" not in tabelas


def test_backup_seguranca_usa_copia_consistente(temp_app):
    """Regressão: backup de segurança contém um SQLite válido e legível."""
    import sqlite3 as _sqlite3

    storage, db, service = temp_app
    with db.get_connection() as conn:
        conn.execute("CREATE TABLE dados_op (id INTEGER PRIMARY KEY, v TEXT)")
        conn.execute("INSERT INTO dados_op (id, v) VALUES (1, 'x')")
        conn.commit()
    db.close_all()

    seguranca = service._criar_backup_seguranca()
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp) / "seguro.db"
        with zipfile.ZipFile(seguranca, "r") as zf:
            assert "database/app.db" in zf.namelist()
            destino.write_bytes(zf.read("database/app.db"))
        conn = _sqlite3.connect(str(destino))
        try:
            row = conn.execute("SELECT v FROM dados_op WHERE id=1").fetchone()
            assert row[0] == "x"
        finally:
            conn.close()


# ============================================================
# Testes: manifesto expandido + verificação de anexos
# ============================================================


def test_manifest_contem_total_anexo_files_e_hash(temp_app):
    """Manifesto deve incluir total_anexo_files e anexo_integrity_hash."""
    storage, db, service = temp_app
    storage.anexos_dir.mkdir(parents=True, exist_ok=True)
    (storage.anexos_dir / "arq1.pdf").write_bytes(b"pdf-fake")
    (storage.anexos_dir / "arq2.jpg").write_bytes(b"jpg-fake")

    caminho_zip = service.gerar_backup(
        nome_empresa="Empresa", versao_sistema="1.0.0",
        quantidade_obras=0, quantidade_anexos=2,
    )
    with zipfile.ZipFile(caminho_zip, "r") as zf:
        manifest = json.loads(zf.read("manifest.json"))

    assert manifest["total_anexo_files"] == 2
    assert isinstance(manifest["anexo_integrity_hash"], str)
    assert len(manifest["anexo_integrity_hash"]) == 32


def test_manifest_hash_anexos_deterministico(temp_app):
    """Mesmos arquivos devem gerar o mesmo hash, independentemente da ordem."""
    storage, db, service = temp_app
    storage.anexos_dir.mkdir(parents=True, exist_ok=True)
    (storage.anexos_dir / "a.pdf").write_bytes(b"conteudo-a")
    (storage.anexos_dir / "b.jpg").write_bytes(b"conteudo-b")

    h1 = service._calcular_hash_anexos(storage.anexos_dir)
    h2 = service._calcular_hash_anexos(storage.anexos_dir)
    assert h1 == h2
    assert h1[0] == 2  # 2 arquivos


def test_manifest_hash_anexos_sem_diretorio(temp_app):
    """Se não há anexos, hash deve ser vazio e total 0."""
    storage, db, service = temp_app
    total, h = service._calcular_hash_anexos()
    assert total == 0
    assert h == ""


def test_backup_zip_contem_todos_os_anexos_do_disco(temp_app):
    """ZIP de backup deve conter todos os arquivos de storage/anexos/."""
    storage, db, service = temp_app
    storage.anexos_dir.mkdir(parents=True, exist_ok=True)
    (storage.anexos_dir / "doc1.pdf").write_bytes(b"pdf")
    sub = storage.anexos_dir / "OBRA_X" / "lancamentos" / "LANC_0001"
    sub.mkdir(parents=True)
    (sub / "comprovante.jpg").write_bytes(b"jpg")

    caminho_zip = service.gerar_backup(
        nome_empresa="E", versao_sistema="1.0.0",
        quantidade_obras=0, quantidade_anexos=2,
    )
    with zipfile.ZipFile(caminho_zip, "r") as zf:
        nomes = set(zf.namelist())
        assert "storage/anexos/doc1.pdf" in nomes
        assert "storage/anexos/OBRA_X/lancamentos/LANC_0001/comprovante.jpg" in nomes


def test_validar_anexos_pos_restauracao_ok(temp_app):
    """Após restore, se todos os anexos existem no disco, não há warning."""
    storage, db, service = temp_app
    storage.anexos_dir.mkdir(parents=True, exist_ok=True)
    (storage.anexos_dir / "nota.pdf").write_bytes(b"pdf")

    with db.get_connection() as conn:
        conn.execute(
            "INSERT INTO obras (codigo, nome, valor_contratado_inicial) VALUES ('T1', 'Teste', 0)"
        )
        conn.execute(
            "INSERT INTO anexos (obra_id, tipo_anexo, nome_original, nome_armazenado, "
            "caminho_relativo, hash_arquivo, tamanho_bytes) VALUES (1, 'Nota Fiscal', "
            "'nota.pdf', 'nota.pdf', 'nota.pdf', '', 3)"
        )
        conn.commit()

    service._validar_anexos_pos_restauracao()


def test_auditar_anexos_tudo_ok(temp_app):
    """auditar_anexos() com banco e disco consistentes retorna zero problemas."""
    from controle_obras.infrastructure.storage import FileHasher

    storage, db, service = temp_app
    storage.anexos_dir.mkdir(parents=True, exist_ok=True)
    (storage.anexos_dir / "foto.jpg").write_bytes(b"jpg-conteudo")
    hash_real = FileHasher.sha256_file(storage.anexos_dir / "foto.jpg")

    with db.get_connection() as conn:
        conn.execute(
            "INSERT INTO obras (codigo, nome, valor_contratado_inicial) VALUES ('T1', 'Teste', 0)"
        )
        conn.execute(
            "INSERT INTO anexos (obra_id, tipo_anexo, nome_original, nome_armazenado, "
            "caminho_relativo, hash_arquivo, tamanho_bytes) VALUES (1, 'Comprovante', "
            "'foto.jpg', 'foto.jpg', 'foto.jpg', ?, 13)",
            (hash_real,),
        )
        conn.commit()

    resultado = service.auditar_anexos()
    assert resultado["total_banco"] == 1
    assert resultado["total_disco"] == 1
    assert resultado["faltando_no_disco"] == []
    assert resultado["orfaos_no_disco"] == []
    assert resultado["hash_mismatches"] == []


def test_auditar_anexos_detecta_faltando_no_disco(temp_app):
    """Registro no banco sem arquivo no disco deve aparecer em faltando_no_disco."""
    storage, db, service = temp_app
    storage.anexos_dir.mkdir(parents=True, exist_ok=True)

    with db.get_connection() as conn:
        conn.execute(
            "INSERT INTO obras (codigo, nome, valor_contratado_inicial) VALUES ('T1', 'Teste', 0)"
        )
        conn.execute(
            "INSERT INTO anexos (obra_id, tipo_anexo, nome_original, nome_armazenado, "
            "caminho_relativo, hash_arquivo, tamanho_bytes) VALUES (1, 'NF', "
            "'fantasma.pdf', 'fantasma.pdf', 'fantasma.pdf', '', 0)"
        )
        conn.commit()

    resultado = service.auditar_anexos()
    assert resultado["total_banco"] == 1
    assert resultado["total_disco"] == 0
    assert len(resultado["faltando_no_disco"]) == 1
    assert resultado["faltando_no_disco"][0]["caminho"] == "fantasma.pdf"


def test_auditar_anexos_detecta_orfaos_no_disco(temp_app):
    """Arquivo no disco sem registro no banco deve aparecer em orfaos_no_disco."""
    storage, db, service = temp_app
    storage.anexos_dir.mkdir(parents=True, exist_ok=True)
    (storage.anexos_dir / "solitario.pdf").write_bytes(b"pdf")

    resultado = service.auditar_anexos()
    assert resultado["total_banco"] == 0
    assert resultado["total_disco"] == 1
    assert "solitario.pdf" in resultado["orfaos_no_disco"]


def test_auditar_anexos_detecta_hash_mismatch(temp_app):
    """Hash do banco diferente do hash do arquivo deve aparecer em hash_mismatches."""
    from controle_obras.infrastructure.storage import FileHasher

    storage, db, service = temp_app
    storage.anexos_dir.mkdir(parents=True, exist_ok=True)
    (storage.anexos_dir / "alterado.pdf").write_bytes(b"conteudo-original")
    hash_original = FileHasher.sha256_file(storage.anexos_dir / "alterado.pdf")

    with db.get_connection() as conn:
        conn.execute(
            "INSERT INTO obras (codigo, nome, valor_contratado_inicial) VALUES ('T1', 'Teste', 0)"
        )
        conn.execute(
            "INSERT INTO anexos (obra_id, tipo_anexo, nome_original, nome_armazenado, "
            "caminho_relativo, hash_arquivo, tamanho_bytes) VALUES (1, 'NF', "
            "'alterado.pdf', 'alterado.pdf', 'alterado.pdf', ?, 18)",
            (hash_original,),
        )
        conn.commit()

    (storage.anexos_dir / "alterado.pdf").write_bytes(b"conteudo-ALTERADO")

    resultado = service.auditar_anexos()
    assert len(resultado["hash_mismatches"]) == 1
    assert resultado["hash_mismatches"][0]["caminho"] == "alterado.pdf"
    assert resultado["hash_mismatches"][0]["hash_banco"] == hash_original
    assert resultado["hash_mismatches"][0]["hash_disco"] != hash_original
