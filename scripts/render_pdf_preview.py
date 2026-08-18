"""Renderiza PDF do relatório para PNG para revisão visual.

Uso:
    python scripts/render_pdf_preview.py [obra_id] [--gerador reportlab|xhtml2pdf|docx]

Saída: artifacts/pdf_review/<timestamp>/paginas_*.png
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fitz  # pymupdf

from controle_obras.infrastructure.database import DatabaseManager
from controle_obras.infrastructure.repositories import (
    AditivoRepository,
    AnexoRepository,
    EmpresaRepository,
    LancamentoRepository,
    ObraRepository,
    RelatorioRepository,
    TipoLancamentoRepository,
)
from controle_obras.infrastructure.storage import AppStorage
from controle_obras.application.services import (
    AditivoService,
    AnexoService,
    EmpresaService,
    LancamentoService,
    ObraResumoService,
    ObraService,
    RelatorioPDFService,
)


def setup_services():
    """Configura todos os serviços necessários."""
    db = DatabaseManager()
    storage = AppStorage()

    obra_repo = ObraRepository(db)
    aditivo_repo = AditivoRepository(db)
    lancamento_repo = LancamentoRepository(db)
    anexo_repo = AnexoRepository(db)
    relatorio_repo = RelatorioRepository(db)
    empresa_repo = EmpresaRepository(db)

    obra_service = ObraService(obra_repo)
    aditivo_service = AditivoService(aditivo_repo)
    lancamento_service = LancamentoService(lancamento_repo)
    anexo_service = AnexoService(anexo_repo, storage)
    resumo_service = ObraResumoService(obra_repo, aditivo_repo, lancamento_repo)
    empresa_service = EmpresaService(empresa_repo)

    relatorio_service = RelatorioPDFService(
        obra_service=obra_service,
        aditivo_service=aditivo_service,
        lancamento_service=lancamento_service,
        anexo_service=anexo_service,
        resumo_service=resumo_service,
        relatorio_repo=relatorio_repo,
        storage=storage,
        empresa_service=empresa_service,
    )

    return relatorio_service, obra_service


def render_pdf_to_png(pdf_path: Path, output_dir: Path, dpi: int = 150) -> list[Path]:
    """Renderiza cada página do PDF para PNG.

    Args:
        pdf_path: Caminho do PDF.
        output_dir: Diretório de saída.
        dpi: Resolução da renderização.

    Returns:
        Lista de caminhos dos PNGs gerados.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    png_paths = []

    zoom = dpi / 72  # 72 dpi é a resolução base do PDF
    mat = fitz.Matrix(zoom, zoom)

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=mat)

        png_path = output_dir / f"pagina_{page_num + 1:02d}.png"
        pix.save(str(png_path))
        png_paths.append(png_path)
        print(f"  Renderizada pagina {page_num + 1}/{len(doc)} -> {png_path.name}")

    doc.close()
    return png_paths


def listar_obras_disponiveis(obra_service: ObraService) -> None:
    """Lista obras disponíveis no banco."""
    obras = obra_service.listar()
    if not obras:
        print("Nenhuma obra encontrada no banco.")
        return

    print("\nObras disponíveis:")
    for obra in obras:
        print(f"  ID={obra.id} | Código={obra.codigo} | {obra.nome}")


def main():
    parser = argparse.ArgumentParser(
        description="Renderiza relatório PDF para PNG para revisão visual."
    )
    parser.add_argument(
        "obra_id",
        nargs="?",
        type=int,
        default=None,
        help="ID da obra para gerar relatório (padrão: lista disponíveis)",
    )
    parser.add_argument(
        "--gerador",
        choices=["reportlab", "xhtml2pdf"],
        default="reportlab",
        help="Gerador a usar (padrao: reportlab). xhtml2pdf usa o metodo legacy.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Resolução da renderização em DPI (padrão: 150)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("RENDER PDF PREVIEW - Controle de Obras")
    print("=" * 60)

    relatorio_service, obra_service = setup_services()

    if args.obra_id is None:
        listar_obras_disponiveis(obra_service)
        print("\nUso: python scripts/render_pdf_preview.py <obra_id> [--gerador reportlab]")
        return

    # Verificar se obra existe
    obra = obra_service.obter(args.obra_id)
    if not obra:
        print(f"Erro: Obra ID={args.obra_id} não encontrada.")
        listar_obras_disponiveis(obra_service)
        sys.exit(1)

    print(f"\nObra: {obra.nome} (Código: {obra.codigo})")
    print(f"Gerador: {args.gerador}")
    print(f"DPI: {args.dpi}")

    # Gerar PDF usando metodo canonico (ReportLab)
    print("\nGerando PDF (gerador: reportlab)...")
    try:
        pdf_path = relatorio_service.gerar_relatorio_obra(args.obra_id)

        print(f"PDF gerado: {pdf_path}")
        print(f"Tamanho: {pdf_path.stat().st_size:,} bytes")

    except Exception as e:
        print(f"ERRO ao gerar PDF: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Renderizar para PNG
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent.parent / "artifacts" / "pdf_review" / timestamp
    print(f"\nRenderizando PNGs em: {output_dir}")

    png_paths = render_pdf_to_png(pdf_path, output_dir, dpi=args.dpi)

    print("\n" + "=" * 60)
    print(f"CONCLUÍDO: {len(png_paths)} página(s) renderizada(s)")
    print(f"Diretório: {output_dir}")
    print("=" * 60)

    # Abrir explorador no diretório
    os.startfile(str(output_dir))


if __name__ == "__main__":
    main()
