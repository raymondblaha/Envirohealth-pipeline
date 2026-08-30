import pandas as pd
import pytest

from envirohealth.analysis.descriptive import (
    PRIMARY_COLUMNS,
    build_descriptive_statistics,
    build_primary_complete_case_cohort,
)


def primary_row(index: int) -> dict[str, float | int | str]:
    return {
        "county_fips": f"{index:05d}",
        "pm25_mean": 1.0,
        "pm25_p90": 2.0,
        "pm25_monitor_count": 1,
        "pm25_observation_count": 10,
        "avg_observation_percent": 95.0,
        "asthma_age_adjusted": 10.0,
        "copd_age_adjusted": 6.0,
    }


def test_build_primary_complete_case_cohort_enforces_frozen_n() -> None:
    cohort = pd.DataFrame([primary_row(index) for index in range(752)])

    primary = build_primary_complete_case_cohort(cohort)

    assert len(primary) == 752
    assert primary["county_fips"].nunique() == 752


def test_build_primary_complete_case_cohort_fails_for_unexpected_n() -> None:
    cohort = pd.DataFrame([primary_row(index) for index in range(751)])

    with pytest.raises(ValueError, match="Expected 752"):
        build_primary_complete_case_cohort(cohort)


def test_build_descriptive_statistics_uses_primary_columns() -> None:
    primary = pd.DataFrame([primary_row(index) for index in range(752)])

    descriptive = build_descriptive_statistics(primary)

    assert descriptive["variable"].tolist() == PRIMARY_COLUMNS
    assert descriptive["n"].tolist() == [752] * len(PRIMARY_COLUMNS)
    assert descriptive["missing"].tolist() == [0] * len(PRIMARY_COLUMNS)
