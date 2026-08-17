"""Tela de cadastro e edição de obra."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from controle_obras.domain.models import Obra

if TYPE_CHECKING:
    from controle_obras.ui.app_container import AppContainer


class ObraFormScreen(QWidget):
    """Tela para criar ou editar uma obra."""

    def __init__(self, parent: AppContainer) -> None:
        super().__init__()
        self._parent = parent
        self._obra_id: int | None = None
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.title = QLabel("Nova Obra")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.title)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.input_codigo = QLineEdit()
        self.input_nome = QLineEdit()
        self.input_cliente = QLineEdit()
        self.input_local = QLineEdit()
        self.input_engenheiro = QLineEdit()
        self.input_data_inicio = QDateEdit()
        self.input_data_inicio.setCalendarPopup(True)
        self.input_data_inicio.setDate(date.today())
        self.input_previsao = QDateEdit()
        self.input_previsao.setCalendarPopup(True)
        self.input_previsao.setDate(date.today())
        self.input_status = QComboBox()
        self.input_status.addItems(["Em andamento", "Concluída", "Pausada", "Cancelada"])
        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("0,00")
        self.input_observacoes = QTextEdit()
        self.input_observacoes.setMaximumHeight(120)

        form_layout.addRow("Código *", self.input_codigo)
        form_layout.addRow("Nome *", self.input_nome)
        form_layout.addRow("Cliente Contratante", self.input_cliente)
        form_layout.addRow("Local da Obra", self.input_local)
        form_layout.addRow("Engenheiro Responsável", self.input_engenheiro)
        form_layout.addRow("Data de Início", self.input_data_inicio)
        form_layout.addRow("Previsão de Término", self.input_previsao)
        form_layout.addRow("Status", self.input_status)
        form_layout.addRow("Valor Contratado Inicial *", self.input_valor)
        form_layout.addRow("Observações", self.input_observacoes)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self._parent.show_obras_list)
        btn_layout.addWidget(btn_cancelar)

        btn_salvar = QPushButton("Salvar")
        btn_salvar.setStyleSheet("padding: 10px 24px; background-color: #27ae60; color: white;")
        btn_salvar.clicked.connect(self._salvar)
        btn_layout.addWidget(btn_salvar)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def carregar(self, obra_id: int | None = None) -> None:
        self._obra_id = obra_id
        if obra_id:
            self.title.setText("Editar Obra")
            obra = self._parent.obra_service.obter(obra_id)
            if obra:
                self.input_codigo.setText(obra.codigo)
                self.input_nome.setText(obra.nome)
                self.input_cliente.setText(obra.cliente_contratante)
                self.input_local.setText(obra.local_obra)
                self.input_engenheiro.setText(obra.engenheiro_responsavel)
                if obra.data_inicio:
                    self.input_data_inicio.setDate(obra.data_inicio)
                if obra.previsao_termino:
                    self.input_previsao.setDate(obra.previsao_termino)
                self.input_status.setCurrentText(obra.status)
                self.input_valor.setText(str(obra.valor_contratado_inicial))
                self.input_observacoes.setPlainText(obra.observacoes)
        else:
            self.title.setText("Nova Obra")
            self._limpar_campos()

    def _limpar_campos(self) -> None:
        self.input_codigo.clear()
        self.input_nome.clear()
        self.input_cliente.clear()
        self.input_local.clear()
        self.input_engenheiro.clear()
        self.input_data_inicio.setDate(date.today())
        self.input_previsao.setDate(date.today())
        self.input_status.setCurrentIndex(0)
        self.input_valor.clear()
        self.input_observacoes.clear()

    def _salvar(self) -> None:
        codigo = self.input_codigo.text().strip()
        nome = self.input_nome.text().strip()
        valor_text = self.input_valor.text().strip().replace(".", "").replace(",", ".")

        if not codigo or not nome:
            QMessageBox.warning(self, "Validação", "Código e nome são obrigatórios.")
            return

        try:
            valor = float(valor_text) if valor_text else 0.0
        except ValueError:
            QMessageBox.warning(self, "Validação", "Valor contratado inválido.")
            return

        obra = Obra(
            id=self._obra_id,
            codigo=codigo,
            nome=nome,
            cliente_contratante=self.input_cliente.text().strip(),
            local_obra=self.input_local.text().strip(),
            engenheiro_responsavel=self.input_engenheiro.text().strip(),
            data_inicio=self.input_data_inicio.date().toPython(),
            previsao_termino=self.input_previsao.date().toPython(),
            status=self.input_status.currentText(),
            valor_contratado_inicial=valor,
            observacoes=self.input_observacoes.toPlainText().strip(),
        )

        try:
            self._parent.obra_service.salvar(obra)
            QMessageBox.information(self, "Sucesso", "Obra salva com sucesso.")
            self._parent.show_obras_list()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar obra:\n{str(e)}")
