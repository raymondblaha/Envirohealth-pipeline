SELECT
    'analytics.analysis_2022 grain is one row per county' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Expected one row per county_fips in the frozen 2022 analysis cohort' AS details
FROM (
    SELECT county_fips
    FROM analytics.analysis_2022
    GROUP BY county_fips
    HAVING COUNT(*) > 1
) AS duplicates

UNION ALL

SELECT
    'analytics.analysis_2022 excludes non-county FIPS' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Expected five-digit county_fips values and no national aggregate geography' AS details
FROM analytics.analysis_2022
WHERE county_fips !~ '^[0-9]{5}$'
   OR county_fips = '00000'

UNION ALL

SELECT
    'analytics.analysis_2022 has respiratory outcomes' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Asthma and COPD outcomes should be populated for the frozen 2022 cohort' AS details
FROM analytics.analysis_2022
WHERE asthma_age_adjusted IS NULL
   OR copd_age_adjusted IS NULL

UNION ALL

SELECT
    'analytics.analysis_2022 PM2.5 missingness is surfaced' AS check_name,
    'warning' AS severity,
    COUNT(*)::integer AS failed_count,
    'Rows without PM2.5 are retained so complete-case N can be reported explicitly' AS details
FROM analytics.analysis_2022
WHERE pm25_mean IS NULL;

