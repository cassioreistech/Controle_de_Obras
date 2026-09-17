"""Testes de regressão: edição da empresa não apaga o logo_path existente."""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QMessageBox

from controle_obras.application.services import EmpresaService
from controle_obras.domain.models import Empresa
from controle_obras.infrastructure.database import DatabaseManager
from controle_obras.infrastructure.repositories import EmpresaRepository
from controle_obras.infrastructure.storage import AppStorage
from controle_obras.ui.empresa_screen import EmpresaScreen


class _ParentFake:
    """Substituto do AppContainer usado apenas por EmpresaScreen."""

    def __init__(self, empresa_service: EmpresaService) -> None:
        self.empresa_service = empresa_service
        self.voltou_para_obras = False

    def show_obras_list(self) -> None:
        self.voltou_para_obras = True


@pytest.fixture
def empresa_service(tmp_path: Path) -> EmpresaService:
    storage = AppStorage(tmp_path)
    db = DatabaseManager(storage.db_path())
    db.init_schema()
    return EmpresaService(EmpresaRepository(db))


def _montar_tela(qtbot, monkeypatch, empresa_service: EmpresaService) -> tuple[EmpresaScreen, _ParentFake]:
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    parent = _ParentFake(empresa_service)
    screen = EmpresaScreen(parent)
    qtbot.addWidget(screen)
    return screen, parent


def test_edicao_preserva_logo_existente(qtbot, monkeypatch, empresa_service: EmpresaService) -> None:
    empresa_service.salvar(
        Empresa(
            razao_social="Construtora Teste",
            nome_fantasia="Teste",
            logo_path="storage/logos/minha_logo.png",
        )
    )

    screen, parent = _montar_tela(qtbot, monkeypatch, empresa_service)
    screen.carregar()
    screen.input_razao.setText("Construtora Teste Editada")
    screen._salvar()

    salva = empresa_service.obter()
    assert salva is not None
    assert salva.razao_social == "Construtora Teste Editada"
    assert salva.logo_path == "storage/logos/minha_logo.png"
    assert parent.voltou_para_obras


def test_edicao_sem_logo_continua_sem_logo(qtbot, monkeypatch, empresa_service: EmpresaService) -> None:
    empresa_service.salvar(Empresa(razao_social="Construtora Sem Logo"))

    screen, _ = _montar_tela(qtbot, monkeypatch, empresa_service)
    screen.carregar()
    screen._salvar()

    salva = empresa_service.obter()
    assert salva is not None
    assert salva.logo_path == ""


def test_primeiro_cadastro_salva_sem_logo(qtbot, monkeypatch, empresa_service: EmpresaService) -> None:
    screen, parent = _montar_tela(qtbot, monkeypatch, empresa_service)
    screen.carregar()
    screen.input_razao.setText("Nova Construtora")
    screen._salvar()

    salva = empresa_service.obter()
    assert salva is not None
    assert salva.razao_social == "Nova Construtora"
    assert salva.logo_path == ""
    assert parent.voltou_para_obras
