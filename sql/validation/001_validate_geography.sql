SELECT
    'core.counties county_fips is five numeric characters' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'county_fips must preserve leading zeros as CHAR(5)' AS details
FROM core.counties
WHERE county_fips IS NULL OR county_fips !~ '^[0-9]{5}$'

UNION ALL

SELECT
    'core.counties state_fips is two numeric characters' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'state_fips is derived from county_fips positions 1-2' AS details
FROM core.counties
WHERE state_fips IS NULL OR state_fips !~ '^[0-9]{2}$'

UNION ALL

SELECT
    'core.counties county_code is three numeric characters' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'county_code is derived from county_fips positions 3-5' AS details
FROM core.counties
WHERE county_code IS NULL OR county_code !~ '^[0-9]{3}$'

UNION ALL

SELECT
    'core.counties state/county parts match county_fips' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'state_fips || county_code should equal county_fips' AS details
FROM core.counties
WHERE state_fips || county_code <> county_fips

UNION ALL

SELECT
    'core.counties has no duplicate county_fips' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Primary key grain should be one row per county_fips' AS details
FROM (
    SELECT county_fips
    FROM core.counties
    GROUP BY county_fips
    HAVING COUNT(*) > 1
) AS duplicates

UNION ALL

SELECT
    'core.counties missing county_name' AS check_name,
    'warning' AS severity,
    COUNT(*)::integer AS failed_count,
    'Names are useful for reporting; missing values should be investigated' AS details
FROM core.counties
WHERE state_fips <> '00'
  AND (county_name IS NULL OR btrim(county_name) = '')

UNION ALL

SELECT
    'core.county_aqi rows not mapped to county_fips yet' AS check_name,
    'warning' AS severity,
    COUNT(*)::integer AS failed_count,
    'EPA county AQI source lacks FIPS; name resolution remains an explicit future step' AS details
FROM core.county_aqi
WHERE county_fips IS NULL;
