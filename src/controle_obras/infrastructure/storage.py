"""Gerenciamento de diretórios e caminhos internos do sistema."""

import hashlib
from pathlib import Path


class AppStorage:
    """Centraliza os caminhos internos usados pelo sistema."""

    def __init__(self, base_dir: Path | str = ".") -> None:
        self.base_dir = Path(base_dir).resolve()
        self.data_dir = self.base_dir / "data"
        self.storage_dir = self.base_dir / "storage"
        self.anexos_dir = self.storage_dir / "anexos"
        self.reports_dir = self.base_dir / "reports"
        self.obras_reports_dir = self.reports_dir / "obras"

        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for directory in (
            self.data_dir,
            self.storage_dir,
            self.anexos_dir,
            self.obras_reports_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def db_path(self) -> Path:
        return self.data_dir / "app.db"

    def anexo_path(self, obra_codigo: str, relative_path: str) -> Path:
        return self.anexos_dir / relative_path

    def relatorio_path(self, filename: str) -> Path:
        return self.obras_reports_dir / filename

    def anexo_relative_path(
        self, obra_codigo: str, lancamento_id: int | None, original_name: str
    ) -> str:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_original = Path(original_name).name
        # Sanitiza o código da obra para impedir path traversal
        safe_codigo = "".join(
            c for c in obra_codigo if c.isalnum() or c in "._-"
        ).strip(".")
        if not safe_codigo:
            safe_codigo = "SEM_CODIGO"
        if lancamento_id:
            relative = f"OBRA_{safe_codigo}/lancamentos/LANC_{lancamento_id:04d}/{timestamp}_{safe_original}"
        else:
            relative = f"OBRA_{safe_codigo}/obra/{timestamp}_{safe_original}"
        return relative


class FileHasher:
    """Utilitário para calcular hash de arquivos."""

    @staticmethod
    def sha256_file(path: Path) -> str:
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def sha256_bytes(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
