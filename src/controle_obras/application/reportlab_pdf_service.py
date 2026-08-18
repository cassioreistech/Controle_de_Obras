"""Gerador de relatório PDF usando ReportLab Platypus."""

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
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas


class NumberedCanvas(Canvas):
    """Canvas com numeração de páginas."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.page_number = 1

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._saved_page_states[-1]['page_number'] = self.page_number
        self.page_number += 1
        super().showPage()

    def save(self) -> None:
        page_count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_rodape(state['page_number'], page_count)
        super().save()

    def draw_rodape(self, page_num: int, total_pages: int) -> None:
        """Desenha o rodapé da página."""
        self.saveState()
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#6B7280"))
        self.drawCentredString(
            A4[0] / 2,
            0.8 * cm,
            f"Página {page_num} de {total_pages}"
        )
        self.restoreState()


def _canvas_maker(canvas_cls):
    """Factory para criar canvas customizado."""
    def make_canvas(*args, **kwargs):
        return canvas_cls(*args, **kwargs)
    return make_canvas


def _registrar_fontes() -> tuple[str, str]:
    """Registra fontes TrueType Unicode. Retorna (fonte_normal, fonte_bold)."""
    # Caminhos possíveis para fontes no Windows
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
                    # Usa a mesma fonte para bold se bold não existir
                    pdfmetrics.registerFont(TTFont("FonteBold", caminho_normal))
                    return "FonteNormal", "FonteBold"
            except Exception as e:
                print(f"[FONTE] Erro ao registrar {caminho_normal}: {e}")
                continue
    
    # Fallback para fontes padrão (não Unicode)
    print("[FONTE] Usando Helvetica como fallback (pode não suportar acentos)")
    return "Helvetica", "Helvetica-Bold"


def _criar_estilos(fonte_normal: str, fonte_bold: str) -> dict[str, ParagraphStyle]:
    """Cria os estilos de parágrafo para o relatório."""
    base = getSampleStyleSheet()
    
    estilos = {
        "Titulo": ParagraphStyle(
            name="Titulo",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=5,
        ),
        "Subtitulo": ParagraphStyle(
            name="Subtitulo",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=13,
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "Secao": ParagraphStyle(
            name="Secao",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=12,
            spaceBefore=8,
            spaceAfter=5,
        ),
        "Texto": ParagraphStyle(
            name="Texto",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=9,
            leading=11,
        ),
        "TabelaCabecalho": ParagraphStyle(
            name="TabelaCabecalho",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=8.5,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
        "TabelaTexto": ParagraphStyle(
            name="TabelaTexto",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=8.5,
            leading=10,
        ),
        "TabelaTextoCentro": ParagraphStyle(
            name="TabelaTextoCentro",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=8.5,
            alignment=TA_CENTER,
        ),
        "TabelaTextoDireita": ParagraphStyle(
            name="TabelaTextoDireita",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=8.5,
            alignment=TA_RIGHT,
        ),
        "AnexoNome": ParagraphStyle(
            name="AnexoNome",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=8,
            leading=10,
        ),
        "AnexoMeta": ParagraphStyle(
            name="AnexoMeta",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=7.5,
            textColor=colors.HexColor("#6B7280"),
            leading=9,
        ),
        "AssinaturaNome": ParagraphStyle(
            name="AssinaturaNome",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=11,
            alignment=TA_CENTER,
        ),
        "AssinaturaCargo": ParagraphStyle(
            name="AssinaturaCargo",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=9,
            textColor=colors.HexColor("#6B7280"),
            alignment=TA_CENTER,
            spaceBefore=2,
        ),
    }
    
    return estilos


def _formatar_data(valor: Any) -> str:
    """Formata data para dd/mm/aaaa."""
    if valor is None:
        return ""
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


def _formatar_moeda(valor: Decimal) -> str:
    """Formata valor monetário para R$ 1.234,56."""
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
    """Retorna string segura, tratanto None."""
    return padrao if valor is None else str(valor)


def _obter_nome_tipo(tipo_id: int | None, tipos: list) -> str:
    """Obtém nome do tipo de lançamento."""
    if tipo_id is None:
        return ""
    for t in tipos:
        if hasattr(t, 'id') and t.id == tipo_id:
            return _texto(t.nome)
    return ""


class ReportLabPDFService:
    """Serviço de geração de relatórios PDF usando ReportLab Platypus."""

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
        tipo_lancamento_service: Any | None = None,
    ) -> None:
        self._obra_service = obra_service
        self._aditivo_service = aditivo_service
        self._lancamento_service = lancamento_service
        self._anexo_service = anexo_service
        self._resumo_service = resumo_service
        self._relatorio_repo = relatorio_repo
        self._storage = storage
        self._empresa_service = empresa_service
        self._tipo_lancamento_service = tipo_lancamento_service

    def _obter_responsavel(self) -> str:
        """Obtém o nome do responsável da empresa."""
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
        """Obtém o CNPJ da empresa."""
        if self._empresa_service is None:
            return ""
        try:
            empresa = self._empresa_service.obter()
            if empresa and empresa.cnpj:
                return empresa.cnpj
            return ""
        except Exception:
            return ""

    def _obter_tipos_lancamento(self) -> list:
        """Obtém todos os tipos de lançamento."""
        if self._tipo_lancamento_service is None:
            return []
        try:
            return self._tipo_lancamento_service.listar()
        except Exception:
            return []

    def gerar_relatorio_obra_reportlab(self, obra_id: int) -> Path:
        """Gera relatório PDF usando ReportLab Platypus.
        
        Args:
            obra_id: ID da obra para gerar o relatório.
            
        Returns:
            Path do arquivo PDF gerado.
            
        Raises:
            ValueError: Se a obra não for encontrada ou erro na geração.
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
        tipos = self._obter_tipos_lancamento()

        # Configurar arquivo
        filename = f"relatorio_obra_{obra.codigo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_reportlab.pdf"
        filepath = self._storage.relatorio_path(filename)
        
        print(f"[PDF] Arquivo: {filepath}")

        # Registrar fontes
        fonte_normal, fonte_bold = _registrar_fontes()
        estilos = _criar_estilos(fonte_normal, fonte_bold)
        
        # Criar documento
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.8 * cm,
        )
        
        elementos = []
        largura_util = A4[0] - 1.5 * cm - 1.5 * cm

        # === CABEÇALHO ===
        elementos.append(Paragraph("RELATÓRIO DA OBRA", estilos["Titulo"]))
        elementos.append(Paragraph(_texto(obra.nome, "Obra sem nome"), estilos["Subtitulo"]))
        elementos.append(Spacer(1, 8))
        
        # Tabela de informações
        info_data = [
            [f"Código: {_texto(obra.codigo)}", f"Cliente: {_texto(obra.cliente_contratante, 'Não informado')}"],
            [f"Local: {_texto(obra.local_obra, 'Não informado')}", f"Engenheiro: {_texto(obra.engenheiro_responsavel, 'Não informado')}"],
        ]
        info_table = Table(info_data, colWidths=[largura_util / 2, largura_util / 2])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), fonte_normal),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elementos.append(info_table)
        
        # Emissão
        elementos.append(Paragraph(
            f"Emissão: {datetime.now().strftime('%d/%m/%Y')}",
            ParagraphStyle(
                name="Emissao",
                parent=estilos["Texto"],
                alignment=TA_RIGHT,
            )
        ))
        elementos.append(Spacer(1, 10))

        # === RESUMO FINANCEIRO ===
        elementos.append(Paragraph("RESUMO FINANCEIRO", estilos["Secao"]))
        
        resumo_data = [
            ["Valor Contratado", "Total Aditivos", "Total Gasto", "Valor Líquido"],
            [
                _formatar_moeda(resumo.valor_contratado),
                _formatar_moeda(resumo.total_aditivos),
                _formatar_moeda(resumo.total_gasto),
                _formatar_moeda(resumo.valor_liquido),
            ],
        ]
        resumo_table = Table(resumo_data, colWidths=[largura_util / 4] * 4)
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#6B7280")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), fonte_bold),
            ('FONTNAME', (0, 1), (-1, 1), fonte_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#F9FAFB")),
        ]))
        elementos.append(resumo_table)
        elementos.append(Spacer(1, 8))

        # === ADITIVOS ===
        if aditivos:
            elementos.append(Paragraph("ADITIVOS", estilos["Secao"]))
            
            aditivos_data = [["Data", "Descrição", "Valor"]]
            for a in aditivos:
                aditivos_data.append([
                    _formatar_data(a.data_aditivo),
                    _texto(a.descricao, "Sem descrição"),
                    _formatar_moeda(a.valor),
                ])
            
            aditivos_table = Table(
                aditivos_data,
                colWidths=[largura_util * 0.20, largura_util * 0.55, largura_util * 0.25],
                repeatRows=1,
            )
            aditivos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#6B7280")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), fonte_bold),
                ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elementos.append(KeepTogether(aditivos_table))
            elementos.append(Spacer(1, 8))

        # === LANÇAMENTOS ===
        if lancamentos:
            elementos.append(Paragraph("LANÇAMENTOS", estilos["Secao"]))
            
            lancamentos_data = [["Data", "Descrição", "Tipo", "Valor"]]
            for l in lancamentos:
                lancamentos_data.append([
                    _formatar_data(l.data_lancamento),
                    _texto(l.descricao, "Sem descrição"),
                    _obter_nome_tipo(l.tipo_lancamento_id, tipos),
                    _formatar_moeda(l.valor_total),
                ])
            
            lancamentos_table = Table(
                lancamentos_data,
                colWidths=[
                    largura_util * 0.15,
                    largura_util * 0.40,
                    largura_util * 0.20,
                    largura_util * 0.25,
                ],
                repeatRows=1,
            )
            lancamentos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#6B7280")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), fonte_bold),
                ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elementos.append(lancamentos_table)
            elementos.append(Spacer(1, 8))

        # === ANEXOS ===
        if anexos:
            elementos.append(Paragraph("ANEXOS", estilos["Secao"]))
            
            for i, a in enumerate(anexos):
                nome = _texto(a.nome_original, "Sem nome")
                tipo = _texto(a.tipo_anexo, "Não informado")
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
                
                if i < len(anexos) - 1:
                    elementos.append(HRFlowable(
                        width=largura_util,
                        thickness=0.5,
                        color=colors.HexColor("#E5E7EB"),
                        spaceAfter=4,
                    ))
            
            elementos.append(Spacer(1, 8))

        # === ASSINATURA ===
        responsavel = self._obter_responsavel()
        cnpj = self._obter_cnpj()
        
        if responsavel:
            assinatura_data = [[Paragraph(responsavel, estilos["AssinaturaNome"])]]
            assinatura_table = Table(assinatura_data, colWidths=[largura_util])
            assinatura_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elementos.append(Spacer(1, 15))
            elementos.append(HRFlowable(
                width=largura_util * 0.5,
                thickness=1,
                color=colors.HexColor("#000000"),
                spaceAfter=4,
            ))
            elementos.append(assinatura_table)
            
            if cnpj:
                elementos.append(Paragraph(f"CNPJ: {cnpj}", estilos["AnexoMeta"]))
            else:
                elementos.append(Paragraph("Responsável Legal", estilos["AnexoMeta"]))

        # Gerar PDF
        def on_page(canvas, doc):
            """Callback para desenhar rodapé em cada página."""
            canvas.saveState()
            canvas.setFont(fonte_normal, 8)
            canvas.setFillColor(colors.HexColor("#6B7280"))
            canvas.drawCentredString(
                A4[0] / 2,
                0.8 * cm,
                f"Página {doc.page}"
            )
            canvas.restoreState()
        
        doc.build(elementos, onFirstPage=on_page, onLaterPages=on_page)
        
        # Registrar no repositório
        from controle_obras.domain.models import RelatorioGerado
        
        self._relatorio_repo.save(
            RelatorioGerado(
                obra_id=obra_id,
                tipo_relatorio="obra",
                arquivo_gerado=str(filepath),
            )
        )
        
        try:
            num_paginas = len(doc.pageStates) if hasattr(doc, 'pageStates') else 1
            print(f"[PDF] Páginas: {num_paginas}")
        except Exception:
            pass
        
        print(f"[PDF] Status: sucesso")
        
        return filepath
