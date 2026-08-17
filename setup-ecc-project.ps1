<#
.SYNOPSIS
    Inicializa projeto novo com ECC (rules, skills, agents, hooks) - Windows PowerShell
.DESCRIPTION
    Copia rules do ECC global para o projeto, cria estrutura .claude e arquivos de configuração.
.PARAMETER Stack
    Stack tecnológica: python, typescript, go, rust, java (default: python)
.EXAMPLE
    .\setup-ecc-project.ps1
    .\setup-ecc-project.ps1 -Stack python
    .\setup-ecc-project.ps1 -Stack typescript
#>

param(
    [ValidateSet('python', 'typescript', 'go', 'rust', 'java')]
    [string]$Stack = 'python'
)

$ErrorActionPreference = "Stop"

# Cores
$GREEN = [ConsoleColor]::Green
$YELLOW = [ConsoleColor]::Yellow
$BLUE = [ConsoleColor]::Cyan
$RED = [ConsoleColor]::Red
$RESET = [ConsoleColor]::Gray

function Log-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor $BLUE }
function Log-Ok { param($msg) Write-Host "[OK]   $msg" -ForegroundColor $GREEN }
function Log-Warn { param($msg) Write-Host "[WARN] $msg" -ForegroundColor $YELLOW }
function Log-Err { param($msg) Write-Host "[ERR]  $msg" -ForegroundColor $RED }

$ECC_CONFIG_DIR = "$env:USERPROFILE\.config\opencode"
$PROJECT_DIR = Get-Location

Log-Info "Inicializando projeto ECC em: $PROJECT_DIR"
Log-Info "Stack: $Stack"

# 1. Verifica ECC global
if (-not (Test-Path "$ECC_CONFIG_DIR\rules\ecc")) {
    Log-Err "ECC não encontrado em $ECC_CONFIG_DIR\rules\ecc"
    Log-Err "Execute primeiro a instalação global do ECC"
    exit 1
}

# 2. Cria estrutura .claude
Log-Info "Criando estrutura .claude/"
@(
    ".claude\rules\ecc",
    ".claude\agents",
    ".claude\commands",
    ".claude\hooks",
    ".claude\skills"
) | ForEach-Object {
    if (-not (Test-Path $_)) { New-Item -ItemType Directory -Path $_ -Force | Out-Null }
}

# 3. Copia rules (common + stack)
Log-Info "Copiando rules (common + $Stack)..."
Copy-Item "$ECC_CONFIG_DIR\rules\ecc\common" ".claude\rules\ecc\" -Recurse -Force
if (Test-Path "$ECC_CONFIG_DIR\rules\ecc\$Stack") {
    Copy-Item "$ECC_CONFIG_DIR\rules\ecc\$Stack" ".claude\rules\ecc\" -Recurse -Force
    Log-Ok "Rules $Stack copiadas"
} else {
    Log-Warn "Stack '$Stack' não encontrada em rules/ecc/, usando apenas common"
}

# 4. Copia AGENTS.md se existir
if (Test-Path "$ECC_CONFIG_DIR\AGENTS.md") {
    Copy-Item "$ECC_CONFIG_DIR\AGENTS.md" ".claude\AGENTS.md" -Force
    Log-Ok "AGENTS.md copiado"
}

# 5. Atualiza .gitignore
$gitignore = @"
# ECC / OpenCode
.claude/rules/ecc/
.opencode/session_state.json
"@
$gitignorePath = ".gitignore"
if (Test-Path $gitignorePath) {
    $content = Get-Content $gitignorePath -Raw
    if ($content -notmatch "ECC / OpenCode") {
        Add-Content $gitignorePath $gitignore
    }
} else {
    Set-Content $gitignorePath $gitignore
}
Log-Ok ".gitignore atualizado"

# 6. Script de ativação rápida
$activateScript = @'
#!/bin/bash
# source .claude/activate-ecc.sh
# Carrega skills essenciais para sessão rapida

echo "=== ECC Skills Disponiveis ==="
ls ~/.config/opencode/skill/ | head -20
echo "... ($(ls ~/.config/opencode/skill/ | wc -l) skills total)"

echo ""
echo "=== Agents Disponiveis ==="
ls ~/.config/opencode/agent/

echo ""
echo "=== Comandos Disponiveis ==="
ls ~/.config/opencode/command/

echo ""
echo "Para usar na conversa:"
echo "  skill(\"nome-da-skill\")"
echo "  agent(\"nome-do-agent\")"
'@
Set-Content ".claude\activate-ecc.sh" $activateScript
Log-Ok "Script de ativação criado: .claude\activate-ecc.sh"

# 7. CLAUDE.md do projeto
if (-not (Test-Path "CLAUDE.md")) {
    $projectName = Split-Path $PROJECT_DIR -Leaf
    $claudeMd = @"
# Projeto: $projectName

## Stack
- Language: $Stack
- Framework: 
- Database: 

## ECC Workflow
- Planning: \`skill("gsd-plan-phase")\` → \`agent("planner")\`
- TDD: \`skill("tdd-workflow")\` → \`agent("tdd-guide")\`
- Review: \`skill("code-review")\` → \`agent("code-reviewer")\`
- Security: \`skill("security-review")\` → \`agent("security-reviewer")\`

## Commands
- \`gsd-next\` - Próximo passo inteligente
- \`gsd-plan-phase\` - Planeja feature
- \`gsd-execute-phase\` - Executa plano
- \`gsd-verify-work\` - Valida com UAT

## Hooks (automáticos)
- pre-commit: lint + typecheck + test
- pre-push: full test suite
- commit-msg: conventional commits

## Rules (project-local)
- .claude/rules/ecc/common/
- .claude/rules/ecc/$Stack/
"@
    Set-Content "CLAUDE.md" $claudeMd
    Log-Ok "CLAUDE.md criado"
}

# 8. Resumo
$skillsCount = (Get-ChildItem "$ECC_CONFIG_DIR\skill").Count
$agentsCount = (Get-ChildItem "$ECC_CONFIG_DIR\agent").Count
$cmdsCount = (Get-ChildItem "$ECC_CONFIG_DIR\command").Count

Log-Info "Recursos ECC disponíveis globalmente:"
Write-Host "  Skills:  $skillsCount"
Write-Host "  Agents:  $agentsCount"
Write-Host "  Commands: $cmdsCount"

Log-Ok "Projeto inicializado com ECC!"
Write-Host ""
Write-Host "Próximos passos:"
Write-Host "  1. .\.claude\activate-ecc.sh        # Ver skills disponíveis (Git Bash/WSL)"
Write-Host "  2. Na conversa: skill(\"gsd-next\")  # Detecta estado do projeto"
Write-Host "  3. Edite CLAUDE.md com info do seu projeto"
Write-Host ""
Write-Host "Skills recomendadas para começar:"
Write-Host "  - skill(\"gsd-next\")           # Smart entry point"
Write-Host "  - skill(\"gsd-plan-phase\")     # Planejar feature"
Write-Host "  - skill(\"tdd-workflow\")       # TDD workflow"
Write-Host "  - skill(\"ui-ux-pro-max\")      # Design system (se UI)"
Write-Host "  - skill(\"security-review\")    # Security audit"