from typing import List, Optional

from src.models.user import User
from src.repositories.user_repo import UserRepository
from src.services.exceptions import EntidadeNaoEncontradaError, ValidacaoError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """
    Camada de lógica de negócio para usuários.
    Aqui entram as regras de validação e uso do UserRepository.
    """

    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    # CREATE
    def create_user(self, name: str, email: str) -> User:
        if not name or not name.strip():
            raise ValidacaoError("Nome é obrigatório.")

        if not email or "@" not in email:
            raise ValidacaoError("E-mail inválido.")

        # validação de duplicidade (uma das regras pedidas)
        existing_users: List[User] = self.repo.list_all()
        if any(u.email == email for u in existing_users):
            raise ValidacaoError("Já existe um usuário com este e-mail.")

        user = User(name=name.strip(), email=email.strip())
        created = self.repo.add(user)
        logger.info("Usuário criado com id=%s", created.id)
        return created

    # READ (listar todos)
    def list_users(self) -> List[User]:
        return self.repo.list_all()

    # READ (buscar 1)
    def get_user(self, user_id: int) -> User:
        user: Optional[User] = self.repo.get(user_id)
        if not user:
            raise EntidadeNaoEncontradaError("Usuário não encontrado.")
        return user

    # UPDATE
    def update_user(self, user_id: int, name: Optional[str] = None,
                    email: Optional[str] = None) -> User:
        user = self.get_user(user_id)

        if name is not None:
            if not name.strip():
                raise ValidacaoError("Nome não pode ser vazio.")
            user.name = name.strip()

        if email is not None:
            if "@" not in email:
                raise ValidacaoError("E-mail inválido.")
            # checa duplicidade se e-mail mudou
            existing_users: List[User] = self.repo.list_all()
            if any(u.email == email and u.id != user_id for u in existing_users):
                raise ValidacaoError("Já existe um usuário com este e-mail.")
            user.email = email.strip()

        updated = self.repo.update(user)
        logger.info("Usuário atualizado id=%s", updated.id)
        return updated

    # DELETE
    def delete_user(self, user_id: int) -> None:
        user = self.get_user(user_id)
        self.repo.delete(user)
        logger.info("Usuário removido id=%s", user_id)
