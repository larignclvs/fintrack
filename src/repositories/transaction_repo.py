from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.models.transaction import Transaction
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TransactionRepository:
    """
    Repositório concreto para transações financeiras.
    Implementa o CRUD usando SQLAlchemy diretamente.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # CREATE
    def add(self, tx: Transaction) -> Transaction:
        self.db.add(tx)
        try:
            self.db.commit()
            self.db.refresh(tx)
            logger.info("Transação criada id=%s", tx.id)
            return tx
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("Erro ao salvar transação: %s", e)
            raise

    # READ (único)
    def get(self, tx_id: int) -> Optional[Transaction]:
        return (
            self.db.query(Transaction)
            .filter(Transaction.id == tx_id)
            .first()
        )

    # READ (lista)
    def list_all(self) -> List[Transaction]:
        return self.db.query(Transaction).all()

    # UPDATE
    def update(self, tx: Transaction) -> Transaction:
        try:
            self.db.commit()
            self.db.refresh(tx)
            logger.info("Transação atualizada id=%s", tx.id)
            return tx
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("Erro ao atualizar transação: %s", e)
            raise

    # DELETE
    def delete(self, tx: Transaction) -> None:
        self.db.delete(tx)
        try:
            self.db.commit()
            logger.info("Transação removida id=%s", tx.id)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("Erro ao deletar transação: %s", e)
            raise

    # CONSULTA ESPECÍFICA (vai servir pra tua parte depois)
    def list_by_user(self, user_id: int) -> List[Transaction]:
        return (
            self.db.query(Transaction)
            .filter(Transaction.user_id == user_id)
            .all()
        )
