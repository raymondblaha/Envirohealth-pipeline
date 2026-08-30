# Statistical Methods

This project uses a cross-sectional ecological county-level design for data year 2022.

The frozen analytical cohort contains 1,036 counties with age-adjusted CDC PLACES asthma and COPD outcomes. The primary PM2.5 complete-case cohort contains 752 counties. The remaining 284 counties are retained in `analytics.analysis_2022` and reported as missing PM2.5 rather than imputed.

## Exposure and Outcomes

Primary exposure:

- annual county-level mean PM2.5, `pm25_mean`

Primary outcomes:

- age-adjusted adult current asthma prevalence, `asthma_age_adjusted`
- age-adjusted adult COPD prevalence, `copd_age_adjusted`

Age-adjusted prevalence is used because county age structures differ.

## Descriptive Analysis

The primary descriptive table uses the same 752 counties used in the primary PM2.5 models. Reported statistics include N, missingness, mean, standard deviation, median, quartiles, IQR, minimum, and maximum.

## Associations

Primary bivariate associations are evaluated with Pearson and Spearman correlations:

- `pm25_mean` and asthma
- `pm25_mean` and COPD

Secondary analyses repeat these checks using `pm25_p90`.

## Regression

The primary models are unadjusted ordinary least squares regressions:

- `asthma_age_adjusted ~ pm25_mean`
- `copd_age_adjusted ~ pm25_mean`

HC3 heteroskedasticity-robust standard errors are used for primary inference. Coefficients are interpreted as percentage-point differences in age-adjusted prevalence associated with a 1 microgram per cubic meter higher annual mean PM2.5 concentration.

## Diagnostics

Diagnostics include residual summaries, residuals-versus-fitted plots, Q-Q plots, Breusch-Pagan tests, Cook's distance, and leverage. Influential counties are identified but not automatically removed.

## Monitoring-Coverage Sensitivity

Monitoring coverage is characterized using:

- `pm25_monitor_count`
- `pm25_observation_count`
- `avg_observation_percent`

The coverage sensitivity subset is data-derived: counties must have PM2.5 observation count at or above the primary cohort median and average observation percent at or above the primary cohort first quartile. This checks whether the PM2.5 coefficient materially changes in better-monitored counties.

## Adjusted Models

Smoking prevalence is included as the first justified covariate because it is a known respiratory risk factor and is especially relevant for COPD. The adjusted models are:

- `asthma_age_adjusted ~ pm25_mean + smoking_age_adjusted`
- `copd_age_adjusted ~ pm25_mean + smoking_age_adjusted`

Covariates are not selected by p-value or automated search. VIF is reported for adjusted predictors.

## Interpretation Limits

This analysis estimates county-level associations only. It does not support individual-level inference or causal claims.

