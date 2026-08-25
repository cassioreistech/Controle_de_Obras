"""Gera chave de licenca do Controle de Obras (uso do desenvolvedor).

A chave e vinculada a maquina do cliente. Para gerar, voce precisa do
ID da maquina que o cliente obteve em: Configuracoes > 'ID da maquina'.

Uso:
    python scripts/gerar_licenca.py YYYY-MM-DD MAQUINA_ID

Saida: uma chave no formato YYYYMMDD-XXXXX valida ate a data informada
e somente na maquina informada.
"""

import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from controle_obras.application.license_service import gerar_chave, obter_maquina_id  # noqa: E402


def main() -> None:
    if len(sys.argv) == 2 and sys.argv[1] == "--id":
        print(f"ID desta maquina: {obter_maquina_id()}")
        return

    if len(sys.argv) != 3:
        print("Uso:")
        print("  python scripts/gerar_licenca.py --id")
        print("  python scripts/gerar_licenca.py YYYY-MM-DD MAQUINA_ID")
        sys.exit(1)

    try:
        validade = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    except ValueError:
        print("Data invalida. Use o formato YYYY-MM-DD (ex.: 2026-12-31).")
        sys.exit(1)

    maquina_id = sys.argv[2].strip().upper()

    if validade < date.today():
        print("Aviso: a data informada ja passou.")

    chave = gerar_chave(validade, maquina_id)
    print("\nChave de licenca gerada:")
    print(f"  {chave}")
    print(f"  Valida ate: {validade.isoformat()}")
    print(f"  Maquina: {maquina_id}\n")


if __name__ == "__main__":
    main()
