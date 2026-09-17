"""Utilitários de formatação e parse de valores monetários (formato brasileiro)."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation


def formatar_valor(valor: Decimal) -> str:
    """Formata Decimal para exibição no formato brasileiro (1.234,56)."""
    partes = f"{valor:.2f}".split(".")
    inteiro = partes[0]
    decimal = partes[1] if len(partes) > 1 else "00"
    inteiro_formatado = f"{int(inteiro):,}".replace(",", ".")
    return f"{inteiro_formatado},{decimal}"


def parse_valor(texto: str) -> Decimal | None:
    """Parse monetário aceitando formatos brasileiro e Python.

    Regras:
      - Vazio ou só zeros → Decimal("0.00")
      - Formato brasileiro (virgula decimal): "1.234,56"
      - Formato Python (ponto decimal): "1234.56"
      - Múltiplos pontos com grupos de 3 dígitos → milhar
        ("1.000" → 1000, "1.234.567" → 1234567)
      - Negativos → None (invalidado)
      - Entrada sem sentido → None

    Retorna Decimal ou None se inválido.
    """
    t = str(texto).strip()
    if not t:
        return Decimal("0.00")

    # Remove R$ se presente
    t = t.replace("R$", "").strip()

    # Remove sinais (negativos sempre rejeitados)
    negativo = t.startswith("-")
    t = t.lstrip("+-").strip()

    if not t or t in (",", "."):
        return Decimal("0.00")

    # Formato brasileiro: contém vírgula → pontos são separador de milhares
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    else:
        # Sem vírgula: tratar ponto como milhar se grupos de 3 dígitos
        if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", t):
            t = t.replace(".", "")

    try:
        valor = Decimal(t)
    except InvalidOperation:
        return None

    if valor < 0 or negativo:
        return None

    return valor
