# Especificação Funcional e Técnica Inicial — Sistema Desktop de Controle de Obras

## Visão geral

Este documento define a especificação funcional e técnica inicial de um sistema desktop em Python, PySide6 e SQLite para controle financeiro e operacional de obras e serviços na área de engenharia civil e construtora. O sistema deve ser tratado como um projeto novo, com domínio próprio centrado em obras, sem reutilizar regras, entidades ou decisões do projeto BPO anterior.[cite:22][cite:23]

A proposta considera uma arquitetura modular, organizada e preparada para crescimento, com interface formal, limpa, profissional e de alta legibilidade. O produto deve evoluir em fases fechadas, com escopo controlado, preservando registro contínuo das decisões de modelagem e arquitetura para evitar perda de contexto nas próximas iterações.[cite:1][cite:22]

## Objetivo do sistema

O objetivo do sistema é controlar, por obra, os dados contratuais, os aditivos, os lançamentos individuais de custos, os anexos comprobatórios e a apuração consolidada de resultado. Ao final, o sistema deve permitir identificar com segurança o valor contratado inicial, o total de aditivos, o total gasto e o valor líquido final de cada obra.[cite:23]

O sistema não deve funcionar como cadastro fixo de estoque ou catálogo rígido de materiais e serviços. Os lançamentos precisam refletir o cenário real da obra, com digitação manual descritiva dos itens ou serviços conforme planilhas, notas, cupons e documentos recebidos, já que a variabilidade operacional do setor torna inviável um cadastro prévio obrigatório de todos os insumos.[cite:23]

## Princípios de produto

Os seguintes princípios orientam a modelagem inicial do produto:

- O domínio central é a obra, e toda operação relevante deve estar vinculada a uma obra ativa.[cite:23]
- O sistema deve permitir múltiplas obras cadastradas, mas o usuário deve operar sempre dentro do contexto explícito da obra selecionada.[cite:23]
- Os lançamentos de custos serão descritivos e manuais, com estrutura suficiente para classificação, totalização e auditoria, sem dependência de catálogo fixo de itens.[cite:23]
- Os anexos devem poder ser vinculados diretamente à obra e, quando necessário, também a um lançamento específico.[cite:23]
- A arquitetura deve separar interface, regras de negócio e persistência, aproveitando o padrão Model/View do Qt para reduzir acoplamento entre dados e apresentação.[cite:1][cite:22][cite:7]
- O sistema deve nascer apto a crescer para novas funcionalidades sem exigir refatoração estrutural do núcleo.[cite:1][cite:22]

## Escopo funcional inicial

O escopo funcional inicial contempla o núcleo mínimo utilizável para operação financeira e documental de obras. A primeira versão deve permitir o cadastro da empresa, o cadastro de obras, a seleção da obra ativa, o registro de aditivos, o lançamento manual de custos, o gerenciamento de anexos e a emissão de relatório PDF por obra.[cite:23]

Itens fora do escopo inicial, mas compatíveis com evolução futura, incluem cronograma físico-financeiro, medições contratuais complexas, workflow de aprovação multinível, controle de estoque, centro de custo avançado, multiusuário em rede e integração com sistemas externos. Esses pontos não devem entrar na Fase 1 para evitar aumento prematuro de complexidade.[cite:1]

## Objetivo operacional por obra

Cada obra deve permitir apuração dos seguintes indicadores principais:

- Valor bruto da obra, correspondente ao valor contratado inicial.[cite:23]
- Total de aditivos lançados para a obra.[cite:23]
- Total gasto, calculado a partir da soma dos lançamentos válidos de custos.[cite:23]
- Valor líquido da obra, obtido pela soma do valor inicial com os aditivos, menos o total gasto.[cite:23]

A fórmula funcional de apuração é:

- Valor líquido = valor contratado inicial + total de aditivos - total gasto.[cite:23]

## Fluxo operacional inicial

O fluxo operacional inicial deve seguir a sequência abaixo, de forma simples e clara para o usuário:

1. Ao abrir o sistema pela primeira vez, o usuário visualiza uma tela de boas-vindas com apresentação premium e institucional do produto.[cite:23][cite:26]
2. Na sequência, o sistema solicita o cadastro inicial da empresa com dados básicos.[cite:23]
3. Após essa etapa, o usuário acessa a área principal do sistema.[cite:23]
4. O usuário cadastra uma ou mais obras com seus dados básicos, incluindo valor contratado inicial.[cite:23]
5. O usuário seleciona a obra ativa com a qual deseja trabalhar naquele momento.[cite:23][cite:33]
6. Dentro da obra selecionada, o usuário acessa um dashboard específico da obra.[cite:23]
7. A partir do dashboard da obra, o usuário registra aditivos, lança custos manualmente e anexa documentos e planilhas de suporte.[cite:23]
8. Ao final, o sistema consolida os totais e permite emitir relatório PDF detalhado da obra.[cite:23]

Esse fluxo é compatível com navegação por páginas empilhadas em interface desktop com `QStackedWidget`, mecanismo apropriado para trocar páginas internas sem perder coerência de navegação no contexto da aplicação.[cite:33]

## Regras dos lançamentos

Os lançamentos não devem depender de cadastro prévio de produtos, materiais ou serviços. Em vez disso, cada lançamento deve ser digitado livremente pelo usuário com estrutura semântica suficiente para auditoria e cálculo.[cite:23]

Cada lançamento deve possuir, no mínimo:

- Tipo macro do lançamento, como material, serviço, mão de obra, manutenção ou outros.[cite:23]
- Descrição livre do item ou serviço, por exemplo “Saco de cimento 50kg”.[cite:23]
- Quantidade, quando aplicável.[cite:23]
- Unidade, quando aplicável, como saco, metro, diária, unidade ou lote.[cite:23]
- Valor unitário, quando aplicável.[cite:23]
- Valor total do lançamento.[cite:23]
- Data do lançamento.[cite:23]
- Observações complementares.[cite:23]
- Origem da informação, como manual, planilha de diretoria, planilha de engenharia, nota geral ou cupom.[cite:23]

Esse modelo atende tanto cenários de item detalhado quanto cenários de lançamento consolidado, como “material para pintura”, quando a documentação recebida vier agrupada e não justificar decomposição em subitens.[cite:23]

## Entidades principais

As entidades iniciais recomendadas para a modelagem do sistema são as seguintes:

### Empresa

Representa a empresa proprietária do sistema e deve ser cadastrada no primeiro uso. Essa entidade armazena os dados institucionais básicos necessários para identificação interna e futura personalização de relatórios.[cite:23]

### Obra

É a entidade central do sistema e deve concentrar o vínculo principal com aditivos, lançamentos, anexos e relatórios. Toda apuração financeira é realizada no contexto de uma obra específica.[cite:23]

### Aditivo

Representa acréscimo financeiro ao valor contratado inicial da obra. Deve manter histórico individualizado com data, descrição e valor.[cite:23]

### Tipo de lançamento

Classifica o lançamento em nível macro, como material, serviço, mão de obra, manutenção e outros. Essa entidade deve ser parametrizada para dar organização analítica sem engessar a descrição real do item.[cite:23]

### Lançamento

Representa um gasto individual lançado manualmente dentro da obra. Deve conter descrição livre, dados quantitativos e monetários, data, observações e vínculo documental quando houver.[cite:23]

### Anexo

Representa arquivos vinculados à obra ou a um lançamento específico, como nota fiscal, cupom fiscal, planilha enviada por diretores ou planilha enviada por engenheiros. Deve armazenar metadados do arquivo e vínculo lógico com o contexto correto.[cite:23]

### Relatório gerado

Representa o histórico de relatórios emitidos pelo sistema, permitindo rastrear quando e para qual obra determinado PDF foi produzido.[cite:23]

### Configuração

Armazena parâmetros técnicos e funcionais do sistema, como diretório de anexos, dados institucionais e preferências operacionais futuras.[cite:23]

## Modelo relacional inicial

O banco de dados inicial em SQLite é adequado para a Fase 1, desde que a aplicação preserve integridade relacional entre obra, aditivo, lançamento e anexo. O SQLite oferece suporte a chaves estrangeiras, mas essa validação precisa ser habilitada explicitamente pela aplicação ao abrir a conexão, usando `PRAGMA foreign_keys = ON`.[cite:29]

As tabelas iniciais recomendadas são as seguintes:

| Tabela | Finalidade |
|---|---|
| `empresa` | Cadastro institucional inicial da empresa usuária do sistema.[cite:23] |
| `obras` | Cadastro principal das obras, com dados contratuais e operacionais.[cite:23] |
| `aditivos` | Histórico de acréscimos financeiros por obra.[cite:23] |
| `tipos_lancamento` | Classificação macro dos lançamentos.[cite:23] |
| `lancamentos` | Registro analítico dos custos da obra com descrição livre.[cite:23] |
| `anexos` | Metadados dos arquivos vinculados à obra e/ou a um lançamento.[cite:23] |
| `relatorios_gerados` | Histórico de emissão de relatórios.[cite:23] |
| `configuracoes` | Parâmetros persistentes do sistema.[cite:23] |

### Estrutura mínima da tabela `empresa`

Campos sugeridos:

- `id`
- `razao_social`
- `nome_fantasia`
- `cnpj`
- `telefone`
- `email`
- `endereco`
- `cidade`
- `uf`
- `responsavel`
- `created_at`
- `updated_at`

### Estrutura mínima da tabela `obras`

Campos sugeridos:

- `id`
- `codigo`
- `nome`
- `cliente_contratante`
- `local_obra`
- `engenheiro_responsavel`
- `data_inicio`
- `previsao_termino`
- `status`
- `valor_contratado_inicial`
- `observacoes`
- `created_at`
- `updated_at`

### Estrutura mínima da tabela `aditivos`

Campos sugeridos:

- `id`
- `obra_id`
- `data_aditivo`
- `descricao`
- `valor`
- `observacoes`
- `created_at`

### Estrutura mínima da tabela `tipos_lancamento`

Campos sugeridos:

- `id`
- `nome`
- `ativo`
- `ordem_exibicao`

Valores iniciais sugeridos:

- Material
- Serviço
- Mão de obra
- Manutenção
- Outros

### Estrutura mínima da tabela `lancamentos`

Campos sugeridos:

- `id`
- `obra_id`
- `tipo_lancamento_id`
- `data_lancamento`
- `descricao`
- `complemento`
- `quantidade`
- `unidade`
- `valor_unitario`
- `valor_total`
- `origem_informacao`
- `observacoes`
- `created_at`
- `updated_at`

### Estrutura mínima da tabela `anexos`

Campos sugeridos:

- `id`
- `obra_id`
- `lancamento_id` opcional
- `tipo_anexo`
- `nome_original`
- `nome_armazenado`
- `caminho_relativo`
- `hash_arquivo`
- `mime_type`
- `tamanho_bytes`
- `data_documento` opcional
- `observacoes`
- `created_at`

### Estrutura mínima da tabela `relatorios_gerados`

Campos sugeridos:

- `id`
- `obra_id`
- `tipo_relatorio`
- `arquivo_gerado`
- `data_geracao`
- `observacoes`

### Estrutura mínima da tabela `configuracoes`

Campos sugeridos:

- `id`
- `chave`
- `valor`
- `descricao`
- `updated_at`

## Regras de negócio iniciais

As regras de negócio iniciais recomendadas são as seguintes:

- Uma obra deve possuir valor contratado inicial obrigatório no momento do cadastro.[cite:23]
- Uma obra pode possuir zero ou muitos aditivos.[cite:23]
- Uma obra pode possuir zero ou muitos lançamentos de custos.[cite:23]
- Um lançamento pertence obrigatoriamente a uma obra.[cite:23]
- Um lançamento deve possuir descrição livre obrigatória.[cite:23]
- Um lançamento pode ou não possuir quantidade e unidade, para acomodar tanto itens unitários quanto lançamentos consolidados.[cite:23]
- Um lançamento deve possuir valor total obrigatório.[cite:23]
- Um anexo deve estar vinculado pelo menos a uma obra.[cite:23]
- Um anexo pode, opcionalmente, estar vinculado também a um lançamento específico.[cite:23]
- A obra ativa deve estar sempre explícita na interface para reduzir o risco de lançamentos na obra errada.[cite:23]
- O cálculo de totais não deve ficar embutido nas telas; ele deve ser centralizado em regras de domínio ou serviços de aplicação, preservando consistência entre dashboard e relatórios.[cite:1][cite:22]

## Arquitetura recomendada

A arquitetura recomendada para o sistema é em camadas, com separação clara entre domínio, aplicação, infraestrutura e interface. Em aplicações Qt for Python, o padrão Model/View reduz acoplamento entre dados e apresentação e é apropriado para tabelas, listagens e painéis que precisam evoluir sem duplicação de lógica de exibição.[cite:7][cite:14]

Estrutura sugerida:

- `src/domain/` para entidades, regras de negócio, objetos de valor e cálculos.[cite:1]
- `src/application/` para casos de uso, serviços, DTOs e orquestração.[cite:1]
- `src/infrastructure/` para SQLite, repositórios, filesystem de anexos, logs e geração de PDF.[cite:1]
- `src/ui/` para telas, janelas, widgets, modelos Qt e controladores de interação.[cite:1][cite:22]
- `src/shared/` para configurações, utilitários, constantes e exceções comuns.[cite:1]
- `docs/` para especificações, decisões arquiteturais e histórico funcional do projeto.[cite:1]

Padrões recomendados:

- Repository para abstrair acesso ao banco.[cite:1]
- Service ou Use Case para centralizar regras como cadastro de obra, lançamento de custo, cálculo de apuração e geração de relatório.[cite:1]
- Separação entre entidades de domínio e objetos apresentados na interface.[cite:7]
- Model/View do Qt para listagens e tabelas, evitando lógica de dados diretamente em widgets de tela.[cite:7][cite:14]

## Armazenamento de anexos

Para a Fase 1, a melhor abordagem é armazenar os arquivos fisicamente no sistema de arquivos local e registrar no banco apenas os metadados e o caminho relativo. Esse desenho reduz peso no banco, facilita backup e torna mais simples a gestão de documentos por obra.[cite:1][cite:22]

Regras recomendadas para anexos:

- O diretório físico deve ser organizado por obra.[cite:23]
- O banco deve registrar nome original, nome interno armazenado, caminho relativo, hash do arquivo e tamanho.[cite:23]
- O sistema deve permitir anexar documentos diretamente na obra e, quando necessário, vincular também ao lançamento correspondente.[cite:23]
- O sistema deve aceitar, no mínimo, notas fiscais, cupons fiscais e planilhas recebidas da diretoria ou engenharia.[cite:23]

## Navegação e experiência do usuário

A interface deve ser formal, limpa e altamente legível, adequada ao perfil corporativo do setor de engenharia e construtora. O usuário também demonstrou preferência por experiência premium, mas isso deve ser traduzido com sobriedade visual e animações bem controladas, sem poluição gráfica.[cite:1][cite:22]

O fluxo de navegação inicial pode ser estruturado com páginas internas empilhadas usando `QStackedWidget`, recurso apropriado para interfaces em que uma página substitui a outra dentro da mesma janela principal. O framework de animação do Qt também permite construir aberturas e transições visuais sofisticadas com elementos como `QPropertyAnimation`, tornando viável uma tela de boas-vindas de aparência premium sem quebrar o padrão desktop corporativo.[cite:33][cite:26][cite:35]

## Telas principais da Fase 1

### 1. Tela de boas-vindas

Deve ser exibida na primeira execução ou no carregamento inicial do produto, com apresentação visual premium e institucional. Sua função é gerar percepção de produto profissional e conduzir o usuário ao cadastro inicial da empresa.[cite:23][cite:26]

### 2. Tela de cadastro inicial da empresa

Deve solicitar os dados básicos da empresa usuária do sistema. Essa etapa deve ser obrigatória antes do uso operacional da aplicação.[cite:23]

### 3. Tela de listagem de obras

Deve apresentar todas as obras cadastradas, com busca, filtros e ação clara para abrir a obra desejada. Essa tela é o ponto de entrada operacional após a configuração inicial.[cite:23]

### 4. Tela de cadastro e edição de obra

Deve permitir informar os dados básicos da obra, como nome, local, engenheiro responsável, data de início, previsão de término, status e valor contratado inicial. Também deve reservar espaço para observações relevantes da obra.[cite:23]

### 5. Tela de seleção ou acesso à obra ativa

Deve deixar claro com qual obra o usuário está trabalhando no momento. Esse contexto precisa ficar visível no topo da interface ou em área de destaque para reduzir erro operacional.[cite:23]

### 6. Dashboard da obra

Deve concentrar a visão executiva da obra selecionada. O topo da tela deve destacar valor contratado inicial, total de aditivos, total gasto e valor líquido, enquanto a área inferior pode apresentar últimas movimentações, anexos recentes e atalhos de ação.[cite:23]

### 7. Tela de lançamentos

Deve ser otimizada para digitação manual rápida e clara. O formulário precisa aceitar descrição livre, quantidade, unidade, valor unitário, valor total, tipo macro, data e observações, sem exigir cadastro prévio do item.[cite:23]

### 8. Tela de anexos e planilhas

Deve centralizar upload, organização e visualização dos documentos da obra. Deve ser possível anexar planilhas enviadas por diretores e engenheiros, bem como notas e cupons relacionados à obra ou a lançamentos específicos.[cite:23]

### 9. Tela de relatório da obra

Deve permitir gerar PDF detalhado contendo identificação da obra, valor inicial, aditivos, lançamentos, anexos relacionados e apuração final consolidada.[cite:23]

## Dashboard da obra

O dashboard específico da obra é um ponto-chave do produto e deve ser tratado como a home operacional da obra ativa. Ele não deve ser apenas uma listagem de dados, mas sim uma tela de leitura rápida e tomada de decisão sobre a situação financeira daquela obra.[cite:23]

Componentes sugeridos do dashboard:

- Cabeçalho com identificação da obra e status atual.[cite:23]
- Cartões de resumo com valor contratado inicial, total de aditivos, total gasto e valor líquido.[cite:23]
- Lista curta de últimos lançamentos.[cite:23]
- Área de anexos recentes ou pendentes de conferência.[cite:23]
- Ações rápidas para novo lançamento, novo aditivo, novo anexo e gerar relatório.[cite:23]

## Relatório PDF por obra

O relatório PDF da obra deve ser detalhado e adequado a uso gerencial e de conferência. Ele deve funcionar como espelho formal da situação da obra em determinado momento.[cite:23]

Conteúdo mínimo recomendado do PDF:

- Dados identificadores da empresa.[cite:23]
- Dados identificadores da obra.[cite:23]
- Valor contratado inicial.[cite:23]
- Relação de aditivos com data, descrição e valor.[cite:23]
- Relação de lançamentos com tipo, descrição, quantidade, unidade, valores e observações.[cite:23]
- Relação de anexos vinculados à obra e aos lançamentos, quando aplicável.[cite:23]
- Apuração final com valor bruto, total de aditivos, total gasto e valor líquido.[cite:23]
- Data e hora de emissão do relatório.[cite:23]

## Riscos de modelagem

Os principais riscos de modelagem identificados para este sistema são os seguintes:

- Tentar transformar o sistema em um ERP de estoque com cadastro rígido de produtos e serviços, contrariando a realidade variável das obras.[cite:23]
- Não separar a classificação macro do lançamento da descrição livre do item, o que reduziria flexibilidade operacional.[cite:23]
- Permitir operação sem obra ativa explícita, elevando o risco de lançar dados na obra errada.[cite:23]
- Misturar regras de cálculo com código de interface, criando divergência entre tela e relatório.[cite:1][cite:22]
- Armazenar anexos binários diretamente no SQLite na Fase 1, aumentando complexidade de manutenção e backup.[cite:1]
- Não registrar decisões arquiteturais e funcionais ao longo do projeto, o que contraria uma das preferências centrais do usuário para continuidade entre conversas e iterações.[cite:1]

## Decisões registradas até aqui

As seguintes decisões devem ser consideradas formalmente aprovadas para a base do projeto:

1. Este sistema é um projeto novo e independente do projeto BPO anterior.[cite:22]
2. O domínio central do sistema é a obra.[cite:23]
3. O sistema deve ser desktop, usando Python, PySide6 e SQLite.[cite:22]
4. A arquitetura deve ser modular e preparada para crescimento futuro.[cite:1][cite:22]
5. A interface deve ser formal, limpa, profissional e de alta legibilidade.[cite:1][cite:22]
6. O desenvolvimento deve ocorrer em fases com escopo fechado.[cite:1]
7. Os lançamentos de custos serão manuais e descritivos, sem cadastro prévio obrigatório de materiais ou serviços.[cite:23]
8. O sistema deve possuir cadastro inicial da empresa no primeiro uso.[cite:23]
9. O sistema deve trabalhar com múltiplas obras, mas sempre dentro do contexto de uma obra ativa selecionada.[cite:23]
10. O sistema deve armazenar anexos vinculados à obra e opcionalmente ao lançamento.[cite:23]
11. O sistema deve gerar relatório PDF detalhado por obra.[cite:23]
12. Todas as decisões relevantes do projeto devem ser registradas em documentação contínua.[cite:1]

## Recomendação para a Fase 1

A Fase 1 deve ser fechada como um núcleo funcional pequeno, sólido e usável, sem tentar antecipar módulos mais amplos. A recomendação é implementar apenas a base institucional, o ciclo principal da obra e a apuração consolidada.[cite:1][cite:23]

Escopo recomendado da Fase 1:

- Estrutura inicial do projeto em camadas.[cite:1]
- Banco SQLite com tabelas principais e integridade relacional habilitada.[cite:29]
- Cadastro inicial da empresa.[cite:23]
- Cadastro de obras.[cite:23]
- Seleção de obra ativa.[cite:23]
- Cadastro de aditivos.[cite:23]
- Lançamentos manuais de custos.[cite:23]
- Gestão de anexos por obra e por lançamento.[cite:23]
- Dashboard individual da obra.[cite:23]
- Geração de relatório PDF da obra.[cite:23]
- Estrutura documental em `docs/` para registrar decisões e evolução do produto.[cite:1]

## Estrutura documental recomendada

Para garantir continuidade e rastreabilidade, o projeto deve nascer com documentação mínima persistente. Isso está alinhado à preferência do usuário por registrar decisões importantes e evitar perda de contexto ao longo da evolução do sistema.[cite:1]

Arquivos sugeridos:

- `docs/especificacao-funcional-inicial.md`
- `docs/decisoes-arquitetura.md`
- `docs/fases-do-projeto.md`
- `docs/regras-de-negocio.md`
- `docs/changelog-interno.md`

## Encaminhamento da próxima etapa

Com esta especificação funcional e técnica inicial aprovada, a próxima etapa recomendada é transformar o documento em plano de implementação da Fase 1, definindo estrutura de pastas, convenções de projeto, módulos iniciais, estratégia de banco de dados e sequência de construção das telas principais.[cite:1][cite:22]
