from __future__ import annotations

from pathlib import Path

from envirohealth.ingestion.common import SourceSpec
from envirohealth.paths import RAW_DATA_DIR

CDC_COLUMN_MAPPING = {
    "Year": "year",
    "StateAbbr": "state_abbr",
    "StateDesc": "state_desc",
    "LocationName": "location_name",
    "DataSource": "data_source",
    "Category": "category",
    "Measure": "measure",
    "Data_Value_Unit": "data_value_unit",
    "Data_Value_Type": "data_value_type",
    "Data_Value": "data_value",
    "Data_Value_Footnote_Symbol": "data_value_footnote_symbol",
    "Data_Value_Footnote": "data_value_footnote",
    "Low_Confidence_Limit": "low_confidence_limit",
    "High_Confidence_Limit": "high_confidence_limit",
    "TotalPopulation": "total_population",
    "TotalPop18plus": "total_pop_18plus",
    "LocationID": "location_id",
    "CategoryID": "category_id",
    "MeasureId": "measure_id",
    "DataValueTypeID": "data_value_type_id",
    "Short_Question_Text": "short_question_text",
    "Geolocation": "geolocation",
}

CDC_PLACES_COUNTY = SourceSpec(
    source_name="cdc_places_county",
    table_name="raw.cdc_places_county",
    file_pattern="*.csv",
    column_mapping=CDC_COLUMN_MAPPING,
    required_columns=tuple(CDC_COLUMN_MAPPING),
    integer_columns=("year", "location_id"),
)


def discover_cdc_files(raw_data_dir: Path = RAW_DATA_DIR) -> list[tuple[Path, SourceSpec]]:
    cdc_dir = raw_data_dir / "cdc"
    return [(path, CDC_PLACES_COUNTY) for path in sorted(cdc_dir.glob(CDC_PLACES_COUNTY.file_pattern))]
