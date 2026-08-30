from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, cross_validate

from envirohealth.modeling.dataset import BASE_FEATURES, TARGETS, feature_target_frame
from envirohealth.modeling.models import RANDOM_STATE, build_model_pipelines


def shared_cv(n_splits: int = 5) -> KFold:
    return KFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)


def evaluate_models(frame: pd.DataFrame, features: list[str] | None = None) -> pd.DataFrame:
    features = features or BASE_FEATURES
    cv = shared_cv()
    rows = []
    for outcome in TARGETS:
        x, y = feature_target_frame(frame, outcome, features)
        for model_name, pipeline in build_model_pipelines(features).items():
            scores = cross_validate(
                pipeline,
                x,
                y,
                cv=cv,
                scoring={
                    "mae": "neg_mean_absolute_error",
                    "rmse": "neg_root_mean_squared_error",
                    "r2": "r2",
                },
                n_jobs=None,
            )
            rows.append(
                {
                    "outcome": outcome,
                    "model": model_name,
                    "n": len(y),
                    "cv_mae": -np.mean(scores["test_mae"]),
                    "cv_mae_sd": np.std(-scores["test_mae"], ddof=1),
                    "cv_rmse": -np.mean(scores["test_rmse"]),
                    "cv_rmse_sd": np.std(-scores["test_rmse"], ddof=1),
                    "cv_r2": np.mean(scores["test_r2"]),
                    "cv_r2_sd": np.std(scores["test_r2"], ddof=1),
                }
            )
    return pd.DataFrame(rows)

