CREATE OR REPLACE VIEW analytics.analysis_2022 AS
SELECT
    county_fips,
    state_abbr,
    state_name,
    county_name,
    pm25_mean,
    monitor_count AS pm25_monitor_count,
    measurement_count AS pm25_observation_count,
    NULL::integer AS median_aqi,
    NULL::integer AS p90_aqi,
    NULL::integer AS max_aqi,
    current_asthma_prevalence AS asthma_age_adjusted,
    copd_prevalence AS copd_age_adjusted,
    avg_observation_percent,
    pm25_p90,
    high_pm25_county_year
FROM analytics.county_environment_health
WHERE year = 2022
  AND data_value_type_id = 'AgeAdjPrv'
  AND county_fips ~ '^[0-9]{5}$'
  AND county_fips <> '00000';

