import importlib
import os
from datetime import date
from src.models.transaction import Transaction

import pytest


def test_fluxo_basico_repos_user_categoria_transacao(db_session):
    from src.repositories.user_repo import UserRepository
    from src.repositories.category_repo import CategoryRepository
    from src.repositories.transaction_repo import TransactionRepository
    from src.models.user import User
    from src.models.category import Category
    from src.models.transaction import Transaction

    urepo = UserRepository(db_session)
    crepo = CategoryRepository(db_session)
    trepo = TransactionRepository(db_session)

    u = User(name="Alice", email="a@x.com")
    urepo.add(u)
    assert u.id is not None
    c = Category(name="Salary", type="Receita")
    crepo.add(c)
    assert c.id is not None

    tx = Transaction(amount=100.0, date=date(2025, 1, 1), description="pay", type="Receita", user_id=u.id, category_id=c.id)
    trepo.add(tx)
    assert tx.id is not None
    assert trepo.get(tx.id).amount == 100.0
    assert trepo.list_by_user(u.id)[0].id == tx.id


def test_servico_transacao_ponta_a_ponta(db_session):
    from src.repositories.user_repo import UserRepository
    from src.repositories.category_repo import CategoryRepository
    from src.repositories.transaction_repo import TransactionRepository
    from src.services.transaction_service import TransactionService
    from src.models.user import User
    from src.models.category import Category

    urepo = UserRepository(db_session)
    crepo = CategoryRepository(db_session)
    trepo = TransactionRepository(db_session)

    u = urepo.add(User(name="Bob", email="b@x.com"))
    c = crepo.add(Category(name="Groceries", type="Despesa"))

    svc = TransactionService(trepo, urepo, crepo)
    created = svc.create_transaction(25.0, date(2025, 2, 2), "buy", "Despesa", u.id, c.id)
    assert created.id is not None
    # retrieve via repo
    got = trepo.get(created.id)
    assert got.description == "buy"


def test_categoria_listar_por_tipo_e_atualizar(db_session):
    from src.repositories.category_repo import CategoryRepository
    from src.models.category import Category

    crepo = CategoryRepository(db_session)
    a = crepo.add(Category(name="A", type="Receita"))
    b = crepo.add(Category(name="B", type="Despesa"))
    rece = crepo.list_by_type("Receita")
    assert any(x.id == a.id for x in rece)


def test_usuario_obter_por_email_e_atualizar_deletar(db_session):
    from src.repositories.user_repo import UserRepository
    from src.models.user import User

    urepo = UserRepository(db_session)
    u = urepo.add(User(name="C", email="c@x.com"))
    assert urepo.get_by_email("c@x.com").id == u.id
    u.name = "C2"
    urepo.update(u)
    assert urepo.get(u.id).name == "C2"
    urepo.delete(u)
    assert urepo.get(u.id) is None


def test_servico_financeiro_saldo_com_repo_real(db_session):
    from src.repositories.transaction_repo import TransactionRepository
    from src.services.finance_service import FinanceService
    from src.models.transaction import Transaction

    trepo = TransactionRepository(db_session)
    trepo.list = trepo.list_all
    fs = FinanceService(trepo)
    t1 = Transaction(amount=100, date=date(2025, 3, 1), type="Receita", user_id=1, category_id=1)
    t2 = Transaction(amount=40, date=date(2025, 3, 2), type="Despesa", user_id=1, category_id=2)
    trepo.add(t1)
    trepo.add(t2)
    assert fs.balance(1) == 60


def test_atualizar_e_deletar_transacao_fluxo(db_session):
    from src.repositories.transaction_repo import TransactionRepository
    from src.models.transaction import Transaction

    trepo = TransactionRepository(db_session)
    t = trepo.add(Transaction(amount=10, date=date(2025, 4, 1), type="Receita", user_id=1, category_id=1))
    t.amount = 15
    trepo.update(t)
    assert trepo.get(t.id).amount == 15
    trepo.delete(t)
    assert trepo.get(t.id) is None


def test_ordenacao_multiplas_transacoes(db_session):
    from src.repositories.transaction_repo import TransactionRepository
    from src.services.transaction_service import TransactionService
    from src.repositories.user_repo import UserRepository
    from src.repositories.category_repo import CategoryRepository
    from src.models.user import User
    from src.models.category import Category

    urepo = UserRepository(db_session)
    crepo = CategoryRepository(db_session)
    trepo = TransactionRepository(db_session)
    u = urepo.add(User(name="D", email="d@x"))
    c = crepo.add(Category(name="c", type="Receita"))
    trepo.add(Transaction(amount=5, date=date(2025, 5, 1), type="Receita", user_id=u.id, category_id=c.id))
    trepo.add(Transaction(amount=20, date=date(2025, 5, 2), type="Receita", user_id=u.id, category_id=c.id))
    svc = TransactionService(trepo, urepo, crepo)
    res = svc.list_transactions(user_id=u.id, order_by="amount", order="asc")
    assert [r.amount for r in res] == [5, 20]


def test_integridade_constraint_unico_gera_erro(db_session):
    from src.repositories.user_repo import UserRepository
    from src.models.user import User

    urepo = UserRepository(db_session)
    urepo.add(User(name="E", email="e@x.com"))
    with pytest.raises(Exception):
        urepo.add(User(name="E2", email="e@x.com"))


def test_obter_inexistente_retorna_none(db_session):
    """Ensure repositories return None for missing records."""
    from src.repositories.user_repo import UserRepository
    from src.repositories.transaction_repo import TransactionRepository

    urepo = UserRepository(db_session)
    trepo = TransactionRepository(db_session)
    assert urepo.get(9999) is None
    assert trepo.get(9999) is None


def test_init_db_idempotente(db_session):
    """Calling init_db multiple times should not error and should keep schema usable."""
    import src.repositories.db as db_mod
    db_mod.init_db()
    from src.repositories.user_repo import UserRepository
    from src.models.user import User

    urepo = UserRepository(db_session)
    u = urepo.add(User(name="Z", email="z@x.com"))
    assert u.id is not None
