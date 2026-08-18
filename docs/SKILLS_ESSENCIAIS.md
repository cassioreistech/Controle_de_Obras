# Skills Essenciais para Novos Projetos

Guia prático de skills para configurar rapidamente novos sistemas.

---

## 🚀 Setup Inicial (Obrigatório)

### 1. Codebase Onboarding
```python
skill("codebase-onboarding")
```
**O que faz:** Analisa o código existente e gera documentação automática  
**Quando usar:** Primeiro dia em qualquer projeto novo

### 2. Documentation Lookup
```python
skill("documentation-lookup")
```
**O que faz:** Busca documentação atualizada de bibliotecas e frameworks  
**Quando usar:** Sempre que for usar uma API/biblioteca nova

### 3. Git Workflow
```python
skill("git-workflow")
```
**O que faz:** Padroniza branches, commits, merges e convenções  
**Quando usar:** Setup inicial do repositório

---

## 💻 Desenvolvimento (Daily Use)

### 4. TDD Workflow
```python
skill("tdd-workflow")
```
**O que faz:** Guia desenvolvimento com testes (80%+ coverage)  
**Quando usar:** Criar features, fixar bugs, refatorar

### 5. Security Review
```python
skill("security-review")
```
**O que faz:** Revisa segurança de autenticação, inputs, secrets, APIs  
**Quando usar:** Implementar auth, lidar com dados sensíveis, criar endpoints

### 6. Error Handling
```python
skill("error-handling")
```
**O que faz:** Padroniza tratamento de erros em TS/Python/Go  
**Quando usar:** Criar APIs, lidar com falhas, definir tipos de erro

### 7. Database Migrations
```python
skill("database-migrations")
```
**O que faz:** Guia migrations seguras (zero downtime)  
**Quando usar:** Mudar schema, migrar dados, fazer rollback

---

## 🎨 Frontend/UI (Se aplicável)

### 8. UI/UX Pro Max
```python
skill("ui-ux-pro-max")
```
**O que faz:** 79 styles, 192 paletas, 119 guidelines de UX  
**Quando usar:** Criar interfaces, componentes, design systems

### 9. Design System
```python
skill("design-system")
```
**O que faz:** Tokens, componentes, slides, CSS variables  
**Quando usar:** Criar sistema de design consistente

### 10. UI Styling
```python
skill("ui-styling")
```
**O que faz:** shadcn/ui, Tailwind, componentes acessíveis  
**Quando usar:** Estilizar componentes, criar layouts

---

## 🧪 Qualidade & Testes

### 11. Code Review and Quality
```python
skill("code-review-and-quality")
```
**O que faz:** Revisão multi-critério antes de merge  
**Quando usar:** Antes de qualquer merge, PR review

### 12. E2E Testing
```python
skill("e2e-testing")
```
**O que faz:** Playwright, Page Object Model, CI/CD  
**Quando usar:** Testes end-to-end, fluxos críticos

### 13. Verification Loop
```python
skill("verification-loop")
```
**O que faz:** Valida se o trabalho está completo antes de entregar  
**Quando usar:** Antes de declarar tarefa como "pronta"

---

## 📊 Planejamento & Gestão

### 14. Blueprint
```python
skill("blueprint")
```
**O que faz:** Cria plano passo-a-passo para projetos complexos  
**Quando usar:** Projeto com 3+ passos, multi-PR, multi-sessão

### 15. Intent Driven Development
```python
skill("intent-driven-development")
```
**O que faz:** Transforma requisitos ambíguos em critérios de aceite  
**Quando usar:** Feature complexa, security/data/migration/integration

### 16. Architecture Decision Records
```python
skill("architecture-decision-records")
```
**O que faz:** Captura decisões arquiteturais como ADRs estruturados  
**Quando usar:** Decidir arquitetura, padrões, tecnologias

---

## 🛡️ Segurança (Crítico)

### 17. Security Scan
```python
skill("security-scan")
```
**O que faz:** Scaneia configuração em busca de vulnerabilidades  
**Quando usar:** Setup inicial, auditoria de segurança

### 18. Safety Guard
```python
skill("safety-guard")
```
**O que faz:** Previne operações destrutivas em produção  
**Quando usar:** Agentes autônomos, production access

---

## 📦 Deploy & DevOps

### 19. Deployment Patterns
```python
skill("deployment-patterns")
```
**O que faz:** CI/CD, Docker, health checks, rollback  
**Quando usar:** Deploy, containerizar, production readiness

### 20. Docker Patterns
```python
skill("docker-patterns")
```
**O que faz:** Dockerfiles, Compose, volumes, redes, segurança  
**Quando usar:** Containerizar serviços, multi-service

### 21. Kubernetes Patterns
```python
skill("kubernetes-patterns")
```
**O que faz:** K8s manifests, RBAC, probes, autoscaling  
**Quando usar:** Deploy em Kubernetes, production-grade

---

## 🔧 Utilitários (Nice to Have)

### 22. Prompt Optimizer
```python
skill("prompt-optimizer")
```
**O que faz:** Melhora prompts para melhor qualidade de resposta  
**Quando usar:** Prompt complexo, alta importância

### 23. Token Budget Advisor
```python
skill("token-budget-advisor")
```
**O que faz:** Oferece controle sobre profundidade da resposta  
**Quando usar:** Respostas longas, controle de tokens

### 24. Growth Log
```python
skill("growth-log")
```
**O que faz:** Captura aprendizados após tarefas complexas  
**Quando usar:** Após falha, tarefa complexa, review de sprint

### 25. Cost Aware LLM Pipeline
```python
skill("cost-aware-llm-pipeline")
```
**O que faz:** Otimiza custos de LLM por task complexity  
**Quando usar:** LLM spend alto, model routing

---

## 📁 Skills Específicas por Stack

### Python Backend
```python
skill("django-security")         # Django auth, CSRF, XSS
skill("laravel-security")        # Laravel auth, Eloquent
skill("prisma-patterns")         # Prisma ORM TypeScript
skill("jpa-patterns")            # JPA/Hibernate Java
skill("postgres-patterns")       # PostgreSQL otimização
skill("mysql-patterns")          # MySQL/MariaDB
skill("redis-patterns")          # Redis caching, locks
```

### Frontend Específico
```python
skill("swiftui-patterns")        # SwiftUI iOS
skill("swift-concurrency-6-2")   # Swift 6.2 concurrency
skill("e2e-testing")             # Playwright web
skill("windows-desktop-e2e")     # Pywinauto desktop
```

### Blockchain/Web3
```python
skill("defi-amm-security")       # AMM Solidity
skill("evm-token-decimals")      # EVM decimals
skill("nodejs-keccak256")        # Ethereum hashing JS
```

### Healthcare (Compliance)
```python
skill("hipaa-compliance")        # HIPAA EUA
skill("healthcare-phi-compliance")  # PHI/PII
skill("healthcare-emr-patterns")    # EMR/EHR
skill("healthcare-cdss-patterns")   # CDSS clínico
skill("healthcare-eval-harness")    # Patient safety evals
```

### Redes/Homelab
```python
skill("cisco-ios-patterns")      # Cisco IOS
skill("netmiko-ssh-automation")  # Python Netmiko
skill("homelab-network-setup")   # Home network
skill("homelab-vlan-segmentation")  # VLANs
skill("homelab-wireguard-vpn")   # WireGuard
skill("homelab-pihole-dns")      # Pi-hole
```

---

## 📋 Checklist de Setup por Tipo de Projeto

### Projeto Backend Python
```python
skills = [
    "codebase-onboarding",
    "documentation-lookup",
    "git-workflow",
    "tdd-workflow",
    "security-review",
    "error-handling",
    "database-migrations",
    "security-scan",
    "pytest-patterns",  # (se existir)
    "prisma-patterns" if typescript else "django-security",
]
```

### Projeto Fullstack Web
```python
skills = [
    "codebase-onboarding",
    "documentation-lookup",
    "git-workflow",
    "tdd-workflow",
    "security-review",
    "ui-ux-pro-max",
    "design-system",
    "e2e-testing",
    "code-review-and-quality",
    "deployment-patterns",
]
```

### Projeto Mobile iOS
```python
skills = [
    "codebase-onboarding",
    "documentation-lookup",
    "git-workflow",
    "tdd-workflow",
    "swiftui-patterns",
    "swift-concurrency-6-2",
    "security-review",
    "code-review-and-quality",
]
```

### Projeto Data/Analytics
```python
skills = [
    "codebase-onboarding",
    "documentation-lookup",
    "git-workflow",
    "tdd-workflow",
    "postgres-patterns",
    "clickhouse-io",  # se usar ClickHouse
    "data-throughput-accelerator",
    "security-review",
]
```

---

## 🚫 Skills que NÃO usar (a menos que necessário)

- `agent-payment-x402` - Só se agente for pagar algo
- `defi-amm-security` - Só se for DeFi/AMM
- `healthcare-*` - Só se for healthcare
- `homelab-*` - Só se for rede/homelab
- `ito-*` - Só se for GPU/compute
- `prediction-market-*` - Só se for prediction market
- `agent-eval` - Só se estiver avaliando agents

---

## 📞 Como Ativar

### Método 1: Skill Individual
```python
skill("nome-da-skill")
```

### Método 2: Skill com Parâmetros
```python
skill("security-review", type="code", severity="high")
```

### Método 3: Múltiplas Skills
```python
for skill_name in ["tdd-workflow", "security-review", "code-review-and-quality"]:
    skill(skill_name)
```

---

## 📊 Matriz de Prioridade

| Prioridade | Skills | Quando |
|------------|--------|--------|
| **P0** | codebase-onboarding, documentation-lookup, git-workflow | Dia 1 |
| **P1** | tdd-workflow, security-review, error-handling | Daily dev |
| **P2** | code-review-and-quality, e2e-testing, deployment-patterns | Pré-merge |
| **P3** | blueprint, architecture-decision-records | Complexo |
| **P4** | token-budget-advisor, growth-log | Nice to have |

---

## 💡 Dicas de Uso

1. **Comece leve:** Ative 3-5 skills essenciais no início
2. **Adicione conforme necessidade:** Não ative tudo de uma vez
3. **Monitore contexto:** Skills consomem tokens de contexto
4. **Documente decisões:** Use `architecture-decision-records` para escolhas importantes
5. **Sempre revise:** `code-review-and-quality` antes de merge

---

## 📁 Exemplo de Configuração

Crie um arquivo `.claude/skills-config.md` no projeto:

```markdown
# Skills Ativas - [Nome do Projeto]

## Setup Inicial
- [x] codebase-onboarding
- [x] documentation-lookup
- [x] git-workflow

## Daily Development
- [x] tdd-workflow
- [x] security-review
- [x] error-handling

## Específicas do Projeto
- [x] ui-ux-pro-max (frontend)
- [x] postgres-patterns (backend)
- [x] prisma-patterns (ORM)

## Qualidade
- [x] code-review-and-quality
- [x] e2e-testing
```

---

**Última atualização:** 2026-08-18  
**Manter atualizado:** Adicionar novas skills conforme necessário  
**Revisar:** A cada 3 meses ou quando stack mudar
