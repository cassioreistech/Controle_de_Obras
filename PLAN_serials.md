# Plano: Sistema de Controle de Seriais

## Contexto
O sistema atual gera chaves de licença vinculadas a máquinas, mas não há controle de quais seriais foram gerados, para quem foram enviados ou suas validades. Isso gera falta de rastreabilidade e controle.

## Objetivo
Criar um sistema de gerenciamento de seriais que permita registrar, controlar e rastrear todas as licenças geradas.

## Funcionalidades

### 1. Modelo de Dados
Nova tabela `seriais` no banco de dados:
```sql
CREATE TABLE IF NOT EXISTS seriais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chave TEXT NOT NULL UNIQUE,
    cliente_nome TEXT,
    cliente_empresa TEXT,
    cliente_contato TEXT,
    maquina_id TEXT NOT NULL,
    data_geracao DATE NOT NULL,
    data_validade DATE NOT NULL,
    status TEXT DEFAULT 'Ativo',
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Serviço de Gerenciamento
Novo arquivo `serial_service.py`:
- `registrar_serial(chave, cliente, maquina_id, validade)` - Registra um serial gerado
- `listar_seriais(filtros)` - Lista seriais com filtros
- `buscar_serial(chave)` - Busca serial por chave
- `atualizar_status(serial_id, status)` - Atualiza status (Ativo/Inativo/Expirado)
- `obter_estatisticas()` - Retorna estatísticas (total, ativos, expirados)

### 3. Interface de Gerenciamento
Nova tela `serials_screen.py`:
- Tabela com lista de seriais
- Filtros por status, cliente, data
- Botão "Novo Serial" (abre formulário)
- Botão "Editar" / "Excluir"
- Painel de estatísticas no topo

### 4. Formulário de Cadastro
Modal `serial_form_dialog.py`:
- Campos: Chave, Nome do Cliente, Empresa, Contato, Data de Validade
- Validação da chave antes de salvar
- Opção de gerar chave automaticamente

### 5. Integração com Sistema Atual
- Modificar `gerar_licenca.py` para salvar no novo repositório
- Adicionar menu "Seriais" na barra lateral
- Adicionar estatísticas no dashboard

## Fluxo de Uso

### Gerar novo serial:
1. Usuário clica em "Novo Serial"
2. Preenche dados do cliente
3. Sistema gera chave automaticamente
4. Serial é registrado no banco
5. Chave é exibida para copiar e enviar

### Consultar seriais:
1. Usuário acessa tela "Seriais"
2. Visualiza tabela com todos os seriais
3. Pode filtrar por status, cliente, data
4. Pode editar ou excluir seriais

## Arquivos a Criar/Modificar

### Novos:
1. `src/controle_obras/domain/models.py` - Adicionar modelo Serial
2. `src/controle_obras/infrastructure/serial_repository.py` - Repositório de seriais
3. `src/controle_obras/application/serial_service.py` - Serviço de gerenciamento
4. `src/controle_obras/ui/serials_screen.py` - Tela de listagem
5. `src/controle_obras/ui/serial_form_dialog.py` - Formulário de cadastro

### Modificar:
1. `src/controle_obras/infrastructure/database.py` - Adicionar tabela seriais
2. `src/controle_obras/ui/app_container.py` - Adicionar menu e navegação
3. `scripts/gerar_licenca.py` - Integrar com repositório

## Verificação

### Critérios de Aceite:
- [ ] Tabela `seriais` criada no banco
- [ ] Serviço permite CRUD completo
- [ ] Tela lista seriais com filtros
- [ ] Formulário valida e salva corretamente
- [ ] Integração com script de geração funciona
- [ ] Estatísticas são exibidas corretamente

### Testes:
- Unitários para repositório e serviço
- Integração para fluxo completo
- UI para interface (opcional)

## Estimativa
- **Tempo**: 2-3 horas
- **Complexidade**: Média
- **Dependências**: Nenhuma nova

## Prioridade
**Alta** - Controle essencial para gestão de licenças