from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

import pandas as pd

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SourceSpec:
    source_name: str
    table_name: str
    file_pattern: str
    column_mapping: dict[str, str]
    required_columns: tuple[str, ...]
    integer_columns: tuple[str, ...] = ()

    @property
    def copy_columns(self) -> list[str]:
        return ["ingestion_run_id", "source_file", "source_row_number", *self.column_mapping.values()]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_source_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def validate_required_columns(frame: pd.DataFrame, spec: SourceSpec) -> None:
    missing = sorted(set(spec.required_columns) - set(frame.columns))
    if missing:
        raise ValueError(f"{pathless(spec)} is missing required columns: {missing}")


def pathless(spec: SourceSpec) -> str:
    return f"{spec.source_name} ({spec.table_name})"


def prepare_raw_frame(path: Path, spec: SourceSpec, ingestion_run_id: int) -> pd.DataFrame:
    frame = read_source_csv(path)
    validate_required_columns(frame, spec)

    prepared = frame.loc[:, list(spec.column_mapping.keys())].rename(columns=spec.column_mapping)
    normalize_nullable_integer_columns(prepared, spec.integer_columns)
    prepared.insert(0, "source_row_number", range(2, len(prepared) + 2))
    prepared.insert(0, "source_file", path.name)
    prepared.insert(0, "ingestion_run_id", ingestion_run_id)
    return prepared


def normalize_nullable_integer_columns(frame: pd.DataFrame, columns: tuple[str, ...]) -> None:
    for column in columns:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").astype("Int64")


def source_year(path: Path, frame: pd.DataFrame) -> int | None:
    if "Year" in frame.columns and frame["Year"].nunique(dropna=True) == 1:
        return int(frame["Year"].dropna().iloc[0])

    for token in path.stem.split("_"):
        if token.isdigit() and len(token) == 4:
            return int(token)
    return None


def copy_frame(connection: object, table_name: str, frame: pd.DataFrame, columns: list[str]) -> None:
    csv_buffer = StringIO()
    frame.to_csv(csv_buffer, index=False, columns=columns)
    csv_buffer.seek(0)
    column_sql = ", ".join(columns)
    copy_sql = f"COPY {table_name} ({column_sql}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"

    with connection.cursor() as cursor, cursor.copy(copy_sql) as copy:
        copy.write(csv_buffer.getvalue())


def count_rows_for_source_file(connection: object, table_name: str, source_file: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE source_file = %s", (source_file,))
        row = cursor.fetchone()
    return int(row[0])


def delete_existing_source_file(connection: object, table_name: str, source_file: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM {table_name} WHERE source_file = %s", (source_file,))


def start_ingestion_run(
    connection: object,
    spec: SourceSpec,
    path: Path,
    rows_read: int,
    year: int | None,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO raw.ingestion_runs (
                source_name,
                source_file,
                source_year,
                rows_read,
                file_size_bytes,
                file_sha256,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'running')
            RETURNING ingestion_run_id
            """,
            (spec.source_name, path.name, year, rows_read, path.stat().st_size, file_sha256(path)),
        )
        row = cursor.fetchone()
    return int(row[0])


def complete_ingestion_run(connection: object, run_id: int, rows_loaded: int) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE raw.ingestion_runs
            SET completed_at = now(), rows_loaded = %s, status = 'success'
            WHERE ingestion_run_id = %s
            """,
            (rows_loaded, run_id),
        )


def fail_ingestion_run(connection: object, run_id: int, error: Exception) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE raw.ingestion_runs
            SET completed_at = now(), status = 'failed', error_message = %s
            WHERE ingestion_run_id = %s
            """,
            (str(error), run_id),
        )


def load_source_file(connection: object, path: Path, spec: SourceSpec) -> dict[str, object]:
    source_frame = read_source_csv(path)
    validate_required_columns(source_frame, spec)
    year = source_year(path, source_frame)
    rows_read = len(source_frame)
    run_id = start_ingestion_run(connection, spec, path, rows_read, year)
    connection.commit()

    try:
        LOGGER.info("Reloading %s into %s", path.name, spec.table_name)
        delete_existing_source_file(connection, spec.table_name, path.name)
        prepared = prepare_raw_frame(path, spec, run_id)
        copy_frame(connection, spec.table_name, prepared, spec.copy_columns)
        rows_loaded = count_rows_for_source_file(connection, spec.table_name, path.name)

        if rows_loaded != rows_read:
            raise ValueError(f"Expected {rows_read:,} rows loaded for {path.name}; found {rows_loaded:,}")

        complete_ingestion_run(connection, run_id, rows_loaded)
        return {
            "ingestion_run_id": run_id,
            "source_name": spec.source_name,
            "source_file": path.name,
            "source_year": year,
            "rows_read": rows_read,
            "rows_loaded": rows_loaded,
            "status": "success",
        }
    except Exception as exc:
        connection.rollback()
        try:
            fail_ingestion_run(connection, run_id, exc)
            connection.commit()
        except Exception:
            LOGGER.exception("Unable to mark ingestion run %s as failed", run_id)
            connection.rollback()
        raise
