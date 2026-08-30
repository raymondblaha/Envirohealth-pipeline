from __future__ import annotations

import pandas as pd

from envirohealth.analysis.dataset import load_analysis_2022, load_smoking_covariate_2022
from envirohealth.analysis.descriptive import build_primary_complete_case_cohort

TARGETS = ["asthma_age_adjusted", "copd_age_adjusted"]
BASE_FEATURES = [
    "pm25_mean",
    "pm25_p90",
    "pm25_monitor_count",
    "pm25_observation_count",
    "avg_observation_percent",
    "smoking_age_adjusted",
]


def load_modeling_dataset() -> pd.DataFrame:
    cohort = build_primary_complete_case_cohort(load_analysis_2022())
    smoking = load_smoking_covariate_2022()
    modeled = cohort.merge(smoking, on="county_fips", how="left", validate="one_to_one")
    return coerce_modeling_numeric_columns(modeled)


def coerce_modeling_numeric_columns(frame: pd.DataFrame) -> pd.DataFrame:
    coerced = frame.copy()
    for column in [*BASE_FEATURES, *TARGETS]:
        if column in coerced.columns:
            coerced[column] = pd.to_numeric(coerced[column], errors="coerce")
    return coerced


def feature_target_frame(
    frame: pd.DataFrame,
    outcome: str,
    features: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.Series]:
    features = features or BASE_FEATURES
    if outcome not in TARGETS:
        raise ValueError(f"Unsupported modeling target: {outcome}")

    forbidden = set(TARGETS) - {outcome}
    leakage = sorted(forbidden.intersection(features))
    if leakage:
        raise ValueError(f"Potential target leakage in feature list: {leakage}")

    model_frame = frame[[*features, outcome]].dropna(subset=[outcome]).copy()
    return model_frame[features], model_frame[outcome]

