"""Ponto de entrada da aplicação Controle de Obras."""

import logging
import sys
import traceback
from pathlib import Path

from PySide6.QtCore import QLockFile
from PySide6.QtWidgets import QApplication, QMessageBox

from controle_obras.infrastructure.storage import AppStorage
from controle_obras.ui.app_container import AppContainer


def _configurar_logging() -> Path:
    log_dir = AppStorage().data_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    logging.basicConfig(
        filename=str(log_file),
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        filemode="a",
    )
    return log_file


def _adquirir_lock(data_dir: Path) -> QLockFile | None:
    """Adquire lock de instância única. Retorna None se já estiver rodando."""
    lock = QLockFile(str(data_dir / "app.lock"))
    lock.setStaleLockTime(0)  # Nunca expira: detecta processo morto
    if lock.tryLock(100):
        return lock
    return None


def main() -> None:
    log_file = _configurar_logging()
    logger = logging.getLogger(__name__)
    logger.info("Iniciando aplicacao Controle de Obras")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    storage = AppStorage()
    lock = _adquirir_lock(storage.data_dir)
    if lock is None:
        QMessageBox.information(
            None,
            "Controle de Obras",
            "O Controle de Obras já está em execução.\n\n"
            "Feche a janela aberta e tente novamente.",
        )
        sys.exit(0)

    try:
        window = AppContainer()
        if not window.verificar_licenca():
            logger.info("Acesso negado pela verificacao de licenca")
            sys.exit(0)

        window.showMaximized()
        logger.info("Janela exibida")

        app.exec()
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
    finally:
        lock.unlock()


if __name__ == "__main__":
    main()
