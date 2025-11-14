import importlib
import pytest


def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_criar_e_obter_usuario(client):
    payload = {"name": "FuncUser", "email": "func@example.com"}
    r = client.post("/users", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == payload["email"]

    uid = body["id"]
    r2 = client.get(f"/users/{uid}")
    assert r2.status_code == 200
    assert r2.json()["id"] == uid


def test_criar_usuario_email_duplicado_rejeita(client):
    payload = {"name": "A", "email": "dup@example.com"}
    r = client.post("/users", json=payload)
    assert r.status_code == 201
    # segunda criação com mesmo e-mail deve retornar 400
    r2 = client.post("/users", json=payload)
    assert r2.status_code == 400


def test_criar_categoria_e_filtrar_por_tipo(client):
    a = {"name": "Salario", "type": "Receita"}
    b = {"name": "Lanches", "type": "Despesa"}
    r1 = client.post("/categories", json=a)
    r2 = client.post("/categories", json=b)
    assert r1.status_code == 201 and r2.status_code == 201

    lista = client.get("/categories", params={"tipo": "Receita"})
    assert lista.status_code == 200
    dados = lista.json()
    assert any(x["type"] == "Receita" for x in dados)


def test_criar_transacao_valor_negativo_rejeita(client):
    # preparar usuario e categoria
    u = client.post("/users", json={"name": "U1", "email": "u1@example.com"}).json()
    c = client.post("/categories", json={"name": "C1", "type": "Receita"}).json()

    tx = {
        "amount": -10.0,
        "date": "2025-01-01",
        "description": "x",
        "type": "Receita",
        "user_id": u["id"],
        "category_id": c["id"],
    }
    r = client.post("/transactions", json=tx)
    assert r.status_code == 400


def test_limite_mensal_de_despesas_e_rejeicao(client, monkeypatch):
    # força um limite baixo
    monkeypatch.setenv("MONTHLY_LIMIT", "50.0")
    # recria o cliente para que o serviço leia a nova variável (TestClient criado no fixture já)
    # montar dados
    u = client.post("/users", json={"name": "U2", "email": "u2@example.com"}).json()
    c = client.post("/categories", json={"name": "Desp", "type": "Despesa"}).json()

    # cria uma despesa existente de 40 no mês
    tx1 = {
        "amount": 40.0,
        "date": "2025-05-01",
        "description": "old",
        "type": "Despesa",
        "user_id": u["id"],
        "category_id": c["id"],
    }
    r1 = client.post("/transactions", json=tx1)
    assert r1.status_code == 201

    # tentativa que excede (20) deve falhar
    tx2 = tx1.copy()
    tx2["amount"] = 20.0
    tx2["date"] = "2025-05-02"
    r2 = client.post("/transactions", json=tx2)
    assert r2.status_code == 400


def test_resumo_transacoes_calcula_receitas_e_despesas(client):
    u = client.post("/users", json={"name": "U3", "email": "u3@example.com"}).json()
    cre = client.post("/categories", json={"name": "R1", "type": "Receita"}).json()
    cde = client.post("/categories", json={"name": "D1", "type": "Despesa"}).json()

    client.post(
        "/transactions",
        json={
            "amount": 100.0,
            "date": "2025-06-01",
            "description": "sal",
            "type": "Receita",
            "user_id": u["id"],
            "category_id": cre["id"],
        },
    )
    client.post(
        "/transactions",
        json={
            "amount": 30.0,
            "date": "2025-06-02",
            "description": "buy",
            "type": "Despesa",
            "user_id": u["id"],
            "category_id": cde["id"],
        },
    )

    r = client.get("/transactions/summary", params={"user_id": u["id"]})
    assert r.status_code == 200
    data = r.json()
    assert data["receitas"] == 100.0
    assert data["despesas"] == 30.0
    assert data["saldo"] == 70.0


def test_export_sem_transacoes_retorna_404(client):
    u = client.post("/users", json={"name": "U4", "email": "u4@example.com"}).json()
    r = client.get("/transactions/export", params={"user_id": u["id"]})
    assert r.status_code == 404


def test_export_com_transacoes_cria_arquivo(client, tmp_path):
    u = client.post("/users", json={"name": "U5", "email": "u5@example.com"}).json()
    c = client.post("/categories", json={"name": "Cat5", "type": "Receita"}).json()
    client.post(
        "/transactions",
        json={
            "amount": 12.0,
            "date": "2025-07-01",
            "description": "x",
            "type": "Receita",
            "user_id": u["id"],
            "category_id": c["id"],
        },
    )
    r = client.get("/transactions/export", params={"user_id": u["id"]})
    assert r.status_code == 200
    body = r.json()
    assert "arquivo" in body
    # arquivo deve existir no cwd (tmp_path via fixture)
    from pathlib import Path

    assert Path(body["arquivo"]).exists()


def test_update_usuario_email_invalido_retorna_400(client):
    """Atualiza um usuário com email inválido — validação do Pydantic retorna 422.
    Antigo comportamento esperava 400 (mapeamento do serviço), mas a validação de schema
    acontece antes do serviço. Ajustamos o teste para esperar 422.
    """
    u = client.post("/users", json={"name": "UX", "email": "ux@example.com"}).json()
    r = client.put(f"/users/{u['id']}", json={"name": "UX", "email": "bad-email"})
    assert r.status_code == 422
