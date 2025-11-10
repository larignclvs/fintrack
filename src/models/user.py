from sqlalchemy import Column, Integer, String
from .base import Base

class User(Base):
    """Modelo ORM que representa um usuário do sistema."""

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(100), nullable=False)
    email: str = Column(String(120), unique=True, nullable=False)

    def __repr__(self) -> str:
        """Retorna representação textual do usuário."""
        return f"<User(name={self.name}, email={self.email})>"
