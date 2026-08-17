"""Tela de lançamentos de custos da obra."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from controle_obras.domain.models import Lancamento

if TYPE_CHECKING:
    from controle_obras.ui.app_container import AppContainer


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
        layout = QVBoxLayout(self)

        title = QLabel("Lançamentos da Obra")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form_layout = QFormLayout()

        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        self.input_data.setDate(date.today())
        self.input_tipo = QComboBox()
        self.input_descricao = QLineEdit()
        self.input_complemento = QLineEdit()
        self.input_quantidade = QLineEdit()
        self.input_quantidade.setPlaceholderText("0")
        self.input_quantidade.textChanged.connect(self._auto_calcular_total)
        self.input_unidade = QLineEdit()
        self.input_valor_unitario = QLineEdit()
        self.input_valor_unitario.setPlaceholderText("0,00")
        self.input_valor_unitario.textChanged.connect(self._auto_calcular_total)
        self.input_valor_total = QLineEdit()
        self.input_valor_total.setPlaceholderText("0,00")
        self.input_valor_total.setReadOnly(True)
        self.input_origem = QComboBox()
        self.input_origem.addItems(
            ["Manual", "Planilha de diretoria", "Planilha de engenharia", "Nota geral", "Cupom"]
        )
        self.input_origem.currentTextChanged.connect(self._origem_alterada)
        self.input_observacoes = QTextEdit()
        self.input_observacoes.setMaximumHeight(80)

        self.lbl_anexo = QLabel("Nenhum arquivo selecionado")
        self.lbl_anexo.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        self.lbl_anexo.setVisible(False)

        self.btn_ver_anexo = QPushButton("👁 Ver Anexo")
        self.btn_ver_anexo.setStyleSheet("padding: 2px 8px; background-color: #3498db; color: white; border-radius: 3px; font-size: 11px;")
        self.btn_ver_anexo.setVisible(False)
        self.btn_ver_anexo.clicked.connect(self._ver_anexo_atual)

        self.btn_excluir_anexo = QPushButton("🗑 Excluir Anexo")
        self.btn_excluir_anexo.setStyleSheet("padding: 2px 8px; background-color: #e74c3c; color: white; border-radius: 3px; font-size: 11px;")
        self.btn_excluir_anexo.setVisible(False)
        self.btn_excluir_anexo.clicked.connect(self._excluir_anexo_atual)

        anexo_layout = QHBoxLayout()
        anexo_layout.addWidget(self.lbl_anexo)
        anexo_layout.addWidget(self.btn_ver_anexo)
        anexo_layout.addWidget(self.btn_excluir_anexo)
        anexo_layout.addStretch()

        form_layout.addRow("Data", self.input_data)
        form_layout.addRow("Tipo", self.input_tipo)
        form_layout.addRow("Descrição *", self.input_descricao)
        form_layout.addRow("Complemento", self.input_complemento)
        form_layout.addRow("Quantidade", self.input_quantidade)
        form_layout.addRow("Unidade", self.input_unidade)
        form_layout.addRow("Valor Unitário", self.input_valor_unitario)
        form_layout.addRow("Valor Total *", self.input_valor_total)
        form_layout.addRow("Origem", self.input_origem)
        form_layout.addRow("Anexo vinculado", anexo_layout)
        form_layout.addRow("Observações", self.input_observacoes)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_salvar = QPushButton("Salvar Lançamento")
        btn_salvar.setToolTip("Salvar o lançamento e anexar arquivo se houver")
        btn_salvar.setStyleSheet("padding: 10px 24px; background-color: #27ae60; color: white;")
        btn_salvar.clicked.connect(self._salvar)
        btn_layout.addWidget(btn_salvar)

        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Data", "Descrição", "Tipo", "Origem", "Valor", "", ""])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTableWidget::item:selected:!active {
                background-color: #3498db;
                color: white;
            }
        """)
        self.table.viewport().installEventFilter(self)
        layout.addWidget(self.table)

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

            item_desc = QTableWidgetItem(lanc.descricao)
            item_desc.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
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
            font.setPointSize(font.pointSize() + 1)
            valor_item.setFont(font)
            valor_item.setForeground(Qt.GlobalColor.darkGreen)
            self.table.setItem(row, 4, valor_item)

            # Botão Editar
            btn_editar = QPushButton("✏️")
            btn_editar.setToolTip("Editar lançamento")
            btn_editar.setStyleSheet("padding: 4px 8px; background-color: transparent; color: #2980b9; border: none; border-radius: 3px; font-size: 14px;")
            btn_editar.clicked.connect(lambda checked, lid=lanc.id: self._editar_lancamento(lid))
            self.table.setCellWidget(row, 5, btn_editar)

            # Botão Excluir
            btn_excluir = QPushButton("🗑️")
            btn_excluir.setToolTip("Excluir lançamento")
            btn_excluir.setStyleSheet("padding: 4px 8px; background-color: transparent; color: #c0392b; border: none; border-radius: 3px; font-size: 14px;")
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
            complemento=self.input_complemento.text().strip(),
            quantidade=float(qtd_text) if qtd_text else None,
            unidade=self.input_unidade.text().strip(),
            valor_unitario=float(unit_text) if unit_text else None,
            valor_total=valor_total,
            origem_informacao=origem,
            observacoes=self.input_observacoes.toPlainText().strip(),
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
        self.input_complemento.clear()
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
        self.input_complemento.setText(lancamento.complemento)
        self.input_quantidade.setText(str(lancamento.quantidade) if lancamento.quantidade else "")
        self.input_unidade.setText(lancamento.unidade)
        self.input_valor_unitario.setText(f"R$ {lancamento.valor_unitario:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if lancamento.valor_unitario else "")
        self.input_valor_total.setText(f"R$ {lancamento.valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # Bloquear sinais do combo origem para não abrir dialog de anexo
        self.input_origem.blockSignals(True)
        self.input_origem.setCurrentText(lancamento.origem_informacao)
        self.input_origem.blockSignals(False)

        self.input_observacoes.setPlainText(lancamento.observacoes)

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
