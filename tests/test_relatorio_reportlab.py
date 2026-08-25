"""Testes para o gerador de relatório PDF com ReportLab."""

from decimal import Decimal
from pathlib import Path

import pytest

from controle_obras.application.reportlab_pdf_service import ReportLabPDFService
from controle_obras.domain.models import Aditivo, Empresa, Lancamento, Obra
from controle_obras.infrastructure.database import DatabaseManager
from controle_obras.infrastructure.repositories import (
    AditivoRepository,
    AnexoRepository,
    EmpresaRepository,
    LancamentoRepository,
    ObraRepository,
    RelatorioRepository,
    TipoLancamentoRepository,
)
from controle_obras.infrastructure.storage import AppStorage
from controle_obras.application.services import (
    AditivoService,
    AnexoService,
    EmpresaService,
    LancamentoService,
    ObraResumoService,
    ObraService,
)


def _seed_obra(obra_service, aditivo_service, lancamento_service, empresa_service):
    """Cria empresa + obra de exemplo."""
    empresa_service.salvar(
        Empresa(
            razao_social="Construtora Teste LTDA",
            cnpj="12.345.678/0001-90",
            responsavel="Carlos Alberto",
        )
    )
    obra = obra_service.salvar(
        Obra(
            codigo="02",
            nome="Construcao de uma Ponte de 500 m",
            cliente_contratante="Prefeitura Municipal",
            valor_contratado_inicial=Decimal("1500000.00"),
        )
    )
    aditivo_service.salvar(
        Aditivo(
            obra_id=obra.id,
            descricao="Acrescimo de fundacoes",
            valor=Decimal("250000.00"),
        )
    )
    lancamento_service.salvar(
        Lancamento(
            obra_id=obra.id,
            descricao="Aco CA-50",
            valor_total=Decimal("45000.00"),
        )
    )
    return obra


class TestRelatorioReportLab:
    """Testes para geração de relatório com ReportLab."""

    @pytest.fixture
    def servicos(self, tmp_path):
        """Configura os serviços para os testes."""
        db = DatabaseManager(tmp_path / "test.db")
        db.init_schema()
        storage = AppStorage(tmp_path)

        obra_repo = ObraRepository(db)
        aditivo_repo = AditivoRepository(db)
        lancamento_repo = LancamentoRepository(db)
        anexo_repo = AnexoRepository(db)
        relatorio_repo = RelatorioRepository(db)
        empresa_repo = EmpresaRepository(db)
        tipo_repo = TipoLancamentoRepository(db)

        services = {
            "obra_service": ObraService(obra_repo),
            "aditivo_service": AditivoService(aditivo_repo),
            "lancamento_service": LancamentoService(lancamento_repo),
            "anexo_service": AnexoService(anexo_repo, storage),
            "resumo_service": ObraResumoService(obra_repo, aditivo_repo, lancamento_repo),
            "relatorio_repo": relatorio_repo,
            "storage": storage,
            "empresa_service": EmpresaService(empresa_repo),
        }

        self._obra = _seed_obra(
            services["obra_service"],
            services["aditivo_service"],
            services["lancamento_service"],
            services["empresa_service"],
        )
        return services

    @pytest.fixture
    def pdf_service(self, servicos):
        """Cria a instância do serviço ReportLab."""
        return ReportLabPDFService(
            obra_service=servicos["obra_service"],
            aditivo_service=servicos["aditivo_service"],
            lancamento_service=servicos["lancamento_service"],
            anexo_service=servicos["anexo_service"],
            resumo_service=servicos["resumo_service"],
            relatorio_repo=servicos["relatorio_repo"],
            storage=servicos["storage"],
            empresa_service=servicos["empresa_service"],
        )

    def test_gerar_relatorio_obra(self, pdf_service, tmp_path):
        """Gera relatório PDF da obra seedada e verifica que o arquivo existe."""
        pdf_service._storage._relatorios_dir = tmp_path
        filepath = pdf_service.gerar_relatorio_obra_reportlab(self._obra.id)

        assert filepath.exists(), f"Arquivo não foi criado: {filepath}"
        assert filepath.stat().st_size > 0, "Arquivo PDF está vazio"
        assert filepath.suffix.lower() == ".pdf", f"Extensão inválida: {filepath.suffix}"

    def test_obra_nao_existe(self, pdf_service):
        """Verifica que erro é lançado para obra inexistente."""
        with pytest.raises(ValueError, match="Obra .* não encontrada"):
            pdf_service.gerar_relatorio_obra_reportlab(99999)
