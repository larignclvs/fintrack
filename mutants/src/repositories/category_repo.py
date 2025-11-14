from typing import List, Optional
import types

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.models.category import Category
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CategoryRepository:
    """Repositório concreto para categorias."""

    def __init__(self, db: Session) -> None:
        # Mutmut instrumentation may yield a generator-like object instead
        # of a Session; defensively extract the session if possible.
        from src.repositories._db_utils import DBProxy

        self.db = DBProxy(db)

    def add(self, cat: Category) -> Category:
        self.db.add(cat)
        try:
            self.db.commit()
            self.db.refresh(cat)
            logger.info("Categoria criada id=%s", cat.id)
            return cat
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("Erro ao salvar categoria: %s", e)
            raise

    def get(self, cat_id: int) -> Optional[Category]:
        return (
            self.db.query(Category)
            .filter(Category.id == cat_id)
            .first()
        )

    def list_all(self) -> List[Category]:
        return self.db.query(Category).all()

    def update(self, cat: Category) -> Category:
        try:
            self.db.commit()
            self.db.refresh(cat)
            logger.info("Categoria atualizada id=%s", cat.id)
            return cat
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("Erro ao atualizar categoria: %s", e)
            raise

    def delete(self, cat: Category) -> None:
        self.db.delete(cat)
        try:
            self.db.commit()
            logger.info("Categoria removida id=%s", cat.id)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("Erro ao deletar categoria: %s", e)
            raise

    def list_by_type(self, tipo: str) -> List[Category]:
        return (
            self.db.query(Category)
            .filter(Category.type == tipo)
            .all()
        )
