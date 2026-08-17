# ROADMAP — Sistema de Controle de Obras

## Visão
Sistema desktop para controle financeiro e documental de obras de engenharia civil, operando sempre no contexto de uma obra ativa.

## Fases

### Fase 1 — Núcleo Operacional
**Objetivo:** Entregar o ciclo mínimo utilizável: empresa, obras, aditivos, lançamentos, anexos, dashboard e relatório PDF.

**Entregáveis:**
- Estrutura de projeto em camadas
- Banco SQLite com integridade relacional
- Cadastro inicial da empresa
- Cadastro de obras e seleção de obra ativa
- Cadastro de aditivos
- Lançamentos manuais de custos
- Gestão de anexos por obra/lançamento
- Dashboard da obra
- Relatório PDF por obra
- Documentação de decisões

**UAT:** Usuário consegue cadastrar empresa, obra, aditivo, lançamento, anexo e gerar PDF com apuração correta.

### Fase 2 — Refinamentos Operacionais
**Objetivo:** Melhorar usabilidade, buscas, filtros e relatórios.

**Entregáveis (futuro):**
- Filtros avançados em obras e lançamentos
- Relatórios adicionais
- Backup/exportação de dados
- Preferências do usuário

### Fase 3 — Escalabilidade
**Objetivo:** Expandir para recursos mais avançados quando necessário.

**Entregáveis (futuro):**
- Cronograma físico-financeiro
- Medições contratuais
- Multiusuário
- Integrações externas

## Decisões Aprovadas
1. Stack: Python + PySide6 + SQLite
2. Arquitetura em camadas: `src/domain`, `src/application`, `src/infrastructure`, `src/ui`, `src/shared`
3. Lançamentos descritivos manuais, sem catálogo rígido
4. Obra ativa obrigatória para operação
5. Anexos no filesystem, metadados no banco
6. Fase 1 fechada sem antecipar módulos complexos
