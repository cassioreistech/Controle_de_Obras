"""Repositórios para acesso ao banco de dados."""

import sqlite3
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Generic, TypeVar

from controle_obras.domain.models import (
    Aditivo,
    Anexo,
    Configuracao,
    Empresa,
    Lancamento,
    Obra,
    RelatorioGerado,
    TipoLancamento,
)
from controle_obras.infrastructure.database import DatabaseManager

T = TypeVar("T")


def _to_decimal(value: Any) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value))


def _to_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


class BaseRepository(Generic[T]):
    """Repositório base com operações CRUD comuns."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db


class EmpresaRepository(BaseRepository[Empresa]):
    """Repositório para Empresa."""

    def save(self, empresa: Empresa) -> Empresa:
        data = {
            "razao_social": empresa.razao_social,
            "nome_fantasia": empresa.nome_fantasia,
            "cnpj": empresa.cnpj,
            "telefone": empresa.telefone,
            "email": empresa.email,
            "endereco": empresa.endereco,
            "cidade": empresa.cidade,
            "uf": empresa.uf,
            "responsavel": empresa.responsavel,
            "updated_at": datetime.now().isoformat(),
        }

        with self._db.get_connection() as conn:
            if empresa.id:
                conn.execute(
                    """
                    UPDATE empresa SET razao_social=:razao_social, nome_fantasia=:nome_fantasia,
                        cnpj=:cnpj, telefone=:telefone, email=:email, endereco=:endereco,
                        cidade=:cidade, uf=:uf, responsavel=:responsavel, updated_at=:updated_at
                    WHERE id=:id
                    """,
                    {**data, "id": empresa.id},
                )
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO empresa (razao_social, nome_fantasia, cnpj, telefone, email,
                        endereco, cidade, uf, responsavel, updated_at)
                    VALUES (:razao_social, :nome_fantasia, :cnpj, :telefone, :email,
                        :endereco, :cidade, :uf, :responsavel, :updated_at)
                    """,
                    data,
                )
                empresa.id = cursor.lastrowid
        return empresa

    def get(self) -> Empresa | None:
        row = self._db.execute("SELECT * FROM empresa LIMIT 1").fetchone()
        if not row:
            return None
        return Empresa(
            id=row["id"],
            razao_social=row["razao_social"],
            nome_fantasia=row["nome_fantasia"],
            cnpj=row["cnpj"],
            telefone=row["telefone"],
            email=row["email"],
            endereco=row["endereco"],
            cidade=row["cidade"],
            uf=row["uf"],
            responsavel=row["responsavel"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


class ObraRepository(BaseRepository[Obra]):
    """Repositório para Obra."""

    def save(self, obra: Obra) -> Obra:
        data = {
            "codigo": obra.codigo,
            "nome": obra.nome,
            "cliente_contratante": obra.cliente_contratante,
            "local_obra": obra.local_obra,
            "engenheiro_responsavel": obra.engenheiro_responsavel,
            "data_inicio": obra.data_inicio.isoformat() if obra.data_inicio else None,
            "previsao_termino": obra.previsao_termino.isoformat() if obra.previsao_termino else None,
            "status": obra.status,
            "valor_contratado_inicial": float(obra.valor_contratado_inicial),
            "observacoes": obra.observacoes,
            "updated_at": datetime.now().isoformat(),
        }

        with self._db.get_connection() as conn:
            if obra.id:
                conn.execute(
                    """
                    UPDATE obras SET codigo=:codigo, nome=:nome, cliente_contratante=:cliente_contratante,
                        local_obra=:local_obra, engenheiro_responsavel=:engenheiro_responsavel,
                        data_inicio=:data_inicio, previsao_termino=:previsao_termino, status=:status,
                        valor_contratado_inicial=:valor_contratado_inicial, observacoes=:observacoes,
                        updated_at=:updated_at
                    WHERE id=:id
                    """,
                    {**data, "id": obra.id},
                )
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO obras (codigo, nome, cliente_contratante, local_obra,
                        engenheiro_responsavel, data_inicio, previsao_termino, status,
                        valor_contratado_inicial, observacoes, updated_at)
                    VALUES (:codigo, :nome, :cliente_contratante, :local_obra,
                        :engenheiro_responsavel, :data_inicio, :previsao_termino, :status,
                        :valor_contratado_inicial, :observacoes, :updated_at)
                    """,
                    data,
                )
                obra.id = cursor.lastrowid
        return obra

    def get_by_id(self, obra_id: int) -> Obra | None:
        row = self._db.execute("SELECT * FROM obras WHERE id=?", (obra_id,)).fetchone()
        if not row:
            return None
        return self._row_to_obra(row)

    def list_all(self) -> list[Obra]:
        rows = self._db.execute("SELECT * FROM obras ORDER BY created_at DESC").fetchall()
        return [self._row_to_obra(row) for row in rows]

    def delete(self, obra_id: int) -> None:
        self._db.execute("DELETE FROM obras WHERE id=?", (obra_id,))

    @staticmethod
    def _row_to_obra(row: sqlite3.Row) -> Obra:
        return Obra(
            id=row["id"],
            codigo=row["codigo"],
            nome=row["nome"],
            cliente_contratante=row["cliente_contratante"],
            local_obra=row["local_obra"],
            engenheiro_responsavel=row["engenheiro_responsavel"],
            data_inicio=_to_date(row["data_inicio"]),
            previsao_termino=_to_date(row["previsao_termino"]),
            status=row["status"],
            valor_contratado_inicial=_to_decimal(row["valor_contratado_inicial"]),
            observacoes=row["observacoes"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


class AditivoRepository(BaseRepository[Aditivo]):
    """Repositório para Aditivo."""

    def save(self, aditivo: Aditivo) -> Aditivo:
        data = {
            "obra_id": aditivo.obra_id,
            "data_aditivo": aditivo.data_aditivo.isoformat(),
            "descricao": aditivo.descricao,
            "valor": float(aditivo.valor),
            "observacoes": aditivo.observacoes,
        }

        with self._db.get_connection() as conn:
            if aditivo.id:
                conn.execute(
                    """
                    UPDATE aditivos SET obra_id=:obra_id, data_aditivo=:data_aditivo,
                        descricao=:descricao, valor=:valor, observacoes=:observacoes
                    WHERE id=:id
                    """,
                    {**data, "id": aditivo.id},
                )
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO aditivos (obra_id, data_aditivo, descricao, valor, observacoes)
                    VALUES (:obra_id, :data_aditivo, :descricao, :valor, :observacoes)
                    """,
                    data,
                )
                aditivo.id = cursor.lastrowid
        return aditivo

    def list_by_obra(self, obra_id: int) -> list[Aditivo]:
        rows = self._db.execute(
            "SELECT * FROM aditivos WHERE obra_id=? ORDER BY data_aditivo DESC", (obra_id,)
        ).fetchall()
        return [self._row_to_aditivo(row) for row in rows]

    def delete(self, aditivo_id: int) -> None:
        self._db.execute("DELETE FROM aditivos WHERE id=?", (aditivo_id,))

    @staticmethod
    def _row_to_aditivo(row: sqlite3.Row) -> Aditivo:
        return Aditivo(
            id=row["id"],
            obra_id=row["obra_id"],
            data_aditivo=_to_date(row["data_aditivo"]) or date.today(),
            descricao=row["descricao"],
            valor=_to_decimal(row["valor"]),
            observacoes=row["observacoes"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


class TipoLancamentoRepository(BaseRepository[TipoLancamento]):
    """Repositório para Tipo de Lançamento."""

    def list_all(self) -> list[TipoLancamento]:
        rows = self._db.execute(
            "SELECT * FROM tipos_lancamento WHERE ativo=1 ORDER BY ordem_exibicao, nome"
        ).fetchall()
        return [self._row_to_tipo(row) for row in rows]

    @staticmethod
    def _row_to_tipo(row: sqlite3.Row) -> TipoLancamento:
        return TipoLancamento(
            id=row["id"],
            nome=row["nome"],
            ativo=bool(row["ativo"]),
            ordem_exibicao=row["ordem_exibicao"],
        )


class LancamentoRepository(BaseRepository[Lancamento]):
    """Repositório para Lançamento."""

    def save(self, lancamento: Lancamento) -> Lancamento:
        data = {
            "obra_id": lancamento.obra_id,
            "tipo_lancamento_id": lancamento.tipo_lancamento_id,
            "data_lancamento": lancamento.data_lancamento.isoformat(),
            "descricao": lancamento.descricao,
            "complemento": lancamento.complemento,
            "quantidade": float(lancamento.quantidade) if lancamento.quantidade else None,
            "unidade": lancamento.unidade,
            "valor_unitario": float(lancamento.valor_unitario) if lancamento.valor_unitario else None,
            "valor_total": float(lancamento.valor_total),
            "origem_informacao": lancamento.origem_informacao,
            "observacoes": lancamento.observacoes,
            "updated_at": datetime.now().isoformat(),
        }

        with self._db.get_connection() as conn:
            if lancamento.id:
                conn.execute(
                    """
                    UPDATE lancamentos SET obra_id=:obra_id, tipo_lancamento_id=:tipo_lancamento_id,
                        data_lancamento=:data_lancamento, descricao=:descricao,
                        complemento=:complemento, quantidade=:quantidade, unidade=:unidade,
                        valor_unitario=:valor_unitario, valor_total=:valor_total,
                        origem_informacao=:origem_informacao, observacoes=:observacoes,
                        updated_at=:updated_at
                    WHERE id=:id
                    """,
                    {**data, "id": lancamento.id},
                )
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO lancamentos (obra_id, tipo_lancamento_id, data_lancamento,
                        descricao, complemento, quantidade, unidade, valor_unitario, valor_total,
                        origem_informacao, observacoes, updated_at)
                    VALUES (:obra_id, :tipo_lancamento_id, :data_lancamento, :descricao,
                        :complemento, :quantidade, :unidade, :valor_unitario, :valor_total,
                        :origem_informacao, :observacoes, :updated_at)
                    """,
                    data,
                )
                lancamento.id = cursor.lastrowid
        return lancamento

    def list_by_obra(self, obra_id: int) -> list[Lancamento]:
        rows = self._db.execute(
            """
            SELECT l.*, t.nome AS tipo_nome
            FROM lancamentos l
            LEFT JOIN tipos_lancamento t ON t.id = l.tipo_lancamento_id
            WHERE l.obra_id=?
            ORDER BY l.data_lancamento DESC
            """,
            (obra_id,),
        ).fetchall()
        return [self._row_to_lancamento(row) for row in rows]

    def get_by_id(self, lancamento_id: int) -> Lancamento | None:
        row = self._db.execute(
            """
            SELECT l.*, t.nome AS tipo_nome
            FROM lancamentos l
            LEFT JOIN tipos_lancamento t ON t.id = l.tipo_lancamento_id
            WHERE l.id=?
            """,
            (lancamento_id,),
        ).fetchone()
        if not row:
            return None
        return self._row_to_lancamento(row)

    def delete(self, lancamento_id: int) -> None:
        self._db.execute("DELETE FROM lancamentos WHERE id=?", (lancamento_id,))

    @staticmethod
    def _row_to_lancamento(row: sqlite3.Row) -> Lancamento:
        return Lancamento(
            id=row["id"],
            obra_id=row["obra_id"],
            tipo_lancamento_id=row["tipo_lancamento_id"],
            tipo_nome=row["tipo_nome"] or "",
            data_lancamento=_to_date(row["data_lancamento"]) or date.today(),
            descricao=row["descricao"],
            complemento=row["complemento"] or "",
            quantidade=_to_decimal(row["quantidade"]) if row["quantidade"] is not None else None,
            unidade=row["unidade"] or "",
            valor_unitario=_to_decimal(row["valor_unitario"]) if row["valor_unitario"] is not None else None,
            valor_total=_to_decimal(row["valor_total"]),
            origem_informacao=row["origem_informacao"] or "",
            observacoes=row["observacoes"] or "",
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


class AnexoRepository(BaseRepository[Anexo]):
    """Repositório para Anexo."""

    def save(self, anexo: Anexo) -> Anexo:
        data = {
            "obra_id": anexo.obra_id,
            "lancamento_id": anexo.lancamento_id,
            "tipo_anexo": anexo.tipo_anexo,
            "nome_original": anexo.nome_original,
            "nome_armazenado": anexo.nome_armazenado,
            "caminho_relativo": anexo.caminho_relativo,
            "hash_arquivo": anexo.hash_arquivo,
            "mime_type": anexo.mime_type,
            "tamanho_bytes": anexo.tamanho_bytes,
            "data_documento": anexo.data_documento.isoformat() if anexo.data_documento else None,
            "observacoes": anexo.observacoes,
        }

        with self._db.get_connection() as conn:
            if anexo.id:
                conn.execute(
                    """
                    UPDATE anexos SET obra_id=:obra_id, lancamento_id=:lancamento_id,
                        tipo_anexo=:tipo_anexo, nome_original=:nome_original,
                        nome_armazenado=:nome_armazenado, caminho_relativo=:caminho_relativo,
                        hash_arquivo=:hash_arquivo, mime_type=:mime_type,
                        tamanho_bytes=:tamanho_bytes, data_documento=:data_documento,
                        observacoes=:observacoes
                    WHERE id=:id
                    """,
                    {**data, "id": anexo.id},
                )
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO anexos (obra_id, lancamento_id, tipo_anexo, nome_original,
                        nome_armazenado, caminho_relativo, hash_arquivo, mime_type,
                        tamanho_bytes, data_documento, observacoes)
                    VALUES (:obra_id, :lancamento_id, :tipo_anexo, :nome_original,
                        :nome_armazenado, :caminho_relativo, :hash_arquivo, :mime_type,
                        :tamanho_bytes, :data_documento, :observacoes)
                    """,
                    data,
                )
                anexo.id = cursor.lastrowid
        return anexo

    def list_by_obra(self, obra_id: int) -> list[Anexo]:
        rows = self._db.execute(
            "SELECT * FROM anexos WHERE obra_id=? ORDER BY created_at DESC", (obra_id,)
        ).fetchall()
        return [self._row_to_anexo(row) for row in rows]

    def get_by_id(self, anexo_id: int) -> Anexo | None:
        row = self._db.execute("SELECT * FROM anexos WHERE id=?", (anexo_id,)).fetchone()
        if not row:
            return None
        return self._row_to_anexo(row)

    def list_by_lancamento(self, lancamento_id: int) -> list[Anexo]:
        rows = self._db.execute(
            "SELECT * FROM anexos WHERE lancamento_id=? ORDER BY created_at DESC", (lancamento_id,)
        ).fetchall()
        return [self._row_to_anexo(row) for row in rows]

    def delete(self, anexo_id: int) -> None:
        self._db.execute("DELETE FROM anexos WHERE id=?", (anexo_id,))

    @staticmethod
    def _row_to_anexo(row: sqlite3.Row) -> Anexo:
        return Anexo(
            id=row["id"],
            obra_id=row["obra_id"],
            lancamento_id=row["lancamento_id"],
            tipo_anexo=row["tipo_anexo"] or "",
            nome_original=row["nome_original"],
            nome_armazenado=row["nome_armazenado"],
            caminho_relativo=row["caminho_relativo"],
            hash_arquivo=row["hash_arquivo"] or "",
            mime_type=row["mime_type"] or "",
            tamanho_bytes=row["tamanho_bytes"] or 0,
            data_documento=_to_date(row["data_documento"]),
            observacoes=row["observacoes"] or "",
            created_at=datetime.fromisoformat(row["created_at"]),
        )


class ConfiguracaoRepository(BaseRepository[Configuracao]):
    """Repositório para Configuração."""

    def get(self, chave: str) -> Configuracao | None:
        row = self._db.execute(
            "SELECT * FROM configuracoes WHERE chave=?", (chave,)
        ).fetchone()
        if not row:
            return None
        return Configuracao(
            id=row["id"],
            chave=row["chave"],
            valor=row["valor"],
            descricao=row["descricao"] or "",
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def set(self, configuracao: Configuracao) -> Configuracao:
        data = {
            "chave": configuracao.chave,
            "valor": configuracao.valor,
            "descricao": configuracao.descricao,
            "updated_at": datetime.now().isoformat(),
        }

        with self._db.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO configuracoes (chave, valor, descricao, updated_at)
                VALUES (:chave, :valor, :descricao, :updated_at)
                ON CONFLICT(chave) DO UPDATE SET
                    valor=excluded.valor,
                    descricao=excluded.descricao,
                    updated_at=excluded.updated_at
                """,
                data,
            )
            if not configuracao.id:
                configuracao.id = cursor.lastrowid
        return configuracao


class RelatorioRepository(BaseRepository[RelatorioGerado]):
    """Repositório para Relatórios Gerados."""

    def save(self, relatorio: RelatorioGerado) -> RelatorioGerado:
        data = {
            "obra_id": relatorio.obra_id,
            "tipo_relatorio": relatorio.tipo_relatorio,
            "arquivo_gerado": relatorio.arquivo_gerado,
            "observacoes": relatorio.observacoes,
        }

        with self._db.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO relatorios_gerados (obra_id, tipo_relatorio, arquivo_gerado, observacoes)
                VALUES (:obra_id, :tipo_relatorio, :arquivo_gerado, :observacoes)
                """,
                data,
            )
            relatorio.id = cursor.lastrowid
        return relatorio

    def list_by_obra(self, obra_id: int) -> list[RelatorioGerado]:
        rows = self._db.execute(
            "SELECT * FROM relatorios_gerados WHERE obra_id=? ORDER BY data_geracao DESC",
            (obra_id,),
        ).fetchall()
        return [
            RelatorioGerado(
                id=row["id"],
                obra_id=row["obra_id"],
                tipo_relatorio=row["tipo_relatorio"],
                arquivo_gerado=row["arquivo_gerado"],
                data_geracao=datetime.fromisoformat(row["data_geracao"]),
                observacoes=row["observacoes"] or "",
            )
            for row in rows
        ]
