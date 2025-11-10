from datetime import date
from src.repositories.db import SessionLocal, init_db
from src.models.user import User
from src.models.category import Category
from src.models.transaction import Transaction

init_db()
session = SessionLocal()

user = User(name="Gabrielle", email="gabi@example.com")
session.add(user)
session.commit()
session.refresh(user)

cat1 = Category(name="Salário", type="Receita")
cat2 = Category(name="Mercado", type="Despesa")
session.add_all([cat1, cat2])
session.commit()
session.refresh(cat1)
session.refresh(cat2)

tx1 = Transaction(amount=2500.0, date=date.today(), description="Salário do mês", type="Receita", user_id=user.id, category_id=cat1.id)
tx2 = Transaction(amount=300.0, date=date.today(), description="Compras no mercado", type="Despesa", user_id=user.id, category_id=cat2.id)
session.add_all([tx1, tx2])
session.commit()

print("✅ Dados inseridos com sucesso!")
session.close()
