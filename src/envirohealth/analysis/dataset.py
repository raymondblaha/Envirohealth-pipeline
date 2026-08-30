from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from envirohealth.database.connection import get_connection
from envirohealth.paths import OUTPUTS_DIR

LOGGER = logging.getLogger(__name__)
ANALYSIS_OUTPUT_DIR = OUTPUTS_DIR / "analysis"
NUMERIC_ANALYSIS_COLUMNS = [
    "pm25_mean",
    "pm25_monitor_count",
    "pm25_observation_count",
    "median_aqi",
    "p90_aqi",
    "max_aqi",
    "asthma_age_adjusted",
    "copd_age_adjusted",
    "avg_observation_percent",
    "pm25_p90",
]


def summarize_series(series: pd.Series) -> dict[str, float | int]:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)

    return {
        "n": int(clean.size),
        "missing": int(series.isna().sum()),
        "mean": clean.mean(),
        "sd": clean.std(ddof=1),
        "median": clean.median(),
        "q1": q1,
        "q3": q3,
        "iqr": q3 - q1,
        "min": clean.min(),
        "max": clean.max(),
    }


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def read_sql_frame(sql: str) -> pd.DataFrame:
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [column.name for column in cursor.description]
    return pd.DataFrame(rows, columns=columns)


def load_analysis_2022() -> pd.DataFrame:
    frame = read_sql_frame(
        """
        SELECT *
        FROM analytics.analysis_2022
        ORDER BY state_name, county_name, county_fips
        """
    )
    return coerce_analysis_numeric_columns(frame)


def coerce_analysis_numeric_columns(frame: pd.DataFrame) -> pd.DataFrame:
    coerced = frame.copy()
    for column in NUMERIC_ANALYSIS_COLUMNS:
        if column in coerced.columns:
            coerced[column] = pd.to_numeric(coerced[column], errors="coerce")
    return coerced


def load_smoking_covariate_2022() -> pd.DataFrame:
    frame = read_sql_frame(
        """
        SELECT
            county_fips,
            estimate AS smoking_age_adjusted
        FROM core.county_health
        WHERE year = 2022
          AND measure_id = 'CSMOKING'
          AND data_value_type_id = 'AgeAdjPrv'
        ORDER BY county_fips
        """
    )
    frame["smoking_age_adjusted"] = pd.to_numeric(frame["smoking_age_adjusted"], errors="coerce")
    return frame


def build_cohort_summary(cohort: pd.DataFrame) -> pd.DataFrame:
    rows = [
        ("2022 analytical counties", len(cohort)),
        ("PM2.5 unavailable", int(cohort["pm25_mean"].isna().sum())),
        ("PM2.5 available", int(cohort["pm25_mean"].notna().sum())),
        ("Asthma available", int(cohort["asthma_age_adjusted"].notna().sum())),
        ("COPD available", int(cohort["copd_age_adjusted"].notna().sum())),
        (
            "PM2.5 + asthma complete cases",
            int((cohort["pm25_mean"].notna() & cohort["asthma_age_adjusted"].notna()).sum()),
        ),
        (
            "PM2.5 + COPD complete cases",
            int((cohort["pm25_mean"].notna() & cohort["copd_age_adjusted"].notna()).sum()),
        ),
    ]
    return pd.DataFrame(rows, columns=["metric", "value"])


def build_monitoring_missingness_comparison(cohort: pd.DataFrame) -> pd.DataFrame:
    comparison = cohort.assign(pm25_available=cohort["pm25_mean"].notna())
    rows: list[dict[str, object]] = []
    for available, group in comparison.groupby("pm25_available", dropna=False):
        label = "PM2.5 available" if available else "PM2.5 unavailable"
        for outcome in ["asthma_age_adjusted", "copd_age_adjusted"]:
            stats = summarize_series(group[outcome])
            rows.append(
                {
                    "group": label,
                    "variable": outcome,
                    "counties": len(group),
                    "n": stats["n"],
                    "mean": stats["mean"],
                    "sd": stats["sd"],
                    "median": stats["median"],
                    "q1": stats["q1"],
                    "q3": stats["q3"],
                    "iqr": stats["iqr"],
                    "min": stats["min"],
                    "max": stats["max"],
                }
            )
    return pd.DataFrame(rows).sort_values("group")


def write_cohort_outputs(cohort: pd.DataFrame, output_dir: Path = ANALYSIS_OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    cohort.to_csv(output_dir / "analysis_2022_cohort.csv", index=False)
    build_cohort_summary(cohort).to_csv(output_dir / "cohort_summary.csv", index=False)
    build_monitoring_missingness_comparison(cohort).to_csv(
        output_dir / "monitoring_missingness_health_comparison.csv",
        index=False,
    )


def write_analysis_outputs() -> pd.DataFrame:
    cohort = load_analysis_2022()
    write_cohort_outputs(cohort)

    LOGGER.info("Wrote cohort outputs to %s", ANALYSIS_OUTPUT_DIR)
    return cohort


def main() -> None:
    configure_logging()
    cohort = write_analysis_outputs()

    from envirohealth.analysis.descriptive import write_descriptive_outputs
    from envirohealth.analysis.reporting import write_full_analysis_outputs

    write_descriptive_outputs(cohort)
    write_full_analysis_outputs(cohort)
