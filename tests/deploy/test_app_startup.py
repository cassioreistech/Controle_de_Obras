"""Smoke test de inicializacao (health check) do aplicativo.

Valida que o app inicia sem falhas criticas: logging, QApplication,
AppContainer e exibicao da janela principal.

Este e o "canary check" do app desktop: se qualquer tela quebrar na
inicializacao, este teste falha antes do usuario abrir o app.
"""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from controle_obras.ui.app_container import AppContainer


@pytest.fixture
def app_startup(qtbot, tmp_path: Path, monkeypatch):
    """Inicializa o app como no main.py (sem entrar no event loop)."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_app_inicializa_com_servicos(app_startup):
    """AppContainer cria todos os servicos e schema do banco."""
    container = AppContainer()

    assert container.empresa_service is not None
    assert container.obra_service is not None
    assert container.aditivo_service is not None
    assert container.lancamento_service is not None
    assert container.anexo_service is not None
    assert container.resumo_service is not None
    assert container.relatorio_service is not None
    assert container.db.db_path.exists()


def test_app_cria_todas_as_telas(app_startup):
    """AppContainer cria as 7 telas e as adiciona ao stack."""
    container = AppContainer()

    assert container.stack.count() == 7
    assert container.welcome_screen is not None
    assert container.empresa_screen is not None
    assert container.obras_list_screen is not None
    assert container.obra_form_screen is not None
    assert container.dashboard_screen is not None
    assert container.lancamentos_screen is not None
    assert container.anexos_screen is not None


def test_app_gera_logs_sem_erros(app_startup, tmp_path: Path):
    """O arquivo de log e criado na inicializacao apos a primeira mensagem."""
    import logging

    from controle_obras.main import _configurar_logging

    # pytest ja configura handlers no root logger, o que torna basicConfig no-op.
    # Removemos para simular a inicializacao real do app.
    root = logging.getLogger()
    handlers_antigos = list(root.handlers)
    for h in handlers_antigos:
        root.removeHandler(h)

    try:
        log_file = _configurar_logging()
        logging.getLogger("controle_obras.test").info("Teste de inicializacao")

        assert log_file.exists(), f"Log nao criado: {log_file}"
        assert log_file.suffix == ".log"
        conteudo = log_file.read_text(encoding="utf-8", errors="replace")
        assert "Teste de inicializacao" in conteudo
    finally:
        # Restaura handlers do pytest
        for h in handlers_antigos:
            root.addHandler(h)


def test_first_run_redireciona_para_welcome(app_startup):
    """Na primeira execucao, a tela inicial deve ser a Welcome."""
    container = AppContainer()

    # Sem empresa cadastrada, app redireciona para welcome (index 0)
    assert container.stack.currentIndex() == 0
    assert isinstance(container.stack.currentWidget(), type(container.welcome_screen))