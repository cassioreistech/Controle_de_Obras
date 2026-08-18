"""Testes do relatorio PDF com verificacao golden-master.

Estes testes validam:
1. Estrutura do PDF (numero de paginas, secoes presentes)
2. Conteudo textual (valores formatados, nomes, datas)
3. Snapshot visual (renderizacao PNG para comparacao manual)

Nota: O teste usa banco temporario com dados seedados (nao depende do
banco real), tornando-o reproduzivel em CI.

A numeracao de pagina foi removida intencionalmente do rodape (para
corrigir bug de duplicacao de paginas), por isso nao e mais validada.
"""

import re
from decimal import Decimal
from pathlib import Path

import pytest
import fitz  # pymupdf

from controle_obras.application.reportlab_pdf_service import ReportLabPDFService
from controle_obras.application.services import (
    AditivoService,
    AnexoService,
    EmpresaService,
    LancamentoService,
    ObraResumoService,
    ObraService,
)
from controle_obras.domain.models import Aditivo, Empresa, Lancamento, Obra
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


def _seed_obra(obra_service, aditivo_service, lancamento_service, empresa_service):
    """Cria empresa + obra + aditivo + lancamento de exemplo."""
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


class TestRelatorioPDFStructure:
    """Testes de estrutura do relatorio PDF."""

    @pytest.fixture
    def servicos(self, tmp_path: Path, monkeypatch):
        """Configura servicos com banco temporario e saida em tmp_path."""
        # Redireciona Downloads (hardcoded no servico) para tmp_path
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        db = DatabaseManager(tmp_path / "test.db")
        db.init_schema()
        storage = AppStorage(tmp_path / "storage")

        obra_repo = ObraRepository(db)
        aditivo_repo = AditivoRepository(db)
        lancamento_repo = LancamentoRepository(db)
        anexo_repo = AnexoRepository(db)
        relatorio_repo = RelatorioRepository(db)
        empresa_repo = EmpresaRepository(db)

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

        _seed_obra(
            services["obra_service"],
            services["aditivo_service"],
            services["lancamento_service"],
            services["empresa_service"],
        )

        return services

    @pytest.fixture
    def pdf_service(self, servicos):
        """Cria instancia do servico PDF."""
        return ReportLabPDFService(**servicos)

    @pytest.fixture
    def pdf_gerado(self, pdf_service):
        """Gera PDF e retorna caminho."""
        return pdf_service.gerar_relatorio_obra_reportlab(1)

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

        # Verificar dados da obra seedada
        assert "Construcao de uma Ponte" in texto_completo, "Nome da obra ausente"

        # Verificar formatacao de moeda
        assert "R$" in texto_completo, "Formatacao de moeda (R$) ausente"

    def test_tabelas_com_valores(self, pdf_gerado):
        """Verifica presenca de valores formatados nas tabelas."""
        doc = fitz.open(str(pdf_gerado))
        texto_completo = ""
        for page in doc:
            texto_completo += page.get_text()
        doc.close()

        # Verificar colunas esperadas
        assert "VALOR CONTRATADO" in texto_completo or "TOTAL ADITIVOS" in texto_completo, \
            "Colunas do resumo financeiro ausentes"

        # Pelo menos um valor numerico formatado
        valores = re.findall(r"R\$\s[\d\.,]+", texto_completo)
        assert len(valores) > 0, "Nenhum valor monetario encontrado no PDF"

    def test_pdf_nao_contem_numeracao_de_pagina(self, pdf_gerado):
        """A numeracao de pagina foi removida intencionalmente.

        Regressao: numero de pagina no rodape causava duplicacao de
        paginas no relatorio. O rodape agora tem apenas a linha.
        """
        doc = fitz.open(str(pdf_gerado))
        texto_completo = ""
        for page in doc:
            texto_completo += page.get_text()
        doc.close()

        assert "Pagina" not in texto_completo, "Numeracao de pagina nao deveria existir"


class TestRelatorioGoldenMaster:
    """Testes de snapshot visual (golden master).

    Renderiza o PDF em PNG para revisao humana em tmp_path.
    Nao compara automaticamente (requer ferramenta de diff de imagem).
    """

    @pytest.fixture
    def servicos(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        db = DatabaseManager(tmp_path / "test.db")
        db.init_schema()
        storage = AppStorage(tmp_path / "storage")

        obra_repo = ObraRepository(db)
        aditivo_repo = AditivoRepository(db)
        lancamento_repo = LancamentoRepository(db)
        anexo_repo = AnexoRepository(db)
        relatorio_repo = RelatorioRepository(db)
        empresa_repo = EmpresaRepository(db)

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

        _seed_obra(
            services["obra_service"],
            services["aditivo_service"],
            services["lancamento_service"],
            services["empresa_service"],
        )

        return services

    @pytest.fixture
    def pdf_service(self, servicos):
        return ReportLabPDFService(**servicos)

    def test_golden_master_visual(self, pdf_service, tmp_path):
        """Renderiza PDF e salva PNG em tmp_path para revisao visual."""
        pdf_path = pdf_service.gerar_relatorio_obra_reportlab(1)

        doc = fitz.open(str(pdf_path))
        zoom = 150 / 72  # 150 DPI
        mat = fitz.Matrix(zoom, zoom)

        output_dir = tmp_path / "golden_preview"
        output_dir.mkdir()

        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=mat)
            png_path = output_dir / f"pagina_{i + 1:02d}.png"
            pix.save(str(png_path))

        doc.close()

        assert len(list(output_dir.glob("*.png"))) > 0, "Nenhuma imagem PNG gerada"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])