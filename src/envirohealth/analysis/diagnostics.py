from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import OLSInfluence, variance_inflation_factor

from envirohealth.analysis.regression import PRIMARY_MODELS, fit_ols


def model_label(outcome: str) -> str:
    return "asthma" if outcome.startswith("asthma") else "copd"


def build_model_diagnostics(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome, exposure, analysis_type in PRIMARY_MODELS:
        model_frame, fit, _robust = fit_ols(frame, outcome, [exposure])
        influence = OLSInfluence(fit)
        cooks = influence.cooks_distance[0]
        leverage = influence.hat_matrix_diag
        bp_lm, bp_lm_p, bp_f, bp_f_p = het_breuschpagan(fit.resid, fit.model.exog)
        cooks_threshold = 4 / len(model_frame)
        leverage_threshold = 2 * fit.df_model / len(model_frame)

        rows.append(
            {
                "analysis_type": analysis_type,
                "outcome": outcome,
                "exposure": exposure,
                "n": len(model_frame),
                "residual_mean": fit.resid.mean(),
                "residual_sd": fit.resid.std(ddof=1),
                "breusch_pagan_lm": bp_lm,
                "breusch_pagan_lm_p_value": bp_lm_p,
                "breusch_pagan_f": bp_f,
                "breusch_pagan_f_p_value": bp_f_p,
                "max_cooks_distance": cooks.max(),
                "cooks_distance_threshold_4_over_n": cooks_threshold,
                "influential_count_cooks_gt_4_over_n": int((cooks > cooks_threshold).sum()),
                "max_leverage": leverage.max(),
                "leverage_threshold_2p_over_n": leverage_threshold,
                "high_leverage_count": int((leverage > leverage_threshold).sum()),
            }
        )
    return pd.DataFrame(rows)


def build_influential_observations(frame: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    rows = []
    for outcome, exposure, analysis_type in PRIMARY_MODELS:
        model_frame, fit, _robust = fit_ols(frame, outcome, [exposure])
        metadata = frame.loc[
            model_frame.index,
            ["county_fips", "state_name", "county_name", exposure, outcome],
        ]
        influence = OLSInfluence(fit)
        ranked = metadata.assign(
            cooks_distance=influence.cooks_distance[0],
            leverage=influence.hat_matrix_diag,
            residual=fit.resid,
            fitted=fit.fittedvalues,
        ).sort_values("cooks_distance", ascending=False)
        for _, row in ranked.head(top_n).iterrows():
            rows.append(
                {
                    "analysis_type": analysis_type,
                    "outcome": outcome,
                    "county_fips": row["county_fips"],
                    "state_name": row.get("state_name"),
                    "county_name": row.get("county_name"),
                    "pm25_mean": row["pm25_mean"],
                    outcome: row[outcome],
                    "fitted": row["fitted"],
                    "residual": row["residual"],
                    "leverage": row["leverage"],
                    "cooks_distance": row["cooks_distance"],
                }
            )
    return pd.DataFrame(rows)


def write_diagnostic_plots(frame: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for outcome, exposure, _analysis_type in PRIMARY_MODELS:
        _model_frame, fit, _robust = fit_ols(frame, outcome, [exposure])
        label = model_label(outcome)

        figure, axis = plt.subplots(figsize=(6, 4))
        axis.scatter(fit.fittedvalues, fit.resid, alpha=0.65)
        axis.axhline(0, color="black", linewidth=1)
        axis.set_xlabel("Fitted values")
        axis.set_ylabel("Residuals")
        axis.set_title(f"{label}: residuals vs fitted")
        figure.tight_layout()
        figure.savefig(output_dir / f"{label}_residuals_vs_fitted.png", dpi=150)
        plt.close(figure)

        figure = sm.qqplot(fit.resid, line="45", fit=True)
        figure.suptitle(f"{label}: residual Q-Q plot")
        figure.tight_layout()
        figure.savefig(output_dir / f"{label}_qq.png", dpi=150)
        plt.close(figure)


def build_vif_table(frame: pd.DataFrame, predictors: list[str]) -> pd.DataFrame:
    model_frame = frame[predictors].dropna()
    x = sm.add_constant(model_frame, has_constant="add")
    return pd.DataFrame(
        [
            {"variable": column, "vif": variance_inflation_factor(x.to_numpy(), index)}
            for index, column in enumerate(x.columns)
            if column != "const"
        ]
    )
