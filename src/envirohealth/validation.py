from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

from envirohealth.database.connection import get_connection
from envirohealth.database.execute import VALIDATION_FILES
from envirohealth.paths import OUTPUTS_DIR

LOGGER = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def run_validation_query(connection: object, sql_path: Path) -> pd.DataFrame:
    with connection.cursor() as cursor:
        cursor.execute(sql_path.read_text())
        rows = cursor.fetchall()
        columns = [column.name for column in cursor.description]
    frame = pd.DataFrame(rows, columns=columns)
    frame.insert(0, "validation_file", sql_path.name)
    return frame


def write_validation_outputs(results: pd.DataFrame) -> None:
    output_dir = OUTPUTS_DIR / "validation"
    output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_dir / "database_validation_report.csv", index=False)

    failing = results[results["failed_count"] > 0]
    failing.to_csv(output_dir / "database_validation_failures.csv", index=False)
    LOGGER.info("Wrote validation reports to %s", output_dir)


def run_database_validation(fail_on_critical: bool = True) -> pd.DataFrame:
    frames = []
    with get_connection() as connection:
        for sql_path in VALIDATION_FILES:
            LOGGER.info("Running %s", sql_path.name)
            frames.append(run_validation_query(connection, sql_path))

    results = pd.concat(frames, ignore_index=True)
    write_validation_outputs(results)

    critical_failures = results[
        (results["severity"] == "critical") & (results["failed_count"].astype(int) > 0)
    ]
    if fail_on_critical and not critical_failures.empty:
        raise RuntimeError(
            "Critical database validation checks failed. "
            "See outputs/validation/database_validation_failures.csv"
        )
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run database validation SQL checks.")
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Write validation reports but do not exit with an error for critical failures.",
    )
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    run_database_validation(fail_on_critical=not args.no_fail)


if __name__ == "__main__":
    main()

