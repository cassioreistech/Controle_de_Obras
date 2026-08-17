# Controle de Obras

Sistema desktop para controle financeiro e operacional de obras de engenharia civil e construção.

## Funcionalidades

- **Dashboard** — Visão geral com cards de valores (contratado, aditivos, gastos), tabela de movimentos e gráficos
- **Cadastro de Obras** — Gerenciamento completo de obras com dados do cliente, local e responsável
- **Lançamentos** — Registro de lançamentos financeiros com tipos, valores e origens
- **Aditivos** — Controle de aditivos contratuais
- **Anexos** — Upload e gerenciamento de documentos (PDF, imagens, etc.)
- **Relatórios PDF** — Geração de relatórios em PDF com os dados da obra
- **Backup/Restaurar** — Sistema de backup completo com anexos
- **Configurações** — Dados da empresa e informações do sistema

## Stack

- **Python 3.10+**
- **PySide6** — interface desktop
- **SQLite** — persistência local
- **ReportLab** — geração de PDF

## Estrutura

```
src/
  controle_obras/
    domain/         # Entidades e regras de negócio
    application/    # Casos de uso e serviços
    infrastructure/ # Repositórios, banco, filesystem, PDF
    ui/             # Telas PySide6
    shared/         # Utilitários e configurações
tests/
  domain/
  application/
  infrastructure/
  ui/
docs/             # Documentação do projeto
data/             # Banco SQLite local e backups
storage/anexos/   # Arquivos anexados por obra
reports/obras/    # Relatórios PDF gerados
```

## Instalação

```bash
pip install -e ".[dev]"
```

## Execução

```bash
python -m controle_obras
```

Ou execute o arquivo `abrir.bat` no Windows.

## Testes

```bash
pytest
```

## Qualidade

```bash
ruff check src tests
ruff format src tests
mypy src
```

## Screenshots

- Dashboard com cards de valores e tabela de movimentos
- Formulário compacto de lançamentos
- Tela de anexos com botões de ação
- Configurações da empresa

## Autor

**Cassio Vicente** — cassioreistech

## Licença

Projeto proprietário.
