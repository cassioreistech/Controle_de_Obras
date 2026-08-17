# Controle de Obras

Sistema desktop para controle financeiro e operacional de obras de engenharia civil e construção.

## Stack

- **Python 3.10+**
- **PySide6** — interface desktop
- **SQLite** — persistência local
- **ReportLab** — geração de PDF

## Estrutura

```
src/
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
