# Project Roadmap

## Milestone 1: Repository and Raw Data Architecture

Status: started

Deliverables:

- Professional project structure
- Local-only raw data folder
- README and data source documentation
- Python project configuration

## Milestone 2: Data Profiling

Status: started

Deliverables:

- Reusable Python profiling command
- Dataset inventory
- Schema report
- Missingness report
- Duplicate report
- Numeric and categorical summaries

Run:

```bash
python -m envirohealth.profiling
```

## Milestone 3: PostgreSQL Design

Status: started

Likely entities:

- `geography.states`
- `geography.counties`
- `air_quality.county_aqi`
- `air_quality.cbsa_aqi`
- `air_quality.monitors`
- `air_quality.monitor_concentrations`
- `health.places_county_measures`

Key design question:

- Use CDC `LocationID` and EPA `State Code` + `County Code` to construct a consistent five-digit county FIPS key.

Current deliverables:

- `docs/database_design.md`
- `sql/schema/001_create_schemas.sql`
- `sql/schema/002_create_raw_tables.sql`
- `sql/schema/003_create_core_tables.sql`
- `sql/schema/004_add_indexes.sql`
- `outputs/validation/candidate_key_report.csv`
- `outputs/validation/monitor_site_attribute_report.csv`

## Milestone 4: ETL

Status: started

Build extract, transform, validation, and database-loading modules under `src/envirohealth/`.

Current deliverables:

- `.env.example`
- `docker-compose.yml`
- `docs/etl_design.md`
- `src/envirohealth/database/`
- `src/envirohealth/ingestion/`
- `src/envirohealth/pipeline.py`
- `sql/transformations/001_raw_to_core.sql`

## Milestone 5: SQL Validation and Analytical Layer

Status: started

Initial validation targets:

- County FIPS format
- AQI non-negative values
- Latitude and longitude bounds
- CDC prevalence between 0 and 100
- Confidence interval order
- Primary-key uniqueness

Current deliverables:

- `sql/validation/001_validate_geography.sql`
- `sql/validation/002_validate_epa.sql`
- `sql/validation/003_validate_cdc.sql`
- `sql/validation/004_validate_referential_integrity.sql`
- `sql/analytics/001_county_air_quality.sql`
- `sql/analytics/002_respiratory_health.sql`
- `sql/analytics/003_county_environment_health.sql`
- `sql/analysis/001_build_2022_analysis_cohort.sql`
- `src/envirohealth/validation.py`

## Milestone 6: Statistical Analysis

Status: started

Primary question:

Among U.S. counties with available EPA PM2.5 monitoring data in 2022, is annual mean PM2.5 associated with age-adjusted adult asthma and COPD prevalence?

Current deliverables:

- `docs/statistical_analysis_plan.md`
- `src/envirohealth/analysis/`
- `outputs/analysis/cohort_summary.csv`
- `outputs/analysis/monitoring_missingness_health_comparison.csv`

## Milestone 7: Predictive ML Benchmark

Status: started

Current deliverables:

- `src/envirohealth/modeling/`
- `docs/modeling_methods.md`
- `outputs/modeling/model_performance.csv`
- `outputs/modeling/permutation_importance.csv`

Current result:

- Asthma prediction improved with Random Forest relative to linear baselines.
- COPD prediction was already strong with linear/ridge models, and nonlinear ML added little.
- Smoking prevalence dominated permutation importance, especially for COPD.

## Milestone 8: Resume Write-Up

Status: superseded by Milestones 8-10

## Milestone 8: Production Hardening

Status: complete

Current deliverables:

- `Dockerfile`
- `.dockerignore`
- `docker-compose.yml` with PostgreSQL health check and optional app service
- `Makefile`
- `docs/production_hardening.md`
- opt-in PostgreSQL integration test

## Milestone 9: GitHub Actions CI/CD

Status: functionally complete; awaiting GitHub-side workflow confirmation

Current deliverables:

- `.github/workflows/ci.yml`
- CI badge in `README.md`
- workflow runs Ruff, pytest, PostgreSQL integration test, and Docker app build

## Milestone 10: Portfolio Release

Status: started

Turn the finished work into README diagrams, architecture notes, and resume bullets.

Current deliverables:

- Polished `README.md`
- `LICENSE`
- `docs/release_checklist.md`
- `docs/resume_notes.md`
- Selected portfolio figures in `docs/assets/`
