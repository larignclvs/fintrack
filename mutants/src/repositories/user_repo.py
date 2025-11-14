from typing import List, Optional
import types
from src.repositories._db_utils import DBProxy

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.models.user import User
from src.utils.logger import get_logger

logger = get_logger(__name__)


class UserRepository:
    """Repositório concreto para usuários."""

    def __init__(self, db: Session) -> None:
        # Mutmut instrumentation can sometimes wrap/decorate callables and
        # produce a generator-like object instead of the SQLAlchemy Session
        # instance. Be defensive: if db is a generator, extract the actual
        # session via next().
        # Wrap the db in a proxy that resolves generator-like objects on demand.
        self.db = DBProxy(db)

    def add(self, user: User) -> User:
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
            logger.info("Usuário criado id=%s", user.id)
            return user
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("Erro ao salvar usuário: %s", e)
            raise

    def get(self, user_id: int) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def list_all(self) -> List[User]:
        return self.db.query(User).all()

    def update(self, user: User) -> User:
        try:
            self.db.commit()
            self.db.refresh(user)
            logger.info("Usuário atualizado id=%s", user.id)
            return user
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("Erro ao atualizar usuário: %s", e)
            raise

    def delete(self, user: User) -> None:
        self.db.delete(user)
        try:
            self.db.commit()
            logger.info("Usuário removido id=%s", user.id)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("Erro ao deletar usuário: %s", e)
            raise

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )
