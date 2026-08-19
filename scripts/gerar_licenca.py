"""Gera chave de licenca do Controle de Obras (uso do desenvolvedor).

Uso:
    python scripts/gerar_licenca.py 2026-12-31

Saida: uma chave no formato YYYYMMDD-XXXXX valida ate a data informada.
"""

import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from controle_obras.application.license_service import gerar_chave  # noqa: E402


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python scripts/gerar_licenca.py YYYY-MM-DD")
        sys.exit(1)

    try:
        validade = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    except ValueError:
        print("Data invalida. Use o formato YYYY-MM-DD (ex.: 2026-12-31).")
        sys.exit(1)

    if validade < date.today():
        print("Aviso: a data informada ja passou.")

    chave = gerar_chave(validade)
    print("\nChave de licenca gerada:")
    print(f"  {chave}")
    print(f"  Valida ate: {validade.isoformat()}\n")


if __name__ == "__main__":
    main()
