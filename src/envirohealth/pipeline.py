from __future__ import annotations

import argparse
import logging

import pandas as pd

from envirohealth.database.connection import get_connection
from envirohealth.database.execute import (
    ANALYSIS_FILES,
    ANALYTICS_FILES,
    SCHEMA_FILES,
    TRANSFORMATION_FILES,
    execute_sql_files,
)
from envirohealth.ingestion.cdc import discover_cdc_files
from envirohealth.ingestion.common import load_source_file
from envirohealth.ingestion.epa import discover_epa_files
from envirohealth.paths import OUTPUTS_DIR

LOGGER = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def discover_sources() -> list[tuple[object, object]]:
    return [*discover_epa_files(), *discover_cdc_files()]


def write_run_summary(rows: list[dict[str, object]]) -> None:
    output_path = OUTPUTS_DIR / "pipeline" / "etl_run_summary.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_path, index=False)
    LOGGER.info("Wrote %s", output_path)


def run_pipeline(
    apply_schema: bool = True,
    transform_core: bool = True,
    build_analytics: bool = True,
) -> None:
    LOGGER.info("Starting EnviroHealth ETL")
    sources = discover_sources()
    if not sources:
        raise FileNotFoundError("No source files found under data/raw")

    run_rows: list[dict[str, object]] = []
    with get_connection() as connection:
        if apply_schema:
            LOGGER.info("Applying schema SQL")
            execute_sql_files(connection, SCHEMA_FILES)
            connection.commit()

        for path, spec in sources:
            try:
                row = load_source_file(connection, path, spec)
                run_rows.append(row)
                connection.commit()
                LOGGER.info("Loaded %s rows from %s", f"{row['rows_loaded']:,}", path.name)
            except Exception:
                connection.rollback()
                raise

        if transform_core:
            LOGGER.info("Transforming raw tables into core tables")
            try:
                execute_sql_files(connection, TRANSFORMATION_FILES)
                connection.commit()
            except Exception:
                connection.rollback()
                raise

        if build_analytics:
            LOGGER.info("Building analytics views")
            try:
                execute_sql_files(connection, ANALYTICS_FILES)
                execute_sql_files(connection, ANALYSIS_FILES)
                connection.commit()
            except Exception:
                connection.rollback()
                raise

    write_run_summary(run_rows)
    LOGGER.info("Pipeline completed successfully")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the EnviroHealth ETL pipeline.")
    parser.add_argument("--skip-schema", action="store_true", help="Do not apply schema SQL first.")
    parser.add_argument("--skip-core", action="store_true", help="Do not transform raw tables to core.")
    parser.add_argument("--skip-analytics", action="store_true", help="Do not build analytics views.")
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    run_pipeline(
        apply_schema=not args.skip_schema,
        transform_core=not args.skip_core,
        build_analytics=not args.skip_analytics,
    )


if __name__ == "__main__":
    main()
