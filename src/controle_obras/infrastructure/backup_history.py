"""Histórico e auditoria de operações de backup e restauração."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class BackupHistory:
    """Registra eventos de backup e restauração em arquivo JSON local."""

    def __init__(self, base_dir: Path | str = "data") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.base_dir / "backup_history.json"

    def _load(self) -> list[dict[str, Any]]:
        if not self.history_file.exists():
            return []
        try:
            return json.loads(self.history_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("Arquivo de histórico corrompido. Iniciando novo histórico.")
            return []

    def _save(self, entries: list[dict[str, Any]]) -> None:
        self.history_file.write_text(
            json.dumps(entries, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def registrar(
        self,
        operacao: str,
        status: str,
        detalhes: dict[str, Any] | None = None,
    ) -> None:
        entries = self._load()
        entry = {
            "id": len(entries) + 1,
            "timestamp": datetime.now().isoformat(),
            "operacao": operacao,
            "status": status,
            "detalhes": detalhes or {},
        }
        entries.append(entry)
        self._save(entries)
        logger.info("Histórico: %s - %s", operacao, status)

    def listar(self, limite: int = 50) -> list[dict[str, Any]]:
        entries = self._load()
        return sorted(entries, key=lambda x: x["timestamp"], reverse=True)[:limite]
