"""Tela de dashboard da obra ativa."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from controle_obras.ui.app_container import AppContainer


class DashboardScreen(QWidget):
    """Dashboard executivo da obra selecionada."""

    def __init__(self, parent: AppContainer) -> None:
        super().__init__()
        self._parent = parent
        self._obra_id: int | None = None
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.header = QLabel("")
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.header)

        cards_layout = QGridLayout()

        self.card_contratado = self._create_card("Valor Contratado", "R$ 0,00")
        self.card_aditivos = self._create_card("Total de Aditivos", "R$ 0,00")
        self.card_gasto = self._create_card("Total Gasto", "R$ 0,00")
        self.card_liquido = self._create_card("Valor Líquido", "R$ 0,00")

        cards_layout.addWidget(self.card_contratado, 0, 0)
        cards_layout.addWidget(self.card_aditivos, 0, 1)
        cards_layout.addWidget(self.card_gasto, 0, 2)
        cards_layout.addWidget(self.card_liquido, 0, 3)

        layout.addLayout(cards_layout)

        acoes_layout = QHBoxLayout()
        btn_aditivo = QPushButton("+ Aditivo")
        btn_aditivo.clicked.connect(self._novo_aditivo)
        acoes_layout.addWidget(btn_aditivo)

        btn_lancamento = QPushButton("+ Lançamento")
        btn_lancamento.clicked.connect(self._novo_lancamento)
        acoes_layout.addWidget(btn_lancamento)

        btn_anexo = QPushButton("+ Anexo")
        btn_anexo.clicked.connect(self._novo_anexo)
        acoes_layout.addWidget(btn_anexo)

        btn_relatorio = QPushButton("Gerar PDF")
        btn_relatorio.clicked.connect(self._gerar_pdf)
        acoes_layout.addWidget(btn_relatorio)

        acoes_layout.addStretch()
        layout.addLayout(acoes_layout)

        ultimos_label = QLabel("Últimos Lançamentos")
        ultimos_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 16px;")
        layout.addWidget(ultimos_label)

        self.table_lancamentos = QTableWidget()
        self.table_lancamentos.setColumnCount(4)
        self.table_lancamentos.setHorizontalHeaderLabels(
            ["Data", "Descrição", "Tipo", "Valor"]
        )
        self.table_lancamentos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_lancamentos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_lancamentos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_lancamentos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_lancamentos.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table_lancamentos)

    def _create_card(self, title: str, value: str) -> QWidget:
        card = QWidget()
        card.setStyleSheet(
            "background-color: #ecf0f1; border-radius: 8px; padding: 16px;"
        )
        layout = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        value_label.setProperty("value_label", True)
        layout.addWidget(value_label)

        return card

    def carregar(self, obra_id: int) -> None:
        self._obra_id = obra_id
        obra = self._parent.obra_service.obter(obra_id)
        if not obra:
            return

        self.header.setText(f"{obra.codigo} - {obra.nome}")
        resumo = self._parent.resumo_service.calcular_resumo(obra_id)

        self._update_card(self.card_contratado, f"R$ {resumo.valor_contratado:,.2f}")
        self._update_card(self.card_aditivos, f"R$ {resumo.total_aditivos:,.2f}")
        self._update_card(self.card_gasto, f"R$ {resumo.total_gasto:,.2f}")
        self._update_card(self.card_liquido, f"R$ {resumo.valor_liquido:,.2f}")

        lancamentos = self._parent.lancamento_service.listar_por_obra(obra_id)[:10]
        self.table_lancamentos.setRowCount(len(lancamentos))
        for row, lanc in enumerate(lancamentos):
            self.table_lancamentos.setItem(row, 0, QTableWidgetItem(str(lanc.data_lancamento)))
            self.table_lancamentos.setItem(row, 1, QTableWidgetItem(lanc.descricao))
            self.table_lancamentos.setItem(row, 2, QTableWidgetItem(lanc.origem_informacao))
            self.table_lancamentos.setItem(row, 3, QTableWidgetItem(f"R$ {lanc.valor_total:,.2f}"))

    def _update_card(self, card: QWidget, value: str) -> None:
        for child in card.findChildren(QLabel):
            if child.property("value_label"):
                child.setText(value)
                return

    def _novo_aditivo(self) -> None:
        if self._obra_id is None:
            return
        valor, ok = self._input_valor("Novo Aditivo", "Valor do aditivo:")
        if ok and valor > 0:
            from controle_obras.domain.models import Aditivo

            aditivo = Aditivo(
                obra_id=self._obra_id,
                descricao="Aditivo",
                valor=valor,
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
