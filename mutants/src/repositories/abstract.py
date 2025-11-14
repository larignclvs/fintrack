from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional

T = TypeVar("T")

class Repository(ABC, Generic[T]):
    """Interface genérica de repositório (CRUD básico)."""

    @abstractmethod
    def add(self, obj: T) -> T:
        pass

    @abstractmethod
    def get(self, obj_id: int) -> Optional[T]:
        pass

    @abstractmethod
    def list_all(self) -> List[T]:
        pass

    @abstractmethod
    def update(self, obj_id: int, **fields) -> Optional[T]:
        pass

    @abstractmethod
    def delete(self, obj_id: int) -> None:
        pass
