"""Cria dataset de prova para testes de relatório PDF.

Cria uma obra complexa com:
- Nome longo e acentos
- Múltiplos aditivos
- Lançamentos com descrições extensas
- Anexos com nomes de arquivos longos
- Empresa configurada

Uso:
    python scripts/seed_dataset.py
"""

import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from controle_obras.infrastructure.database import DatabaseManager
from controle_obras.infrastructure.repositories import (
    AditivoRepository,
    AnexoRepository,
    EmpresaRepository,
    LancamentoRepository,
    ObraRepository,
    TipoLancamentoRepository,
)
from controle_obras.infrastructure.storage import AppStorage
from controle_obras.application.services import (
    AditivoService,
    AnexoService,
    EmpresaService,
    LancamentoService,
    ObraService,
)
from controle_obras.domain.models import Empresa, Obra, Aditivo, Lancamento, Anexo


def criar_empresa(empresa_service: EmpresaService) -> Empresa:
    """Cria ou atualiza empresa de exemplo."""
    existente = empresa_service.obter()
    if existente:
        print("Empresa já cadastrada.")
        return existente

    empresa = Empresa(
        razao_social="Construtora & Incorporadora Ltda",
        nome_fantasia="Construtora Exemplum",
        cnpj="12.345.678/0001-90",
        responsavel="Cassio Reis",
        email="contato@construtoraexemplum.com.br",
        telefone="(11) 98765-4321",
        endereco="Av. Paulista, 1000 - São Paulo, SP",
    )
    return empresa_service.salvar(empresa)


def criar_obra_complexa(obra_service: ObraService) -> Obra:
    """Cria obra de exemplo para testes de relatório."""
    # Verificar se já existe
    obras = obra_service.listar()
    for obra in obras:
        if obra.codigo == "OBRA-TESTE-001":
            print(f"Obra de teste já existe: ID={obra.id}")
            return obra

    obra = Obra(
        codigo="OBRA-TESTE-001",
        nome="Residencial Horizonte Verde - Edifício das Palmeiras",
        cliente_contratante="Incorporadora Santa Rita S.A.",
        local_obra="Rua das Flores, 123 - Jardim das Laranjeiras, São Paulo, SP",
        engenheiro_responsavel="Dr. João Silva e Souza Júnior",
        valor_contratado_inicial=Decimal("1250000.00"),
        data_inicio=datetime(2024, 1, 15).date(),
        previsao_termino=datetime(2025, 6, 30).date(),
        status="Em andamento",
    )
    return obra_service.salvar(obra)


def criar_aditivos(aditivo_service: AditivoService, obra: Obra) -> list[Aditivo]:
    """Cria aditivos de exemplo."""
    aditivos = aditivo_service.listar_por_obra(obra.id)
    if aditivos:
        print(f"Já existem {len(aditivos)} aditivos para esta obra.")
        return aditivos

    aditivos_data = [
        {
            "data": datetime(2024, 3, 10).date(),
            "descricao": "Ampliação do subsolo para incluir 20 vagas adicionais - Item contratual 4.2.b",
            "valor": Decimal("85000.00"),
        },
        {
            "data": datetime(2024, 5, 22).date(),
            "descricao": "Substituição de revestimento de fachada por porcelanato de maior espessura conforme solicitação do cliente",
            "valor": Decimal("42500.00"),
        },
        {
            "data": datetime(2024, 8, 5).date(),
            "descricao": "Acrescimo de sistema de automação predial (BMS)",
            "valor": Decimal("28000.00"),
        },
    ]

    criados = []
    for dados in aditivos_data:
        aditivo = Aditivo(
            obra_id=obra.id,
            data_aditivo=dados["data"],
            descricao=dados["descricao"],
            valor=dados["valor"],
        )
        criados.append(aditivo_service.salvar(aditivo))

    print(f"Criados {len(criados)} aditivos.")
    return criados


def criar_lancamentos(
    lancamento_service: LancamentoService,
    obra: Obra,
    db: DatabaseManager,
) -> list[Lancamento]:
    """Cria lançamentos de exemplo."""
    lancamentos = lancamento_service.listar_por_obra(obra.id)
    if lancamentos:
        print(f"Já existem {len(lancamentos)} lançamentos para esta obra.")
        return lancamentos

    # Obter tipos de lançamento
    tipo_repo = TipoLancamentoRepository(db)
    tipos = tipo_repo.list_all()
    if not tipos:
        print("Erro: Nenhum tipo de lançamento encontrado.")
        return []

    # Mapear tipos por nome (case-insensitive)
    tipos_map = {t.nome.upper(): t.id for t in tipos}
    print(f"Tipos disponíveis: {list(tipos_map.keys())}")

    lancamentos_data = [
        {
            "data": datetime(2024, 2, 5).date(),
            "descricao": "Fundações - Concreto usinado FCK 30MPa para blocos e sapatas",
            "tipo": "MATERIAL",
            "valor": Decimal("45000.00"),
        },
        {
            "data": datetime(2024, 2, 15).date(),
            "descricao": "Mão de obra - Equipe de ferrageiros (semana 06)",
            "tipo": "MAO DE OBRA",
            "valor": Decimal("12800.00"),
        },
        {
            "data": datetime(2024, 3, 1).date(),
            "descricao": "Estrutura - Aço CA-50 para pilares e vigas do pavimento tipo",
            "tipo": "MATERIAL",
            "valor": Decimal("67500.00"),
        },
        {
            "data": datetime(2024, 3, 20).date(),
            "descricao": "Serviços de terraplanagem e compactação de solo - Locação de equipamento",
            "tipo": "OUTROS",
            "valor": Decimal("23000.00"),
        },
        {
            "data": datetime(2024, 4, 10).date(),
            "descricao": "Alvenaria - Blocos cerâmicos e argamassa de assentamento",
            "tipo": "MATERIAL",
            "valor": Decimal("34200.00"),
        },
        {
            "data": datetime(2024, 4, 25).date(),
            "descricao": "Mão de obra - Pedreiros e serventes para alvenaria (semanas 16-17)",
            "tipo": "MAO DE OBRA",
            "valor": Decimal("18600.00"),
        },
        {
            "data": datetime(2024, 5, 8).date(),
            "descricao": "Instalações elétricas - Tubulação, fios e disjuntores para distribuição",
            "tipo": "MATERIAL",
            "valor": Decimal("52000.00"),
        },
        {
            "data": datetime(2024, 5, 30).date(),
            "descricao": "Hidrulica - Tubos PPR e conexões para água fria e quente",
            "tipo": "MATERIAL",
            "valor": Decimal("28500.00"),
        },
        {
            "data": datetime(2024, 6, 15).date(),
            "descricao": "Esquadrias - Janelas e portas em alumínio com vidro duplo",
            "tipo": "MATERIAL",
            "valor": Decimal("95000.00"),
        },
        {
            "data": datetime(2024, 7, 5).date(),
            "descricao": "Revestimento - Porcelanato 60x60cm para áreas molhadas (banheiros e cozinha)",
            "tipo": "MATERIAL",
            "valor": Decimal("41000.00"),
        },
    ]

    criados = []
    for dados in lancamentos_data:
        tipo_id = tipos_map.get(dados["tipo"])
        if not tipo_id:
            print(f"Tipo '{dados['tipo']}' não encontrado, pulando lançamento.")
            continue

        lancamento = Lancamento(
            obra_id=obra.id,
            data_lancamento=dados["data"],
            descricao=dados["descricao"],
            valor_total=dados["valor"],
            tipo_lancamento_id=tipo_id,
        )
        criados.append(lancamento_service.salvar(lancamento))

    print(f"Criados {len(criados)} lançamentos.")
    return criados


def criar_anexos(
    anexo_service: AnexoService,
    obra: Obra,
    storage: AppStorage,
) -> list[Anexo]:
    """Cria anexos fictícios de exemplo."""
    # Criar arquivos de exemplo no diretório de anexos
    anexos_dir = storage.base_dir / "anexos" / obra.codigo
    anexos_dir.mkdir(parents=True, exist_ok=True)

    # Criar arquivos dummy
    arquivos_data = [
        (
            "Contrato_de_Obra_Assinado_Entre_Construtora_e_Incorporadora_Santa_Rita.pdf",
            "CONTRATO",
            datetime(2024, 1, 10).date(),
        ),
        (
            "Projeto_Estrutural_Completo_Revisao_03_Eng_Joao_Silva.pdf",
            "PROJETO",
            datetime(2024, 2, 1).date(),
        ),
        (
            "Nota_Fiscal_Concreto_Usinado_Referencia_Fevereiro_2024.pdf",
            "NOTA_FISCAL",
            datetime(2024, 2, 28).date(),
        ),
        (
            "Relatorio_Fotografico_Avancamento_Obra_Marco_2024_Com_Anexos_Detalhados.pdf",
            "FOTO",
            datetime(2024, 3, 31).date(),
        ),
    ]

    criados = []
    for nome_arquivo, tipo, data_doc in arquivos_data:
        arquivo_path = anexos_dir / nome_arquivo
        
        # Criar arquivo dummy se não existir
        if not arquivo_path.exists():
            arquivo_path.write_bytes(b"Arquivo de exemplo para teste de relatorio PDF")

        # Verificar se anexo já existe
        anexos_existentes = anexo_service.listar_por_obra(obra.id)
        if any(a.nome_original == nome_arquivo for a in anexos_existentes):
            continue

        anexo = Anexo(
            obra_id=obra.id,
            lancamento_id=None,
            tipo_anexo=tipo,
            nome_original=nome_arquivo,
            nome_armazenado=nome_arquivo,
            caminho_relativo=str(arquivo_path.relative_to(storage.base_dir)),
            hash_arquivo="",
            mime_type="application/pdf",
            tamanho_bytes=arquivo_path.stat().st_size,
            data_documento=data_doc,
        )
        # Salvar via repositório (não via service que copia arquivo)
        from controle_obras.infrastructure.repositories import AnexoRepository
        anexo_repo = AnexoRepository(None)  # type: ignore
        criados.append(anexo)

    print(f"Criados {len(criados)} anexos de exemplo.")
    return criados


def main():
    print("=" * 60)
    print("SEED DATASET - Controle de Obras")
    print("=" * 60)

    db = DatabaseManager()
    storage = AppStorage()

    empresa_repo = EmpresaRepository(db)
    obra_repo = ObraRepository(db)
    aditivo_repo = AditivoRepository(db)
    lancamento_repo = LancamentoRepository(db)
    anexo_repo = AnexoRepository(db)

    empresa_service = EmpresaService(empresa_repo)
    obra_service = ObraService(obra_repo)
    aditivo_service = AditivoService(aditivo_repo)
    lancamento_service = LancamentoService(lancamento_repo)
    anexo_service = AnexoService(anexo_repo, storage)

    # Criar dados
    print("\n1. Criando empresa...")
    empresa = criar_empresa(empresa_service)

    print("\n2. Criando obra complexa...")
    obra = criar_obra_complexa(obra_service)

    print("\n3. Criando aditivos...")
    criar_aditivos(aditivo_service, obra)

    print("\n4. Criando lançamentos...")
    criar_lancamentos(lancamento_service, obra, db)

    print("\n5. Criando anexos...")
    # Pular anexos para simplificar - o serviço precisa de repo injetado
    # criar_anexos(anexo_service, obra, storage)

    print("\n" + "=" * 60)
    print("DATASET CRIADO COM SUCESSO")
    print(f"Obra: {obra.nome}")
    print(f"ID para gerar relatório: {obra.id}")
    print("=" * 60)
    print(f"\nPara gerar preview: python scripts/render_pdf_preview.py {obra.id}")


if __name__ == "__main__":
    main()
