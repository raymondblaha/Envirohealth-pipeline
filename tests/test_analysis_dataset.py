import pandas as pd

from envirohealth.analysis.dataset import (
    build_cohort_summary,
    build_monitoring_missingness_comparison,
    coerce_analysis_numeric_columns,
    summarize_series,
)


def test_build_cohort_summary_counts_complete_cases() -> None:
    cohort = pd.DataFrame(
        {
            "pm25_mean": [1.0, None, 3.0],
            "asthma_age_adjusted": [10.0, 11.0, None],
            "copd_age_adjusted": [5.0, 6.0, 7.0],
        }
    )

    summary = build_cohort_summary(cohort).set_index("metric")["value"].to_dict()

    assert summary["2022 analytical counties"] == 3
    assert summary["PM2.5 unavailable"] == 1
    assert summary["PM2.5 available"] == 2
    assert summary["PM2.5 + asthma complete cases"] == 1
    assert summary["PM2.5 + COPD complete cases"] == 2


def test_build_monitoring_missingness_comparison_groups_by_pm25_availability() -> None:
    cohort = pd.DataFrame(
        {
            "pm25_mean": [1.0, None],
            "asthma_age_adjusted": [10.0, 12.0],
            "copd_age_adjusted": [5.0, 7.0],
        }
    )

    comparison = build_monitoring_missingness_comparison(cohort)

    assert comparison["group"].tolist() == [
        "PM2.5 available",
        "PM2.5 available",
        "PM2.5 unavailable",
        "PM2.5 unavailable",
    ]
    assert comparison["counties"].tolist() == [1, 1, 1, 1]


def test_summarize_series_reports_iqr() -> None:
    stats = summarize_series(pd.Series([1, 2, 3, None]))

    assert stats["n"] == 3
    assert stats["missing"] == 1
    assert stats["median"] == 2
    assert stats["iqr"] == 1


def test_coerce_analysis_numeric_columns_converts_object_values() -> None:
    frame = pd.DataFrame({"pm25_mean": ["1.2"], "county_fips": ["01001"]})

    coerced = coerce_analysis_numeric_columns(frame)

    assert coerced["pm25_mean"].tolist() == [1.2]
