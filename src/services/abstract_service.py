from abc import ABC, abstractmethod
from typing import Any

class Service(ABC):
    """Interface base para serviços de regras de negócio."""

    @abstractmethod
    def create(self, data: Any) -> Any:
        """Cria uma nova entidade."""
        pass

    @abstractmethod
    def get(self, obj_id: int) -> Any:
        """Obtém uma entidade pelo ID."""
        pass

    @abstractmethod
    def list_all(self) -> list[Any]:
        """Lista todas as entidades."""
        pass

    @abstractmethod
    def update(self, obj_id: int, data: dict) -> Any:
        """Atualiza uma entidade."""
        pass

    @abstractmethod
    def delete(self, obj_id: int) -> None:
        """Remove uma entidade."""
        pass
