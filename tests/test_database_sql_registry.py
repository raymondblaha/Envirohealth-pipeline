from envirohealth.database.execute import (
    ANALYSIS_FILES,
    ANALYTICS_EXPORT_QUERIES,
    ANALYTICS_FILES,
    VALIDATION_FILES,
)


def test_validation_sql_files_are_registered_and_exist() -> None:
    assert [path.name for path in VALIDATION_FILES] == [
        "001_validate_geography.sql",
        "002_validate_epa.sql",
        "003_validate_cdc.sql",
        "004_validate_referential_integrity.sql",
        "005_validate_analysis_2022.sql",
    ]
    assert all(path.exists() for path in VALIDATION_FILES)


def test_analytics_sql_files_are_registered_and_exist() -> None:
    assert [path.name for path in ANALYTICS_FILES] == [
        "001_county_air_quality.sql",
        "002_respiratory_health.sql",
        "003_county_environment_health.sql",
    ]
    assert all(path.exists() for path in ANALYTICS_FILES)


def test_analysis_sql_files_are_registered_and_exist() -> None:
    assert [path.name for path in ANALYSIS_FILES] == [
        "001_build_2022_analysis_cohort.sql",
    ]
    assert all(path.exists() for path in ANALYSIS_FILES)


def test_analytics_export_queries_are_registered() -> None:
    assert sorted(ANALYTICS_EXPORT_QUERIES) == [
        "analysis_2022_cohort_counts",
        "analysis_2022_complete_case_n",
        "analysis_2022_duplicate_counties",
        "analysis_2022_missing_critical_fields",
        "county_environment_health_summary",
        "county_environment_health_year_coverage",
        "respiratory_health_year_coverage",
    ]
