from src.services.finance_service import FinanceService
from src.repositories.memory_repo import MemoryRepository


def _make_tx(amount, type_, user_id=1):
    t = type("T", (), {})()
    t.amount = amount
    t.type = type_
    t.user_id = user_id
    return t


def test_financeiro_crud_e_saldo():
    repo = MemoryRepository()
    svc = FinanceService(repo)
    tx = _make_tx(100, "Receita", 1)
    created = svc.create(tx)
    assert created.id == 1
    assert svc.get(created.id) is created
    assert created in svc.list_all()
    svc.update(created.id, {"amount": 50})
    assert svc.get(created.id).amount == 50
    svc.delete(created.id)
    assert svc.get(created.id) is None


def test_sinal_do_saldo_e_usuarios():
    repo = MemoryRepository()
    svc = FinanceService(repo)
    svc.create(_make_tx(200, "Receita", 1))
    svc.create(_make_tx(30, "Despesa", 1))
    svc.create(_make_tx(10, "Despesa", 2))
    assert svc.balance(1) == 170
    assert svc.balance(2) == -10
from src.services.finance_service import FinanceService
from unittest.mock import Mock
from types import SimpleNamespace


def _make_repo_with_storage(items=None):
    storage = list(items or [])
    repo = Mock()

    def add(obj):
        if getattr(obj, "id", None) is None:
            obj.id = (max((getattr(x, 'id', 0) for x in storage), default=0) + 1)
        storage.append(obj)
        return obj

    def get(obj_id):
        for x in storage:
            if getattr(x, 'id', None) == obj_id:
                return x
        return None

    def list_all():
        return list(storage)

    def update(obj_id, **fields):
        target = get(obj_id)
        if not target:
            return None
        for k, v in fields.items():
            setattr(target, k, v)
        return target

    def delete(obj_id):
        target = get(obj_id)
        if target:
            try:
                storage.remove(target)
            except ValueError:
                pass

    repo.add.side_effect = add
    repo.get.side_effect = get
    repo.list_all.side_effect = list_all
    repo.list.side_effect = list_all
    repo.update.side_effect = update
    repo.delete.side_effect = delete
    return repo


def test_criar_obter_listar_atualizar_deletar():
    repo = _make_repo_with_storage()
    svc = FinanceService(repo)
    t = SimpleNamespace(amount=10, user_id=1)
    created = svc.create(t)
    assert created.id is not None
    assert svc.get(created.id) is created
    assert created in svc.list_all()
    svc.update(created.id, {"amount": 20})
    assert svc.get(created.id).amount == 20
    svc.delete(created.id)
    assert svc.get(created.id) is None


def test_calculo_do_saldo():
    repo = _make_repo_with_storage()
    repo.add(SimpleNamespace(amount=100, type="Receita", user_id=1))
    repo.add(SimpleNamespace(amount=30, type="Despesa", user_id=1))
    svc = FinanceService(repo)
    assert svc.balance(1) == 70


def test_listar_retorna_lista():
    repo = _make_repo_with_storage()
    svc = FinanceService(repo)
    assert isinstance(svc.list_all(), list)
