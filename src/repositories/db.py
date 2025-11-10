import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.models.base import Base
from config.settings import get_setting

from src.models.user import User
from src.models.category import Category
from src.models.transaction import Transaction

def get_engine() -> "Engine":
    """
    Cria e retorna a engine de conexão com o banco de dados.

    Returns:
        sqlalchemy.engine.Engine: Objeto Engine configurado.
    """
    database_url: str = get_setting("DATABASE_URL", "sqlite:///./fintrack.db")
    return create_engine(database_url, echo=False, future=True)

engine = get_engine()
SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine, autoflush=False, autocommit=False
)

def init_db() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas definidas nos modelos ORM.
    Caso as tabelas já existam, nenhuma alteração é feita.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Banco de dados inicializado com sucesso!")
