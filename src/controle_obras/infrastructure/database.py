"""Gerenciamento do banco de dados SQLite."""

import contextlib
import gc
import sqlite3
from pathlib import Path
from typing import Any

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS empresa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    razao_social TEXT NOT NULL,
    nome_fantasia TEXT,
    cnpj TEXT,
    telefone TEXT,
    email TEXT,
    endereco TEXT,
    cidade TEXT,
    uf TEXT,
    responsavel TEXT,
    logo_path TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS obras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    cliente_contratante TEXT,
    local_obra TEXT,
    engenheiro_responsavel TEXT,
    data_inicio DATE,
    previsao_termino DATE,
    status TEXT DEFAULT 'Em andamento',
    valor_contratado_inicial REAL NOT NULL DEFAULT 0,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS aditivos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    obra_id INTEGER NOT NULL,
    data_aditivo DATE NOT NULL,
    descricao TEXT NOT NULL,
    valor REAL NOT NULL DEFAULT 0,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (obra_id) REFERENCES obras(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tipos_lancamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    ativo INTEGER DEFAULT 1,
    ordem_exibicao INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS lancamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    obra_id INTEGER NOT NULL,
    tipo_lancamento_id INTEGER,
    data_lancamento DATE NOT NULL,
    descricao TEXT NOT NULL,
    complemento TEXT,
    quantidade REAL,
    unidade TEXT,
    valor_unitario REAL,
    valor_total REAL NOT NULL DEFAULT 0,
    origem_informacao TEXT,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (obra_id) REFERENCES obras(id) ON DELETE CASCADE,
    FOREIGN KEY (tipo_lancamento_id) REFERENCES tipos_lancamento(id)
);

CREATE TABLE IF NOT EXISTS anexos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    obra_id INTEGER NOT NULL,
    lancamento_id INTEGER,
    tipo_anexo TEXT,
    nome_original TEXT NOT NULL,
    nome_armazenado TEXT NOT NULL,
    caminho_relativo TEXT NOT NULL,
    hash_arquivo TEXT,
    mime_type TEXT,
    tamanho_bytes INTEGER DEFAULT 0,
    data_documento DATE,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (obra_id) REFERENCES obras(id) ON DELETE CASCADE,
    FOREIGN KEY (lancamento_id) REFERENCES lancamentos(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS relatorios_gerados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    obra_id INTEGER NOT NULL,
    tipo_relatorio TEXT NOT NULL,
    arquivo_gerado TEXT NOT NULL,
    data_geracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observacoes TEXT,
    FOREIGN KEY (obra_id) REFERENCES obras(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS configuracoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chave TEXT NOT NULL UNIQUE,
    valor TEXT,
    descricao TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO tipos_lancamento (nome, ordem_exibicao) VALUES
    ('Material', 1),
    ('Mao de obra', 2),
    ('Manutencao', 3),
    ('Outros', 4);

-- Desativa tipo removido (Servico) e suas variantes
UPDATE tipos_lancamento SET ativo = 0, ordem_exibicao = 99 WHERE LOWER(nome) LIKE '%servi%';

-- Desativa variantes com acento (mantendo apenas os nomes canonicos acima)
UPDATE tipos_lancamento SET ativo = 0, ordem_exibicao = 99
WHERE nome IN ('Mao de obra', 'Manutencao')
AND id NOT IN (
    SELECT MIN(id) FROM tipos_lancamento
    WHERE nome IN ('Mao de obra', 'Manutencao')
);

-- Limpa duplicatas restantes (mantendo menor id por nome)
DELETE FROM tipos_lancamento
WHERE ativo = 0 AND id NOT IN (
    SELECT MIN(id) FROM tipos_lancamento WHERE ativo = 0 GROUP BY nome
);

-- Migracao de origens antigas para novas (compatibilidade DB existente)
UPDATE lancamentos SET origem_informacao = 'Outros'
WHERE origem_informacao IN ('Cupom', 'Nota geral');

UPDATE lancamentos SET origem_informacao = 'Planilha orçamentária'
WHERE origem_informacao IN ('Planilha de diretoria', 'Planilha de engenharia');
"""


class DatabaseManager:
    """Gerencia conexão e schema do SQLite."""

    def __init__(self, db_path: Path | str = "data/app.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connections: list[sqlite3.Connection] = []

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        self._connections.append(conn)
        return conn

    def close_all(self) -> None:
        """Fecha todas as conexões rastreadas abertas."""
        for conn in self._connections:
            with contextlib.suppress(sqlite3.Error):
                conn.close()
        self._connections.clear()
        gc.collect()

    def init_schema(self) -> None:
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            self._run_migrations(conn)

    def _run_migrations(self, conn: sqlite3.Connection) -> None:
        """Executa migracoes para bancos existentes."""
        try:
            # Checa se coluna logo_path ja existe na tabela empresa
            has_logo = False
            for col in conn.execute("PRAGMA table_info(empresa)"):
                if col[1] == "logo_path":
                    has_logo = True
                    break
                    
            if not has_logo:
                conn.execute("ALTER TABLE empresa ADD COLUMN logo_path TEXT DEFAULT ''")
        except Exception:
            pass

    def execute(
        self, sql: str, params: tuple[Any, ...] | dict[str, Any] | None = None
    ) -> sqlite3.Cursor:
        with self.get_connection() as conn:
            return conn.execute(sql, params or ())

    def executemany(
        self, sql: str, params: list[tuple[Any, ...]] | None = None
    ) -> sqlite3.Cursor:
        with self.get_connection() as conn:
            return conn.executemany(sql, params or [])
