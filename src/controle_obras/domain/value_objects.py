"""Objetos de valor para cálculos financeiros do domínio."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ResumoFinanceiroObra:
    """Resumo financeiro consolidado de uma obra."""

    valor_contratado: Decimal
    total_aditivos: Decimal
    total_gasto: Decimal

    @property
    def valor_liquido(self) -> Decimal:
        """Valor líquido = contratado + aditivos - gastos."""
        return self.valor_contratado + self.total_aditivos - self.total_gasto
