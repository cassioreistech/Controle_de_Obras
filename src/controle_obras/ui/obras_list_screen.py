"""Tela de listagem e seleção de obras com melhorias de usabilidade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
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

from controle_obras.ui.styles import (
    BACKGROUND,
    BORDER,
    DANGER,
    DANGER_HOVER,
    DANGER_LIGHT,
    INFO,
    INFO_HOVER,
    INFO_LIGHT,
    PRIMARY,
    SUCCESS,
    SUCCESS_HOVER,
    SURFACE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    get_action_button_style,
    get_input_style,
    get_primary_button_style,
    get_screen_title_style,
    get_success_button_style,
    get_table_style,
)


class ObrasListScreen(QWidget):
    """Tela para listar, selecionar e gerenciar obras."""

    def __init__(self, parent: AppContainer) -> None:
        super().__init__()
        self._parent = parent
        self._obras: list[Obra] = []
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title_layout = QHBoxLayout()
        title = QLabel("Obras Cadastradas")
        title.setStyleSheet(get_screen_title_style())
        title_layout.addWidget(title)

        self.lbl_contagem = QLabel("")
        self.lbl_contagem.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; margin-left: 8px;")
        title_layout.addWidget(self.lbl_contagem)
        title_layout.addStretch()

        btn_nova = QPushButton("Nova Obra")
        btn_nova.setToolTip("Cadastrar uma nova obra")
        btn_nova.setStyleSheet(get_success_button_style())
        btn_nova.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_nova.clicked.connect(lambda: self._parent.show_obra_form())
        title_layout.addWidget(btn_nova)

        layout.addLayout(title_layout)

        busca_layout = QHBoxLayout()
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Buscar por código, nome, cliente ou local...")
        self.input_busca.textChanged.connect(self._aplicar_filtro)
        self.input_busca.setToolTip("Digite para filtrar a lista de obras")
        self.input_busca.setStyleSheet(get_input_style())
        busca_layout.addWidget(self.input_busca)
        layout.addLayout(busca_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["Código", "Nome", "Cliente", "Local", "Valor Contratado", "Status", "", ""]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._menu_contexto)
        self.table.doubleClicked.connect(self._duplo_clique)
        self.table.viewport().installEventFilter(self)
        self.table.setStyleSheet(get_table_style(PRIMARY))
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().resizeSection(6, 70)
        self.table.horizontalHeader().resizeSection(7, 75)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(42)
        layout.addWidget(self.table)

        self.lbl_vazio = QLabel("Nenhuma obra cadastrada. Clique em 'Nova Obra' para começar.")
        self.lbl_vazio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_vazio.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 14px; padding: 32px;")
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
            item_codigo = QTableWidgetItem(obra.codigo)
            item_codigo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_codigo)

            item_nome = QTableWidgetItem(obra.nome.upper())
            item_nome.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font_nome = item_nome.font()
            font_nome.setBold(True)
            item_nome.setFont(font_nome)
            self.table.setItem(row, 1, item_nome)

            item_cliente = QTableWidgetItem(obra.cliente_contratante)
            item_cliente.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, item_cliente)

            item_local = QTableWidgetItem(obra.local_obra)
            item_local.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, item_local)

            valor_item = QTableWidgetItem(f"R$ {obra.valor_contratado_inicial:,.2f}")
            valor_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            valor_item.setData(Qt.ItemDataRole.UserRole, float(obra.valor_contratado_inicial))
            font = valor_item.font()
            font.setBold(True)
            font.setPointSize(font.pointSize() + 1)
            valor_item.setFont(font)
            valor_item.setForeground(QColor(SUCCESS))
            self.table.setItem(row, 4, valor_item)

            # Status
            status_item = QTableWidgetItem(obra.status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font_status = status_item.font()
            font_status.setBold(True)
            status_item.setFont(font_status)
            # Cor baseada no status
            if obra.status == "Concluída":
                status_item.setForeground(QColor(SUCCESS))
            elif obra.status == "Cancelada":
                status_item.setForeground(QColor(DANGER))
            elif obra.status == "Pausada":
                status_item.setForeground(QColor("#D97706"))
            else:
                status_item.setForeground(QColor(INFO))
            self.table.setItem(row, 5, status_item)

            if obra.id == obra_ativa_id:
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setToolTip("Obra ativa selecionada")

            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, obra.id)

            # Botão Editar (ícone SVG: edit-3)
            btn_editar = QPushButton()
            btn_editar.setToolTip("Editar obra")
            btn_editar.setAccessibleName("Editar obra")
            btn_editar.setFixedSize(30, 30)
            btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # SVG inline - ícone de editar mais moderno
            svg_editar = '''
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 20h9"/>
                    <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
                </svg>
            '''
            
            from PySide6.QtGui import QPixmap, QPainter, QIcon
            from PySide6.QtSvg import QSvgRenderer
            
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.GlobalColor.transparent)
            renderer = QSvgRenderer(svg_editar.encode())
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            btn_editar.setIcon(QIcon(pixmap))
            btn_editar.setIconSize(pixmap.rect().size())
            
            btn_editar.setStyleSheet(f"""
                QPushButton {{
                    background-color: {INFO};
                    border: none;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: {INFO_HOVER};
                }}
            """)
            btn_editar.clicked.connect(lambda checked, oid=obra.id: self._parent.show_obra_form(oid))
            self.table.setCellWidget(row, 6, btn_editar)

            # Botão Excluir (ícone SVG: trash-2)
            btn_excluir = QPushButton()
            btn_excluir.setToolTip("Excluir obra")
            btn_excluir.setAccessibleName("Excluir obra")
            btn_excluir.setFixedSize(30, 30)
            btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # SVG inline - ícone de lixeira mais moderno
            svg_excluir = '''
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    <line x1="10" y1="11" x2="10" y2="17"/>
                    <line x1="14" y1="11" x2="14" y2="17"/>
                </svg>
            '''
            
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.GlobalColor.transparent)
            renderer = QSvgRenderer(svg_excluir.encode())
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            btn_excluir.setIcon(QIcon(pixmap))
            btn_excluir.setIconSize(pixmap.rect().size())
            
            btn_excluir.setStyleSheet(f"""
                QPushButton {{
                    background-color: {DANGER};
                    border: none;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: {DANGER_HOVER};
                }}
            """)
            btn_excluir.clicked.connect(lambda checked, oid=obra.id: self._confirmar_exclusao(oid))
            self.table.setCellWidget(row, 7, btn_excluir)

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

    def eventFilter(self, obj, event):
        if obj == self.table.viewport() and event.type() == event.Type.MouseButtonPress:
            index = self.table.indexAt(event.pos())
            if not index.isValid():
                self.table.clearSelection()
                self.table.clearFocus()
                self.table.setCurrentItem(None)
        return super().eventFilter(obj, event)
