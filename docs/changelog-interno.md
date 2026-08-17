# Changelog Interno — Controle de Obras

## [1.0.0] — Fase 1

### Adicionado
- Estrutura inicial do projeto em camadas (domain, application, infrastructure, ui, shared).
- Domínio com entidades: Empresa, Obra, Aditivo, TipoLancamento, Lancamento, Anexo, Configuracao.
- Objetos de valor para cálculos financeiros (`ResumoFinanceiroObra`).
- Persistência em SQLite com integridade relacional habilitada.
- Repositórios para todas as entidades principais.
- Casos de uso: cadastro de empresa, obras, aditivos, lançamentos, anexos, resumo financeiro e PDF.
- Interface desktop PySide6 com telas de boas-vindas, empresa, obras, dashboard, lançamentos e anexos.
- Geração de relatório PDF por obra usando ReportLab.
- Módulo completo de backup e restauração com pacote `.zip`, manifesto e validações.
- Testes unitários e de integração com pytest.
- Documentação inicial: especificação funcional, decisões arquiteturais, fases, regras de negócio e changelog.

### Decisões
- Stack: Python 3.12, PySide6, SQLite, ReportLab.
- Lançamentos descritivos manuais sem catálogo rígido.
- Anexos armazenados em `storage/anexos/` com metadados no banco.
- Backup completo como requisito funcional crítico da Fase 1.
