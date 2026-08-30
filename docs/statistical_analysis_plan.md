# Statistical Analysis Plan

## Research Question

Among U.S. counties with available EPA PM2.5 monitoring data in 2022, is annual mean PM2.5 associated with age-adjusted adult asthma and COPD prevalence?

## Design

Cross-sectional ecological county-level analysis.

This analysis evaluates county-level associations. It does not estimate individual-level risk and does not make causal claims.

## Analysis Year

2022.

## Primary Exposure

Annual county-level mean PM2.5 from the EPA monitor-derived analytics layer:

```text
pm25_mean
```

## Primary Outcomes

Age-adjusted CDC PLACES adult respiratory health prevalence measures:

```text
asthma_age_adjusted
copd_age_adjusted
```

Age-adjusted prevalence is used for the primary analysis because county age distributions differ and crude prevalence may reflect age structure rather than the exposure-outcome relationship of interest.

## Primary Population

Real U.S. county geographies in `analytics.analysis_2022` with nonmissing PM2.5 and respiratory outcome data.

Expected complete-case sample size:

```text
752 counties
```

The broader frozen 2022 analytical cohort includes 1,036 counties with respiratory outcomes. Counties missing PM2.5 are retained in the cohort view so monitoring availability can be assessed transparently.

## Primary Complete-Case Definitions

PM2.5 + asthma:

```text
pm25_mean IS NOT NULL
AND asthma_age_adjusted IS NOT NULL
```

PM2.5 + COPD:

```text
pm25_mean IS NOT NULL
AND copd_age_adjusted IS NOT NULL
```

## Significance Threshold

```text
alpha = 0.05
```

## Planned Sequence

1. Cohort and missingness report
2. Descriptive statistics
3. Bivariate Pearson and Spearman associations
4. Unadjusted linear regression models with HC3 robust standard errors
5. Regression diagnostics
6. Monitoring-coverage sensitivity analysis
7. Carefully justified adjusted models, if appropriate

## Primary Regression Models

Asthma:

```text
asthma_age_adjusted ~ pm25_mean
```

COPD:

```text
copd_age_adjusted ~ pm25_mean
```

Regression coefficients will be interpreted as percentage-point differences in age-adjusted prevalence per 1 microgram per cubic meter higher annual mean PM2.5.

## Limitations to Preserve

- Ecological county-level analysis cannot support individual-level causal conclusions.
- EPA PM2.5 monitoring is not available for every county.
- Counties without PM2.5 may differ systematically from monitored counties.
- EPA county AQI summary fields are not included in the primary cohort until county-name-to-FIPS mapping is validated.

