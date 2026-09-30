# Plano Definitivo — Controle de Obras Web

## 1. Decisão e justificativa

- **Arquitetura:** Aplicação web (navegador) — acesso de qualquer lugar, sem instalar nada no cliente.
- **Backend:** **FastAPI** reutilizando `domain/` e `application/` (as regras de negócio não mudam).
- **Frontend:** **Jinja2 + HTMX** (server-rendered, sem build/Node) — o mais simples e barato de manter para 1–3 usuários.
- **Banco:** **PostgreSQL 16** (em container no próprio servidor).
- **Arquivos:** **MinIO** (S3-compatível, auto-hospedado, grátis) ou **Cloudflare R2** (free tier 10 GB).
- **Login:** simples (tabela de usuários + Argon2 + sessão). Sem RBAC, todos com acesso total.
- **Licença por máquina:** removida (não faz sentido na web). Substituída por login.

## 2. Arquitetura alvo

```
Internet → Cloudflare (DNS + WAF grátis)
              │
              ▼
        VPS Linux (São Paulo)
        ┌─────────────────────────────┐
        │  Caddy  (HTTPS automático)  │  ← Let's Encrypt
        │      │                      │
        │      ▼                      │
        │  FastAPI (app) ── Jinja2/HTMX
        │      │            │
        │      ▼            ▼
        │  PostgreSQL    MinIO (anexos)
        │      │            │
        │  pg_dump diário → R2/B2 (backup offsite)
        └─────────────────────────────┘
```

## 3. Estrutura de código proposta (aditiva, não destrutiva)

```
src/controle_obras/
  domain/          # INALTERADO
  application/     # INALTERADO (reuso total)
  infrastructure/
    database_pg.py     # NOVO — Postgres (schema já quase portável)
    storage_s3.py      # NOVO — MinIO/R2 no lugar do disco
    repositories.py    # ajuste leve (SQLite → psycopg)
  web/                 # NOVO
    main.py            # app FastAPI
    auth.py            # login/sessão/Argon2
    routes/            # dashboard, obras, lancamentos, anexos, empresa, relatorios
    templates/         # Jinja2
    static/            # CSS/JS
  ui/                  # mantido no repo, não usado no deploy web
deploy/
  Dockerfile
  docker-compose.yml
  Caddyfile
  .env.example
  scripts/backup.sh
```

## 4. Ferramentas exatas (custo mínimo)

| Item | Escolha | Custo |
|---|---|---|
| Servidor | VPS 2 vCPU / 4 GB — **São Paulo** (DigitalOcean/Vultr/Locaweb) | ~R$ 130/mês |
| (alternativa mais barata) | Hetzner CX22 (latência maior, ~Europa) | ~R$ 25/mês |
| Banco | PostgreSQL 16 (container) | R$ 0 |
| Arquivos | MinIO (container) ou Cloudflare R2 | R$ 0 (free tier) |
| SSL | Let's Encrypt via **Caddy** | R$ 0 |
| Domínio | `.com.br` no Registro.br | ~R$ 40/ano |
| CDN/WAF | Cloudflare Free | R$ 0 |
| Monitoramento | UptimeRobot + Sentry Free | R$ 0 |
| Backup offsite | Backblaze B2 / R2 | ~R$ 15/mês |
| Deploy | GitHub Actions + Docker | R$ 0 |
| **Total** | | **≈ R$ 145–190/mês** |

> Sem restrição de orçamento, mas priorizando menor custo, esta é a opção com melhor custo-benefício e que mantém o caminho aberto para escalar (basta trocar VPS maior ou banco gerenciado depois).

## 5. Fases de execução

**Fase 0 — Infraestrutura base (2–3 dias)**
- Contratar VPS SP + domínio; apontar DNS no Cloudflare.
- Criar `Dockerfile`, `docker-compose.yml` (app + Postgres + MinIO + Caddy).
- HTTPS automático funcionando; acesso via `https://app.suaempresa.com.br`.

**Fase 1 — Backend + migração de banco (5–7 dias)**
- Adaptar `database.py`/`repositories.py` para PostgreSQL.
- API FastAPI expondo os serviços já existentes.
- Auth: usuários, senha Argon2, sessão, tela de login.

**Fase 2 — Telas web (10–12 dias)**
- Dashboard, Obras, Lançamentos, Aditivos, Empresa, Configurações.
- Reuso dos cálculos de `services.py` (nenhuma regra de negócio reescrita).

**Fase 3 — Anexos + Relatórios (3–4 dias)**
- Upload/download via MinIO (S3).
- Relatórios PDF/DOCX já existentes servidos pela API.

**Fase 4 — Migração de dados + Go-live (3–4 dias)**
- Script que lê o `app.db` atual do cliente e importa no Postgres.
- Backup diário automatizado (pg_dump + anexos → B2/R2) + teste de restauração.
- Monitoramento e alertas.

**Fase 5 — Treinamento e documentação (2 dias)**
- Manual curto de uso + credenciais de acesso.

**Total estimado:** 4–5 semanas.

## 6. Segurança essencial

- HTTPS obrigatório + HSTS; Cloudflare WAF.
- Senhas com **Argon2**; bloqueio após tentativas falhas.
- Firewall: só portas 80/443 expostas; Postgres/MinIO **sem acesso externo**.
- Backups criptografados, regra 3-2-1, testados.
- Segredos em `.env` no servidor (nunca no Git).
- Atualizações automáticas de segurança do SO.

## 7. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Servidor cai | Backups diários offsite + monitoramento + restaurar em minutos |
| Migração de dados perde algo | Script validado + backup do `.db` original antes |
| Queda de internet do cliente | App web funciona de qualquer rede/navegador |
| Custos sobem | Arquitetura enxuta; só 1 VPS para começar |

## 8. Impactos no código atual

| Atual | Novo |
|---|---|
| `ui/*.py` (PySide6) | Reescrever (web) — **única camada descartada** |
| `domain/`, `application/` | **Reutilizados quase 100%** |
| `infrastructure/database.py` | Adaptar para PostgreSQL |
| `infrastructure/storage.py` | Trocar disco → S3 |
| `license_service.py` | Substituir por auth de usuários |
| `backup.py` | Adaptar p/ Postgres + S3 |
