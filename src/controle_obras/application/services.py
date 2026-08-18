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

    def _obter_nome_tipo(self, tipo_lancamento_id: int | None) -> str:
        """Obtém o nome do tipo de lançamento pelo ID."""
        if tipo_lancamento_id is None:
            return ""
        try:
            from controle_obras.infrastructure.repositories import TipoLancamentoRepository
            repo = TipoLancamentoRepository(self._lancamento_service._repo._db)
            tipos = repo.list_all()
            for tipo in tipos:
                if tipo.id == tipo_lancamento_id:
                    return tipo.nome
            return ""
        except Exception:
            return ""

    def _obter_responsavel(self) -> str:
        """Obtém o nome do responsável legal da empresa."""
        if self._empresa_service is None:
            return "Não informado"
        try:
            empresa = self._empresa_service.obter()
            if empresa and empresa.responsavel:
                return empresa.responsavel
            return "Não informado"
        except Exception:
            return "Não informado"

    def _obter_cnpj(self) -> str:
        """Obtém o CNPJ da empresa."""
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
        from datetime import datetime

        from jinja2 import Environment, FileSystemLoader
        from xhtml2pdf import pisa

        obra = self._obra_service.obter(obra_id)
        if not obra:
            raise ValueError(f"Obra {obra_id} não encontrada.")

        resumo = self._resumo_service.calcular_resumo(obra_id)
        aditivos = self._aditivo_service.listar_por_obra(obra_id)
        lancamentos = self._lancamento_service.listar_por_obra(obra_id)
        anexos = self._anexo_service.listar_por_obra(obra_id)

        filename = f"relatorio_obra_{obra.codigo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = self._storage.relatorio_path(filename)

        templates_dir = Path(__file__).parent.parent / "templates"
        css_dir = Path(__file__).parent.parent / "static" / "css"

        env = Environment(loader=FileSystemLoader(str(templates_dir)))
        template = env.get_template("relatorio_obra.html")

        css_path = css_dir / "relatorio.css"
        css_content = css_path.read_text(encoding="utf-8")

        def formatar_moeda(valor: Decimal) -> str:
            return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        def formatar_data(d) -> str:
            if d is None:
                return ""
            if hasattr(d, "strftime"):
                return d.strftime("%d/%m/%Y")
            return str(d)

        def formatar_tamanho(tamanho_bytes: int) -> str:
            if tamanho_bytes >= 1024 * 1024:
                return f"{tamanho_bytes / (1024 * 1024):.1f} MB"
            elif tamanho_bytes >= 1024:
                return f"{tamanho_bytes / 1024:.1f} KB"
            return f"{tamanho_bytes} B"

        def texto(valor, padrao=""):
            return padrao if valor is None else str(valor)

        context = {
            "obra": {
                "codigo": texto(obra.codigo),
                "nome": texto(obra.nome, "Obra sem nome"),
                "cliente_contratante": texto(obra.cliente_contratante, "Não informado"),
                "local_obra": texto(obra.local_obra, "Não informado"),
                "engenheiro_responsavel": texto(obra.engenheiro_responsavel, "Não informado"),
            },
            "resumo": {
                "valor_contratado": formatar_moeda(resumo.valor_contratado),
                "total_aditivos": formatar_moeda(resumo.total_aditivos),
                "total_gasto": formatar_moeda(resumo.total_gasto),
                "valor_liquido": formatar_moeda(resumo.valor_liquido),
            },
            "aditivos": [
                {
                    "data": formatar_data(a.data_aditivo),
                    "descricao": texto(a.descricao, "Sem descrição"),
                    "valor": formatar_moeda(a.valor),
                }
                for a in aditivos
            ],
            "lancamentos": [
                {
                    "data": formatar_data(l.data_lancamento),
                    "descricao": texto(l.descricao, "Sem descrição"),
                    "tipo": self._obter_nome_tipo(l.tipo_lancamento_id),
                    "origem": texto(l.origem_informacao, "Não informado"),
                    "valor": formatar_moeda(l.valor_total),
                }
                for l in lancamentos
            ],
            "anexos": [
                {
                    "nome": texto(a.nome_original, "Sem nome"),
                    "tipo": texto(a.tipo_anexo, "Não informado"),
                    "data": formatar_data(a.data_documento or (a.created_at.date() if a.created_at else None)),
                    "tamanho": formatar_tamanho(a.tamanho_bytes or 0),
                }
                for a in anexos
            ],
            "responsavel": self._obter_responsavel(),
            "cnpj": self._obter_cnpj(),
            "data_emissao": datetime.now().strftime("%d/%m/%Y"),
            "css": css_content,
        }

        html_content = template.render(**context)

        with open(str(filepath), "w+b") as output_file:
            status = pisa.CreatePDF(
                html_content,
                dest=output_file,
                encoding="utf-8",
            )

        if status.err:
            raise ValueError(f"Erro ao gerar PDF: {status.err}")

        from controle_obras.domain.models import RelatorioGerado

        self._relatorio_repo.save(
            RelatorioGerado(
                obra_id=obra_id,
                tipo_relatorio="obra",
                arquivo_gerado=str(filepath),
            )
        )

        return filepath

    def gerar_relatorio_obra_weasyprint(self, obra_id: int) -> Path:
        """Gera relatório PDF usando WeasyPrint + Jinja2."""
        from datetime import datetime

        from jinja2 import Environment, FileSystemLoader
        from weasyprint import HTML

        obra = self._obra_service.obter(obra_id)
        if not obra:
            raise ValueError(f"Obra {obra_id} não encontrada.")

        resumo = self._resumo_service.calcular_resumo(obra_id)
        aditivos = self._aditivo_service.listar_por_obra(obra_id)
        lancamentos = self._lancamento_service.listar_por_obra(obra_id)
        anexos = self._anexo_service.listar_por_obra(obra_id)

        filename = f"relatorio_obra_{obra.codigo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = self._storage.relatorio_path(filename)

        templates_dir = Path(__file__).parent.parent / "templates"
        css_dir = Path(__file__).parent.parent / "static" / "css"

        env = Environment(loader=FileSystemLoader(str(templates_dir)))
        template = env.get_template("relatorio_obra_weasy.html")

        css_path = css_dir / "relatorio_weasy.css"
        css_content = css_path.read_text(encoding="utf-8")

        def formatar_moeda(valor: Decimal) -> str:
            return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        def formatar_data(d) -> str:
            if d is None:
                return ""
            if hasattr(d, "strftime"):
                return d.strftime("%d/%m/%Y")
            return str(d)

        def formatar_tamanho(tamanho_bytes: int) -> str:
            if tamanho_bytes >= 1024 * 1024:
                return f"{tamanho_bytes / (1024 * 1024):.1f} MB"
            elif tamanho_bytes >= 1024:
                return f"{tamanho_bytes / 1024:.1f} KB"
            return f"{tamanho_bytes} B"

        def texto(valor, padrao=""):
            return padrao if valor is None else str(valor)

        context = {
            "obra": {
                "codigo": texto(obra.codigo),
                "nome": texto(obra.nome, "Obra sem nome"),
                "cliente_contratante": texto(obra.cliente_contratante, "Não informado"),
                "local_obra": texto(obra.local_obra, "Não informado"),
                "engenheiro_responsavel": texto(obra.engenheiro_responsavel, "Não informado"),
            },
            "resumo": {
                "valor_contratado": formatar_moeda(resumo.valor_contratado),
                "total_aditivos": formatar_moeda(resumo.total_aditivos),
                "total_gasto": formatar_moeda(resumo.total_gasto),
                "valor_liquido": formatar_moeda(resumo.valor_liquido),
            },
            "aditivos": [
                {
                    "data": formatar_data(a.data_aditivo),
                    "descricao": texto(a.descricao, "Sem descrição"),
                    "valor": formatar_moeda(a.valor),
                }
                for a in aditivos
            ],
            "lancamentos": [
                {
                    "data": formatar_data(l.data_lancamento),
                    "descricao": texto(l.descricao, "Sem descrição"),
                    "tipo": self._obter_nome_tipo(l.tipo_lancamento_id),
                    "valor": formatar_moeda(l.valor_total),
                }
                for l in lancamentos
            ],
            "anexos": [
                {
                    "nome": texto(a.nome_original, "Sem nome"),
                    "tipo": texto(a.tipo_anexo, "Não informado"),
                    "data": formatar_data(a.data_documento or (a.created_at.date() if a.created_at else None)),
                    "tamanho": formatar_tamanho(a.tamanho_bytes or 0),
                }
                for a in anexos
            ],
            "responsavel": self._obter_responsavel(),
            "cnpj": self._obter_cnpj(),
            "data_emissao": datetime.now().strftime("%d/%m/%Y"),
            "css": css_content,
        }

        html_content = template.render(**context)

        HTML(string=html_content).write_pdf(str(filepath))

        from controle_obras.domain.models import RelatorioGerado

        self._relatorio_repo.save(
            RelatorioGerado(
                obra_id=obra_id,
                tipo_relatorio="obra_weasyprint",
                arquivo_gerado=str(filepath),
            )
        )

        return filepath
