"""Testes E2E completos - Fluxo: Criar Obra -> Aditivo -> Relatório.

Cenários testados:
1. Fluxo principal feliz (happy path)
2. Fluxo com múltiplos aditivos
3. Fluxo com valores zeros
4. Validações de integridade referencial
5. Relatório com dados completos
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from controle_obras.application.services import (
    AditivoService,
    AnexoService,
    EmpresaService,
    LancamentoService,
    ObraResumoService,
    ObraService,
    RelatorioPDFService,
)
from controle_obras.domain.models import Aditivo, Anexo, Empresa, Lancamento, Obra
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


class MockAnexoService:
    """Mock de anexo_service para testes de relatório."""

    def listar_por_obra(self, obra_id: int) -> list[Anexo]:
        return []

    def obter(self, anexo_id: int) -> Anexo | None:
        return None


@pytest.fixture
def full_services(tmp_path: Path):
    """Cria todos os serviços com banco real para testes E2E."""
    db = DatabaseManager(tmp_path / "e2e.db")
    db.init_schema()

    storage = AppStorage(tmp_path)
    empresa_repo = EmpresaRepository(db)
    obra_repo = ObraRepository(db)
    aditivo_repo = AditivoRepository(db)
    lancamento_repo = LancamentoRepository(db)
    relatorio_repo = RelatorioRepository(db)

    return {
        "db": db,
        "storage": storage,
        "empresa": EmpresaService(empresa_repo),
        "obra": ObraService(obra_repo),
        "aditivo": AditivoService(aditivo_repo),
        "lancamento": LancamentoService(lancamento_repo),
        "resumo": ObraResumoService(obra_repo, aditivo_repo, lancamento_repo),
    }


class TestFluxoCompletoObraAditivo:
    """Testes E2E do fluxo completo de cadastro."""

    def test_fluxo_principal_feliz(self, full_services):
        """FLUXO 1: Criar obra -> Adicionar aditivo -> Verificar resumo."""
        svc = full_services

        # 1. Cadastrar empresa
        empresa = Empresa(
            razao_social="Construtora XYZ",
            nome_fantasia="XYZ Engenharia",
            cnpj="12.345.678/0001-90",
        )
        empresa_salva = svc["empresa"].salvar(empresa)
        assert empresa_salva.id is not None

        # 2. Criar obra
        obra = Obra(
            codigo="OBRA-001",
            nome="Edifício Residencial Sol",
            cliente_contratante="João da Silva",
            local_obra="São Paulo - SP",
            engenheiro_responsavel="Eng. Maria Santos",
            data_inicio=date(2024, 1, 15),
            previsao_termino=date(2024, 12, 31),
            valor_contratado_inicial=Decimal("500000.00"),
        )
        obra_salva = svc["obra"].salvar(obra)

        assert obra_salva.id is not None
        assert obra_salva.codigo == "OBRA-001"

        # 3. Adicionar 2 aditivos
        aditivo1 = Aditivo(
            obra_id=obra_salva.id,
            data_aditivo=date(2024, 3, 10),
            descricao="Acréscimo de vagas",
            valor=Decimal("75000.00"),
        )
        aditivo2 = Aditivo(
            obra_id=obra_salva.id,
            data_aditivo=date(2024, 6, 20),
            descricao="Mudança de acabamento",
            valor=Decimal("45000.00"),
        )
        svc["aditivo"].salvar(aditivo1)
        svc["aditivo"].salvar(aditivo2)

        # 4. Registrar lançamentos
        lanc1 = Lancamento(
            obra_id=obra_salva.id,
            descricao="Cimento CP-II 50kg",
            quantidade=Decimal("100"),
            unidade="sc",
            valor_unitario=Decimal("45.00"),
            valor_total=Decimal("4500.00"),
        )
        lanc2 = Lancamento(
            obra_id=obra_salva.id,
            descricao="Areia média",
            quantidade=Decimal("20"),
            unidade="m3",
            valor_unitario=Decimal("120.00"),
            valor_total=Decimal("2400.00"),
        )
        svc["lancamento"].salvar(lanc1)
        svc["lancamento"].salvar(lanc2)

        # 5. Verificar resumo financeiro
        resumo = svc["resumo"].calcular_resumo(obra_salva.id)

        assert resumo.valor_contratado == Decimal("500000.00")
        assert resumo.total_aditivos == Decimal("120000.00")  # 75000 + 45000
        assert resumo.total_gasto == Decimal("6900.00")  # 4500 + 2400
        assert resumo.valor_liquido == Decimal("613100.00")  # 500000 + 120000 - 6900

    def test_fluxo_aditivos_multiplas_vezes(self, full_services):
        """FLUXO 2: Adicionar múltiplos aditivos em datas diferentes."""
        svc = full_services

        obra = svc["obra"].salvar(
            Obra(
                codigo="OBRA-002",
                nome="Conjunto Habitacional",
                valor_contratado_inicial=Decimal("1000000.00"),
            )
        )

        # Adicionar 5 aditivos
        valores = [
            Decimal("50000.00"),
            Decimal("75000.00"),
            Decimal("120000.00"),
            Decimal("30000.00"),
            Decimal("25000.00"),
        ]

        for i, valor in enumerate(valores, 1):
            aditivo = Aditivo(
                obra_id=obra.id,
                data_aditivo=date(2024, i * 2, 15),
                descricao=f"Aditivo {i}",
                valor=valor,
            )
            svc["aditivo"].salvar(aditivo)

        # Verificar total de aditivos
        aditivos = svc["aditivo"].listar_por_obra(obra.id)
        assert len(aditivos) == 5

        total_esperado = sum(valores)
        resumo = svc["resumo"].calcular_resumo(obra.id)
        assert resumo.total_aditivos == total_esperado

    def test_fluxo_obra_sem_aditivos(self, full_services):
        """FLUXO 3: Obra criada sem aditivos."""
        svc = full_services

        obra = svc["obra"].salvar(
            Obra(
                codigo="OBRA-003",
                nome="Projeto Simples",
                valor_contratado_inicial=Decimal("100000.00"),
            )
        )

        resumo = svc["resumo"].calcular_resumo(obra.id)

        assert resumo.total_aditivos == Decimal("0.00")
        assert resumo.valor_liquido == Decimal("100000.00")

    def test_fluxo_obra_valores_zeros(self, full_services):
        """FLUXO 4: Obra e aditivos com valores zero."""
        svc = full_services

        obra = svc["obra"].salvar(
            Obra(
                codigo="OBRA-004",
                nome="Projeto Pro Bono",
                valor_contratado_inicial=Decimal("0.00"),
            )
        )

        aditivo = Aditivo(
            obra_id=obra.id,
            descricao="Custo operacional",
            valor=Decimal("0.00"),
        )
        svc["aditivo"].salvar(aditivo)

        resumo = svc["resumo"].calcular_resumo(obra.id)

        assert resumo.valor_contratado == Decimal("0.00")
        assert resumo.total_aditivos == Decimal("0.00")
        assert resumo.valor_liquido == Decimal("0.00")


class TestFluxoRelatorioPDF:
    """Testes E2E para geração de relatório PDF."""

    def test_gerar_relatorio_obra_com_dados(self, full_services):
        """FLUXO 5: Gerar relatório PDF com dados completos."""
        svc = full_services

        # Configurar empresa
        svc["empresa"].salvar(
            Empresa(
                razao_social="Construtora ABC",
                cnpj="11.222.333/0001-44",
                responsavel="Carlos Alberto",
            )
        )

        # Criar obra
        obra = svc["obra"].salvar(
            Obra(
                codigo="OBRA-005",
                nome="Edifício Comercial",
                cliente_contratante="Empresa XYZ",
                local_obra="Rio de Janeiro - RJ",
                data_inicio=date(2024, 2, 1),
                previsao_termino=date(2024, 11, 30),
                valor_contratado_inicial=Decimal("800000.00"),
            )
        )

        # Adicionar aditivo
        svc["aditivo"].salvar(
            Aditivo(
                obra_id=obra.id,
                descricao="Acréscimo de 10 pavimentos",
                valor=Decimal("200000.00"),
            )
        )

        # Adicionar lançamento
        svc["lancamento"].salvar(
            Lancamento(
                obra_id=obra.id,
                descricao="Aço CA-50",
                valor_total=Decimal("45000.00"),
            )
        )

        # Gerar relatório
        relatorio_service = RelatorioPDFService(
            obra_service=svc["obra"],
            aditivo_service=svc["aditivo"],
            lancamento_service=svc["lancamento"],
            anexo_service=MockAnexoService(),
            resumo_service=svc["resumo"],
            relatorio_repo=RelatorioRepository(svc["db"]),
            storage=svc["storage"],
            empresa_service=svc["empresa"],
        )

        pdf_path = relatorio_service.gerar_relatorio_obra(obra.id)

        # Verificar que o PDF foi gerado
        assert pdf_path is not None
        assert pdf_path.exists()
        assert pdf_path.suffix == ".pdf"
        assert pdf_path.stat().st_size > 0

    def test_gerar_relatorio_obras_multiplas(self, full_services):
        """FLUXO 6: Gerar relatórios para múltiplas obras."""
        svc = full_services

        svc["empresa"].salvar(
            Empresa(razao_social="Empresa Teste", cnpj="00.000.000/0001-00")
        )

        relatorio_service = RelatorioPDFService(
            obra_service=svc["obra"],
            aditivo_service=svc["aditivo"],
            lancamento_service=svc["lancamento"],
            anexo_service=MockAnexoService(),
            resumo_service=svc["resumo"],
            relatorio_repo=RelatorioRepository(svc["db"]),
            storage=svc["storage"],
            empresa_service=svc["empresa"],
        )

        # Criar 3 obras e gerar relatório de cada
        for i in range(1, 4):
            obra = svc["obra"].salvar(
                Obra(
                    codigo=f"OBRA-R{i:03d}",
                    nome=f"Projeto Relatório {i}",
                    valor_contratado_inicial=Decimal(f"{i * 100000}.00"),
                )
            )
            pdf_path = relatorio_service.gerar_relatorio_obra(obra.id)
            assert pdf_path.exists()


class TestIntegridadeReferencial:
    """Testes de integridade referencial do banco."""

    def test_excluir_obra_remove_aditivos(self, full_services):
        """FLUXO 7: Excluir obra deve excluir aditivos (CASCADE)."""
        svc = full_services

        obra = svc["obra"].salvar(
            Obra(codigo="OBRA-006", nome="Para Excluir")
        )

        svc["aditivo"].salvar(
            Aditivo(obra_id=obra.id, descricao="Aditivo 1", valor=Decimal("10000.00"))
        )
        svc["aditivo"].salvar(
            Aditivo(obra_id=obra.id, descricao="Aditivo 2", valor=Decimal("20000.00"))
        )

        # Verificar que aditivos existem
        assert len(svc["aditivo"].listar_por_obra(obra.id)) == 2

        # Excluir obra
        svc["obra"].excluir(obra.id)

        # Verificar que aditivos foram removidos
        assert len(svc["aditivo"].listar_por_obra(obra.id)) == 0

    def test_listar_obras_por_codigo(self, full_services):
        """FLUXO 8: Buscar obra por código."""
        svc = full_services

        svc["obra"].salvar(
            Obra(codigo="UNICO-001", nome="Projeto Único")
        )

        obras = svc["obra"].listar()

        # Filtrar por código
        obras_filtradas = [o for o in obras if o.codigo == "UNICO-001"]
        assert len(obras_filtradas) == 1
        assert obras_filtradas[0].nome == "Projeto Único"


class TestValidacoesNegativas:
    """Testes de validações e cenários negativos."""

    def test_aditivo_sem_descricao_levanta_erro(self, full_services):
        """Deve rejeitar aditivo sem descrição."""
        svc = full_services

        obra = svc["obra"].salvar(
            Obra(codigo="OBRA-007", nome="Teste")
        )

        aditivo = Aditivo(
            obra_id=obra.id,
            descricao="",
            valor=Decimal("10000.00"),
        )

        with pytest.raises(ValueError, match="Descrição do aditivo é obrigatória"):
            svc["aditivo"].salvar(aditivo)

    def test_lancamento_sem_descricao_levanta_erro(self, full_services):
        """Deve rejeitar lançamento sem descrição."""
        svc = full_services

        obra = svc["obra"].salvar(
            Obra(codigo="OBRA-008", nome="Teste")
        )

        lancamento = Lancamento(
            obra_id=obra.id,
            descricao="",
            valor_total=Decimal("500.00"),
        )

        with pytest.raises(ValueError, match="Descrição do lançamento é obrigatória"):
            svc["lancamento"].salvar(lancamento)

    def test_resumo_obra_inexistente_levanta_erro(self, full_services):
        """Deve levantar erro ao calcular resumo de obra inexistente."""
        svc = full_services

        with pytest.raises(ValueError, match="não encontrada"):
            svc["resumo"].calcular_resumo(99999)
