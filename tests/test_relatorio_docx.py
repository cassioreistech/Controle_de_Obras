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


class TestRelatorioDocx:
    """Testes para geração de relatório DOCX."""

    @pytest.fixture
    def servicos(self):
        """Configura os serviços para os testes."""
        db = DatabaseManager()
        storage = AppStorage()
        
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

    def test_gerar_docx_obra_2(self, docx_service, tmp_path):
        """Gera DOCX da obra 2 e verifica que o arquivo existe."""
        docx_service._storage._relatorios_dir = tmp_path
        
        filepath = docx_service.gerar_relatorio_obra_docx(2)
        
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
                docx_service.gerar_relatorio_obra_docx(2)
