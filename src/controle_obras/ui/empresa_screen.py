"""Tela de cadastro inicial da empresa."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from controle_obras.domain.models import Empresa

if TYPE_CHECKING:
    from controle_obras.ui.app_container import AppContainer


class EmpresaScreen(QWidget):
    """Tela para cadastro e edição dos dados da empresa."""

    def __init__(self, parent: AppContainer) -> None:
        super().__init__()
        self._parent = parent
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Cadastro da Empresa")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(12)

        self.input_razao = QLineEdit()
        self.input_fantasia = QLineEdit()
        self.input_cnpj = QLineEdit()
        self.input_telefone = QLineEdit()
        self.input_email = QLineEdit()
        self.input_endereco = QLineEdit()
        self.input_cidade = QLineEdit()
        self.input_uf = QLineEdit()
        self.input_responsavel = QLineEdit()

        self.form_layout.addRow("Razão Social *", self.input_razao)
        self.form_layout.addRow("Nome Fantasia", self.input_fantasia)
        self.form_layout.addRow("CNPJ", self.input_cnpj)
        self.form_layout.addRow("Telefone", self.input_telefone)
        self.form_layout.addRow("E-mail", self.input_email)
        self.form_layout.addRow("Endereço", self.input_endereco)
        self.form_layout.addRow("Cidade", self.input_cidade)
        self.form_layout.addRow("UF", self.input_uf)
        self.form_layout.addRow("Responsável", self.input_responsavel)

        layout.addLayout(self.form_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_limpar = QPushButton("Limpar")
        btn_limpar.clicked.connect(self._limpar)
        btn_layout.addWidget(btn_limpar)

        btn_salvar = QPushButton("Salvar e Continuar")
        btn_salvar.setStyleSheet(
            "padding: 10px 24px; background-color: #27ae60; color: white;"
        )
        btn_salvar.clicked.connect(self._salvar)
        btn_layout.addWidget(btn_salvar)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def carregar(self) -> None:
        empresa = self._parent.empresa_service.obter()
        if empresa:
            self.input_razao.setText(empresa.razao_social)
            self.input_fantasia.setText(empresa.nome_fantasia)
            self.input_cnpj.setText(empresa.cnpj)
            self.input_telefone.setText(empresa.telefone)
            self.input_email.setText(empresa.email)
            self.input_endereco.setText(empresa.endereco)
            self.input_cidade.setText(empresa.cidade)
            self.input_uf.setText(empresa.uf)
            self.input_responsavel.setText(empresa.responsavel)

    def _limpar(self) -> None:
        self.input_razao.clear()
        self.input_fantasia.clear()
        self.input_cnpj.clear()
        self.input_telefone.clear()
        self.input_email.clear()
        self.input_endereco.clear()
        self.input_cidade.clear()
        self.input_uf.clear()
        self.input_responsavel.clear()

    def _salvar(self) -> None:
        razao = self.input_razao.text().strip()
        if not razao:
            QMessageBox.warning(self, "Validação", "Razão social é obrigatória.")
            return

        empresa = Empresa(
            razao_social=razao,
            nome_fantasia=self.input_fantasia.text().strip(),
            cnpj=self.input_cnpj.text().strip(),
            telefone=self.input_telefone.text().strip(),
            email=self.input_email.text().strip(),
            endereco=self.input_endereco.text().strip(),
            cidade=self.input_cidade.text().strip(),
            uf=self.input_uf.text().strip(),
            responsavel=self.input_responsavel.text().strip(),
        )

        empresa_existente = self._parent.empresa_service.obter()
        if empresa_existente:
            empresa.id = empresa_existente.id

        self._parent.empresa_service.salvar(empresa)
        QMessageBox.information(self, "Sucesso", "Empresa salva com sucesso.")
        self._parent.show_obras_list()
