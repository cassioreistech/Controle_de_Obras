# Projeto: Controle de Obras

## Stack
- Language: python
- Framework: 
- Database: 

## ECC Workflow
- Planning: `skill("gsd-plan-phase")` → `agent("planner")`
- TDD: `skill("tdd-workflow")` → `agent("tdd-guide")`
- Review: `skill("code-review")` → `agent("code-reviewer")`
- Security: `skill("security-review")` → `agent("security-reviewer")`

## Commands
- `gsd-next` - Próximo passo inteligente
- `gsd-plan-phase` - Planeja feature
- `gsd-execute-phase` - Executa plano
- `gsd-verify-work` - Valida com UAT

## Hooks (automáticos)
- pre-commit: lint + typecheck + test
- pre-push: full test suite
- commit-msg: conventional commits

## Rules (project-local)
- .claude/rules/ecc/common/
- .claude/rules/ecc/python/
