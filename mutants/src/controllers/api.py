from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from src.repositories.db import SessionLocal, init_db
from src.repositories.user_repo import UserRepository
from src.repositories.category_repo import CategoryRepository
from src.repositories.transaction_repo import TransactionRepository
from src.services.user_service import UserService
from src.services.category_service import CategoryService
from src.services.transaction_service import TransactionService
from src.services.exceptions import EntidadeNaoEncontradaError, ValidacaoError
from src.controllers.schemas import (
    UserCreate, UserUpdate, UserOut,
    CategoryCreate, CategoryUpdate, CategoryOut,
    TransactionCreate, TransactionUpdate, TransactionOut,
)
from src.utils.logger import get_logger
from src.utils.file_export import export_transactions_to_csv

@asynccontextmanager
async def _lifespan(app: FastAPI):
    # inicializa o DB na inicialização da aplicação
    init_db()
    log.info("API inicializada e banco configurado.")
    yield


app = FastAPI(title="FinTrack API", lifespan=_lifespan)
log = get_logger("API")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(CategoryRepository(db))


def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    tx_repo = TransactionRepository(db)
    user_repo = UserRepository(db)
    cat_repo = CategoryRepository(db)
    return TransactionService(tx_repo, user_repo, cat_repo)


# startup handled by lifespan manager above


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# ===== USERS =====

@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user_in: UserCreate, service: UserService = Depends(get_user_service)):
    try:
        return service.create_user(user_in.name, user_in.email)
    except ValidacaoError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users", response_model=list[UserOut])
def list_users(service: UserService = Depends(get_user_service)):
    return service.list_users()


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    try:
        return service.get_user(user_id)
    except EntidadeNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_in: UserUpdate, service: UserService = Depends(get_user_service)):
    try:
        return service.update_user(user_id, user_in.name, user_in.email)
    except (EntidadeNaoEncontradaError, ValidacaoError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    try:
        service.delete_user(user_id)
    except EntidadeNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===== CATEGORIES =====

@app.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(cat_in: CategoryCreate, service: CategoryService = Depends(get_category_service)):
    try:
        return service.create_category(cat_in.name, cat_in.type)
    except ValidacaoError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/categories", response_model=list[CategoryOut])
def list_categories(
    tipo: str | None = None,
    order: str = "asc",
    service: CategoryService = Depends(get_category_service),
):
    return service.list_categories(tipo, order)


@app.get("/categories/{cat_id}", response_model=CategoryOut)
def get_category(cat_id: int, service: CategoryService = Depends(get_category_service)):
    try:
        return service.get_category(cat_id)
    except EntidadeNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/categories/{cat_id}", response_model=CategoryOut)
def update_category(
    cat_id: int,
    cat_in: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
):
    try:
        return service.update_category(cat_id, cat_in.name, cat_in.type)
    except (EntidadeNaoEncontradaError, ValidacaoError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/categories/{cat_id}", status_code=204)
def delete_category(cat_id: int, service: CategoryService = Depends(get_category_service)):
    try:
        service.delete_category(cat_id)
    except EntidadeNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===== TRANSACTIONS =====

@app.post("/transactions", response_model=TransactionOut, status_code=201)
def create_transaction(
    tx_in: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        return service.create_transaction(
            amount=tx_in.amount,
            date=tx_in.date,
            description=tx_in.description,
            type_=tx_in.type,
            user_id=tx_in.user_id,
            category_id=tx_in.category_id,
        )
    except (ValidacaoError, EntidadeNaoEncontradaError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/transactions", response_model=list[TransactionOut])
def list_transactions(
    user_id: int | None = None,
    tipo: str | None = None,
    order_by: str = "date",
    order: str = "asc",
    service: TransactionService = Depends(get_transaction_service),
):
    return service.list_transactions(user_id, tipo, order_by, order)


@app.get("/transactions/summary")
def transaction_summary(user_id: int, service: TransactionService = Depends(get_transaction_service)):
    """Retorna o total de receitas e despesas do usuário."""
    txs = service.list_transactions(user_id=user_id)
    receitas = sum(t.amount for t in txs if t.type.lower() == "receita")
    despesas = sum(t.amount for t in txs if t.type.lower() == "despesa")
    saldo = receitas - despesas
    return {
        "user_id": user_id,
        "receitas": receitas,
        "despesas": despesas,
        "saldo": saldo
    }


@app.get("/transactions/export")
def export_transactions(user_id: int, service: TransactionService = Depends(get_transaction_service)):
    """
    Exporta todas as transações de um usuário específico para CSV.
    """
    txs = service.list_transactions(user_id=user_id)
    if not txs:
        raise HTTPException(status_code=404, detail="Nenhuma transação encontrada para este usuário.")

    path = export_transactions_to_csv(txs, user_id)
    return {"mensagem": "Exportação concluída com sucesso.", "arquivo": path}


@app.get("/transactions/{tx_id}", response_model=TransactionOut)
def get_transaction(tx_id: int, service: TransactionService = Depends(get_transaction_service)):
    try:
        return service.get_transaction(tx_id)
    except EntidadeNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/transactions/{tx_id}", response_model=TransactionOut)
def update_transaction(
    tx_id: int,
    tx_in: TransactionUpdate,
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        return service.update_transaction(
            tx_id,
            amount=tx_in.amount,
            date=tx_in.date,
            description=tx_in.description,
            type_=tx_in.type,
            category_id=tx_in.category_id,
        )
    except (ValidacaoError, EntidadeNaoEncontradaError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/transactions/{tx_id}", status_code=204)
def delete_transaction(tx_id: int, service: TransactionService = Depends(get_transaction_service)):
    try:
        service.delete_transaction(tx_id)
    except EntidadeNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
