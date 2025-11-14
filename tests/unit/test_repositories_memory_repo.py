import pytest

from src.repositories.memory_repo import MemoryRepository
import pytest
from unittest.mock import Mock
from types import SimpleNamespace

def test_memoria_adicionar_e_obter():
    repo = MemoryRepository()
    obj = type("X", (), {})()
    obj.name = "a"
    added = repo.add(obj)
    assert hasattr(added, "id")
    assert repo.get(added.id) is added


@pytest.mark.parametrize("n", [1, 3, 5])
def test_memoria_listar_contagem(n):
    repo = MemoryRepository()
    for i in range(n):
        repo.add(type("T", (), {})())
    assert len(repo.list_all()) == n


def test_memoria_atualizar_por_id_e_obter():
    repo = MemoryRepository()
    o = type("O", (), {})()
    o.foo = 1
    added = repo.add(o)
    updated = repo.update(added.id, foo=2)
    assert updated.foo == 2
    repo.update(added.id, foo=3)
    assert repo.get(added.id).foo == 3


def test_memoria_deletar_e_ausente():
    repo = MemoryRepository()
    o = type("O", (), {})()
    added = repo.add(o)
    repo.delete(added.id)
    assert repo.get(added.id) is None
    repo.delete(999)
    assert repo.update(999, name="x") is None


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

    def list_by_user(user_id):
        return [i for i in storage if getattr(i, 'user_id', None) == user_id]

    def update(obj, **fields):
        if not hasattr(obj, 'id'):
            obj_id = obj
            target = get(obj_id)
            if not target:
                return None
            for k, v in fields.items():
                setattr(target, k, v)
            return target
        else:
            for k, v in fields.items():
                setattr(obj, k, v)
            return obj

    def delete(obj_or_id):
        obj = obj_or_id
        if not hasattr(obj_or_id, 'id'):
            obj = get(obj_or_id)
            if obj:
                try:
                    storage.remove(obj)
                except ValueError:
                    pass
        else:
            try:
                storage.remove(obj_or_id)
            except Exception:
                pass

    repo.add.side_effect = add
    repo.get.side_effect = get
    repo.list_all.side_effect = list_all
    repo.list_by_user.side_effect = list_by_user
    repo.update.side_effect = update
    repo.delete.side_effect = delete
    repo.list.side_effect = list_all
    return repo


def test_adicionar_atribui_id_e_obter():
    repo = _make_repo_with_storage()
    t = SimpleNamespace(amount=1)
    added = repo.add(t)
    assert added.id is not None
    assert repo.get(added.id) is added


def test_listar_e_listar_por_usuario():
    a = SimpleNamespace(id=1, user_id=1)
    b = SimpleNamespace(id=2, user_id=2)
    repo = _make_repo_with_storage([a, b])
    assert len(repo.list_all()) == 2
    assert repo.list_by_user(1) == [a]


def test_atualizar_por_objeto_e_por_id():
    t = SimpleNamespace(id=1, amount=5)
    repo = _make_repo_with_storage([t])
    repo.update(t, amount=8)
    assert t.amount == 8
    repo.update(1, amount=9)
    assert repo.get(1).amount == 9


def test_deletar_por_id_e_por_objeto():
    t = SimpleNamespace(id=1)
    repo = _make_repo_with_storage([t])
    repo.delete(1)
    assert repo.get(1) is None
    repo.add(t)
    repo.delete(t)
    assert repo.get(t.id) is None


def test_adicionar_multiplos_ids_incremento():
    repo = _make_repo_with_storage()
    a = repo.add(SimpleNamespace())
    b = repo.add(SimpleNamespace())
    assert b.id == a.id + 1


def test_obter_ausente_retorna_none():
    repo = _make_repo_with_storage()
    assert repo.get(999) is None


def test_deletar_ausente_nao_faz_nada():
    repo = _make_repo_with_storage()
    # should not raise
    repo.delete(12345)


def test_alias_list_equivale_list_all():
    a = SimpleNamespace(id=1)
    repo = _make_repo_with_storage([a])
    assert repo.list() == repo.list_all()
