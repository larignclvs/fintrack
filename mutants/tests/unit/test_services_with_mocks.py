from datetime import date
from unittest.mock import Mock

import pytest

from src.services.user_service import UserService
from src.services.transaction_service import TransactionService
from src.services.exceptions import ValidacaoError


def test_create_user_success_and_duplicate_email():
    # repo stub: list_all returns no users initially, add returns created user with id
    repo = Mock()
    repo.list_all.return_value = []

    created = Mock(id=1, name="Alice", email="alice@example.com")
    repo.add.return_value = created

    svc = UserService(repo)

    out = svc.create_user("Alice", "alice@example.com")
    assert out.id == 1
    repo.add.assert_called_once()

    # now simulate duplicate email present
    repo.list_all.return_value = [Mock(email="alice@example.com", id=2)]
    with pytest.raises(ValidacaoError):
        svc.create_user("Alice", "alice@example.com")


def test_transaction_create_limit_and_success_using_mocks(monkeypatch):
    # Create tx_repo mock where list_by_user returns existing expenses summing 40
    tx_repo = Mock()
    existing = Mock(amount=40, date=date(2025, 6, 1), type="Despesa", user_id=1)
    tx_repo.list_by_user.return_value = [existing]

    # user and category repos return existing entities
    user_repo = Mock()
    user_repo.get.return_value = Mock(id=1)
    cat_repo = Mock()
    cat_repo.get.return_value = Mock(id=2, type="Despesa")

    # set low monthly limit
    monkeypatch.setenv("MONTHLY_LIMIT", "50.0")

    svc = TransactionService(tx_repo, user_repo, cat_repo)

    # attempt to create expense of 20 should raise (40 + 20 > 50)
    with pytest.raises(ValidacaoError):
        svc.create_transaction(20, date(2025, 6, 2), None, "Despesa", 1, 2)

    # now make list_by_user empty and simulate add returning created tx
    tx_repo.list_by_user.return_value = []
    created = Mock(id=5, amount=10, date=date(2025, 6, 2), type="Despesa", user_id=1)
    tx_repo.add.return_value = created

    out = svc.create_transaction(10, date(2025, 6, 2), None, "Despesa", 1, 2)
    assert out.id == 5
    tx_repo.add.assert_called()
