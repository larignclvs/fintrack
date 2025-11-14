from unittest.mock import Mock

import pytest

from src.services.user_service import UserService
from src.services.exceptions import ValidacaoError, EntidadeNaoEncontradaError


def make_repo(users=None):
    m = Mock()
    users = users or []
    m.list_all.return_value = list(users)
    def _get(uid):
        for u in users:
            if getattr(u, "id", None) == uid:
                return u
        return None

    m.get.side_effect = lambda i: _get(i)
    m.add.side_effect = lambda obj: setattr(obj, "id", 1) or obj
    m.update.side_effect = lambda obj: obj
    m.delete.side_effect = lambda obj: None
    return m


def test_create_user_validates_name_and_email():
    repo = make_repo()
    svc = UserService(repo)
    with pytest.raises(ValidacaoError):
        svc.create_user("  ", "x@x.com")
    with pytest.raises(ValidacaoError):
        svc.create_user("Name", "bad-email")


def test_create_user_duplicate_email_rejects():
    existing = Mock(id=2, name="A", email="a@x.com")
    repo = make_repo([existing])
    svc = UserService(repo)
    with pytest.raises(ValidacaoError):
        svc.create_user("B", "a@x.com")


def test_get_user_not_found_raises():
    repo = make_repo()
    svc = UserService(repo)
    with pytest.raises(EntidadeNaoEncontradaError):
        svc.get_user(999)


def test_update_user_validations_and_duplicates():
    u = Mock(id=1, name="fulano", email="fulano@x.com")
    other = Mock(id=2, name="Other", email="ciclano@x.com")
    repo = make_repo([u, other])
    svc = UserService(repo)
    with pytest.raises(ValidacaoError):
        svc.update_user(1, name="   ")
    with pytest.raises(ValidacaoError):
        svc.update_user(1, email="no-at")
    with pytest.raises(ValidacaoError):
        svc.update_user(1, email="ciclano@x.com")


def test_delete_user_flow_calls_repo_delete():
    u = Mock(id=5, name="fulano", email="fulano@x.com")
    repo = make_repo([u])
    svc = UserService(repo)
    svc.delete_user(5)
    repo.delete.assert_called()
