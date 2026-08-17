"""Smoke tests para as telas PySide6."""

from pathlib import Path

import pytest

from controle_obras.ui.anexos_screen import AnexosScreen
from controle_obras.ui.app_container import AppContainer
from controle_obras.ui.dashboard_screen import DashboardScreen
from controle_obras.ui.empresa_screen import EmpresaScreen
from controle_obras.ui.lancamentos_screen import LancamentosScreen
from controle_obras.ui.obra_form_screen import ObraFormScreen
from controle_obras.ui.obras_list_screen import ObrasListScreen
from controle_obras.ui.welcome_screen import WelcomeScreen


@pytest.fixture
def app_container(qtbot, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    container = AppContainer()
    qtbot.addWidget(container)
    return container


def test_app_container_inicializa(app_container):
    assert app_container.windowTitle() == "Controle de Obras"
    assert app_container.stack.count() == 7


def test_welcome_screen(app_container):
    screen = WelcomeScreen(app_container)
    assert screen is not None


def test_empresa_screen(app_container):
    screen = EmpresaScreen(app_container)
    screen.carregar()
    assert screen is not None


def test_obras_list_screen(app_container):
    screen = ObrasListScreen(app_container)
    screen.carregar()
    assert screen is not None


def test_obra_form_screen(app_container):
    screen = ObraFormScreen(app_container)
    screen.carregar()
    assert screen is not None


def test_dashboard_screen(app_container):
    screen = DashboardScreen(app_container)
    assert screen is not None


def test_lancamentos_screen(app_container):
    screen = LancamentosScreen(app_container)
    screen.carregar(1)
    assert screen is not None


def test_anexos_screen(app_container):
    screen = AnexosScreen(app_container)
    screen.carregar(1)
    assert screen is not None
