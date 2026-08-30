from __future__ import annotations

from pathlib import Path

from envirohealth.ingestion.common import SourceSpec
from envirohealth.paths import RAW_DATA_DIR

AQI_COLUMN_MAPPING = {
    "State": "state",
    "County": "county",
    "Year": "year",
    "Days with AQI": "days_with_aqi",
    "Good Days": "good_days",
    "Moderate Days": "moderate_days",
    "Unhealthy for Sensitive Groups Days": "unhealthy_sensitive_days",
    "Unhealthy Days": "unhealthy_days",
    "Very Unhealthy Days": "very_unhealthy_days",
    "Hazardous Days": "hazardous_days",
    "Max AQI": "max_aqi",
    "90th Percentile AQI": "p90_aqi",
    "Median AQI": "median_aqi",
    "Days CO": "days_co",
    "Days NO2": "days_no2",
    "Days Ozone": "days_ozone",
    "Days PM2.5": "days_pm25",
    "Days PM10": "days_pm10",
}

CBSA_COLUMN_MAPPING = {
    "CBSA": "cbsa",
    "CBSA Code": "cbsa_code",
    "Year": "year",
    "Days with AQI": "days_with_aqi",
    "Good Days": "good_days",
    "Moderate Days": "moderate_days",
    "Unhealthy for Sensitive Groups Days": "unhealthy_sensitive_days",
    "Unhealthy Days": "unhealthy_days",
    "Very Unhealthy Days": "very_unhealthy_days",
    "Hazardous Days": "hazardous_days",
    "Max AQI": "max_aqi",
    "90th Percentile AQI": "p90_aqi",
    "Median AQI": "median_aqi",
    "Days CO": "days_co",
    "Days NO2": "days_no2",
    "Days Ozone": "days_ozone",
    "Days PM2.5": "days_pm25",
    "Days PM10": "days_pm10",
}

MONITOR_COLUMN_MAPPING = {
    "State Code": "state_code",
    "County Code": "county_code",
    "Site Num": "site_num",
    "Parameter Code": "parameter_code",
    "POC": "poc",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Datum": "datum",
    "Parameter Name": "parameter_name",
    "Sample Duration": "sample_duration",
    "Pollutant Standard": "pollutant_standard",
    "Metric Used": "metric_used",
    "Method Name": "method_name",
    "Year": "year",
    "Units of Measure": "units_of_measure",
    "Event Type": "event_type",
    "Observation Count": "observation_count",
    "Observation Percent": "observation_percent",
    "Completeness Indicator": "completeness_indicator",
    "Valid Day Count": "valid_day_count",
    "Required Day Count": "required_day_count",
    "Exceptional Data Count": "exceptional_data_count",
    "Null Data Count": "null_data_count",
    "Primary Exceedance Count": "primary_exceedance_count",
    "Secondary Exceedance Count": "secondary_exceedance_count",
    "Certification Indicator": "certification_indicator",
    "Num Obs Below MDL": "num_obs_below_mdl",
    "Arithmetic Mean": "arithmetic_mean",
    "Arithmetic Standard Dev": "arithmetic_standard_dev",
    "1st Max Value": "first_max_value",
    "1st Max DateTime": "first_max_datetime",
    "2nd Max Value": "second_max_value",
    "2nd Max DateTime": "second_max_datetime",
    "3rd Max Value": "third_max_value",
    "3rd Max DateTime": "third_max_datetime",
    "4th Max Value": "fourth_max_value",
    "4th Max DateTime": "fourth_max_datetime",
    "1st Max Non Overlapping Value": "first_max_non_overlapping_value",
    "1st NO Max DateTime": "first_no_max_datetime",
    "2nd Max Non Overlapping Value": "second_max_non_overlapping_value",
    "2nd NO Max DateTime": "second_no_max_datetime",
    "99th Percentile": "p99",
    "98th Percentile": "p98",
    "95th Percentile": "p95",
    "90th Percentile": "p90",
    "75th Percentile": "p75",
    "50th Percentile": "p50",
    "10th Percentile": "p10",
    "Local Site Name": "local_site_name",
    "Address": "address",
    "State Name": "state_name",
    "County Name": "county_name",
    "City Name": "city_name",
    "CBSA Name": "cbsa_name",
    "Date of Last Change": "date_of_last_change",
}

EPA_COUNTY_AQI = SourceSpec(
    source_name="epa_county_aqi",
    table_name="raw.epa_county_aqi",
    file_pattern="annual_aqi_by_county_*.csv",
    column_mapping=AQI_COLUMN_MAPPING,
    required_columns=tuple(AQI_COLUMN_MAPPING),
    integer_columns=tuple(
        column for column in AQI_COLUMN_MAPPING.values() if column not in {"state", "county"}
    ),
)

EPA_CBSA_AQI = SourceSpec(
    source_name="epa_cbsa_aqi",
    table_name="raw.epa_cbsa_aqi",
    file_pattern="annual_aqi_by_cbsa_*.csv",
    column_mapping=CBSA_COLUMN_MAPPING,
    required_columns=tuple(CBSA_COLUMN_MAPPING),
    integer_columns=tuple(column for column in CBSA_COLUMN_MAPPING.values() if column != "cbsa"),
)

EPA_MONITOR_CONCENTRATION = SourceSpec(
    source_name="epa_monitor_concentration",
    table_name="raw.epa_monitor_concentration",
    file_pattern="annual_conc_by_monitor_*.csv",
    column_mapping=MONITOR_COLUMN_MAPPING,
    required_columns=tuple(MONITOR_COLUMN_MAPPING),
    integer_columns=(
        "state_code",
        "county_code",
        "site_num",
        "parameter_code",
        "poc",
        "year",
        "observation_count",
        "valid_day_count",
        "required_day_count",
        "exceptional_data_count",
        "null_data_count",
        "primary_exceedance_count",
        "secondary_exceedance_count",
        "num_obs_below_mdl",
    ),
)

EPA_SPECS = [EPA_COUNTY_AQI, EPA_CBSA_AQI, EPA_MONITOR_CONCENTRATION]


def discover_epa_files(raw_data_dir: Path = RAW_DATA_DIR) -> list[tuple[Path, SourceSpec]]:
    files: list[tuple[Path, SourceSpec]] = []
    epa_dir = raw_data_dir / "epa"
    for spec in EPA_SPECS:
        for path in sorted(epa_dir.glob(spec.file_pattern)):
            files.append((path, spec))
    return files
