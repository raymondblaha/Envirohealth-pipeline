import pandas as pd

from envirohealth.analysis.regression import build_regression_results


def test_build_regression_results_reports_expected_columns() -> None:
    frame = pd.DataFrame(
        {
            "pm25_mean": [1.0, 2.0, 3.0, 4.0],
            "asthma_age_adjusted": [2.0, 4.0, 6.0, 8.0],
            "copd_age_adjusted": [3.0, 5.0, 7.0, 9.0],
        }
    )

    results = build_regression_results(frame)

    assert len(results) == 2
    assert {"outcome", "exposure", "n", "beta", "standard_error", "p_value"}.issubset(
        results.columns
    )
    assert results["n"].tolist() == [4, 4]

