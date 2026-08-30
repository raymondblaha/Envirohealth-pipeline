# Data Sources

This project currently expects raw source files in local folders under `data/raw/`.

## EPA

Expected folder: `data/raw/epa/`

Current files:

- `annual_aqi_by_cbsa_2021.csv`
- `annual_aqi_by_cbsa_2022.csv`
- `annual_aqi_by_county_2021.csv`
- `annual_aqi_by_county_2022.csv`
- `annual_conc_by_monitor_2021.csv`
- `annual_conc_by_monitor_2022.csv`

## CDC PLACES

Expected folder: `data/raw/cdc/`

Current file:

- `PLACES__Local_Data_for_Better_Health,_County_Data_2024_release_20260829.csv`

## Git Policy

Raw data is not committed to Git. The repository should contain code, documentation, SQL, tests, and reproducible instructions. Generated profiling and processed outputs are also ignored by default.

## Reproducibility TODO

- Add exact download URLs for each EPA file.
- Add exact download URL and access date for the CDC PLACES file.
- Add checksum manifest for local raw files.

