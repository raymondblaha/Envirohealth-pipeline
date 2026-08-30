CREATE TABLE IF NOT EXISTS core.counties (
    county_fips char(5) PRIMARY KEY,
    state_fips char(2) NOT NULL,
    county_code char(3) NOT NULL,
    state_abbr text,
    state_name text,
    county_name text
);

CREATE TABLE IF NOT EXISTS core.cbsas (
    cbsa_code integer PRIMARY KEY,
    cbsa_name text NOT NULL
);

CREATE TABLE IF NOT EXISTS core.epa_parameters (
    parameter_code integer PRIMARY KEY,
    parameter_name text NOT NULL
);

CREATE TABLE IF NOT EXISTS core.epa_monitors (
    monitor_id bigserial PRIMARY KEY,
    county_fips char(5) REFERENCES core.counties (county_fips),
    state_code integer NOT NULL,
    county_code integer NOT NULL,
    site_num integer NOT NULL,
    latitude numeric,
    longitude numeric,
    datum text,
    local_site_name text,
    address text,
    city_name text,
    cbsa_name text,
    UNIQUE (state_code, county_code, site_num)
);

CREATE TABLE IF NOT EXISTS core.epa_monitor_measurements (
    measurement_id bigserial PRIMARY KEY,
    monitor_id bigint NOT NULL REFERENCES core.epa_monitors (monitor_id),
    parameter_code integer NOT NULL REFERENCES core.epa_parameters (parameter_code),
    poc integer NOT NULL,
    year integer NOT NULL,
    sample_duration text,
    pollutant_standard text,
    metric_used text,
    method_name text,
    units_of_measure text,
    event_type text,
    observation_count integer,
    observation_percent numeric,
    valid_day_count integer,
    required_day_count integer,
    arithmetic_mean numeric,
    arithmetic_standard_dev numeric,
    p99 numeric,
    p98 numeric,
    p95 numeric,
    p90 numeric,
    p75 numeric,
    p50 numeric,
    p10 numeric
);

CREATE TABLE IF NOT EXISTS core.county_aqi (
    county_fips char(5) REFERENCES core.counties (county_fips),
    state_name text NOT NULL,
    county_name text NOT NULL,
    year integer NOT NULL,
    days_with_aqi integer,
    good_days integer,
    moderate_days integer,
    unhealthy_sensitive_days integer,
    unhealthy_days integer,
    very_unhealthy_days integer,
    hazardous_days integer,
    max_aqi integer,
    p90_aqi integer,
    median_aqi integer,
    days_co integer,
    days_no2 integer,
    days_ozone integer,
    days_pm25 integer,
    days_pm10 integer,
    PRIMARY KEY (state_name, county_name, year)
);

CREATE TABLE IF NOT EXISTS core.cbsa_aqi (
    cbsa_code integer REFERENCES core.cbsas (cbsa_code),
    year integer NOT NULL,
    days_with_aqi integer,
    good_days integer,
    moderate_days integer,
    unhealthy_sensitive_days integer,
    unhealthy_days integer,
    very_unhealthy_days integer,
    hazardous_days integer,
    max_aqi integer,
    p90_aqi integer,
    median_aqi integer,
    days_co integer,
    days_no2 integer,
    days_ozone integer,
    days_pm25 integer,
    days_pm10 integer,
    PRIMARY KEY (cbsa_code, year)
);

CREATE TABLE IF NOT EXISTS core.health_measures (
    measure_id text PRIMARY KEY,
    category_id text NOT NULL,
    category_name text NOT NULL,
    measure_name text NOT NULL,
    short_question_text text
);

CREATE TABLE IF NOT EXISTS core.county_health (
    county_fips char(5) NOT NULL REFERENCES core.counties (county_fips),
    measure_id text NOT NULL REFERENCES core.health_measures (measure_id),
    year integer NOT NULL,
    data_value_type_id text NOT NULL,
    estimate numeric,
    lower_ci numeric,
    upper_ci numeric,
    total_population integer,
    population_18plus integer,
    source_release integer NOT NULL,
    PRIMARY KEY (county_fips, measure_id, year, data_value_type_id)
);

