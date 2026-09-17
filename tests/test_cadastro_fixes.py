"""Testes de regressão das correções na estrutura de cadastro.

Cobre os bugs 1-6, 9 e 10 da auditoria:
- parse de valores monetários (milhar BR, ponto decimal, inválido, negativo) [1, 2]
- AnexoService.excluir com remoção de arquivo físico [4]
- exclusão de obra limpa anexos físicos [4]
- TipoLancamentoService.obter (tipos inativos) [6]
"""

from decimal import Decimal

import pytest

from controle_obras.application.services import AnexoService, ObraService, TipoLancamentoService
from controle_obras.domain.models import Obra
from controle_obras.infrastructure.database import DatabaseManager
from controle_obras.infrastructure.repositories import (
    AnexoRepository,
    ObraRepository,
    TipoLancamentoRepository,
)
from controle_obras.infrastructure.storage import AppStorage
from controle_obras.ui.value_utils import formatar_valor, parse_valor


class TestParseValor:
    """Bug 1+2: parser robusto para valores monetários."""

    def test_milhar_brasileiro_sem_virgula(self):
        assert parse_valor("1.000") == Decimal("1000")
        assert parse_valor("1.234.567") == Decimal("1234567")
        assert parse_valor("1500000") == Decimal("1500000")

    def test_ponto_decimal_python(self):
        assert parse_valor("1234.56") == Decimal("1234.56")
        assert parse_valor("0.00") == Decimal("0.00")

    def test_virgula_brasileira(self):
        assert parse_valor("1.000,00") == Decimal("1000.00")
        assert parse_valor("12,5") == Decimal("12.50")

    def test_com_r_dolar(self):
        assert parse_valor("R$ 1.234,56") == Decimal("1234.56")

    def test_vazio_ou_zero(self):
        assert parse_valor("") == Decimal("0.00")
        assert parse_valor("0") == Decimal("0.00")
        assert parse_valor("0,00") == Decimal("0.00")

    def test_invalido_retorna_none(self):
        assert parse_valor("abc") is None
        assert parse_valor("-100") is None
        assert parse_valor("-1.000,00") is None
        assert parse_valor("..") is None
        assert parse_valor("12.3.4") is None

    def test_formatar_valor_br(self):
        assert formatar_valor(Decimal("1234.5")) == "1.234,50"
        assert formatar_valor(Decimal("1000000")) == "1.000.000,00"
        assert formatar_valor(Decimal("0")) == "0,00"
        assert formatar_valor(Decimal("-1234.5")) == "-1.234,50"


class TestExclusaoAnexos:
    """Bug 4: excluir anexo remove arquivo físico; excluir obra limpa anexos."""

    @pytest.fixture
    def ambiente(self, tmp_path):
        db = DatabaseManager(tmp_path / "test.db")
        db.init_schema()
        storage = AppStorage(tmp_path)
        services = {
            "obra_service": ObraService(ObraRepository(db)),
            "anexo_service": AnexoService(AnexoRepository(db), storage),
            "storage": storage,
        }
        return services

    @staticmethod
    def _criar_obra(services):
        return services["obra_service"].salvar(Obra(codigo="O1", nome="Obra Teste"))

    @staticmethod
    def _anexar(services, obra, origem):
        return services["anexo_service"].anexar_arquivo(
            obra_codigo=obra.codigo,
            arquivo_origem=origem,
            tipo_anexo="Nota Fiscal",
            obra_id=obra.id,
        )

    def test_excluir_anexo_remove_arquivo_fisico(self, ambiente, tmp_path):
        obra = self._criar_obra(ambiente)
        origem = tmp_path / "nf.pdf"
        origem.write_bytes(b"dados")
        anexo = self._anexar(ambiente, obra, origem)

        caminho_arquivo = ambiente["storage"].anexo_path(obra.codigo, anexo.caminho_relativo)
        assert caminho_arquivo.exists()

        ambiente["anexo_service"].excluir(anexo.id, obra.codigo)
        assert not caminho_arquivo.exists()

    def test_excluir_obra_remove_arquivos_de_anexos(self, ambiente, tmp_path):
        obra = self._criar_obra(ambiente)
        origem = tmp_path / "planilha.xlsx"
        origem.write_bytes(b"planilha")
        anexo = self._anexar(ambiente, obra, origem)

        caminho_arquivo = ambiente["storage"].anexo_path(obra.codigo, anexo.caminho_relativo)
        assert caminho_arquivo.exists()

        for a in ambiente["anexo_service"].listar_por_obra(obra.id):
            ambiente["anexo_service"].excluir(a.id, obra.codigo)
        ambiente["obra_service"].excluir(obra.id)

        assert not caminho_arquivo.exists()
        assert ambiente["obra_service"].obter(obra.id) is None

    def test_excluir_anexo_sem_codigo_nao_quebra(self, ambiente, tmp_path):
        obra = self._criar_obra(ambiente)
        origem = tmp_path / "doc.txt"
        origem.write_bytes(b"x")
        anexo = self._anexar(ambiente, obra, origem)
        ambiente["anexo_service"].excluir(anexo.id)
        assert ambiente["anexo_service"].obter(anexo.id) is None


class TestTipoLancamentoObter:
    """Bug 6: obter tipo mesmo desativado (fallback na edição)."""

    @pytest.fixture
    def servico(self, tmp_path):
        db = DatabaseManager(tmp_path / "test.db")
        db.init_schema()
        db.execute(
            "INSERT INTO tipos_lancamento (nome, ativo, ordem_exibicao) VALUES (?, ?, ?)",
            ("Servico antigo", 0, 99),
        )
        tipo_id = db.execute(
            "SELECT id FROM tipos_lancamento WHERE nome=?", ("Servico antigo",)
        ).fetchone()["id"]
        return TipoLancamentoService(TipoLancamentoRepository(db)), tipo_id

    def test_obter_tipo_inativo(self, servico):
        tipo_service, tipo_id = servico
        tipo = tipo_service.obter(tipo_id)
        assert tipo is not None
        assert tipo.nome == "Servico antigo"
        assert tipo.ativo is False

    def test_listar_ativos_exclui_inativo(self, servico):
        tipo_service, _ = servico
        assert all(t.nome != "Servico antigo" for t in tipo_service.listar_ativos())

    def test_obter_tipo_inexistente_retorna_none(self, servico):
        tipo_service, _ = servico
        assert tipo_service.obter(99999) is None
