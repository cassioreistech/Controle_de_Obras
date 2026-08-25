"""Validacao visual das telas PySide6.

Renderiza cada tela offscreen, salva screenshot PNG em tests/screenshots/
e valida que a renderizacao e valida (nao-branca, dimensoes esperadas).

Uso: python -m pytest tests/ui/test_visual_screens.py -v
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage

from controle_obras.domain.models import Aditivo, Empresa, Lancamento, Obra
from controle_obras.ui.app_container import AppContainer

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@pytest.fixture(scope="module")
def screenshots_dir():
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    return SCREENSHOT_DIR


def _salvar_screenshot(widget, nome: str, diretorio: Path) -> Path:
    """Renderiza um widget e salva como PNG. Retorna o caminho."""
    widget.show()
    widget.resize(1200, 800)
    widget.repaint()
    pixmap = widget.grab()
    caminho = diretorio / f"{nome}.png"
    assert pixmap.save(str(caminho)), f"Falha ao salvar screenshot {nome}"
    return caminho


def _validar_screenshot(caminho: Path, nome: str) -> None:
    """Valida que o PNG nao e vazio/em branco e tem tamanho esperado."""
    assert caminho.exists(), f"Screenshot nao gerado: {nome}"
    assert caminho.stat().st_size > 500, f"Screenshot muito pequeno: {nome}"

    imagem = QImage(str(caminho))
    assert not imagem.isNull(), f"Imagem invalida: {nome}"
    assert imagem.width() >= 800, f"Largura insuficiente em {nome}: {imagem.width()}"
    assert imagem.height() >= 400, f"Altura insuficiente em {nome}: {imagem.height()}"

    # Detecta tela em branco contando cores unicas:
    # uma tela vazia tem ~1 cor; uma UI renderizada tem dezenas (texto, cards, sombras)
    cores = set()
    step = 8  # amostragem a cada 8px para performance
    for x in range(0, imagem.width(), step):
        for y in range(0, imagem.height(), step):
            cor = imagem.pixelColor(x, y)
            cores.add((cor.red(), cor.green(), cor.blue()))
    assert len(cores) >= 5, f"Screenshot aparentemente em branco: {nome} ({len(cores)} cores)"


@pytest.fixture
def app_com_dados(qtbot, tmp_path: Path, monkeypatch):
    """AppContainer com dados de exemplo populados."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CONTROLE_OBRAS_DATA_DIR", str(tmp_path))

    container = AppContainer()
    qtbot.addWidget(container)

    # Seed: empresa + obra + aditivo + lancamento
    container.empresa_service.salvar(
        Empresa(
            razao_social="Construtora Teste LTDA",
            cnpj="12.345.678/0001-90",
            responsavel="Carlos Alberto",
        )
    )
    obra = container.obra_service.salvar(
        Obra(
            codigo="OBRA-001",
            nome="Edificio Residencial Sol",
            cliente_contratante="Joao da Silva",
            local_obra="Sao Paulo - SP",
            data_inicio=date(2024, 1, 15),
            previsao_termino=date(2024, 12, 31),
            valor_contratado_inicial=Decimal("500000.00"),
        )
    )
    container.aditivo_service.salvar(
        Aditivo(
            obra_id=obra.id,
            descricao="Acrescimo de vagas",
            valor=Decimal("75000.00"),
        )
    )
    container.lancamento_service.salvar(
        Lancamento(
            obra_id=obra.id,
            descricao="Cimento CP-II 50kg",
            valor_total=Decimal("4500.00"),
        )
    )
    container.config_service.definir_obra_ativa(obra.id)

    return container


class TestVisualScreens:
    """Renderiza e valida cada tela principal."""

    def test_welcome_screen(self, app_com_dados, screenshots_dir):
        screen = app_com_dados.welcome_screen
        path = _salvar_screenshot(screen, "01_welcome", screenshots_dir)
        _validar_screenshot(path, "01_welcome")

    def test_empresa_screen(self, app_com_dados, screenshots_dir):
        screen = app_com_dados.empresa_screen
        screen.carregar()
        path = _salvar_screenshot(screen, "02_empresa", screenshots_dir)
        _validar_screenshot(path, "02_empresa")

    def test_obras_list_screen(self, app_com_dados, screenshots_dir):
        screen = app_com_dados.obras_list_screen
        screen.carregar()
        path = _salvar_screenshot(screen, "03_obras_lista", screenshots_dir)
        _validar_screenshot(path, "03_obras_lista")

    def test_obra_form_screen(self, app_com_dados, screenshots_dir):
        screen = app_com_dados.obra_form_screen
        screen.carregar()
        path = _salvar_screenshot(screen, "04_obra_form", screenshots_dir)
        _validar_screenshot(path, "04_obra_form")

    def test_dashboard_screen(self, app_com_dados, screenshots_dir):
        screen = app_com_dados.dashboard_screen
        screen.carregar(1)
        path = _salvar_screenshot(screen, "05_dashboard", screenshots_dir)
        _validar_screenshot(path, "05_dashboard")

    def test_lancamentos_screen(self, app_com_dados, screenshots_dir):
        screen = app_com_dados.lancamentos_screen
        screen.carregar(1)
        path = _salvar_screenshot(screen, "06_lancamentos", screenshots_dir)
        _validar_screenshot(path, "06_lancamentos")

    def test_anexos_screen(self, app_com_dados, screenshots_dir):
        screen = app_com_dados.anexos_screen
        screen.carregar(1)
        path = _salvar_screenshot(screen, "07_anexos", screenshots_dir)
        _validar_screenshot(path, "07_anexos")