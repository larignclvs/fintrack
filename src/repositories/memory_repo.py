from typing import Dict, Generic, TypeVar, List, Optional
from src.repositories.abstract import Repository

T = TypeVar("T")

class MemoryRepository(Generic[T], Repository[T]):
    """
    Implementação de repositório em memória (mock).
    Ideal para testes unitários sem necessidade de banco real.
    """

    def __init__(self) -> None:
        """Inicializa o repositório com um dicionário interno e contador de IDs."""
        self._data: Dict[int, T] = {}
        self._counter: int = 1

    def add(self, obj: T) -> T:
        """
        Adiciona um novo objeto à memória.

        Args:
            obj (T): Objeto a ser adicionado.

        Returns:
            T: Objeto com ID atribuído.
        """
        setattr(obj, "id", self._counter)
        self._data[self._counter] = obj
        self._counter += 1
        return obj

    def get(self, obj_id: int) -> Optional[T]:
        """Busca um objeto pelo ID."""
        return self._data.get(obj_id)

    def list_all(self) -> List[T]:
        """Lista todos os objetos armazenados."""
        return list(self._data.values())

    def update(self, obj_id: int, **fields) -> Optional[T]:
        """
        Atualiza campos de um objeto existente.

        Args:
            obj_id (int): ID do objeto.
            **fields: Campos a atualizar.

        Returns:
            T | None: Objeto atualizado ou None se não encontrado.
        """
        obj = self._data.get(obj_id)
        if not obj:
            return None
        for k, v in fields.items():
            setattr(obj, k, v)
        return obj

    def delete(self, obj_id: int) -> None:
        """Remove um objeto da memória pelo ID."""
        self._data.pop(obj_id, None)
