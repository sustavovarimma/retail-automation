"""Подключение к PostgreSQL."""
from contextlib import contextmanager
import psycopg2


@contextmanager
def get_connection(cfg):
    """Контекст-менеджер соединения: commit при успехе, rollback при ошибке."""
    conn = psycopg2.connect(
        host=cfg["database"]["host"],
        port=cfg["database"]["port"],
        dbname=cfg["database"]["name"],
        user=cfg["database"]["user"],
        password=cfg["database"]["password"],
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
