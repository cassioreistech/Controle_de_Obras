"""Casos de uso e serviços de aplicação."""

import shutil
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from controle_obras.domain.models import (
    Aditivo,
    Anexo,
    Configuracao,
    Empresa,
    Lancamento,
    Obra,
)
from controle_obras.domain.value_objects import ResumoFinanceiroObra
from controle_obras.infrastructure.backup import BackupError
from controle_obras.infrastructure.backup import BackupService as InfraBackupService
from controle_obras.infrastructure.backup_history import BackupHistory
from controle_obras.infrastructure.repositories import (
    AditivoRepository,
    AnexoRepository,
    ConfiguracaoRepository,
    EmpresaRepository,
    LancamentoRepository,
    ObraRepository,
    RelatorioRepository,
    TipoLancamentoRepository,
)
from controle_obras.infrastructure.storage import AppStorage, FileHasher


class EmpresaService:
    """Caso de uso para cadastro da empresa."""

    def __init__(self, repository: EmpresaRepository) -> None:
        self._repo = repository

    def salvar(self, empresa: Empresa) -> Empresa:
        return self._repo.save(empresa)

    def obter(self) -> Empresa | None:
        return self._repo.get()

    def empresa_configurada(self) -> bool:
        return self._repo.get() is not None


class ObraService:
    """Caso de uso para cadastro e gestão de obras."""

    def __init__(self, repository: ObraRepository) -> None:
        self._repo = repository

    def salvar(self, obra: Obra) -> Obra:
        if not obra.codigo:
            raise ValueError("Código da obra é obrigatório.")
        if not obra.nome:
            raise ValueError("Nome da obra é obrigatório.")
        if obra.valor_contratado_inicial is None:
            obra.valor_contratado_inicial = Decimal("0.00")
        return self._repo.save(obra)

    def listar(self) -> list[Obra]:
        return self._repo.list_all()

    def obter(self, obra_id: int) -> Obra | None:
        return self._repo.get_by_id(obra_id)

    def excluir(self, obra_id: int) -> None:
        self._repo.delete(obra_id)


class ObraResumoService:
    """Serviço de cálculo financeiro consolidado da obra."""

    def __init__(
        self,
        obra_repository: ObraRepository,
        aditivo_repository: AditivoRepository,
        lancamento_repository: LancamentoRepository,
    ) -> None:
        self._obra_repo = obra_repository
        self._aditivo_repo = aditivo_repository
        self._lancamento_repo = lancamento_repository

    def calcular_resumo(self, obra_id: int) -> ResumoFinanceiroObra:
        obra = self._obra_repo.get_by_id(obra_id)
        if not obra:
            raise ValueError(f"Obra {obra_id} não encontrada.")

        aditivos = self._aditivo_repo.list_by_obra(obra_id)
        total_aditivos = sum((a.valor for a in aditivos), Decimal("0.00"))

        lancamentos = self._lancamento_repo.list_by_obra(obra_id)
        total_gasto = sum((lanc.valor_total for lanc in lancamentos), Decimal("0.00"))

        return ResumoFinanceiroObra(
            valor_contratado=obra.valor_contratado_inicial,
            total_aditivos=total_aditivos,
            total_gasto=total_gasto,
        )


class AditivoService:
    """Caso de uso para aditivos."""

    def __init__(self, repository: AditivoRepository) -> None:
        self._repo = repository

    def salvar(self, aditivo: Aditivo) -> Aditivo:
        if not aditivo.descricao:
            raise ValueError("Descrição do aditivo é obrigatória.")
        if aditivo.valor is None:
            aditivo.valor = Decimal("0.00")
        return self._repo.save(aditivo)

    def listar_por_obra(self, obra_id: int) -> list[Aditivo]:
        return self._repo.list_by_obra(obra_id)

    def excluir(self, aditivo_id: int) -> None:
        self._repo.delete(aditivo_id)


class LancamentoService:
    """Caso de uso para lançamentos de custos."""

    def __init__(self, repository: LancamentoRepository) -> None:
        self._repo = repository

    def salvar(self, lancamento: Lancamento) -> Lancamento:
        if not lancamento.descricao:
            raise ValueError("Descrição do lançamento é obrigatória.")
        if lancamento.valor_total is None:
            lancamento.valor_total = Decimal("0.00")
        return self._repo.save(lancamento)

    def listar_por_obra(self, obra_id: int) -> list[Lancamento]:
        return self._repo.list_by_obra(obra_id)

    def obter(self, lancamento_id: int) -> Lancamento | None:
        return self._repo.get_by_id(lancamento_id)

    def excluir(self, lancamento_id: int) -> None:
        self._repo.delete(lancamento_id)


class TipoLancamentoService:
    """Serviço para tipos de lançamento."""

    def __init__(self, repository: TipoLancamentoRepository) -> None:
        self._repo = repository

    def listar_ativos(self) -> list[Any]:
        return self._repo.list_all()


class AnexoService:
    """Caso de uso para anexos."""

    def __init__(
        self,
        repository: AnexoRepository,
        storage: AppStorage,
    ) -> None:
        self._repo = repository
        self._storage = storage

    def anexar_arquivo(
        self,
        obra_codigo: str,
        arquivo_origem: Path,
        tipo_anexo: str,
        obra_id: int,
        lancamento_id: int | None = None,
        observacoes: str = "",
        data_documento: Any = None,
    ) -> Anexo:
        if not arquivo_origem.exists():
            raise ValueError(f"Arquivo não encontrado: {arquivo_origem}")

        relativo = self._storage.anexo_relative_path(
            obra_codigo, lancamento_id, arquivo_origem.name
        )
        destino = self._storage.anexo_path(obra_codigo, relativo)
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(arquivo_origem, destino)

        anexo = Anexo(
            obra_id=obra_id,
            lancamento_id=lancamento_id,
            tipo_anexo=tipo_anexo,
            nome_original=arquivo_origem.name,
            nome_armazenado=destino.name,
            caminho_relativo=relativo,
            hash_arquivo=FileHasher.sha256_file(destino),
            mime_type="",
            tamanho_bytes=destino.stat().st_size,
            data_documento=data_documento,
            observacoes=observacoes,
        )
        return self._repo.save(anexo)

    def listar_por_obra(self, obra_id: int) -> list[Anexo]:
        return self._repo.list_by_obra(obra_id)

    def obter(self, anexo_id: int) -> Anexo | None:
        return self._repo.get_by_id(anexo_id)

    def listar_por_lancamento(self, lancamento_id: int) -> list[Anexo]:
        return self._repo.list_by_lancamento(lancamento_id)

    def excluir(self, anexo_id: int) -> None:
        self._repo.delete(anexo_id)


class ConfiguracaoSistemaService:
    """Serviço para configurações do sistema."""

    def __init__(self, repository: ConfiguracaoRepository) -> None:
        self._repo = repository

    def obter_obra_ativa(self) -> int | None:
        config = self._repo.get("obra_ativa_id")
        if config and config.valor:
            return int(config.valor)
        return None

    def definir_obra_ativa(self, obra_id: int | None) -> None:
        self._repo.set(
            Configuracao(
                chave="obra_ativa_id",
                valor=str(obra_id) if obra_id else "",
                descricao="ID da obra atualmente selecionada no sistema",
            )
        )


class BackupApplicationService:
    """Wrapper de aplicação para o serviço de backup."""

    def __init__(
        self,
        backup_service: InfraBackupService,
        empresa_service: EmpresaService,
        obra_service: ObraService,
        anexo_service: AnexoService,
        storage: AppStorage,
        versao_sistema: str = "1.0.0",
    ) -> None:
        self._backup_service = backup_service
        self._empresa_service = empresa_service
        self._obra_service = obra_service
        self._anexo_service = anexo_service
        self._storage = storage
        self._versao = versao_sistema
        self._history = BackupHistory(storage.base_dir / "data")

    def gerar_backup(self, destino: Path | str | None = None) -> Path:
        self._history.registrar("backup", "iniciado")
        try:
            empresa = self._empresa_service.obter()
            nome_empresa = empresa.razao_social if empresa else ""
            obras = self._obra_service.listar()
            quantidade_anexos = sum(
                len(self._anexo_service.listar_por_obra(obra.id or 0)) for obra in obras
            )

            caminho = self._backup_service.gerar_backup(
                nome_empresa=nome_empresa,
                versao_sistema=self._versao,
                quantidade_obras=len(obras),
                quantidade_anexos=quantidade_anexos,
                destino=destino,
            )
            self._history.registrar(
                "backup",
                "concluido",
                {"arquivo": str(caminho), "obras": len(obras), "anexos": quantidade_anexos},
            )
            return caminho
        except BackupError as exc:
            self._history.registrar("backup", "falha", {"erro": str(exc)})
            raise

    def restaurar_backup(self, caminho_zip: Path | str) -> dict[str, Any]:
        self._history.registrar("restauracao", "iniciada", {"arquivo": str(caminho_zip)})
        try:
            manifest = self._backup_service.restaurar_backup(caminho_zip)
            self._history.registrar("restauracao", "concluida", {"arquivo": str(caminho_zip)})
            return manifest
        except BackupError as exc:
            self._history.registrar("restauracao", "falha", {"erro": str(exc)})
            raise

    def historico(self, limite: int = 50) -> list[dict[str, Any]]:
        return self._history.listar(limite)


class RelatorioPDFService:
    """Servico para geracao de relatorio PDF da obra.
    
    Motor unificado: ReportLab Platypus (sem dependencias externas).
    """

    def __init__(
        self,
        obra_service: ObraService,
        aditivo_service: AditivoService,
        lancamento_service: LancamentoService,
        anexo_service: AnexoService,
        resumo_service: ObraResumoService,
        relatorio_repo: RelatorioRepository,
        storage: AppStorage,
        empresa_service: "EmpresaService | None" = None,
    ) -> None:
        self._obra_service = obra_service
        self._aditivo_service = aditivo_service
        self._lancamento_service = lancamento_service
        self._anexo_service = anexo_service
        self._resumo_service = resumo_service
        self._relatorio_repo = relatorio_repo
        self._storage = storage
        self._empresa_service = empresa_service

    def _obter_responsavel(self) -> str:
        """Obtem o nome do responsavel legal da empresa."""
        if self._empresa_service is None:
            return ""
        try:
            empresa = self._empresa_service.obter()
            if empresa and empresa.responsavel:
                return empresa.responsavel
            return ""
        except Exception:
            return ""

    def _obter_cnpj(self) -> str:
        """Obtem o CNPJ da empresa."""
        if self._empresa_service is None:
            return ""
        try:
            empresa = self._empresa_service.obter()
            if empresa and empresa.cnpj:
                return empresa.cnpj
            return ""
        except Exception:
            return ""

    def gerar_relatorio_obra(self, obra_id: int) -> Path:
        """Gera relatorio PDF usando ReportLab Platypus.
        
        Args:
            obra_id: ID da obra para gerar o relatorio.
            
        Returns:
            Path do arquivo PDF gerado.
            
        Raises:
            ValueError: Se a obra nao for encontrada ou erro na geracao.
        """
        from controle_obras.application.reportlab_pdf_service import ReportLabPDFService

        rl_service = ReportLabPDFService(
            obra_service=self._obra_service,
            aditivo_service=self._aditivo_service,
            lancamento_service=self._lancamento_service,
            anexo_service=self._anexo_service,
            resumo_service=self._resumo_service,
            relatorio_repo=self._relatorio_repo,
            storage=self._storage,
            empresa_service=self._empresa_service,
        )

        return rl_service.gerar_relatorio_obra_reportlab(obra_id)

