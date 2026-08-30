CREATE OR REPLACE VIEW analytics.county_air_quality AS
SELECT
    monitors.county_fips,
    measurements.year,
    COUNT(DISTINCT monitors.monitor_id)::integer AS monitor_count,
    COUNT(*)::integer AS measurement_count,
    COUNT(DISTINCT measurements.parameter_code)::integer AS parameter_count,
    AVG(measurements.observation_percent) AS avg_observation_percent,
    AVG(measurements.arithmetic_mean) FILTER (
        WHERE parameters.parameter_name ILIKE '%PM2.5%'
    ) AS pm25_mean,
    AVG(measurements.p90) FILTER (
        WHERE parameters.parameter_name ILIKE '%PM2.5%'
    ) AS pm25_p90,
    AVG(measurements.arithmetic_mean) FILTER (
        WHERE parameters.parameter_name ILIKE '%ozone%'
    ) AS ozone_mean,
    AVG(measurements.arithmetic_mean) FILTER (
        WHERE parameters.parameter_name ILIKE '%nitrogen dioxide%'
    ) AS no2_mean,
    AVG(measurements.arithmetic_mean) FILTER (
        WHERE parameters.parameter_name ILIKE '%sulfur dioxide%'
    ) AS so2_mean,
    AVG(measurements.arithmetic_mean) FILTER (
        WHERE parameters.parameter_name ILIKE '%carbon monoxide%'
    ) AS co_mean
FROM core.epa_monitor_measurements AS measurements
INNER JOIN core.epa_monitors AS monitors
    ON measurements.monitor_id = monitors.monitor_id
INNER JOIN core.epa_parameters AS parameters
    ON measurements.parameter_code = parameters.parameter_code
GROUP BY monitors.county_fips, measurements.year;

