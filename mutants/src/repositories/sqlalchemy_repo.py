from typing import Type, TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from .abstract import Repository
from src.utils.logger import get_logger

T = TypeVar("T")
log = get_logger("SQLAlchemyRepository")

class SQLAlchemyRepository(Generic[T], Repository[T]):
    """Repositório genérico que implementa operações CRUD com SQLAlchemy."""

    def __init__(self, model: Type[T], session: Session) -> None:
        """
        Inicializa o repositório com um modelo e uma sessão SQLAlchemy.

        :param model: Classe do modelo (ORM)
        :param session: Instância de sessão SQLAlchemy
        """
        self.model = model
        self.session = session

    def add(self, obj: T) -> T:
        """Adiciona um novo objeto no banco de dados."""
        try:
            self.session.add(obj)
            self.session.commit()
            self.session.refresh(obj)
            log.info(f"{self.model.__name__} adicionado: {obj}")
            return obj
        except IntegrityError as e:
            self.session.rollback()
            log.error(f"Erro de integridade ao adicionar {self.model.__name__}: {e.orig}")
            raise ValueError(f"Erro de integridade: {e.orig}")
        except OperationalError as e:
            self.session.rollback()
            log.error(f"Erro operacional no BD: {e.orig}")
            raise ConnectionError(f"Erro de conexão: {e.orig}")
