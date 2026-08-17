"""Container principal da aplicação com navegação por páginas."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from controle_obras.application.services import (
    AditivoService,
    AnexoService,
    BackupApplicationService,
    ConfiguracaoSistemaService,
    EmpresaService,
    LancamentoService,
    ObraResumoService,
    ObraService,
    RelatorioPDFService,
    TipoLancamentoService,
)
from controle_obras.infrastructure.database import DatabaseManager
from controle_obras.infrastructure.repositories import (
    AditivoRepository,
    AnexoRepository,
    ConfiguracaoRepository,
    EmpresaRepository,
    LancamentoRepository,
    ObraRepository,
    RelatorioRepository,
    TipoLancamentoRepository,
)
from controle_obras.infrastructure.storage import AppStorage
from controle_obras.ui.anexos_screen import AnexosScreen
from controle_obras.ui.dashboard_screen import DashboardScreen
from controle_obras.ui.empresa_screen import EmpresaScreen
from controle_obras.ui.lancamentos_screen import LancamentosScreen
from controle_obras.ui.obra_form_screen import ObraFormScreen
from controle_obras.ui.obras_list_screen import ObrasListScreen
from controle_obras.ui.styles import (
    BACKGROUND,
    PRIMARY,
    SURFACE,
    TEXT_PRIMARY,
    get_combo_header_style,
    get_header_button_style,
    get_header_style,
)
from controle_obras.ui.welcome_screen import WelcomeScreen


class AppContainer(QMainWindow):
    """Janela principal com navegação por QStackedWidget."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Controle de Obras")
        self.setMinimumSize(1200, 800)

        self._init_services()
        self._init_ui()
        self._check_first_run()

    def _init_services(self) -> None:
        self.storage = AppStorage()
        self.db = DatabaseManager(self.storage.db_path())
        self.db.init_schema()

        self.empresa_service = EmpresaService(EmpresaRepository(self.db))
        self.obra_service = ObraService(ObraRepository(self.db))
        self.aditivo_service = AditivoService(AditivoRepository(self.db))
        self.lancamento_service = LancamentoService(LancamentoRepository(self.db))
        self.anexo_service = AnexoService(AnexoRepository(self.db), self.storage)
        self.tipo_lancamento_service = TipoLancamentoService(TipoLancamentoRepository(self.db))
        self.config_service = ConfiguracaoSistemaService(ConfiguracaoRepository(self.db))
        self.resumo_service = ObraResumoService(
            ObraRepository(self.db),
            AditivoRepository(self.db),
            LancamentoRepository(self.db),
        )
        self.relatorio_service = RelatorioPDFService(
            self.obra_service,
            self.aditivo_service,
            self.lancamento_service,
            self.anexo_service,
            self.resumo_service,
            RelatorioRepository(self.db),
            self.storage,
        )

    def _init_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = self._build_header()
        layout.addWidget(self.header)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self.welcome_screen = WelcomeScreen(self)
        self.empresa_screen = EmpresaScreen(self)
        self.obras_list_screen = ObrasListScreen(self)
        self.obra_form_screen = ObraFormScreen(self)
        self.dashboard_screen = DashboardScreen(self)
        self.lancamentos_screen = LancamentosScreen(self)
        self.anexos_screen = AnexosScreen(self)

        self.stack.addWidget(self.welcome_screen)
        self.stack.addWidget(self.empresa_screen)
        self.stack.addWidget(self.obras_list_screen)
        self.stack.addWidget(self.obra_form_screen)
        self.stack.addWidget(self.dashboard_screen)
        self.stack.addWidget(self.lancamentos_screen)
        self.stack.addWidget(self.anexos_screen)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(50)
        header.setStyleSheet(get_header_style())

        main_layout = QHBoxLayout(header)
        main_layout.setContentsMargins(16, 0, 16, 0)
        main_layout.setSpacing(0)

        # Grupo esquerdo: título
        left_layout = QHBoxLayout()
        left_layout.setSpacing(8)
        self.title_label = QLabel("Controle de Obras")
        self.title_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {SURFACE};
            letter-spacing: 0.5px;
            padding: 0;
        """)
        left_layout.addWidget(self.title_label)
        main_layout.addLayout(left_layout)

        main_layout.addStretch(1)

        # Grupo central: seletor da obra (centralizado)
        center_layout = QHBoxLayout()
        center_layout.setSpacing(10)

        lbl_obra = QLabel("OBRA:")
        lbl_obra.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            padding: 0;
            color: {SURFACE};
            letter-spacing: 0.5px;
        """)
        lbl_obra.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        center_layout.addWidget(lbl_obra)

        self.combo_obras = QComboBox()
        self.combo_obras.setToolTip("Selecionar obra ativa")
        self.combo_obras.currentIndexChanged.connect(self._obra_selecionada)
        self.combo_obras.setStyleSheet(get_combo_header_style())
        center_layout.addWidget(self.combo_obras)

        main_layout.addLayout(center_layout)

        main_layout.addStretch(1)

        # Grupo direito: navegação
        right_layout = QHBoxLayout()
        right_layout.setSpacing(4)

        separator = QLabel("│")
        separator.setStyleSheet(f"color: rgba(255,255,255,0.2); padding: 0 6px; font-size: 16px;")
        right_layout.addWidget(separator)

        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_dashboard.clicked.connect(self.show_dashboard)
        self.btn_dashboard.setStyleSheet(get_header_button_style())
        right_layout.addWidget(self.btn_dashboard)

        self.btn_obras = QPushButton("Obras")
        self.btn_obras.clicked.connect(self.show_obras_list)
        self.btn_obras.setStyleSheet(get_header_button_style())
        right_layout.addWidget(self.btn_obras)

        self.btn_backup = QPushButton("Backup")
        self.btn_backup.clicked.connect(self._gerar_backup)
        self.btn_backup.setStyleSheet(get_header_button_style())
        right_layout.addWidget(self.btn_backup)

        self.btn_restore = QPushButton("Restaurar")
        self.btn_restore.clicked.connect(self._restaurar_backup)
        self.btn_restore.setStyleSheet(get_header_button_style())
        right_layout.addWidget(self.btn_restore)

        self.btn_config = QPushButton("⚙")
        self.btn_config.setToolTip("Configurações")
        self.btn_config.clicked.connect(self._abrir_configuracoes)
        self.btn_config.setStyleSheet(get_header_button_style())
        right_layout.addWidget(self.btn_config)

        main_layout.addLayout(right_layout)

        return header

    def _carregar_combo_obras(self) -> None:
        self.combo_obras.blockSignals(True)
        self.combo_obras.clear()
        obras = self.obra_service.listar()
        for obra in obras:
            self.combo_obras.addItem(f"{obra.codigo} - {obra.nome}", obra.id)
        self.combo_obras.blockSignals(False)

    def _obra_selecionada(self, index: int) -> None:
        if index < 0:
            return
        obra_id = self.combo_obras.itemData(index)
        if obra_id:
            self.set_obra_ativa(obra_id)
            # Atualizar a tela atual se depender da obra
            current = self.stack.currentWidget()
            if current == self.dashboard_screen:
                self.dashboard_screen.carregar(obra_id)
            elif current == self.lancamentos_screen:
                self.lancamentos_screen.carregar(obra_id)
            elif current == self.anexos_screen:
                self.anexos_screen.carregar(obra_id)

    def _check_first_run(self) -> None:
        if not self.empresa_service.empresa_configurada():
            self.show_welcome()
        else:
            self._carregar_combo_obras()
            obra_ativa_id = self.config_service.obter_obra_ativa()
            if obra_ativa_id:
                self.set_obra_ativa(obra_ativa_id)
                self.show_dashboard()
            else:
                self.show_obras_list()

    def show_welcome(self) -> None:
        self.stack.setCurrentWidget(self.welcome_screen)
        self._update_context("")

    def show_empresa(self) -> None:
        self.empresa_screen.carregar()
        self.stack.setCurrentWidget(self.empresa_screen)
        self._update_context("")

    def show_obras_list(self) -> None:
        self.obras_list_screen.carregar()
        self.stack.setCurrentWidget(self.obras_list_screen)
        self._update_context("")

    def show_obra_form(self, obra_id: int | None = None) -> None:
        self.obra_form_screen.carregar(obra_id)
        self.stack.setCurrentWidget(self.obra_form_screen)

    def show_dashboard(self) -> None:
        obra_ativa_id = self.config_service.obter_obra_ativa()
        if obra_ativa_id is None:
            self.show_obras_list()
            return
        self._carregar_combo_obras()
        self._selecionar_obra_no_combo(obra_ativa_id)
        self.dashboard_screen.carregar(obra_ativa_id)
        self.stack.setCurrentWidget(self.dashboard_screen)

    def show_lancamentos(self) -> None:
        obra_ativa_id = self.config_service.obter_obra_ativa()
        if obra_ativa_id is None:
            self.show_obras_list()
            return
        self.lancamentos_screen.carregar(obra_ativa_id)
        self.stack.setCurrentWidget(self.lancamentos_screen)

    def show_anexos(self) -> None:
        obra_ativa_id = self.config_service.obter_obra_ativa()
        if obra_ativa_id is None:
            self.show_obras_list()
            return
        self.anexos_screen.carregar(obra_ativa_id)
        self.stack.setCurrentWidget(self.anexos_screen)

    def set_obra_ativa(self, obra_id: int | None) -> None:
        self.config_service.definir_obra_ativa(obra_id)
        if obra_id:
            obra = self.obra_service.obter(obra_id)
            nome = obra.nome if obra else ""
            self._update_context(nome)
            self._selecionar_obra_no_combo(obra_id)
        else:
            self._update_context("")

    def _selecionar_obra_no_combo(self, obra_id: int) -> None:
        self.combo_obras.blockSignals(True)
        index = self.combo_obras.findData(obra_id)
        if index >= 0:
            self.combo_obras.setCurrentIndex(index)
        self.combo_obras.blockSignals(False)

    def _update_context(self, text: str) -> None:
        pass

    def _gerar_backup(self) -> None:
        from PySide6.QtWidgets import QFileDialog, QMessageBox

        from controle_obras.infrastructure.backup import BackupService as InfraBackupService

        try:
            backup_app = BackupApplicationService(
                InfraBackupService(self.storage, self.db),
                self.empresa_service,
                self.obra_service,
                self.anexo_service,
                self.storage,
            )
            destino = QFileDialog.getExistingDirectory(self, "Salvar backup em")
            if destino:
                caminho = backup_app.gerar_backup(destino)
                QMessageBox.information(self, "Backup", f"Backup gerado:\n{caminho}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gerar backup:\n{str(e)}")

    def _restaurar_backup(self) -> None:
        from PySide6.QtWidgets import QFileDialog, QMessageBox

        from controle_obras.infrastructure.backup import BackupService as InfraBackupService

        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecionar backup", "", "Arquivos ZIP (*.zip)"
        )
        if not caminho:
            return

        resposta = QMessageBox.warning(
            self,
            "Restaurar Backup",
            "ATENÇÃO: O estado atual do sistema será substituído.\n"
            "Um backup de segurança será criado automaticamente.\n"
            "Deseja continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            backup_app = BackupApplicationService(
                InfraBackupService(self.storage, self.db),
                self.empresa_service,
                self.obra_service,
                self.anexo_service,
                self.storage,
            )
            self.setEnabled(False)
            manifest = backup_app.restaurar_backup(caminho)
            self.setEnabled(True)
            QMessageBox.information(
                self,
                "Restauração",
                f"Backup restaurado com sucesso.\nEmpresa: {manifest.get('company_name', '')}",
            )
            self._check_first_run()
        except Exception as e:
            self.setEnabled(True)
            QMessageBox.critical(self, "Erro", f"Falha ao restaurar backup:\n{str(e)}")

    def _abrir_configuracoes(self) -> None:
        from PySide6.QtWidgets import QFormLayout, QLineEdit, QMessageBox

        empresa = self.empresa_service.obter()

        dialog = QDialog(self)
        dialog.setWindowTitle("Configurações")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(450)

        layout = QVBoxLayout(dialog)

        # Título
        titulo = QLabel("Configurações do Sistema")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        # Seção: Dados da Empresa
        secao_empresa = QLabel("Dados da Empresa")
        secao_empresa.setStyleSheet("font-size: 13px; font-weight: bold; color: #1B2A4A; margin-top: 10px;")
        layout.addWidget(secao_empresa)

        form_layout = QFormLayout()

        self.input_razao_social = QLineEdit(empresa.razao_social if empresa else "")
        form_layout.addRow("Razão Social *:", self.input_razao_social)

        self.input_nome_fantasia = QLineEdit(empresa.nome_fantasia if empresa else "")
        form_layout.addRow("Nome Fantasia:", self.input_nome_fantasia)

        self.input_cnpj_config = QLineEdit(empresa.cnpj if empresa else "")
        form_layout.addRow("CNPJ:", self.input_cnpj_config)

        self.input_telefone_config = QLineEdit(empresa.telefone if empresa else "")
        form_layout.addRow("Telefone:", self.input_telefone_config)

        self.input_email_config = QLineEdit(empresa.email if empresa else "")
        form_layout.addRow("E-mail:", self.input_email_config)

        self.input_endereco_config = QLineEdit(empresa.endereco if empresa else "")
        form_layout.addRow("Endereço:", self.input_endereco_config)

        self.input_cidade_config = QLineEdit(empresa.cidade if empresa else "")
        form_layout.addRow("Cidade:", self.input_cidade_config)

        self.input_uf_config = QLineEdit(empresa.uf if empresa else "")
        form_layout.addRow("UF:", self.input_uf_config)

        self.input_responsavel_config = QLineEdit(empresa.responsavel if empresa else "")
        form_layout.addRow("Responsável:", self.input_responsavel_config)

        layout.addLayout(form_layout)

        # Seção: Informações do Software
        secao_software = QLabel("Informações do Software")
        secao_software.setStyleSheet("font-size: 13px; font-weight: bold; color: #1B2A4A; margin-top: 10px;")
        layout.addWidget(secao_software)

        info_software = QLabel(
            "<b>Versão:</b> 1.0.0<br>"
            "<b>Desenvolvido por:</b> CASSIO REIS TECH<br>"
            "<b>Tecnologias:</b> Python, PySide6, SQLite<br>"
            "<b>Ano:</b> 2026"
        )
        info_software.setStyleSheet("font-size: 12px;")
        layout.addWidget(info_software)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(dialog.close)
        btn_layout.addWidget(btn_cancelar)

        btn_salvar = QPushButton("Salvar")
        btn_salvar.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 20px;
                background-color: {PRIMARY};
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #243656;
            }}
        """)
        btn_salvar.clicked.connect(lambda: self._salvar_configuracoes(dialog))
        btn_layout.addWidget(btn_salvar)

        layout.addLayout(btn_layout)

        dialog.exec()

    def _salvar_configuracoes(self, dialog: QDialog) -> None:
        from PySide6.QtWidgets import QMessageBox

        from controle_obras.domain.models import Empresa

        razao = self.input_razao_social.text().strip()
        if not razao:
            QMessageBox.warning(dialog, "Validação", "Razão social é obrigatória.")
            return

        try:
            empresa = self.empresa_service.obter()
            if not empresa:
                empresa = Empresa()

            empresa.razao_social = razao
            empresa.nome_fantasia = self.input_nome_fantasia.text().strip()
            empresa.cnpj = self.input_cnpj_config.text().strip()
            empresa.telefone = self.input_telefone_config.text().strip()
            empresa.email = self.input_email_config.text().strip()
            empresa.endereco = self.input_endereco_config.text().strip()
            empresa.cidade = self.input_cidade_config.text().strip()
            empresa.uf = self.input_uf_config.text().strip()
            empresa.responsavel = self.input_responsavel_config.text().strip()

            self.empresa_service.salvar(empresa)

            QMessageBox.information(dialog, "Sucesso", "Configurações salvas com sucesso!")
            dialog.close()
        except Exception as e:
            QMessageBox.critical(dialog, "Erro", f"Falha ao salvar configurações:\n{str(e)}")


def main() -> None:
    import sys

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AppContainer()
    window.show()
    sys.exit(app.exec())
