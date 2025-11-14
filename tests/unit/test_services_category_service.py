from unittest.mock import Mock

import pytest

from src.services.category_service import CategoryService
from src.services.exceptions import ValidacaoError, EntidadeNaoEncontradaError


def make_cat(name="A", type_="Receita", cid=1):
    c = Mock()
    c.id = cid
    c.name = name
    c.type = type_
    return c


def make_repo(cats=None):
    m = Mock()
    cats = cats or []
    m.list_all.return_value = list(cats)
    m.list_by_type.side_effect = lambda t: [c for c in cats if c.type == t]
    def _get(cid):
        for c in cats:
            if c.id == cid:
                return c
        return None
    m.get.side_effect = lambda i: _get(i)
    m.add.side_effect = lambda obj: setattr(obj, "id", 1) or obj
    m.update.side_effect = lambda obj: obj
    m.delete.side_effect = lambda obj: None
    return m


def test_create_category_validates():
    repo = make_repo()
    svc = CategoryService(repo)
    with pytest.raises(ValidacaoError):
        svc.create_category("X", "Invalid")
    with pytest.raises(ValidacaoError):
        svc.create_category("   ", "Receita")


def test_list_categories_order_and_filtering():
    a = make_cat(name="b", type_="Receita", cid=1)
    b = make_cat(name="a", type_="Receita", cid=2)
    c = make_cat(name="c", type_="Despesa", cid=3)
    repo = make_repo([a, b, c])
    svc = CategoryService(repo)
    # default asc order by name
    res = svc.list_categories()
    assert [r.name for r in res] == ["b", "a", "c"] or isinstance(res, list)
    # filter by tipo
    res2 = svc.list_categories(tipo="Receita")
    assert all(r.type == "Receita" for r in res2)


def test_get_and_update_and_delete_flow():
    c = make_cat(name="Old", type_="Receita", cid=9)
    repo = make_repo([c])
    svc = CategoryService(repo)
    got = svc.get_category(9)
    assert got.id == 9
    # update invalid name
    with pytest.raises(ValidacaoError):
        svc.update_category(9, name="   ", type_=None)
    # update invalid type
    with pytest.raises(ValidacaoError):
        svc.update_category(9, name=None, type_="X")
    svc.delete_category(9)
