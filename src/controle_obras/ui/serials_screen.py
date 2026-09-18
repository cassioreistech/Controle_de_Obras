"""Tela de gerenciamento de seriais de licença."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
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

from controle_obras.domain.models import Serial

if TYPE_CHECKING:
    from controle_obras.ui.app_container import AppContainer

from controle_obras.ui.styles import (
    DANGER,
    DANGER_HOVER,
    PRIMARY,
    SUCCESS,
    TEXT_MUTED,
    get_input_style,
    get_screen_title_style,
    get_success_button_style,
    get_table_style,
)


class SerialsScreen(QWidget):
    """Tela para listar e gerenciar seriais de licença."""

    def __init__(self, parent: AppContainer) -> None:
        super().__init__()
        self._parent = parent
        self._seriais: list[Serial] = []
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Título e botão novo
        title_layout = QHBoxLayout()
        title = QLabel("Seriais de Licença")
        title.setStyleSheet(get_screen_title_style())
        title_layout.addWidget(title)

        self.lbl_contagem = QLabel("")
        self.lbl_contagem.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; margin-left: 8px;")
        title_layout.addWidget(self.lbl_contagem)
        title_layout.addStretch()

        btn_novo = QPushButton("Novo Serial")
        btn_novo.setToolTip("Registrar um novo serial de licença")
        btn_novo.setStyleSheet(get_success_button_style())
        btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_novo.clicked.connect(self._novo_serial)
        title_layout.addWidget(btn_novo)

        layout.addLayout(title_layout)

        # Painel de estatísticas
        stats_layout = QHBoxLayout()
        self.lbl_total = self._criar_label_stats("Total", "0")
        self.lbl_ativos = self._criar_label_stats("Ativos", "0")
        self.lbl_inativos = self._criar_label_stats("Inativos", "0")
        self.lbl_expirados = self._criar_label_stats("Expirados", "0")

        stats_layout.addWidget(self.lbl_total)
        stats_layout.addWidget(self.lbl_ativos)
        stats_layout.addWidget(self.lbl_inativos)
        stats_layout.addWidget(self.lbl_expirados)
        stats_layout.addStretch()

        layout.addLayout(stats_layout)

        # Filtros
        filtro_layout = QHBoxLayout()
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Buscar por chave, cliente ou empresa...")
        self.input_busca.textChanged.connect(self._aplicar_filtro)
        self.input_busca.setStyleSheet(get_input_style())
        filtro_layout.addWidget(self.input_busca)

        layout.addLayout(filtro_layout)

        # Tabela de seriais
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Chave", "Cliente", "Empresa", "Máquina ID", "Validade", "Status", "Ações"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setStyleSheet(get_table_style(PRIMARY))
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table)

        # Botões de ação
        acoes_layout = QHBoxLayout()
        btn_atualizar = QPushButton("Atualizar")
        btn_atualizar.setStyleSheet(get_success_button_style())
        btn_atualizar.clicked.connect(self._atualizar_lista)
        acoes_layout.addWidget(btn_atualizar)

        btn_expirados = QPushButton("Marcar Expirados")
        btn_expirados.setStyleSheet(f"background-color: {DANGER}; color: white; padding: 8px 16px; border-radius: 4px;")
        btn_expirados.clicked.connect(self._marcar_expirados)
        acoes_layout.addWidget(btn_expirados)

        acoes_layout.addStretch()
        layout.addLayout(acoes_layout)

        # Carregar dados iniciais
        self._atualizar_lista()

    def _criar_label_stats(self, titulo: str, valor: str) -> QLabel:
        """Cria um label de estatísticas."""
        label = QLabel(f"{titulo}: {valor}")
        label.setStyleSheet(
            f"background-color: #f0f0f0; padding: 8px 16px; border-radius: 4px; "
            f"font-weight: bold; color: {PRIMARY};"
        )
        return label

    def _atualizar_lista(self) -> None:
        """Atualiza a lista de seriais na tabela."""
        serial_service = self._parent.serial_service
        self._seriais = serial_service.listar_todos()
        self._preencher_tabela(self._seriais)
        self._atualizar_estatisticas()

    def _preencher_tabela(self, seriais: list[Serial]) -> None:
        """Preenche a tabela com os seriais."""
        self.table.setRowCount(len(seriais))

        for row, serial in enumerate(seriais):
            # Chave
            item_chave = QTableWidgetItem(serial.chave)
            item_chave.setData(Qt.ItemDataRole.UserRole, serial.id)
            self.table.setItem(row, 0, item_chave)

            # Cliente
            self.table.setItem(row, 1, QTableWidgetItem(serial.cliente_nome))

            # Empresa
            self.table.setItem(row, 2, QTableWidgetItem(serial.cliente_empresa))

            # Máquina ID
            self.table.setItem(row, 3, QTableWidgetItem(serial.maquina_id[:8] + "..."))

            # Validade
            item_validade = QTableWidgetItem(serial.data_validade.strftime("%d/%m/%Y"))
            if serial.data_validade < date.today() and serial.status == "Ativo":
                item_validade.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 4, item_validade)

            # Status
            item_status = QTableWidgetItem(serial.status)
            if serial.status == "Ativo":
                item_status.setForeground(Qt.GlobalColor.darkGreen)
            elif serial.status == "Inativo":
                item_status.setForeground(Qt.GlobalColor.gray)
            elif serial.status == "Expirado":
                item_status.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 5, item_status)

            # Botões de ação
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(4)

            btn_editar = QPushButton("Editar")
            btn_editar.setStyleSheet(f"background-color: {PRIMARY}; color: white; padding: 4px 8px; border-radius: 3px; font-size: 11px;")
            btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_editar.clicked.connect(lambda checked, sid=serial.id: self._editar_serial(sid))
            btn_layout.addWidget(btn_editar)

            btn_excluir = QPushButton("Excluir")
            btn_excluir.setStyleSheet(f"background-color: {DANGER}; color: white; padding: 4px 8px; border-radius: 3px; font-size: 11px;")
            btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_excluir.clicked.connect(lambda checked, sid=serial.id: self._excluir_serial(sid))
            btn_layout.addWidget(btn_excluir)

            self.table.setCellWidget(row, 6, btn_widget)

        self.lbl_contagem.setText(f"({len(seriais)} seriais)")

    def _atualizar_estatisticas(self) -> None:
        """Atualiza os labels de estatísticas."""
        stats = self._parent.serial_service.obter_estatisticas()
        self.lbl_total.setText(f"Total: {stats['total']}")
        self.lbl_ativos.setText(f"Ativos: {stats['ativos']}")
        self.lbl_inativos.setText(f"Inativos: {stats['inativos']}")
        self.lbl_expirados.setText(f"Expirados: {stats['expirados']}")

    def _aplicar_filtro(self) -> None:
        """Aplica filtro de busca na tabela."""
        texto = self.input_busca.text().lower()
        if not texto:
            self._preencher_tabela(self._seriais)
            return

        filtrados = [
            s for s in self._seriais
            if texto in s.chave.lower()
            or texto in s.cliente_nome.lower()
            or texto in s.cliente_empresa.lower()
        ]
        self._preencher_tabela(filtrados)

    def _novo_serial(self) -> None:
        """Abre formulário para novo serial."""
        dialog = SerialFormDialog(self._parent, parent=self)
        if dialog.exec():
            self._atualizar_lista()

    def _editar_serial(self, serial_id: int) -> None:
        """Abre formulário para editar serial."""
        serial = self._parent.serial_service.buscar_por_id(serial_id)
        if not serial:
            QMessageBox.warning(self, "Erro", "Serial não encontrado.")
            return

        dialog = SerialFormDialog(self._parent, serial=serial, parent=self)
        if dialog.exec():
            self._atualizar_lista()

    def _excluir_serial(self, serial_id: int) -> None:
        """Exclui um serial."""
        reply = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir este serial?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self._parent.serial_service.excluir(serial_id):
                self._atualizar_lista()
                QMessageBox.information(self, "Sucesso", "Serial excluído com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Erro ao excluir serial.")

    def _marcar_expirados(self) -> None:
        """Marca seriais expirados automaticamente."""
        atualizados = self._parent.serial_service.atualizar_expirados()
        self._atualizar_lista()
        if atualizados > 0:
            QMessageBox.information(
                self,
                "Sucesso",
                f"{atualizados} serial(is) expirado(s) atualizado(s)!",
            )
        else:
            QMessageBox.information(
                self,
                "Informação",
                "Nenhum serial expirado encontrado para atualizar.",
            )


class SerialFormDialog(QDialog):
    """Diálogo para cadastro/edição de serial."""

    def __init__(
        self,
        parent: AppContainer,
        serial: Serial | None = None,
        parent_widget: QWidget | None = None,
    ) -> None:
        super().__init__(parent_widget)
        self._parent = parent
        self._serial = serial
        self._is_editing = serial is not None

        self.setWindowTitle("Editar Serial" if self._is_editing else "Novo Serial")
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)

        self._init_ui()

        if self._is_editing and serial:
            self._preencher_dados(serial)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Chave
        self.input_chave = QLineEdit()
        self.input_chave.setPlaceholderText("Ex.: 20261231-ABC12")
        if not self._is_editing:
            self.input_chave.setStyleSheet(get_input_style())
        else:
            self.input_chave.setReadOnly(True)
            self.input_chave.setStyleSheet("background-color: #f0f0f0; padding: 8px; border-radius: 4px;")
        form_layout.addRow("Chave:", self.input_chave)

        # Nome do Cliente
        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Nome completo do cliente")
        self.input_cliente.setStyleSheet(get_input_style())
        form_layout.addRow("Cliente:", self.input_cliente)

        # Empresa
        self.input_empresa = QLineEdit()
        self.input_empresa.setPlaceholderText("Nome da empresa")
        self.input_empresa.setStyleSheet(get_input_style())
        form_layout.addRow("Empresa:", self.input_empresa)

        # Contato
        self.input_contato = QLineEdit()
        self.input_contato.setPlaceholderText("Telefone ou email")
        self.input_contato.setStyleSheet(get_input_style())
        form_layout.addRow("Contato:", self.input_contato)

        # Máquina ID (somente leitura se editando)
        if self._is_editing:
            self.input_maquina = QLineEdit()
            self.input_maquina.setReadOnly(True)
            self.input_maquina.setStyleSheet("background-color: #f0f0f0; padding: 8px; border-radius: 4px;")
        else:
            self.input_maquina = QLineEdit()
            self.input_maquina.setPlaceholderText("ID da máquina do cliente")
            self.input_maquina.setStyleSheet(get_input_style())
        form_layout.addRow("Máquina ID:", self.input_maquina)

        # Data de Validade
        self.input_validade = QLineEdit()
        self.input_validade.setPlaceholderText("YYYY-MM-DD")
        self.input_validade.setStyleSheet(get_input_style())
        form_layout.addRow("Validade:", self.input_validade)

        # Observações
        self.input_observacoes = QTextEdit()
        self.input_observacoes.setPlaceholderText("Observações opcionais...")
        self.input_observacoes.setMaximumHeight(80)
        self.input_observacoes.setStyleSheet(get_input_style())
        form_layout.addRow("Observações:", self.input_observacoes)

        # Status (somente na edição)
        if self._is_editing:
            self.input_status = QLineEdit()
            self.input_status.setPlaceholderText("Ativo, Inativo ou Expirado")
            self.input_status.setStyleSheet(get_input_style())
            form_layout.addRow("Status:", self.input_status)

        layout.addLayout(form_layout)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("background-color: #6c757d; color: white; padding: 8px 16px; border-radius: 4px;")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        btn_salvar = QPushButton("Salvar")
        btn_salvar.setStyleSheet(get_success_button_style())
        btn_salvar.clicked.connect(self._salvar)
        btn_layout.addWidget(btn_salvar)

        layout.addLayout(btn_layout)

    def _preencher_dados(self, serial: Serial) -> None:
        """Preenche o formulário com dados do serial."""
        self.input_chave.setText(serial.chave)
        self.input_cliente.setText(serial.cliente_nome)
        self.input_empresa.setText(serial.cliente_empresa)
        self.input_contato.setText(serial.cliente_contato)
        self.input_maquina.setText(serial.maquina_id)
        self.input_validade.setText(serial.data_validade.isoformat())
        self.input_observacoes.setText(serial.observacoes)
        if hasattr(self, "input_status"):
            self.input_status.setText(serial.status)

    def _salvar(self) -> None:
        """Salva o serial."""
        # Validações
        chave = self.input_chave.text().strip().upper()
        if not chave:
            QMessageBox.warning(self, "Erro", "Chave é obrigatória.")
            return

        cliente = self.input_cliente.text().strip()
        if not cliente:
            QMessageBox.warning(self, "Erro", "Nome do cliente é obrigatório.")
            return

        maquina = self.input_maquina.text().strip()
        if not maquina:
            QMessageBox.warning(self, "Erro", "ID da máquina é obrigatório.")
            return

        validade_str = self.input_validade.text().strip()
        if not validade_str:
            QMessageBox.warning(self, "Erro", "Data de validade é obrigatória.")
            return

        try:
            from datetime import datetime
            validade = datetime.strptime(validade_str, "%Y-%m-%d").date()
        except ValueError:
            QMessageBox.warning(self, "Erro", "Data de validade inválida. Use o formato YYYY-MM-DD.")
            return

        empresa = self.input_empresa.text().strip()
        contato = self.input_contato.text().strip()
        observacoes = self.input_observacoes.toPlainText().strip()

        try:
            if self._is_editing and self._serial:
                # Atualizar
                self._parent.serial_service.atualizar_serial(
                    self._serial.id,
                    cliente_nome=cliente,
                    cliente_empresa=empresa,
                    cliente_contato=contato,
                    observacoes=observacoes,
                    status=self.input_status.text().strip() if hasattr(self, "input_status") else self._serial.status,
                )
                QMessageBox.information(self, "Sucesso", "Serial atualizado com sucesso!")
            else:
                # Criar novo
                self._parent.serial_service.registrar_serial(
                    chave=chave,
                    cliente_nome=cliente,
                    cliente_empresa=empresa,
                    cliente_contato=contato,
                    maquina_id=maquina,
                    data_validade=validade,
                    observacoes=observacoes,
                )
                QMessageBox.information(self, "Sucesso", "Serial registrado com sucesso!")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar serial: {e}")
