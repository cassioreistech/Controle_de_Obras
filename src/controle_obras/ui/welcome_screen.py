"""Tela de boas-vindas inicial."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from controle_obras.ui.app_container import AppContainer


class WelcomeScreen(QWidget):
    """Tela de boas-vindas apresentada no primeiro uso."""

    def __init__(self, parent: AppContainer) -> None:
        super().__init__()
        self._parent = parent
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Bem-vindo ao Controle de Obras")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Sistema de gestão financeira e documental para obras")
        subtitle.setStyleSheet("font-size: 16px; color: #7f8c8d; margin: 16px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_iniciar = QPushButton("Iniciar Configuração")
        btn_iniciar.setStyleSheet(
            "padding: 12px 32px; font-size: 16px; background-color: #27ae60; color: white;"
        )
        btn_iniciar.clicked.connect(self._iniciar)
        btn_layout.addWidget(btn_iniciar)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def _iniciar(self) -> None:
        self._parent.show_empresa()
