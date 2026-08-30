from __future__ import annotations

import argparse
import logging

import pandas as pd

from envirohealth.database.connection import get_connection
from envirohealth.database.execute import (
    ANALYSIS_FILES,
    ANALYTICS_EXPORT_QUERIES,
    ANALYTICS_FILES,
    execute_sql_files,
)
from envirohealth.paths import OUTPUTS_DIR

LOGGER = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def query_frame(connection: object, sql: str) -> pd.DataFrame:
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [column.name for column in cursor.description]
    return pd.DataFrame(rows, columns=columns)


def export_analytics_summaries(rebuild_views: bool = False) -> None:
    output_dir = OUTPUTS_DIR / "analytics"
    output_dir.mkdir(parents=True, exist_ok=True)

    with get_connection() as connection:
        if rebuild_views:
            LOGGER.info("Rebuilding analytics views")
            execute_sql_files(connection, ANALYTICS_FILES)
            execute_sql_files(connection, ANALYSIS_FILES)
            connection.commit()

        for name, sql in ANALYTICS_EXPORT_QUERIES.items():
            output_path = output_dir / f"{name}.csv"
            query_frame(connection, sql).to_csv(output_path, index=False)
            LOGGER.info("Wrote %s", output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export analytics-layer summary CSVs.")
    parser.add_argument("--rebuild-views", action="store_true", help="Rebuild analytics views first.")
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    export_analytics_summaries(rebuild_views=args.rebuild_views)


if __name__ == "__main__":
    main()
