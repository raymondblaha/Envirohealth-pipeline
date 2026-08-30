import pandas as pd

from envirohealth.analysis.sensitivity import build_high_coverage_subset


def test_build_high_coverage_subset_uses_data_derived_thresholds() -> None:
    frame = pd.DataFrame(
        {
            "pm25_observation_count": [10, 20, 30, 40],
            "avg_observation_percent": [80, 85, 90, 95],
        }
    )

    subset, criterion = build_high_coverage_subset(frame)

    assert len(subset) == 2
    assert "cohort median" in criterion
    assert "cohort Q1" in criterion

