from __future__ import annotations

import pandas as pd
from scipy import stats

PRIMARY_ASSOCIATIONS = [
    ("pm25_mean", "asthma_age_adjusted", "primary"),
    ("pm25_mean", "copd_age_adjusted", "primary"),
]

SECONDARY_ASSOCIATIONS = [
    ("pm25_p90", "asthma_age_adjusted", "secondary"),
    ("pm25_p90", "copd_age_adjusted", "secondary"),
]


def build_correlation_results(
    frame: pd.DataFrame,
    associations: list[tuple[str, str, str]] | None = None,
) -> pd.DataFrame:
    associations = associations or [*PRIMARY_ASSOCIATIONS, *SECONDARY_ASSOCIATIONS]
    rows = []
    for exposure, outcome, analysis_type in associations:
        complete = frame[[exposure, outcome]].dropna()
        for method in ["pearson", "spearman"]:
            if method == "pearson":
                result = stats.pearsonr(complete[exposure], complete[outcome])
            else:
                result = stats.spearmanr(complete[exposure], complete[outcome])

            rows.append(
                {
                    "analysis_type": analysis_type,
                    "exposure": exposure,
                    "outcome": outcome,
                    "method": method,
                    "n": len(complete),
                    "correlation": result.statistic,
                    "p_value": result.pvalue,
                }
            )
    return pd.DataFrame(rows)

