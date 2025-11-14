def test_create_user_invalid_email_returns_422(client):
    # pydantic validation should return 422 for invalid email format
    payload = {"name": "Bob", "email": "not-an-email"}
    r = client.post("/users", json=payload)
    assert r.status_code == 422
    data = r.json()
    # detail should be present and be a list of validation errors
    assert "detail" in data
    assert isinstance(data["detail"], list)


def test_get_nonexistent_user_returns_404_with_message(client):
    r = client.get("/users/9999")
    assert r.status_code == 404
    data = r.json()
    assert data.get("detail") == "Usuário não encontrado."
