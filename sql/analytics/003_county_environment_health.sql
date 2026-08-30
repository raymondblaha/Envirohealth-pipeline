CREATE OR REPLACE VIEW analytics.county_environment_health AS
WITH yearly_pm25_thresholds AS (
    SELECT
        year,
        percentile_cont(0.75) WITHIN GROUP (ORDER BY pm25_mean) AS pm25_p75
    FROM analytics.county_air_quality
    WHERE pm25_mean IS NOT NULL
    GROUP BY year
)
SELECT
    air.county_fips,
    counties.state_abbr,
    counties.state_name,
    counties.county_name,
    air.year,
    health.data_value_type_id,
    air.monitor_count,
    air.measurement_count,
    air.parameter_count,
    air.avg_observation_percent,
    air.pm25_mean,
    air.pm25_p90,
    air.ozone_mean,
    air.no2_mean,
    air.so2_mean,
    air.co_mean,
    health.current_asthma_prevalence,
    health.current_asthma_lower_ci,
    health.current_asthma_upper_ci,
    health.copd_prevalence,
    health.copd_lower_ci,
    health.copd_upper_ci,
    CASE
        WHEN air.pm25_mean IS NULL THEN NULL
        WHEN air.pm25_mean >= thresholds.pm25_p75 THEN TRUE
        ELSE FALSE
    END AS high_pm25_county_year
FROM analytics.county_air_quality AS air
INNER JOIN core.counties AS counties
    ON air.county_fips = counties.county_fips
LEFT JOIN yearly_pm25_thresholds AS thresholds
    ON air.year = thresholds.year
LEFT JOIN analytics.respiratory_health AS health
    ON air.county_fips = health.county_fips
    AND air.year = health.year;
