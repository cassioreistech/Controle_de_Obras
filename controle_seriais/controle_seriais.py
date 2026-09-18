"""Sistema Portátil de Gerenciamento de Seriais - Controle de Obras.

Ferramenta standalone para gerenciar seriais de licença.
Não depende do sistema principal - pode ser copiada para qualquer máquina.

Uso:
    python controle_seriais.py listar
    python controle_seriais.py registrar --chave CHAVE --cliente NOME --validade YYYY-MM-DD
    python controle_seriais.py buscar CHAVE
    python controle_seriais.py estatisticas
"""

import hashlib
import hmac
import sqlite3
import sys
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Optional


# ==========================================
# CONFIGURAÇÃO DO BANCO DE DADOS PORTÁTIL
# ==========================================

class DatabaseManager:
    """Gerencia banco de dados SQLite portátil."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Banco fica na mesma pasta do script
            db_path = str(Path(__file__).parent / "seriais.db")
        self.db_path = Path(db_path)
        self._init_schema()
    
    def _init_schema(self):
        """Cria tabela de seriais se não existir."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS seriais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chave TEXT NOT NULL UNIQUE,
                    cliente_nome TEXT,
                    cliente_empresa TEXT,
                    cliente_contato TEXT,
                    maquina_id TEXT NOT NULL,
                    data_geracao DATE NOT NULL,
                    data_validade DATE NOT NULL,
                    status TEXT DEFAULT 'Ativo',
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def execute(self, sql: str, params: tuple = ()):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(sql, params).fetchall()
    
    def execute_insert(self, sql: str, params: tuple = ()):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(sql, params)
            return cursor.lastrowid


# ==========================================
# MODELO DE DADOS
# ==========================================

class Serial:
    """Serial de licença."""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.chave = kwargs.get('chave', '')
        self.cliente_nome = kwargs.get('cliente_nome', '')
        self.cliente_empresa = kwargs.get('cliente_empresa', '')
        self.cliente_contato = kwargs.get('cliente_contato', '')
        self.maquina_id = kwargs.get('maquina_id', '')
        self.data_geracao = kwargs.get('data_geracao', date.today())
        self.data_validade = kwargs.get('data_validade', date.today())
        self.status = kwargs.get('status', 'Ativo')
        self.observacoes = kwargs.get('observacoes', '')


# ==========================================
# SERVIÇO DE LICENÇA (para gerar chaves)
# ==========================================

# Segredo ofuscado (mesmo do sistema principal)
_SECRETO_HEX = bytes.fromhex(
    "4330 6e74 7230 6c65 2d30 6272 3473 2d4c 3163 336e 6334 2d32 3032 3621 4023 24".replace(" ", "")
)
SECRETO_LICENCA = _SECRETO_HEX.decode("utf-8")


def obter_maquina_id() -> str:
    """Retorna ID da máquina (compatível com o sistema principal)."""
    maquina_id = ""
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Cryptography",
                0,
                winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
            ) as chave:
                maquina_id, _ = winreg.QueryValueEx(chave, "MachineGuid")
        except OSError:
            maquina_id = ""
    
    if not maquina_id:
        maquina_id = str(uuid.getnode())
    
    return hashlib.sha256(maquina_id.encode("utf-8")).hexdigest()[:6].upper()


def _checksum(validade: date, maquina_id: str) -> str:
    payload = f"CONTROLE-OBRAS|{validade.isoformat()}|{maquina_id}"
    digest = hmac.new(
        SECRETO_LICENCA.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest[:5].upper()


def gerar_chave(validade: date, maquina_id: str) -> str:
    """Gera chave de licença (mesma lógica do sistema principal)."""
    return f"{validade.strftime('%Y%m%d')}-{_checksum(validade, maquina_id)}"


# ==========================================
# SERVIÇO DE SERIAIS
# ==========================================

class SerialService:
    """Serviço de gerenciamento de seriais."""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def registrar(self, chave: str, cliente_nome: str, cliente_empresa: str,
                  cliente_contato: str, maquina_id: str, data_validade: date,
                  observacoes: str = "") -> Serial:
        """Registra um novo serial."""
        # Verificar se já existe
        existing = self.buscar_por_chave(chave)
        if existing:
            raise ValueError(f"Serial {chave} já está registrado")
        
        sql = """
            INSERT INTO seriais (chave, cliente_nome, cliente_empresa, cliente_contato,
                maquina_id, data_geracao, data_validade, status, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Ativo', ?)
        """
        serial_id = self.db.execute_insert(sql, (
            chave.upper(), cliente_nome, cliente_empresa, cliente_contato,
            maquina_id, date.today().isoformat(), data_validade.isoformat(), observacoes
        ))
        
        return self.buscar_por_id(serial_id)
    
    def buscar_por_chave(self, chave: str) -> Optional[Serial]:
        """Busca serial por chave."""
        rows = self.db.execute("SELECT * FROM seriais WHERE chave=?", (chave.upper(),))
        return self._row_to_serial(rows[0]) if rows else None
    
    def buscar_por_id(self, serial_id: int) -> Optional[Serial]:
        """Busca serial por ID."""
        rows = self.db.execute("SELECT * FROM seriais WHERE id=?", (serial_id,))
        return self._row_to_serial(rows[0]) if rows else None
    
    def listar_todos(self) -> list[Serial]:
        """Lista todos os seriais."""
        rows = self.db.execute("SELECT * FROM seriais ORDER BY data_geracao DESC")
        return [self._row_to_serial(row) for row in rows]
    
    def listar_por_status(self, status: str) -> list[Serial]:
        """Lista seriais por status."""
        rows = self.db.execute(
            "SELECT * FROM seriais WHERE status=? ORDER BY data_geracao DESC", (status,)
        )
        return [self._row_to_serial(row) for row in rows]
    
    def atualizar_status(self, serial_id: int, status: str) -> bool:
        """Atualiza status de um serial."""
        if status not in ["Ativo", "Inativo", "Expirado"]:
            return False
        
        self.db.execute(
            "UPDATE seriais SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (status, serial_id)
        )
        return True
    
    def excluir(self, serial_id: int) -> bool:
        """Exclui um serial."""
        self.db.execute("DELETE FROM seriais WHERE id=?", (serial_id,))
        return True
    
    def estatisticas(self) -> dict:
        """Retorna estatísticas."""
        rows = self.db.execute("SELECT status, COUNT(*) as total FROM seriais GROUP BY status")
        contagem = {row[0]: row[1] for row in rows}
        
        todos = self.listar_todos()
        total = len(todos)
        hoje = date.today()
        expirados_real = sum(1 for s in todos if s.data_validade < hoje and s.status == "Ativo")
        
        return {
            "total": total,
            "ativos": contagem.get("Ativo", 0),
            "inativos": contagem.get("Inativo", 0),
            "expirados": contagem.get("Expirado", 0),
            "expirados_real": expirados_real,
        }
    
    def _row_to_serial(self, row) -> Serial:
        """Converte linha do banco para objeto Serial."""
        return Serial(
            id=row[0],
            chave=row[1],
            cliente_nome=row[2] or "",
            cliente_empresa=row[3] or "",
            cliente_contato=row[4] or "",
            maquina_id=row[5],
            data_geracao=date.fromisoformat(row[6]),
            data_validade=date.fromisoformat(row[7]),
            status=row[8],
            observacoes=row[9] or "",
        )


# ==========================================
# INTERFACE DE LINHA DE COMANDO
# ==========================================

def cmd_listar(service: SerialService):
    """Lista todos os seriais."""
    seriais = service.listar_todos()
    
    if not seriais:
        print("\nNenhum serial registrado.\n")
        return
    
    print(f"\n{'='*80}")
    print(f"SERIAIS DE LICENÇA ({len(seriais)} total)")
    print(f"{'='*80}\n")
    
    for s in seriais:
        status_icon = "[OK]" if s.status == "Ativo" else "[X]" if s.status == "Expirado" else "[-]"
        print(f"{status_icon} {s.chave}")
        print(f"  Cliente: {s.cliente_nome}")
        print(f"  Empresa: {s.cliente_empresa}")
        print(f"  Máquina: {s.maquina_id[:8]}...")
        print(f"  Validade: {s.data_validade.strftime('%d/%m/%Y')}")
        print(f"  Status: {s.status}")
        if s.observacoes:
            print(f"  Obs: {s.observacoes}")
        print()


def cmd_buscar(service: SerialService, chave: str):
    """Busca serial por chave."""
    serial = service.buscar_por_chave(chave)
    
    if not serial:
        print(f"\nSerial {chave} não encontrado.\n")
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
    print()


def cmd_registrar(service: SerialService, args):
    """Registra novo serial."""
    try:
        validade = datetime.strptime(args.validade, "%Y-%m-%d").date()
    except ValueError:
        print("\nData invalida. Use o formato YYYY-MM-DD.\n")
        return
    
    try:
        serial = service.registrar(
            chave=args.chave,
            cliente_nome=args.cliente,
            cliente_empresa=args.empresa or "",
            cliente_contato=args.contato or "",
            maquina_id=args.maquina or "",
            data_validade=validade,
            observacoes=args.obs or "",
        )
        print(f"\n[OK] Serial registrado com sucesso!")
        print(f"  ID: {serial.id}")
        print(f"  Chave: {serial.chave}\n")
    except ValueError as e:
        print(f"\n[ERRO] {e}\n")


def cmd_status(service: SerialService, chave: str, status: str):
    """Atualiza status."""
    serial = service.buscar_por_chave(chave)
    
    if not serial:
        print(f"\nSerial {chave} nao encontrado.\n")
        return
    
    if service.atualizar_status(serial.id, status):
        print(f"\n[OK] Status do serial {chave} atualizado para {status}.\n")
    else:
        print("\n[ERRO] Erro ao atualizar status.\n")


def cmd_excluir(service: SerialService, serial_id: int):
    """Exclui serial."""
    serial = service.buscar_por_id(serial_id)
    
    if not serial:
        print(f"\nSerial ID {serial_id} nao encontrado.\n")
        return
    
    confirmacao = input(f"\nTem certeza que deseja excluir o serial {serial.chave}? (s/N): ")
    if confirmacao.lower() != "s":
        print("Operacao cancelada.\n")
        return
    
    if service.excluir(serial_id):
        print(f"\n[OK] Serial {serial.chave} excluido com sucesso.\n")
    else:
        print("\n[ERRO] Erro ao excluir serial.\n")


def cmd_estatisticas(service: SerialService):
    """Mostra estatísticas."""
    stats = service.estatisticas()
    
    print(f"\n{'='*40}")
    print("ESTATÍSTICAS DE SERIAIS")
    print(f"{'='*40}\n")
    print(f"  Total: {stats['total']}")
    print(f"  Ativos: {stats['ativos']}")
    print(f"  Inativos: {stats['inativos']}")
    print(f"  Expirados: {stats['expirados']}")
    print()


def cmd_gerar_chave(args):
    """Gera nova chave de licença."""
    try:
        validade = datetime.strptime(args.validade, "%Y-%m-%d").date()
    except ValueError:
        print("\nData invalida. Use o formato YYYY-MM-DD.\n")
        return
    
    maquina_id = args.maquina.upper() if args.maquina else obter_maquina_id()
    
    chave = gerar_chave(validade, maquina_id)
    print(f"\n[OK] Chave gerada com sucesso!")
    print(f"  Chave: {chave}")
    print(f"  Validade: {validade.isoformat()}")
    print(f"  Maquina: {maquina_id}\n")
    print("Para registrar no controle, use:")
    print(f"  python controle_seriais.py registrar --chave {chave} --cliente \"NOME\" --validade {validade.isoformat()}\n")


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sistema Portátil de Gerenciamento de Seriais - Controle de Obras"
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
    parser_registrar.add_argument("--maquina", help="ID da máquina")
    parser_registrar.add_argument("--validade", required=True, help="Data de validade (YYYY-MM-DD)")
    parser_registrar.add_argument("--obs", help="Observações")
    
    # Status
    parser_status = subparsers.add_parser("status", help="Atualiza status")
    parser_status.add_argument("chave", help="Chave do serial")
    parser_status.add_argument("status", help="Novo status (Ativo/Inativo/Expirado)")
    
    # Excluir
    parser_excluir = subparsers.add_parser("excluir", help="Exclui serial")
    parser_excluir.add_argument("id", type=int, help="ID do serial")
    
    # Estatísticas
    subparsers.add_parser("estatisticas", help="Mostra estatísticas")
    
    # Gerar chave
    parser_gerar = subparsers.add_parser("gerar", help="Gera nova chave de licença")
    parser_gerar.add_argument("validade", help="Data de validade (YYYY-MM-DD)")
    parser_gerar.add_argument("--maquina", help="ID da máquina (opcional)")
    
    args = parser.parse_args()
    
    if not args.comando:
        parser.print_help()
        return
    
    service = SerialService(DatabaseManager())
    
    if args.comando == "listar":
        cmd_listar(service)
    elif args.comando == "buscar":
        cmd_buscar(service, args.chave)
    elif args.comando == "registrar":
        cmd_registrar(service, args)
    elif args.comando == "status":
        cmd_status(service, args.chave, args.status)
    elif args.comando == "excluir":
        cmd_excluir(service, args.id)
    elif args.comando == "estatisticas":
        cmd_estatisticas(service)
    elif args.comando == "gerar":
        cmd_gerar_chave(args)


if __name__ == "__main__":
    main()
