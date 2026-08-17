"""Testes de integração do fluxo principal da Fase 1."""

from decimal import Decimal
from pathlib import Path

import pytest

from controle_obras.application.services import (
    AditivoService,
    EmpresaService,
    LancamentoService,
    ObraResumoService,
    ObraService,
)
from controle_obras.domain.models import Aditivo, Empresa, Lancamento, Obra
from controle_obras.infrastructure.database import DatabaseManager
from controle_obras.infrastructure.repositories import (
    AditivoRepository,
    EmpresaRepository,
    LancamentoRepository,
    ObraRepository,
)


@pytest.fixture
def services(tmp_path: Path):
    db = DatabaseManager(tmp_path / "app.db")
    db.init_schema()

    empresa_service = EmpresaService(EmpresaRepository(db))
    obra_service = ObraService(ObraRepository(db))
    aditivo_service = AditivoService(AditivoRepository(db))
    lancamento_service = LancamentoService(LancamentoRepository(db))
    resumo_service = ObraResumoService(
        ObraRepository(db),
        AditivoRepository(db),
        LancamentoRepository(db),
    )

    return {
        "db": db,
        "empresa": empresa_service,
        "obra": obra_service,
        "aditivo": aditivo_service,
        "lancamento": lancamento_service,
        "resumo": resumo_service,
    }


def test_fluxo_principal_cadastro_e_apuracao(services):
    # Cadastra empresa
    empresa = Empresa(razao_social="Construtora Teste", cnpj="00.000.000/0001-00")
    services["empresa"].salvar(empresa)
    assert services["empresa"].empresa_configurada()

    # Cadastra obra
    obra = Obra(
        codigo="OBRA-001",
        nome="Edificio Residencial",
        cliente_contratante="Cliente A",
        local_obra="Sao Paulo",
        valor_contratado_inicial=Decimal("100000.00"),
    )
    obra = services["obra"].salvar(obra)
    assert obra.id is not None

    # Registra aditivo
    aditivo = Aditivo(
        obra_id=obra.id,
        descricao="Aditivo de acabamento",
        valor=Decimal("15000.00"),
    )
    services["aditivo"].salvar(aditivo)

    # Registra lancamento
    lancamento = Lancamento(
        obra_id=obra.id,
        descricao="Saco de cimento",
        valor_total=Decimal("5000.00"),
    )
    services["lancamento"].salvar(lancamento)

    # Calcula resumo
    resumo = services["resumo"].calcular_resumo(obra.id)
    assert resumo.valor_contratado == Decimal("100000.00")
    assert resumo.total_aditivos == Decimal("15000.00")
    assert resumo.total_gasto == Decimal("5000.00")
    assert resumo.valor_liquido == Decimal("110000.00")
