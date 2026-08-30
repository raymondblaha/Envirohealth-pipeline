import pandas as pd
import pytest

from envirohealth.modeling.dataset import BASE_FEATURES, feature_target_frame
from envirohealth.modeling.evaluation import evaluate_models
from envirohealth.modeling.models import build_model_pipelines


def modeling_frame() -> pd.DataFrame:
    rows = []
    for index in range(20):
        rows.append(
            {
                "pm25_mean": index + 1,
                "pm25_p90": index + 2,
                "pm25_monitor_count": (index % 3) + 1,
                "pm25_observation_count": (index + 1) * 10,
                "avg_observation_percent": 80 + index,
                "smoking_age_adjusted": 10 + index,
                "asthma_age_adjusted": 9 + index,
                "copd_age_adjusted": 5 + index,
            }
        )
    return pd.DataFrame(rows)


def test_feature_target_frame_blocks_obvious_target_leakage() -> None:
    with pytest.raises(ValueError, match="target leakage"):
        feature_target_frame(
            modeling_frame(),
            "asthma_age_adjusted",
            features=["pm25_mean", "copd_age_adjusted"],
        )


def test_model_pipelines_include_expected_benchmarks() -> None:
    pipelines = build_model_pipelines(BASE_FEATURES)

    assert list(pipelines) == [
        "DummyRegressor",
        "LinearRegression",
        "Ridge",
        "RandomForestRegressor",
        "HistGradientBoostingRegressor",
    ]


def test_evaluate_models_returns_metrics_for_each_outcome_and_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LOKY_MAX_CPU_COUNT", "1")

    results = evaluate_models(modeling_frame(), BASE_FEATURES)

    assert len(results) == 10
    assert {"cv_mae", "cv_rmse", "cv_r2"}.issubset(results.columns)
