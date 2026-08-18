# 🧪 Rota de Testes - Template Master

Guia completo para colocar sistemas em rota de testes reais.

**⚠️ ATENÇÃO:** Este template deve ser atualizado periodicamente. Veja os gatilhos abaixo.

**Versão:** 1.0  
**Última atualização:** 2026-08-18  
**Próxima revisão:** 2026-11-18  
**Responsável pela atualização:** [SEU NOME]  

---

## 🔔 Gatilhos de Atualização (IMPORTANTE)

### Quando este template precisa ser atualizado:

| Gatilho | Ação | Skill para Verificar |
|---------|------|---------------------|
| **Nova skill descoberta** | Adicionar na lista | `skill-scout` |
| **Skill desatualizada** | Verificar se há nova versão | `skill-stocktake` |
| **Mudança de stack** | Atualizar templates por projeto | `documentation-lookup` |
| **Processo mudou** | Revisar fluxo | `continuous-learning-v2` |
| **Time cresceu** | Adaptar workflows | `agentic-engineering` |
| **3 meses sem revisão** | Revisão geral | `benchmark` |
| **Nova tecnologia** | Adicionar exemplos | `documentation-lookup` |
| **Erro em produção** | Atualizar matriz de risco | `verification-loop` |
| **Feedback de usuários** | Melhorar templates | `growth-log` |

---

### 🚨 Alertas Automáticos (Configurar no Projeto)

```markdown
# ATUALIZAÇÕES PENDENTES
- [ ] Próxima revisão em: {{DATA + 90 dias}}
- [ ] Skills para verificar: `skill-stocktake`
- [ ] Processo para revisar: `continuous-learning-v2`
- [ ] Template para atualizar: ROTA_DE_TESTES_TEMPLATE.md

# NOTIFICAÇÕES CONFIGURADAS
- [ ] Lembrete trimestral no calendário
- [ ] CI check para versões desatualizadas
- [ ] Hook pre-commit para verificar docs
```

---

### 📝 Log de Mudanças (Preencher a Cada Atualização)

```markdown
## Histórico de Atualizações

### v1.0 - 2026-08-18
- **Criado por:** [SEU NOME]
- **Mudanças:** Versão inicial
- **Skills verificadas:** codebase-onboarding, tdd-workflow
- **Próxima revisão:** 2026-11-18

### v{{N}} - {{DATA}}
- **Atualizado por:** [NOME]
- **Mudanças:** {{DESCRÇÃO}}
- **Skills adicionadas:** {{SKILLS}}
- **Skills removidas:** {{SKILLS}}
- **Motivo:** {{JUSTIFICATIVA}}
- **Próxima revisão:** {{DATA + 90 dias}}
```

---

---

---

## 🔄 Script de Atualização Automática

### Criar Hook de Verificação (Recomendado)

```bash
# .git/hooks/pre-commit (adicionar no final)
#!/bin/bash

# Verificar idade do template
TEMPLATE_FILE="docs/ROTA_DE_TESTES_TEMPLATE.md"
if [ -f "$TEMPLATE_FILE" ]; then
    LAST_MODIFIED=$(stat -f %m "$TEMPLATE_FILE" 2>/dev/null || stat -c %Y "$TEMPLATE_FILE")
    CURRENT_TIME=$(date +%s)
    AGE_DAYS=$(( (CURRENT_TIME - LAST_MODIFIED) / 86400 ))
    
    if [ $AGE_DAYS -gt 90 ]; then
        echo "⚠️  ATENÇÃO: Template com $AGE_DAYS dias sem atualização!"
        echo "Execute: skill('skill-stocktake') para verificar atualizações"
        echo ""
        # Não bloqueia, apenas avisa
    fi
fi
```

---

### Script Python de Verificação

```python
# tests/check_template_update.py
"""
Verifica setemplate precisa de atualização.
Rodar: python tests/check_template_update.py
"""

import os
from datetime import datetime, timedelta

TEMPLATE_PATH = "docs/ROTA_DE_TESTES_TEMPLATE.md"
MAX_AGE_DAYS = 90

def check_template_age():
    """Verifica idade do template."""
    if not os.path.exists(TEMPLATE_PATH):
        print(f"❌ Template não encontrado: {TEMPLATE_PATH}")
        return False
    
    mtime = os.path.getmtime(TEMPLATE_PATH)
    last_modified = datetime.fromtimestamp(mtime)
    age = datetime.now() - last_modified
    
    print(f"📄 Template: {TEMPLATE_PATH}")
    print(f"📅 Última atualização: {last_modified.strftime('%Y-%m-%d')}")
    print(f"⏰ Idade: {age.days} dias")
    
    if age.days > MAX_AGE_DAYS:
        print(f"\n⚠️  ALERTA: Template está desatualizado!")
        print(f"   Execute estas skills para atualizar:")
        print(f"   - skill('skill-stocktake')")
        print(f"   - skill('skill-scout')")
        print(f"   - skill('documentation-lookup')")
        return False
    else:
        print(f"\n✅ Template atualizado!")
        return True

def check_skills_versions():
    """Verifica se há novas versões de skills."""
    print("\n🔍 Verificando versões de skills...")
    print("   Execute: skill('skill-stocktake')")
    print("   Execute: skill('skill-scout')")
    return True

if __name__ == "__main__":
    print("="*50)
    print("VERIFICAÇÃO DE ATUALIZAÇÃO DO TEMPLATE")
    print("="*50)
    
    template_ok = check_template_age()
    skills_ok = check_skills_versions()
    
    if template_ok and skills_ok:
        print("\n✅ Tudo atualizado!")
        exit(0)
    else:
        print("\n⚠️  Atualizações pendentes!")
        exit(1)
```

---

### Configurar CI Check (GitHub Actions)

```yaml
# .github/workflows/check-template-update.yml
name: Check Template Update

on:
  schedule:
    - cron: '0 0 * * 1'  # Toda segunda-feira
  workflow_dispatch:

jobs:
  check-template:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check template age
        run: |
          python tests/check_template_update.py
          
      - name: Notify if outdated
        if: failure()
        run: |
          echo "⚠️ Template desatualizado!"
          echo "Execute as skills de atualização"
```

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Skills por Fase](#skills-por-fase)
3. [Checklist de Validação](#checklist-de-validação)
4. [Workflow Diário](#workflow-diário)
5. [Templates por Tipo de Projeto](#templates-por-tipo-de-projeto)
6. [Matriz de Risco](#matriz-de-risco)
7. [Exemplos Práticos](#exemplos-práticos)

---

## 🎯 Visão Geral

### Objetivo
Colocar sistemas em **rota de testes reais** com validação progressiva e segura.

### Duração Estimada
- **Mínimo:** 4 semanas (projeto simples)
- **Padrão:** 6 semanas (projeto fullstack)
- **Completo:** 8-10 semanas (sistema crítico)

### Pré-requisitos
- [ ] Sistema funcional (MVP pronto)
- [ ] Código versionado (Git)
- [ ] Ambiente de testes configurado
- [ ] Dados de exemplo disponíveis

---

## 📊 Skills por Fase

### 🔍 Verificação de Skills Atualizadas

Antes de iniciar cada fase, execute:

```python
# Verificar se há skills atualizadas
skill("skill-scout")          # Buscar novas skills
skill("skill-stocktake")      # Auditar qualidade das skills
skill("documentation-lookup") # Verificar docs atualizadas
```

**⚠️ ALERTA:** Se alguma skill estiver desatualizada (>3 meses), atualize antes de prosseguir.

---

### Fase 1: Fundamentos (Semana 1-2)
**Objetivo:** Garantir base sólida de testes unitários

```python
# Skills obrigatórias
skill("tdd-workflow")           # Desenvolvimento com testes
skill("security-review")        # Segurança no código
skill("documentation-lookup")   # Documentação de APIs/bibliotecas

# Validação
# ✅ Cobertura de testes ≥80%
# ✅ Services testados
# ✅ Repositórios testados
# ✅ Validações cobertas
```

**Entregáveis:**
- [ ] Testes unitários para todas as functions
- [ ] Testes de unidade para services
- [ ] Validações de input testadas
- [ ] Edge cases documentados

---

### Fase 2: Integração (Semana 2-3)
**Objetivo:** Validar fluxos completos e dados

```python
# Skills obrigatórias
skill("e2e-testing")            # Testes end-to-end
skill("database-migrations")    # Migrations seguras

# Validação
# ✅ Fluxos críticos testados
# ✅ Migrations testadas
# ✅ Rollback validado
# ✅ Dados preservados
```

**Entregáveis:**
- [ ] Testes E2E para fluxos principais
- [ ] Script de migration testado
- [ ] Rollback testado
- [ ] Backup automático configurado

---

### Fase 3: Validação Visual (Semana 3-4)
**Objetivo:** Garantir UI consistente e responsiva

```python
# Skills obrigatórias
skill("ui-demo")                # Gravar demos de UI
skill("browser-qa")             # QA visual entre navegadores

# Validação
# ✅ Responsividade (desktop, tablet, mobile)
# ✅ Consistência entre browsers
# ✅ Sem console errors
# ✅ Acessibilidade básica
```

**Entregáveis:**
- [ ] Demo gravada dos fluxos principais
- [ ] Teste visual em Chrome, Firefox, Safari
- [ ] Responsividade validada
- [ ] Console errors zerados

---

### Fase 4: Segurança (Semana 4-5)
**Objetivo:** Validar segurança e compliance

```python
# Skills obrigatórias
skill("security-review")        # Revisão manual de segurança
skill("security-scan")          # Scan automatizado

# Validação
# ✅ Inputs validados
# ✅ SQL injection prevenido
# ✅ XSS prevenido
# ✅ Secrets protegidos
# ✅ APIs autenticadas
```

**Entregáveis:**
- [ ] Revisão de segurança completa
- [ ] Scan automatizado sem críticos
- [ ] Validações de input implementadas
- [ ] Secrets em cofre/variáveis de ambiente

---

### Fase 5: Deploy e Monitoramento (Semana 5-6)
**Objetivo:** Preparar para produção com segurança

```python
# Skills obrigatórias
skill("deployment-patterns")    # Deploy seguro
skill("canary-watch")           # Monitoramento post-deploy

# Validação
# ✅ Docker build funcional
# ✅ Health checks respondem
# ✅ Logs gerados
# ✅ Backup automático
# ✅ Smoke tests passando
```

**Entregáveis:**
- [ ] Container Docker funcional
- [ ] Health check implementado
- [ ] Logs estruturados
- [ ] Backup automático testado
- [ ] Smoke tests configurados

---

### Fase 6: Performance (Opcional, Semana 6-8)
**Objetivo:** Otimizar performance e escalabilidade

```python
# Skills opcionais
skill("benchmark")                      # Baseline de performance
skill("data-throughput-accelerator")    # Big data handling
skill("latency-critical-systems")       # Sistemas realtime

# Validação (se aplicável)
# ✅ Baseline estabelecida
# ✅ Regressões detectadas
# ✅ Throughput adequado
# ✅ Latência dentro do SLA
```

**Entregáveis:**
- [ ] Baseline de performance
- [ ] Testes de carga
- [ ] Otimizações aplicadas
- [ ] SLA definido

---

## ✅ Checklist de Validação

### Checklist Mestre (Copiar e Colar)

```markdown
# Validação - [Nome do Sistema]

## Fase 1: Fundamentos
- [ ] `tdd-workflow` ativo
- [ ] Cobertura de testes ≥80%
- [ ] Services testados
- [ ] Repositórios testados
- [ ] Validações cobertas
- [ ] Edge cases documentados

## Fase 2: Integração
- [ ] `e2e-testing` configurado
- [ ] Fluxos principais testados
- [ ] Migrations testadas
- [ ] Rollback validado
- [ ] Backup configurado

## Fase 3: Visual
- [ ] `ui-demo` gravado
- [ ] `browser-qa` passou
- [ ] Responsividade OK
- [ ] Sem console errors
- [ ] Acessibilidade básica

## Fase 4: Segurança
- [ ] `security-review` passou
- [ ] `security-scan` sem críticos
- [ ] Inputs validados
- [ ] SQL injection prevenido
- [ ] XSS prevenido
- [ ] Secrets protegidos

## Fase 5: Deploy
- [ ] `deployment-patterns` OK
- [ ] `canary-watch` configurado
- [ ] Docker build OK
- [ ] Health check OK
- [ ] Logs OK
- [ ] Backup testado

## Fase 6: Performance (Opcional)
- [ ] `benchmark` baseline
- [ ] Testes de carga
- [ ] SLA definido
- [ ] Otimizações aplicadas
```

---

## 📅 Workflow Diário

### Manhã (Planejamento - 30min)
```python
skill("blueprint")              # Planejar tasks do dia
skill("intent-driven-development")  # Clarificar requisitos
```

**Checklist:**
- [ ] Definir 3-5 tarefas prioritárias
- [ ] Clarificar critérios de aceite
- [ ] Identificar dependências
- [ ] Estimar tempo por tarefa

---

### Durante o Dia (Execução)
```python
skill("tdd-workflow")           # Desenvolver com testes
skill("security-review")        # Revisar segurança
skill("documentation-lookup")   # Buscar docs quando necessário
```

**Checklist por tarefa:**
- [ ] Escrever teste primeiro (TDD)
- [ ] Implementar feature
- [ ] Revisar segurança
- [ ] Rodar testes locais
- [ ] Commitar com mensagem clara

---

### Final do Dia (Validação - 1h)
```python
skill("verification-loop")      # Validar completo
skill("code-review-and-quality") # Revisar qualidade
skill("growth-log")             # Capturar aprendizados
```

**Checklist:**
- [ ] Validar critérios de aceite
- [ ] Revisar código (qualidade)
- [ ] Rodar suíte de testes
- [ ] Capturar aprendizados
- [ ] Atualizar documentação

---

### Pré-Commit (Gatilhos Automáticos)
```python
skill("e2e-testing")            # Testes E2E
skill("browser-qa")             # QA visual (se UI mudou)
skill("security-scan")          # Scan de segurança (se auth mudou)
```

** Gatilhos:**
- [ ] Push para branch de feature → Rodar testes unitários
- [ ] PR aberto → Rodar E2E + code review
- [ ] PR aprovado → Rodar security scan
- [ ] Merge para master → Deploy + canary watch

---

## 📦 Templates por Tipo de Projeto

### Template 1: Fullstack Web (React + Python)

```python
# Setup inicial (Dia 1)
skill("codebase-onboarding")
skill("documentation-lookup")
skill("git-workflow")

# Fase 1: Fundamentos
skill("tdd-workflow")
skill("security-review")
skill("error-handling")

# Fase 2: Integração
skill("e2e-testing")            # Playwright
skill("database-migrations")    # Alembic/Prisma

# Fase 3: Visual
skill("ui-demo")
skill("browser-qa")
skill("ui-ux-pro-max")

# Fase 4: Segurança
skill("security-scan")

# Fase 5: Deploy
skill("deployment-patterns")
skill("canary-watch")
skill("docker-patterns")
```

**Duração estimada:** 6 semanas

---

### Template 2: Backend API (Python/Node)

```python
# Setup inicial
skill("codebase-onboarding")
skill("documentation-lookup")
skill("git-workflow")

# Fase 1: Fundamentos
skill("tdd-workflow")
skill("security-review")
skill("error-handling")

# Fase 2: Integração
skill("e2e-testing")            # API tests
skill("database-migrations")

# Fase 4: Segurança
skill("security-scan")
skill("hipaa-compliance")       # Se healthcare

# Fase 5: Deploy
skill("deployment-patterns")
skill("canary-watch")
skill("docker-patterns")
skill("kubernetes-patterns")    # Se K8s

# Fase 6: Performance
skill("benchmark")
skill("latency-critical-systems")
```

**Duração estimada:** 5 semanas

---

### Template 3: Mobile (iOS/Swift)

```python
# Setup inicial
skill("codebase-onboarding")
skill("documentation-lookup")
skill("git-workflow")

# Fase 1: Fundamentos
skill("tdd-workflow")
skill("security-review")

# Mobile específico
skill("swiftui-patterns")
skill("swift-concurrency-6-2")
skill("swift-protocol-di-testing")

# Fase 3: Visual
skill("ui-demo")

# Fase 4: Segurança
skill("security-scan")

# Fase 5: Deploy
skill("deployment-patterns")    # TestFlight/App Store
```

**Duração estimada:** 6 semanas

---

### Template 4: Data Science / Analytics

```python
# Setup inicial
skill("codebase-onboarding")
skill("documentation-lookup")
skill("git-workflow")

# Fase 1: Fundamentos
skill("tdd-workflow")
skill("security-review")

# Data específico
skill("postgres-patterns")
skill("clickhouse-io")
skill("data-throughput-accelerator")

# Fase 2: Integração
skill("database-migrations")

# Fase 6: Performance
skill("benchmark")
skill("data-throughput-accelerator")
```

**Duração estimada:** 5 semanas

---

### Template 5: Healthcare (Compliance Crítico)

```python
# Setup inicial
skill("codebase-onboarding")
skill("documentation-lookup")
skill("git-workflow")

# Fase 1: Fundamentos
skill("tdd-workflow")
skill("security-review")

# Healthcare compliance
skill("hipaa-compliance")
skill("healthcare-phi-compliance")
skill("healthcare-emr-patterns")
skill("healthcare-cdss-patterns")

# Fase 2: Integração
skill("e2e-testing")

# Fase 4: Segurança (Reforçado)
skill("security-scan")
skill("healthcare-eval-harness")    # Patient safety

# Fase 5: Deploy
skill("deployment-patterns")
skill("canary-watch")
```

**Duração estimada:** 8-10 semanas (compliance extra)

---

## ⚠️ Matriz de Risco

| Risco | Impacto | Teste | Skill | Frequência | Gatilho |
|-------|---------|-------|-------|------------|---------|
| **Perda de dados** | Crítico | Migration rollback | `database-migrations` | Toda migration | Schema change |
| **Vazamento de dados** | Crítico | Security audit | `security-review` | Toda feature | Auth/dados sensíveis |
| **Feature quebrada** | Alto | Validação funcional | `verification-loop` | Toda feature | Merge |
| **Regressão** | Alto | Testes automatizados | `tdd-workflow` | Todo commit | Code change |
| **UI quebrada** | Médio | QA visual | `browser-qa` | Pré-deploy | UI change |
| **Performance** | Médio | Benchmark | `benchmark` | Mensal | Data growth |
| **Downtime** | Alto | Health checks | `canary-watch` | Pós-deploy | Deploy |
| **Compliance** | Crítico | Patient safety eval | `healthcare-eval-harness` | Toda feature | Healthcare feature |

---

## 🧪 Exemplos Práticos

### Exemplo 1: Testar Fluxo de Login

```python
skill("e2e-testing")

# Fluxo a testar
fluxo = """
1. Acessar /login
2. Preencher email e senha
3. Clicar em "Entrar"
4. Verificar redirect para /dashboard
5. Verificar cards de resumo
6. Clicar em "Sair"
7. Verificar redirect para /login
"""

# Playwright test
test_login = """
import pytest
from playwright.sync_api import Page

def test_login_sucesso(page: Page, base_url: str):
    page.goto(f"{base_url}/login")
    page.fill("input[name='email']", "usuario@teste.com")
    page.fill("input[name='senha']", "senha123")
    page.click("button[type='submit']")
    page.wait_for_url(f"{base_url}/dashboard")
    assert page.is_visible("text=Dashboard")
    assert page.is_visible("text=Resumo Financeiro")
"""
```

---

### Exemplo 2: Testar Geração de PDF

```python
skill("tdd-workflow")

# Teste unitário
test_gerar_pdf = """
def test_gerar_relatorio_pdf():
    # Arrange
    obra = criar_obra_exemplo()
    service = RelatorioService()
    
    # Act
    pdf_path = service.gerar_relatorio(obra.id)
    
    # Assert
    assert pdf_path.exists()
    assert pdf_path.suffix == ".pdf"
    
    # Validar conteúdo
    pdf = PdfReader(pdf_path)
    assert len(pdf.pages) >= 1
    assert "RELATORIO" in pdf.pages[0].extract_text()
"""
```

---

### Exemplo 3: Validar Responsividade

```python
skill("browser-qa")

# Viewports para testar
viewports = [
    {"width": 1920, "height": 1080, "name": "Desktop Grande"},
    {"width": 1440, "height": 900, "name": "Desktop Padrão"},
    {"width": 1366, "height": 768, "name": "Notebook"},
    {"width": 1024, "height": 768, "name": "Tablet"},
    {"width": 390, "height": 844, "name": "Celular"},
]

# Teste Playwright
for viewport in viewports:
    page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
    page.goto("http://localhost:3000/dashboard")
    assert page.is_visible("text=Dashboard")
    assert not page.locator("body").evaluate("el => el.scrollWidth > el.clientWidth")
```

---

### Exemplo 4: Testar Migração de Banco

```python
skill("database-migrations")

# Migration script
migration = """
-- Adicionar coluna de ativo
ALTER TABLE obras ADD COLUMN ativo BOOLEAN DEFAULT TRUE;

-- Migrar dados existentes
UPDATE obras SET ativo = TRUE WHERE status NOT IN ('cancelada', 'finalizada');

-- Rollback
-- ALTER TABLE obras DROP COLUMN ativo;
"""

# Teste de migration
test_migration = """
def test_adicionar_coluna_ativo():
    # Antes
    assert not column_exists("obras", "ativo")
    
    # Executar migration
    run_migration("001_add_ativo_column.sql")
    
    # Depois
    assert column_exists("obras", "ativo")
    
    # Rollback
    run_migration("001_add_ativo_column.sql", rollback=True)
    assert not column_exists("obras", "ativo")
"""
```

---

## 📊 Dashboard de Progresso

### Template de Status (Atualizar Semanalmente)

```markdown
# Status de Testes - [Sistema]

## Semana 1 ({{DATA}})
- **Fase:** Fundamentos
- **Progresso:** 30%
- **Skills Ativas:** tdd-workflow, security-review
- **Entregáveis:** ✅ Tests unitários services
- **Bloqueios:** Nenhum

## Semana 2 ({{DATA}})
- **Fase:** Fundamentos
- **Progresso:** 60%
- **Skills Ativas:** tdd-workflow, e2e-testing
- **Entregáveis:** ✅ Tests unitários repos, ✅ E2E login
- **Bloqueios:** Aguardando seed de dados

## Semana 3 ({{DATA}})
- **Fase:** Integração
- **Progresso:** 80%
- **Skills Ativas:** e2e-testing, database-migrations
- **Entregáveis:** ✅ Fluxos E2E completos
- **Bloqueios:** Nenhum

## Semana 4 ({{DATA}})
- **Fase:** Validação Visual
- **Progresso:** 90%
- **Skills Ativas:** ui-demo, browser-qa
- **Entregáveis:** ✅ Demo gravada, ✅ QA visual
- **Bloqueios:** Nenhum

## Semana 5 ({{DATA}})
- **Fase:** Segurança
- **Progresso:** 95%
- **Skills Ativas:** security-review, security-scan
- **Entregáveis:** ✅ Review de segurança
- **Bloqueios:** Nenhum

## Semana 6 ({{DATA}})
- **Fase:** Deploy
- **Progresso:** 100%
- **Skills Ativas:** deployment-patterns, canary-watch
- **Entregáveis:** ✅ Deploy em produção
- **Bloqueios:** Nenhum
```

---

## 🚀 Quick Start (5 minutos)

### Passo 1: Copiar Template
```bash
# Criar estrutura de testes
mkdir -p tests/{unit,integration,e2e,visual}
touch tests/README.md
touch tests/requirements.txt
```

### Passo 2: Ativar Skills Básica
```python
skill("codebase-onboarding")
skill("tdd-workflow")
skill("verification-loop")
```

### Passo 3: Rodar Primeiro Teste
```python
# Criar teste Hello World
# tests/test_hello.py
def test_hello():
    assert True

# Rodar
pytest tests/test_hello.py
```

### Passo 4: Configurar CI/CD
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest tests/
```

### Passo 5: Monitorar Progresso
```bash
# Atualizar dashboard semanalmente
code docs/TESTES_PROGRESSO.md
```

---

## 💡 Dicas de Ouro

### ✅ DO
- Comece com testes simples e aumente complexidade
- Use TDD para features críticas
- Documente aprendizados em growth-log
- Valide segurança cedo (não deixe para o final)
- Automatize o máximo possível

### ❌ NÃO
- Não pule testes de integração
- Não ignore warnings de segurança
- Não adie testes de UI/UX
- Não esqueça de testar rollback
- Não deploy sem smoke tests

---

## 📞 Escalando Issues

| Issue | Severidade | Ação | Skill para Ajuda |
|-------|------------|------|------------------|
| Bug crítico em produção | 🔴 Crítico | Rollback imediato | `safety-guard` |
| Vazamento de dados | 🔴 Crítico | Patch de emergência | `security-review` |
| Feature não funciona | 🟠 Alto | Hotfix | `verification-loop` |
| Testes falhando | 🟡 Médio | Investigar e corrigir | `tdd-workflow` |
| Performance abaixo | 🟢 Baixo | Otimizar na próxima sprint | `benchmark` |

---

## 📁 Arquivos do Template

```
docs/
├── ROTA_DE_TESTES_TEMPLATE.md       # Este arquivo master
├── SKILLS_ESSENCIAIS.md             # Guia de skills
├── SKILLS_CONFIG_TEMPLATE.md        # Config de skills
└── TESTES_PROGRESSO.md              # Dashboard (copiar)

tests/
├── README.md                         # Instruções
├── requirements.txt                  # Dependências
├── unit/                             # Testes unitários
├── integration/                      # Testes de integração
├── e2e/                              # Testes E2E
└── visual/                           # Testes visuais
```

---

## 🔄 Atualização do Template

**Revisar e atualizar:**
- A cada 3 meses
- Quando nova skill for descoberta
- Quando processo mudar
- Quando time crescer

**Contribuidores:**
- Adicionar aprendizados
- Melhorar exemplos
- Refinar matrizes
- Compartilhar com outros projetos

---

**Este template é seu! Adapte conforme necessidade do projeto.** 🚀

Pronto para começar? Me avise que inicio o passo-a-passo no seu sistema atual! 😊
