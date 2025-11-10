from src.services.abstract_service import Service
from src.repositories.abstract import Repository
from src.models.transaction import Transaction

class FinanceService(Service):
    def __init__(self, tx_repo: Repository[Transaction]):
        self.tx_repo = tx_repo

    def create(self, data: Transaction):
        return self.tx_repo.add(data)

    def get(self, obj_id: int):
        return self.tx_repo.get(obj_id)

    def list_all(self):
        return self.tx_repo.list()

    def update(self, obj_id: int, data: dict):
        return self.tx_repo.update(obj_id, **data)

    def delete(self, obj_id: int):
        return self.tx_repo.delete(obj_id)

    # Regras de negócio extras:
    def balance(self, user_id: int) -> float:
        total = 0.0
        for t in self.tx_repo.list():
            if t.user_id == user_id:
                total += t.amount if t.type.lower() == "receita" else -t.amount
        return total
