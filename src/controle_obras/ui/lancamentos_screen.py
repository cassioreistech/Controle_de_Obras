"""Tela de lançamentos de custos da obra."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

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
        self.input_unidade = QLineEdit()
        self.input_valor_unitario = QLineEdit()
        self.input_valor_total = QLineEdit()
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

        form_layout.addRow("Data", self.input_data)
        form_layout.addRow("Tipo", self.input_tipo)
        form_layout.addRow("Descrição *", self.input_descricao)
        form_layout.addRow("Complemento", self.input_complemento)
        form_layout.addRow("Quantidade", self.input_quantidade)
        form_layout.addRow("Unidade", self.input_unidade)
        form_layout.addRow("Valor Unitário", self.input_valor_unitario)
        form_layout.addRow("Valor Total *", self.input_valor_total)
        form_layout.addRow("Origem", self.input_origem)
        form_layout.addRow("Anexo vinculado", self.lbl_anexo)
        form_layout.addRow("Observações", self.input_observacoes)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_calcular = QPushButton("Calcular Total")
        btn_calcular.setToolTip("Calcular valor total a partir da quantidade e valor unitário")
        btn_calcular.clicked.connect(self._calcular_total)
        btn_layout.addWidget(btn_calcular)

        btn_salvar = QPushButton("Salvar Lançamento")
        btn_salvar.setToolTip("Salvar o lançamento e anexar arquivo se houver")
        btn_salvar.setStyleSheet("padding: 10px 24px; background-color: #27ae60; color: white;")
        btn_salvar.clicked.connect(self._salvar)
        btn_layout.addWidget(btn_salvar)

        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Data", "Descrição", "Tipo", "Origem", "Valor"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
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
            self.table.setItem(row, 0, QTableWidgetItem(str(lanc.data_lancamento)))
            self.table.setItem(row, 1, QTableWidgetItem(lanc.descricao))
            tipo_nome = self.input_tipo.itemText(
                self.input_tipo.findData(lanc.tipo_lancamento_id)
            ) if lanc.tipo_lancamento_id else ""
            self.table.setItem(row, 2, QTableWidgetItem(tipo_nome))
            self.table.setItem(row, 3, QTableWidgetItem(lanc.origem_informacao))
            self.table.setItem(row, 4, QTableWidgetItem(f"R$ {lanc.valor_total:,.2f}"))

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

    def _calcular_total(self) -> None:
        try:
            qtd_text = self.input_quantidade.text().strip().replace(".", "").replace(",", ".")
            unit_text = self.input_valor_unitario.text().strip().replace(".", "").replace(",", ".")
            qtd = float(qtd_text) if qtd_text else 1.0
            unit = float(unit_text) if unit_text else 0.0
            total = qtd * unit
            self.input_valor_total.setText(f"{total:.2f}")
        except ValueError:
            QMessageBox.warning(self, "Validação", "Quantidade ou valor unitário inválido.")

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

        valor_text = self.input_valor_total.text().strip().replace(".", "").replace(",", ".")
        try:
            valor_total = float(valor_text) if valor_text else 0.0
        except ValueError:
            QMessageBox.warning(self, "Validação", "Valor total inválido.")
            return

        qtd_text = self.input_quantidade.text().strip().replace(".", "").replace(",", ".")
        unit_text = self.input_valor_unitario.text().strip().replace(".", "").replace(",", ".")

        lancamento = Lancamento(
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

            QMessageBox.information(self, "Sucesso", "Lançamento salvo.")
            self._limpar_formulario()
            self._carregar_lancamentos()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar lançamento:\n{str(e)}")

    def _limpar_formulario(self) -> None:
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
