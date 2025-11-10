import csv
from pathlib import Path
from datetime import datetime
from typing import Iterable, List

from src.models.transaction import Transaction
from src.utils.logger import get_logger

logger = get_logger(__name__)


def export_transactions_to_csv(transactions: Iterable[Transaction], user_id: int | None = None) -> str:
    """
    Exporta uma lista de transações para um arquivo CSV dentro da pasta 'exports/'.

    Args:
        transactions (Iterable[Transaction]): Lista ou iterável de transações.
        user_id (int | None): ID do usuário (opcional, usado no nome do arquivo).

    Returns:
        str: Caminho completo do arquivo CSV gerado.
    """
    export_dir = Path("exports")
    export_dir.mkdir(parents=True, exist_ok=True)

    # Nome do arquivo: transactions_<user>_<data>.csv
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transactions_{user_id or 'all'}_{timestamp}.csv"
    path = export_dir / filename

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "amount", "type", "description", "user_id", "category_id"])

        for t in transactions:
            writer.writerow([
                t.id,
                t.date.isoformat() if hasattr(t.date, "isoformat") else t.date,
                f"{t.amount:.2f}",
                t.type,
                t.description or "",
                t.user_id,
                t.category_id
            ])

    logger.info("✅ Arquivo CSV exportado com sucesso: %s", path)
    return str(path)


def import_transactions_from_csv(filepath: str) -> List[dict]:
    """
    Lê um arquivo CSV de transações e retorna uma lista de dicionários.

    Args:
        filepath (str): Caminho do arquivo CSV.

    Returns:
        List[dict]: Lista contendo os dados das transações.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"O arquivo {filepath} não foi encontrado.")

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]

    logger.info("📥 %d transações importadas de %s", len(data), path)
    return data
