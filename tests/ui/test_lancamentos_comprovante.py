"""Testes de regressão: origem 'Comprovante Pagamento' nos lançamentos.

A origem 'Comprovante Pagamento' deve se comportar como 'Nota Fiscal':
exigir anexo, aceitar PDF/JPG e salvar o arquivo no mesmo formato.
"""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QMessageBox

import controle_obras.ui.lancamentos_screen as lanc_screen
from controle_obras.application.services import (
    AnexoService,
    LancamentoService,
    ObraService,
    TipoLancamentoService,
)
from controle_obras.domain.models import Obra
from controle_obras.infrastructure.database import DatabaseManager
from controle_obras.infrastructure.repositories import (
    AnexoRepository,
    LancamentoRepository,
    ObraRepository,
    TipoLancamentoRepository,
)
from controle_obras.infrastructure.storage import AppStorage
from controle_obras.ui.lancamentos_screen import (
    ORIGENS_COM_ANEXO_OBRIGATORIO,
    LancamentosScreen,
)


class _ParentFake:
    """Substituto mínimo do AppContainer para a tela de lançamentos."""

    def __init__(self, storage, obra_service, lancamento_service, anexo_service, tipo_service):
        self.storage = storage
        self.obra_service = obra_service
        self.lancamento_service = lancamento_service
        self.anexo_service = anexo_service
        self.tipo_lancamento_service = tipo_service


@pytest.fixture
def ambiente(tmp_path: Path) -> tuple[LancamentosScreen, _ParentFake, Obra]:
    storage = AppStorage(tmp_path)
    db = DatabaseManager(storage.db_path())
    db.init_schema()

    obra_service = ObraService(ObraRepository(db))
    lancamento_service = LancamentoService(LancamentoRepository(db))
    anexo_service = AnexoService(AnexoRepository(db), storage)
    tipo_service = TipoLancamentoService(TipoLancamentoRepository(db))

    parent = _ParentFake(storage, obra_service, lancamento_service, anexo_service, tipo_service)
    obra = obra_service.salvar(Obra(codigo="TESTE-01", nome="Obra Teste"))
    screen = LancamentosScreen(parent)
    screen.carregar(obra.id)
    return screen, parent, obra


def test_origem_comprovante_pagamento_existe_e_exige_anexo(qtbot, ambiente) -> None:
    screen, _, _ = ambiente
    qtbot.addWidget(screen)

    origens = [screen.input_origem.itemText(i) for i in range(screen.input_origem.count())]
    assert "Comprovante Pagamento" in origens
    assert "Comprovante Pagamento" in ORIGENS_COM_ANEXO_OBRIGATORIO


def test_filtro_dialogo_aceita_pdf_e_jpg(qtbot, ambiente, monkeypatch) -> None:
    screen, _, _ = ambiente
    qtbot.addWidget(screen)

    capturado: dict[str, str] = {}

    def _fake_dialog(parent, title, directory, filtro, *args, **kwargs):
        capturado["filtro"] = filtro
        return ("", "")

    monkeypatch.setattr(lanc_screen.QFileDialog, "getOpenFileName", _fake_dialog)

    screen._selecionar_arquivo_anexo("Comprovante Pagamento")
    assert "*.pdf" in capturado["filtro"]
    assert "*.jpg" in capturado["filtro"]

    # Não deve alterar o filtro da Nota Fiscal
    screen._selecionar_arquivo_anexo("Nota Fiscal")
    assert "*.xlsx" in capturado["filtro"]


def test_salvar_comprovante_grava_anexo_como_nota_fiscal(
    qtbot, ambiente, tmp_path: Path, monkeypatch
) -> None:
    screen, parent, obra = ambiente
    qtbot.addWidget(screen)
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a, **k: None)

    jpg = tmp_path / "comprovante.jpg"
    jpg.write_bytes(b"\xff\xd8\xff\xe0conteudo-jpg")

    screen.input_origem.blockSignals(True)
    screen.input_origem.setCurrentText("Comprovante Pagamento")
    screen.input_origem.blockSignals(False)
    screen._arquivo_anexo = jpg
    screen.input_descricao.setText("Pagamento fornecedor X")
    screen.input_valor_total.setText("150,00")

    screen._salvar()

    lancamentos = parent.lancamento_service.listar_por_obra(obra.id)
    assert len(lancamentos) == 1
    lanc = lancamentos[0]
    assert lanc.origem_informacao == "Comprovante Pagamento"

    anexos = parent.anexo_service.listar_por_lancamento(lanc.id)
    assert len(anexos) == 1
    assert anexos[0].tipo_anexo == "Comprovante Pagamento"
    assert anexos[0].nome_original == "comprovante.jpg"

    caminho = parent.storage.anexo_path(obra.codigo, anexos[0].caminho_relativo)
    assert caminho.exists()
