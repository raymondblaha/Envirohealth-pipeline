TRUNCATE TABLE
    core.county_health,
    core.cbsa_aqi,
    core.county_aqi,
    core.epa_monitor_measurements,
    core.epa_monitors,
    core.health_measures,
    core.epa_parameters,
    core.cbsas,
    core.counties
RESTART IDENTITY;

INSERT INTO core.counties (
    county_fips,
    state_fips,
    county_code,
    state_abbr,
    state_name,
    county_name
)
SELECT DISTINCT
    lpad(location_id::text, 5, '0') AS county_fips,
    substring(lpad(location_id::text, 5, '0') FROM 1 FOR 2) AS state_fips,
    substring(lpad(location_id::text, 5, '0') FROM 3 FOR 3) AS county_code,
    state_abbr,
    state_desc,
    location_name
FROM raw.cdc_places_county
WHERE location_id IS NOT NULL
ON CONFLICT (county_fips) DO UPDATE
SET
    state_abbr = EXCLUDED.state_abbr,
    state_name = EXCLUDED.state_name,
    county_name = EXCLUDED.county_name;

INSERT INTO core.counties (
    county_fips,
    state_fips,
    county_code,
    state_name,
    county_name
)
SELECT DISTINCT
    lpad(state_code::text, 2, '0') || lpad(county_code::text, 3, '0') AS county_fips,
    lpad(state_code::text, 2, '0') AS state_fips,
    lpad(county_code::text, 3, '0') AS county_code,
    state_name,
    county_name
FROM raw.epa_monitor_concentration
ON CONFLICT (county_fips) DO UPDATE
SET
    state_name = COALESCE(core.counties.state_name, EXCLUDED.state_name),
    county_name = COALESCE(core.counties.county_name, EXCLUDED.county_name);

INSERT INTO core.cbsas (cbsa_code, cbsa_name)
SELECT DISTINCT cbsa_code, cbsa
FROM raw.epa_cbsa_aqi
ON CONFLICT (cbsa_code) DO UPDATE
SET cbsa_name = EXCLUDED.cbsa_name;

INSERT INTO core.epa_parameters (parameter_code, parameter_name)
SELECT DISTINCT parameter_code, parameter_name
FROM raw.epa_monitor_concentration
ON CONFLICT (parameter_code) DO UPDATE
SET parameter_name = EXCLUDED.parameter_name;

INSERT INTO core.health_measures (
    measure_id,
    category_id,
    category_name,
    measure_name,
    short_question_text
)
SELECT DISTINCT
    measure_id,
    category_id,
    category,
    measure,
    short_question_text
FROM raw.cdc_places_county
ON CONFLICT (measure_id) DO UPDATE
SET
    category_id = EXCLUDED.category_id,
    category_name = EXCLUDED.category_name,
    measure_name = EXCLUDED.measure_name,
    short_question_text = EXCLUDED.short_question_text;

INSERT INTO core.epa_monitors (
    county_fips,
    state_code,
    county_code,
    site_num,
    latitude,
    longitude,
    datum,
    local_site_name,
    address,
    city_name,
    cbsa_name
)
SELECT DISTINCT
    lpad(state_code::text, 2, '0') || lpad(county_code::text, 3, '0') AS county_fips,
    state_code,
    county_code,
    site_num,
    latitude,
    longitude,
    datum,
    local_site_name,
    address,
    city_name,
    cbsa_name
FROM raw.epa_monitor_concentration
ON CONFLICT (state_code, county_code, site_num) DO UPDATE
SET
    county_fips = EXCLUDED.county_fips,
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    datum = EXCLUDED.datum,
    local_site_name = EXCLUDED.local_site_name,
    address = EXCLUDED.address,
    city_name = EXCLUDED.city_name,
    cbsa_name = EXCLUDED.cbsa_name;

INSERT INTO core.county_health (
    county_fips,
    measure_id,
    year,
    data_value_type_id,
    estimate,
    lower_ci,
    upper_ci,
    total_population,
    population_18plus,
    source_release
)
SELECT
    lpad(location_id::text, 5, '0') AS county_fips,
    measure_id,
    year,
    data_value_type_id,
    data_value,
    low_confidence_limit,
    high_confidence_limit,
    NULLIF(regexp_replace(total_population, '[^0-9]', '', 'g'), '')::integer,
    NULLIF(regexp_replace(total_pop_18plus, '[^0-9]', '', 'g'), '')::integer,
    source_release
FROM raw.cdc_places_county
ON CONFLICT (county_fips, measure_id, year, data_value_type_id) DO UPDATE
SET
    estimate = EXCLUDED.estimate,
    lower_ci = EXCLUDED.lower_ci,
    upper_ci = EXCLUDED.upper_ci,
    total_population = EXCLUDED.total_population,
    population_18plus = EXCLUDED.population_18plus,
    source_release = EXCLUDED.source_release;

INSERT INTO core.county_aqi (
    state_name,
    county_name,
    year,
    days_with_aqi,
    good_days,
    moderate_days,
    unhealthy_sensitive_days,
    unhealthy_days,
    very_unhealthy_days,
    hazardous_days,
    max_aqi,
    p90_aqi,
    median_aqi,
    days_co,
    days_no2,
    days_ozone,
    days_pm25,
    days_pm10
)
SELECT
    state,
    county,
    year,
    days_with_aqi,
    good_days,
    moderate_days,
    unhealthy_sensitive_days,
    unhealthy_days,
    very_unhealthy_days,
    hazardous_days,
    max_aqi,
    p90_aqi,
    median_aqi,
    days_co,
    days_no2,
    days_ozone,
    days_pm25,
    days_pm10
FROM raw.epa_county_aqi
ON CONFLICT (state_name, county_name, year) DO UPDATE
SET
    days_with_aqi = EXCLUDED.days_with_aqi,
    good_days = EXCLUDED.good_days,
    moderate_days = EXCLUDED.moderate_days,
    unhealthy_sensitive_days = EXCLUDED.unhealthy_sensitive_days,
    unhealthy_days = EXCLUDED.unhealthy_days,
    very_unhealthy_days = EXCLUDED.very_unhealthy_days,
    hazardous_days = EXCLUDED.hazardous_days,
    max_aqi = EXCLUDED.max_aqi,
    p90_aqi = EXCLUDED.p90_aqi,
    median_aqi = EXCLUDED.median_aqi,
    days_co = EXCLUDED.days_co,
    days_no2 = EXCLUDED.days_no2,
    days_ozone = EXCLUDED.days_ozone,
    days_pm25 = EXCLUDED.days_pm25,
    days_pm10 = EXCLUDED.days_pm10;

INSERT INTO core.cbsa_aqi (
    cbsa_code,
    year,
    days_with_aqi,
    good_days,
    moderate_days,
    unhealthy_sensitive_days,
    unhealthy_days,
    very_unhealthy_days,
    hazardous_days,
    max_aqi,
    p90_aqi,
    median_aqi,
    days_co,
    days_no2,
    days_ozone,
    days_pm25,
    days_pm10
)
SELECT
    cbsa_code,
    year,
    days_with_aqi,
    good_days,
    moderate_days,
    unhealthy_sensitive_days,
    unhealthy_days,
    very_unhealthy_days,
    hazardous_days,
    max_aqi,
    p90_aqi,
    median_aqi,
    days_co,
    days_no2,
    days_ozone,
    days_pm25,
    days_pm10
FROM raw.epa_cbsa_aqi
ON CONFLICT (cbsa_code, year) DO UPDATE
SET
    days_with_aqi = EXCLUDED.days_with_aqi,
    good_days = EXCLUDED.good_days,
    moderate_days = EXCLUDED.moderate_days,
    unhealthy_sensitive_days = EXCLUDED.unhealthy_sensitive_days,
    unhealthy_days = EXCLUDED.unhealthy_days,
    very_unhealthy_days = EXCLUDED.very_unhealthy_days,
    hazardous_days = EXCLUDED.hazardous_days,
    max_aqi = EXCLUDED.max_aqi,
    p90_aqi = EXCLUDED.p90_aqi,
    median_aqi = EXCLUDED.median_aqi,
    days_co = EXCLUDED.days_co,
    days_no2 = EXCLUDED.days_no2,
    days_ozone = EXCLUDED.days_ozone,
    days_pm25 = EXCLUDED.days_pm25,
    days_pm10 = EXCLUDED.days_pm10;

INSERT INTO core.epa_monitor_measurements (
    monitor_id,
    parameter_code,
    poc,
    year,
    sample_duration,
    pollutant_standard,
    metric_used,
    method_name,
    units_of_measure,
    event_type,
    observation_count,
    observation_percent,
    valid_day_count,
    required_day_count,
    arithmetic_mean,
    arithmetic_standard_dev,
    p99,
    p98,
    p95,
    p90,
    p75,
    p50,
    p10
)
SELECT
    monitors.monitor_id,
    raw_measurements.parameter_code,
    raw_measurements.poc,
    raw_measurements.year,
    raw_measurements.sample_duration,
    raw_measurements.pollutant_standard,
    raw_measurements.metric_used,
    raw_measurements.method_name,
    raw_measurements.units_of_measure,
    raw_measurements.event_type,
    raw_measurements.observation_count,
    raw_measurements.observation_percent,
    raw_measurements.valid_day_count,
    raw_measurements.required_day_count,
    raw_measurements.arithmetic_mean,
    raw_measurements.arithmetic_standard_dev,
    raw_measurements.p99,
    raw_measurements.p98,
    raw_measurements.p95,
    raw_measurements.p90,
    raw_measurements.p75,
    raw_measurements.p50,
    raw_measurements.p10
FROM raw.epa_monitor_concentration AS raw_measurements
INNER JOIN core.epa_monitors AS monitors
    ON raw_measurements.state_code = monitors.state_code
    AND raw_measurements.county_code = monitors.county_code
    AND raw_measurements.site_num = monitors.site_num;
