# Fases do Projeto — Controle de Obras

## Fase 1 — Núcleo Operacional (em andamento)

### Objetivo
Entregar o ciclo mínimo utilizável para controle financeiro e documental de obras.

### Entregáveis concluídos
- [x] Estrutura de projeto em camadas (`src/domain`, `src/application`, `src/infrastructure`, `src/ui`, `src/shared`)
- [x] Banco SQLite com integridade relacional (`PRAGMA foreign_keys = ON`)
- [x] Cadastro inicial da empresa
- [x] Cadastro de obras e seleção de obra ativa
- [x] Cadastro de aditivos
- [x] Lançamentos manuais de custos
- [x] Gestão de anexos por obra
- [x] Dashboard da obra com apuração financeira
- [x] Relatório PDF por obra
- [x] Módulo de backup e restauração completo (banco + anexos + relatórios + manifesto)
- [x] Testes unitários e de integração
- [x] Documentação de decisões arquiteturais

### Próximos passos sugeridos
- Testes de interface (smoke tests PySide6)
- Refinamentos visuais e UX
- Filtros e buscas em listagens
- Exportação adicional de dados

## Fase 2 — Refinamentos Operacionais (futuro)

- Filtros avançados em obras e lançamentos
- Relatórios adicionais
- Backup incremental e retenção
- Preferências do usuário

## Fase 3 — Escalabilidade (futuro)

- Cronograma físico-financeiro
- Medições contratuais
- Multiusuário
- Integrações externas
