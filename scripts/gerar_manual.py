"""Gera manual do sistema em PDF usando ReportLab."""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)

LARGURA, ALTURA = A4
MARGEM = 2 * cm
OUTPUT = Path(__file__).parent / "Manual_ControleDeObras_v1.0.5.pdf"

# ── Cores ──
AZUL = colors.HexColor("#1a5276")
AZUL_CLARO = colors.HexColor("#2980b9")
VERDE = colors.HexColor("#27ae60")
CINZA = colors.HexColor("#7f8c8d")
CINZA_CLARO = colors.HexColor("#f2f3f4")
PRETO = colors.HexColor("#2c3e50")


def build_styles():
    base = getSampleStyleSheet()
    return {
        "CapaTitulo": ParagraphStyle("CapaTitulo", parent=base["Title"],
            fontSize=28, textColor=AZUL, alignment=TA_CENTER, spaceAfter=8),
        "CapaSub": ParagraphStyle("CapaSub", parent=base["Normal"],
            fontSize=14, textColor=CINZA, alignment=TA_CENTER, spaceAfter=6),
        "H1": ParagraphStyle("H1", parent=base["Heading1"],
            fontSize=18, textColor=AZUL, spaceBefore=16, spaceAfter=8,
            borderWidth=0, borderPadding=0),
        "H2": ParagraphStyle("H2", parent=base["Heading2"],
            fontSize=14, textColor=AZUL_CLARO, spaceBefore=12, spaceAfter=6),
        "H3": ParagraphStyle("H3", parent=base["Heading3"],
            fontSize=12, textColor=PRETO, spaceBefore=8, spaceAfter=4),
        "Corpo": ParagraphStyle("Corpo", parent=base["Normal"],
            fontSize=10, textColor=PRETO, alignment=TA_JUSTIFY,
            leading=14, spaceAfter=6),
        "Item": ParagraphStyle("Item", parent=base["Normal"],
            fontSize=10, textColor=PRETO, leftIndent=18,
            leading=14, spaceAfter=3),
        "Dica": ParagraphStyle("Dica", parent=base["Normal"],
            fontSize=9, textColor=CINZA, leftIndent=18,
            leading=12, spaceAfter=6, fontName="Helvetica-Oblique"),
        "Rodape": ParagraphStyle("Rodape", parent=base["Normal"],
            fontSize=8, textColor=CINZA, alignment=TA_CENTER),
    }


def hr():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#bdc3c7"),
                       spaceBefore=6, spaceAfter=6)


def tabela_simples(dados, larguras=None):
    """Cria tabela com cabeçalho colorido."""
    t = Table(dados, colWidths=larguras, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d5d8dc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CINZA_CLARO]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def gerar_manual():
    estilos = build_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4,
        leftMargin=MARGEM, rightMargin=MARGEM,
        topMargin=MARGEM, bottomMargin=MARGEM,
        title="Manual do Usuário - Controle de Obras",
        author="CASSIO REIS TECH",
    )
    story = []

    def h1(t): story.append(Paragraph(t, estilos["H1"]))
    def h2(t): story.append(Paragraph(t, estilos["H2"]))
    def h3(t): story.append(Paragraph(t, estilos["H3"]))
    def p(t): story.append(Paragraph(t, estilos["Corpo"]))
    def item(t): story.append(Paragraph(f"• {t}", estilos["Item"]))
    def dica(t): story.append(Paragraph(f"💡 {t}", estilos["Dica"]))
    def sp(h=6): story.append(Spacer(1, h))
    def pg(): story.append(PageBreak())

    # ═══════════════════════════════════════════
    # CAPA
    # ═══════════════════════════════════════════
    sp(80)
    story.append(Paragraph("CONTROLE DE OBRAS", estilos["CapaTitulo"]))
    story.append(Paragraph("Manual do Usuário", estilos["CapaSub"]))
    sp(12)
    story.append(Paragraph("Versão 1.0.5", estilos["CapaSub"]))
    story.append(Paragraph("CASSIO REIS TECH", estilos["CapaSub"]))
    sp(40)
    story.append(Paragraph(
        "Sistema de gestão financeira e documental para obras da construção civil.",
        estilos["Corpo"]))
    story.append(Paragraph(
        "Controle completo de obras, lançamentos financeiros, aditivos, anexos e relatórios.",
        estilos["Corpo"]))
    pg()

    # ═══════════════════════════════════════════
    # SUMÁRIO
    # ═══════════════════════════════════════════
    h1("Sumário")
    story.append(hr())
    capitulos = [
        "1. Visão Geral do Sistema",
        "2. Primeiro Uso e Licença",
        "3. Cadastro da Empresa",
        "4. Obras (Contratos)",
        "5. Dashboard da Obra",
        "6. Lançamentos Financeiros",
        "7. Aditivos de Obra",
        "8. Anexos e Documentos",
        "9. Relatórios (PDF e DOCX)",
        "10. Backup e Restauração",
        "11. Segurança de Anexos",
        "12. Configurações",
        "13. Dicas e Boas Práticas",
    ]
    for c in capitulos:
        story.append(Paragraph(c, estilos["Item"]))
    pg()

    # ═══════════════════════════════════════════
    # 1. VISÃO GERAL
    # ═══════════════════════════════════════════
    h1("1. Visão Geral do Sistema")
    story.append(hr())
    p("O Controle de Obras é um sistema desktop para gerenciamento financeiro e documental de obras da construção civil. Ele permite:")
    sp()
    item("Cadastrar e gerenciar múltiplas obras (contratos)")
    item("Controlar lançamentos financeiros por obra (despesas e receitas)")
    item("Gerenciar aditivos contratuais")
    item("Anexar documentos (notas fiscais, comprovantes, planilhas, fotos)")
    item("Gerar relatórios profissionais em PDF e DOCX")
    item("Realizar backup e restauração completa dos dados")
    item("Auditar integridade dos anexos armazenados")
    sp()
    p("Todos os dados ficam armazenados localmente em <b>%APPDATA%\\ControleDeObras</b>, garantindo segurança e privacidade.")
    pg()

    # ═══════════════════════════════════════════
    # 2. PRIMEIRO USO E LICENÇA
    # ═══════════════════════════════════════════
    h1("2. Primeiro Uso e Licença")
    story.append(hr())
    h2("2.1 Período de Teste (Trial)")
    p("Na primeira execução, o sistema oferece um período de teste de <b>7 dias</b>. Após esse período, é necessário ativar uma licença.")
    sp()
    h2("2.2 Ativação da Licença")
    p("Ao abrir o sistema, uma janela exibe o <b>ID da máquina</b> (identificador único do computador). Siga os passos:")
    sp()
    item("Clique em <b>Copiar ID</b> para copiar o identificador")
    item("Envie o ID ao suporte técnico para gerar sua chave de licença")
    item("Cole a chave recebida no campo <b>Chave de licença</b>")
    item("Clique em <b>OK</b> para ativar")
    sp()
    dica("A licença é vinculada à máquina. Se trocar de computador, será necessário solicitar uma nova chave.")
    pg()

    # ═══════════════════════════════════════════
    # 3. CADASTRO DA EMPRESA
    # ═══════════════════════════════════════════
    h1("3. Cadastro da Empresa")
    story.append(hr())
    p("Na primeira execução (após ativar a licença), o sistema direciona para o cadastro da empresa responsável pelas obras.")
    sp()
    h2("3.1 Campos do Cadastro")
    story.append(tabela_simples([
        ["Campo", "Obrigatório", "Descrição"],
        ["Razão Social", "Sim", "Nome completo da empresa"],
        ["Nome Fantasia", "Não", "Nome popular da empresa"],
        ["CNPJ", "Não", "CNPJ da empresa"],
        ["Telefone", "Não", "Telefone de contato"],
        ["E-mail", "Não", "E-mail de contato"],
        ["Endereço", "Não", "Endereço completo"],
        ["Cidade", "Não", "Cidade da empresa"],
        ["UF", "Não", "Estado (sigla de 2 letras)"],
        ["Responsável", "Não", "Nome do responsável legal"],
    ], larguras=[3.5*cm, 2.5*cm, 10*cm]))
    sp()
    item("O logo da empresa pode ser adicionado pela tela de configurações (⚙)")
    item("Apenas <b>Razão Social</b> é obrigatória para o primeiro cadastro")
    item("Após salvar, o sistema redireciona para a lista de obras")
    pg()

    # ═══════════════════════════════════════════
    # 4. OBRAS
    # ═══════════════════════════════════════════
    h1("4. Obras (Contratos)")
    story.append(hr())
    h2("4.1 Lista de Obras")
    p("A tela <b>Obras</b> (acessível pelo menu superior) exibe todas as obras cadastradas em uma tabela com as colunas:")
    sp()
    item("<b>Contrato</b> — Número/código identificador da obra")
    item("<b>Nome</b> — Nome descritivo da obra")
    item("<b>Cliente</b> — Nome do cliente contratante")
    item("<b>Local</b> — Endereço/local da obra")
    item("<b>Valor Contratado</b> — Valor inicial do contrato")
    item("<b>Status</b> — Situação atual da obra")
    sp()
    h3("Ordenação e Filtro")
    item("Obras <b>Concluídas</b> e <b>Canceladas</b> aparecem automaticamente no final da lista")
    item("Use o campo de busca para filtrar por contrato, nome, cliente ou local")
    item("Clique no cabeçalho de qualquer coluna para ordenar")
    sp()
    h2("4.2 Cadastro/Edição de Obra")
    p("Para criar uma nova obra, clique em <b>Nova Obra</b>. Para editar, clique no botão ✏️ na linha da obra.")
    sp()
    story.append(tabela_simples([
        ["Campo", "Obrigatório", "Descrição"],
        ["Contrato", "Sim", "Número/código do contrato (ex.: 094-2026)"],
        ["Nome", "Sim", "Nome descritivo da obra"],
        ["Cliente Contratante", "Não", "Nome do cliente"],
        ["Local da Obra", "Não", "Endereço da obra"],
        ["Responsável", "Não", "Engenheiro ou responsável técnico"],
        ["Data de Início", "Não", "Data de início da obra"],
        ["Previsão de Término", "Não", "Data prevista para conclusão"],
        ["Status", "Não", "Em andamento / Concluída / Pausada / Cancelada"],
        ["Valor Contratado", "Sim", "Valor inicial do contrato (R$)"],
        ["Observações", "Não", "Anotações livres"],
    ], larguras=[3.5*cm, 2*cm, 10.5*cm]))
    sp()
    h3("Status da Obra")
    story.append(tabela_simples([
        ["Status", "Cor", "Significado"],
        ["Em andamento", "Verde", "Obra em execução ativa"],
        ["Concluída", "Verde (destaque)", "Obra finalizada — aparece no final da lista"],
        ["Pausada", "Amarelo", "Obra temporariamente paralisada"],
        ["Cancelada", "Vermelho", "Obra cancelada — aparece no final da lista"],
    ], larguras=[3.5*cm, 3*cm, 9.5*cm]))
    sp()
    dica("Para excluir uma obra, use o botão 🗑️ na lista. Todos os lançamentos, aditivos e anexos vinculados serão removidos.")
    pg()

    # ═══════════════════════════════════════════
    # 5. DASHBOARD
    # ═══════════════════════════════════════════
    h1("5. Dashboard da Obra")
    story.append(hr())
    p("O Dashboard é a tela principal de acompanhamento de uma obra. Selecione a obra desejada no seletor <b>OBRA:</b> no cabeçalho superior.")
    sp()
    h2("5.1 Cards de Resumo Financeiro")
    p("Quatro cards exibem o resumo financeiro da obra selecionada:")
    sp()
    story.append(tabela_simples([
        ["Card", "Cálculo", "Cor"],
        ["Valor Contratado", "Valor inicial + Aditivos aprovados", "Azul"],
        ["Total de Aditivos", "Soma de todos os aditivos", "Azul claro"],
        ["Total Gasto", "Soma de todos os lançamentos", "Vermelho"],
        ["Saldo Disponível", "Valor Contratado − Total Gasto", "Verde"],
    ], larguras=[3.5*cm, 8*cm, 4.5*cm]))
    sp()
    h2("5.2 Tabela de Lançamentos Recentes")
    p("Exibe os últimos lançamentos da obra com: data, descrição, tipo, origem, valor e ações.")
    sp()
    h2("5.3 Ações do Dashboard")
    item("<b>Novo Lançamento</b> — Abre o formulário de lançamento para a obra")
    item("<b>Gerar Relatório PDF</b> — Gera relatório completo em PDF")
    item("<b>Ver Anexos</b> — Abre a tela de anexos da obra")
    item("<b>Aditivos</b> — Abre o gerenciador de aditivos")
    item("Botão <b>+</b> (aditivo) — Abre diálogo rápido para novo aditivo")
    pg()

    # ═══════════════════════════════════════════
    # 6. LANÇAMENTOS
    # ═══════════════════════════════════════════
    h1("6. Lançamentos Financeiros")
    story.append(hr())
    p("Os lançamentos representam os gastos e receitas de cada obra. Acesse pela tela de Lançamentos ou pelo Dashboard.")
    sp()
    h2("6.1 Campos do Lançamento")
    story.append(tabela_simples([
        ["Campo", "Obrigatório", "Descrição"],
        ["Data", "Sim", "Data do lançamento (com calendário)"],
        ["Tipo", "Não", "Material / Mão de obra / Outros"],
        ["Descrição", "Sim", "Descrição do gasto ou receita"],
        ["Quantidade", "Não", "Quantidade do item"],
        ["Unidade", "Não", "Unidade de medida (ex.: m², kg, un)"],
        ["Valor Unitário", "Não", "Valor por unidade (R$)"],
        ["Valor Total", "Sim", "Valor total do lançamento (R$)"],
        ["Origem", "Não", "Manual / Planilha orçamentária / Nota Fiscal / Comprovante Pagamento / Outros"],
        ["Observações", "Não", "Anotações adicionais"],
    ], larguras=[3*cm, 2*cm, 11*cm]))
    sp()
    h2("6.2 Origens de Lançamento")
    p("A origem indica a fonte da informação do lançamento. Algumas origens exigem anexo obrigatório:")
    sp()
    story.append(tabela_simples([
        ["Origem", "Exige Anexo", "Formatos Aceitos", "Descrição"],
        ["Manual", "Não", "—", "Lançamento digitado manualmente"],
        ["Planilha orçamentária", "Sim", "XLSX, XLS, CSV, PDF", "Planilha de orçamento"],
        ["Nota Fiscal", "Sim", "XLSX, XLS, CSV, PDF", "Nota fiscal do fornecedor"],
        ["Comprovante Pagamento", "Sim", "PDF, JPG, JPEG, PNG", "Comprovante de pagamento (PIX, boleto, etc.)"],
        ["Outros", "Não", "—", "Qualquer outra origem"],
    ], larguras=[3.5*cm, 2*cm, 3.5*cm, 7*cm]))
    sp()
    h3("Cálculo Automático")
    item("Se preencher <b>Quantidade</b> e <b>Valor Unitário</b>, o <b>Valor Total</b> é calculado automaticamente")
    item("O Valor Total pode ser editado manualmente se necessário")
    sp()
    h3("Edição e Exclusão")
    item("Clique no botão ✏️ de um lançamento na tabela para editar")
    item("Clique no botão 🗑️ para excluir (com confirmação)")
    item("Ao editar, o anexo existente pode ser substituído ou removido")
    pg()

    # ═══════════════════════════════════════════
    # 7. ADITIVOS
    # ═══════════════════════════════════════════
    h1("7. Aditivos de Obra")
    story.append(hr())
    p("Aditivos são acréscimos ou reduções ao valor contratado original da obra. Eles são somados ao valor contratado para calcular o <b>Valor Contratado Total</b>.")
    sp()
    h2("7.1 Campos do Aditivo")
    story.append(tabela_simples([
        ["Campo", "Obrigatório", "Descrição"],
        ["Data do Aditivo", "Sim", "Data de formalização do aditivo"],
        ["Descrição", "Sim", "Descrição do aditivo (ex.: 'Acréscimo de 15%')"],
        ["Valor", "Sim", "Valor do aditivo em R$ (positivo = acréscimo)"],
        ["Observações", "Não", "Anotações adicionais"],
    ], larguras=[3.5*cm, 2*cm, 10.5*cm]))
    sp()
    h2("7.2 Acesso aos Aditivos")
    item("Pelo Dashboard: botão <b>Aditivos</b> ou botão <b>+</b> (aditivo rápido)")
    item("O total de aditivos é exibido no card <b>Total de Aditivos</b> do Dashboard")
    pg()

    # ═══════════════════════════════════════════
    # 8. ANEXOS
    # ═══════════════════════════════════════════
    h1("8. Anexos e Documentos")
    story.append(hr())
    p("O sistema permite anexar documentos a obras e lançamentos. Os arquivos são armazenados fisicamente em <b>%APPDATA%\\ControleDeObras\\storage\\anexos</b>.")
    sp()
    h2("8.1 Tipos de Anexo")
    story.append(tabela_simples([
        ["Tipo", "Vinculado a", "Descrição"],
        ["Nota Fiscal", "Lançamento", "NF anexada ao selecionar origem 'Nota Fiscal'"],
        ["Comprovante Pagamento", "Lançamento", "Comprovante anexado ao selecionar 'Comprovante Pagamento'"],
        ["Planilha orçamentária", "Lançamento", "Planilha anexada ao selecionar 'Planilha orçamentária'"],
        ["Documento", "Obra", "Documento geral anexado pela tela de Anexos"],
    ], larguras=[4*cm, 3*cm, 9*cm]))
    sp()
    h2("8.2 Tela de Anexos da Obra")
    p("Acesse pelo Dashboard → botão <b>Ver Anexos</b>. Permite:")
    item("Visualizar todos os anexos da obra em tabela")
    item("Adicionar novos anexos à obra (botão <b>Adicionar</b>)")
    item("Visualizar um anexo (botão 👁 — abre o arquivo no aplicativo padrão)")
    item("Excluir um anexos (botão 🗑️)")
    sp()
    h2("8.3 Estrutura de Armazenamento")
    p("Os anexos são organizados por obra e lançamento:")
    sp()
    item("Anexos de obra: <b>storage/anexos/OBRA_{codigo}/obra/</b>")
    item("Anexos de lançamento: <b>storage/anexos/OBRA_{codigo}/lancamentos/LANC_{id}/</b>")
    item("Cada arquivo recebe um nome único com timestamp + hash para evitar conflitos")
    pg()

    # ═══════════════════════════════════════════
    # 9. RELATÓRIOS
    # ═══════════════════════════════════════════
    h1("9. Relatórios (PDF e DOCX)")
    story.append(hr())
    p("O sistema gera relatórios profissionais completos de cada obra.")
    sp()
    h2("9.1 Relatório PDF (ReportLab)")
    p("Gerado pelo botão <b>Gerar Relatório PDF</b> no Dashboard. O relatório contém:")
    sp()
    item("<b>Cabeçalho</b> — Logo da empresa, título, data de emissão")
    item("<b>Informações da Obra</b> — Contrato, cliente, local, responsável")
    item("<b>Resumo Financeiro</b> — Valor contratado, aditivos, total gasto, saldo")
    item("<b>Aditivos</b> — Tabela detalhada de todos os aditivos")
    item("<b>Lançamentos</b> — Tabela completa de todos os lançamentos")
    item("<b>Anexos</b> — Lista de todos os documentos anexados")
    item("<b>Assinatura</b> — Espaço para assinatura do responsável")
    item("Rodapé com numeração de páginas")
    sp()
    p("O arquivo é salvo automaticamente na pasta <b>Downloads</b> do usuário.")
    sp()
    h2("9.2 Relatório DOCX (Word)")
    p("Também disponível pelo Dashboard. Gera um documento Word com o mesmo conteúdo do PDF. Requer <b>LibreOffice</b> instalado para conversão automática para PDF.")
    sp()
    dica("Se o LibreOffice não estiver instalado, o arquivo DOCX será gerado normalmente, mas a conversão para PDF não será realizada.")
    pg()

    # ═══════════════════════════════════════════
    # 10. BACKUP E RESTAURAÇÃO
    # ═══════════════════════════════════════════
    h1("10. Backup e Restauração")
    story.append(hr())
    h2("10.1 Gerar Backup")
    p("Acesse pelo menu superior → botão <b>Backup</b>. O sistema gera um arquivo ZIP contendo:")
    sp()
    item("Banco de dados completo (<b>database/app.db</b>)")
    item("Todos os anexos (<b>storage/anexos/</b>)")
    item("Logos (<b>storage/logos/</b>)")
    item("Relatórios gerados (<b>reports/obras/</b>)")
    item("Manifesto com metadados e hashes de integridade (<b>manifest.json</b>)")
    sp()
    p("Os backups são salvos em <b>%APPDATA%\\ControleDeObras\\data\\backups</b>.")
    sp()
    h3("Backup Automático Diário")
    p("O sistema realiza um backup automático uma vez por dia ao iniciar, se ainda não existir um backup do dia.")
    sp()
    h2("10.2 Restaurar Backup")
    p("Acesse pelo menu superior → botão <b>Restaurar</b>. Selecione o arquivo ZIP de backup.")
    sp()
    item("O sistema cria um <b>backup de segurança</b> automático antes de restaurar")
    item("Valida o hash do banco de dados contra o manifesto")
    item("Substitui banco, anexos, logos e relatórios")
    item("Se a restauração falhar, reverte automaticamente para o backup de segurança")
    sp()
    dica("Nunca delete manualmente os arquivos em %APPDATA%\\ControleDeObras. Use sempre o sistema para backup e restauração.")
    sp()
    h2("10.3 Política de Retenção")
    p("O sistema mantém no máximo <b>10 backups</b> no diretório. Backups mais antigos são removidos automaticamente.")
    pg()

    # ═══════════════════════════════════════════
    # 11. SEGURANÇA DE ANEXOS
    # ═══════════════════════════════════════════
    h1("11. Segurança de Anexos")
    story.append(hr())
    p("O sistema possui verificações avançadas para garantir que nenhum anexo seja perdido:")
    sp()
    h2("11.1 Manifesto Expandido")
    p("Cada backup inclui no manifesto:")
    item("<b>total_anexo_files</b> — Quantidade real de arquivos no disco")
    item("<b>anexo_integrity_hash</b> — Hash SHA-256 composto de todos os anexos")
    sp()
    h2("11.2 Verificação Pós-Backup")
    p("Após gerar o backup, o sistema reabre o ZIP e confirma que todos os anexos do disco estão presentes. Se algum arquivo faltar, um WARNING é registrado no log.")
    sp()
    h2("11.3 Verificação Pós-Restauração")
    p("Após restaurar, o sistema percorre todos os registros da tabela <b>anexos</b> no banco e confirma que cada arquivo existe no disco.")
    sp()
    h2("11.4 Auditoria de Anexos")
    p("O sistema dispõe de uma função de auditoria que compara banco vs disco e detecta:")
    item("<b>Faltando no disco</b> — Registro no banco mas arquivo ausente")
    item("<b>Órfãos no disco</b> — Arquivo no disco sem registro no banco")
    item("<b>Hash mismatches</b> — Hash do banco diferente do hash do arquivo")
    sp()
    dica("As verificações são automáticas e não bloqueiam o uso do sistema. Os problemas são registrados no log para análise.")
    pg()

    # ═══════════════════════════════════════════
    # 12. CONFIGURAÇÕES
    # ═══════════════════════════════════════════
    h1("12. Configurações")
    story.append(hr())
    p("Acesse pelo botão ⚙ no canto superior direito. Permite:")
    sp()
    item("Editar os dados da empresa")
    item("Adicionar/alterar o logo da empresa (exibido nos relatórios)")
    item("Visualizar informações da licença")
    pg()

    # ═══════════════════════════════════════════
    # 13. DICAS
    # ═══════════════════════════════════════════
    h1("13. Dicas e Boas Práticas")
    story.append(hr())
    sp()
    item("Faça backup regularmente antes de grandes alterações")
    item("Use a origem correta ao lançar despesas (Nota Fiscal, Comprovante, etc.) para manter a documentação organizada")
    item("Mantenha o logo da empresa atualizado para relatórios profissionais")
    item("Revise o Dashboard regularmente para acompanhar o saldo de cada obra")
    item("Ao encerrar uma obra, altere o status para <b>Concluída</b>")
    item("Não mova ou delete manualmente arquivos em %APPDATA%\\ControleDeObras")
    item("Se precisar trocar de computador, faça um backup completo e restaure no novo equipamento")
    item("A licença é vinculada à máquina — solicite nova chave ao trocar de computador")
    sp(20)
    story.append(hr())
    sp()
    story.append(Paragraph(
        "Controle de Obras v1.0.5 — CASSIO REIS TECH<br/>"
        "Para suporte, entre em contato com o desenvolvedor.",
        estilos["Dica"]))

    # ── Gerar PDF ──
    doc.build(story)
    print(f"Manual gerado: {OUTPUT}")
    print(f"Tamanho: {OUTPUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    gerar_manual()