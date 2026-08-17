"""Tela de listagem e seleção de obras."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QHBoxLayout,
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


class ObrasListScreen(QWidget):
    """Tela para listar, selecionar e gerenciar obras."""

    def __init__(self, parent: AppContainer) -> None:
        super().__init__()
        self._parent = parent
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        title = QLabel("Obras Cadastradas")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Código", "Nome", "Cliente", "Local", "Valor Contratado", "Ações"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_nova = QPushButton("Nova Obra")
        btn_nova.setStyleSheet("padding: 10px 24px; background-color: #2980b9; color: white;")
        btn_nova.clicked.connect(lambda: self._parent.show_obra_form())
        btn_layout.addWidget(btn_nova)

        layout.addLayout(btn_layout)

    def carregar(self) -> None:
        obras = self._parent.obra_service.listar()
        self.table.setRowCount(len(obras))

        for row, obra in enumerate(obras):
            self.table.setItem(row, 0, QTableWidgetItem(obra.codigo))
            self.table.setItem(row, 1, QTableWidgetItem(obra.nome))
            self.table.setItem(row, 2, QTableWidgetItem(obra.cliente_contratante))
            self.table.setItem(row, 3, QTableWidgetItem(obra.local_obra))
            valor = f"R$ {obra.valor_contratado_inicial:,.2f}"
            self.table.setItem(row, 4, QTableWidgetItem(valor))

            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(4, 4, 4, 4)

            btn_abrir = QPushButton("Abrir")
            btn_abrir.clicked.connect(lambda checked, oid=obra.id: self._abrir_obra(oid))
            acoes_layout.addWidget(btn_abrir)

            btn_editar = QPushButton("Editar")
            btn_editar.clicked.connect(lambda checked, oid=obra.id: self._parent.show_obra_form(oid))
            acoes_layout.addWidget(btn_editar)

            btn_excluir = QPushButton("Excluir")
            btn_excluir.clicked.connect(lambda checked, oid=obra.id: self._excluir_obra(oid))
            acoes_layout.addWidget(btn_excluir)

            acoes_layout.addStretch()
            self.table.setCellWidget(row, 5, acoes_widget)

        self.table.resizeColumnsToContents()

    def _abrir_obra(self, obra_id: int | None) -> None:
        if obra_id is None:
            return
        self._parent.set_obra_ativa(obra_id)
        self._parent.show_dashboard()

    def _excluir_obra(self, obra_id: int | None) -> None:
        if obra_id is None:
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Deseja realmente excluir esta obra? Todos os dados vinculados serão removidos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self._parent.obra_service.excluir(obra_id)
            if self._parent.config_service.obter_obra_ativa() == obra_id:
                self._parent.set_obra_ativa(None)
            self.carregar()
