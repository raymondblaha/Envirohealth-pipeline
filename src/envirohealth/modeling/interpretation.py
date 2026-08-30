from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.model_selection import cross_val_score

from envirohealth.modeling.dataset import BASE_FEATURES, TARGETS, feature_target_frame
from envirohealth.modeling.evaluation import shared_cv
from envirohealth.modeling.models import RANDOM_STATE, build_model_pipelines

NONLINEAR_MODELS = ["RandomForestRegressor", "HistGradientBoostingRegressor"]


def select_best_nonlinear_model(frame: pd.DataFrame, outcome: str, features: list[str]) -> str:
    x, y = feature_target_frame(frame, outcome, features)
    cv = shared_cv()
    scores = {}
    for name, pipeline in build_model_pipelines(features).items():
        if name in NONLINEAR_MODELS:
            scores[name] = cross_val_score(pipeline, x, y, cv=cv, scoring="r2").mean()
    return max(scores, key=scores.get)


def build_permutation_importance(frame: pd.DataFrame, features: list[str] | None = None) -> pd.DataFrame:
    features = features or BASE_FEATURES
    rows = []
    for outcome in TARGETS:
        x, y = feature_target_frame(frame, outcome, features)
        model_name = select_best_nonlinear_model(frame, outcome, features)
        pipeline = build_model_pipelines(features)[model_name]
        pipeline.fit(x, y)
        importance = permutation_importance(
            pipeline,
            x,
            y,
            n_repeats=30,
            random_state=RANDOM_STATE,
            scoring="neg_mean_absolute_error",
        )
        for feature, mean, std in zip(
            features,
            importance.importances_mean,
            importance.importances_std,
            strict=True,
        ):
            rows.append(
                {
                    "outcome": outcome,
                    "model": model_name,
                    "feature": feature,
                    "importance_mean": mean,
                    "importance_sd": std,
                }
            )
    return pd.DataFrame(rows).sort_values(["outcome", "importance_mean"], ascending=[True, False])


def write_importance_figures(importance: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for outcome in TARGETS:
        frame = importance[importance["outcome"] == outcome].sort_values("importance_mean")
        label = "asthma" if outcome.startswith("asthma") else "copd"
        figure, axis = plt.subplots(figsize=(7, 4))
        axis.barh(frame["feature"], frame["importance_mean"], color="#506f52")
        axis.set_xlabel("Permutation importance: MAE increase")
        axis.set_title(f"{label} feature importance")
        figure.tight_layout()
        figure.savefig(output_dir / f"{label}_feature_importance.png", dpi=150)
        plt.close(figure)

