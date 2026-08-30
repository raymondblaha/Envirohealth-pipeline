SELECT
    'core.epa_monitors county_fips has parent county' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Every monitor county_fips should exist in core.counties' AS details
FROM core.epa_monitors AS monitors
LEFT JOIN core.counties AS counties
    ON monitors.county_fips = counties.county_fips
WHERE monitors.county_fips IS NOT NULL
  AND counties.county_fips IS NULL

UNION ALL

SELECT
    'core.county_health county_fips has parent county' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Every county_health county_fips should exist in core.counties' AS details
FROM core.county_health AS health
LEFT JOIN core.counties AS counties
    ON health.county_fips = counties.county_fips
WHERE counties.county_fips IS NULL

UNION ALL

SELECT
    'core.county_health measure_id has parent measure' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Every county_health measure_id should exist in core.health_measures' AS details
FROM core.county_health AS health
LEFT JOIN core.health_measures AS measures
    ON health.measure_id = measures.measure_id
WHERE measures.measure_id IS NULL

UNION ALL

SELECT
    'core.cbsa_aqi cbsa_code has parent cbsa' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Every cbsa_aqi cbsa_code should exist in core.cbsas' AS details
FROM core.cbsa_aqi AS aqi
LEFT JOIN core.cbsas AS cbsas
    ON aqi.cbsa_code = cbsas.cbsa_code
WHERE cbsas.cbsa_code IS NULL

UNION ALL

SELECT
    'core.epa_monitor_measurements monitor_id has parent monitor' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Every measurement monitor_id should exist in core.epa_monitors' AS details
FROM core.epa_monitor_measurements AS measurements
LEFT JOIN core.epa_monitors AS monitors
    ON measurements.monitor_id = monitors.monitor_id
WHERE monitors.monitor_id IS NULL

UNION ALL

SELECT
    'core.epa_monitor_measurements parameter_code has parent parameter' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Every measurement parameter_code should exist in core.epa_parameters' AS details
FROM core.epa_monitor_measurements AS measurements
LEFT JOIN core.epa_parameters AS parameters
    ON measurements.parameter_code = parameters.parameter_code
WHERE parameters.parameter_code IS NULL

UNION ALL

SELECT
    'successful ingestion runs loaded expected rows' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Successful ingestion run metadata should have rows_read = rows_loaded' AS details
FROM raw.ingestion_runs
WHERE status = 'success'
  AND rows_read <> rows_loaded

UNION ALL

SELECT
    'analytics.county_environment_health grain is county/year' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Expected one row per county_fips, year in final analytical view' AS details
FROM (
    SELECT county_fips, year
    FROM analytics.county_environment_health
    GROUP BY county_fips, year
    HAVING COUNT(*) > 1
) AS duplicates

UNION ALL

SELECT
    'analytics.county_environment_health county_fips has parent county' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Every analytical row should map back to core.counties' AS details
FROM analytics.county_environment_health AS analytical
LEFT JOIN core.counties AS counties
    ON analytical.county_fips = counties.county_fips
WHERE counties.county_fips IS NULL;
