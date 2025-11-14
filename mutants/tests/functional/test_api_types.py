import importlib


def _make_client(monkeypatch, tmp_path):
    # helper to create a TestClient with a file-backed sqlite DB
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{db_file}")
    monkeypatch.chdir(tmp_path)

    import src.repositories.db as db_mod
    importlib.reload(db_mod)
    db_mod.init_db()

    import src.controllers.api as api_mod
    importlib.reload(api_mod)
    from fastapi.testclient import TestClient

    return TestClient(api_mod.app)


def test_user_crud_methods(monkeypatch, tmp_path):
    """Teste de API/REST: criar, obter, deletar e verificar comportamento (vários métodos HTTP)."""
    client = _make_client(monkeypatch, tmp_path)

    # criar
    r = client.post("/users", json={"name": "TUser", "email": "tuser@example.com"})
    assert r.status_code == 201
    uid = r.json()["id"]

    # obter (GET)
    r2 = client.get(f"/users/{uid}")
    assert r2.status_code == 200
    assert r2.json()["email"] == "tuser@example.com"

    # deletar (DELETE)
    r3 = client.delete(f"/users/{uid}")
    assert r3.status_code == 204

    # obter novamente deve retornar 404
    r4 = client.get(f"/users/{uid}")
    assert r4.status_code == 404

    client.close()


def test_create_user_invalid_email_returns_422(monkeypatch, tmp_path):
    """Valida que envio de email inválido gera 422 e mensagem de validação no corpo."""
    client = _make_client(monkeypatch, tmp_path)

    r = client.post("/users", json={"name": "Bad", "email": "not-an-email"})
    assert r.status_code == 422
    body = r.json()
    assert "detail" in body
    # detail costuma ser uma lista de erros de validação; checamos presença de 'email'
    detail = body["detail"]
    assert isinstance(detail, list)
    combined = " ".join(str(d).lower() for d in detail)
    assert "email" in combined

    client.close()


def test_export_no_transactions_returns_404_and_message(monkeypatch, tmp_path):
    """Verifica mensagem de erro específica ao tentar exportar sem transações."""
    client = _make_client(monkeypatch, tmp_path)

    # cria usuário sem transações
    u = client.post("/users", json={"name": "E1", "email": "e1@example.com"}).json()

    r = client.get("/transactions/export", params={"user_id": u["id"]})
    assert r.status_code == 404
    body = r.json()
    assert body.get("detail") == "Nenhuma transação encontrada para este usuário."

    client.close()
