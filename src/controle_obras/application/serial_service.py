"""Serviço de gerenciamento de seriais de licença."""

from datetime import date, datetime
from typing import Literal

from controle_obras.domain.models import Serial
from controle_obras.infrastructure.repositories import SerialRepository

TipoStatusSerial = Literal["Ativo", "Inativo", "Expirado"]


class SerialService:
    """Coordena operações de gerenciamento de seriais."""

    def __init__(self, repository: SerialRepository) -> None:
        self._repo = repository

    def registrar_serial(
        self,
        chave: str,
        cliente_nome: str,
        cliente_empresa: str,
        cliente_contato: str,
        maquina_id: str,
        data_validade: date,
        observacoes: str = "",
    ) -> Serial:
        """Registra um novo serial no sistema."""
        # Verificar se a chave já existe
        existing = self._repo.get_by_chave(chave)
        if existing:
            raise ValueError(f"Serial {chave} já está registrado")

        serial = Serial(
            chave=chave.upper(),
            cliente_nome=cliente_nome,
            cliente_empresa=cliente_empresa,
            cliente_contato=cliente_contato,
            maquina_id=maquina_id,
            data_geracao=date.today(),
            data_validade=data_validade,
            status="Ativo",
            observacoes=observacoes,
        )
        return self._repo.save(serial)

    def listar_todos(self) -> list[Serial]:
        """Lista todos os seriais registrados."""
        return self._repo.list_all()

    def listar_por_status(self, status: TipoStatusSerial) -> list[Serial]:
        """Lista seriais filtrados por status."""
        return self._repo.list_by_status(status)

    def listar_por_cliente(self, cliente_nome: str) -> list[Serial]:
        """Lista seriais de um cliente específico."""
        return self._repo.list_by_cliente(cliente_nome)

    def buscar_por_chave(self, chave: str) -> Serial | None:
        """Busca serial por chave."""
        return self._repo.get_by_chave(chave)

    def buscar_por_id(self, serial_id: int) -> Serial | None:
        """Busca serial por ID."""
        return self._repo.get_by_id(serial_id)

    def atualizar_status(self, serial_id: int, status: TipoStatusSerial) -> bool:
        """Atualiza o status de um serial."""
        serial = self._repo.get_by_id(serial_id)
        if not serial:
            return False
        serial.status = status
        serial.updated_at = datetime.now()
        self._repo.save(serial)
        return True

    def atualizar_serial(self, serial_id: int, **kwargs) -> bool:
        """Atualiza dados de um serial."""
        serial = self._repo.get_by_id(serial_id)
        if not serial:
            return False

        if "cliente_nome" in kwargs:
            serial.cliente_nome = kwargs["cliente_nome"]
        if "cliente_empresa" in kwargs:
            serial.cliente_empresa = kwargs["cliente_empresa"]
        if "cliente_contato" in kwargs:
            serial.cliente_contato = kwargs["cliente_contato"]
        if "observacoes" in kwargs:
            serial.observacoes = kwargs["observacoes"]
        if "status" in kwargs:
            serial.status = kwargs["status"]

        serial.updated_at = datetime.now()
        self._repo.save(serial)
        return True

    def excluir(self, serial_id: int) -> bool:
        """Exclui um serial do sistema."""
        serial = self._repo.get_by_id(serial_id)
        if not serial:
            return False
        self._repo.delete(serial_id)
        return True

    def obter_estatisticas(self) -> dict:
        """Retorna estatísticas dos seriais."""
        contagem = self._repo.count_by_status()
        todos = self._repo.list_all()

        total = len(todos)
        ativos = contagem.get("Ativo", 0)
        inativos = contagem.get("Inativo", 0)
        expirados = contagem.get("Expirado", 0)

        # Verificar seriais expirados (data_validade < hoje)
        hoje = date.today()
        expirados_real = sum(1 for s in todos if s.data_validade < hoje and s.status == "Ativo")

        return {
            "total": total,
            "ativos": ativos,
            "inativos": inativos,
            "expirados": expirados,
            "expirados_real": expirados_real,
        }

    def atualizar_expirados(self) -> int:
        """Atualiza automaticamente seriais expirados. Retorna quantidade atualizada."""
        todos = self._repo.list_all()
        hoje = date.today()
        atualizados = 0

        for serial in todos:
            if serial.status == "Ativo" and serial.data_validade < hoje:
                serial.status = "Expirado"
                serial.updated_at = datetime.now()
                self._repo.save(serial)
                atualizados += 1

        return atualizados
