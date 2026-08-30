import pandas as pd

from envirohealth.analysis.associations import build_correlation_results


def test_build_correlation_results_returns_pearson_and_spearman() -> None:
    frame = pd.DataFrame(
        {
            "pm25_mean": [1.0, 2.0, 3.0, 4.0],
            "asthma_age_adjusted": [2.0, 4.0, 6.0, 8.0],
        }
    )

    results = build_correlation_results(
        frame,
        associations=[("pm25_mean", "asthma_age_adjusted", "primary")],
    )

    assert results["method"].tolist() == ["pearson", "spearman"]
    assert results["n"].tolist() == [4, 4]

