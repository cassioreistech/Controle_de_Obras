"""Tela de anexos da obra."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QFileDialog,
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


class AnexosScreen(QWidget):
    """Tela para gerenciamento de anexos da obra."""

    def __init__(self, parent: AppContainer) -> None:
        super().__init__()
        self._parent = parent
        self._obra_id: int | None = None
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        title = QLabel("Anexos da Obra")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_adicionar = QPushButton("Adicionar Anexo")
        btn_adicionar.setStyleSheet("padding: 10px 24px; background-color: #2980b9; color: white;")
        btn_adicionar.clicked.connect(self._adicionar_anexo)
        btn_layout.addWidget(btn_adicionar)

        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nome Original", "Tipo", "Data", "Tamanho"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def carregar(self, obra_id: int) -> None:
        self._obra_id = obra_id
        anexos = self._parent.anexo_service.listar_por_obra(obra_id)
        self.table.setRowCount(len(anexos))
        for row, anexo in enumerate(anexos):
            self.table.setItem(row, 0, QTableWidgetItem(anexo.nome_original))
            self.table.setItem(row, 1, QTableWidgetItem(anexo.tipo_anexo))
            self.table.setItem(row, 2, QTableWidgetItem(str(anexo.data_documento or anexo.created_at.date())))
            tamanho = f"{anexo.tamanho_bytes / 1024:.1f} KB" if anexo.tamanho_bytes else ""
            self.table.setItem(row, 3, QTableWidgetItem(tamanho))
        self.table.resizeColumnsToContents()

    def _adicionar_anexo(self) -> None:
        if self._obra_id is None:
            return

        arquivo, _ = QFileDialog.getOpenFileName(
            self, "Selecionar anexo", "", "Todos os arquivos (*.*)"
        )
        if not arquivo:
            return

        obra = self._parent.obra_service.obter(self._obra_id)
        if not obra:
            return

        try:
            self._parent.anexo_service.anexar_arquivo(
                obra_codigo=obra.codigo,
                arquivo_origem=Path(arquivo),
                tipo_anexo="Documento",
                obra_id=self._obra_id,
            )
            QMessageBox.information(self, "Sucesso", "Anexo adicionado.")
            self.carregar(self._obra_id)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao anexar arquivo:\n{str(e)}")
