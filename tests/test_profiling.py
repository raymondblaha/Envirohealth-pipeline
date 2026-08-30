from pathlib import Path

from envirohealth.profiling.profile import dataset_name, looks_like_identifier


def test_dataset_name_uses_raw_relative_path() -> None:
    path = Path("data/raw/epa/annual_aqi_by_county_2022.csv").resolve()

    assert dataset_name(path) == "epa__annual_aqi_by_county_2022"


def test_identifier_detection_flags_codes_and_ids() -> None:
    assert looks_like_identifier("State Code")
    assert looks_like_identifier("LocationID")
    assert not looks_like_identifier("Arithmetic Mean")

