# PLAN — Fase 1: Núcleo Operacional

## Contexto
Projeto novo: Sistema Desktop de Controle de Obras.  
Stack: Python, PySide6, SQLite.  
Domínio central: obra. Lançamentos descritivos manuais. Anexos no filesystem.

## Objetivo da fase
Entregar o ciclo mínimo utilizável: cadastro de empresa, obras, aditivos, lançamentos, anexos, dashboard da obra e relatório PDF.

## Critérios de aceitação (UAT)
1. Usuário cadastra empresa no primeiro uso.
2. Usuário cadastra obra com valor contratado inicial.
3. Usuário seleciona obra ativa e o contexto fica visível.
4. Usuário registra aditivo vinculado à obra.
5. Usuário lança custo manual descritivo vinculado à obra.
6. Usuário anexa arquivo à obra e/ou a um lançamento.
7. Dashboard mostra: valor contratado, total aditivos, total gasto, valor líquido.
8. Relatório PDF consolidado por obra é gerado corretamente.

## Tarefas

### 1. Esqueleto do projeto
- [x] Criar estrutura de pastas (`src/domain`, `src/application`, `src/infrastructure`, `src/ui`, `src/shared`, `tests`, `docs`, `data`, `storage/anexos`, `reports/obras`)
- [x] Criar `pyproject.toml` com dependências (PySide6, reportlab, pytest)
- [x] Criar `README.md` inicial com instruções de execução
- [x] Configurar hook local de qualidade (lint + testes rápidos)

### 2. Domínio e modelos
- [x] Criar entidades: `Empresa`, `Obra`, `Aditivo`, `TipoLancamento`, `Lancamento`, `Anexo`, `Configuracao`
- [x] Criar objetos de valor para cálculos financeiros (`ResumoFinanceiroObra`)
- [x] Implementar regras: valor líquido = contratado + aditivos - gastos

### 3. Persistência (SQLite)
- [x] Criar schema com `PRAGMA foreign_keys = ON`
- [x] Implementar `DatabaseManager` e migrations iniciais
- [x] Implementar repositórios para cada entidade
- [x] Implementar inicialização de dados (tipos de lançamento padrão)

### 4. Casos de uso (application)
- [x] Cadastrar/Editar empresa
- [x] Cadastrar/Editar obra
- [x] Selecionar obra ativa
- [x] Cadastrar/Editar aditivo
- [x] Cadastrar/Editar lançamento
- [x] Anexar arquivo à obra ou lançamento
- [x] Calcular resumo da obra
- [x] Gerar relatório PDF

### 5. Interface (PySide6)
- [x] Tela de boas-vindas
- [x] Tela de cadastro inicial da empresa
- [x] Tela de listagem de obras
- [x] Melhorias de usabilidade na listagem de obras (busca, ordenação, duplo clique, tooltips, menu de contexto, contagem, destaque)
- [x] Tela de cadastro/edição de obra
- [x] Tela de seleção ou acesso à obra ativa
- [x] Dashboard da obra
- [x] Tela de lançamentos
- [x] Tela de anexos
- [x] Tela/geração de relatório PDF
- [x] Botões de backup e restauração no cabeçalho

### 6. Testes
- [x] Testes de domínio (cálculos, regras)
- [x] Testes de repositório (CRUD e integridade)
- [x] Testes de casos de uso
- [x] Testes de integração do fluxo principal
- [x] Testes do módulo de backup/restauração
- [ ] Smoke test da aplicação (depende de ambiente gráfico)

### 7. Documentação
- [x] Atualizar `docs/decisoes-arquitetura.md`
- [x] Criar `docs/fases-do-projeto.md`
- [x] Criar `docs/regras-de-negocio.md`
- [x] Criar `docs/changelog-interno.md`

## Ordem de execução recomendada
1. Esqueleto do projeto
2. Domínio e modelos
3. Persistência
4. Casos de uso
5. Interface
6. Testes
7. Documentação

## Automações sugeridas
- `pre-commit`: `ruff` + `pytest` tests/unit
- `pre-push`: `pytest` completo
- Hook ECC `post-plan`: gerar esqueleto do projeto após plano aprovado
- Hook ECC `post-execute`: rodar smoke test após implementação
