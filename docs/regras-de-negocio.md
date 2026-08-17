# Regras de Negócio — Controle de Obras

## Domínio central
- O domínio central do sistema é a **obra**.
- Toda operação financeira e documental relevante deve estar vinculada a uma obra ativa.

## Empresa
- A empresa deve ser cadastrada no primeiro uso do sistema.
- Apenas uma empresa ativa é suportada na Fase 1.

## Obra
- Uma obra deve possuir código único e nome obrigatórios.
- Uma obra deve possuir valor contratado inicial obrigatório.
- Uma obra pode possuir zero ou muitos aditivos.
- Uma obra pode possuir zero ou muitos lançamentos de custos.
- O usuário deve operar sempre dentro do contexto explícito da obra ativa selecionada.

## Aditivo
- Representa acréscimo financeiro ao valor contratado inicial.
- Deve manter histórico individualizado com data, descrição e valor.

## Lançamento
- Um lançamento pertence obrigatoriamente a uma obra.
- Um lançamento deve possuir descrição livre obrigatória.
- Um lançamento pode ou não possuir quantidade e unidade.
- Um lançamento deve possuir valor total obrigatório.
- Lançamentos não dependem de cadastro prévio de produtos ou serviços.

## Anexo
- Um anexo deve estar vinculado pelo menos a uma obra.
- Um anexo pode, opcionalmente, estar vinculado também a um lançamento específico.
- O sistema armazena apenas metadados e caminho relativo interno; o arquivo físico fica em `storage/anexos/`.

## Apuração financeira
- Valor líquido = valor contratado inicial + total de aditivos - total gasto.
- O cálculo de totais é centralizado em serviços de aplicação, não duplicado nas telas.

## Backup e restauração
- O backup é completo: banco SQLite, anexos, relatórios e manifesto.
- O backup gera um arquivo `.zip` com estrutura interna padronizada.
- A restauração substitui o estado atual e cria backup de segurança automático.
- O banco é copiado usando SQLite Backup API para garantir consistência.
- Arquivos `-wal` e `-shm` são removidos antes da substituição do banco.
