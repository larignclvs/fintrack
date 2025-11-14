import importlib


def _init_db_with_env(monkeypatch, db_url):
    monkeypatch.setenv("DATABASE_URL", db_url)
    import src.repositories.db as db_mod
    importlib.reload(db_mod)
    db_mod.init_db()
    return db_mod


import pytest


@pytest.fixture
def client(monkeypatch, tmp_path):
    db_file = tmp_path / "test.db"
    db_mod = _init_db_with_env(monkeypatch, f"sqlite+pysqlite:///{db_file}")

    import src.controllers.api as api_mod
    importlib.reload(api_mod)
    from fastapi.testclient import TestClient

    client = TestClient(api_mod.app)
    yield client
    client.close()


@pytest.fixture
def db_session(tmp_path, monkeypatch):
   
    db_mod = _init_db_with_env(monkeypatch, "sqlite+pysqlite:///:memory:")
    SessionLocal = db_mod.SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        # cleanup schema
        from src.models.base import Base

        Base.metadata.drop_all(bind=db_mod.engine)
