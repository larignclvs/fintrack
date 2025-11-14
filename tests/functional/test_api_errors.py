import importlib
import pytest


def test_get_user_not_found(client):
    r = client.get("/users/999")
    assert r.status_code == 404


def test_update_user_not_found_returns_400(client):
    payload = {"name": "X", "email": "x@x.com"}
    r = client.put("/users/999", json=payload)
    assert r.status_code == 400


def test_delete_user_not_found_returns_404(client):
    r = client.delete("/users/999")
    assert r.status_code == 404


def test_create_category_invalid_type_returns_400(client):
    r = client.post("/categories", json={"name": "C", "type": "X"})
    assert r.status_code == 400


def test_category_not_found_and_update_delete_errors(client):
    assert client.get("/categories/999").status_code == 404
    assert client.put("/categories/999", json={"name": "N", "type": "Receita"}).status_code == 400
    assert client.delete("/categories/999").status_code == 404


def test_transaction_not_found_update_delete(client):
    assert client.get("/transactions/999").status_code == 404
    payload = {"amount": 10.0}
    assert client.put("/transactions/999", json=payload).status_code == 400
    assert client.delete("/transactions/999").status_code == 404
