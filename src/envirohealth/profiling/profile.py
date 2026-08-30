from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from envirohealth.paths import OUTPUTS_DIR, RAW_DATA_DIR

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class DatasetProfile:
    dataset: str
    path: Path
    rows: int
    columns: int
    duplicate_rows: int
    memory_mb: float


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def find_csv_files(raw_data_dir: Path = RAW_DATA_DIR) -> list[Path]:
    return sorted(raw_data_dir.glob("**/*.csv"))


def dataset_name(path: Path) -> str:
    return path.relative_to(RAW_DATA_DIR).with_suffix("").as_posix().replace("/", "__")


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def looks_like_identifier(column_name: str) -> bool:
    normalized = column_name.lower().replace("_", " ")
    return any(token in normalized for token in ["id", "code", "fips", "location"])


def date_range_for_series(series: pd.Series) -> tuple[str | None, str | None]:
    if pd.api.types.is_numeric_dtype(series) and "year" in series.name.lower():
        values = pd.to_numeric(series, errors="coerce").dropna()
        if values.empty:
            return None, None
        return str(int(values.min())), str(int(values.max()))

    if not any(token in series.name.lower() for token in ["date", "year"]):
        return None, None

    values = pd.to_datetime(series, errors="coerce").dropna()
    if values.empty:
        return None, None
    return values.min().isoformat(), values.max().isoformat()


def inventory_row(path: Path, frame: pd.DataFrame) -> DatasetProfile:
    return DatasetProfile(
        dataset=dataset_name(path),
        path=path,
        rows=len(frame),
        columns=len(frame.columns),
        duplicate_rows=int(frame.duplicated().sum()),
        memory_mb=round(frame.memory_usage(deep=True).sum() / 1024**2, 3),
    )


def build_schema_rows(dataset: str, frame: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    total_rows = len(frame)

    for column in frame.columns:
        series = frame[column]
        missing_count = int(series.isna().sum())
        min_date, max_date = date_range_for_series(series)
        rows.append(
            {
                "dataset": dataset,
                "column_name": column,
                "dtype": str(series.dtype),
                "missing_count": missing_count,
                "missing_percent": round((missing_count / total_rows) * 100, 3)
                if total_rows
                else 0,
                "unique_values": int(series.nunique(dropna=True)),
                "is_potential_identifier": looks_like_identifier(column),
                "min_date_or_year": min_date,
                "max_date_or_year": max_date,
            }
        )
    return rows


def build_numeric_rows(dataset: str, frame: pd.DataFrame) -> list[dict[str, object]]:
    numeric = frame.select_dtypes(include="number")
    if numeric.empty:
        return []

    stats = numeric.describe(percentiles=[0.25, 0.5, 0.75]).transpose()
    rows = []
    for column_name, values in stats.iterrows():
        rows.append(
            {
                "dataset": dataset,
                "column_name": column_name,
                "count": values["count"],
                "mean": values["mean"],
                "std": values["std"],
                "min": values["min"],
                "p25": values["25%"],
                "median": values["50%"],
                "p75": values["75%"],
                "max": values["max"],
            }
        )
    return rows


def build_categorical_rows(
    dataset: str,
    frame: pd.DataFrame,
    max_values_per_column: int = 5,
) -> list[dict[str, object]]:
    categorical = frame.select_dtypes(exclude="number")
    rows: list[dict[str, object]] = []

    for column_name in categorical.columns:
        series = categorical[column_name]
        value_counts = series.value_counts(dropna=True).head(max_values_per_column)
        for value, frequency in value_counts.items():
            rows.append(
                {
                    "dataset": dataset,
                    "column_name": column_name,
                    "unique_values": int(series.nunique(dropna=True)),
                    "value": value,
                    "frequency": int(frequency),
                    "missing_count": int(series.isna().sum()),
                }
            )
    return rows


def write_report(rows: list[dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_path, index=False)
    LOGGER.info("Wrote %s", output_path)


def profile_all(raw_data_dir: Path = RAW_DATA_DIR, output_dir: Path = OUTPUTS_DIR / "profiling") -> None:
    csv_files = find_csv_files(raw_data_dir)
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found under {raw_data_dir}")

    inventory: list[DatasetProfile] = []
    schema_rows: list[dict[str, object]] = []
    numeric_rows: list[dict[str, object]] = []
    categorical_rows: list[dict[str, object]] = []
    missingness_rows: list[dict[str, object]] = []
    duplicate_rows: list[dict[str, object]] = []

    for path in csv_files:
        LOGGER.info("Profiling %s", path)
        frame = read_csv(path)
        name = dataset_name(path)
        profile = inventory_row(path, frame)
        inventory.append(profile)
        schema_rows.extend(build_schema_rows(name, frame))
        numeric_rows.extend(build_numeric_rows(name, frame))
        categorical_rows.extend(build_categorical_rows(name, frame))

        for column in frame.columns:
            missing = int(frame[column].isna().sum())
            missingness_rows.append(
                {
                    "dataset": name,
                    "column_name": column,
                    "missing_count": missing,
                    "missing_percent": round((missing / len(frame)) * 100, 3)
                    if len(frame)
                    else 0,
                }
            )

        duplicate_rows.append(
            {
                "dataset": name,
                "duplicate_rows": profile.duplicate_rows,
                "duplicate_percent": round((profile.duplicate_rows / profile.rows) * 100, 3)
                if profile.rows
                else 0,
            }
        )

    inventory_rows = [
        {
            "dataset": item.dataset,
            "path": item.path.as_posix(),
            "rows": item.rows,
            "columns": item.columns,
            "duplicate_rows": item.duplicate_rows,
            "memory_mb": item.memory_mb,
        }
        for item in inventory
    ]

    write_report(inventory_rows, output_dir / "dataset_inventory.csv")
    write_report(schema_rows, output_dir / "schema_report.csv")
    write_report(missingness_rows, output_dir / "missingness_report.csv")
    write_report(duplicate_rows, output_dir / "duplicate_report.csv")
    write_report(numeric_rows, output_dir / "numeric_summary.csv")
    write_report(categorical_rows, output_dir / "categorical_summary.csv")


def main() -> None:
    configure_logging()
    profile_all()

