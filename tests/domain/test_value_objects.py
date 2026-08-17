"""Testes para objetos de valor do domínio."""

from decimal import Decimal

from controle_obras.domain.value_objects import ResumoFinanceiroObra


def test_resumo_financeiro_calcula_valor_liquido():
    resumo = ResumoFinanceiroObra(
        valor_contratado=Decimal("100000.00"),
        total_aditivos=Decimal("15000.00"),
        total_gasto=Decimal("45000.00"),
    )

    assert resumo.valor_liquido == Decimal("70000.00")


def test_resumo_financeiro_sem_aditivos():
    resumo = ResumoFinanceiroObra(
        valor_contratado=Decimal("50000.00"),
        total_aditivos=Decimal("0.00"),
        total_gasto=Decimal("20000.00"),
    )

    assert resumo.valor_liquido == Decimal("30000.00")
