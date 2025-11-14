import importlib
import os


def test_obter_logger_retorna_logger():
    from src.utils.logger import get_logger
    lg = get_logger('tests')
    assert hasattr(lg, 'info')


def test_logger_escreve_arquivo(tmp_path, monkeypatch):
    # set LOG_FILE env before importing module to control path
    log_path = tmp_path / 'mylogs' / 'app.log'
    monkeypatch.setenv('LOG_FILE', str(log_path))
    # reload module to pick env var
    import src.utils.logger as logger_mod
    importlib.reload(logger_mod)
    lg = logger_mod.get_logger('t')
    lg.info('hello')
    assert log_path.exists()
import importlib
import logging
from pathlib import Path

import os


def test_logger_child_e_nome(monkeypatch):
    # ensure logger module will pick up a temp LOG_FILE
    tmp = Path(".tmp_logs")
    monkeypatch.setenv("LOG_FILE", str(tmp / "app.log"))
    # import module fresh
    import src.utils.logger as logger_mod
    importlib.reload(logger_mod)
    child = logger_mod.get_logger("mymod")
    assert isinstance(child, logging.Logger)
    assert child.name.endswith("mymod")


def test_logger_escreve_arquivo_2(monkeypatch, tmp_path):
    logfile = tmp_path / "mylogs.log"
    monkeypatch.setenv("LOG_FILE", str(logfile))
    import src.utils.logger as logger_mod
    importlib.reload(logger_mod)
    log = logger_mod.get_logger("tst")
    log.warning("hello world")
    assert logfile.exists()
