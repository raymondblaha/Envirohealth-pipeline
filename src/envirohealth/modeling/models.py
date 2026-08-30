from __future__ import annotations

from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import Pipeline

from envirohealth.modeling.preprocessing import numeric_preprocessor

RANDOM_STATE = 42


def build_model_pipelines(features: list[str]) -> dict[str, Pipeline]:
    return {
        "DummyRegressor": Pipeline(
            [
                ("preprocess", numeric_preprocessor(features, scale=False)),
                ("model", DummyRegressor(strategy="mean")),
            ]
        ),
        "LinearRegression": Pipeline(
            [
                ("preprocess", numeric_preprocessor(features, scale=True)),
                ("model", LinearRegression()),
            ]
        ),
        "Ridge": Pipeline(
            [
                ("preprocess", numeric_preprocessor(features, scale=True)),
                ("model", Ridge(alpha=1.0)),
            ]
        ),
        "RandomForestRegressor": Pipeline(
            [
                ("preprocess", numeric_preprocessor(features, scale=False)),
                (
                    "model",
                    RandomForestRegressor(
                        n_estimators=300,
                        min_samples_leaf=5,
                        random_state=RANDOM_STATE,
                        n_jobs=1,
                    ),
                ),
            ]
        ),
        "HistGradientBoostingRegressor": Pipeline(
            [
                ("preprocess", numeric_preprocessor(features, scale=False)),
                (
                    "model",
                    HistGradientBoostingRegressor(
                        max_iter=200,
                        learning_rate=0.05,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
    }
