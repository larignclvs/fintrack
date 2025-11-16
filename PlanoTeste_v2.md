
# 🧪 FINTRACK — MASTER TEST PLAN

## 1. Introdução
Este documento apresenta o Plano Mestre de Teste (Master Test Plan) do sistema **FinTrack**, um software modular de controle financeiro. O objetivo é definir a estratégia, escopo, metodologia e critérios utilizados para assegurar a qualidade do sistema por meio de testes funcionais, estruturais, integração, desempenho e validação das regras de negócio.

## 2. Objetivos do Teste
- Verificar correção, confiabilidade e integridade das funcionalidades.
- Validar regras de negócio do domínio financeiro.
- Garantir funcionamento integrado da arquitetura modular.
- Confirmar conformidade da API com requisitos REST.
- Avaliar desempenho sob carga.
- Validar exportação de arquivos e logs.

## 3. Escopo

### 3.1 Incluído
- CRUDs de Users, Categories e Transactions
- Regras de negócio
- Validações
- API FastAPI completa
- Repositórios SQL e Mock
- Exportação CSV
- Logs rotativos
- Testes de carga e estresse

### 3.2 Excluído
- Testes de UI
- Testes de segurança avançados
- Concorrência distribuída

## 4. Itens a Serem Testados
| Camada | Item | Testes |
|-------|-------|--------|
| Models | User, Category, Transaction | Integridade e validações |
| Repository | SQLAlchemyRepository e MemoryRepository | CRUD, exceções e persistência |
| Services | TransactionService, UserService, CategoryService | Regras de negócio |
| API | FastAPI | Rotas, filtros e respostas HTTP |
| Utils | logger, export CSV | Logs e exportação |

---

# 📊 **5. Quantidade Total de Testes Executados**

Este bloco garante alinhamento com as evidências apresentadas no relatório e nos slides.

| Tipo de Teste | Quantidade |
|---------------|------------|
| **Testes Unitários** | **59** |
| **Testes de Integração** | **10** |
| **Testes Funcionais (regras de negócio)** | **23** |
| **Testes Específicos de API (erros e mensagens)** | **8** |
| **Cobertura Total** | **90%** |

---

## 6. Funcionalidades a Serem Testadas

### 6.1 Regras de Negócio
- Email único e válido para usuários  
- Transações exigem usuário e categoria existentes  
- Valor deve ser numérico e positivo  
- Tipo da transação deve combinar com o da categoria  
- Limite mensal de despesas  
- Filtros e ordenação  
- Exportação CSV  
- Erros 400/404 adequados  
- Isolamento entre usuários  

## 7. Abordagem de Teste

### 7.1 Funcionais — Caixa-Preta
<img width="567" height="384" alt="image" src="https://github.com/user-attachments/assets/7be8519f-6ead-4eec-abb2-7b8bfa31f2f7" />


### 7.2 Estruturais — Caixa-Branca
- Cobertura de branches  
- Testes com MemoryRepository  
- Testes de exceções personalizadas  
- Validação de mensagens de erro  

### 7.3 Integração
Fluxo completo de criação → consulta → validação → exportação → logs.


