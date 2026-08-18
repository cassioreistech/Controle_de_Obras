# Skills Config - Novos Projetos

## 🚀 Setup Rápido (Copiar e Colar)

### Projeto Fullstack Padrão (Recomendado)
```python
# Setup inicial (Dia 1)
skill("codebase-onboarding")
skill("documentation-lookup")
skill("git-workflow")

# Desenvolvimento diário
skill("tdd-workflow")
skill("security-review")
skill("error-handling")

# Frontend (se aplicável)
skill("ui-ux-pro-max")

# Qualidade (pré-merge)
skill("code-review-and-quality")
skill("verification-loop")
```

---

## 📦 Por Tipo de Projeto

### Backend Python Puro
```python
skill("codebase-onboarding")
skill("documentation-lookup")
skill("git-workflow")
skill("tdd-workflow")
skill("security-review")
skill("error-handling")
skill("database-migrations")
skill("postgres-patterns")  # ou mysql-patterns
skill("prisma-patterns")    # se usar TypeScript
```

### Frontend React/Next.js
```python
skill("codebase-onboarding")
skill("documentation-lookup")
skill("git-workflow")
skill("tdd-workflow")
skill("ui-ux-pro-max")
skill("design-system")
skill("ui-styling")
skill("e2e-testing")          # Playwright
skill("code-review-and-quality")
```

### Mobile iOS (Swift)
```python
skill("codebase-onboarding")
skill("documentation-lookup")
skill("git-workflow")
skill("tdd-workflow")
skill("swiftui-patterns")
skill("swift-concurrency-6-2")
skill("swift-protocol-di-testing")
skill("security-review")
skill("code-review-and-quality")
```

### Data Science / Analytics
```python
skill("codebase-onboarding")
skill("documentation-lookup")
skill("git-workflow")
skill("tdd-workflow")
skill("postgres-patterns")
skill("clickhouse-io")        # se usar ClickHouse
skill("data-throughput-accelerator")
skill("benchmark")
skill("security-review")
```

### API / Microserviço
```python
skill("codebase-onboarding")
skill("documentation-lookup")
skill("git-workflow")
skill("tdd-workflow")
skill("security-review")
skill("error-handling")
skill("database-migrations")
skill("deployment-patterns")
skill("docker-patterns")
skill("kubernetes-patterns")  # se usar K8s
```

### Healthcare (Compliance)
```python
skill("codebase-onboarding")
skill("documentation-lookup")
skill("git-workflow")
skill("tdd-workflow")
skill("hipaa-compliance")
skill("healthcare-phi-compliance")
skill("healthcare-emr-patterns")
skill("healthcare-cdss-patterns")
skill("healthcare-eval-harness")
skill("security-review")
```

---

## 🎯 Por Fase do Projeto

### Fase 1: Setup (Semana 1)
```python
skill("codebase-onboarding")      # Entender código existente
skill("documentation-lookup")     # Buscar docs de bibliotecas
skill("git-workflow")             # Configurar versionamento
skill("blueprint")                # Planejar features complexas
```

### Fase 2: Desenvolvimento (Daily)
```python
skill("tdd-workflow")             # Desenvolver com testes
skill("security-review")          # Revisar segurança
skill("error-handling")           # Tratar erros
skill("intent-driven-development") # Clarificar requisitos
```

### Fase 3: Qualidade (Pré-Merge)
```python
skill("code-review-and-quality")  # Revisar código
skill("verification-loop")        # Validar completo
skill("e2e-testing")              # Testar fluxos
skill("security-scan")            # Auditar segurança
```

### Fase 4: Deploy (Production)
```python
skill("deployment-patterns")      # Deploy seguro
skill("docker-patterns")          # Containerização
skill("canary-watch")             # Monitor post-deploy
skill("browser-qa")               # QA visual
```

---

## ⚡ Minimalista (Apenas Essencial)

Se quiser o **mínimo viável** para começar:

```python
# Apenas 5 skills essenciais
skill("codebase-onboarding")    # Entender projeto
skill("documentation-lookup")   # Buscar docs
skill("tdd-workflow")           # Desenvolver bem
skill("security-review")        # Segurança básica
skill("code-review-and-quality") # Qualidade
```

---

## 🎨 Projetos Criativos / Content

```python
skill("article-writing")        # Escrever artigos
skill("content-engine")         # Conteúdo social
skill("banner-design")          # Banners
skill("design")                 # Design geral
skill("ui-ux-pro-max")          # UI/UX
```

---

## 📊 Matriz de Decisão

| Precisa de... | Ative... |
|---------------|----------|
| Entender código novo | `codebase-onboarding` |
| Usar biblioteca nova | `documentation-lookup` |
| Criar feature do zero | `tdd-workflow` + `blueprint` |
| Lidar com auth/dados sensíveis | `security-review` |
| Criar interface bonita | `ui-ux-pro-max` |
| Testar fluxos completos | `e2e-testing` |
| Deploy em produção | `deployment-patterns` |
| Decisão arquitetural importante | `architecture-decision-records` |
| Revisar antes de merge | `code-review-and-quality` |
| Otimizar custos de LLM | `cost-aware-llm-pipeline` |

---

## 📁 Estrutura Recomendada

```
.claude/
├── skills-config.md        # Skills ativas do projeto
├── rules/                  # Regras específicas
└── memory/                 # Memória do projeto
```

Exemplo de `skills-config.md`:

```markdown
# Skills Ativas - Controle de Obras

## Obrigatórias
- [x] codebase-onboarding
- [x] documentation-lookup
- [x] git-workflow

## Development
- [x] tdd-workflow
- [x] security-review
- [x] error-handling

## Projeto-Específicas
- [x] ui-ux-pro-max (design system)
- [x] postgres-patterns (banco)
- [x] reportlab (PDFs)

## Qualidade
- [x] code-review-and-quality
- [x] verification-loop
```

---

## 🚫 Quando NÃO Usar Skills

| Situação | Não Use... | Use... |
|----------|------------|--------|
| Tarefa simples (< 3 passos) | `blueprint` | `gsd-fast` |
| Já sabe como fazer | `documentation-lookup` | Implementação direta |
| Projeto pessoal rápido | Todas as skills | Apenas `tdd-workflow` |
| Agente já está configurado | `configure-ecc` | Trabalhar normalmente |
| Resposta curta necessária | Skills verbose | `token-budget-advisor` |

---

## 💡 Dicas Pro

1. **Comece com 3-5 skills** - Não ative tudo de uma vez
2. **Adicione gradualmente** - Conforme necessidade surgir
3. **Monitore contexto** - Skills consomem tokens
4. **Desative quando não usar** - Limpeza periódica
5. **Documente no projeto** - Mantenha `skills-config.md` atualizado

---

## 🔄 Atualização

Para atualizar esta lista:
1. Liste skills usadas nos últimos 30 dias
2. Remova skills não utilizadas
3. Adicione novas skills descobertas
4. Compartilhe com o time

---

**Versão:** 1.0  
**Última atualização:** 2026-08-18  
**Próxima revisão:** 2026-11-18
