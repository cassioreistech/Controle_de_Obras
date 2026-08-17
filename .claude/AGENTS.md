# Protocolo Global de Economia de Tokens (opencode)

> Este arquivo é GLOBAL: aplica-se a TODOS os projetos, novos ou antigos.

## Ao iniciar uma sessão em qualquer projeto
1. Se `.opencode/session_state.json` existir no projeto, **LEIA-O PRIMEIRO** para
   restaurar o contexto sem reler todo o histórico.
2. Se **não** existir, **CRIE-O** automaticamente com o formato padrão abaixo e
   preencha com o contexto real do projeto. Sempre marque `token_saving_mode: true`.
3. Se `.opencode/session_state.json` existir mas estiver vazio/genérico, preencha-o
   com o contexto do projeto antes de começar o trabalho.

## Formato padrão do `.opencode/session_state.json`
```json
{
  "project_name": "Nome do projeto",
  "version": "1.0",
  "token_saving_mode": true,
  "last_summary": "Resumo curto do último estado do trabalho.",
  "current_task": "O que está em andamento agora.",
  "key_decisions": ["Decisões importantes já tomadas"],
  "pending_actions": ["Próximos passos"],
  "recent_files": ["Arquivos mais relevantes"]
}
```

## Durante a sessão
- Respostas **diretas e focadas**, sem preâmbulos nem repetição.
- Prefira **editar blocos/patch** em vez de reescrever arquivos inteiros.
- **Não releia arquivos de histórico** (session_state, docs antigos, ROADMAP
  inteiro) sem comando explícito do usuário — o state file já resume o essencial.
- Ao concluir uma **etapa importante**, ATUALIZE `.opencode/session_state.json`
  (last_summary, current_task, key_decisions, pending_actions, recent_files) e
  limpe detalhes descartáveis. Não deixe acumular contexto não usado.
- Se o usuário pedir "resume/contexto/estado", leia o state file e responda a
  partir dele, sem explorar o código desnecessariamente.

## Regras de economia
- Não gere código/lixo irrelevante ao pedido.
- Não rode comandos caros (testes/lint completos) se não pedidos ou se a mudança
  for trivial e segura.
- Em dúvida sobre verbosidade: seja menor.
