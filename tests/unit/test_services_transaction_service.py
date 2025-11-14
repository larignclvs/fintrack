from datetime import date
from unittest.mock import Mock
from types import SimpleNamespace

import pytest

from src.services.transaction_service import TransactionService
from src.services.exceptions import ValidacaoError, EntidadeNaoEncontradaError


def make_repo_with_get(return_value=None):
    m = Mock()
    m.get.return_value = return_value
    m.list_all.return_value = []
    m.list_by_user.return_value = []
    m.add.return_value = return_value
    return m


def test_criar_valor_invalido_levanta_erro_com_mock():
    tx_repo = make_repo_with_get()
    user_repo = make_repo_with_get()
    cat_repo = make_repo_with_get()
    svc = TransactionService(tx_repo, user_repo, cat_repo)
    with pytest.raises(ValidacaoError):
        svc.create_transaction(-1, date.today(), "x", "Receita", 1, 1)


def test_criar_tipo_invalido_levanta_erro_com_mock():
    tx_repo = make_repo_with_get()
    user_repo = make_repo_with_get()
    cat_repo = make_repo_with_get()
    svc = TransactionService(tx_repo, user_repo, cat_repo)
    with pytest.raises(ValidacaoError):
        svc.create_transaction(10, date.today(), "x", "Invalid", 1, 1)


def test_validar_usuario_falta_levanta_erro_com_mock():
    tx_repo = make_repo_with_get()
    user_repo = make_repo_with_get(return_value=None)
    cat_repo = make_repo_with_get()
    svc = TransactionService(tx_repo, user_repo, cat_repo)
    with pytest.raises(EntidadeNaoEncontradaError):
        svc._validar_user_category(1, 1, "Receita")


def test_validar_categoria_falta_levanta_erro_com_mock():
    tx_repo = make_repo_with_get()
    user_repo = make_repo_with_get(return_value=Mock(id=1))
    cat_repo = make_repo_with_get(return_value=None)
    svc = TransactionService(tx_repo, user_repo, cat_repo)
    with pytest.raises(EntidadeNaoEncontradaError):
        svc._validar_user_category(1, 2, "Receita")


def test_validar_tipo_incompativel_levanta_erro_com_mock():
    tx_repo = make_repo_with_get()
    user_repo = make_repo_with_get(return_value=Mock(id=1))
    cat_repo = make_repo_with_get(return_value=Mock(id=2, type="Despesa"))
    svc = TransactionService(tx_repo, user_repo, cat_repo)
    with pytest.raises(ValidacaoError):
        svc._validar_user_category(1, 2, "Receita")


def test_limite_mensal_aplicado_com_mock(monkeypatch):
    monkeypatch.setenv("MONTHLY_LIMIT", "50.0")
    tx_repo = Mock()
    existing = Mock(amount=40, date=date(2025, 1, 2), type="Despesa", user_id=1)
    tx_repo.list_by_user.return_value = [existing]
    user_repo = make_repo_with_get(return_value=Mock(id=1))
    cat_repo = make_repo_with_get(return_value=Mock(id=2, type="Despesa"))
    svc = TransactionService(tx_repo, user_repo, cat_repo)
    with pytest.raises(ValidacaoError):
        svc.create_transaction(20, date(2025, 1, 3), "x", "Despesa", 1, 2)

def make_user(uid=1):
    return SimpleNamespace(id=uid)


def make_category(type_="Receita", cid=1):
    return SimpleNamespace(id=cid, type=type_)


def _make_repo_with_storage(items=None):
    storage = list(items or [])
    repo = Mock()

    def add(obj):
        if getattr(obj, "id", None) is None:
            max_id = max((getattr(x, "id", 0) for x in storage), default=0)
            obj.id = max_id + 1
        storage.append(obj)
        return obj

    def get(obj_id):
        for x in storage:
            if getattr(x, "id", None) == obj_id:
                return x
        return None

    def list_all():
        return list(storage)

    def list_by_user(user_id):
        return [i for i in storage if getattr(i, "user_id", None) == user_id]

    def delete(obj):
        for i, x in enumerate(storage):
            if getattr(x, "id", None) == getattr(obj, "id", None):
                del storage[i]
                return None

    def update(obj):
        for i, x in enumerate(storage):
            if getattr(x, "id", None) == getattr(obj, "id", None):
                storage[i] = obj
                return obj
        storage.append(obj)
        return obj

    repo.add.side_effect = add
    repo.get.side_effect = get
    repo.list_all.side_effect = list_all
    repo.list_by_user.side_effect = list_by_user
    repo.delete.side_effect = delete
    repo.update.side_effect = update
    return repo


def test_criar_valor_invalido_levanta_erro_com_fakes():
    svc = TransactionService(_make_repo_with_storage(), _make_repo_with_storage(), _make_repo_with_storage())
    with pytest.raises(ValidacaoError):
        svc.create_transaction(-1, date.today(), None, "Receita", 1, 1)


def test_criar_tipo_invalido_levanta_erro_com_fakes():
    svc = TransactionService(_make_repo_with_storage(), _make_repo_with_storage(), _make_repo_with_storage())
    with pytest.raises(ValidacaoError):
        svc.create_transaction(10, date.today(), None, "Invalid", 1, 1)


def test_validar_user_category_usuario_ausente_levanta_erro():
    svc = TransactionService(_make_repo_with_storage(), _make_repo_with_storage(), _make_repo_with_storage())
    with pytest.raises(EntidadeNaoEncontradaError):
        svc._validar_user_category(999, 1, "Receita")


def test_validar_user_category_categoria_ausente_levanta_erro():
    svc = TransactionService(_make_repo_with_storage(), _make_repo_with_storage([make_user(1)]), _make_repo_with_storage())
    with pytest.raises(EntidadeNaoEncontradaError):
        svc._validar_user_category(1, 999, "Receita")


def test_validar_user_category_tipo_incompativel():
    svc = TransactionService(_make_repo_with_storage(), _make_repo_with_storage([make_user(1)]), _make_repo_with_storage([make_category(type_="Despesa", cid=2)]))
    with pytest.raises(ValidacaoError):
        svc._validar_user_category(1, 2, "Receita")


def test_despesas_do_mes_soma_apenas_despesas():
    t1 = SimpleNamespace(amount=100, date=date(2025, 1, 5), type="Despesa", user_id=1)
    t2 = SimpleNamespace(amount=50, date=date(2025, 1, 6), type="Receita", user_id=1)
    svc = TransactionService(_make_repo_with_storage([t1, t2]), _make_repo_with_storage(), _make_repo_with_storage())
    assert svc._despesas_do_mes(1, date(2025, 1, 1)) == 100


def test_criar_obter_deletar_fluxo():
    tx = SimpleNamespace(amount=20, date=date(2025, 3, 1), type="Receita", user_id=1)
    tx_repo = _make_repo_with_storage([tx])
    us = _make_repo_with_storage([make_user(1)])
    cr = _make_repo_with_storage([make_category(type_="Receita", cid=1)])
    svc = TransactionService(tx_repo, us, cr)
    created = svc.create_transaction(20, date(2025, 3, 1), None, "Receita", 1, 1)
    got = svc.get_transaction(created.id)
    assert got.id == created.id
    svc.delete_transaction(created.id)
    with pytest.raises(EntidadeNaoEncontradaError):
        svc.get_transaction(created.id)


def test_criar_transacao_limite_mensal_excedido(monkeypatch):
    monkeypatch.setenv("MONTHLY_LIMIT", "50.0")
    existing = SimpleNamespace(amount=40, date=date(2025, 5, 1), type="Despesa", user_id=1)
    repo = _make_repo_with_storage([existing])
    us = _make_repo_with_storage([make_user(1)])
    cr = _make_repo_with_storage([make_category(type_="Despesa", cid=2)])
    svc = TransactionService(repo, us, cr)
    with pytest.raises(ValidacaoError):
        svc.create_transaction(20, date(2025, 5, 2), None, "Despesa", 1, 2)


def test_listar_transacoes_filtrar_e_ordenar():
    a = SimpleNamespace(id=1, amount=10, date=date(2025, 1, 1), type="Receita", user_id=1)
    b = SimpleNamespace(id=2, amount=5, date=date(2025, 1, 2), type="Despesa", user_id=2)
    tx_repo = _make_repo_with_storage([a, b])
    svc = TransactionService(tx_repo, _make_repo_with_storage(), _make_repo_with_storage())
    assert svc.list_transactions(user_id=1) == [a]
    assert svc.list_transactions(tipo="Despesa") == [b]
    res3 = svc.list_transactions(order_by="amount", order="desc")
    assert res3[0].amount == 10
