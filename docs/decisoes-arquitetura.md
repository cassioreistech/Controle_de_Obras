# Decisões Arquiteturais — Controle de Obras

## Contexto
Sistema desktop para controle financeiro e documental de obras de engenharia civil.

## Decisões

### D1. Stack tecnológica
- **Python** como linguagem principal
- **PySide6** para interface desktop
- **SQLite** para persistência local na Fase 1
- **ReportLab** para geração de PDF
- **pytest** para testes

### D2. Arquitetura em camadas
Organização do código em:
- `src/domain/` — entidades e regras de negócio
- `src/application/` — casos de uso e serviços
- `src/infrastructure/` — repositórios, banco, filesystem, PDF
- `src/ui/` — telas PySide6
- `src/shared/` — utilitários e configurações

### D3. Padrão Model/View do Qt
Listagens e tabelas usarão modelos Qt (`QAbstractTableModel`) separados da lógica de dados.

### D4. Persistência de anexos
Arquivos ficam em `storage/anexos/` organizados por obra; o banco armazena apenas metadados e caminho relativo interno, nunca caminho absoluto do sistema operacional.

### D4.1. Relatórios PDF
Relatórios gerados ficam em `reports/obras/`.

### D4.2. Backup completo
Backup gera pacote único `.zip` contendo `database/app.db`, `storage/anexos/`, `reports/obras/` e `manifest.json`. Banco é copiado via SQLite Backup API para garantir consistência. Restauração recria a estrutura interna exata e faz backup de segurança automático do estado atual.

### D5. Obra ativa
O usuário sempre opera dentro do contexto explícito de uma obra selecionada. O contexto da obra ativa ficará visível na interface.

### D6. Lançamentos descritivos
Lançamentos de custos são manuais e descritivos, sem dependência de catálogo fixo de produtos ou serviços.

### D7. Integridade relacional
SQLite será usado com `PRAGMA foreign_keys = ON` para garantir integridade entre obra, aditivo, lançamento e anexo.

### D8. Cálculo centralizado
Totais financeiros (valor contratado, aditivos, gastos, líquido) serão centralizados em serviços de aplicação, não duplicados nas telas.

## Consequências
- Sistema nasce modular e preparado para crescimento.
- Fase 1 deliberadamente simples, sem estoque, rede ou integrações.
- Anexos ficam fáceis de fazer backup independente do banco.
