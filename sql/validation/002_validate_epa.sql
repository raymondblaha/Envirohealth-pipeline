SELECT
    'core.county_aqi business key is unique' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Expected one row per state_name, county_name, year' AS details
FROM (
    SELECT state_name, county_name, year
    FROM core.county_aqi
    GROUP BY state_name, county_name, year
    HAVING COUNT(*) > 1
) AS duplicates

UNION ALL

SELECT
    'core.cbsa_aqi business key is unique' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Expected one row per cbsa_code, year' AS details
FROM (
    SELECT cbsa_code, year
    FROM core.cbsa_aqi
    GROUP BY cbsa_code, year
    HAVING COUNT(*) > 1
) AS duplicates

UNION ALL

SELECT
    'core.epa_monitors business key is unique' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Expected one row per state_code, county_code, site_num' AS details
FROM (
    SELECT state_code, county_code, site_num
    FROM core.epa_monitors
    GROUP BY state_code, county_code, site_num
    HAVING COUNT(*) > 1
) AS duplicates

UNION ALL

SELECT
    'EPA AQI and day-count metrics are nonnegative' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'AQI metrics and day counts should not be negative' AS details
FROM (
    SELECT days_with_aqi, good_days, moderate_days, unhealthy_sensitive_days, unhealthy_days,
           very_unhealthy_days, hazardous_days, max_aqi, p90_aqi, median_aqi,
           days_co, days_no2, days_ozone, days_pm25, days_pm10
    FROM core.county_aqi
    UNION ALL
    SELECT days_with_aqi, good_days, moderate_days, unhealthy_sensitive_days, unhealthy_days,
           very_unhealthy_days, hazardous_days, max_aqi, p90_aqi, median_aqi,
           days_co, days_no2, days_ozone, days_pm25, days_pm10
    FROM core.cbsa_aqi
) AS aqi
WHERE days_with_aqi < 0
   OR good_days < 0
   OR moderate_days < 0
   OR unhealthy_sensitive_days < 0
   OR unhealthy_days < 0
   OR very_unhealthy_days < 0
   OR hazardous_days < 0
   OR max_aqi < 0
   OR p90_aqi < 0
   OR median_aqi < 0
   OR days_co < 0
   OR days_no2 < 0
   OR days_ozone < 0
   OR days_pm25 < 0
   OR days_pm10 < 0

UNION ALL

SELECT
    'EPA monitor coordinates are in valid ranges' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Latitude must be [-90, 90] and longitude must be [-180, 180]' AS details
FROM core.epa_monitors
WHERE latitude < -90
   OR latitude > 90
   OR longitude < -180
   OR longitude > 180

UNION ALL

SELECT
    'EPA monitor measurements preserve raw row count' AS check_name,
    'critical' AS severity,
    (
        SELECT ABS(
            (SELECT COUNT(*) FROM raw.epa_monitor_concentration)
            - (SELECT COUNT(*) FROM core.epa_monitor_measurements)
        )::integer
    ) AS failed_count,
    'Core measurement rows should equal raw monitor concentration rows' AS details

UNION ALL

SELECT
    'EPA measurement observation counts are nonnegative' AS check_name,
    'critical' AS severity,
    COUNT(*)::integer AS failed_count,
    'Observation and valid/required day counts should not be negative' AS details
FROM core.epa_monitor_measurements
WHERE observation_count < 0
   OR observation_percent < 0
   OR valid_day_count < 0
   OR required_day_count < 0

UNION ALL

SELECT
    'EPA parameter code maps to one current parameter name' AS check_name,
    'warning' AS severity,
    COUNT(*)::integer AS failed_count,
    'Multiple source names for one parameter code should be reviewed before stricter constraints' AS details
FROM (
    SELECT parameter_code
    FROM raw.epa_monitor_concentration
    GROUP BY parameter_code
    HAVING COUNT(DISTINCT parameter_name) > 1
) AS conflicting_parameters;

