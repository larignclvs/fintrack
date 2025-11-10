from typing import List, Optional

from src.models.category import Category
from src.repositories.category_repo import CategoryRepository
from src.services.exceptions import EntidadeNaoEncontradaError, ValidacaoError


class CategoryService:
    def __init__(self, repo: CategoryRepository) -> None:
        self.repo = repo

    def create_category(self, name: str, type_: str) -> Category:
        if type_ not in ("Receita", "Despesa"):
            raise ValidacaoError("Tipo de categoria deve ser 'Receita' ou 'Despesa'.")
        if not name or not name.strip():
            raise ValidacaoError("Nome de categoria é obrigatório.")

        cat = Category(name=name.strip(), type=type_)
        return self.repo.add(cat)

    def list_categories(self, tipo: Optional[str] = None, order: str = "asc") -> List[Category]:
        cats = self.repo.list_all() if tipo is None else self.repo.list_by_type(tipo)
        reverse = order == "desc"
        return sorted(cats, key=lambda c: c.name.lower(), reverse=reverse)

    def get_category(self, cat_id: int) -> Category:
        cat = self.repo.get(cat_id)
        if not cat:
            raise EntidadeNaoEncontradaError("Categoria não encontrada.")
        return cat

    def update_category(self, cat_id: int, name: Optional[str], type_: Optional[str]) -> Category:
        cat = self.get_category(cat_id)

        if name is not None:
            if not name.strip():
                raise ValidacaoError("Nome de categoria não pode ser vazio.")
            cat.name = name.strip()

        if type_ is not None:
            if type_ not in ("Receita", "Despesa"):
                raise ValidacaoError("Tipo inválido.")
            cat.type = type_

        return self.repo.update(cat)

    def delete_category(self, cat_id: int) -> None:
        cat = self.get_category(cat_id)
        self.repo.delete(cat)
