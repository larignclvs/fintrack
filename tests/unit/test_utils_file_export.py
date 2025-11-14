import os
import csv

from src.utils.file_export import export_transactions_to_csv, import_transactions_from_csv
from datetime import date

from pathlib import Path

from types import SimpleNamespace




def test_exportar_e_importar_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    class T:
        pass

    t1 = T(); t1.id = 1; t1.amount = 12.5; t1.date = t1_date = __import__('datetime').date(2025,1,1); t1.type = 'Receita'; t1.description = None; t1.user_id = 1; t1.category_id = 1
    t2 = T(); t2.id = 2; t2.amount = 3.5; t2.date = __import__('datetime').date(2025,2,2); t2.type = 'Despesa'; t2.description = 'x'; t2.user_id = 2; t2.category_id = 2
    path = export_transactions_to_csv([t1, t2], user_id=1)
    assert path.endswith('.csv')
    assert os.path.exists(path)
    data = import_transactions_from_csv(path)
    assert isinstance(data, list) and len(data) == 2


def test_importar_ausente_gera_erro(tmp_path):
    p = tmp_path / 'nope.csv'
    try:
        import_transactions_from_csv(str(p))
        assert False, "should have raised"
    except FileNotFoundError:
        pass


def test_exportar_formatacao_valor(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    class T: pass
    t = T(); t.id = 1; t.amount = 1.2; t.date = __import__('datetime').date(2025,1,1); t.type='Receita'; t.description=''; t.user_id=42; t.category_id=1
    path = export_transactions_to_csv([t], user_id=42)
    with open(path, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    assert rows[0]['amount'] == '1.20'

def test_export_cria_arquivo_e_retorna_caminho(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    t = SimpleNamespace(id=1, amount=12.5, date=date(2025, 1, 1), type="Receita", description=None, user_id=1, category_id=1)
    txs = [t]
    path = export_transactions_to_csv(txs, user_id=1)
    assert Path(path).exists()


def test_export_escreve_colunas_esperadas(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    t = SimpleNamespace(id=2, amount=3.0, date=date(2025, 2, 2), type="Despesa", description="x", user_id=2, category_id=1)
    txs = [t]
    path = export_transactions_to_csv(txs, user_id=2)
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert rows[0] == ["id", "date", "amount", "type", "description", "user_id", "category_id"]
    assert rows[1][0] == "2"


def test_importa_ler_linhas(tmp_path):
    p = tmp_path / "in.csv"
    p.write_text("id,date,amount,type,description,user_id,category_id\n1,2025-01-01,10.00,Receita,,1,1\n")
    data = import_transactions_from_csv(str(p))
    assert isinstance(data, list)
    assert data[0]["id"] == "1"


def test_importa_gera_arquivo_nao_encontrado():
    import pytest

    with pytest.raises(FileNotFoundError):
        import_transactions_from_csv("no-way-this-file.csv")


def test_nome_arquivo_export_contem_usuario(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    t = SimpleNamespace(id=3, amount=1.0, date=date(2025, 3, 3), type="Receita", description=None, user_id=42, category_id=1)
    txs = [t]
    path = export_transactions_to_csv(txs, user_id=42)
    assert "transactions_42_" in Path(path).name


def test_exportar_formatacao_valor_2(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    t = SimpleNamespace(id=4, amount=1.5, date=date(2025, 4, 4), type="Receita", description=None, user_id=1, category_id=1)
    txs = [t]
    path = export_transactions_to_csv(txs, user_id=1)
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows[1][2] == "1.50"
