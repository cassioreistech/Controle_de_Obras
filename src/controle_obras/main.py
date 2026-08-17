"""Ponto de entrada da aplicação Controle de Obras."""

import sys

from PySide6.QtWidgets import QApplication

from controle_obras.ui.app_container import AppContainer


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AppContainer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
