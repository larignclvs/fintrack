from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Transaction(Base):
    """Modelo ORM que representa uma transação financeira."""

    __tablename__ = "transactions"

    id: int = Column(Integer, primary_key=True, index=True)
    amount: float = Column(Float, nullable=False)
    date: str = Column(Date, nullable=False)
    description: str = Column(String(255))
    type: str = Column(String(10), nullable=False)  # "Receita" | "Despesa"
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id: int = Column(Integer, ForeignKey("categories.id"), nullable=False)

    user = relationship("User")
    category = relationship("Category")

    def __repr__(self) -> str:
        """Retorna representação textual da transação."""
        return f"<Transaction(amount={self.amount}, type={self.type})>"
