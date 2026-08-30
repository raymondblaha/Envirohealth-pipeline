from __future__ import annotations

import pandas as pd

from envirohealth.analysis.dataset import summarize_series
from envirohealth.analysis.regression import PRIMARY_MODELS, regression_result_row

COVERAGE_COLUMNS = [
    "pm25_monitor_count",
    "pm25_observation_count",
    "avg_observation_percent",
]


def build_coverage_summary(primary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in COVERAGE_COLUMNS:
        row = {"variable": column}
        row.update(summarize_series(primary[column]))
        rows.append(row)
    return pd.DataFrame(rows)


def build_high_coverage_subset(primary: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    observation_threshold = primary["pm25_observation_count"].median()
    observation_percent_threshold = primary["avg_observation_percent"].quantile(0.25)
    subset = primary.loc[
        (primary["pm25_observation_count"] >= observation_threshold)
        & (primary["avg_observation_percent"] >= observation_percent_threshold)
    ].copy()
    criterion = (
        "pm25_observation_count >= cohort median "
        f"({observation_threshold:.1f}) and avg_observation_percent >= cohort Q1 "
        f"({observation_percent_threshold:.2f})"
    )
    return subset, criterion


def build_sensitivity_results(primary: pd.DataFrame) -> pd.DataFrame:
    subset, criterion = build_high_coverage_subset(primary)
    rows = []
    for outcome, exposure, _analysis_type in PRIMARY_MODELS:
        primary_row = regression_result_row(primary, outcome, exposure, "primary_all_complete_cases")
        sensitivity_row = regression_result_row(subset, outcome, exposure, "monitoring_coverage_subset")
        primary_row["coverage_criterion"] = "all primary complete-case counties"
        sensitivity_row["coverage_criterion"] = criterion
        rows.extend([primary_row, sensitivity_row])
    return pd.DataFrame(rows)

