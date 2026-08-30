from pathlib import Path

import pytest

from envirohealth.database.config import DatabaseConfig, read_env_file


def test_read_env_file_ignores_comments_and_blank_lines(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        """
        # local database
        DB_HOST=localhost

        DB_NAME='envirohealth'
        """
    )

    assert read_env_file(env_file) == {
        "DB_HOST": "localhost",
        "DB_NAME": "envirohealth",
    }


def test_database_config_uses_env_file_values(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        """
        DB_HOST=db
        DB_PORT=5433
        DB_NAME=envirohealth
        DB_USER=etl
        DB_PASSWORD=secret
        """
    )

    config = DatabaseConfig.from_env(env_file)

    assert config.host == "db"
    assert config.port == 5433
    assert config.database == "envirohealth"
    assert config.user == "etl"
    assert config.password == "secret"


def test_database_config_requires_credentials(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DB_NAME", raising=False)
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)

    with pytest.raises(ValueError, match="DB_NAME"):
        DatabaseConfig.from_env(tmp_path / "missing.env")

