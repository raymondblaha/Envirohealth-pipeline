# Analytics Design

Milestone 5 adds SQL validation and analysis-ready views.

## Validation

Run:

```bash
python -m envirohealth.validation
```

Validation SQL files return a consistent shape:

```text
check_name
severity
failed_count
details
```

Critical checks should have `failed_count = 0`. Warning checks surface known limitations or follow-up work, such as EPA county AQI name-to-FIPS resolution.

Reports are written to:

- `outputs/validation/database_validation_report.csv`
- `outputs/validation/database_validation_failures.csv`

## Summary Exports

Run:

```bash
python -m envirohealth.analytics
```

Summary exports are written to `outputs/analytics/`.

## Analytical Views

The analytics layer currently contains:

- `analytics.county_air_quality`
- `analytics.respiratory_health`
- `analytics.county_environment_health`
- `analytics.analysis_2022`

`analytics.county_environment_health` uses one row per monitored county/year and joins EPA monitor-derived exposure features with age-adjusted CDC respiratory prevalence measures.

The core CDC table still preserves both crude and age-adjusted prevalence. The analytical respiratory view intentionally selects `AgeAdjPrv` for a cleaner comparison layer.

## 2022 Analysis Cohort

`analytics.analysis_2022` freezes the pre-statistical-analysis cohort:

- one row per monitored county with 2022 age-adjusted asthma and COPD data
- data year 2022 only
- age-adjusted CDC asthma and COPD
- EPA monitor-derived PM2.5 exposure
- county FIPS represented as five-character text

The view includes placeholder `median_aqi`, `p90_aqi`, and `max_aqi` fields as nulls because EPA county AQI files have not yet been safely mapped from county names to county FIPS.

Current cohort counts:

- 1,036 rows
- 1,036 distinct counties
- 284 counties missing PM2.5
- 752 counties with complete PM2.5 + asthma data
- 752 counties with complete PM2.5 + COPD data
