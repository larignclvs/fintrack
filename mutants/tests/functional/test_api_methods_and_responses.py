import pytest


def test_health_and_user_crud(client):
    # health
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

    # create user
    payload = {"name": "Alice", "email": "alice@example.com"}
    r = client.post("/users", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert "id" in body and body["name"] == "Alice" and body["email"] == "alice@example.com"

    user_id = body["id"]

    # get user
    r = client.get(f"/users/{user_id}")
    assert r.status_code == 200
    got = r.json()
    assert got["id"] == user_id
    assert got["email"] == "alice@example.com"


def test_method_not_allowed_on_user_detail(client):
    # POST to a detail endpoint should be 405
    r = client.post("/users/1", json={"name": "x"})
    assert r.status_code == 405
