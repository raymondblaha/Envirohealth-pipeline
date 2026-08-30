from __future__ import annotations

import pandas as pd
import statsmodels.api as sm

PRIMARY_MODELS = [
    ("asthma_age_adjusted", "pm25_mean", "primary_unadjusted"),
    ("copd_age_adjusted", "pm25_mean", "primary_unadjusted"),
]

SECONDARY_MODELS = [
    ("asthma_age_adjusted", "pm25_p90", "secondary_unadjusted"),
    ("copd_age_adjusted", "pm25_p90", "secondary_unadjusted"),
]


def fit_ols(frame: pd.DataFrame, outcome: str, exposures: list[str]):
    model_frame = frame[[outcome, *exposures]].dropna()
    x = sm.add_constant(model_frame[exposures], has_constant="add")
    y = model_frame[outcome]
    fit = sm.OLS(y, x).fit()
    robust = fit.get_robustcov_results(cov_type="HC3")
    return model_frame, fit, robust


def regression_result_row(
    frame: pd.DataFrame,
    outcome: str,
    exposure: str,
    analysis_type: str,
    covariates: list[str] | None = None,
) -> dict[str, object]:
    covariates = covariates or []
    model_frame, fit, robust = fit_ols(frame, outcome, [exposure, *covariates])
    param_names = list(robust.model.exog_names)
    exposure_index = param_names.index(exposure)
    const_index = param_names.index("const")
    ci = robust.conf_int()

    return {
        "analysis_type": analysis_type,
        "outcome": outcome,
        "exposure": exposure,
        "covariates": " | ".join(covariates),
        "n": len(model_frame),
        "intercept": robust.params[const_index],
        "beta": robust.params[exposure_index],
        "standard_error": robust.bse[exposure_index],
        "ci_lower": ci[exposure_index][0],
        "ci_upper": ci[exposure_index][1],
        "p_value": robust.pvalues[exposure_index],
        "r_squared": fit.rsquared,
        "adjusted_r_squared": fit.rsquared_adj,
    }


def build_regression_results(
    frame: pd.DataFrame,
    models: list[tuple[str, str, str]] | None = None,
) -> pd.DataFrame:
    models = models or PRIMARY_MODELS
    return pd.DataFrame(
        [
            regression_result_row(frame, outcome, exposure, analysis_type)
            for outcome, exposure, analysis_type in models
        ]
    )


def build_adjusted_regression_results(frame: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            regression_result_row(
                frame,
                outcome="asthma_age_adjusted",
                exposure="pm25_mean",
                analysis_type="adjusted_smoking",
                covariates=["smoking_age_adjusted"],
            ),
            regression_result_row(
                frame,
                outcome="copd_age_adjusted",
                exposure="pm25_mean",
                analysis_type="adjusted_smoking",
                covariates=["smoking_age_adjusted"],
            ),
        ]
    )

