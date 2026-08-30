from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from envirohealth.modeling.dataset import BASE_FEATURES, load_modeling_dataset
from envirohealth.modeling.evaluation import evaluate_models
from envirohealth.modeling.interpretation import (
    build_permutation_importance,
    write_importance_figures,
)
from envirohealth.paths import OUTPUTS_DIR

LOGGER = logging.getLogger(__name__)
MODELING_OUTPUT_DIR = OUTPUTS_DIR / "modeling"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def write_performance_figure(performance: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    labels = performance["outcome"].str.replace("_age_adjusted", "", regex=False)
    labels = labels + "\n" + performance["model"]

    figure, axis = plt.subplots(figsize=(10, 5))
    axis.bar(labels, performance["cv_r2"], color="#3f6f8f")
    axis.axhline(0, color="black", linewidth=1)
    axis.set_ylabel("Cross-validated R-squared")
    axis.set_title("Model performance by outcome")
    axis.tick_params(axis="x", rotation=45)
    figure.tight_layout()
    figure.savefig(output_dir / "model_performance.png", dpi=150)
    plt.close(figure)


def write_modeling_outputs() -> None:
    output_dir = MODELING_OUTPUT_DIR
    figure_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = load_modeling_dataset()
    dataset.to_csv(output_dir / "modeling_dataset.csv", index=False)

    performance = evaluate_models(dataset, BASE_FEATURES)
    performance.to_csv(output_dir / "model_performance.csv", index=False)
    write_performance_figure(performance, figure_dir)

    importance = build_permutation_importance(dataset, BASE_FEATURES)
    importance.to_csv(output_dir / "permutation_importance.csv", index=False)
    write_importance_figures(importance, figure_dir)

    LOGGER.info("Wrote modeling outputs to %s", output_dir)


def main() -> None:
    configure_logging()
    write_modeling_outputs()

