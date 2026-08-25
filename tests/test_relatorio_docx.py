"""Testes para o gerador de relatório DOCX/PDF."""

import os
from pathlib import Path

import pytest

from controle_obras.application.docx_report_service import DocxReportService
from controle_obras.infrastructure.database import DatabaseManager
from controle_obras.infrastructure.repositories import (
    AditivoRepository,
    AnexoRepository,
    EmpresaRepository,
    LancamentoRepository,
    ObraRepository,
    RelatorioRepository,
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
from controle_obras.domain.models import Aditivo, Empresa, Lancamento, Obra
from decimal import Decimal


def _seed_obra(obra_service, aditivo_service, lancamento_service, empresa_service):
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
        Aditivo(obra_id=obra.id, descricao="Acrescimo de fundacoes", valor=Decimal("250000.00"))
    )
    lancamento_service.salvar(
        Lancamento(obra_id=obra.id, descricao="Aco CA-50", valor_total=Decimal("45000.00"))
    )
    return obra


class TestRelatorioDocx:
    """Testes para geração de relatório DOCX."""

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
        
        obra_service = ObraService(obra_repo)
        aditivo_service = AditivoService(aditivo_repo)
        lancamento_service = LancamentoService(lancamento_repo)
        anexo_service = AnexoService(anexo_repo, storage)
        resumo_service = ObraResumoService(obra_repo, aditivo_repo, lancamento_repo)
        empresa_service = EmpresaService(empresa_repo)
        
        self._obra = _seed_obra(
            obra_service, aditivo_service, lancamento_service, empresa_service
        )
        
        return {
            "obra_service": obra_service,
            "aditivo_service": aditivo_service,
            "lancamento_service": lancamento_service,
            "anexo_service": anexo_service,
            "resumo_service": resumo_service,
            "relatorio_repo": relatorio_repo,
            "storage": storage,
            "empresa_service": empresa_service,
        }

    @pytest.fixture
    def docx_service(self, servicos):
        """Cria a instância do serviço DOCX."""
        return DocxReportService(
            obra_service=servicos["obra_service"],
            aditivo_service=servicos["aditivo_service"],
            lancamento_service=servicos["lancamento_service"],
            anexo_service=servicos["anexo_service"],
            resumo_service=servicos["resumo_service"],
            relatorio_repo=servicos["relatorio_repo"],
            storage=servicos["storage"],
            empresa_service=servicos["empresa_service"],
        )

    def test_gerar_docx_obra(self, docx_service, tmp_path):
        """Gera DOCX da obra seedada e verifica que o arquivo existe."""
        docx_service._storage._relatorios_dir = tmp_path
        
        filepath = docx_service.gerar_relatorio_obra_docx(self._obra.id)
        
        assert filepath.exists(), f"Arquivo não foi criado: {filepath}"
        assert filepath.stat().st_size > 0, "Arquivo está vazio"
        assert filepath.suffix.lower() == ".pdf", f"Extensão inválida: {filepath.suffix}"
        
        print(f"\n[TESTE] PDF gerado: {filepath}")
        print(f"[TESTE] Tamanho: {filepath.stat().st_size} bytes")

    def test_libreoffice_nao_instalado(self, docx_service, tmp_path):
        """Verifica erro claro quando LibreOffice não está instalado."""
        docx_service._storage._relatorios_dir = tmp_path
        
        # Verificar se LibreOffice está instalado
        libreoffice_path = docx_service._obter_libreoffice_path()
        if not libreoffice_path:
            with pytest.raises(RuntimeError, match="LibreOffice"):
                docx_service.gerar_relatorio_obra_docx(self._obra.id)
