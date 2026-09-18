"""Servico de licenciamento COM SEGURANCA AVANCADA.

Nivel 3 de protecao:
- Vinculo forte a maquina (MachineGuid + MAC + hostname)
- Verificacao de integridade do banco de dados
- Protecao contra manipulacao de configuracoes
- Registro de tentativas de fraude
- Bloqueio apos multiplas tentativas invalidas
- Ofuscao avancada do segredo
"""

import hashlib
import hmac
import json
import os
import platform
import sqlite3
import time
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Literal

from controle_obras.domain.models import Configuracao
from controle_obras.infrastructure.repositories import ConfiguracaoRepository

# ==========================================
# SEGREDO OFUSCADO (compilado no executavel)
# ==========================================

# Segredo dividido em partes para dificultar extracao
_PARTE1 = bytes.fromhex("43306e7472306c652d3062723473")
_PARTE2 = bytes.fromhex("2d4c3163336e63342d3230323621402324")
SECRETO_LICENCA = (_PARTE1 + _PARTE2).decode("utf-8")

# Segredo adicional para verificacao de integridade
_SEGREDO_INTEGRIDADE = "CONTROLE-OBRAS-INTEGRITY-CHECK-2026"

# ==========================================
# CONFIGURACOES DE SEGURANCA
# ==========================================

TRIAL_DIAS = 7
TRIAL_AVISO_DIAS = 7
MAX_TENTATIVAS_FALHA = 5
BLOQUEIO_MINUTOS = 30

# Chaves de configuracao
CHAVE_PRIMEIRO_USO = "licenca_primeiro_uso"
CHAVE_LICENCA = "licenca_chave"
CHAVE_TENTATIVAS_FALHA = "licenca_tentativas_falha"
CHAVE_BLOQUEIO_ATE = "licenca_bloqueio_ate"
CHAVE_HASH_INTEGRIDADE = "licenca_hash_integridade"
CHAVE_MAQUINA_REGISTRADA = "licenca_maquina_registrada"
CHAVE_DATA_ATIVACAO = "licenca_data_ativacao"
CHAVEULTIMA_VERIFICACAO = "licenca_ultima_verificacao"

TipoStatus = Literal[
    "LICENCIADO",
    "EM_TRIAL",
    "TRIAL_EXPIRADO",
    "CHAVE_INVALIDA",
    "CHAVE_EXPIRADA",
    "BLOQUEADO",
    "MAQUINA_INCORRETA",
    "INTEGRIDADE_COMPROMETIDA",
]


# ==========================================
# IDENTIFICACAO DA MAQUINA (MAIS ROBUSTA)
# ==========================================

def _obter_machineguid() -> str:
    """Obtem MachineGuid do Windows (identificador unico da maquina)."""
    if os.name != "nt":
        return ""
    
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
        ) as chave:
            valor, _ = winreg.QueryValueEx(chave, "MachineGuid")
            return valor
    except (OSError, FileNotFoundError):
        return ""


def _obter_mac_address() -> str:
    """Obtem endereco MAC da placa de rede."""
    mac = uuid.getnode()
    return ':'.join(f'{(mac >> i) & 0xff:02x}' for i in range(0, 48, 8))


def _obter_hostname() -> str:
    """Obtem nome da maquina."""
    return platform.node()


def _obter_disk_serial() -> str:
    """Obtem serial do disco rigido (Windows)."""
    if os.name != "nt":
        return ""
    
    try:
        import subprocess
        resultado = subprocess.run(
            ["wmic", "diskdrive", "get", "serialnumber"],
            capture_output=True,
            text=True,
            timeout=5
        )
        linhas = resultado.stdout.strip().split('\n')
        if len(linhas) > 1:
            return linhas[1].strip()
    except Exception:
        pass
    return ""


def obter_maquina_id() -> str:
    """Gera ID composto da maquina (mais dificil de falsificar)."""
    componentes = []
    
    # Componente 1: MachineGuid (principal)
    machineguid = _obter_machineguid()
    if machineguid:
        componentes.append(f"MG:{machineguid}")
    
    # Componente 2: MAC address
    mac = _obter_mac_address()
    componentes.append(f"MAC:{mac}")
    
    # Componente 3: Hostname
    hostname = _obter_hostname()
    componentes.append(f"HOST:{hostname}")
    
    # Componente 4: Serial do disco (opcional)
    disk_serial = _obter_disk_serial()
    if disk_serial:
        componentes.append(f"DISK:{disk_serial}")
    
    if not componentes:
        # Fallback fraco
        componentes.append(f"FALLBACK:{uuid.getnode()}")
    
    # Combina todos os componentes
    payload = "|".join(sorted(componentes))
    return _hash_of(payload)


def _hash_of(texto: str) -> str:
    """Gera hash seguro e deterministico."""
    # Usa SHA-256 com salt personalizado
    salted = f"{_SEGREDO_INTEGRIDADE}:{texto}:{_SEGREDO_INTEGRIDADE}"
    return hashlib.sha256(salted.encode("utf-8")).hexdigest()[:8].upper()


# ==========================================
# GERACAO E VALIDACAO DE CHAVES
# ==========================================

def _checksum(validade: date, maquina_id: str) -> str:
    """Gera checksum HMAC robusto."""
    payload = f"CONTROLE-OBRAS|{validade.isoformat()}|{maquina_id}|v2"
    digest = hmac.new(
        SECRETO_LICENCA.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest[:6].upper()


def gerar_chave(validade: date, maquina_id: str) -> str:
    """Gera chave de licenca com formatao avancada.
    
    Formato: YYYYMMDD-XXXXXX (data + checksum de 6 caracteres)
    """
    return f"{validade.strftime('%Y%m%d')}-{_checksum(validade, maquina_id)}"


def validar_chave(chave: str, maquina_id: str) -> date | None:
    """Valida chave com multiplas verificacoes.
    
    Retorna data de validade se valida, None caso contrario.
    """
    # Normalizacao
    chave = chave.strip().upper().replace(" ", "").replace("-", "")
    
    # Verificacao de formato: 8 digitos + 6 caracteres = 14 caracteres
    if len(chave) != 14:
        return None
    
    # Separar data e checksum
    parte_data = chave[:8]
    parte_checksum = chave[8:]
    
    # Validar data
    try:
        validade = datetime.strptime(parte_data, "%Y%m%d").date()
    except ValueError:
        return None
    
    # Validar checksum
    checksum_esperado = _checksum(validade, maquina_id)
    if not hmac.compare_digest(checksum_esperado, parte_checksum):
        return None
    
    # Validar que a data nao e muito distante (max 10 anos)
    hoje = date.today()
    dias_diferenca = (validade - hoje).days
    if dias_diferenca > 3650:  # 10 anos
        return None
    
    return validade


# ==========================================
# VERIFICACAO DE INTEGRIDADE
# ==========================================

def _calcular_hash_integridade(db_path: Path) -> str:
    """Calcula hash de integridade do banco de dados."""
    if not db_path.exists():
        return ""
    
    try:
        # Le apenas metadados criticos (nao dados sensiveis)
        with sqlite3.connect(str(db_path)) as conn:
            # Verifica se tabela existe
            tabelas = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            
            # Conta registros criticos
            configs = conn.execute("SELECT COUNT(*) FROM configuracoes").fetchone()[0]
            
            # Hash composto
            payload = f"tabelas:{len(tabelas)}|configs:{configs}|{_SEGREDO_INTEGRIDADE}"
            return hashlib.sha256(payload.encode()).hexdigest()[:16]
    except Exception:
        return ""


def _verificar_integridade(repo: ConfiguracaoRepository, db_path: Path) -> bool:
    """Verifica integridade do banco de dados."""
    config_hash = repo.get(CHAVE_HASH_INTEGRIDADE)
    
    if not config_hash or not config_hash.valor:
        # Primeira execucao - registra hash
        hash_atual = _calcular_hash_integridade(db_path)
        if hash_atual:
            repo.set(Configuracao(
                chave=CHAVE_HASH_INTEGRIDADE,
                valor=hash_atual,
                descricao="Hash de integridade do banco"
            ))
        return True
    
    # Verifica se hash ainda e valido
    hash_atual = _calcular_hash_integridade(db_path)
    return hash_atual == config_hash.valor


# ==========================================
# CONTROLE DE TENTATIVAS
# ==========================================

class ControleTentativas:
    """Gerencia tentativas de autenticacao."""
    
    def __init__(self, repo: ConfiguracaoRepository):
        self._repo = repo
    
    def registrar_tentativa_falha(self) -> int:
        """Registra tentativa falha e retorna total."""
        config = self._repo.get(CHAVE_TENTATIVAS_FALHA)
        total = int(config.valor) + 1 if config and config.valor else 1
        
        self._repo.set(Configuracao(
            chave=CHAVE_TENTATIVAS_FALHA,
            valor=str(total),
            descricao=f"Tentativas falha: {total}"
        ))
        
        # Se atingiu limite, bloqueia
        if total >= MAX_TENTATIVAS_FALHA:
            self._bloquear()
        
        return total
    
    def _bloquear(self) -> None:
        """Bloqueia o sistema por tempo determinado."""
        from datetime import timedelta
        ate = datetime.now() + timedelta(minutes=BLOQUEIO_MINUTOS)
        
        self._repo.set(Configuracao(
            chave=CHAVE_BLOQUEIO_ATE,
            valor=ate.isoformat(),
            descricao=f"Bloqueado ate {ate}"
        ))
    
    def esta_bloqueado(self) -> bool:
        """Verifica se esta bloqueado."""
        config = self._repo.get(CHAVE_BLOQUEIO_ATE)
        if not config or not config.valor:
            return False
        
        try:
            ate = datetime.fromisoformat(config.valor)
            if datetime.now() < ate:
                return True
            # Bloqueio expirou - reseta
            self._repo.set(Configuracao(
                chave=CHAVE_BLOQUEIO_ATE,
                valor="",
                descricao="Bloqueio expirado"
            ))
            self._repo.set(Configuracao(
                chave=CHAVE_TENTATIVAS_FALHA,
                valor="0",
                descricao="Tentativas resetadas"
            ))
            return False
        except ValueError:
            return False
    
    def resetar(self) -> None:
        """Reseta contador de tentativas."""
        self._repo.set(Configuracao(
            chave=CHAVE_TENTATIVAS_FALHA,
            valor="0",
            descricao="Reset manual"
        ))
        self._repo.set(Configuracao(
            chave=CHAVE_BLOQUEIO_ATE,
            valor="",
            descricao="Bloqueio removido"
        ))
    
    def obter_tentativas(self) -> int:
        """Retorna numero de tentativas."""
        config = self._repo.get(CHAVE_TENTATIVAS_FALHA)
        return int(config.valor) if config and config.valor else 0


# ==========================================
# STATUS DA LICENCA
# ==========================================

class StatusLicenca:
    """Resultado detalhado da verificacao."""
    
    def __init__(
        self,
        tipo: TipoStatus,
        dias_restantes: int | None = None,
        mensagem: str = "",
        tentativas: int = 0,
    ) -> None:
        self.tipo = tipo
        self.dias_restantes = dias_restantes
        self.mensagem = mensagem
        self.tentativas = tentativas
    
    @property
    def pode_usar(self) -> bool:
        """True se o usuario pode usar o sistema."""
        return self.tipo in ("LICENCIADO", "EM_TRIAL")


# ==========================================
# SERVICO PRINCIPAL
# ==========================================

class LicencaService:
    """Servico de licenciamento com seguranca avancada."""
    
    def __init__(
        self,
        repository: ConfiguracaoRepository,
        db_path: Path | None = None,
    ) -> None:
        self._repo = repository
        self._db_path = db_path or Path("data/app.db")
        self._controle = ControleTentativas(repository)
    
    def verificar(self) -> StatusLicenca:
        """Verificacao completa de licenca."""
        # 1. Verificar bloqueio
        if self._controle.esta_bloqueado():
            tentativas = self._controle.obter_tentativas()
            return StatusLicenca(
                "BLOQUEADO",
                tentativas=tentativas,
                mensagem=f"Sistema bloqueado apos {tentativas} tentativas invalidas. Aguarde {BLOQUEIO_MINUTOS} minutos."
            )
        
        # 2. Verificar integridade
        if not _verificar_integridade(self._repo, self._db_path):
            return StatusLicenca(
                "INTEGRIDADE_COMPROMETIDA",
                mensagem="Banco de dados violado. Contate o suporte."
            )
        
        # 3. Obter maquina
        maquina_id = obter_maquina_id()
        
        # 4. Verificar chave existente
        config_chave = self._repo.get(CHAVE_LICENCA)
        if config_chave and config_chave.valor:
            return self._verificar_chave_existente(config_chave, maquina_id)
        
        # 5. Verificar trial
        return self._verificar_trial()
    
    def _verificar_chave_existente(
        self,
        config_chave: Configuracao,
        maquina_id: str,
    ) -> StatusLicenca:
        """Verifica chave ja registrada."""
        chave = config_chave.valor
        hoje = date.today()
        
        # Validar chave
        validade = validar_chave(chave, maquina_id)
        
        if validade is None:
            # Chave invalida - pode ser de outra maquina
            # Verificar se e de outra maquina
            config_maquina = self._repo.get(CHAVE_MAQUINA_REGISTRADA)
            if config_maquina and config_maquina.valor != maquina_id:
                return StatusLicenca(
                    "MAQUINA_INCORRETA",
                    mensagem="Esta chave pertence a outra maquina."
                )
            return StatusLicenca(
                "CHAVE_INVALIDA",
                mensagem="Chave de licenca invalida."
            )
        
        # Chave valida - verificar validade
        if validade < hoje:
            return StatusLicenca(
                "CHAVE_EXPIRADA",
                dias_restantes=0,
                mensagem="Chave de licenca expirada."
            )
        
        # Atualizar ultima verificacao
        self._repo.set(Configuracao(
            chave=CHAVEULTIMA_VERIFICACAO,
            valor=hoje.isoformat(),
            descricao=f"Ultima verificacao: {hoje}"
        ))
        
        dias_restantes = (validade - hoje).days
        return StatusLicenca(
            "LICENCIADO",
            dias_restantes=dias_restantes,
            mensagem=f"Licenca valida por {dias_restantes} dias."
        )
    
    def _verificar_trial(self) -> StatusLicenca:
        """Verifica periodo de teste."""
        hoje = date.today()
        
        config_trial = self._repo.get(CHAVE_PRIMEIRO_USO)
        if not config_trial or not config_trial.valor:
            # Primeiro uso
            self._repo.set(Configuracao(
                chave=CHAVE_PRIMEIRO_USO,
                valor=hoje.isoformat(),
                descricao="Data do primeiro uso (inicio do periodo de teste)"
            ))
            return StatusLicenca(
                "EM_TRIAL",
                dias_restantes=TRIAL_DIAS,
                mensagem=f"Periodo de teste: {TRIAL_DIAS} dias restantes."
            )
        
        try:
            primeiro_uso = datetime.strptime(config_trial.valor, "%Y-%m-%d").date()
        except ValueError:
            primeiro_uso = hoje
        
        dias_usados = (hoje - primeiro_uso).days
        restantes = TRIAL_DIAS - dias_usados
        
        if restantes > 0:
            return StatusLicenca(
                "EM_TRIAL",
                dias_restantes=restantes,
                mensagem=f"Periodo de teste: {restantes} dias restantes."
            )
        
        return StatusLicenca(
            "TRIAL_EXPIRADO",
            dias_restantes=0,
            mensagem="Periodo de teste expirado. Adquira uma licenca."
        )
    
    def registrar_chave(self, chave: str) -> tuple[bool, str]:
        """Valida e registra chave com verificacoes extras.
        
        Retorna (sucesso, mensagem).
        """
        # 1. Verificar bloqueio
        if self._controle.esta_bloqueado():
            return False, "Sistema bloqueado. Aguarde."
        
        # 2. Normalizar chave
        chave = chave.strip().upper().replace(" ", "")
        
        # 3. Obter maquina
        maquina_id = obter_maquina_id()
        
        # 4. Validar chave
        validade = validar_chave(chave, maquina_id)
        
        if validade is None:
            # Registrar tentativa falha
            tentativas = self._controle.registrar_tentativa_falha()
            restantes = MAX_TENTATIVAS_FALHA - tentativas
            
            if restantes > 0:
                return False, f"Chave invalida. {restantes} tentativas restantes."
            else:
                return False, f"Limite de tentativas atingido. Sistema bloqueado por {BLOQUEIO_MINUTOS} minutos."
        
        # 5. Verificar se chave ja foi usada em outra maquina
        config_maquina = self._repo.get(CHAVE_MAQUINA_REGISTRADA)
        if config_maquina and config_maquina.valor:
            if config_maquina.valor != maquina_id:
                return False, "Esta chave ja foi utilizada em outra maquina."
        
        # 6. Registrar chave
        self._repo.set(Configuracao(
            chave=CHAVE_LICENCA,
            valor=chave,
            descricao=f"Chave de licenca valida ate {validade.isoformat()} (maquina {maquina_id})"
        ))
        
        # 7. Registrar maquina
        self._repo.set(Configuracao(
            chave=CHAVE_MAQUINA_REGISTRADA,
            valor=maquina_id,
            descricao=f"Maquina registrada: {maquina_id}"
        ))
        
        # 8. Registrar data de ativacao
        self._repo.set(Configuracao(
            chave=CHAVE_DATA_ATIVACAO,
            valor=date.today().isoformat(),
            descricao=f"Data de ativacao: {date.today()}"
        ))
        
        # 9. Resetar tentativas
        self._controle.resetar()
        
        return True, f"Licenca ativada com sucesso! Validade: {validade.strftime('%d/%m/%Y')}"
    
    def obter_info_licenca(self) -> dict:
        """Retorna informacoes detalhadas da licenca."""
        info = {
            "maquina_id": obter_maquina_id(),
            "data_ativacao": None,
            "data_validade": None,
            "dias_restantes": None,
            "status": None,
        }
        
        config_data = self._repo.get(CHAVE_DATA_ATIVACAO)
        if config_data and config_data.valor:
            info["data_ativacao"] = config_data.valor
        
        config_chave = self._repo.get(CHAVE_LICENCA)
        if config_chave and config_chave.valor:
            maquina_id = obter_maquina_id()
            validade = validar_chave(config_chave.valor, maquina_id)
            if validade:
                info["data_validade"] = validade.isoformat()
                info["dias_restantes"] = (validade - date.today()).days
                info["status"] = "ATIVO"
        
        return info
