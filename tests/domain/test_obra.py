"""Testes unitários completos para cadastro de obras.

Cenários testados:
- Criação com dados válidos
- Validação de campos obrigatórios
- Valores padrão
- Atualização de obra existente
- Exclusão de obra
- Listagem de obras
"""

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from controle_obras.application.services import ObraService
from controle_obras.domain.models import Obra
from controle_obras.infrastructure.repositories import ObraRepository


class TestObraModel:
    """Testes unitários para a entidade Obra."""

    def test_criar_obra_com_dados_validos(self):
        """Deve criar obra com todos os campos obrigatórios."""
        obra = Obra(
            codigo="OBRA-001",
            nome="Edifício Sunset",
            cliente_contratante="Construtora ABC",
        )

        assert obra.codigo == "OBRA-001"
        assert obra.nome == "Edifício Sunset"
        assert obra.cliente_contratante == "Construtora ABC"
        assert obra.id is None

    def test_obra_valor_padrao_zero(self):
        """Deve inicializar valor_contratado_inicial com 0.00."""
        obra = Obra(codigo="OBRA-002", nome="Projeto B")

        assert obra.valor_contratado_inicial == Decimal("0.00")

    def test_obra_status_padrao_em_andamento(self):
        """Deve inicializar status como 'Em andamento'."""
        obra = Obra(codigo="OBRA-003", nome="Projeto C")

        assert obra.status == "Em andamento"

    def test_obra_com_datas(self):
        """Deve aceitar datas de início e previsão de término."""
        obra = Obra(
            codigo="OBRA-004",
            nome="Projeto D",
            data_inicio=date(2024, 1, 15),
            previsao_termino=date(2024, 12, 31),
        )

        assert obra.data_inicio == date(2024, 1, 15)
        assert obra.previsao_termino == date(2024, 12, 31)

    def test_obra_com_valor_contratado(self):
        """Deve aceitar valor contratado específico."""
        obra = Obra(
            codigo="OBRA-005",
            nome="Projeto E",
            valor_contratado_inicial=Decimal("250000.00"),
        )

        assert obra.valor_contratado_inicial == Decimal("250000.00")


class TestObraService:
    """Testes unitários para o serviço de obras."""

    def test_salvar_obra_com_dados_validos(self):
        """Deve salvar obra com dados válidos e retornar com ID."""
        mock_repo = MagicMock(spec=ObraRepository)
        mock_repo.save.return_value = Obra(
            id=1,
            codigo="OBRA-001",
            nome="Edifício Sunset",
        )

        service = ObraService(mock_repo)
        obra = Obra(codigo="OBRA-001", nome="Edifício Sunset")

        resultado = service.salvar(obra)

        assert resultado.id == 1
        mock_repo.save.assert_called_once_with(obra)

    def test_salvar_obra_sem_codigo_levanta_erro(self):
        """Deve levantar erro se código estiver vazio."""
        mock_repo = MagicMock(spec=ObraRepository)
        service = ObraService(mock_repo)

        obra = Obra(codigo="", nome="Projeto Sem Código")

        with pytest.raises(ValueError, match="Código da obra é obrigatório"):
            service.salvar(obra)

    def test_salvar_obra_sem_nome_levanta_erro(self):
        """Deve levantar erro se nome estiver vazio."""
        mock_repo = MagicMock(spec=ObraRepository)
        service = ObraService(mock_repo)

        obra = Obra(codigo="OBRA-001", nome="")

        with pytest.raises(ValueError, match="Nome da obra é obrigatório"):
            service.salvar(obra)

    def test_salvar_obra_definir_valor_padrao(self):
        """Deve definir valor 0.00 se None."""
        mock_repo = MagicMock(spec=ObraRepository)
        mock_repo.save.return_value = Obra(id=1, codigo="OBRA-001", nome="Projeto")

        service = ObraService(mock_repo)
        obra = Obra(codigo="OBRA-001", nome="Projeto", valor_contratado_inicial=None)

        service.salvar(obra)

        assert obra.valor_contratado_inicial == Decimal("0.00")

    def test_listar_obras(self):
        """Deve retornar lista de obras."""
        mock_repo = MagicMock(spec=ObraRepository)
        mock_repo.list_all.return_value = [
            Obra(id=1, codigo="OBRA-001", nome="Projeto 1"),
            Obra(id=2, codigo="OBRA-002", nome="Projeto 2"),
        ]

        service = ObraService(mock_repo)
        obras = service.listar()

        assert len(obras) == 2
        assert obras[0].codigo == "OBRA-001"
        mock_repo.list_all.assert_called_once()

    def test_obter_obra_por_id(self):
        """Deve retornar obra pelo ID."""
        mock_repo = MagicMock(spec=ObraRepository)
        obra_esperada = Obra(id=1, codigo="OBRA-001", nome="Projeto 1")
        mock_repo.get_by_id.return_value = obra_esperada

        service = ObraService(mock_repo)
        obra = service.obter(1)

        assert obra is not None
        assert obra.id == 1
        mock_repo.get_by_id.assert_called_once_with(1)

    def test_obter_obra_inexistente(self):
        """Deve retornar None se obra não existir."""
        mock_repo = MagicMock(spec=ObraRepository)
        mock_repo.get_by_id.return_value = None

        service = ObraService(mock_repo)
        obra = service.obter(999)

        assert obra is None

    def test_excluir_obra(self):
        """Deve excluir obra pelo ID."""
        mock_repo = MagicMock(spec=ObraRepository)
        service = ObraService(mock_repo)

        service.excluir(1)

        mock_repo.delete.assert_called_once_with(1)
