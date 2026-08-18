"""Testes de integração para cadastro de obras com banco real.

Testa:
- Criação e persistência no SQLite
- Validações no banco
- Operações CRUD completas
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from controle_obras.application.services import ObraService
from controle_obras.domain.models import Obra
from controle_obras.infrastructure.database import DatabaseManager
from controle_obras.infrastructure.repositories import ObraRepository


@pytest.fixture
def db_in_memory(tmp_path: Path):
    """Cria banco de dados temporário para testes."""
    db = DatabaseManager(tmp_path / "test.db")
    db.init_schema()
    return db


@pytest.fixture
def obra_service(db_in_memory):
    """Cria serviço de obras com banco real."""
    repo = ObraRepository(db_in_memory)
    return ObraService(repo)


class TestObraIntegration:
    """Testes de integração com banco de dados."""

    def test_criar_obra_no_banco(self, obra_service):
        """Deve criar obra e persistir no banco."""
        obra = Obra(
            codigo="OBRA-001",
            nome="Edifício Sunset",
            cliente_contratante="Construtora ABC",
            local_obra="São Paulo",
            valor_contratado_inicial=Decimal("150000.00"),
        )

        resultado = obra_service.salvar(obra)

        assert resultado.id is not None
        assert resultado.id > 0

    def test_listar_obras_no_banco(self, obra_service):
        """Deve listar obras criadas no banco."""
        obra_service.salvar(Obra(codigo="OBRA-001", nome="Projeto 1"))
        obra_service.salvar(Obra(codigo="OBRA-002", nome="Projeto 2"))

        obras = obra_service.listar()

        assert len(obras) == 2

    def test_obter_obra_por_id_banco(self, obra_service):
        """Deve recuperar obra pelo ID no banco."""
        obra_original = obra_service.salvar(
            Obra(codigo="OBRA-001", nome="Projeto Único")
        )

        obra_recuperada = obra_service.obter(obra_original.id)

        assert obra_recuperada is not None
        assert obra_recuperada.codigo == "OBRA-001"
        assert obra_recuperada.nome == "Projeto Único"

    def test_atualizar_obra(self, obra_service):
        """Deve atualizar dados de obra existente."""
        obra = obra_service.salvar(
            Obra(codigo="OBRA-001", nome="Nome Original")
        )

        obra.nome = "Nome Atualizado"
        obra_service.salvar(obra)

        obra_atualizada = obra_service.obter(obra.id)
        assert obra_atualizada.nome == "Nome Atualizado"

    def test_excluir_obra(self, obra_service):
        """Deve excluir obra do banco."""
        obra = obra_service.salvar(Obra(codigo="OBRA-001", nome="Para Excluir"))

        obra_service.excluir(obra.id)

        assert obra_service.obter(obra.id) is None

    def test_obra_com_datas_banco(self, obra_service):
        """Deve persistir e recuperar datas corretamente."""
        obra = obra_service.salvar(
            Obra(
                codigo="OBRA-001",
                nome="Projeto com Datas",
                data_inicio=date(2024, 3, 15),
                previsao_termino=date(2024, 11, 30),
            )
        )

        obra_recuperada = obra_service.obter(obra.id)

        assert obra_recuperada.data_inicio == date(2024, 3, 15)
        assert obra_recuperada.previsao_termino == date(2024, 11, 30)

    def test_obra_com_valores_grandes(self, obra_service):
        """Deve lidar com valores contratados grandes."""
        valor_grande = Decimal("999999999.99")
        obra = obra_service.salvar(
            Obra(
                codigo="OBRA-GRANDE",
                nome="Projeto Grande",
                valor_contratado_inicial=valor_grande,
            )
        )

        obra_recuperada = obra_service.obter(obra.id)

        assert obra_recuperada.valor_contratado_inicial == valor_grande

    def test_validar_campos_obrigatorios_banco(self, obra_service):
        """Deve rejeitar obra sem código no banco."""
        with pytest.raises(ValueError, match="Código da obra é obrigatório"):
            obra_service.salvar(Obra(codigo="", nome="Sem Código"))

    def test_ordenacao_obras_por_data(self, obra_service):
        """Deve ordenar obras por data de criacao (mais recente primeiro)."""
        import time

        # Criar primeira obra
        obra_service.salvar(Obra(codigo="OBRA-001", nome="Primeira"))

        # CURRENT_TIMESTAMP tem precisao de segundos: esperar > 1s
        time.sleep(1.1)

        # Criar segunda obra
        obra_service.salvar(Obra(codigo="OBRA-002", nome="Segunda"))

        obras = obra_service.listar()

        # OBRA-002 foi criada depois, deve aparecer primeiro
        assert obras[0].codigo == "OBRA-002"
        assert obras[1].codigo == "OBRA-001"
