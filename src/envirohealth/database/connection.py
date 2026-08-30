from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from envirohealth.database.config import DatabaseConfig


@contextmanager
def get_connection(config: DatabaseConfig | None = None) -> Iterator[object]:
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("Install database dependencies with `pip install -e .`.") from exc

    database_config = config or DatabaseConfig.from_env()
    with psycopg.connect(database_config.conninfo()) as connection:
        yield connection

