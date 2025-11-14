import logging
from logging.handlers import RotatingFileHandler
import os


# Defer import of config.settings and provide environment fallback so that
# mutated workspaces that don't have the top-level `config` package won't
# fail at import time.
def _get_setting(name: str, default=None):
    try:
        from config.settings import get_setting as _gs

        return _gs(name, default)
    except Exception:
        return os.environ.get(name, default)


# === Configurações vindas do .env (com fallback) ===
LOG_FILE = _get_setting("LOG_FILE", ".logs/app.log")
LOG_LEVEL = _get_setting("LOG_LEVEL", "INFO").upper()

# Garante que a pasta .logs exista
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# === Cria handler rotativo (limita tamanho e mantém histórico) ===
rotating_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=1024 * 1024,  # 1 MB
    backupCount=5,  # mantém até 5 arquivos antigos
    encoding="utf-8",
)

# === Formato dos logs ===
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
rotating_handler.setFormatter(formatter)

# === Logger global ===
logger = logging.getLogger("fintrack")
logger.setLevel(LOG_LEVEL)
logger.addHandler(rotating_handler)


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger configurado para o módulo especificado."""
    return logger.getChild(name)
