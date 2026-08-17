"""Ponto de entrada da aplicação Controle de Obras."""

import logging
import sys
import traceback
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from controle_obras.ui.app_container import AppContainer


def _configurar_logging() -> Path:
    log_dir = Path("data")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    logging.basicConfig(
        filename=str(log_file),
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        filemode="a",
    )
    return log_file


def main() -> None:
    log_file = _configurar_logging()
    logger = logging.getLogger(__name__)
    logger.info("Iniciando aplicacao Controle de Obras")

    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        logger.info("QApplication criado")

        window = AppContainer()
        logger.info("AppContainer criado")

        window.show()
        logger.info("Janela exibida")

        sys.exit(app.exec())
    except Exception as exc:
        logger.exception("Erro fatal na inicializacao da aplicacao")
        mensagem = (
            f"Ocorreu um erro fatal ao iniciar o sistema:\n\n{exc}\n\n"
            f"Detalhes salvos em: {log_file}\n\n"
            f"{traceback.format_exc()}"
        )
        try:
            QMessageBox.critical(None, "Erro Fatal", mensagem)
        except Exception:
            print(mensagem, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
