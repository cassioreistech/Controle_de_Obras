"""Container principal da aplicação com navegação por páginas."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
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
        header.setFixedHeight(48)
        header.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
            }
            QPushButton {
                min-height: 28px;
                max-height: 30px;
                padding: 2px 10px;
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        main_layout = QHBoxLayout(header)
        main_layout.setContentsMargins(12, 0, 12, 0)
        main_layout.setSpacing(0)

        # Grupo esquerdo: título
        left_layout = QHBoxLayout()
        left_layout.setSpacing(6)
        self.title_label = QLabel("Controle de Obras")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; letter-spacing: 1px; padding: 0;")
        left_layout.addWidget(self.title_label)
        main_layout.addLayout(left_layout)

        main_layout.addStretch(1)

        # Grupo central: seletor da obra (centralizado)
        center_layout = QHBoxLayout()
        center_layout.setSpacing(8)

        lbl_obra = QLabel("OBRA:")
        lbl_obra.setStyleSheet("font-size: 14px; padding: 0; color: #e74c3c; font-weight: bold;")
        lbl_obra.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        center_layout.addWidget(lbl_obra)

        self.combo_obras = QComboBox()
        self.combo_obras.setToolTip("Selecionar obra ativa")
        self.combo_obras.currentIndexChanged.connect(self._obra_selecionada)
        self.combo_obras.setStyleSheet("""
            QComboBox {
                min-height: 28px;
                max-height: 30px;
                padding: 2px 8px;
                border: 1px solid #27ae60;
                border-radius: 3px;
                background-color: rgba(39, 174, 96, 0.15);
                color: white;
                font-size: 12px;
                font-weight: bold;
                min-width: 200px;
            }
            QComboBox:hover {
                border-color: #2ecc71;
                background-color: rgba(39, 174, 96, 0.25);
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #d5f5e3;
                selection-color: #2c3e50;
            }
            QComboBox QAbstractItemView::item {
                padding: 4px 8px;
                min-height: 24px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #27ae60;
                color: white;
            }
        """)
        center_layout.addWidget(self.combo_obras)

        self.btn_trocar = QPushButton("Trocar Obra")
        self.btn_trocar.setStyleSheet("""
            QPushButton {
                min-height: 28px;
                max-height: 30px;
                padding: 2px 12px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_trocar.clicked.connect(self.show_obras_list)
        center_layout.addWidget(self.btn_trocar)

        main_layout.addLayout(center_layout)

        main_layout.addStretch(1)

        # Grupo direito: navegação
        right_layout = QHBoxLayout()
        right_layout.setSpacing(6)

        separator = QLabel("|")
        separator.setStyleSheet("color: rgba(255,255,255,0.3); padding: 0 4px;")
        right_layout.addWidget(separator)

        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_dashboard.clicked.connect(self.show_dashboard)
        right_layout.addWidget(self.btn_dashboard)

        self.btn_obras = QPushButton("Obras")
        self.btn_obras.clicked.connect(self.show_obras_list)
        right_layout.addWidget(self.btn_obras)

        self.btn_backup = QPushButton("Backup")
        self.btn_backup.clicked.connect(self._gerar_backup)
        right_layout.addWidget(self.btn_backup)

        self.btn_restore = QPushButton("Restaurar")
        self.btn_restore.clicked.connect(self._restaurar_backup)
        right_layout.addWidget(self.btn_restore)

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
            obra_ativa_id = self.config_service.obter_obra_ativa()
            if self.stack.currentWidget() == self.dashboard_screen:
                self.dashboard_screen.carregar(obra_id)

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


def main() -> None:
    import sys

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AppContainer()
    window.show()
    sys.exit(app.exec())
