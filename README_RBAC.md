# Implementação de RBAC e Área Administrativa

## Visão Geral
Este módulo adiciona controle de acesso baseado em roles (RBAC) e listas de controle de acesso (ACL) por sistema para a Central de Sistemas MG.

## Pré-requisitos
O sistema agora utiliza banco de dados SQLite e requer a biblioteca `flask-sqlalchemy`.

### Instalação
```bash
pip install -r requirements.txt
```

## Configuração Inicial (Migração)
Antes de iniciar a aplicação pela primeira vez com o novo sistema, é necessário inicializar o banco de dados e migrar os usuários existentes do `users.json`.

Execute o script de inicialização:
```bash
python init_db.py
```

Isto irá:
1. Criar o arquivo `portal_mg.db` (Banco de Dados SQLite).
2. Criar as tabelas `users`, `systems`, `user_system_access`, `audit_logs`.
3. Popular a tabela de sistemas com os padrões (Portal, Comissão, Ponto, Adiantamento).
4. Migrar todos os usuários do `users.json`.
   - **Nota**: O usuário `admin@mendoncagalvao.com.br` será promovido automaticamente a **Admin**.
   - Outros usuários serão cadastrados como **User** (Padrão).

## Funcionalidades Adicionadas

### Perfis de Usuário (Roles)
- **Admin**: Acesso total ao sistema e área administrativa.
- **Manager**: Pode gerenciar permissões de usuários, mas não pode alterar Admins.
- **User**: Acesso apenas ao dashboard e sistemas permitidos.

### Auditoria
Todas as alterações de permissão e role são registradas na tabela `audit_logs` e podem ser visualizadas no Dashboard Admin.

### Como Acessar
1. Faça login com um usuário Admin/Manager.
2. No menu superior (ao lado de "Sair"), clique no botão **Admin**.
