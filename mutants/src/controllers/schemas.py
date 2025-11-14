from datetime import date
from pydantic import BaseModel, EmailStr, ConfigDict

from typing import Optional

# =========================
#        USERS
# =========================

class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    """Dados obrigatórios para criar usuário."""
    pass


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class UserOut(UserBase):
    id: int

    # pydantic v2: use model_config / ConfigDict to enable from_attributes (orm_mode)
    model_config = ConfigDict(from_attributes=True)

# ===== CATEGORIES =====

class CategoryBase(BaseModel):
    name: str
    type: str  # "Receita" ou "Despesa"


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    type: str | None = None


class CategoryOut(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# =========================
#     TRANSACTIONS
# =========================

class TransactionBase(BaseModel):
    amount: float
    date: date
    description: str | None = None
    type: str        # "Receita" ou "Despesa"
    user_id: int
    category_id: int

class TransactionCreate(TransactionBase):
    """Dados obrigatórios para criar uma transação."""
    pass

class TransactionOut(TransactionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    date: Optional[date] = None
    description: Optional[str] = None
    type: Optional[str] = None
    category_id: Optional[int] = None


