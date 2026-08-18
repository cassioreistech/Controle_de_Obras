"""
PDF Generator Template - Relatórios Profissionais com ReportLab

Template pronto para usar em qualquer sistema Python que precise gerar PDFs.
Inclui design tokens, componentes reutilizáveis e layout profissional.

Instalação:
    pip install reportlab

Uso básico:
    from pdf_generator import PDFReportGenerator
    
    generator = PDFReportGenerator()
    pdf_path = generator.generate(
        titulo="RELATORIO",
        subtitulo="Nome do Projeto",
        dados={...},
        tabelas=[...],
        output_dir=Path("~/Downloads").expanduser()
    )
"""

import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
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


# ============================================
# DESIGN TOKENS - Personalize aqui
# ============================================

CORES = {
    "primaria": colors.HexColor("#1B2A4A"),      # Cor principal da empresa
    "secundaria": colors.HexColor("#6B7280"),    # Cor secundária
    "sucesso": colors.HexColor("#16A34A"),
    "perigo": colors.HexColor("#DC2626"),
    "fundo_claro": colors.HexColor("#F9FAFB"),
    "borda": colors.HexColor("#E5E7EB"),
    "texto_escuro": colors.HexColor("#000000"),
    "texto_cinza": colors.HexColor("#6B7280"),
    "branco": colors.white,
    
    # Cores para valores (opcional)
    "azul_1": colors.HexColor("#2563EB"),
    "azul_2": colors.HexColor("#3B82F6"),
    "vermelho": colors.HexColor("#DC2626"),
    "verde": colors.HexColor("#16A34A"),
}

FONTES = {
    "tamanho_titulo": 20,
    "tamanho_subtitulo": 16,
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
}

MARGENS = {
    "esquerda": 1.5 * cm,
    "direita": 1.5 * cm,
    "cima": 1.5 * cm,
    "baixo": 1.8 * cm,
}

LARGURA_UTIL = A4[0] - MARGENS["esquerda"] - MARGENS["direita"]


# ============================================
# CANVAS CUSTOMIZADO
# ============================================

class SimpleCanvas(Canvas):
    """Canvas com rodapé simples (linha divisória)."""
    
    def showPage(self) -> None:
        self._draw_footer()
        super().showPage()
    
    def _draw_footer(self) -> None:
        """Desenha linha do rodapé."""
        self.saveState()
        self.setStrokeColor(CORES["borda"])
        self.setLineWidth(0.5)
        self.line(
            MARGENS["esquerda"], 
            1.2 * cm, 
            A4[0] - MARGENS["direita"], 
            1.2 * cm
        )
        self.restoreState()


# ============================================
# UTILITÁRIOS
# ============================================

def registrar_fontes() -> tuple[str, str]:
    """
    Registra fontes TrueType. Retorna (fonte_normal, fonte_bold).
    
    Tenta Arial, Verdana, Times. Fallback para Helvetica.
    """
    caminhos_fontes = [
        ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
        ("C:/Windows/Fonts/verdana.ttf", "C:/Windows/Fonts/verdanab.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
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
                print(f"[FONTE] Erro: {e}")
                continue
    
    return "Helvetica", "Helvetica-Bold"


def criar_estilos(fonte_normal: str, fonte_bold: str) -> dict:
    """Cria estilos de parágrafo para o relatório."""
    base = getSampleStyleSheet()
    
    return {
        "Titulo": ParagraphStyle(
            name="Titulo",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=FONTES["tamanho_titulo"],
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "Subtitulo": ParagraphStyle(
            name="Subtitulo",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=FONTES["tamanho_subtitulo"],
            alignment=TA_CENTER,
            spaceAfter=10,
            textColor=CORES["primaria"],
        ),
        "Emissao": ParagraphStyle(
            name="Emissao",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=8,
            spaceBefore=4,
            textColor=CORES["texto_cinza"],
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
            alignment=TA_CENTER,
            spaceBefore=ESPACAMENTO["secao_antes"],
            spaceAfter=ESPACAMENTO["secao_depois"],
            textColor=CORES["primaria"],
        ),
        "Texto": ParagraphStyle(
            name="Texto",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=FONTES["tamanho_texto"],
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
        ),
        "TabelaTextoDireita": ParagraphStyle(
            name="TabelaTextoDireita",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=FONTES["tamanho_tabela"],
            alignment=TA_RIGHT,
        ),
        "TabelaValorColorido": ParagraphStyle(
            name="TabelaValorColorido",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=11,
            textColor=CORES["azul_1"],
            alignment=TA_CENTER,
        ),
    }


def _texto(valor: Any, padrao: str = "") -> str:
    """Retorna string segura, tratando None."""
    return padrao if valor is None else str(valor)


def _formatar_data(valor: Any) -> str:
    """Formata data para dd/mm/aaaa."""
    if not valor:
        return ""
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


def _formatar_moeda(valor: Decimal | float) -> str:
    """Formata valor monetário para R$ 1.234,56."""
    if valor is None:
        valor = 0.0
    fmt = f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {fmt}"


# ============================================
# COMPONENTES DE LAYOUT
# ============================================

def build_cabecalho(
    titulo: str,
    subtitulo: str,
    data_emissao: Optional[str] = None,
    info_grid: Optional[list[list[str]]] = None,
    estilos: dict = None,
    fonte_bold: str = None,
    base: Any = None
) -> list:
    """
    Constrói cabeçalho com título, subtítulo e informações.
    
    Args:
        titulo: Título principal
        subtitulo: Subtítulo ou nome do projeto
        data_emissao: Data de emissão (default: hoje)
        info_grid: Lista de listas com informações [[label, valor], ...]
        estilos: Dicionário de estilos
        fonte_bold: Nome da fonte em negrito
    """
    elementos = []
    
    if data_emissao is None:
        data_emissao = datetime.now().strftime("%d/%m/%Y")
    
    # Título e subtítulo
    elementos.append(Paragraph(titulo, estilos["Titulo"]))
    elementos.append(Paragraph(subtitulo, estilos["Subtitulo"]))
    elementos.append(Paragraph(f"Data de emissão: {data_emissao}", estilos["Emissao"]))
    elementos.append(Spacer(1, 10))
    
    # Grid de informações (opcional)
    if info_grid:
        info_data = [[
            Paragraph(str(label).upper(), estilos["Texto"]),
            Paragraph(str(valor).upper(), ParagraphStyle(
                name="InfoValor",
                parent=base["Normal"],
                fontName=fonte_bold,
                fontSize=10,
                textColor=CORES["primaria"],
            ))
        ] for label, valor in info_grid]
        
        info_table = Table(info_data, colWidths=[LARGURA_UTIL / 4] * 2)
        info_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, CORES["borda"]),
            ("BACKGROUND", (0, 0), (-1, -1), CORES["fundo_claro"]),
        ]))
        elementos.append(info_table)
        elementos.append(Spacer(1, 10))
    
    return elementos


def build_tabela(
    titulo: str,
    colunas: list[str],
    dados: list[list[str]],
    estilos: dict,
    fonte_normal: str,
    fonte_bold: str,
    larguras_colunas: Optional[list[float]] = None,
    cabecalho_maiusculo: bool = True,
    titulo_centralizado: bool = False,
    estilo_valor_col: Optional[int] = None,  # Índice da coluna com estilo colorido
) -> list:
    """
    Constrói tabela padrão com cabeçalho colorido.
    
    Args:
        titulo: Título da seção
        colunas: Lista de colunas
        dados: Lista de linhas [[col1, col2, ...], ...]
        estilos: Dicionário de estilos
        fonte_normal: Nome da fonte normal
        fonte_bold: Nome da fonte bold
        larguras_colunas: Larguras relativas (ex: [0.2, 0.5, 0.3])
        cabecalho_maiusculo: Se True, colunas em maiúsculas
        titulo_centralizado: Se True, centraliza título
        estilo_valor_col: Índice da coluna com estilo colorido
    """
    elementos = []
    
    # Título da seção
    if titulo_centralizado:
        elementos.append(Paragraph(titulo, estilos["SecaoCentralizada"]))
    else:
        elementos.append(Paragraph(titulo, estilos["Secao"]))
    
    if not dados:
        return elementos
    
    # Preparar colunas
    colunas_formatadas = [c.upper() for c in colunas] if cabecalho_maiusculo else colunas
    cabecalho = [Paragraph(col, estilos["TabelaCabecalho"]) for col in colunas_formatadas]
    
    # Preparar dados
    dados_formatados = []
    for linha in dados:
        linha_formatada = []
        for col_idx, valor in enumerate(linha):
            if estilo_valor_col is not None and col_idx == estilo_valor_col:
                linha_formatada.append(Paragraph(valor, estilos["TabelaValorColorido"]))
            else:
                linha_formatada.append(Paragraph(valor, estilos["TabelaTexto"]))
        dados_formatados.append(linha_formatada)
    
    # Montar tabela
    tabela_dados = [cabecalho] + dados_formatados
    
    # Calcular larguras
    if larguras_colunas:
        larguras = [
            w if isinstance(w, (int, float)) and w > 1 else LARGURA_UTIL * w
            for w in larguras_colunas
        ]
    else:
        larguras = [LARGURA_UTIL / len(colunas)] * len(colunas)
    
    table = Table(tabela_dados, colWidths=larguras, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), CORES["primaria"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), CORES["branco"]),
        ("FONTNAME", (0, 0), (-1, 0), fonte_bold),
        ("FONTSIZE", (0, 0), (-1, -1), FONTES["tamanho_tabela"]),
        ("GRID", (0, 0), (-1, -1), 0.5, CORES["borda"]),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
    ]))
    
    # Linhas zebradas
    for i in range(len(dados_formatados)):
        if (i + 1) % 2 == 0:
            table.setStyle(TableStyle([(
                "BACKGROUND", (0, i + 1), (-1, i + 1), CORES["fundo_claro"]
            )]))
    
    elementos.append(table)
    elementos.append(Spacer(1, ESPACAMENTO["tabela_depois"]))
    
    return elementos


def build_assinatura(
    responsavel: str,
    cargo_ou_cnpj: Optional[str] = None,
    espacamento: int = 20
) -> list:
    """
    Constrói bloco de assinatura.
    
    Args:
        responsavel: Nome do responsável
        cargo_ou_cnpj: Cargo ou CNPJ
        espacamento: Espaçamento antes da assinatura (padrão: 20)
    """
    elementos = []
    
    if not responsavel:
        return elementos
    
    elementos.append(Spacer(1, espacamento))
    
    # Linha de assinatura
    elementos.append(HRFlowable(
        width=LARGURA_UTIL * 0.5,
        thickness=1,
        color=CORES["texto_escuro"],
        spaceAfter=4,
    ))
    
    # Nome
    assinatura_style = ParagraphStyle(
        name="Assinatura",
        parent=getSampleStyleSheet()["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        alignment=TA_CENTER,
    )
    elementos.append(Paragraph(responsavel, assinatura_style))
    
    # Cargo ou CNPJ
    if cargo_ou_cnpj:
        cargo_style = ParagraphStyle(
            name="AssinaturaCargo",
            parent=getSampleStyleSheet()["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=CORES["texto_cinza"],
            alignment=TA_CENTER,
        )
        elementos.append(Paragraph(cargo_ou_cnpj, cargo_style))
    
    return elementos


# ============================================
# GERADOR PRINCIPAL
# ============================================

class PDFReportGenerator:
    """
    Gerador de relatórios PDF profissionais.
    
    Exemplo de uso:
        generator = PDFReportGenerator()
        pdf_path = generator.generate(
            titulo="RELATORIO DE OBRAS",
            subtitulo="Construção Civil - 2026",
            dados={
                "info_grid": [["Código", "001"], ["Cliente", "Empresa X"]],
                "tabelas": [
                    {
                        "titulo": "OBRAS",
                        "colunas": ["Nome", "Status", "Valor"],
                        "dados": [["Obra A", "Em andamento", "1000000"], ...]
                    }
                ],
                "responsavel": "Eng. João Silva",
                "cnpj": "00.000.000/0001-00"
            },
            output_dir=Path("~/Downloads").expanduser()
        )
    """
    
    def generate(
        self,
        titulo: str,
        subtitulo: str,
        dados: dict,
        output_dir: Path,
        filename: Optional[str] = None
    ) -> Path:
        """
        Gera relatório PDF.
        
        Args:
            titulo: Título principal
            subtitulo: Subtítulo
            dados: Dados do relatório (info_grid, tabelas, responsavel, cnpj)
            output_dir: Diretório de saída
            filename: Nome do arquivo (opcional)
        
        Returns:
            Path do PDF gerado
        """
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Nome do arquivo
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_{timestamp}.pdf"
        
        filepath = output_dir / filename
        
        # Configurar
        fonte_normal, fonte_bold = registrar_fontes()
        base = getSampleStyleSheet()
        estilos = criar_estilos(fonte_normal, fonte_bold)
        
        # Criar documento
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            leftMargin=MARGENS["esquerda"],
            rightMargin=MARGENS["direita"],
            topMargin=MARGENS["cima"],
            bottomMargin=MARGENS["baixo"],
        )
        
        # Construir elementos
        elementos = []
        
        # 1. Cabeçalho
        elementos.extend(build_cabecalho(
            titulo=titulo,
            subtitulo=subtitulo,
            info_grid=dados.get("info_grid"),
            estilos=estilos,
            fonte_bold=fonte_bold,
            base=base,
        ))
        
        # 2. Tabelas
        for tabela_config in dados.get("tabelas", []):
            elementos.extend(build_tabela(
                titulo=tabela_config.get("titulo", "DADOS"),
                colunas=tabela_config.get("colunas", []),
                dados=tabela_config.get("dados", []),
                estilos=estilos,
                fonte_normal=fonte_normal,
                fonte_bold=fonte_bold,
                larguras_colunas=tabela_config.get("larguras"),
                cabecalho_maiusculo=tabela_config.get("maiuculo", True),
                titulo_centralizado=tabela_config.get("titulo_centralizado", False),
                estilo_valor_col=tabela_config.get("coluna_colorida"),
            ))
        
        # 3. Assinatura
        if dados.get("responsavel"):
            elementos.extend(build_assinatura(
                responsavel=dados["responsavel"],
                cargo_ou_cnpj=dados.get("cnpj"),
                espacamento=dados.get("espacamento_assinatura", 20),
            ))
        
        # Gerar PDF
        doc.build(elementos, canvasmaker=SimpleCanvas)
        
        print(f"[PDF] Gerado: {filepath}")
        
        # Abrir automaticamente (Windows)
        try:
            os.startfile(str(filepath))
        except Exception:
            pass
        
        return filepath


# ============================================
# EXEMPLO DE USO (main)
# ============================================

if __name__ == "__main__":
    # Exemplo completo
    from decimal import Decimal
    
    generator = PDFReportGenerator()
    
    dados_exemplo = {
        "info_grid": [
            ["Código", "OBRA-001"],
            ["Cliente", "Construtora ABC"],
            ["Local", "São Paulo - SP"],
            ["Engenheiro", "João Silva"],
        ],
        "tabelas": [
            {
                "titulo": "RESUMO FINANCEIRO",
                "colunas": ["Contratado", "Aditivos", "Gasto", "Líquido"],
                "dados": [[
                    _formatar_moeda(Decimal("500000.00")),
                    _formatar_moeda(Decimal("50000.00")),
                    _formatar_moeda(Decimal("320000.00")),
                    _formatar_moeda(Decimal("230000.00")),
                ]],
                "larguras": [0.25, 0.25, 0.25, 0.25],
                "titulo_centralizado": True,
            },
            {
                "titulo": "ADITIVOS",
                "colunas": ["Data", "Descrição", "Valor"],
                "dados": [
                    ["10/01/2026", "ADIÇÃO DE GARAGEM", _formatar_moeda(Decimal("30000.00"))],
                    ["15/02/2026", "ACABAMENTO PREMIUM", _formatar_moeda(Decimal("20000.00"))],
                ],
                "larguras": [0.20, 0.55, 0.25],
                "titulo_centralizado": True,
                "coluna_colorida": 2,  # Última coluna com estilo colorido
            },
        ],
        "responsavel": "Eng. João Silva",
        "cnpj": "00.000.000/0001-00",
    }
    
    pdf_path = generator.generate(
        titulo="RELATORIO DA OBRA",
        subtitulo="Edifício Sunset - Barra Funda",
        dados=dados_exemplo,
        output_dir=Path.home() / "Downloads",
        filename="relatorio_obra_exemplo.pdf"
    )
    
    print(f"PDF gerado: {pdf_path}")
