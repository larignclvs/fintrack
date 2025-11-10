import os
from dotenv import load_dotenv

load_dotenv()

def get_setting(key: str, default: str | None = None) -> str | None:
    """
    Retorna o valor de uma variável do .env.

    Args:
        key (str): Nome da variável de ambiente.
        default (str | None): Valor padrão caso não seja encontrada.

    Returns:
        str | None: Valor da variável.
    """
    return os.getenv(key.upper(), default)

if __name__ == "__main__":
    print("DATABASE_URL:", get_setting("DATABASE_URL"))
    print("LOG_LEVEL:", get_setting("LOG_LEVEL"))
