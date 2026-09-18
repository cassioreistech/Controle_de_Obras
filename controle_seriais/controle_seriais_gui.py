"""Interface Gráfica Portátil de Gerenciamento de Seriais - Controle de Obras.

Ferramenta standalone com GUI (PySide6) para gerenciar seriais de licença.
Completamente independente do sistema principal do cliente.

Uso:
    python controle_seriais_gui.py
"""

import sys
from datetime import date, datetime
from pathlib import Path

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QLabel, QComboBox, QDateEdit, QTextEdit,
    QMessageBox, QHeaderView, QGroupBox, QFormLayout, QFrame,
    QSplitter, QStatusBar, QAbstractItemView
)

from controle_seriais import DatabaseManager, SerialService, Serial, gerar_chave, obter_maquina_id


# ==========================================
# ESTILO GLOBAL
# ==========================================

ESTILO = """
QMainWindow {
    background-color: #1e1e2e;
}
QTabWidget::pane {
    border: 1px solid #313244;
    background-color: #1e1e2e;
    border-radius: 6px;
}
QTabBar::tab {
    background-color: #313244;
    color: #cdd6f4;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-size: 13px;
}
QTabBar::tab:selected {
    background-color: #45475a;
    color: #89b4fa;
}
QTabBar::tab:hover {
    background-color: #45475a;
}
QGroupBox {
    font-size: 14px;
    font-weight: bold;
    color: #89b4fa;
    border: 1px solid #313244;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 15px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px;
}
QLabel {
    color: #cdd6f4;
    font-size: 12px;
}
QLineEdit, QComboBox, QDateEdit, QTextEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
    border: 1px solid #89b4fa;
}
QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 4px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #74c7ec;
}
QPushButton:pressed {
    background-color: #89dceb;
}
QPushButton#btn_excluir {
    background-color: #f38ba8;
}
QPushButton#btn_excluir:hover {
    background-color: #eba0ac;
}
QPushButton#btn_inativo {
    background-color: #fab387;
}
QPushButton#btn_inativo:hover {
    background-color: #f9e2af;
}
QPushButton#btn_gerar {
    background-color: #a6e3a1;
    color: #1e1e2e;
}
QPushButton#btn_gerar:hover {
    background-color: #94e2d5;
}
QTableWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    gridline-color: #313244;
    border: 1px solid #313244;
    border-radius: 6px;
    font-size: 12px;
    selection-background-color: #45475a;
}
QTableWidget::item {
    padding: 6px;
}
QHeaderView::section {
    background-color: #313244;
    color: #89b4fa;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #89b4fa;
    font-weight: bold;
    font-size: 12px;
}
QStatusBar {
    background-color: #313244;
    color: #cdd6f4;
}
QFrame#separator {
    background-color: #313244;
    max-width: 1px;
}
QLabel#stat_valor {
    font-size: 28px;
    font-weight: bold;
    color: #89b4fa;
}
QLabel#stat_label {
    font-size: 11px;
    color: #6c7086;
    text-transform: uppercase;
}
"""


# ==========================================
# JANELA PRINCIPAL
# ==========================================

class GerenciadorSeriaisGUI(QMainWindow):
    """Janela principal do gerenciador de seriais."""
    
    def __init__(self):
        super().__init__()
        
        self.db = DatabaseManager()
        self.service = SerialService(self.db)
        
        self.setWindowTitle("Gerenciador de Seriais - Controle de Obras")
        self.setMinimumSize(1000, 650)
        self.resize(1100, 700)
        
        self._setup_ui()
        self._atualizar_tabela()
        self._atualizar_estatisticas()
    
    def _setup_ui(self):
        """Monta a interface."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #181825; padding: 12px;")
        header_layout = QHBoxLayout(header)
        
        titulo = QLabel("GERENCIADOR DE SERIAIS")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #89b4fa;")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        self.lbl_maquina = QLabel(f"ID Máquina: {obter_maquina_id()}")
        self.lbl_maquina.setStyleSheet("font-size: 11px; color: #6c7086;")
        header_layout.addWidget(self.lbl_maquina)
        
        layout.addWidget(header)
        
        # Stats bar
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background-color: #181825; padding: 8px;")
        stats_layout = QHBoxLayout(stats_frame)
        
        self.stat_total = self._criar_stat("0", "TOTAL")
        self.stat_ativos = self._criar_stat("0", "ATIVOS")
        self.stat_inativos = self._criar_stat("0", "INATIVOS")
        self.stat_expirados = self._criar_stat("0", "EXPIRADOS")
        
        for stat in [self.stat_total, self.stat_ativos, self.stat_inativos, self.stat_expirados]:
            stats_layout.addWidget(stat)
        
        layout.addWidget(stats_frame)
        
        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._criar_tab_listar(), "Lista de Seriais")
        tabs.addTab(self._criar_tab_registrar(), "Novo Serial")
        tabs.addTab(self._criar_tab_gerar(), "Gerar Chave")
        
        layout.addWidget(tabs)
        
        # Status bar
        self.statusBar().showMessage("Pronto")
    
    def _criar_stat(self, valor: str, label: str) -> QFrame:
        """Cria um widget de estatística."""
        frame = QFrame()
        frame.setStyleSheet("background-color: #1e1e2e; border-radius: 6px; padding: 8px;")
        layout = QVBoxLayout(frame)
        layout.setSpacing(2)
        
        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName("stat_valor")
        lbl_valor.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_valor)
        
        lbl_label = QLabel(label)
        lbl_label.setObjectName("stat_label")
        lbl_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_label)
        
        frame._lbl_valor = lbl_valor
        return frame
    
    def _criar_tab_listar(self) -> QWidget:
        """Cria aba de listagem."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Barra de busca
        busca_layout = QHBoxLayout()
        
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Buscar por chave, cliente, empresa...")
        self.input_busca.textChanged.connect(self._filtrar_tabela)
        busca_layout.addWidget(self.input_busca)
        
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Todos", "Ativo", "Inativo", "Expirado"])
        self.combo_status.currentTextChanged.connect(self._filtrar_tabela)
        self.combo_status.setFixedWidth(120)
        busca_layout.addWidget(self.combo_status)
        
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self._filtrar_tabela)
        busca_layout.addWidget(btn_buscar)
        
        layout.addLayout(busca_layout)
        
        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Chave", "Cliente", "Empresa", "Validade", "Status", "Observações", "Ações"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tabela.setColumnWidth(0, 45)
        self.tabela.setColumnWidth(1, 140)
        self.tabela.setColumnWidth(6, 200)
        self.tabela.setColumnWidth(7, 180)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setStyleSheet("""
            QTableWidget { alternate-background-color: #181825; }
        """)
        
        layout.addWidget(self.tabela)
        
        # Botões de ação
        acoes_layout = QHBoxLayout()
        
        btn_atualizar = QPushButton("Atualizar")
        btn_atualizar.clicked.connect(self._atualizar_tabela)
        acoes_layout.addWidget(btn_atualizar)
        
        acoes_layout.addStretch()
        
        btn_excluir_sel = QPushButton("Excluir Selecionado")
        btn_excluir_sel.setObjectName("btn_excluir")
        btn_excluir_sel.clicked.connect(self._excluir_selecionado)
        acoes_layout.addWidget(btn_excluir_sel)
        
        layout.addLayout(acoes_layout)
        
        return widget
    
    def _criar_tab_registrar(self) -> QWidget:
        """Cria aba de registro."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Formulário
        form_group = QGroupBox("Registrar Novo Serial")
        form_layout = QFormLayout(form_group)
        
        self.reg_chave = QLineEdit()
        self.reg_chave.setPlaceholderText("AAAAAMMDD-XXXXX")
        form_layout.addRow("Chave:", self.reg_chave)
        
        self.reg_cliente = QLineEdit()
        self.reg_cliente.setPlaceholderText("Nome do cliente")
        form_layout.addRow("Cliente:", self.reg_cliente)
        
        self.reg_empresa = QLineEdit()
        self.reg_empresa.setPlaceholderText("Nome da empresa")
        form_layout.addRow("Empresa:", self.reg_empresa)
        
        self.reg_contato = QLineEdit()
        self.reg_contato.setPlaceholderText("Telefone / Email")
        form_layout.addRow("Contato:", self.reg_contato)
        
        self.reg_maquina = QLineEdit()
        self.reg_maquina.setPlaceholderText("ID da máquina do cliente (deixe vazio para usar a atual)")
        form_layout.addRow("Máquina ID:", self.reg_maquina)
        
        self.reg_validade = QDateEdit()
        self.reg_validade.setCalendarPopup(True)
        self.reg_validade.setDate(QDate.currentDate().addYears(1))
        self.reg_validade.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("Validade:", self.reg_validade)
        
        self.reg_obs = QTextEdit()
        self.reg_obs.setPlaceholderText("Observações (opcional)")
        self.reg_obs.setMaximumHeight(80)
        form_layout.addRow("Observações:", self.reg_obs)
        
        layout.addWidget(form_group)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        btn_registrar = QPushButton("Registrar Serial")
        btn_registrar.clicked.connect(self._registrar_serial)
        btn_layout.addWidget(btn_registrar)
        
        btn_limpar = QPushButton("Limpar")
        btn_limpar.clicked.connect(self._limpar_formulario)
        btn_layout.addWidget(btn_limpar)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        return widget
    
    def _criar_tab_gerar(self) -> QWidget:
        """Cria aba de geração de chave."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Gerar chave
        gerar_group = QGroupBox("Gerar Nova Chave de Licença")
        gerar_layout = QFormLayout(gerar_group)
        
        self.gerar_validade = QDateEdit()
        self.gerar_validade.setCalendarPopup(True)
        self.gerar_validade.setDate(QDate.currentDate().addYears(1))
        self.gerar_validade.setDisplayFormat("dd/MM/yyyy")
        gerar_layout.addRow("Data de Validade:", self.gerar_validade)
        
        self.gerar_maquina = QLineEdit()
        self.gerar_maquina.setPlaceholderText("Deixe vazio para usar esta máquina")
        gerar_layout.addRow("ID Máquina:", self.gerar_maquina)
        
        layout.addWidget(gerar_group)
        
        # Botão gerar
        btn_gerar = QPushButton("Gerar Chave")
        btn_gerar.setObjectName("btn_gerar")
        btn_gerar.clicked.connect(self._gerar_chave)
        layout.addWidget(btn_gerar)
        
        # Resultado
        resultado_group = QGroupBox("Chave Gerada")
        resultado_layout = QVBoxLayout(resultado_group)
        
        self.resultado_chave = QLineEdit()
        self.resultado_chave.setReadOnly(True)
        self.resultado_chave.setStyleSheet("font-size: 18px; font-weight: bold; color: #a6e3a1;")
        resultado_layout.addWidget(self.resultado_chave)
        
        self.btn_copiar = QPushButton("Copiar Chave")
        self.btn_copiar.clicked.connect(self._copiar_chave)
        resultado_layout.addWidget(self.btn_copiar)
        
        self.btn_registrar_gerada = QPushButton("Registrar Esta Chave")
        self.btn_registrar_gerada.clicked.connect(self._registrar_chave_gerada)
        resultado_layout.addWidget(self.btn_registrar_gerada)
        
        layout.addWidget(resultado_group)
        
        # Info
        info = QLabel("A chave gerada pode ser registrada diretamente na aba 'Novo Serial'.")
        info.setStyleSheet("color: #6c7086; font-style: italic;")
        layout.addWidget(info)
        
        layout.addStretch()
        
        return widget
    
    def _atualizar_tabela(self):
        """Atualiza a tabela com todos os seriais."""
        seriais = self.service.listar_todos()
        self._preencher_tabela(seriais)
        self.statusBar().showMessage(f"Total: {len(seriais)} seriais")
    
    def _preencher_tabela(self, seriais: list[Serial]):
        """Preenche a tabela com a lista de seriais."""
        self.tabela.setRowCount(len(seriais))
        
        for i, s in enumerate(seriais):
            status_cor = {
                "Ativo": QColor("#a6e3a1"),
                "Inativo": QColor("#fab387"),
                "Expirado": QColor("#f38ba8"),
            }.get(s.status, QColor("#cdd6f4"))
            
            # ID
            item_id = QTableWidgetItem(str(s.id))
            item_id.setTextAlign(Qt.AlignCenter)
            self.tabela.setItem(i, 0, item_id)
            
            # Chave
            item_chave = QTableWidgetItem(s.chave)
            fonte = QFont("Consolas", 11)
            fonte.setBold(True)
            item_chave.setFont(fonte)
            self.tabela.setItem(i, 1, item_chave)
            
            # Cliente
            self.tabela.setItem(i, 2, QTableWidgetItem(s.cliente_nome))
            
            # Empresa
            self.tabela.setItem(i, 3, QTableWidgetItem(s.cliente_empresa))
            
            # Validade
            item_validade = QTableWidgetItem(s.data_validade.strftime("%d/%m/%Y"))
            item_validade.setTextAlign(Qt.AlignCenter)
            if s.data_validade < date.today() and s.status == "Ativo":
                item_validade.setForeground(QColor("#f38ba8"))
            self.tabela.setItem(i, 4, item_validade)
            
            # Status
            item_status = QTableWidgetItem(s.status)
            item_status.setTextAlign(Qt.AlignCenter)
            item_status.setForeground(status_cor)
            fonte_status = QFont()
            fonte_status.setBold(True)
            item_status.setFont(fonte_status)
            self.tabela.setItem(i, 5, item_status)
            
            # Observações
            self.tabela.setItem(i, 6, QTableWidgetItem(s.observacoes))
            
            # Botões de ação
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setSpacing(4)
            
            btn_status = QPushButton("Inativar" if s.status == "Ativo" else "Ativar")
            btn_status.setObjectName("btn_inativo" if s.status == "Ativo" else "")
            btn_status.setFixedHeight(26)
            btn_status.clicked.connect(lambda _, sid=s.id, st=s.status: self._toggle_status(sid, st))
            btn_layout.addWidget(btn_status)
            
            btn_del = QPushButton("Excluir")
            btn_del.setObjectName("btn_excluir")
            btn_del.setFixedHeight(26)
            btn_del.clicked.connect(lambda _, sid=s.id, ch=s.chave: self._excluir_serial(sid, ch))
            btn_layout.addWidget(btn_del)
            
            self.tabela.setCellWidget(i, 7, btn_widget)
            self.tabela.setRowHeight(i, 40)
    
    def _filtrar_tabela(self):
        """Filtra tabela por busca e status."""
        texto = self.input_busca.text().lower()
        status = self.combo_status.currentText()
        
        seriais = self.service.listar_todos()
        
        filtrados = []
        for s in seriais:
            if status != "Todos" and s.status != status:
                continue
            if texto and texto not in s.chave.lower() and texto not in s.cliente_nome.lower() \
                    and texto not in s.cliente_empresa.lower() and texto not in s.observacoes.lower():
                continue
            filtrados.append(s)
        
        self._preencher_tabela(filtrados)
        self.statusBar().showMessage(f"Filtrados: {len(filtrados)} de {len(seriais)} seriais")
    
    def _atualizar_estatisticas(self):
        """Atualiza as estatísticas."""
        stats = self.service.estatisticas()
        self.stat_total._lbl_valor.setText(str(stats["total"]))
        self.stat_ativos._lbl_valor.setText(str(stats["ativos"]))
        self.stat_inativos._lbl_valor.setText(str(stats["inativos"]))
        self.stat_expirados._lbl_valor.setText(str(stats["expirados"]))
    
    def _registrar_serial(self):
        """Registra um novo serial."""
        chave = self.reg_chave.text().strip().upper()
        cliente = self.reg_cliente.text().strip()
        empresa = self.reg_empresa.text().strip()
        contato = self.reg_contato.text().strip()
        maquina = self.reg_maquina.text().strip()
        validade = self.reg_validade.date().toPython()
        obs = self.reg_obs.toPlainText().strip()
        
        if not chave or not cliente:
            QMessageBox.warning(self, "Aviso", "Chave e Cliente são obrigatórios.")
            return
        
        try:
            self.service.registrar(
                chave=chave,
                cliente_nome=cliente,
                cliente_empresa=empresa,
                cliente_contato=contato,
                maquina_id=maquina or obter_maquina_id(),
                data_validade=validade,
                observacoes=obs,
            )
            QMessageBox.information(self, "Sucesso", f"Serial {chave} registrado com sucesso!")
            self._limpar_formulario()
            self._atualizar_tabela()
            self._atualizar_estatisticas()
        except ValueError as e:
            QMessageBox.critical(self, "Erro", str(e))
    
    def _limpar_formulario(self):
        """Limpa o formulário de registro."""
        self.reg_chave.clear()
        self.reg_cliente.clear()
        self.reg_empresa.clear()
        self.reg_contato.clear()
        self.reg_maquina.clear()
        self.reg_validade.setDate(QDate.currentDate().addYears(1))
        self.reg_obs.clear()
    
    def _gerar_chave(self):
        """Gera uma nova chave."""
        validade = self.gerar_validade.date().toPython()
        maquina = self.gerar_maquina.text().strip().upper() or obter_maquina_id()
        
        chave = gerar_chave(validade, maquina)
        self.resultado_chave.setText(chave)
        self.statusBar().showMessage(f"Chave gerada: {chave}")
    
    def _copiar_chave(self):
        """Copia a chave gerada para a área de transferência."""
        chave = self.resultado_chave.text()
        if chave:
            QApplication.clipboard().setText(chave)
            self.statusBar().showMessage("Chave copiada!")
    
    def _registrar_chave_gerada(self):
        """Vai para aba de registro com a chave gerada preenchida."""
        chave = self.resultado_chave.text()
        if chave:
            self.reg_chave.setText(chave)
            self.statusBar().showMessage("Chave preenchida no formulário de registro.")
    
    def _toggle_status(self, serial_id: int, status_atual: str):
        """Alterna o status do serial."""
        novo_status = "Inativo" if status_atual == "Ativo" else "Ativo"
        if self.service.atualizar_status(serial_id, novo_status):
            self._atualizar_tabela()
            self._atualizar_estatisticas()
            self.statusBar().showMessage(f"Status alterado para {novo_status}")
    
    def _excluir_selecionado(self):
        """Exclui o serial selecionado na tabela."""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um serial na tabela.")
            return
        
        serial_id = int(self.tabela.item(row, 0).text())
        chave = self.tabela.item(row, 1).text()
        self._excluir_serial(serial_id, chave)
    
    def _excluir_serial(self, serial_id: int, chave: str):
        """Exclui um serial."""
        resp = QMessageBox.question(
            self, "Confirmar",
            f"Tem certeza que deseja excluir o serial {chave}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            self.service.excluir(serial_id)
            self._atualizar_tabela()
            self._atualizar_estatisticas()
            self.statusBar().showMessage(f"Serial {chave} excluído")


# ==========================================
# MAIN
# ==========================================

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(ESTILO)
    
    window = GerenciadorSeriaisGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
