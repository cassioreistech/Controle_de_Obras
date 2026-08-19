"""Servico de licenciamento: trial por data + chave de licenca offline (HMAC).

Nivel 1 de protecao: sem backend. A chave e validada por HMAC local e
embute a data de validade. Adequado para fase de teste com cliente.

ATENCAO: o segredo abaixo esta compilado no executavel. Para uma
protecao forte, usar ativacao online (phone-home).
"""

import hashlib
import hmac
from datetime import date, datetime
from typing import Literal

from controle_obras.domain.models import Configuracao
from controle_obras.infrastructure.repositories import ConfiguracaoRepository

SECRETO_LICENCA = "C0ntr0le-0br4s-L1c3nc4-2026!@#$"

TRIAL_DIAS = 7
TRIAL_AVISO_DIAS = 7

CHAVE_PRIMEIRO_USO = "licenca_primeiro_uso"
CHAVE_LICENCA = "licenca_chave"

TipoStatus = Literal[
    "LICENCIADO",
    "EM_TRIAL",
    "TRIAL_EXPIRADO",
    "CHAVE_INVALIDA",
    "CHAVE_EXPIRADA",
]


class StatusLicenca:
    """Resultado da verificacao de licenca."""

    def __init__(self, tipo: TipoStatus, dias_restantes: int | None = None) -> None:
        self.tipo = tipo
        self.dias_restantes = dias_restantes


def _checksum(validade: date) -> str:
    payload = f"CONTROLE-OBRAS|{validade.isoformat()}"
    digest = hmac.new(
        SECRETO_LICENCA.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest[:5].upper()


def gerar_chave(validade: date) -> str:
    """Gera uma chave de licenca valida ate a data informada.

    Formato: YYYYMMDD-XXXXX (data de validade + checksum HMAC).
    """
    return f"{validade.strftime('%Y%m%d')}-{_checksum(validade)}"


def validar_chave(chave: str) -> date | None:
    """Valida a assinatura da chave e retorna a data de validade.

    Retorna None se a chave for invalida (assinatura errada ou formato ruim).
    """
    chave = chave.strip().upper().replace(" ", "")
    if len(chave) != 14 or chave[8] != "-":
        return None
    try:
        validade = datetime.strptime(chave[:8], "%Y%m%d").date()
    except ValueError:
        return None
    if not hmac.compare_digest(_checksum(validade), chave[9:]):
        return None
    return validade


class LicencaService:
    """Coordena trial e chave de licenca usando a tabela de configuracoes."""

    def __init__(self, repository: ConfiguracaoRepository) -> None:
        self._repo = repository

    def verificar(self) -> StatusLicenca:
        hoje = date.today()

        config_chave = self._repo.get(CHAVE_LICENCA)
        if config_chave and config_chave.valor:
            validade = validar_chave(config_chave.valor)
            if validade is None:
                return StatusLicenca("CHAVE_INVALIDA")
            if validade < hoje:
                return StatusLicenca("CHAVE_EXPIRADA", dias_restantes=0)
            return StatusLicenca("LICENCIADO", dias_restantes=(validade - hoje).days)

        config_trial = self._repo.get(CHAVE_PRIMEIRO_USO)
        if not config_trial or not config_trial.valor:
            self._repo.set(
                Configuracao(
                    chave=CHAVE_PRIMEIRO_USO,
                    valor=hoje.isoformat(),
                    descricao="Data do primeiro uso (inicio do periodo de teste)",
                )
            )
            return StatusLicenca("EM_TRIAL", dias_restantes=TRIAL_DIAS)

        try:
            primeiro_uso = datetime.strptime(config_trial.valor, "%Y-%m-%d").date()
        except ValueError:
            primeiro_uso = hoje

        dias_usados = (hoje - primeiro_uso).days
        restantes = TRIAL_DIAS - dias_usados
        if restantes > 0:
            return StatusLicenca("EM_TRIAL", dias_restantes=restantes)
        return StatusLicenca("TRIAL_EXPIRADO", dias_restantes=0)

    def registrar_chave(self, chave: str) -> bool:
        """Valida e registra a chave. Retorna True se aceita."""
        validade = validar_chave(chave)
        if validade is None:
            return False
        self._repo.set(
            Configuracao(
                chave=CHAVE_LICENCA,
                valor=chave.strip().upper(),
                descricao=f"Chave de licenca valida ate {validade.isoformat()}",
            )
        )
        return True
