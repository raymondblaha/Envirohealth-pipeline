from pathlib import Path

import pandas as pd
import pytest

from envirohealth.ingestion.common import (
    SourceSpec,
    file_sha256,
    normalize_nullable_integer_columns,
    prepare_raw_frame,
    source_year,
    validate_required_columns,
)


def test_prepare_raw_frame_renames_columns_and_adds_source_metadata(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "sample_2022.csv"
    source_file.write_text("Year,State,County\n2022,California,Alameda\n")
    spec = SourceSpec(
        source_name="epa_county_aqi",
        table_name="raw.epa_county_aqi",
        file_pattern="*.csv",
        column_mapping={"Year": "year", "State": "state", "County": "county"},
        required_columns=("Year", "State", "County"),
    )

    frame = prepare_raw_frame(source_file, spec, ingestion_run_id=42)

    assert frame.to_dict(orient="records") == [
        {
            "ingestion_run_id": 42,
            "source_file": "sample_2022.csv",
            "source_row_number": 2,
            "year": 2022,
            "state": "California",
            "county": "Alameda",
        }
    ]


def test_validate_required_columns_fails_for_missing_source_columns() -> None:
    spec = SourceSpec(
        source_name="cdc_places_county",
        table_name="raw.cdc_places_county",
        file_pattern="*.csv",
        column_mapping={"Year": "year"},
        required_columns=("Year", "LocationID"),
    )

    with pytest.raises(ValueError, match="LocationID"):
        validate_required_columns(pd.DataFrame({"Year": [2022]}), spec)


def test_source_year_prefers_single_year_column(tmp_path: Path) -> None:
    path = tmp_path / "annual_aqi_by_county_2021.csv"
    frame = pd.DataFrame({"Year": [2022, 2022]})

    assert source_year(path, frame) == 2022


def test_source_year_falls_back_to_filename(tmp_path: Path) -> None:
    path = tmp_path / "annual_aqi_by_county_2021.csv"
    frame = pd.DataFrame({"State": ["California"]})

    assert source_year(path, frame) == 2021


def test_file_sha256_hashes_source_file(tmp_path: Path) -> None:
    source_file = tmp_path / "source.csv"
    source_file.write_text("abc")

    assert file_sha256(source_file) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_normalize_nullable_integer_columns_removes_float_artifacts() -> None:
    frame = pd.DataFrame({"count": [0.0, 1.0, None]})

    normalize_nullable_integer_columns(frame, ("count",))

    assert frame["count"].astype("string").tolist() == ["0", "1", pd.NA]
