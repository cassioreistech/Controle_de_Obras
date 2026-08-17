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
