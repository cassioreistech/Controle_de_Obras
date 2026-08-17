"""Tela de dashboard da obra ativa."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from controle_obras.ui.app_container import AppContainer


# Paleta de cores consistente
CORES = {
    "primaria": "#2c3e50",
    "secundaria": "#34495e",
    "sucesso": "#27ae60",
    "info": "#2980b9",
    "alerta": "#f39c12",
    "perigo": "#e74c3c",
    "fundo": "#f8f9fa",
    "fundo_card": "#ffffff",
    "borda": "#dee2e6",
    "texto": "#2c3e50",
    "texto_secundario": "#6c757d",
    "aditivo": "#8e44ad",
}

ESTILO_BOTAO = """
    QPushButton {{
        padding: 6px 12px;
        background-color: {cor};
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        font-size: 11px;
    }}
    QPushButton:hover {{
        background-color: {cor_hover};
    }}
    QPushButton:pressed {{
        background-color: {cor_pressed};
    }}
"""

ESTILO_TABELA = """
    QTableWidget {{
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        gridline-color: #e9ecef;
        font-size: 13px;
        selection-background-color: transparent;
    }}
    QTableWidget::item {{
        padding: 8px 12px;
        border-bottom: 1px solid #e9ecef;
    }}
    QTableWidget::item:selected {{
        background-color: #e3f2fd;
        color: #1565c0;
    }}
    QTableWidget::item:hover {{
        background-color: #f5f5f5;
    }}
    QHeaderView::section {{
        background-color: {cor_header};
        color: white;
        font-weight: bold;
        font-size: 12px;
        padding: 10px 12px;
        border: none;
        border-right: 1px solid rgba(255,255,255,0.1);
        border-bottom: 2px solid rgba(255,255,255,0.2);
    }}
    QHeaderView::section:last {{
        border-right: none;
    }}
"""


class DashboardScreen(QWidget):
    """Dashboard executivo da obra selecionada."""

    def __init__(self, parent: AppContainer) -> None:
        super().__init__()
        self._parent = parent
        self._obra_id: int | None = None
        self.setStyleSheet(f"background-color: {CORES['fundo']};")
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # Header
        layout.addWidget(self._build_header())

        # Cards de resumo
        layout.addWidget(self._build_cards())

        # Ações rápidas
        layout.addWidget(self._build_acoes())

        # Tabela últimos movimentos
        layout.addWidget(self._build_tabela(), 1)

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setFixedHeight(52)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {CORES['primaria']};
                border-radius: 4px;
                padding: 0px;
            }}
            QLabel {{
                color: white;
                padding: 0px;
            }}
            QComboBox {{
                min-height: 28px;
                max-height: 30px;
                padding: 2px 8px;
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 3px;
                background-color: rgba(255,255,255,0.1);
                color: white;
                font-size: 12px;
                min-width: 220px;
            }}
            QComboBox:hover {{
                border-color: rgba(255,255,255,0.5);
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 6px;
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                color: {CORES['texto']};
                selection-background-color: {CORES['info']};
            }}
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        self.header = QLabel("")
        self.header.setStyleSheet("font-size: 13px; font-weight: bold; padding: 0;")
        layout.addWidget(self.header)

        layout.addStretch()

        lbl_obra = QLabel("Obra ativa:")
        lbl_obra.setStyleSheet("font-size: 11px; padding: 0;")
        layout.addWidget(lbl_obra)

        self.combo_obras = QComboBox()
        self.combo_obras.setToolTip("Selecionar obra ativa")
        self.combo_obras.currentIndexChanged.connect(self._obra_selecionada)
        layout.addWidget(self.combo_obras)

        btn_trocar = QPushButton("Trocar Obra")
        btn_trocar.setStyleSheet(ESTILO_BOTAO.format(
            cor="rgba(255,255,255,0.15)",
            cor_hover="rgba(255,255,255,0.25)",
            cor_pressed="rgba(255,255,255,0.1)"
        ))
        btn_trocar.clicked.connect(lambda: self._parent.show_obras_list())
        layout.addWidget(btn_trocar)

        return header

    def _build_cards(self) -> QWidget:
        cards_widget = QWidget()
        cards_layout = QGridLayout(cards_widget)
        cards_layout.setSpacing(12)

        self.card_contratado = self._create_card(
            "Valor Contratado", "R$ 0,00", CORES["sucesso"], "#e8f5e9"
        )
        self.card_aditivos = self._create_card(
            "Total de Aditivos", "R$ 0,00", CORES["info"], "#e3f2fd", show_button=True
        )
        self.card_gasto = self._create_card(
            "Total Gasto", "R$ 0,00", CORES["perigo"], "#ffebee"
        )
        self.card_liquido = self._create_card(
            "Valor Líquido", "R$ 0,00", CORES["primaria"], "#e8eaf6"
        )

        cards_layout.addWidget(self.card_contratado, 0, 0)
        cards_layout.addWidget(self.card_aditivos, 0, 1)
        cards_layout.addWidget(self.card_gasto, 0, 2)
        cards_layout.addWidget(self.card_liquido, 0, 3)

        return cards_widget

    def _build_acoes(self) -> QWidget:
        acoes = QFrame()
        acoes.setStyleSheet(f"""
            QFrame {{
                background-color: {CORES['fundo_card']};
                border: 1px solid {CORES['borda']};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        layout = QHBoxLayout(acoes)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 8, 12, 8)

        botoes = [
            ("+ Aditivo", CORES["info"], "#2471a3", "#1a5276", self._novo_aditivo),
            ("+ Lançamento", CORES["sucesso"], "#229954", "#1e8449", self._novo_lancamento),
            ("+ Anexo", CORES["aditivo"], "#7d3c98", "#6c3483", self._novo_anexo),
            ("Gerar PDF", CORES["primaria"], "#1a252f", "#151d26", self._gerar_pdf),
            ("Atualizar", "#17a2b8", "#138496", "#117a8b", lambda: self.carregar(self._obra_id) if self._obra_id else None),
            ("Limpar", CORES["texto_secundario"], "#5a6268", "#4e555b", self._limpar_selecao),
        ]

        for texto, cor, hover, pressed, callback in botoes:
            btn = QPushButton(texto)
            btn.setStyleSheet(ESTILO_BOTAO.format(cor=cor, cor_hover=hover, cor_pressed=pressed))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(callback)
            layout.addWidget(btn)

        layout.addStretch()

        return acoes

    def _build_tabela(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        header_layout = QHBoxLayout()
        titulo = QLabel("Últimos Movimentos")
        titulo.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {CORES['texto']};
        """)
        header_layout.addWidget(titulo)
        header_layout.addStretch()

        self.lbl_total = QLabel("")
        self.lbl_total.setStyleSheet(f"color: {CORES['texto_secundario']}; font-size: 12px;")
        header_layout.addWidget(self.lbl_total)

        layout.addLayout(header_layout)

        self.table_lancamentos = QTableWidget()
        self.table_lancamentos.setColumnCount(4)
        self.table_lancamentos.setHorizontalHeaderLabels(
            ["Data", "Descrição", "Tipo", "Valor"]
        )
        self.table_lancamentos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_lancamentos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_lancamentos.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table_lancamentos.verticalHeader().setVisible(False)
        self.table_lancamentos.verticalHeader().setDefaultSectionSize(40)
        self.table_lancamentos.horizontalHeader().setStretchLastSection(True)
        self.table_lancamentos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_lancamentos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_lancamentos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_lancamentos.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_lancamentos.setStyleSheet(ESTILO_TABELA.format(cor_header=CORES["primaria"]))
        self.table_lancamentos.viewport().installEventFilter(self)

        layout.addWidget(self.table_lancamentos)

        return container

    def _create_card(
        self, title: str, value: str, color: str, bg_color: str, show_button: bool = False
    ) -> QWidget:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 6px;
                border-left: 3px solid {color};
                padding: 10px 12px;
            }}
            QFrame:hover {{
                border-left-width: 5px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 10px; color: {CORES['texto_secundario']}; font-weight: 500;")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        value_label.setProperty("value_label", True)
        layout.addWidget(value_label)

        if show_button:
            btn_ver = QPushButton("Ver Aditivos")
            btn_ver.setStyleSheet(f"""
                QPushButton {{
                    padding: 6px 12px;
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                    margin-top: 8px;
                }}
                QPushButton:hover {{
                    background-color: {color}dd;
                }}
            """)
            btn_ver.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_ver.clicked.connect(self._ver_aditivos)
            layout.addWidget(btn_ver)

        return card

    def carregar(self, obra_id: int) -> None:
        self._obra_id = obra_id
        self._carregar_combo_obras(obra_id)

        obra = self._parent.obra_service.obter(obra_id)
        if not obra:
            return

        self.header.setText(f"{obra.codigo} — {obra.nome}")
        resumo = self._parent.resumo_service.calcular_resumo(obra_id)

        self._update_card(self.card_contratado, f"R$ {resumo.valor_contratado:,.2f}")
        self._update_card(self.card_aditivos, f"R$ {resumo.total_aditivos:,.2f}")
        self._update_card(self.card_gasto, f"R$ {resumo.total_gasto:,.2f}")
        self._update_card(self.card_liquido, f"R$ {resumo.valor_liquido:,.2f}")

        movimentos = []

        lancamentos = self._parent.lancamento_service.listar_por_obra(obra_id)
        for lanc in lancamentos:
            movimentos.append({
                "data": lanc.data_lancamento,
                "descricao": lanc.descricao,
                "tipo": lanc.origem_informacao or "Lançamento",
                "valor": lanc.valor_total,
            })

        aditivos = self._parent.aditivo_service.listar_por_obra(obra_id)
        for adit in aditivos:
            movimentos.append({
                "data": adit.data_aditivo,
                "descricao": adit.descricao or "Aditivo",
                "tipo": "Aditivo",
                "valor": adit.valor,
            })

        movimentos.sort(key=lambda m: m["data"] or date.min, reverse=True)
        movimentos = movimentos[:10]

        self.lbl_total.setText(f"{len(movimentos)} movimentos")
        self.table_lancamentos.setRowCount(len(movimentos))
        for row, mov in enumerate(movimentos):
            data_str = mov["data"].strftime("%d/%m/%Y") if mov["data"] else ""
            item_data = QTableWidgetItem(data_str)
            item_data.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_lancamentos.setItem(row, 0, item_data)

            item_desc = QTableWidgetItem(mov["descricao"])
            item_desc.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table_lancamentos.setItem(row, 1, item_desc)

            item_tipo = QTableWidgetItem(mov["tipo"])
            item_tipo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if mov["tipo"] == "Aditivo":
                item_tipo.setForeground(QColor(CORES["aditivo"]))
                font = item_tipo.font()
                font.setBold(True)
                item_tipo.setFont(font)
            self.table_lancamentos.setItem(row, 2, item_tipo)

            valor_item = QTableWidgetItem(f"R$ {mov['valor']:,.2f}")
            valor_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            font = valor_item.font()
            font.setBold(True)
            font.setPointSize(font.pointSize() + 1)
            valor_item.setFont(font)
            if mov["tipo"] == "Aditivo":
                valor_item.setForeground(QColor(CORES["aditivo"]))
            else:
                valor_item.setForeground(QColor(CORES["sucesso"]))
            self.table_lancamentos.setItem(row, 3, valor_item)

    def _carregar_combo_obras(self, obra_atual_id: int) -> None:
        self.combo_obras.blockSignals(True)
        self.combo_obras.clear()
        obras = self._parent.obra_service.listar()
        for obra in obras:
            self.combo_obras.addItem(f"{obra.codigo} - {obra.nome}", obra.id)
        index = self.combo_obras.findData(obra_atual_id)
        if index >= 0:
            self.combo_obras.setCurrentIndex(index)
        self.combo_obras.blockSignals(False)

    def _obra_selecionada(self, index: int) -> None:
        if index < 0:
            return
        obra_id = self.combo_obras.itemData(index)
        if obra_id and obra_id != self._obra_id:
            self._parent.set_obra_ativa(obra_id)
            self.carregar(obra_id)

    def eventFilter(self, obj, event):
        if obj == self.table_lancamentos.viewport() and event.type() == event.Type.MouseButtonPress:
            idx = self.table_lancamentos.indexAt(event.pos())
            if not idx.isValid():
                self.table_lancamentos.clearSelection()
                self.table_lancamentos.clearFocus()
                self.table_lancamentos.setCurrentItem(None)
        return super().eventFilter(obj, event)

    def _limpar_selecao(self) -> None:
        self.table_lancamentos.clearSelection()
        self.table_lancamentos.clearFocus()
        self.table_lancamentos.setCurrentItem(None)

    def _update_card(self, card: QWidget, value: str) -> None:
        for child in card.findChildren(QLabel):
            if child.property("value_label"):
                child.setText(value)
                return

    def _novo_aditivo(self) -> None:
        if self._obra_id is None:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Novo Aditivo")
        dialog.setMinimumWidth(450)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {CORES['fundo']};
            }}
            QLabel {{
                font-size: 13px;
                color: {CORES['texto']};
            }}
            QLineEdit, QDateEdit {{
                padding: 8px;
                border: 1px solid {CORES['borda']};
                border-radius: 4px;
                font-size: 13px;
            }}
            QLineEdit:focus, QDateEdit:focus {{
                border-color: {CORES['info']};
            }}
        """)

        form = QFormLayout(dialog)
        form.setSpacing(12)
        form.setContentsMargins(24, 24, 24, 24)

        input_data = QDateEdit()
        input_data.setCalendarPopup(True)
        input_data.setDate(date.today())
        form.addRow("Data:", input_data)

        input_desc = QLineEdit()
        input_desc.setPlaceholderText("Descrição do aditivo")
        form.addRow("Descrição:", input_desc)

        input_valor = QLineEdit()
        input_valor.setPlaceholderText("0,00")
        form.addRow("Valor (R$):", input_valor)

        input_obs = QLineEdit()
        input_obs.setPlaceholderText("Observações opcionais")
        form.addRow("Observações:", input_obs)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        btn_ok = buttons.button(QDialogButtonBox.StandardButton.Ok)
        btn_ok.setStyleSheet(ESTILO_BOTAO.format(
            cor=CORES["sucesso"], cor_hover="#229954", cor_pressed="#1e8449"
        ))
        btn_cancel = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        btn_cancel.setStyleSheet(ESTILO_BOTAO.format(
            cor=CORES["texto_secundario"], cor_hover="#5a6268", cor_pressed="#4e555b"
        ))

        form.addRow(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        descricao = input_desc.text().strip()
        if not descricao:
            QMessageBox.warning(self, "Validação", "Descrição é obrigatória.")
            return

        valor_text = input_valor.text().strip().replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            valor = float(valor_text) if valor_text else 0.0
        except ValueError:
            QMessageBox.warning(self, "Validação", "Valor inválido.")
            return

        if valor <= 0:
            QMessageBox.warning(self, "Validação", "Valor deve ser maior que zero.")
            return

        from controle_obras.domain.models import Aditivo

        aditivo = Aditivo(
            obra_id=self._obra_id,
            data_aditivo=input_data.date().toPython(),
            descricao=descricao,
            valor=Decimal(str(valor)),
            observacoes=input_obs.text().strip(),
        )
        self._parent.aditivo_service.salvar(aditivo)
        self.carregar(self._obra_id)

    def _novo_lancamento(self) -> None:
        self._parent.show_lancamentos()

    def _novo_anexo(self) -> None:
        self._parent.show_anexos()

    def _gerar_pdf(self) -> None:
        if self._obra_id is None:
            return
        try:
            caminho = self._parent.relatorio_service.gerar_relatorio_obra(self._obra_id)
            QMessageBox.information(self, "Relatório", f"PDF gerado:\n{caminho}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gerar PDF:\n{str(e)}")

    def _input_valor(self, title: str, label: str) -> tuple[float, bool]:
        from PySide6.QtWidgets import QInputDialog

        text, ok = QInputDialog.getText(self, title, label)
        if not ok:
            return 0.0, False
        try:
            return float(text.replace(".", "").replace(",", ".")), True
        except ValueError:
            QMessageBox.warning(self, "Validação", "Valor inválido.")
            return 0.0, False

    def _excluir_aditivo(self, aditivo_id: int) -> None:
        if self._obra_id is None:
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Deseja realmente excluir este aditivo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self._parent.aditivo_service.excluir(aditivo_id)
            self.carregar(self._obra_id)

    def _ver_aditivos(self) -> None:
        if self._obra_id is None:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Aditivos da Obra")
        dialog.setMinimumSize(650, 400)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {CORES['fundo']};
            }}
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Data", "Descrição", "Valor", "Observações", ""])
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(36)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        table.setStyleSheet(ESTILO_TABELA.format(cor_header=CORES["info"]))

        aditivos = self._parent.aditivo_service.listar_por_obra(self._obra_id)
        table.setRowCount(len(aditivos))
        for row, adit in enumerate(aditivos):
            data_str = adit.data_aditivo.strftime("%d/%m/%Y") if adit.data_aditivo else ""
            item_data = QTableWidgetItem(data_str)
            item_data.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 0, item_data)

            item_desc = QTableWidgetItem(adit.descricao or "Aditivo")
            item_desc.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row, 1, item_desc)

            valor_item = QTableWidgetItem(f"R$ {adit.valor:,.2f}")
            valor_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            font = valor_item.font()
            font.setBold(True)
            valor_item.setFont(font)
            valor_item.setForeground(QColor(CORES["aditivo"]))
            table.setItem(row, 2, valor_item)

            item_obs = QTableWidgetItem(adit.observacoes or "")
            item_obs.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row, 3, item_obs)

            btn_excluir = QPushButton("🗑️")
            btn_excluir.setToolTip("Excluir aditivo")
            btn_excluir.setStyleSheet(f"""
                QPushButton {{
                    padding: 4px 8px;
                    background-color: transparent;
                    color: {CORES['perigo']};
                    border: none;
                    border-radius: 3px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: #ffebee;
                }}
            """)
            btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_excluir.clicked.connect(lambda checked, aid=adit.id: self._excluir_aditivo_dialog(aid, dialog))
            table.setCellWidget(row, 4, btn_excluir)

        layout.addWidget(table)

        btn_fechar = QPushButton("Fechar")
        btn_fechar.setStyleSheet(ESTILO_BOTAO.format(
            cor=CORES["texto_secundario"], cor_hover="#5a6268", cor_pressed="#4e555b"
        ))
        btn_fechar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_fechar.clicked.connect(dialog.accept)
        layout.addWidget(btn_fechar)

        dialog.exec()

    def _excluir_aditivo_dialog(self, aditivo_id: int, dialog: QDialog) -> None:
        resposta = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Deseja realmente excluir este aditivo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self._parent.aditivo_service.excluir(aditivo_id)
            dialog.accept()
            self.carregar(self._obra_id)
