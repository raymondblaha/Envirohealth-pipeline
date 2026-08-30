from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def numeric_preprocessor(features: list[str], scale: bool) -> ColumnTransformer:
    steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale:
        steps.append(("scaler", StandardScaler()))

    return ColumnTransformer(
        transformers=[("numeric", Pipeline(steps), features)],
        remainder="drop",
        verbose_feature_names_out=False,
    )

