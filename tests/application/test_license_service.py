"""Testes do servico de licenciamento (trial + chave HMAC vinculada a maquina)."""

from datetime import date, timedelta

from controle_obras.application.license_service import (
    CHAVE_DATA_ATIVACAO,
    CHAVE_LICENCA,
    CHAVE_MAQUINA_REGISTRADA,
    CHAVE_PRIMEIRO_USO,
    TRIAL_DIAS,
    LicencaService,
    _checksum_legado,
    _maquina_id_legado,
    gerar_chave,
    obter_maquina_id,
    validar_chave,
    validar_chave_legado,
)
from controle_obras.domain.models import Configuracao

MAQUINA = obter_maquina_id()


def test_gerar_chave_roundtrip():
    validade = date(2026, 12, 31)
    chave = gerar_chave(validade, MAQUINA)
    assert len(chave) == 15  # 8 data + 1 hifen + 6 checksum
    assert chave[8] == "-"
    assert validar_chave(chave, MAQUINA) == validade


def test_chave_nao_funciona_em_outra_maquina():
    validade = date(2026, 12, 31)
    chave = gerar_chave(validade, MAQUINA)
    assert validar_chave(chave, "OUTRAMAQ") is None


def test_chave_invalida_rejeitada():
    assert validar_chave("", MAQUINA) is None
    assert validar_chave("abc", MAQUINA) is None
    assert validar_chave("20261231-XXXXX", MAQUINA) is None
    assert validar_chave("2026123-1-XXXXX", MAQUINA) is None


def test_chave_com_data_passada_valida_assinatura():
    validade = date(2020, 1, 1)
    chave = gerar_chave(validade, MAQUINA)
    assert validar_chave(chave, MAQUINA) == validade


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
    chave = gerar_chave(date.today() + timedelta(days=30), MAQUINA)
    sucesso, mensagem = service.registrar_chave(chave)
    assert sucesso is True
    status = service.verificar()
    assert status.tipo == "LICENCIADO"
    assert status.dias_restantes == 30


def test_chave_invalida_nao_registra(tmp_path):
    repo = _repo(tmp_path)
    service = LicencaService(repo)
    sucesso, mensagem = service.registrar_chave("CHAVE-ERRADA")
    assert sucesso is False
    assert repo.get(CHAVE_LICENCA) is None


def test_chave_invalida_gravada_cai_no_trial(tmp_path):
    """Chave salva invalida nao deve travar: cai no trial em vez de bloquear."""
    repo = _repo(tmp_path)
    service = LicencaService(repo)
    # Simula chave corrompida/antiga gravada (ex.: de algoritmo pre-v2)
    repo.set(Configuracao(chave=CHAVE_LICENCA, valor="20260925-87318"))

    status = service.verificar()
    assert status.tipo == "EM_TRIAL"
    assert status.dias_restantes == TRIAL_DIAS


def test_chave_expirada_bloqueia(tmp_path):
    repo = _repo(tmp_path)
    service = LicencaService(repo)
    chave = gerar_chave(date.today() - timedelta(days=1), MAQUINA)
    sucesso, mensagem = service.registrar_chave(chave)
    assert sucesso is True  # Chave e valida (assinatura correta), mas expirada
    status = service.verificar()
    assert status.tipo == "CHAVE_EXPIRADA"


# ==========================================
# Testes legado (compatibilidade pre-v2)
# ==========================================


def _gerar_chave_legado(validade: date, maquina_id: str) -> str:
    """Gera uma chave no formato legado (5-char checksum, com traço)."""
    return f"{validade.strftime('%Y%m%d')}-{_checksum_legado(validade, maquina_id)}"


def test_chave_legado_roundtrip():
    """Chave legado valida com o algoritmo antigo."""
    maquina_legado = _maquina_id_legado()
    validade = date(2027, 6, 30)
    chave = _gerar_chave_legado(validade, maquina_legado)
    assert len(chave) == 14  # 8 data + 1 hifen + 5 checksum
    assert chave[8] == "-"
    assert validar_chave_legado(chave) == validade


def test_chave_legado_rejeitada_pelo_novo_algoritmo():
    """Chave legado NAO valida pelo algoritmo novo (checksum diferente)."""
    maquina_legado = _maquina_id_legado()
    validade = date(2027, 6, 30)
    chave = _gerar_chave_legado(validade, maquina_legado)
    assert validar_chave(chave, maquina_legado) is None


def test_chave_legado_migra_para_novo_formato(tmp_path):
    """Ao verificar uma chave legado, o sistema migra automaticamente."""
    repo = _repo(tmp_path)
    service = LicencaService(repo)

    maquina_legado = _maquina_id_legado()
    validade = date.today() + timedelta(days=60)
    chave = _gerar_chave_legado(validade, maquina_legado)

    # Simular estado antigo: chave gravada sem machine_registrada/data_ativacao
    repo.set(Configuracao(chave=CHAVE_LICENCA, valor=chave))

    status = service.verificar()
    assert status.tipo == "LICENCIADO"
    assert status.dias_restantes == 60

    # Verificar que migracao gravou os campos que faltavam
    assert repo.get(CHAVE_MAQUINA_REGISTRADA) is not None
    assert repo.get(CHAVE_DATA_ATIVACAO) is not None


def test_anti_drift_maquina_registrada(tmp_path):
    """Se a maquina mudou (drift), chave valida contra a maquina registrada."""
    repo = _repo(tmp_path)
    service = LicencaService(repo)

    validade = date.today() + timedelta(days=30)
    chave = gerar_chave(validade, MAQUINA)
    sucesso, _ = service.registrar_chave(chave)
    assert sucesso is True

    # Simular drift: mudar a maquina registrada
    repo.set(Configuracao(
        chave=CHAVE_MAQUINA_REGISTRADA,
        valor="OUTRA_MAQUINA_QUE_NAO_A_ATUAL",
    ))

    # A chave continua valida via anti-drift
    status = service.verificar()
    assert status.tipo == "LICENCIADO"


def _repo(tmp_path):
    from controle_obras.infrastructure.database import DatabaseManager
    from controle_obras.infrastructure.repositories import ConfiguracaoRepository

    db = DatabaseManager(tmp_path / "test.db")
    db.init_schema()
    return ConfiguracaoRepository(db)
