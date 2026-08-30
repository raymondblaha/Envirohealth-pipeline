SELECT
    'core.county_health business key is unique' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Expected one row per county_fips, measure_id, year, data_value_type_id' AS details
FROM (
    SELECT county_fips, measure_id, year, data_value_type_id
    FROM core.county_health
    GROUP BY county_fips, measure_id, year, data_value_type_id
    HAVING COUNT(*) > 1
) AS duplicates

UNION ALL

SELECT
    'CDC estimates are percentages from 0 to 100' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'PLACES prevalence estimates should be bounded percentages' AS details
FROM core.county_health
WHERE estimate < 0 OR estimate > 100

UNION ALL

SELECT
    'CDC confidence intervals contain estimate' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Expected lower_ci <= estimate <= upper_ci when all three values are present' AS details
FROM core.county_health
WHERE lower_ci IS NOT NULL
  AND estimate IS NOT NULL
  AND upper_ci IS NOT NULL
  AND (lower_ci > estimate OR estimate > upper_ci)

UNION ALL

SELECT
    'CDC confidence interval order is valid' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Expected lower_ci <= upper_ci' AS details
FROM core.county_health
WHERE lower_ci IS NOT NULL
  AND upper_ci IS NOT NULL
  AND lower_ci > upper_ci

UNION ALL

SELECT
    'core.health_measures business key is unique' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Expected one row per measure_id' AS details
FROM (
    SELECT measure_id
    FROM core.health_measures
    GROUP BY measure_id
    HAVING COUNT(*) > 1
) AS duplicates

UNION ALL

SELECT
    'CDC health rows preserve raw row count' AS check_name,
    'critical' AS severity,
    (
        SELECT ABS(
            (SELECT COUNT(*) FROM raw.cdc_places_county)
            - (SELECT COUNT(*) FROM core.county_health)
        )::integer
    ) AS failed_count,
    'Core county_health rows should equal raw CDC rows' AS details

UNION ALL

SELECT
    'CDC expected core fields are populated' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'County, measure, year, value type, estimate, and CI fields should be present' AS details
FROM core.county_health
WHERE county_fips IS NULL
   OR measure_id IS NULL
   OR year IS NULL
   OR data_value_type_id IS NULL
   OR estimate IS NULL
   OR lower_ci IS NULL
   OR upper_ci IS NULL;

