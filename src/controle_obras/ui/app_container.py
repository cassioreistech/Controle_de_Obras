"""Container principal da aplicação com navegação por páginas."""

from PySide6.QtWidgets import (
    QApplication,
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
        header.setStyleSheet("background-color: #2c3e50; color: white;")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 8, 16, 8)

        self.title_label = QLabel("Controle de Obras")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.context_label = QLabel("")
        self.context_label.setStyleSheet("font-size: 12px; color: #bdc3c7;")
        layout.addWidget(self.context_label, 1)

        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_dashboard.clicked.connect(self.show_dashboard)
        layout.addWidget(self.btn_dashboard)

        self.btn_obras = QPushButton("Obras")
        self.btn_obras.clicked.connect(self.show_obras_list)
        layout.addWidget(self.btn_obras)

        self.btn_lancamentos = QPushButton("Lançamentos")
        self.btn_lancamentos.clicked.connect(self.show_lancamentos)
        layout.addWidget(self.btn_lancamentos)

        self.btn_anexos = QPushButton("Anexos")
        self.btn_anexos.clicked.connect(self.show_anexos)
        layout.addWidget(self.btn_anexos)

        self.btn_backup = QPushButton("Backup")
        self.btn_backup.clicked.connect(self._gerar_backup)
        layout.addWidget(self.btn_backup)

        self.btn_restore = QPushButton("Restaurar")
        self.btn_restore.clicked.connect(self._restaurar_backup)
        layout.addWidget(self.btn_restore)

        return header

    def _check_first_run(self) -> None:
        if not self.empresa_service.empresa_configurada():
            self.show_welcome()
        else:
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
            self._update_context(f"Obra ativa: {obra.nome if obra else ''}")
        else:
            self._update_context("")

    def _update_context(self, text: str) -> None:
        self.context_label.setText(text)

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


def main() -> None:
    import sys

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AppContainer()
    window.show()
    sys.exit(app.exec())
