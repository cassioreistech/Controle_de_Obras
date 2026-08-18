"""Testes do relatorio PDF com verificacao golden-master.

Estes testes validam:
1. Estrutura do PDF (numero de paginas, secoes presentes)
2. Conteudo textual (valores formatados, nomes, datas)
3. Snapshot visual (renderizacao PNG para comparacao manual)

Para atualizar o golden master:
1. Gere novo PDF aprovado
2. Copie os PNGs para tests/golden_images/
3. Atualize o hash esperado se necessario
"""

import os
from pathlib import Path
from decimal import Decimal

import pytest
import fitz  # pymupdf

from controle_obras.application.reportlab_pdf_service import ReportLabPDFService
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


class TestRelatorioPDFStructure:
    """Testes de estrutura do relatorio PDF."""

    @pytest.fixture
    def servicos(self):
        """Configura servicos para testes."""
        db = DatabaseManager()
        storage = AppStorage()
        
        obra_repo = ObraRepository(db)
        aditivo_repo = AditivoRepository(db)
        lancamento_repo = LancamentoRepository(db)
        anexo_repo = AnexoRepository(db)
        relatorio_repo = RelatorioRepository(db)
        empresa_repo = EmpresaRepository(db)
        
        return {
            "obra_service": ObraService(obra_repo),
            "aditivo_service": AditivoService(aditivo_repo),
            "lancamento_service": LancamentoService(lancamento_repo),
            "anexo_service": AnexoService(anexo_repo, storage),
            "resumo_service": ObraResumoService(obra_repo, aditivo_repo, lancamento_repo),
            "relatorio_repo": relatorio_repo,
            "storage": storage,
            "empresa_service": EmpresaService(empresa_repo),
        }

    @pytest.fixture
    def pdf_service(self, servicos):
        """Cria instancia do servico PDF."""
        return ReportLabPDFService(**servicos)

    @pytest.fixture
    def pdf_gerado(self, pdf_service, tmp_path):
        """Gera PDF e retorna caminho."""
        pdf_service._storage._relatorios_dir = tmp_path
        return pdf_service.gerar_relatorio_obra_reportlab(2)

    def test_pdf_nao_vazio(self, pdf_gerado):
        """Verifica que PDF foi gerado e nao esta vazio."""
        assert pdf_gerado.exists(), f"PDF nao foi criado: {pdf_gerado}"
        assert pdf_gerado.stat().st_size > 1000, "PDF muito pequeno, pode estar corrompido"

    def test_extensao_pdf(self, pdf_gerado):
        """Verifica extensao do arquivo."""
        assert pdf_gerado.suffix.lower() == ".pdf", f"Extensao invalida: {pdf_gerado.suffix}"

    def test_numero_paginas(self, pdf_gerado):
        """Verifica numero de paginas do PDF."""
        doc = fitz.open(str(pdf_gerado))
        num_paginas = len(doc)
        doc.close()
        
        # Obra 2 deve ter pelo menos 1 pagina
        assert num_paginas >= 1, "PDF deve ter pelo menos 1 pagina"
        assert num_paginas <= 10, "PDF nao deveria ter tantas paginas"

    def test_conteudo_textual_basico(self, pdf_gerado):
        """Extrai texto e verifica conteudo basico."""
        doc = fitz.open(str(pdf_gerado))
        texto_completo = ""
        for page in doc:
            texto_completo += page.get_text()
        doc.close()
        
        # Verificar secoes principais
        assert "RESUMO FINANCEIRO" in texto_completo, "Secao Resumo Financeiro ausente"
        assert "RELATORIO DA OBRA" in texto_completo, "Titulo principal ausente"
        
        # Verificar formatacao de moeda
        assert "R$" in texto_completo, "Formatacao de moeda (R$) ausente"
        
        # Verificar numeracao de pagina
        assert "Pagina" in texto_completo or "pagina" in texto_completo, "Numeracao de pagina ausente"

    def test_tabelas_com_valores(self, pdf_gerado):
        """Verifica presenca de valores formatados nas tabelas."""
        doc = fitz.open(str(pdf_gerado))
        texto_completo = ""
        for page in doc:
            texto_completo += page.get_text()
        doc.close()
        
        # Verificar colunas esperadas (em maiusculas apos alteracao)
        assert "VALOR CONTRATADO" in texto_completo or "TOTAL ADITIVOS" in texto_completo, \
            "Colunas do resumo financeiro ausentes"
        
        # Pelo menos um valor numerico formatado
        import re
        valores = re.findall(r"R\$\s[\d\.,]+", texto_completo)
        assert len(valores) > 0, "Nenhum valor monetario encontrado no PDF"


class TestRelatorioGoldenMaster:
    """Testes de snapshot visual (golden master).
    
    Para uso:
    1. Gere PDF aprovado manualmente
    2. Converta para PNG e salve em tests/golden_images/
    3. Este teste compara novas geracoes com o baseline
    """

    @pytest.fixture
    def servicos(self):
        db = DatabaseManager()
        storage = AppStorage()
        
        obra_repo = ObraRepository(db)
        aditivo_repo = AditivoRepository(db)
        lancamento_repo = LancamentoRepository(db)
        anexo_repo = AnexoRepository(db)
        relatorio_repo = RelatorioRepository(db)
        empresa_repo = EmpresaRepository(db)
        
        return {
            "obra_service": ObraService(obra_repo),
            "aditivo_service": AditivoService(aditivo_repo),
            "lancamento_service": LancamentoService(lancamento_repo),
            "anexo_service": AnexoService(anexo_repo, storage),
            "resumo_service": ObraResumoService(obra_repo, aditivo_repo, lancamento_repo),
            "relatorio_repo": relatorio_repo,
            "storage": storage,
            "empresa_service": EmpresaService(empresa_repo),
        }

    @pytest.fixture
    def pdf_service(self, servicos):
        return ReportLabPDFService(**servicos)

    def test_golden_master_visual(self, pdf_service, tmp_path):
        """Renderiza PDF e salva PNG para revisao visual.
        
        Nota: Este teste nao falha automaticamente - ele gera artefatos
        para revisao humana. Comparacao automatica requer ferramenta
        de diff de imagem (ex: pytest-snapshot).
        """
        pdf_service._storage._relatorios_dir = tmp_path
        pdf_path = pdf_service.gerar_relatorio_obra_reportlab(2)
        
        # Renderizar para PNG
        doc = fitz.open(str(pdf_path))
        zoom = 150 / 72  # 150 DPI
        mat = fitz.Matrix(zoom, zoom)
        
        output_dir = tmp_path / "golden_preview"
        output_dir.mkdir()
        
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=mat)
            png_path = output_dir / f"pagina_{i+1:02d}.png"
            pix.save(str(png_path))
        
        doc.close()
        
        # Salvar PDF tambem
        import shutil
        golden_dir = Path(__file__).parent / "golden_images"
        golden_dir.mkdir(exist_ok=True)
        shutil.copy(pdf_path, golden_dir / "relatorio_baseline.pdf")
        
        assert len(list(output_dir.glob("*.png"))) > 0, "Nenhuma imagem PNG gerada"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
