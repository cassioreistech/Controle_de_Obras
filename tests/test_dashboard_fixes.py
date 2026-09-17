"""Testes de regressão: parse/format de aditivos (regressão do bug de corrupção 100x)."""
from __future__ import annotations

import unittest
from decimal import Decimal

from controle_obras.ui.value_utils import formatar_valor, parse_valor


class TestParseAditivo(unittest.TestCase):
    """Valores que o diálogo de edição pré-preenche e depois salva."""

    def test_ponto_decimal_preservado(self):
        """'1500.50' -> Decimal('1500.50') (bug antigo retornaria 15050.00)."""
        self.assertEqual(parse_valor("1500.50"), Decimal("1500.50"))

    def test_formato_brasileiro(self):
        """'1.500,50' -> Decimal('1500.50')."""
        self.assertEqual(parse_valor("1.500,50"), Decimal("1500.50"))

    def test_milhar_sem_virgula(self):
        """'1.000' -> Decimal('1000')."""
        self.assertEqual(parse_valor("1.000"), Decimal("1000"))

    def test_formato_python_curto(self):
        """'1.5' -> Decimal('1.5')."""
        self.assertEqual(parse_valor("1.5"), Decimal("1.5"))

    def test_vazio_retorna_zero(self):
        self.assertEqual(parse_valor(""), Decimal("0.00"))
        self.assertEqual(parse_valor("   "), Decimal("0.00"))

    def test_negativo_rejeitado(self):
        self.assertIsNone(parse_valor("-500.00"))
        self.assertIsNone(parse_valor("-1.234,56"))


class TestFormatarParaExibicao(unittest.TestCase):
    """formatar_valor sempre gera separadores brasileiros."""

    def test_valores_grandes_com_casas(self):
        self.assertEqual(formatar_valor(Decimal("1500.50")), "1.500,50")

    def test_valores_grandes_sem_casas(self):
        self.assertEqual(formatar_valor(Decimal("1000.00")), "1.000,00")

    def test_zero(self):
        self.assertEqual(formatar_valor(Decimal("0.00")), "0,00")

    def test_frase_milhar_grande(self):
        self.assertEqual(formatar_valor(Decimal("1234567.89")), "1.234.567,89")


if __name__ == "__main__":
    unittest.main()
