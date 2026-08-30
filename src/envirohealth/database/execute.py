from __future__ import annotations

from pathlib import Path

from envirohealth.paths import PROJECT_ROOT

SCHEMA_FILES = [
    PROJECT_ROOT / "sql/schema/001_create_schemas.sql",
    PROJECT_ROOT / "sql/schema/002_create_raw_tables.sql",
    PROJECT_ROOT / "sql/schema/003_create_core_tables.sql",
    PROJECT_ROOT / "sql/schema/004_add_indexes.sql",
]

TRANSFORMATION_FILES = [
    PROJECT_ROOT / "sql/transformations/001_raw_to_core.sql",
]

ANALYTICS_FILES = [
    PROJECT_ROOT / "sql/analytics/001_county_air_quality.sql",
    PROJECT_ROOT / "sql/analytics/002_respiratory_health.sql",
    PROJECT_ROOT / "sql/analytics/003_county_environment_health.sql",
]

ANALYSIS_FILES = [
    PROJECT_ROOT / "sql/analysis/001_build_2022_analysis_cohort.sql",
]

VALIDATION_FILES = [
    PROJECT_ROOT / "sql/validation/001_validate_geography.sql",
    PROJECT_ROOT / "sql/validation/002_validate_epa.sql",
    PROJECT_ROOT / "sql/validation/003_validate_cdc.sql",
    PROJECT_ROOT / "sql/validation/004_validate_referential_integrity.sql",
    PROJECT_ROOT / "sql/validation/005_validate_analysis_2022.sql",
]

ANALYTICS_EXPORT_QUERIES = {
    "county_environment_health_year_coverage": """
        SELECT
            year,
            COUNT(*) AS rows,
            COUNT(pm25_mean) AS rows_with_pm25,
            COUNT(current_asthma_prevalence) AS rows_with_asthma,
            COUNT(copd_prevalence) AS rows_with_copd
        FROM analytics.county_environment_health
        GROUP BY year
        ORDER BY year
    """,
    "county_environment_health_summary": """
        SELECT
            year,
            COUNT(*) AS county_years,
            MIN(pm25_mean) AS min_pm25_mean,
            AVG(pm25_mean) AS avg_pm25_mean,
            MAX(pm25_mean) AS max_pm25_mean,
            AVG(current_asthma_prevalence) AS avg_current_asthma_prevalence,
            AVG(copd_prevalence) AS avg_copd_prevalence,
            SUM(CASE WHEN high_pm25_county_year THEN 1 ELSE 0 END) AS high_pm25_county_years
        FROM analytics.county_environment_health
        GROUP BY year
        ORDER BY year
    """,
    "respiratory_health_year_coverage": """
        SELECT
            year,
            COUNT(*) AS rows,
            COUNT(current_asthma_prevalence) AS rows_with_asthma,
            COUNT(copd_prevalence) AS rows_with_copd
        FROM analytics.respiratory_health
        GROUP BY year
        ORDER BY year
    """,
    "analysis_2022_cohort_counts": """
        SELECT
            COUNT(*) AS rows,
            COUNT(DISTINCT county_fips) AS counties
        FROM analytics.analysis_2022
    """,
    "analysis_2022_missing_critical_fields": """
        SELECT
            COUNT(*) FILTER (WHERE pm25_mean IS NULL) AS missing_pm25,
            COUNT(*) FILTER (WHERE asthma_age_adjusted IS NULL) AS missing_asthma,
            COUNT(*) FILTER (WHERE copd_age_adjusted IS NULL) AS missing_copd
        FROM analytics.analysis_2022
    """,
    "analysis_2022_complete_case_n": """
        SELECT
            COUNT(*) FILTER (
                WHERE pm25_mean IS NOT NULL
                  AND asthma_age_adjusted IS NOT NULL
            ) AS pm25_asthma_n,
            COUNT(*) FILTER (
                WHERE pm25_mean IS NOT NULL
                  AND copd_age_adjusted IS NOT NULL
            ) AS pm25_copd_n
        FROM analytics.analysis_2022
    """,
    "analysis_2022_duplicate_counties": """
        SELECT county_fips, COUNT(*) AS row_count
        FROM analytics.analysis_2022
        GROUP BY county_fips
        HAVING COUNT(*) > 1
        ORDER BY county_fips
    """,
}


def execute_sql_file(connection: object, path: Path) -> None:
    sql = path.read_text()
    with connection.cursor() as cursor:
        cursor.execute(sql)


def execute_sql_files(connection: object, paths: list[Path]) -> None:
    for path in paths:
        execute_sql_file(connection, path)
