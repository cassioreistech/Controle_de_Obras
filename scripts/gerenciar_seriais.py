"""Gerenciador de seriais de licença (ferramenta do desenvolvedor).

Uso:
    python scripts/gerenciar_seriais.py listar
    python scripts/gerenciar_seriais.py buscar CHAVE
    python scripts/gerenciar_seriais.py registrar --chave CHAVE --cliente NOME --empresa EMPRESA --maquina MAQUINA --validade YYYY-MM-DD
    python scripts/gerenciar_seriais.py status --chave CHAVE --status Ativo|Inativo|Expirado
    python scripts/gerenciar_seriais.py excluir --id ID
    python scripts/gerenciar_seriais.py estatisticas

Exemplos:
    python scripts/gerenciar_seriais.py listar
    python scripts/gerenciar_seriais.py buscar 20261231-ABC12
    python scripts/gerenciar_seriais.py registrar --chave 20261231-ABC12 --cliente "João Silva" --empresa "Construtora ABC" --maquina ABC123 --validade 2026-12-31
    python scripts/gerenciar_seriais.py status --chave 20261231-ABC12 --status Inativo
"""

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from controle_obras.application.serial_service import SerialService
from controle_obras.infrastructure.database import DatabaseManager
from controle_obras.infrastructure.repositories import SerialRepository
from controle_obras.infrastructure.storage import AppStorage


def get_service() -> SerialService:
    """Retorna instância do SerialService."""
    storage = AppStorage()
    db = DatabaseManager(storage.db_path())
    db.init_schema()
    return SerialService(SerialRepository(db))


def cmd_listar(args):
    """Lista todos os seriais."""
    service = get_service()
    seriais = service.listar_todos()

    if not seriais:
        print("Nenhum serial registrado.")
        return

    print(f"\n{'='*80}")
    print(f"SERIAIS DE LICENÇA ({len(seriais)} total)")
    print(f"{'='*80}\n")

    for s in seriais:
        status_icon = "✓" if s.status == "Ativo" else "✗" if s.status == "Expirado" else "○"
        print(f"{status_icon} {s.chave}")
        print(f"  Cliente: {s.cliente_nome}")
        print(f"  Empresa: {s.cliente_empresa}")
        print(f"  Máquina: {s.maquina_id[:8]}...")
        print(f"  Validade: {s.data_validade.strftime('%d/%m/%Y')}")
        print(f"  Status: {s.status}")
        if s.observacoes:
            print(f"  Obs: {s.observacoes}")
        print()


def cmd_buscar(args):
    """Busca serial por chave."""
    service = get_service()
    serial = service.buscar_por_chave(args.chave)

    if not serial:
        print(f"Serial {args.chave} não encontrado.")
        return

    print(f"\nSerial encontrado:")
    print(f"  Chave: {serial.chave}")
    print(f"  Cliente: {serial.cliente_nome}")
    print(f"  Empresa: {serial.cliente_empresa}")
    print(f"  Contato: {serial.cliente_contato}")
    print(f"  Máquina: {serial.maquina_id}")
    print(f"  Geração: {serial.data_geracao.strftime('%d/%m/%Y')}")
    print(f"  Validade: {serial.data_validade.strftime('%d/%m/%Y')}")
    print(f"  Status: {serial.status}")
    if serial.observacoes:
        print(f"  Obs: {serial.observacoes}")


def cmd_registrar(args):
    """Registra um novo serial."""
    service = get_service()

    try:
        validade = datetime.strptime(args.validade, "%Y-%m-%d").date()
    except ValueError:
        print("Data inválida. Use o formato YYYY-MM-DD.")
        return

    try:
        serial = service.registrar_serial(
            chave=args.chave,
            cliente_nome=args.cliente,
            cliente_empresa=args.empresa or "",
            cliente_contato=args.contato or "",
            maquina_id=args.maquina,
            data_validade=validade,
            observacoes=args.obs or "",
        )
        print(f"\nSerial registrado com sucesso!")
        print(f"  ID: {serial.id}")
        print(f"  Chave: {serial.chave}")
    except ValueError as e:
        print(f"Erro: {e}")


def cmd_status(args):
    """Atualiza status de um serial."""
    service = get_service()
    serial = service.buscar_por_chave(args.chave)

    if not serial:
        print(f"Serial {args.chave} não encontrado.")
        return

    if args.status not in ["Ativo", "Inativo", "Expirado"]:
        print("Status inválido. Use: Ativo, Inativo ou Expirado.")
        return

    if service.atualizar_status(serial.id, args.status):
        print(f"Status do serial {args.chave} atualizado para {args.status}.")
    else:
        print("Erro ao atualizar status.")


def cmd_excluir(args):
    """Exclui um serial."""
    service = get_service()

    confirmacao = input(f"Tem certeza que deseja excluir o serial ID {args.id}? (s/N): ")
    if confirmacao.lower() != "s":
        print("Operação cancelada.")
        return

    if service.excluir(args.id):
        print(f"Serial ID {args.id} excluído com sucesso.")
    else:
        print(f"Serial ID {args.id} não encontrado.")


def cmd_estatisticas(args):
    """Mostra estatísticas dos seriais."""
    service = get_service()
    stats = service.obter_estatisticas()

    print(f"\n{'='*40}")
    print("ESTATÍSTICAS DE SERIAIS")
    print(f"{'='*40}\n")
    print(f"  Total: {stats['total']}")
    print(f"  Ativos: {stats['ativos']}")
    print(f"  Inativos: {stats['inativos']}")
    print(f"  Expirados: {stats['expirados']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Gerenciador de seriais de licença - Controle de Obras"
    )
    subparsers = parser.add_subparsers(dest="comando", help="Comando a executar")

    # Listar
    subparsers.add_parser("listar", help="Lista todos os seriais")

    # Buscar
    parser_buscar = subparsers.add_parser("buscar", help="Busca serial por chave")
    parser_buscar.add_argument("chave", help="Chave do serial")

    # Registrar
    parser_registrar = subparsers.add_parser("registrar", help="Registra novo serial")
    parser_registrar.add_argument("--chave", required=True, help="Chave do serial")
    parser_registrar.add_argument("--cliente", required=True, help="Nome do cliente")
    parser_registrar.add_argument("--empresa", help="Nome da empresa")
    parser_registrar.add_argument("--contato", help="Contato do cliente")
    parser_registrar.add_argument("--maquina", required=True, help="ID da máquina")
    parser_registrar.add_argument("--validade", required=True, help="Data de validade (YYYY-MM-DD)")
    parser_registrar.add_argument("--obs", help="Observações")

    # Status
    parser_status = subparsers.add_parser("status", help="Atualiza status de um serial")
    parser_status.add_argument("--chave", required=True, help="Chave do serial")
    parser_status.add_argument("--status", required=True, help="Novo status (Ativo/Inativo/Expirado)")

    # Excluir
    parser_excluir = subparsers.add_parser("excluir", help="Exclui um serial")
    parser_excluir.add_argument("--id", type=int, required=True, help="ID do serial")

    # Estatísticas
    subparsers.add_parser("estatisticas", help="Mostra estatísticas dos seriais")

    args = parser.parse_args()

    if not args.comando:
        parser.print_help()
        return

    comandos = {
        "listar": cmd_listar,
        "buscar": cmd_buscar,
        "registrar": cmd_registrar,
        "status": cmd_status,
        "excluir": cmd_excluir,
        "estatisticas": cmd_estatisticas,
    }

    comandos[args.comando](args)


if __name__ == "__main__":
    main()
