from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from envirohealth.analysis.dataset import ANALYSIS_OUTPUT_DIR, summarize_series

LOGGER = logging.getLogger(__name__)

PRIMARY_COLUMNS = [
    "pm25_mean",
    "pm25_p90",
    "pm25_monitor_count",
    "pm25_observation_count",
    "avg_observation_percent",
    "asthma_age_adjusted",
    "copd_age_adjusted",
]

FIGURE_COLUMNS = [
    "pm25_mean",
    "pm25_p90",
    "asthma_age_adjusted",
    "copd_age_adjusted",
]


def build_primary_complete_case_cohort(cohort: pd.DataFrame) -> pd.DataFrame:
    primary = cohort.loc[
        cohort["pm25_mean"].notna()
        & cohort["asthma_age_adjusted"].notna()
        & cohort["copd_age_adjusted"].notna()
    ].copy()

    expected_n = 752
    if len(primary) != expected_n:
        raise ValueError(f"Expected {expected_n} primary complete-case counties; found {len(primary)}")
    if primary["county_fips"].nunique() != expected_n:
        raise ValueError("Primary complete-case cohort is not one row per county")
    if primary[["pm25_mean", "asthma_age_adjusted", "copd_age_adjusted"]].isna().any().any():
        raise ValueError("Primary complete-case cohort contains missing primary fields")

    return primary


def build_descriptive_statistics(primary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in PRIMARY_COLUMNS:
        row = {"variable": column}
        row.update(summarize_series(primary[column]))
        rows.append(row)

    return pd.DataFrame(rows)[
        [
            "variable",
            "n",
            "missing",
            "mean",
            "sd",
            "median",
            "q1",
            "q3",
            "iqr",
            "min",
            "max",
        ]
    ]


def plot_distribution(primary: pd.DataFrame, column: str, output_dir: Path) -> None:
    clean = pd.to_numeric(primary[column], errors="coerce").dropna()

    figure, axes = plt.subplots(1, 2, figsize=(10, 4), gridspec_kw={"width_ratios": [3, 1]})
    axes[0].hist(clean, bins=30, color="#3f6f8f", edgecolor="white")
    axes[0].set_title(column)
    axes[0].set_xlabel(column)
    axes[0].set_ylabel("Counties")

    axes[1].boxplot(clean, vert=True)
    axes[1].set_title("Boxplot")
    axes[1].set_xticks([])

    figure.tight_layout()
    figure.savefig(output_dir / f"{column}_distribution.png", dpi=150)
    plt.close(figure)


def write_distribution_figures(primary: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for column in FIGURE_COLUMNS:
        plot_distribution(primary, column, output_dir)


def write_descriptive_outputs(
    cohort: pd.DataFrame,
    output_dir: Path = ANALYSIS_OUTPUT_DIR,
) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    primary = build_primary_complete_case_cohort(cohort)
    primary.to_csv(output_dir / "analysis_2022_primary_complete_case.csv", index=False)

    descriptive = build_descriptive_statistics(primary)
    descriptive.to_csv(output_dir / "descriptive_statistics.csv", index=False)
    write_distribution_figures(primary, output_dir / "figures")

    LOGGER.info("Wrote descriptive outputs to %s", output_dir)
    return descriptive

