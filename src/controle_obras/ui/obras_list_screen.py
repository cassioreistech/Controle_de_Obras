"""Tela de listagem e seleção de obras com melhorias de usabilidade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from controle_obras.domain.models import Obra

if TYPE_CHECKING:
    from controle_obras.ui.app_container import AppContainer


class ObrasListScreen(QWidget):
    """Tela para listar, selecionar e gerenciar obras."""

    def __init__(self, parent: AppContainer) -> None:
        super().__init__()
        self._parent = parent
        self._obras: list[Obra] = []
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        title_layout = QHBoxLayout()
        title = QLabel("Obras Cadastradas")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title_layout.addWidget(title)

        self.lbl_contagem = QLabel("0 obras")
        self.lbl_contagem.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        title_layout.addWidget(self.lbl_contagem)
        title_layout.addStretch()

        btn_nova = QPushButton("Nova Obra")
        btn_nova.setToolTip("Cadastrar uma nova obra")
        btn_nova.setStyleSheet(
            "padding: 10px 24px; background-color: #2980b9; color: white;"
        )
        btn_nova.clicked.connect(lambda: self._parent.show_obra_form())
        title_layout.addWidget(btn_nova)

        layout.addLayout(title_layout)

        busca_layout = QHBoxLayout()
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Buscar por código, nome, cliente ou local...")
        self.input_busca.textChanged.connect(self._aplicar_filtro)
        self.input_busca.setToolTip("Digite para filtrar a lista de obras")
        busca_layout.addWidget(self.input_busca)
        layout.addLayout(busca_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Código", "Nome", "Cliente", "Local", "Valor Contratado"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._menu_contexto)
        self.table.doubleClicked.connect(self._duplo_clique)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.lbl_vazio = QLabel("Nenhuma obra cadastrada. Clique em 'Nova Obra' para começar.")
        self.lbl_vazio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_vazio.setStyleSheet("color: #7f8c8d; font-size: 14px; padding: 32px;")
        self.lbl_vazio.setVisible(False)
        layout.addWidget(self.lbl_vazio)

    def carregar(self) -> None:
        self._obras = self._parent.obra_service.listar()
        self._aplicar_filtro()

    def _aplicar_filtro(self) -> None:
        termo = self.input_busca.text().strip().lower()
        obras_filtradas = [
            obra
            for obra in self._obras
            if not termo
            or termo in obra.codigo.lower()
            or termo in obra.nome.lower()
            or termo in obra.cliente_contratante.lower()
            or termo in obra.local_obra.lower()
        ]

        obra_ativa_id = self._parent.config_service.obter_obra_ativa()

        self.table.setRowCount(len(obras_filtradas))
        self.lbl_contagem.setText(
            f"{len(obras_filtradas)} obra{'s' if len(obras_filtradas) != 1 else ''}"
        )
        self.lbl_vazio.setVisible(len(obras_filtradas) == 0)
        self.table.setVisible(len(obras_filtradas) > 0)

        for row, obra in enumerate(obras_filtradas):
            self.table.setItem(row, 0, QTableWidgetItem(obra.codigo))
            self.table.setItem(row, 1, QTableWidgetItem(obra.nome))
            self.table.setItem(row, 2, QTableWidgetItem(obra.cliente_contratante))
            self.table.setItem(row, 3, QTableWidgetItem(obra.local_obra))
            valor_item = QTableWidgetItem(f"R$ {obra.valor_contratado_inicial:,.2f}")
            valor_item.setData(Qt.ItemDataRole.UserRole, float(obra.valor_contratado_inicial))
            self.table.setItem(row, 4, valor_item)

            if obra.id == obra_ativa_id:
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(Qt.GlobalColor.yellow)
                        item.setToolTip("Obra ativa selecionada")

            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, obra.id)

        self.table.resizeColumnsToContents()

    def _duplo_clique(self) -> None:
        obra_id = self._obra_id_selecionada()
        if obra_id:
            self._abrir_obra(obra_id)

    def _menu_contexto(self, position) -> None:
        item = self.table.itemAt(position)
        if not item:
            return

        obra_id = item.data(Qt.ItemDataRole.UserRole)
        if not obra_id:
            return

        menu = QMenu(self)
        acao_abrir = QAction("Abrir", self)
        acao_abrir.triggered.connect(lambda: self._abrir_obra(obra_id))
        acao_editar = QAction("Editar", self)
        acao_editar.triggered.connect(lambda: self._parent.show_obra_form(obra_id))
        acao_excluir = QAction("Excluir", self)
        acao_excluir.triggered.connect(lambda: self._excluir_obra(obra_id))

        menu.addAction(acao_abrir)
        menu.addAction(acao_editar)
        menu.addSeparator()
        menu.addAction(acao_excluir)
        menu.exec(self.table.viewport().mapToGlobal(position))

    def _obra_id_selecionada(self) -> int | None:
        selected = self.table.selectedItems()
        if not selected:
            return None
        obra_id = selected[0].data(Qt.ItemDataRole.UserRole)
        return obra_id if obra_id else None

    def _abrir_obra(self, obra_id: int | None) -> None:
        if obra_id is None:
            return
        self._parent.set_obra_ativa(obra_id)
        self._parent.show_dashboard()

    def _excluir_obra(self, obra_id: int | None) -> None:
        if obra_id is None:
            return
        obra = self._parent.obra_service.obter(obra_id)
        nome = obra.nome if obra else "esta obra"
        resposta = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Deseja realmente excluir '{nome}'?\n\n"
            "Todos os dados vinculados (aditivos, lançamentos e anexos) serão removidos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self._parent.obra_service.excluir(obra_id)
            if self._parent.config_service.obter_obra_ativa() == obra_id:
                self._parent.set_obra_ativa(None)
            self.carregar()
