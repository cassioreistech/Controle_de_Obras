"""Tela de dashboard da obra ativa."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
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

from controle_obras.ui.styles import (
    BACKGROUND,
    BORDER,
    BROWN,
    BROWN_HOVER,
    DANGER,
    DANGER_HOVER,
    DANGER_LIGHT,
    DARK_GREEN,
    DARK_GREEN_HOVER,
    INFO,
    INFO_HOVER,
    INFO_LIGHT,
    PRIMARY,
    PRIMARY_HOVER,
    PRIMARY_PRESSED,
    SUCCESS,
    SUCCESS_HOVER,
    SUCCESS_LIGHT,
    SURFACE,
    SURFACE_ALT,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    WARNING,
    WARNING_HOVER,
    get_action_button_style,
    get_card_style,
    get_input_style,
    get_screen_title_style,
    get_table_style,
)


class DashboardScreen(QWidget):
    """Dashboard executivo da obra selecionada."""

    def __init__(self, parent: AppContainer) -> None:
        super().__init__()
        self._parent = parent
        self._obra_id: int | None = None
        self.setStyleSheet(f"background-color: {BACKGROUND};")
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Cards de resumo
        layout.addWidget(self._build_cards())

        # Ações rápidas
        layout.addWidget(self._build_acoes())

        # Tabela últimos movimentos
        layout.addWidget(self._build_tabela(), 1)

    def _build_cards(self) -> QWidget:
        cards_widget = QWidget()
        cards_layout = QGridLayout(cards_widget)
        cards_layout.setSpacing(12)

        self.card_contratado = self._create_card(
            "Valor Contratado", "R$ 0,00", SUCCESS, SUCCESS_LIGHT
        )
        self.card_aditivos = self._create_card(
            "Total de Aditivos", "R$ 0,00", INFO, INFO_LIGHT
        )
        self.card_gasto = self._create_card(
            "Total Gasto", "R$ 0,00", DANGER, DANGER_LIGHT
        )
        self.card_liquido = self._create_card(
            "Valor Líquido", "R$ 0,00", PRIMARY, SURFACE_ALT
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
                background-color: {SURFACE};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)
        layout = QHBoxLayout(acoes)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 12, 16, 12)

        layout.addStretch()

        botoes = [
            ("+ Aditivo", INFO, INFO_HOVER, self._novo_aditivo),
            ("+ Lançamento", SUCCESS, SUCCESS_HOVER, self._novo_lancamento),
            ("+ Anexo", WARNING, WARNING_HOVER, self._novo_anexo),
            ("Gerar PDF", BROWN, BROWN_HOVER, self._gerar_pdf),
            ("Atualizar", DARK_GREEN, DARK_GREEN_HOVER, lambda: self.carregar(self._obra_id) if self._obra_id else None),
        ]

        for texto, cor, hover, callback in botoes:
            btn = QPushButton(texto)
            btn.setStyleSheet(get_action_button_style(cor, hover))
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
            font-size: 15px;
            font-weight: 600;
            color: {TEXT_PRIMARY};
        """)
        header_layout.addWidget(titulo)
        header_layout.addStretch()

        self.lbl_total = QLabel("")
        self.lbl_total.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
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
        self.table_lancamentos.setStyleSheet(get_table_style(PRIMARY))
        self.table_lancamentos.viewport().installEventFilter(self)

        layout.addWidget(self.table_lancamentos)

        return container

    def _create_card(
        self, title: str, value: str, color: str, bg_color: str
    ) -> QWidget:
        # Container externo para sombra
        shadow_container = QWidget()
        shadow_container.setMinimumHeight(100)

        # Card principal
        card = QFrame(shadow_container)
        card.setObjectName("card")
        card.setStyleSheet(f"""
            QFrame#card {{
                background-color: {bg_color};
                border: 1px solid {BORDER};
                border-radius: 12px;
                border-left: 4px solid {color};
            }}
            QFrame#card:hover {{
                border-left-width: 5px;
            }}
        """)

        # Sombra sutil
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setXOffset(2)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)

        # Layout interno
        card.setGeometry(0, 0, 200, 100)

        layout = QVBoxLayout(shadow_container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(6)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {TEXT_SECONDARY};
            letter-spacing: 0.5px;
            text-transform: uppercase;
            background: transparent;
            padding: 0;
            margin: 0;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title_label)

        # Valor principal
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {color};
            background: transparent;
            padding: 0;
            margin: 0;
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setProperty("value_label", True)
        card_layout.addWidget(value_label)

        return shadow_container

    def carregar(self, obra_id: int) -> None:
        self._obra_id = obra_id

        obra = self._parent.obra_service.obter(obra_id)
        if not obra:
            return

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
            font_data = item_data.font()
            font_data.setBold(True)
            item_data.setFont(font_data)
            self.table_lancamentos.setItem(row, 0, item_data)

            item_desc = QTableWidgetItem(mov["descricao"].upper())
            item_desc.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font_desc = item_desc.font()
            font_desc.setBold(True)
            item_desc.setFont(font_desc)
            self.table_lancamentos.setItem(row, 1, item_desc)

            item_tipo = QTableWidgetItem(mov["tipo"])
            item_tipo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if mov["tipo"] == "Aditivo":
                item_tipo.setForeground(QColor(INFO))
                font = item_tipo.font()
                font.setBold(True)
                item_tipo.setFont(font)
            self.table_lancamentos.setItem(row, 2, item_tipo)

            valor_item = QTableWidgetItem(f"R$ {mov['valor']:,.2f}")
            valor_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font = valor_item.font()
            font.setBold(True)
            font.setPointSize(font.pointSize() + 3)
            valor_item.setFont(font)
            if mov["tipo"] == "Aditivo":
                valor_item.setForeground(QColor(INFO))
            else:
                valor_item.setForeground(QColor(SUCCESS))
            self.table_lancamentos.setItem(row, 3, valor_item)

    def eventFilter(self, obj, event):
        if obj == self.table_lancamentos.viewport() and event.type() == event.Type.MouseButtonPress:
            idx = self.table_lancamentos.indexAt(event.pos())
            if not idx.isValid():
                self.table_lancamentos.clearSelection()
                self.table_lancamentos.clearFocus()
                self.table_lancamentos.setCurrentItem(None)
        return super().eventFilter(obj, event)

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
                background-color: {BACKGROUND};
            }}
            QLabel {{
                font-size: 13px;
                color: {TEXT_PRIMARY};
            }}
            QLineEdit, QDateEdit {{
                {get_input_style()}
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
        btn_ok.setStyleSheet(get_action_button_style(SUCCESS, SUCCESS_HOVER))
        btn_cancel = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        btn_cancel.setStyleSheet(get_action_button_style(TEXT_SECONDARY, TEXT_MUTED))

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
                background-color: {BACKGROUND};
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
        table.setStyleSheet(get_table_style(INFO))

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
            valor_item.setForeground(QColor(INFO))
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
                    color: {DANGER};
                    border: none;
                    border-radius: 3px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {DANGER_LIGHT};
                }}
            """)
            btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_excluir.clicked.connect(lambda checked, aid=adit.id: self._excluir_aditivo_dialog(aid, dialog))
            table.setCellWidget(row, 4, btn_excluir)

        layout.addWidget(table)

        btn_fechar = QPushButton("Fechar")
        btn_fechar.setStyleSheet(get_action_button_style(TEXT_SECONDARY, TEXT_MUTED))
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
