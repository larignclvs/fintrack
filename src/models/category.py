from sqlalchemy import Column, Integer, String
from .base import Base

class Category(Base):
    """Modelo ORM que representa uma categoria de transação."""

    __tablename__ = "categories"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(80), nullable=False)
    type: str = Column(String(10), nullable=False)  # "Receita" | "Despesa"

    def __repr__(self) -> str:
        """Retorna representação textual da categoria."""
        return f"<Category(name={self.name}, type={self.type})>"
