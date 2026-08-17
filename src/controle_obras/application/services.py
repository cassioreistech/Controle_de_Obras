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
    """Serviço para geração de relatório PDF da obra."""

    def __init__(
        self,
        obra_service: ObraService,
        aditivo_service: AditivoService,
        lancamento_service: LancamentoService,
        anexo_service: AnexoService,
        resumo_service: ObraResumoService,
        relatorio_repo: RelatorioRepository,
        storage: AppStorage,
    ) -> None:
        self._obra_service = obra_service
        self._aditivo_service = aditivo_service
        self._lancamento_service = lancamento_service
        self._anexo_service = anexo_service
        self._resumo_service = resumo_service
        self._relatorio_repo = relatorio_repo
        self._storage = storage

    def gerar_relatorio_obra(self, obra_id: int) -> Path:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        obra = self._obra_service.obter(obra_id)
        if not obra:
            raise ValueError(f"Obra {obra_id} não encontrada.")

        resumo = self._resumo_service.calcular_resumo(obra_id)
        aditivos = self._aditivo_service.listar_por_obra(obra_id)
        lancamentos = self._lancamento_service.listar_por_obra(obra_id)
        anexos = self._anexo_service.listar_por_obra(obra_id)

        filename = f"relatorio_obra_{obra.codigo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = self._storage.relatorio_path(filename)

        c = canvas.Canvas(str(filepath), pagesize=A4)
        width, height = A4
        y = height - 50

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, f"Relatório da Obra: {obra.nome}")
        y -= 30

        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Código: {obra.codigo}")
        y -= 15
        c.drawString(50, y, f"Cliente: {obra.cliente_contratante}")
        y -= 15
        c.drawString(50, y, f"Local: {obra.local_obra}")
        y -= 15
        c.drawString(50, y, f"Engenheiro: {obra.engenheiro_responsavel}")
        y -= 30

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Resumo Financeiro")
        y -= 20
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Valor contratado: R$ {resumo.valor_contratado:,.2f}")
        y -= 15
        c.drawString(50, y, f"Total de aditivos: R$ {resumo.total_aditivos:,.2f}")
        y -= 15
        c.drawString(50, y, f"Total gasto: R$ {resumo.total_gasto:,.2f}")
        y -= 15
        c.drawString(50, y, f"Valor líquido: R$ {resumo.valor_liquido:,.2f}")
        y -= 30

        if aditivos:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Aditivos")
            y -= 20
            c.setFont("Helvetica", 10)
            for aditivo in aditivos:
                c.drawString(50, y, f"- {aditivo.data_aditivo}: {aditivo.descricao} - R$ {aditivo.valor:,.2f}")
                y -= 15
                if y < 100:
                    c.showPage()
                    y = height - 50
            y -= 15

        if lancamentos:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Lançamentos")
            y -= 20
            c.setFont("Helvetica", 10)
            for lanc in lancamentos:
                c.drawString(50, y, f"- {lanc.data_lancamento}: {lanc.descricao} - R$ {lanc.valor_total:,.2f}")
                y -= 15
                if y < 100:
                    c.showPage()
                    y = height - 50
            y -= 15

        if anexos:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Anexos")
            y -= 20
            c.setFont("Helvetica", 10)
            for anexo in anexos:
                c.drawString(50, y, f"- {anexo.nome_original}")
                y -= 15
                if y < 100:
                    c.showPage()
                    y = height - 50

        c.save()

        from controle_obras.domain.models import RelatorioGerado

        self._relatorio_repo.save(
            RelatorioGerado(
                obra_id=obra_id,
                tipo_relatorio="obra",
                arquivo_gerado=str(filepath),
            )
        )

        return filepath
