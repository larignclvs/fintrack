import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test_specific.db"

from src.repositories.db import init_db  

dbfile = Path("test_specific.db")
if dbfile.exists():
    dbfile.unlink()

init_db()

from fastapi.testclient import TestClient
from src.controllers.api import app 

client = TestClient(app)


def test_create_user_empty_name_returns_400_and_message():
    r = client.post("/users", json={"name": "", "email": "alexia@email.com"})
    assert r.status_code == 400
    assert "Nome é obrigatório" in r.json().get("detail", "")


def test_create_user_duplicate_email_returns_400_and_message():
    # create first user
    r1 = client.post("/users", json={"name": "U1", "email": "gabi@email.com"})
    assert r1.status_code == 201

    # attempt duplicate
    r2 = client.post("/users", json={"name": "U2", "email": "gabi@email.com"})
    assert r2.status_code == 400
    assert "Já existe um usuário com este e-mail" in r2.json().get("detail", "")


def test_get_nonexistent_user_returns_404_and_message():
    r = client.get("/users/99999")
    assert r.status_code == 404
    assert "Usuário não encontrado" in r.json().get("detail", "")


def test_get_nonexistent_transaction_returns_404_and_message():
    r = client.get("/transactions/99999")
    assert r.status_code == 404
    detail = r.json().get("detail", "").lower()
    assert "não encontr" in detail
