"""Servico de licenciamento: trial por data + chave de licenca offline vinculada a maquina (HMAC).

Nivel 2 de protecao: sem backend, com vínculo ao hardware do cliente.
A chave embute a data de validade e e assinada sobre um ID estavel da
maquina, impedindo uso em outro computador.

ATENCAO: o segredo abaixo esta compilado no executavel. Uma protecao
forte exigiria ativacao online (phone-home). Porem o vínculo por maquina
ja impede a c\u00f3pia simples da chave para outro PC.
"""

import hashlib
import hmac
import uuid
from datetime import date, datetime
from typing import Literal

from controle_obras.domain.models import Configuracao
from controle_obras.infrastructure.repositories import ConfiguracaoRepository

# Segredo ofuscado (nao aparece em texto puro no binario).
_SECRETO_HEX = bytes.fromhex(
    "4330 6e74 7230 6c65 2d30 6272 3473 2d4c 3163 336e 6334 2d32 3032 3621 4023 24".replace(" ", "")
)
SECRETO_LICENCA = _SECRETO_HEX.decode("utf-8")

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


def obter_maquina_id() -> str:
    """Retorna um identificador estavel da maquina (MachineGuid do Windows).

    Usado para vincular a chave de licenca a um unico computador.
    """
    import os

    maquina_id = ""
    if os.name == "nt":
        import winreg  # type: ignore

        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Cryptography",
                0,
                winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
            ) as chave:
                maquina_id, _ = winreg.QueryValueEx(chave, "MachineGuid")
        except OSError:
            maquina_id = ""

    if not maquina_id:
        # Fallback: MAC/host-based (menos estavel, mas portavel)
        maquina_id = str(uuid.getnode())

    return _hash_of(maquina_id)


def _hash_of(texto: str) -> str:
    """Gera um hash curto e legivel do identificador."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:6].upper()


class StatusLicenca:
    """Resultado da verificacao de licenca."""

    def __init__(self, tipo: TipoStatus, dias_restantes: int | None = None) -> None:
        self.tipo = tipo
        self.dias_restantes = dias_restantes


def _checksum(validade: date, maquina_id: str) -> str:
    payload = f"CONTROLE-OBRAS|{validade.isoformat()}|{maquina_id}"
    digest = hmac.new(
        SECRETO_LICENCA.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest[:5].upper()


def gerar_chave(validade: date, maquina_id: str) -> str:
    """Gera uma chave de licenca valida ate a data informada, vinculada a maquina.

    Formato: YYYYMMDD-XXXXX (data de validade + checksum HMAC sobre a maquina).
    """
    return f"{validade.strftime('%Y%m%d')}-{_checksum(validade, maquina_id)}"


def validar_chave(chave: str, maquina_id: str) -> date | None:
    """Valida a assinatura da chave e retorna a data de validade.

    Retorna None se a chave for invalida (assinatura errada, formato ruim
    ou vínculo com outra maquina).
    """
    chave = chave.strip().upper().replace(" ", "")
    if len(chave) != 14 or chave[8] != "-":
        return None
    try:
        validade = datetime.strptime(chave[:8], "%Y%m%d").date()
    except ValueError:
        return None
    if not hmac.compare_digest(_checksum(validade, maquina_id), chave[9:]):
        return None
    return validade


class LicencaService:
    """Coordena trial e chave de licenca usando a tabela de configuracoes."""

    def __init__(self, repository: ConfiguracaoRepository) -> None:
        self._repo = repository

    def verificar(self) -> StatusLicenca:
        hoje = date.today()
        maquina_id = obter_maquina_id()

        config_chave = self._repo.get(CHAVE_LICENCA)
        if config_chave and config_chave.valor:
            validade = validar_chave(config_chave.valor, maquina_id)
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
        """Valida e registra a chave. Retorna True se aceita nesta maquina."""
        maquina_id = obter_maquina_id()
        validade = validar_chave(chave, maquina_id)
        if validade is None:
            return False
        self._repo.set(
            Configuracao(
                chave=CHAVE_LICENCA,
                valor=chave.strip().upper(),
                descricao=f"Chave de licenca valida ate {validade.isoformat()} (maquina {maquina_id})",
            )
        )
        return True
