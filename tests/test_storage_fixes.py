"""Testes de regressão para o fix de colisão de nomes de anexos em storage."""

from pathlib import Path

import pytest

from controle_obras.infrastructure.storage import AppStorage, FileHasher


@pytest.fixture
def storage(tmp_path: Path) -> AppStorage:
    return AppStorage(tmp_path)


class TestColisaoNomesAnexos:
    """Valida que dois anexos iguais anexados no mesmo segundo não sobrescrevem."""

    def test_dois_anexos_iguais_geram_caminhos_distintos(self, storage: AppStorage) -> None:
        relativo1 = storage.anexo_relative_path("OBRA-001", None, "arquivo.pdf")
        relativo2 = storage.anexo_relative_path("OBRA-001", None, "arquivo.pdf")
        assert relativo1 != relativo2

    def test_nome_original_e_prefixo_obras_preservados(self, storage: AppStorage) -> None:
        relativo = storage.anexo_relative_path("OBRA-001", None, "arquivo.pdf")
        assert relativo.endswith("arquivo.pdf")
        assert "OBRA_OBRA-001" in relativo

    def test_anexo_de_lancamento_mantem_estrutura(self, storage: AppStorage) -> None:
        relativo = storage.anexo_relative_path("OBRA-001", 3, "nota.pdf")
        assert "lancamentos" in relativo
        assert "LANC_0003" in relativo
        assert relativo.endswith("nota.pdf")

    def test_anexo_do_obra_nao_usa_pasta_de_lancamento(self, storage: AppStorage) -> None:
        relativo = storage.anexo_relative_path("OBRA-001", None, "arquivo.pdf")
        assert "lancamentos" not in relativo
        assert "/obra/" in relativo

    def test_hash_do_arquivo_gravado_no_diretorio_gerado(self, storage: AppStorage, tmp_path: Path) -> None:
        origem = tmp_path / "foto.png"
        origem.write_bytes(b"conteudo-do-arquivo")

        relativo = storage.anexo_relative_path("OBRA-001", None, "foto.png")
        destino = storage.anexo_path("OBRA-001", relativo)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(b"conteudo-do-arquivo")

        assert FileHasher.sha256_file(destino) == FileHasher.sha256_bytes(b"conteudo-do-arquivo")
