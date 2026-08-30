CREATE INDEX IF NOT EXISTS idx_county_health_measure_year
    ON core.county_health (measure_id, year);

CREATE INDEX IF NOT EXISTS idx_county_aqi_year
    ON core.county_aqi (year);

CREATE INDEX IF NOT EXISTS idx_monitor_measurements_parameter_year
    ON core.epa_monitor_measurements (parameter_code, year);

CREATE INDEX IF NOT EXISTS idx_monitors_county_fips
    ON core.epa_monitors (county_fips);

