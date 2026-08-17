"""Tela de anexos da obra."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFileDialog,
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

from controle_obras.ui.styles import (
    BACKGROUND,
    BORDER,
    DANGER,
    DANGER_HOVER,
    DANGER_LIGHT,
    INFO,
    INFO_HOVER,
    PRIMARY,
    PRIMARY_HOVER,
    SUCCESS,
    SUCCESS_HOVER,
    SURFACE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    get_action_button_style,
    get_screen_title_style,
    get_success_button_style,
)


# Estilo customizado para a tabela de anexos com seleção clara
ESTILO_TABELA_ANEXOS = """
    QTableWidget {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        gridline-color: #F1F5F9;
        font-size: 13px;
        selection-background-color: #DCEBFA;
        selection-color: #163A5F;
        alternate-background-color: #F8FAFC;
    }
    QTableWidget::item {
        padding: 8px 12px;
        border-bottom: 1px solid #F1F5F9;
    }
    QTableWidget::item:selected {
        background-color: #DCEBFA;
        color: #163A5F;
    }
    QTableWidget::item:selected:active {
        background-color: #C7DDF4;
        color: #163A5F;
    }
    QTableWidget::item:selected:!active {
        background-color: #E5EEF8;
        color: #334E68;
    }
    QTableWidget::item:hover {
        background-color: #F1F5F9;
        color: #1F2937;
    }
    QHeaderView::section {
        background-color: #1B2A4A;
        color: #FFFFFF;
        font-weight: 600;
        font-size: 12px;
        padding: 10px 12px;
        border: none;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom: 2px solid rgba(255, 255, 255, 0.15);
    }
    QHeaderView::section:last {
        border-right: none;
    }
"""


class AnexosScreen(QWidget):
    """Tela para gerenciamento de anexos da obra."""

    def __init__(self, parent: AppContainer) -> None:
        super().__init__()
        self._parent = parent
        self._obra_id: int | None = None
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 12, 16, 16)

        # Cabeçalho: título + botão na mesma linha
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title = QLabel("Anexos da Obra")
        title.setStyleSheet(get_screen_title_style())
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title, 1)

        btn_adicionar = QPushButton("Adicionar Anexo")
        btn_adicionar.setStyleSheet(get_success_button_style())
        btn_adicionar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_adicionar.clicked.connect(self._adicionar_anexo)
        btn_adicionar.setFixedHeight(36)
        header_layout.addWidget(btn_adicionar)

        layout.addLayout(header_layout)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Nome Original", "Tipo", "Data", "Tamanho", "", ""])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.horizontalHeader().setStretchLastSection(False)

        # Colunas: Nome Original cresce, demais ajustam ao conteúdo
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().resizeSection(4, 70)
        self.table.horizontalHeader().resizeSection(5, 75)

        self.table.setStyleSheet(ESTILO_TABELA_ANEXOS)
        self.table.viewport().installEventFilter(self)
        layout.addWidget(self.table)

    def carregar(self, obra_id: int) -> None:
        self._obra_id = obra_id
        anexos = self._parent.anexo_service.listar_por_obra(obra_id)
        self.table.setRowCount(len(anexos))
        for row, anexo in enumerate(anexos):
            item_nome = QTableWidgetItem(anexo.nome_original)
            item_nome.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 0, item_nome)

            item_tipo = QTableWidgetItem(anexo.tipo_anexo)
            item_tipo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, item_tipo)

            data_anexo = anexo.data_documento or anexo.created_at.date()
            data_str = data_anexo.strftime("%d/%m/%Y") if data_anexo else ""
            item_data = QTableWidgetItem(data_str)
            item_data.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, item_data)

            tamanho = f"{anexo.tamanho_bytes / 1024:.1f} KB" if anexo.tamanho_bytes else ""
            item_tamanho = QTableWidgetItem(tamanho)
            item_tamanho.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, item_tamanho)

            # Botão Abrir
            btn_abrir = QPushButton("Abrir")
            btn_abrir.setToolTip("Abrir anexo")
            btn_abrir.setStyleSheet(f"""
                QPushButton {{
                    padding: 3px 8px;
                    background-color: {INFO};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {INFO_HOVER};
                }}
            """)
            btn_abrir.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_abrir.clicked.connect(lambda checked, aid=anexo.id: self._abrir_anexo(aid))
            self.table.setCellWidget(row, 4, btn_abrir)

            # Botão Excluir
            btn_excluir = QPushButton("Excluir")
            btn_excluir.setToolTip("Excluir anexo")
            btn_excluir.setStyleSheet(f"""
                QPushButton {{
                    padding: 3px 8px;
                    background-color: {DANGER};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {DANGER_HOVER};
                }}
            """)
            btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_excluir.clicked.connect(lambda checked, aid=anexo.id: self._excluir_anexo(aid))
            self.table.setCellWidget(row, 5, btn_excluir)

    def _abrir_anexo(self, anexo_id: int) -> None:
        if self._obra_id is None:
            return
        anexo = self._parent.anexo_service.obter(anexo_id)
        if not anexo:
            QMessageBox.warning(self, "Erro", "Anexo não encontrado.")
            return

        obra = self._parent.obra_service.obter(self._obra_id)
        if not obra:
            return

        caminho = self._parent.storage.anexo_path(obra.codigo, anexo.caminho_relativo)
        if caminho.exists():
            QDesktopServices.openUrl(caminho.as_uri())
        else:
            QMessageBox.warning(self, "Erro", "Arquivo não encontrado no storage.")

    def _excluir_anexo(self, anexo_id: int) -> None:
        resposta = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Deseja realmente excluir este anexo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self._parent.anexo_service.excluir(anexo_id)
                QMessageBox.information(self, "Sucesso", "Anexo excluído.")
                self.carregar(self._obra_id)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao excluir anexo:\n{str(e)}")

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

    def eventFilter(self, obj, event):
        if obj == self.table.viewport() and event.type() == event.Type.MouseButtonPress:
            index = self.table.indexAt(event.pos())
            if not index.isValid():
                self.table.clearSelection()
                self.table.clearFocus()
                self.table.setCurrentItem(None)
        return super().eventFilter(obj, event)
