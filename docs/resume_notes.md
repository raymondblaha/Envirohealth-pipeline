# Resume Notes

Frame this as a data engineering and analytics engineering portfolio project with applied statistics and ML as the analytical layer.

## Short Project Pitch

Built a reproducible Python/PostgreSQL pipeline that integrates EPA air quality data with CDC PLACES health indicators, validates the data warehouse, and produces county-level statistical and ML analyses for environmental health outcomes.

## Resume Bullets

- Built a reproducible Python and PostgreSQL ETL pipeline integrating EPA air quality and CDC PLACES health datasets into `raw`, `core`, and `analytics` schemas with idempotent loading, source-row lineage, constraints, indexes, Docker, and CI.
- Designed and validated a 1,036-county 2022 analytical cohort, including 752 counties with complete PM2.5 exposure plus asthma/COPD outcomes, and implemented SQL validation for geography, EPA data, CDC measures, referential integrity, and analysis-readiness.
- Conducted pre-specified statistical and ML analysis showing no robust PM2.5-asthma association, a small PM2.5-COPD association that weakened after smoking adjustment, and stronger asthma performance from Random Forest versus Ridge regression.

## Interview Talking Points

- Why a `raw -> core -> analytics` architecture improves reproducibility and debugging.
- How FIPS keys were standardized across EPA and CDC sources.
- Why monitor coverage and missing exposure data affect interpretation.
- How SQL validation and pytest cover different parts of the quality problem.
- Why the analysis is ecological and predictive rather than causal.
