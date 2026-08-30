# Modeling Methods

Milestone 7 evaluates whether a small predictive ML benchmark improves county-level asthma or COPD prediction compared with simple interpretable baselines.

## Prediction Problem

Targets:

- `asthma_age_adjusted`
- `copd_age_adjusted`

The modeling dataset uses the frozen 2022 PM2.5 complete-case cohort. Predictors are deliberately limited to environmental exposure, monitoring coverage, and one justified contextual respiratory risk factor:

- `pm25_mean`
- `pm25_p90`
- `pm25_monitor_count`
- `pm25_observation_count`
- `avg_observation_percent`
- `smoking_age_adjusted`

Asthma and COPD outcome variables are not used as predictors for each other.

## Models

The benchmark includes:

- DummyRegressor
- LinearRegression
- Ridge
- RandomForestRegressor
- HistGradientBoostingRegressor

## Evaluation

Models are evaluated with shared 5-fold cross-validation folds. Preprocessing occurs inside scikit-learn pipelines, including median imputation and scaling where needed.

The random seed is fixed at `42` for deterministic cross-validation splits and model initialization where the estimator supports it.

Reported metrics:

- MAE
- RMSE
- R-squared

## Interpretation

Permutation importance is reported for the stronger nonlinear model for each outcome. Feature importance is interpreted predictively, not causally.

## Current Benchmark Results

The benchmark does not show a universal need for nonlinear ML.

For asthma, Random Forest produced the strongest cross-validated performance among the tested models:

```text
RandomForestRegressor CV R-squared: 0.284
Ridge CV R-squared: 0.189
DummyRegressor CV R-squared: -0.002
```

For COPD, Random Forest was only marginally better than the linear baselines:

```text
RandomForestRegressor CV R-squared: 0.818
Ridge CV R-squared: 0.812
LinearRegression CV R-squared: 0.812
DummyRegressor CV R-squared: -0.004
```

Permutation importance identified `smoking_age_adjusted` as the dominant predictor for both outcomes, especially COPD. This is predictive importance only and should not be interpreted causally.
