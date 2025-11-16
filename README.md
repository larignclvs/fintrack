# 💰 FinTrack — Sistema Modular de Controle Financeiro Pessoal

Projeto acadêmico desenvolvido com Python + FastAPI + SQLAlchemy, seguindo arquitetura modular, injeção de dependências e Repository Pattern.


## 🧩 Estrutura Geral do Projeto  

src/  
 ├── models/              # Entidades ORM (User, Category, Transaction)  
 ├── repositories/        # Camada de persistência e mock  
 ├── services/            # Lógica de negócio (injeção de dependência)  
 ├── controllers/         # API (FastAPI)  
 ├── utils/               # Logger e utilitários  
config/  
 ├── settings.py          # Leitura do .env e configuração global  
tests/                    # Testes unitários e de integração  
.logs/                    # Logs rotativos da aplicação  
fintrack.db               # Banco de dados SQLite local   

## 📦 Execução Completa
### 1️⃣ Ativar o ambiente:   
venv\Scripts\activate  

### 2️⃣ Iniciar banco:  
python -c "from src.repositories.db import init_db; init_db()"  

### 3️⃣ Rodar API:  
uvicorn src.controllers.api:app --reload  

### 4️⃣ Testar endpoints em:
/health  
/transactions  
/docs (Swagger UI)  


## 🧮 Banco de Dados e Modelos

O sistema utiliza três entidades relacionadas:

User: representa o usuário do sistema.  
Category: classifica as transações como Receita ou Despesa.  
Transaction: representa as movimentações financeiras e se relaciona com User e Category.  


## 🧱 Arquitetura e Padrões Aplicados

✅ Arquitetura modular com separação de camadas:  
Apresentação (controllers) → FastAPI  
Lógica de negócio (services) → classes e dependências  
Persistência (repositories) → Repository Pattern  

✅ Injeção de dependências:  
Sessões do banco são injetadas nas rotas via Depends(get_db)  
Serviços recebem os repositórios no construtor  

✅ Repository Pattern:
SQLAlchemyRepository: CRUD genérico  
UserRepository, CategoryRepository, TransactionRepository: específicos
MemoryRepository: mock para testes unitários  


## Instruções do projeto  
## 🧩 Configuração do Ambiente  
### 1️⃣ Criação do ambiente virtual:  
python -m venv venv  
venv\Scripts\activate  

### 2️⃣ Instalação das dependências:
pip install -r requirements.txt   

## 🧪 Testes Realizados
✅ Teste 1 — Inicialização do Banco  
python -c "from src.repositories.db import init_db; init_db()"  

Resultado esperado: ✅ Banco de dados inicializado com sucesso!

✅ Teste 2 — Criação de Usuário (CRUD real)  
python -c "from src.repositories.db import SessionLocal, init_db; from src.repositories.user_repo import UserRepository; from src.models.user import User; init_db(); s=SessionLocal(); repo=UserRepository(User,s); u=repo.add(User(name='Gabrielle',email='gabi@teste.com')); print('Usuário criado:',u.id,u.name); print('Todos:',repo.list_all())"  

Resultado esperado:   
Usuário criado: 1 Gabrielle
Todos: [<User(name=Gabrielle, email=gabi@teste.com)>]  

✅ Teste 3 — Tratamento de Exceção de Integridade  
python -c "from src.repositories.db import SessionLocal, init_db; from src.repositories.user_repo import UserRepository; from src.models.user import User; init_db(); s=SessionLocal(); repo=UserRepository(User,s); repo.add(User(name='Gabrielle',email='gabi@teste.com'))"  
Resultado esperado:  
ValueError: Erro de integridade ao inserir User: UNIQUE constraint failed: users.email

✅ Teste 4 — Mock do Banco (MemoryRepository)  
python -c "from src.repositories.memory_repo import MemoryRepository; from src.models.user import User; repo=MemoryRepository[User](); u=repo.add(User(name='Teste',email='mock@fake.com')); print('Usuário mock:',u.id,u.name); repo.update(u.id,name='Editado'); print('Depois do update:',repo.get(u.id).name); repo.delete(u.id); print('Após delete:',repo.list_all())"  
Resultado esperado:  
Usuário mock: 1 Teste  
Depois do update: Editado  
Após delete: []  

**📋 Mock funciona perfeitamente sem depender do banco físico.**  

✅ Teste 5 — API (FastAPI + Injeção de Dependência)  
uvicorn src.controllers.api:app --reload  
Verificar:  

http://127.0.0.1:8000/health  
 → {"status": "ok"}  

http://127.0.0.1:8000/transactions  
` → lista de transações  

http://127.0.0.1:8000/docs  
` → Swagger UI  

**📋 Confirma integração completa entre FastAPI, Repository e camada de persistência.**  

✅ Teste 6 — Logging  
python -c "from src.utils.logger import get_logger; log=get_logger('test'); log.debug('debug ativo'); log.info('sistema iniciado'); log.warning('aviso de teste'); log.error('erro simulado'); print('✅ Logs gerados em .logs/app.log')"  
 
Conteúdo esperado em .logs/app.log:  
2025-11-04 23:02:11 | INFO | fintrack.test | sistema iniciado  
2025-11-04 23:02:11 | WARNING | fintrack.test | aviso de teste   
2025-11-04 23:02:11 | ERROR | fintrack.test | erro simulado  

#### 1️⃣ CRUDs completos para 3 entidades

- **User**
  - Criação, leitura, atualização e exclusão de usuários.
  - Validação de e-mails com `EmailStr`.
  - Impede duplicidade de e-mails no banco.

- **Category**
  - Gerencia categorias de transações (tipo `Receita` ou `Despesa`).
  - Permite filtros e ordenação por tipo.
  - Garante consistência no tipo da categoria.

- **Transaction**
  - Representa movimentações financeiras (com data, valor e tipo).
  - Se relaciona diretamente com `User` e `Category`.
  - Implementa múltiplas regras de validação de integridade.

---

### 🧩 Regras de Negócio e Validações

#### ✅ Validação com múltiplas condições
- Impede valores negativos ou nulos nas transações.
- Impede criação de transações quando o usuário ou categoria não existirem.
- Garante que o **tipo da transação** corresponda ao **tipo da categoria**.

#### ✅ Cálculo e Limite Mensal
- Soma automática das despesas do usuário no mês atual.
- Bloqueia novas transações de despesa que ultrapassem o limite definido no `.env`: 2000.0


#### ✅ Interação entre Entidades
- Cada `Transaction` valida dinamicamente se o `User` e a `Category` existem.
- O sistema cruza o tipo (`Receita` ou `Despesa`) antes de permitir a operação.

---

### 🚨 Tratamento de Exceções Personalizadas

O projeto define exceções específicas dentro de `src/services/exceptions.py`:

- `EntidadeNaoEncontradaError` — quando um recurso não é encontrado.
- `ValidacaoError` — para erros de entrada ou violações de regras de negócio.

Essas exceções são capturadas na camada `controllers` e convertidas em respostas HTTP:
- 400 → erro de validação
- 404 → entidade inexistente
- 500 → erro interno de servidor

---

### 🔍 Consultas e Filtros

A API permite buscas personalizadas com filtros e ordenação:

**Exemplo:**  
`GET /transactions?user_id=1&tipo=Despesa&order_by=amount&order=desc`

Permite:
- Filtrar transações por `user_id` e `tipo`.
- Ordenar por `date` (padrão) ou `amount`.
- Definir direção de ordenação (`asc` ou `desc`).

---

### 🧱 Interface REST Completa

Todos os endpoints CRUD e utilitários foram implementados:

| Entidade | Método | Rota | Descrição |
|-----------|---------|------|------------|
| **User** | `POST` | `/users` | Cria um novo usuário |
| | `GET` | `/users` | Lista todos os usuários |
| | `GET` | `/users/{id}` | Busca usuário por ID |
| | `PUT` | `/users/{id}` | Atualiza nome/e-mail |
| | `DELETE` | `/users/{id}` | Exclui usuário |
| **Category** | `POST` | `/categories` | Cria categoria (Receita/Despesa) |
| | `GET` | `/categories` | Lista categorias (filtro + ordenação) |
| | `PUT` | `/categories/{id}` | Atualiza nome/tipo |
| | `DELETE` | `/categories/{id}` | Remove categoria |
| **Transaction** | `POST` | `/transactions` | Cria transação com validação de limite |
| | `GET` | `/transactions` | Lista todas (filtro por usuário, tipo, ordenação) |
| | `PUT` | `/transactions/{id}` | Atualiza dados da transação |
| | `DELETE` | `/transactions/{id}` | Exclui transação |
| | `GET` | `/transactions/export` | Exporta transações para CSV |

---

### 📂 Manipulação de Arquivos (Exportação CSV)

O módulo `src/utils/file_export.py` adiciona a função:

```python
def export_transactions_to_csv(transactions: Iterable[Transaction], filepath: str) -> str

Essa função:

Exporta as transações filtradas para um arquivo .csv;

Cria automaticamente o diretório de exportação

Adiciona logs detalhados da operação.

## 🧩 Estrutura de Logs

O logger rotativo (src/utils/logger.py) grava todos os eventos no arquivo .logs/app.log.

Exemplo de logs:

2025-11-10 18:23:15 | INFO | fintrack.API | API inicializada e banco configurado.
2025-11-10 18:23:20 | INFO | fintrack.TransactionService | 12 transações retornadas.
2025-11-10 18:25:01 | ERROR | fintrack.TransactionService | Limite mensal excedido para o usuário 1.



