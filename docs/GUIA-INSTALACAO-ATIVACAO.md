# Guia de Instalação e Ativação — Controle de Obras

## 1) Instalação

1. Execute **`ControleDeObras-Setup-1.0.0.exe`**.
2. Aceite o `Contrato de Licença` e clique em **Avançar**.
3. Escolha criar atalho no **Desktop** (opcional, marcado por padrão).
4. Clique em **Instalar** e aguarde (a instalação leva ~1 minuto).
5. Ao final, o app abre automaticamente.

> **Onde o app fica:** `C:\Program Files\ControleDeObras\`
> **Onde os dados ficam:** `%APPDATA%\ControleDeObras\` (banco, anexos, backups, relatórios)

> **Sobre o Windows SmartScreen:** como o app não possui assinatura digital paga, o Windows pode
> mostrar "Editor desconhecido". Para continuar:
> - Clique em **Mais informações** → **Executar mesmo assim**, ou
> - Botão direito no `.exe` → **Propriedades** → **Desbloquear** → Aplicar/OK.

---

## 2) Período de Teste

Ao abrir pela primeira vez, o app inicia um **teste gratuito de 7 dias**.
Quando faltarem poucos dias, um aviso aparece na tela.

---

## 3) Ativação da Licença (3 passos)

### Passo 1 — Copiar o ID da máquina (no computador do cliente)
1. Abra o app e vá em **Configurações** (botão ⚙ no topo direito).
2. Na seção **Licença**, clique em **"Copiar ID da máquina"**.
3. Envie esse **código de 6 caracteres** (ex.: `14AD16`) para o suporte.

### Passo 2 — Gerar a chave (no seu computador / desenvolvedor)
Receba o ID do cliente e gere a chave:
```
python scripts/gerar_licenca.py 2026-12-31 14AD16
```
Saída:
```
Chave de licenca gerada:
  20261231-409E0
```
Envie essa chave ao cliente.

### Passo 3 — Registrar a chave (no computador do cliente)
1. No app, vá em **Configurações** → seção **Licença**.
2. Cole a chave no campo **"Chave de licença"** (ex.: `20261231-409E0`).
3. Clique em **Salvar**.
4. A mensagem **"Licença ativada com sucesso!"** confirma.
5. **Reinicie a aplicação** para aplicar.

---

## Como funciona a segurança

- A chave é **vinculada ao computador do cliente** (ID da máquina). Ela **não funciona em outro PC**.
- A chave embute a **data de validade**. Ao expirar, o app pede uma nova chave.
- Formato: `AAAAMMDD-XXXXX` (data de validade + assinatura).

> Somente o desenvolvedor consegue gerar chaves (secreto compilado no app).
