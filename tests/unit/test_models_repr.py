from datetime import date

from src.models.transaction import Transaction
from src.models.category import Category
from src.models.user import User


def test_repr_transacao_contem_classe_e_campos():
    t = Transaction()
    t.amount = 1
    t.type = 'Receita'
    r = repr(t)
    assert 'Transaction' in r
    # when constructed with fields, repr should include type/amount info
    t2 = Transaction(amount=10.0, date=date(2025, 1, 1), type="Receita", user_id=1, category_id=1)
    r2 = repr(t2)
    assert "Transaction" in r2
    assert "amount" in r2 or "10.0" in r2


def test_repr_categoria_e_usuario_e_campos():
    c = Category(name="A", type="Despesa")
    u = User(name="X", email="x@gmail.com")
    rc = repr(c)
    ru = repr(u)
    assert 'Category' in rc
    assert 'type' in rc or 'Despesa' in rc
    assert 'User' in ru
    assert 'email' in ru or 'x@gmail.com' in ru
