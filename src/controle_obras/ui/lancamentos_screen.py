"""Tela de lançamentos de custos da obra."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
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

from controle_obras.domain.models import Lancamento

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
    get_screen_title_style,
    get_success_button_style,
    get_table_style,
)


ORIGENS_COM_ANEXO_OBRIGATORIO = {
    "Planilha de diretoria",
    "Planilha de engenharia",
}


class LancamentosScreen(QWidget):
    """Tela para cadastro e listagem de lançamentos."""

    def __init__(self, parent: AppContainer) -> None:
        super().__init__()
        self._parent = parent
        self._obra_id: int | None = None
        self._arquivo_anexo: Path | None = None
        self._editando_id: int | None = None
        self._init_ui()

    def _init_ui(self) -> None:
        # Layout principal centralizado
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(24, 16, 24, 16)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Painel centralizado com largura máxima
        panel = QWidget()
        panel.setMaximumWidth(1200)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setSpacing(10)
        panel_layout.setContentsMargins(0, 0, 0, 0)

        # Container centralizado
        center_container = QHBoxLayout()
        center_container.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        center_container.addWidget(panel)
        main_layout.addLayout(center_container)

        # Título
        title = QLabel("Lançamentos da Obra")
        title.setStyleSheet(get_screen_title_style())
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(title)

        # Grid do formulário
        form_layout = QGridLayout()
        form_layout.setContentsMargins(16, 12, 16, 12)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(8)

        # Estilo dos inputs
        input_style = get_input_style()

        # Criar campos
        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        self.input_data.setDate(date.today())
        self.input_data.setStyleSheet(input_style)
        self.input_data.setMinimumHeight(32)

        self.input_tipo = QComboBox()
        self.input_tipo.setStyleSheet(input_style)
        self.input_tipo.setMinimumHeight(32)

        self.input_descricao = QLineEdit()
        self.input_descricao.setStyleSheet(input_style)
        self.input_descricao.setMinimumHeight(32)

        self.input_quantidade = QLineEdit()
        self.input_quantidade.setPlaceholderText("0")
        self.input_quantidade.textChanged.connect(self._auto_calcular_total)
        self.input_quantidade.setStyleSheet(input_style)
        self.input_quantidade.setMinimumHeight(32)

        self.input_unidade = QLineEdit()
        self.input_unidade.setStyleSheet(input_style)
        self.input_unidade.setMinimumHeight(32)

        self.input_valor_unitario = QLineEdit()
        self.input_valor_unitario.setPlaceholderText("0,00")
        self.input_valor_unitario.textChanged.connect(self._auto_calcular_total)
        self.input_valor_unitario.setStyleSheet(input_style)
        self.input_valor_unitario.setMinimumHeight(32)

        self.input_valor_total = QLineEdit()
        self.input_valor_total.setPlaceholderText("0,00")
        self.input_valor_total.setReadOnly(True)
        self.input_valor_total.setStyleSheet(input_style)
        self.input_valor_total.setMinimumHeight(32)

        self.input_origem = QComboBox()
        self.input_origem.addItems(
            ["Manual", "Planilha de diretoria", "Planilha de engenharia", "Nota geral", "Cupom"]
        )
        self.input_origem.currentTextChanged.connect(self._origem_alterada)
        self.input_origem.setStyleSheet(input_style)
        self.input_origem.setMinimumHeight(32)

        self.input_observacoes = QLineEdit()
        self.input_observacoes.setPlaceholderText("Observações opcionais")
        self.input_observacoes.setStyleSheet(input_style)
        self.input_observacoes.setMinimumHeight(32)

        # Componentes do anexo
        self.lbl_anexo = QLabel("Nenhum arquivo selecionado")
        self.lbl_anexo.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        self.lbl_anexo.setVisible(False)

        self.btn_ver_anexo = QPushButton("👁 Ver")
        self.btn_ver_anexo.setStyleSheet(f"""
            QPushButton {{
                padding: 2px 6px;
                background-color: {INFO};
                color: white;
                border-radius: 3px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {INFO_LIGHT};
            }}
        """)
        self.btn_ver_anexo.setVisible(False)
        self.btn_ver_anexo.clicked.connect(self._ver_anexo_atual)

        self.btn_excluir_anexo = QPushButton("🗑")
        self.btn_excluir_anexo.setStyleSheet(f"""
            QPushButton {{
                padding: 2px 6px;
                background-color: {DANGER};
                color: white;
                border-radius: 3px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {DANGER_LIGHT};
            }}
        """)
        self.btn_excluir_anexo.setVisible(False)
        self.btn_excluir_anexo.clicked.connect(self._excluir_anexo_atual)

        anexo_layout = QHBoxLayout()
        anexo_layout.setContentsMargins(0, 0, 0, 0)
        anexo_layout.setSpacing(4)
        anexo_layout.addWidget(self.lbl_anexo)
        anexo_layout.addWidget(self.btn_ver_anexo)
        anexo_layout.addWidget(self.btn_excluir_anexo)

        # Helper para labels
        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY}; font-weight: 500;")
            l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            return l

        # Linha 1: Data + Tipo
        form_layout.addWidget(lbl("Data:"), 0, 0)
        form_layout.addWidget(self.input_data, 0, 1)
        form_layout.addWidget(lbl("Tipo:"), 0, 2)
        form_layout.addWidget(self.input_tipo, 0, 3, 1, 3)

        # Linha 2: Descrição + Origem + Anexo (mesma linha)
        form_layout.addWidget(lbl("Descrição *:"), 1, 0)
        form_layout.addWidget(self.input_descricao, 1, 1, 1, 3)
        form_layout.addWidget(lbl("Origem:"), 1, 4)
        form_layout.addWidget(self.input_origem, 1, 5)
        form_layout.addWidget(lbl("Anexo:"), 1, 6)
        form_layout.addLayout(anexo_layout, 1, 7)

        # Linha 3: Qtd + Unidade + Valor Unitário + Valor Total
        form_layout.addWidget(lbl("Qtd:"), 2, 0)
        form_layout.addWidget(self.input_quantidade, 2, 1)
        form_layout.addWidget(lbl("Unidade:"), 2, 2)
        form_layout.addWidget(self.input_unidade, 2, 3)
        form_layout.addWidget(lbl("Valor Unit.:"), 2, 4)
        form_layout.addWidget(self.input_valor_unitario, 2, 5)
        form_layout.addWidget(lbl("Valor Total *:"), 2, 6)
        form_layout.addWidget(self.input_valor_total, 2, 7)

        # Linha 4: Observações + Salvar
        form_layout.addWidget(lbl("Observações:"), 3, 0)
        form_layout.addWidget(self.input_observacoes, 3, 1, 1, 5)

        btn_salvar = QPushButton("Salvar Lançamento")
        btn_salvar.setToolTip("Salvar o lançamento e anexar arquivo se houver")
        btn_salvar.setStyleSheet(get_success_button_style())
        btn_salvar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_salvar.clicked.connect(self._salvar)
        btn_salvar.setMinimumHeight(32)

        btn_limpar = QPushButton("Limpar")
        btn_limpar.setToolTip("Limpar formulário")
        btn_limpar.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 16px;
                background-color: {TEXT_SECONDARY};
                color: {SURFACE};
                border: 1px solid rgba(0, 0, 0, 35%);
                border-top-color: rgba(255, 255, 255, 45%);
                border-bottom-color: rgba(0, 0, 0, 45%);
                border-radius: 7px;
                font-size: 13px;
                font-weight: 600;
                min-width: 90px;
            }}
            QPushButton:hover {{
                background-color: {TEXT_MUTED};
                border-top-color: rgba(255, 255, 255, 75%);
            }}
            QPushButton:pressed {{
                padding-top: 10px;
                padding-bottom: 6px;
                border-top-color: rgba(0, 0, 0, 45%);
                border-bottom-color: rgba(255, 255, 255, 35%);
            }}
        """)
        btn_limpar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_limpar.clicked.connect(self._limpar_formulario)
        btn_limpar.setMinimumHeight(32)

        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(8)
        botoes_layout.addWidget(btn_salvar)
        botoes_layout.addWidget(btn_limpar)
        form_layout.addLayout(botoes_layout, 3, 6, 1, 2)

        # Proporções das colunas - equilibradas
        form_layout.setColumnStretch(0, 1)  # labels
        form_layout.setColumnStretch(1, 3)  # Data/Descrição
        form_layout.setColumnStretch(2, 1)  # labels
        form_layout.setColumnStretch(3, 3)  # Tipo/Unidade
        form_layout.setColumnStretch(4, 1)  # labels
        form_layout.setColumnStretch(5, 2)  # Origem/Valor Unit.
        form_layout.setColumnStretch(6, 1)  # labels
        form_layout.setColumnStretch(7, 2)  # Anexo/Valor Total

        panel_layout.addLayout(form_layout)

        # Tabela
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Data", "Descrição", "Tipo", "Origem", "Valor", "", ""])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Configurar colunas da tabela
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Data
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Descrição
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Tipo
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Origem
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Valor
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().resizeSection(5, 70)
        self.table.horizontalHeader().resizeSection(6, 75)
        
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.setStyleSheet(get_table_style(PRIMARY))
        self.table.viewport().installEventFilter(self)

        table_layout.addWidget(self.table)
        panel_layout.addWidget(table_container, 1)

    def carregar(self, obra_id: int) -> None:
        self._obra_id = obra_id
        self._carregar_tipos()
        self._carregar_lancamentos()
        self._arquivo_anexo = None
        self._atualizar_label_anexo()

    def _carregar_tipos(self) -> None:
        self.input_tipo.clear()
        tipos = self._parent.tipo_lancamento_service.listar_ativos()
        for tipo in tipos:
            self.input_tipo.addItem(tipo.nome, tipo.id)

    def _carregar_lancamentos(self) -> None:
        if self._obra_id is None:
            return
        lancamentos = self._parent.lancamento_service.listar_por_obra(self._obra_id)
        self.table.setRowCount(len(lancamentos))
        for row, lanc in enumerate(lancamentos):
            data_str = lanc.data_lancamento.strftime("%d/%m/%Y") if lanc.data_lancamento else ""
            item_data = QTableWidgetItem(data_str)
            item_data.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_data)

            item_desc = QTableWidgetItem(lanc.descricao.upper())
            item_desc.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font_desc = item_desc.font()
            font_desc.setBold(True)
            item_desc.setFont(font_desc)
            self.table.setItem(row, 1, item_desc)

            tipo_nome = self.input_tipo.itemText(
                self.input_tipo.findData(lanc.tipo_lancamento_id)
            ) if lanc.tipo_lancamento_id else ""
            item_tipo = QTableWidgetItem(tipo_nome)
            item_tipo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, item_tipo)

            item_origem = QTableWidgetItem(lanc.origem_informacao)
            item_origem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, item_origem)

            valor_item = QTableWidgetItem(f"R$ {lanc.valor_total:,.2f}")
            valor_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font = valor_item.font()
            font.setBold(True)
            font.setPointSize(10)
            valor_item.setFont(font)
            valor_item.setForeground(Qt.GlobalColor.darkGreen)
            self.table.setItem(row, 4, valor_item)

            # Botão Editar
            btn_editar = QPushButton("✏")
            btn_editar.setToolTip("Editar lançamento")
            btn_editar.setStyleSheet(f"""
                QPushButton {{
                    padding: 2px 6px;
                    background-color: {INFO};
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-size: 12px;
                    min-width: 28px;
                    min-height: 28px;
                    max-height: 30px;
                }}
                QPushButton:hover {{
                    background-color: {INFO_HOVER};
                }}
            """)
            btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_editar.clicked.connect(lambda checked, lid=lanc.id: self._editar_lancamento(lid))
            self.table.setCellWidget(row, 5, btn_editar)

            # Botão Excluir
            btn_excluir = QPushButton("🗑")
            btn_excluir.setToolTip("Excluir lançamento")
            btn_excluir.setStyleSheet(f"""
                QPushButton {{
                    padding: 2px 6px;
                    background-color: {DANGER};
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-size: 12px;
                    min-width: 28px;
                    min-height: 28px;
                    max-height: 30px;
                }}
                QPushButton:hover {{
                    background-color: {DANGER_HOVER};
                }}
            """)
            btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_excluir.clicked.connect(lambda checked, lid=lanc.id: self._excluir_lancamento(lid))
            self.table.setCellWidget(row, 6, btn_excluir)

    def _origem_alterada(self, origem: str) -> None:
        if origem in ORIGENS_COM_ANEXO_OBRIGATORIO:
            self._selecionar_arquivo_anexo(origem)
        else:
            self._arquivo_anexo = None
            self._atualizar_label_anexo()

    def _selecionar_arquivo_anexo(self, origem: str) -> None:
        tipo_arquivo = "Planilhas (*.xlsx *.xls *.csv *.pdf);;Todos os arquivos (*.*)"
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            f"Selecionar {origem}",
            "",
            tipo_arquivo,
        )
        if arquivo:
            self._arquivo_anexo = Path(arquivo)
        else:
            self._arquivo_anexo = None
            if self.input_origem.currentText() in ORIGENS_COM_ANEXO_OBRIGATORIO:
                self.input_origem.setCurrentText("Manual")
        self._atualizar_label_anexo()

    def _atualizar_label_anexo(self) -> None:
        if self._arquivo_anexo:
            self.lbl_anexo.setText(f"✓ {self._arquivo_anexo.name}")
            self.lbl_anexo.setStyleSheet("color: #27ae60; font-size: 12px;")
            self.lbl_anexo.setVisible(True)
            self.btn_excluir_anexo.setVisible(True)
        else:
            origem = self.input_origem.currentText()
            if origem in ORIGENS_COM_ANEXO_OBRIGATORIO:
                self.lbl_anexo.setText("Nenhum arquivo selecionado (obrigatório)")
                self.lbl_anexo.setStyleSheet("color: #e74c3c; font-size: 12px;")
                self.lbl_anexo.setVisible(True)
            else:
                self.lbl_anexo.setText("Nenhum arquivo selecionado")
                self.lbl_anexo.setStyleSheet("color: #7f8c8d; font-size: 12px;")
                self.lbl_anexo.setVisible(False)
            self.btn_excluir_anexo.setVisible(False)

    def _auto_calcular_total(self) -> None:
        try:
            qtd_text = self.input_quantidade.text().strip().replace(".", "").replace(",", ".")
            unit_text = self.input_valor_unitario.text().strip().replace("R$", "").replace(".", "").replace(",", ".").strip()
            qtd = float(qtd_text) if qtd_text else 0.0
            unit = float(unit_text) if unit_text else 0.0
            total = qtd * unit
            if total > 0:
                self.input_valor_total.setText(f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            else:
                self.input_valor_total.setText("")
        except ValueError:
            pass

    def _salvar(self) -> None:
        if self._obra_id is None:
            return

        descricao = self.input_descricao.text().strip()
        if not descricao:
            QMessageBox.warning(self, "Validação", "Descrição é obrigatória.")
            return

        origem = self.input_origem.currentText()
        if origem in ORIGENS_COM_ANEXO_OBRIGATORIO and not self._arquivo_anexo:
            QMessageBox.warning(
                self,
                "Validação",
                f"Para origem '{origem}', é necessário anexar o arquivo correspondente.",
            )
            return

        valor_text = self.input_valor_total.text().strip().replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            valor_total = float(valor_text) if valor_text else 0.0
        except ValueError:
            QMessageBox.warning(self, "Validação", "Valor total inválido.")
            return

        qtd_text = self.input_quantidade.text().strip().replace(".", "").replace(",", ".")
        unit_text = self.input_valor_unitario.text().strip().replace("R$", "").replace(".", "").replace(",", ".").strip()

        lancamento = Lancamento(
            id=self._editando_id,
            obra_id=self._obra_id,
            tipo_lancamento_id=self.input_tipo.currentData(),
            data_lancamento=self.input_data.date().toPython(),
            descricao=descricao,
            complemento="",
            quantidade=float(qtd_text) if qtd_text else None,
            unidade=self.input_unidade.text().strip(),
            valor_unitario=float(unit_text) if unit_text else None,
            valor_total=valor_total,
            origem_informacao=origem,
            observacoes=self.input_observacoes.text().strip(),
        )

        try:
            lancamento_salvo = self._parent.lancamento_service.salvar(lancamento)

            if self._arquivo_anexo and lancamento_salvo.id:
                obra = self._parent.obra_service.obter(self._obra_id)
                if obra:
                    self._parent.anexo_service.anexar_arquivo(
                        obra_codigo=obra.codigo,
                        arquivo_origem=self._arquivo_anexo,
                        tipo_anexo=origem,
                        obra_id=self._obra_id,
                        lancamento_id=lancamento_salvo.id,
                    )

            msg = "Lançamento atualizado." if self._editando_id else "Lançamento salvo."
            QMessageBox.information(self, "Sucesso", msg)
            self._editando_id = None
            self._limpar_formulario()
            self._carregar_lancamentos()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar lançamento:\n{str(e)}")

    def _limpar_formulario(self) -> None:
        self._editando_id = None
        self.input_data.setDate(date.today())
        self.input_tipo.setCurrentIndex(0)
        self.input_descricao.clear()
        self.input_quantidade.clear()
        self.input_unidade.clear()
        self.input_valor_unitario.clear()
        self.input_valor_total.clear()
        self.input_origem.setCurrentIndex(0)
        self.input_observacoes.clear()
        self._arquivo_anexo = None
        self._atualizar_label_anexo()
        self.btn_ver_anexo.setVisible(False)
        self.btn_excluir_anexo.setVisible(False)

    def eventFilter(self, obj, event):
        if obj == self.table.viewport() and event.type() == event.Type.MouseButtonPress:
            index = self.table.indexAt(event.pos())
            if not index.isValid():
                self.table.clearSelection()
                self.table.clearFocus()
                self.table.setCurrentItem(None)
        return super().eventFilter(obj, event)

    def _editar_lancamento(self, lancamento_id: int) -> None:
        """Carrega o lançamento no formulário para edição."""
        if self._obra_id is None:
            return
        lancamento = self._parent.lancamento_service.obter(lancamento_id)
        if not lancamento:
            return

        self._editando_id = lancamento_id

        # Preencher formulário com dados do lançamento
        self.input_data.setDate(lancamento.data_lancamento)
        if lancamento.tipo_lancamento_id:
            idx = self.input_tipo.findData(lancamento.tipo_lancamento_id)
            if idx >= 0:
                self.input_tipo.setCurrentIndex(idx)
        self.input_descricao.setText(lancamento.descricao)
        self.input_quantidade.setText(str(lancamento.quantidade) if lancamento.quantidade else "")
        self.input_unidade.setText(lancamento.unidade)
        self.input_valor_unitario.setText(f"R$ {lancamento.valor_unitario:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if lancamento.valor_unitario else "")
        self.input_valor_total.setText(f"R$ {lancamento.valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # Bloquear sinais do combo origem para não abrir dialog de anexo
        self.input_origem.blockSignals(True)
        self.input_origem.setCurrentText(lancamento.origem_informacao)
        self.input_origem.blockSignals(False)

        self.input_observacoes.setText(lancamento.observacoes)

        # Verificar se existe anexo vinculado
        anexos = self._parent.anexo_service.listar_por_lancamento(lancamento_id)
        if anexos:
            anexo = anexos[0]
            self.lbl_anexo.setText(f"✓ {anexo.nome_original}")
            self.lbl_anexo.setStyleSheet("color: #27ae60; font-size: 12px;")
            self.lbl_anexo.setVisible(True)
            self.btn_ver_anexo.setVisible(True)
            self.btn_excluir_anexo.setVisible(True)
        else:
            self.lbl_anexo.setText("Nenhum arquivo selecionado")
            self.lbl_anexo.setStyleSheet("color: #7f8c8d; font-size: 12px;")
            self.lbl_anexo.setVisible(False)
            self.btn_ver_anexo.setVisible(False)
            self.btn_excluir_anexo.setVisible(False)

        # Scroll para o formulário
        self.input_descricao.setFocus()

    def _excluir_lancamento(self, lancamento_id: int) -> None:
        if self._obra_id is None:
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Deseja realmente excluir este lançamento?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self._parent.lancamento_service.excluir(lancamento_id)
            self._carregar_lancamentos()

    def _ver_anexo_atual(self) -> None:
        if self._editando_id is None:
            return
        anexos = self._parent.anexo_service.listar_por_lancamento(self._editando_id)
        if not anexos:
            QMessageBox.information(self, "Anexo", "Este lançamento não possui anexo.")
            return
        anexo = anexos[0]
        caminho = self._parent.storage.anexo_path(
            self._parent.obra_service.obter(self._obra_id).codigo,
            anexo.caminho_relativo,
        )
        if caminho.exists():
            QDesktopServices.openUrl(caminho.as_uri())
        else:
            QMessageBox.warning(self, "Anexo", "Arquivo não encontrado.")

    def _excluir_anexo_atual(self) -> None:
        self._arquivo_anexo = None
        self._atualizar_label_anexo()
        self.btn_ver_anexo.setVisible(False)
