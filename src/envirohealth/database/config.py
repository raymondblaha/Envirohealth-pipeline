from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from envirohealth.paths import PROJECT_ROOT


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    database: str
    user: str
    password: str

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> DatabaseConfig:
        values = dict(os.environ)
        values.update(read_env_file(env_file or PROJECT_ROOT / ".env"))

        return cls(
            host=values.get("DB_HOST", "localhost"),
            port=int(values.get("DB_PORT", "5432")),
            database=required(values, "DB_NAME"),
            user=required(values, "DB_USER"),
            password=required(values, "DB_PASSWORD"),
        )

    def conninfo(self) -> str:
        return (
            f"host={self.host} port={self.port} dbname={self.database} "
            f"user={self.user} password={self.password}"
        )


def read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def required(values: dict[str, str], key: str) -> str:
    value = values.get(key)
    if not value:
        raise ValueError(f"Missing required database setting: {key}")
    return value

