from __future__ import annotations

import logging

import pandas as pd

from envirohealth.analysis.associations import (
    SECONDARY_ASSOCIATIONS,
    build_correlation_results,
)
from envirohealth.analysis.dataset import (
    ANALYSIS_OUTPUT_DIR,
    load_smoking_covariate_2022,
)
from envirohealth.analysis.descriptive import build_primary_complete_case_cohort
from envirohealth.analysis.diagnostics import (
    build_influential_observations,
    build_model_diagnostics,
    build_vif_table,
    write_diagnostic_plots,
)
from envirohealth.analysis.regression import (
    SECONDARY_MODELS,
    build_adjusted_regression_results,
    build_regression_results,
)
from envirohealth.analysis.sensitivity import (
    build_coverage_summary,
    build_sensitivity_results,
)

LOGGER = logging.getLogger(__name__)


def add_smoking_covariate(primary: pd.DataFrame) -> pd.DataFrame:
    smoking = load_smoking_covariate_2022()
    return primary.merge(smoking, on="county_fips", how="left", validate="one_to_one")


def build_secondary_analysis_results(primary: pd.DataFrame) -> pd.DataFrame:
    correlations = build_correlation_results(primary, SECONDARY_ASSOCIATIONS)
    regressions = build_regression_results(primary, SECONDARY_MODELS)
    return pd.concat(
        [
            correlations.assign(result_type="correlation"),
            regressions.assign(result_type="regression"),
        ],
        ignore_index=True,
        sort=False,
    )


def write_full_analysis_outputs(cohort: pd.DataFrame) -> None:
    output_dir = ANALYSIS_OUTPUT_DIR
    figure_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    primary = build_primary_complete_case_cohort(cohort)
    adjusted = add_smoking_covariate(primary)

    build_correlation_results(primary).to_csv(output_dir / "correlation_results.csv", index=False)
    build_regression_results(primary).to_csv(output_dir / "regression_results.csv", index=False)
    build_model_diagnostics(primary).to_csv(output_dir / "model_diagnostics.csv", index=False)
    build_influential_observations(primary).to_csv(
        output_dir / "influential_observations.csv",
        index=False,
    )
    build_coverage_summary(primary).to_csv(output_dir / "monitoring_coverage_summary.csv", index=False)
    build_sensitivity_results(primary).to_csv(output_dir / "sensitivity_results.csv", index=False)
    build_adjusted_regression_results(adjusted).to_csv(
        output_dir / "adjusted_regression_results.csv",
        index=False,
    )
    build_vif_table(adjusted, ["pm25_mean", "smoking_age_adjusted"]).to_csv(
        output_dir / "adjusted_model_vif.csv",
        index=False,
    )
    build_secondary_analysis_results(primary).to_csv(
        output_dir / "secondary_analysis_results.csv",
        index=False,
    )
    write_diagnostic_plots(primary, figure_dir)

    LOGGER.info("Wrote full statistical analysis outputs to %s", output_dir)

