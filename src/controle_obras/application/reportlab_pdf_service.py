"""Gerador de relatorio PDF usando ReportLab Platypus com arquitetura de componentes.

Layout profissional com:
- Cabecalho com faixa colorida e identidade visual
- Card de informacoes da obra
- Tabelas com alinhamento preciso e zebrado
- Tipografia hierarquica consistente
- Rodape com numeracao de paginas
"""

import logging
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas


logger = logging.getLogger(__name__)


# ============================================
# DESIGN TOKENS
# ============================================

CORES = {
    "primaria": colors.HexColor("#1B2A4A"),  # Azul marinho (PRIMARY do app)
    "secundaria": colors.HexColor("#6B7280"),  # Cinza medio
    "sucesso": colors.HexColor("#16A34A"),
    "fundo_claro": colors.HexColor("#F9FAFB"),
    "borda": colors.HexColor("#E5E7EB"),
    "borda_suave": colors.HexColor("#D1D5DB"),  # Borda cinza clara para tabelas
    "texto_escuro": colors.HexColor("#000000"),
    "texto_cinza": colors.HexColor("#6B7280"),
    "branco": colors.white,
    # Cores para valores do resumo financeiro
    "azul_contratado": colors.HexColor("#2563EB"),
    "azul_aditivos": colors.HexColor("#3B82F6"),  # Azul mais claro
    "vermelho_gasto": colors.HexColor("#DC2626"),
    "verde_liquido": colors.HexColor("#16A34A"),
}

FONTES = {
    "tamanho_titulo": 20,  # Mantido
    "tamanho_subtitulo": 16,  # Aumentado de 15pt
    "tamanho_secao": 12,
    "tamanho_texto": 9,
    "tamanho_tabela": 8.5,
    "tamanho_rodape": 8,
}

ESPACAMENTO = {
    "secao_antes": 12,
    "secao_depois": 6,
    "tabela_antes": 8,
    "tabela_depois": 8,
    "linha_tabela": 10,
}

# Layout grid
MARGENS = {
    "esquerda": 1.5 * cm,
    "direita": 1.5 * cm,
    "cima": 1.5 * cm,
    "baixo": 1.8 * cm,
}
LARGURA_UTIL = A4[0] - MARGENS["esquerda"] - MARGENS["direita"]


class NumberedCanvas(Canvas):
    """Canvas com numeracao de paginas e rodape padronizado."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.page_number = 1

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._saved_page_states[-1]["page_number"] = self.page_number
        self.page_number += 1
        super().showPage()

    def save(self) -> None:
        page_count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_footer(state["page_number"], page_count)
        super().save()

    def _draw_footer(self, page_num: int, total_pages: int) -> None:
        """Desenha rodape com numero da pagina."""
        self.saveState()
        self.setFillColor(CORES["texto_cinza"])
        
        # Linha superior do rodape
        self.setStrokeColor(CORES["borda"])
        self.setLineWidth(0.5)
        self.line(MARGENS["esquerda"], 1.2 * cm, A4[0] - MARGENS["direita"], 1.2 * cm)
        
        # Numero da pagina
        self.setFont("FonteNormal", FONTES["tamanho_rodape"])
        self.drawCentredString(
            A4[0] / 2,
            0.8 * cm,
            f"Pagina {page_num} de {total_pages}"
        )
        self.restoreState()


def _canvas_maker(canvas_cls):
    """Factory para criar canvas customizado."""
    def make_canvas(*args, **kwargs):
        return canvas_cls(*args, **kwargs)
    return make_canvas


def _registrar_fontes() -> tuple[str, str]:
    """Registra fontes TrueType Unicode. Retorna (fonte_normal, fonte_bold)."""
    caminhos_fontes = [
        ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
        ("C:/Windows/Fonts/verdana.ttf", "C:/Windows/Fonts/verdanab.ttf"),
        ("C:/Windows/Fonts/times.ttf", "C:/Windows/Fonts/timesbd.ttf"),
    ]
    
    for caminho_normal, caminho_bold in caminhos_fontes:
        if os.path.exists(caminho_normal):
            try:
                pdfmetrics.registerFont(TTFont("FonteNormal", caminho_normal))
                if os.path.exists(caminho_bold):
                    pdfmetrics.registerFont(TTFont("FonteBold", caminho_bold))
                    return "FonteNormal", "FonteBold"
                else:
                    pdfmetrics.registerFont(TTFont("FonteBold", caminho_normal))
                    return "FonteNormal", "FonteBold"
            except Exception as e:
                print(f"[FONTE] Erro ao registrar {caminho_normal}: {e}")
                continue
    
    print("[FONTE] Usando Helvetica como fallback")
    return "Helvetica", "Helvetica-Bold"


def _criar_estilos(fonte_normal: str, fonte_bold: str) -> dict:
    """Cria estilos de paragrafo para o relatorio."""
    base = getSampleStyleSheet()
    
    return {
        "Titulo": ParagraphStyle(
            name="Titulo",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=FONTES["tamanho_titulo"],
            alignment=TA_CENTER,  # Centralizado
            spaceAfter=8,  # Aumentado de 4pt para mais espacamento
        ),
        "Subtitulo": ParagraphStyle(
            name="Subtitulo",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=FONTES["tamanho_subtitulo"],
            alignment=TA_CENTER,  # Centralizado
            spaceAfter=6,  # Reduzido para aproximar da emissao
            textColor=CORES["primaria"],
        ),
        "Emissao": ParagraphStyle(
            name="Emissao",
            parent=base["Normal"],
            fontName=fonte_bold,  # Negrito
            fontSize=11,  # Aumentado de 9pt
            alignment=TA_CENTER,  # Centralizado
            spaceAfter=8,
            spaceBefore=4,
        ),
        "Secao": ParagraphStyle(
            name="Secao",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=FONTES["tamanho_secao"],
            spaceBefore=ESPACAMENTO["secao_antes"],
            spaceAfter=ESPACAMENTO["secao_depois"],
            textColor=CORES["primaria"],
        ),
        "SecaoCentralizada": ParagraphStyle(
            name="SecaoCentralizada",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=FONTES["tamanho_secao"],
            alignment=TA_CENTER,  # Centralizado
            spaceBefore=ESPACAMENTO["secao_antes"],
            spaceAfter=ESPACAMENTO["secao_depois"],
            textColor=CORES["primaria"],
        ),
        "Texto": ParagraphStyle(
            name="Texto",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=FONTES["tamanho_texto"],
            leading=ESPACAMENTO["linha_tabela"],
        ),
        "TabelaCabecalho": ParagraphStyle(
            name="TabelaCabecalho",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=FONTES["tamanho_tabela"],
            textColor=CORES["branco"],
            alignment=TA_CENTER,
        ),
        "TabelaTexto": ParagraphStyle(
            name="TabelaTexto",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=FONTES["tamanho_tabela"],
            leading=ESPACAMENTO["linha_tabela"],
        ),
        "TabelaTextoDireita": ParagraphStyle(
            name="TabelaTextoDireita",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=FONTES["tamanho_tabela"],
            alignment=TA_RIGHT,
        ),
        # Estilos coloridos para valores do resumo financeiro
        "TabelaValorAzul": ParagraphStyle(
            name="TabelaValorAzul",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=11,
            textColor=CORES["azul_contratado"],
            alignment=TA_CENTER,
        ),
        "TabelaValorAzulClaro": ParagraphStyle(
            name="TabelaValorAzulClaro",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=11,
            textColor=CORES["azul_aditivos"],
            alignment=TA_CENTER,
        ),
        "TabelaValorVermelho": ParagraphStyle(
            name="TabelaValorVermelho",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=11,
            textColor=CORES["vermelho_gasto"],
            alignment=TA_CENTER,
        ),
        "TabelaValorVerde": ParagraphStyle(
            name="TabelaValorVerde",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=11,
            textColor=CORES["verde_liquido"],
            alignment=TA_CENTER,
        ),
        "AnexoNome": ParagraphStyle(
            name="AnexoNome",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=8.5,
            leading=10,
        ),
        "AnexoMeta": ParagraphStyle(
            name="AnexoMeta",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=7.5,
            textColor=CORES["texto_cinza"],
            leading=9,
        ),
        "Assinatura": ParagraphStyle(
            name="Assinatura",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=11,
            alignment=TA_CENTER,
            spaceBefore=4,
        ),
        "AssinaturaCargo": ParagraphStyle(
            name="AssinaturaCargo",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=9,
            textColor=CORES["texto_cinza"],
            alignment=TA_CENTER,
        ),
    }


def _formatar_data(valor: Any) -> str:
    """Formata data para dd/mm/aaaa."""
    if valor is None:
        return ""
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


def _formatar_moeda(valor: Decimal) -> str:
    """Formata valor monetario para R$ 1.234,56."""
    if valor is None:
        valor = Decimal("0.00")
    fmt = f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {fmt}"


def _formatar_tamanho(tamanho_bytes: int) -> str:
    """Formata tamanho de arquivo."""
    if tamanho_bytes >= 1024 * 1024:
        return f"{tamanho_bytes / (1024 * 1024):.1f} MB"
    elif tamanho_bytes >= 1024:
        return f"{tamanho_bytes / 1024:.1f} KB"
    return f"{tamanho_bytes} B"


def _texto(valor: Any, padrao: str = "") -> str:
    """Retorna string segura, tratando None."""
    return padrao if valor is None else str(valor)


# ============================================
# COMPONENTES DE LAYOUT
# ============================================

def _build_cabecalho(obra: Any, estilos: dict, fonte_bold: str, base: Any) -> list:
    """Constroi cabecalho com titulo e informacoes basicas.
    
    Layout:
    - Titulo centralizado
    - Subtitulo centralizado
    - Emissao (data) centralizada, negrito, fonte 11pt
    - Tabela de informacoes com labels em negrito/maiusculo/fonte 10pt
    """
    elementos = []
    
    # Titulo principal (centralizado)
    elementos.append(Paragraph("RELATORIO DA OBRA", estilos["Titulo"]))
    
    # Subtitulo com nome da obra (centralizado)
    elementos.append(Paragraph(_texto(obra.nome, "Obra sem nome"), estilos["Subtitulo"]))
    
    # Emissao (data) - centralizada, negrito, fonte maior
    elementos.append(Paragraph(
        f"Emissao: {datetime.now().strftime('%d/%m/%Y')}",
        estilos["Emissao"]
    ))
    
    elementos.append(Spacer(1, 6))
    
    # Grid de informacoes (tabela com borda cinza clara)
    # Labels em negrito, maiusculas e fonte 10pt
    info_label_style = ParagraphStyle(
        name="InfoLabel",
        parent=base["Normal"],
        fontName=fonte_bold,
        fontSize=10,
    )
    
    info_data = [
        [
            Paragraph("CÓDIGO:", info_label_style),
            Paragraph(_texto(obra.codigo), estilos["Texto"]),
            Paragraph("CLIENTE:", info_label_style),
            Paragraph(_texto(obra.cliente_contratante, 'Nao informado'), estilos["Texto"]),
        ],
        [
            Paragraph("LOCAL:", info_label_style),
            Paragraph(_texto(obra.local_obra, 'Nao informado'), estilos["Texto"]),
            Paragraph("ENGENHEIRO:", info_label_style),
            Paragraph(_texto(obra.engenheiro_responsavel, 'Nao informado'), estilos["Texto"]),
        ],
    ]
    info_table = Table(info_data, colWidths=[LARGURA_UTIL / 4, LARGURA_UTIL / 4, LARGURA_UTIL / 4, LARGURA_UTIL / 4])
    info_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        # Borda cinza clara ao redor
        ("GRID", (0, 0), (-1, -1), 0.5, CORES["borda_suave"]),
        ("BACKGROUND", (0, 0), (-1, -1), CORES["fundo_claro"]),
    ]))
    elementos.append(info_table)
    elementos.append(Spacer(1, 10))
    
    return elementos


def _build_resumo_financeiro(resumo: Any, estilos: dict) -> list:
    """Constroi tabela de resumo financeiro com destaque e cores.
    
    Cores dos valores:
    - Valor Contratado: Azul (#2563EB)
    - Total Aditivos: Azul claro (#3B82F6)
    - Total Gasto: Vermelho (#DC2626)
    - Valor Liquido: Verde (#16A34A)
    """
    elementos = []
    
    # Titulo centralizado
    elementos.append(Paragraph("RESUMO FINANCEIRO", estilos["SecaoCentralizada"]))
    
    # Tabela de resumo
    resumo_data = [
        ["Valor Contratado", "Total Aditivos", "Total Gasto", "Valor Liquido"],
        [
            Paragraph(_formatar_moeda(resumo.valor_contratado), estilos["TabelaValorAzul"]),
            Paragraph(_formatar_moeda(resumo.total_aditivos), estilos["TabelaValorAzulClaro"]),
            Paragraph(_formatar_moeda(resumo.total_gasto), estilos["TabelaValorVermelho"]),
            Paragraph(_formatar_moeda(resumo.valor_liquido), estilos["TabelaValorVerde"]),
        ],
    ]
    
    # Colunas de largura igual
    col_width = LARGURA_UTIL / 4
    
    resumo_table = Table(resumo_data, colWidths=[col_width] * 4)
    resumo_table.setStyle(TableStyle([
        # Cabecalho
        ("BACKGROUND", (0, 0), (-1, 0), CORES["secundaria"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), CORES["branco"]),
        ("FONTNAME", (0, 0), (-1, 0), "FonteBold"),
        ("FONTSIZE", (0, 0), (-1, -1), FONTES["tamanho_tabela"]),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, CORES["borda"]),
        # Linha de valores com fundo e destaque
        ("BACKGROUND", (0, 1), (-1, 1), CORES["fundo_claro"]),
        ("FONTSIZE", (0, 1), (-1, 1), 11),
        ("HEIGHT", (0, 1), (-1, 1), 30),
    ]))
    elementos.append(resumo_table)
    elementos.append(Spacer(1, ESPACAMENTO["tabela_depois"]))
    
    return elementos


def _build_tabela_padrao(
    titulo: str,
    colunas: list[str],
    dados: list[list[str]],
    larguras_colunas: list[float],
    estilos: dict,
    fonte_normal: str,
    fonte_bold: str,
    alinhar_direita: list[bool] | None = None,
) -> list:
    """Constroi tabela padrao com cabecalho colorido e linhas zebradas.
    
    Args:
        titulo: Titulo da secao.
        colunas: Lista de nomes das colunas.
        dados: Lista de linhas de dados.
        larguras_colunas: Larguras em pixel ou fracao de LARGURA_UTIL.
        estilos: Dicionario de estilos.
        fonte_normal: Nome da fonte normal.
        fonte_bold: Nome da fonte em negrito.
        alinhar_direita: Lista de bool indicando quais colunas alinhar a direita.
    """
    elementos = []
    elementos.append(Paragraph(titulo, estilos["Secao"]))
    
    if not dados:
        return elementos
    
    # Monteiro tabela com cabecalho + dados
    tabelaDados = [colunas] + dados
    num_cols = len(colunas)
    
    # Converter larguras relativas para absolutas se necessario
    larguras = [
        w if isinstance(w, (int, float)) and w > 1 else LARGURA_UTIL * w
        for w in larguras_colunas
    ]
    
    table = Table(tabelaDados, colWidths=larguras, repeatRows=1)
    
    # Construir estilo basico
    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), CORES["primaria"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), CORES["branco"]),
        ("FONTNAME", (0, 0), (-1, 0), fonte_bold),
        ("FONTNAME", (0, 1), (-1, -1), fonte_normal),
        ("FONTSIZE", (0, 0), (-1, -1), FONTES["tamanho_tabela"]),
        ("GRID", (0, 0), (-1, -1), 0.5, CORES["borda"]),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    
    # Linhas zebradas
    for i in range(len(dados)):
        if (i + 1) % 2 == 0:  # Linhas pares (0-indexed dados, mas 1-indexed na tabela completa)
            style_commands.append(("BACKGROUND", (0, i + 1), (-1, i + 1), CORES["fundo_claro"]))
    
    # Alinhamento por coluna
    for col_idx in range(num_cols):
        if alinhar_direita and col_idx < len(alinhar_direita) and alinhar_direita[col_idx]:
            style_commands.append(("ALIGN", (col_idx, 0), (col_idx, -1), "RIGHT"))
        else:
            style_commands.append(("ALIGN", (col_idx, 0), (col_idx, -1), "LEFT"))
    
    table.setStyle(TableStyle(style_commands))
    elementos.append(table)
    elementos.append(Spacer(1, ESPACAMENTO["tabela_depois"]))
    
    return elementos


def _build_anexos_lista(anexos: list, estilos: dict, fonte_normal: str) -> list:
    """Constroi lista de anexos com formato de blocos."""
    elementos = []
    elementos.append(Paragraph("ANEXOS", estilos["Secao"]))
    
    for i, a in enumerate(anexos):
        nome = _texto(a.nome_original, "Sem nome")
        tipo = _texto(a.tipo_anexo, "Nao informado")
        data_doc = a.data_documento or (a.created_at.date() if a.created_at else None)
        data = _formatar_data(data_doc)
        tamanho = _formatar_tamanho(a.tamanho_bytes or 0)
        
        anexo_grupo = KeepTogether([
            Paragraph(nome, estilos["AnexoNome"]),
            Paragraph(
                f"Tipo: {tipo} | Data: {data} | Tamanho: {tamanho}",
                estilos["AnexoMeta"],
            ),
            Spacer(1, 4),
        ])
        elementos.append(anexo_grupo)
        
        # Linha separadora (exceto no ultimo)
        if i < len(anexos) - 1:
            elementos.append(HRFlowable(
                width=LARGURA_UTIL,
                thickness=0.5,
                color=CORES["borda"],
                spaceAfter=4,
            ))
    
    elementos.append(Spacer(1, ESPACAMENTO["tabela_depois"]))
    return elementos


def _build_assinatura(responsavel: str, cnpj: str, estilos: dict) -> list:
    """Constroi bloco de assinatura."""
    elementos = []
    
    if not responsavel:
        return elementos
    
    elementos.append(Spacer(1, 15))
    
    # Linha de assinatura
    elementos.append(HRFlowable(
        width=LARGURA_UTIL * 0.5,
        thickness=1,
        color=CORES["texto_escuro"],
        spaceAfter=4,
    ))
    
    # Nome do responsavel
    assinatura_data = [[Paragraph(responsavel, estilos["Assinatura"])]]
    assinatura_table = Table(assinatura_data, colWidths=[LARGURA_UTIL])
    assinatura_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elementos.append(assinatura_table)
    
    # CNPJ ou cargo
    if cnpj:
        elementos.append(Paragraph(f"CNPJ: {cnpj}", estilos["AssinaturaCargo"]))
    else:
        elementos.append(Paragraph("Responsavel Legal", estilos["AssinaturaCargo"]))
    
    return elementos


# ============================================
# SERVICO PRINCIPAL
# ============================================

class ReportLabPDFService:
    """Servico de geracao de relatorios PDF usando ReportLab Platypus."""

    def __init__(
        self,
        obra_service: Any,
        aditivo_service: Any,
        lancamento_service: Any,
        anexo_service: Any,
        resumo_service: Any,
        relatorio_repo: Any,
        storage: Any,
        empresa_service: Any | None = None,
    ) -> None:
        self._obra_service = obra_service
        self._aditivo_service = aditivo_service
        self._lancamento_service = lancamento_service
        self._anexo_service = anexo_service
        self._resumo_service = resumo_service
        self._relatorio_repo = relatorio_repo
        self._storage = storage
        self._empresa_service = empresa_service

    def _obter_responsavel(self) -> str:
        """Obtem o nome do responsavel da empresa."""
        if self._empresa_service is None:
            return ""
        try:
            empresa = self._empresa_service.obter()
            if empresa and empresa.responsavel:
                return empresa.responsavel
            return ""
        except Exception:
            return ""

    def _obter_cnpj(self) -> str:
        """Obtem o CNPJ da empresa."""
        if self._empresa_service is None:
            return ""
        try:
            empresa = self._empresa_service.obter()
            if empresa and empresa.cnpj:
                return empresa.cnpj
            return ""
        except Exception:
            return ""

    def gerar_relatorio_obra_reportlab(self, obra_id: int) -> Path:
        """Gera relatorio PDF usando ReportLab Platypus com componentes.
        
        Args:
            obra_id: ID da obra para gerar o relatorio.
            
        Returns:
            Path do arquivo PDF gerado.
            
        Raises:
            ValueError: Se a obra nao for encontrada ou erro na geracao.
        """
        print(f"[PDF] Gerador: ReportLab")
        print(f"[PDF] Obra: {obra_id}")
        
        # Obter dados
        obra = self._obra_service.obter(obra_id)
        if not obra:
            raise ValueError(f"Obra {obra_id} não encontrada.")

        resumo = self._resumo_service.calcular_resumo(obra_id)
        aditivos = self._aditivo_service.listar_por_obra(obra_id)
        lancamentos = self._lancamento_service.listar_por_obra(obra_id)
        anexos = self._anexo_service.listar_por_obra(obra_id)

        # Configurar arquivo na pasta Downloads
        downloads_dir = Path.home() / "Downloads"
        downloads_dir.mkdir(exist_ok=True)
        
        filename = f"relatorio_obra_{obra.codigo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = downloads_dir / filename
        
        print(f"[PDF] Arquivo: {filepath}")

        # Registrar fontes e criar estilos
        fonte_normal, fonte_bold = _registrar_fontes()
        base = getSampleStyleSheet()
        estilos = _criar_estilos(fonte_normal, fonte_bold)

        # Criar documento
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            leftMargin=MARGENS["esquerda"],
            rightMargin=MARGENS["direita"],
            topMargin=MARGENS["cima"],
            bottomMargin=MARGENS["baixo"],
        )
        
        # Construir elementos usando componentes
        elementos = []
        
        # 1. Cabecalho
        elementos.extend(_build_cabecalho(obra, estilos, fonte_bold, base))
        
        # 2. Resumo financeiro
        elementos.extend(_build_resumo_financeiro(resumo, estilos))
        
        # 3. Aditivos
        if aditivos:
            aditivos_data = [
                [
                    _formatar_data(a.data_aditivo),
                    _texto(a.descricao, "Sem descricao"),
                    _formatar_moeda(a.valor),
                ]
                for a in aditivos
            ]
            elementos.extend(_build_tabela_padrao(
                titulo="ADITIVOS",
                colunas=["Data", "Descricao", "Valor"],
                dados=aditivos_data,
                larguras_colunas=[0.20, 0.55, 0.25],
                estilos=estilos,
                fonte_normal=fonte_normal,
                fonte_bold=fonte_bold,
                alinhar_direita=[False, False, True],
            ))

        # 4. Lancamentos
        if lancamentos:
            # Filtrar lancamentos sem tipo para evitar warnings
            lancamentos_validos = [
                l for l in lancamentos
                if getattr(l, "tipo_nome", None) and l.tipo_nome.strip()
            ]
            
            if lancamentos_validos:
                lancamentos_data = [
                    [
                        _formatar_data(l.data_lancamento),
                        _texto(l.descricao, "Sem descricao"),
                        _texto(l.tipo_nome, "Nao informado"),
                        _formatar_moeda(l.valor_total),
                    ]
                    for l in lancamentos_validos
                ]
                elementos.extend(_build_tabela_padrao(
                    titulo="LANCAMENTOS",
                    colunas=["Data", "Descricao", "Tipo", "Valor"],
                    dados=lancamentos_data,
                    larguras_colunas=[0.15, 0.40, 0.20, 0.25],
                    estilos=estilos,
                    fonte_normal=fonte_normal,
                    fonte_bold=fonte_bold,
                    alinhar_direita=[False, False, False, True],
                ))

        # 5. Anexos
        if anexos:
            elementos.extend(_build_anexos_lista(anexos, estilos, fonte_normal))

        # 6. Assinatura
        responsavel = self._obter_responsavel()
        cnpj = self._obter_cnpj()
        elementos.extend(_build_assinatura(responsavel, cnpj, estilos))

        # Gerar PDF
        doc.build(elementos, canvasmaker=_canvas_maker(NumberedCanvas))
        
        # Registrar no repositorio
        from controle_obras.domain.models import RelatorioGerado
        
        self._relatorio_repo.save(
            RelatorioGerado(
                obra_id=obra_id,
                tipo_relatorio="obra",
                arquivo_gerado=str(filepath),
            )
        )
        
        print(f"[PDF] Status: sucesso")
        
        # Abrir PDF automaticamente
        try:
            os.startfile(str(filepath))
            print(f"[PDF] Aberto: {filepath}")
        except Exception as e:
            print(f"[PDF] Nao foi possivel abrir automaticamente: {e}")
        
        return filepath
