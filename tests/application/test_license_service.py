"""Testes do servico de licenciamento (trial + chave HMAC)."""

from datetime import date, timedelta

from controle_obras.application.license_service import (
    CHAVE_LICENCA,
    CHAVE_PRIMEIRO_USO,
    TRIAL_DIAS,
    LicencaService,
    gerar_chave,
    validar_chave,
)
from controle_obras.domain.models import Configuracao


def test_gerar_chave_roundtrip():
    validade = date(2026, 12, 31)
    chave = gerar_chave(validade)
    assert len(chave) == 14
    assert chave[8] == "-"
    assert validar_chave(chave) == validade


def test_chave_invalida_rejeitada():
    assert validar_chave("") is None
    assert validar_chave("abc") is None
    assert validar_chave("20261231-XXXXX") is None
    assert validar_chave("2026123-1-XXXXX") is None


def test_chave_com_data_passada_valida_assinatura():
    validade = date(2020, 1, 1)
    chave = gerar_chave(validade)
    assert validar_chave(chave) == validade


def test_primeiro_uso_inicia_trial(tmp_path):
    repo = _repo(tmp_path)
    service = LicencaService(repo)
    status = service.verificar()
    assert status.tipo == "EM_TRIAL"
    assert status.dias_restantes == TRIAL_DIAS
    assert repo.get(CHAVE_PRIMEIRO_USO) is not None


def test_trial_nao_reinicia_no_segundo_dia(tmp_path):
    repo = _repo(tmp_path)
    service = LicencaService(repo)
    service.verificar()
    hoje = date.today()
    repo.set(
        Configuracao(
            chave=CHAVE_PRIMEIRO_USO,
            valor=(hoje - timedelta(days=5)).isoformat(),
        )
    )
    status = service.verificar()
    assert status.tipo == "EM_TRIAL"
    assert status.dias_restantes == TRIAL_DIAS - 5


def test_trial_expirado(tmp_path):
    repo = _repo(tmp_path)
    service = LicencaService(repo)
    service.verificar()
    hoje = date.today()
    repo.set(
        Configuracao(
            chave=CHAVE_PRIMEIRO_USO,
            valor=(hoje - timedelta(days=TRIAL_DIAS + 1)).isoformat(),
        )
    )
    status = service.verificar()
    assert status.tipo == "TRIAL_EXPIRADO"


def test_chave_valida_libera(tmp_path):
    repo = _repo(tmp_path)
    service = LicencaService(repo)
    chave = gerar_chave(date.today() + timedelta(days=30))
    assert service.registrar_chave(chave) is True
    status = service.verificar()
    assert status.tipo == "LICENCIADO"
    assert status.dias_restantes == 30


def test_chave_invalida_nao_registra(tmp_path):
    repo = _repo(tmp_path)
    service = LicencaService(repo)
    assert service.registrar_chave("CHAVE-ERRADA") is False
    assert repo.get(CHAVE_LICENCA) is None


def test_chave_expirada_bloqueia(tmp_path):
    repo = _repo(tmp_path)
    service = LicencaService(repo)
    chave = gerar_chave(date.today() - timedelta(days=1))
    assert service.registrar_chave(chave) is True
    status = service.verificar()
    assert status.tipo == "CHAVE_EXPIRADA"


def _repo(tmp_path):
    from controle_obras.infrastructure.database import DatabaseManager
    from controle_obras.infrastructure.repositories import ConfiguracaoRepository

    db = DatabaseManager(tmp_path / "test.db")
    db.init_schema()
    return ConfiguracaoRepository(db)
