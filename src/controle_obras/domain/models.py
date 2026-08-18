"""Entidades de domínio do sistema de controle de obras."""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal


@dataclass
class Empresa:
    """Empresa proprietária do sistema."""

    id: int | None = None
    razao_social: str = ""
    nome_fantasia: str = ""
    cnpj: str = ""
    telefone: str = ""
    email: str = ""
    endereco: str = ""
    cidade: str = ""
    uf: str = ""
    responsavel: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Obra:
    """Obra: entidade central do sistema."""

    id: int | None = None
    codigo: str = ""
    nome: str = ""
    cliente_contratante: str = ""
    local_obra: str = ""
    engenheiro_responsavel: str = ""
    data_inicio: date | None = None
    previsao_termino: date | None = None
    status: str = "Em andamento"
    valor_contratado_inicial: Decimal = field(default_factory=lambda: Decimal("0.00"))
    observacoes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if self.valor_contratado_inicial is None:
            self.valor_contratado_inicial = Decimal("0.00")


@dataclass
class Aditivo:
    """Acréscimo financeiro ao valor contratado da obra."""

    id: int | None = None
    obra_id: int = 0
    data_aditivo: date = field(default_factory=date.today)
    descricao: str = ""
    valor: Decimal = field(default_factory=lambda: Decimal("0.00"))
    observacoes: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TipoLancamento:
    """Classificação macro de um lançamento."""

    id: int | None = None
    nome: str = ""
    ativo: bool = True
    ordem_exibicao: int = 0


@dataclass
class Lancamento:
    """Gasto individual lançado manualmente dentro de uma obra."""

    id: int | None = None
    obra_id: int = 0
    tipo_lancamento_id: int | None = None
    tipo_nome: str = ""
    data_lancamento: date = field(default_factory=date.today)
    descricao: str = ""
    complemento: str = ""
    quantidade: Decimal | None = None
    unidade: str = ""
    valor_unitario: Decimal | None = None
    valor_total: Decimal = field(default_factory=lambda: Decimal("0.00"))
    origem_informacao: str = ""
    observacoes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if self.valor_total is None:
            self.valor_total = Decimal("0.00")


@dataclass
class Anexo:
    """Arquivo vinculado a uma obra ou a um lançamento."""

    id: int | None = None
    obra_id: int = 0
    lancamento_id: int | None = None
    tipo_anexo: str = ""
    nome_original: str = ""
    nome_armazenado: str = ""
    caminho_relativo: str = ""
    hash_arquivo: str = ""
    mime_type: str = ""
    tamanho_bytes: int = 0
    data_documento: date | None = None
    observacoes: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RelatorioGerado:
    """Histórico de relatórios emitidos."""

    id: int | None = None
    obra_id: int = 0
    tipo_relatorio: str = ""
    arquivo_gerado: str = ""
    data_geracao: datetime = field(default_factory=datetime.now)
    observacoes: str = ""


@dataclass
class Configuracao:
    """Parâmetros persistentes do sistema."""

    id: int | None = None
    chave: str = ""
    valor: str = ""
    descricao: str = ""
    updated_at: datetime = field(default_factory=datetime.now)
