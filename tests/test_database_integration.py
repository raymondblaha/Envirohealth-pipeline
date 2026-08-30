import os
from pathlib import Path

import pytest

from envirohealth.database.connection import get_connection
from envirohealth.database.execute import SCHEMA_FILES, execute_sql_files
from envirohealth.ingestion.common import (
    count_rows_for_source_file,
    load_source_file,
)
from envirohealth.ingestion.epa import EPA_COUNTY_AQI

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_DB_TESTS") != "1",
    reason="Database integration tests require RUN_DB_TESTS=1 and PostgreSQL credentials.",
)


def test_database_connection_and_representative_raw_load(tmp_path: Path) -> None:
    source_file = tmp_path / "integration_epa_county_aqi_2099.csv"
    source_file.write_text(
        """State,County,Year,Days with AQI,Good Days,Moderate Days,Unhealthy for Sensitive Groups Days,Unhealthy Days,Very Unhealthy Days,Hazardous Days,Max AQI,90th Percentile AQI,Median AQI,Days CO,Days NO2,Days Ozone,Days PM2.5,Days PM10
Test State,Test County,2099,365,300,60,5,0,0,0,90,70,35,0,5,120,240,0
"""
    )

    with get_connection() as connection:
        execute_sql_files(connection, SCHEMA_FILES)
        connection.commit()

        row = load_source_file(connection, source_file, EPA_COUNTY_AQI)
        connection.commit()

        assert row["rows_read"] == 1
        assert row["rows_loaded"] == 1
        assert count_rows_for_source_file(connection, EPA_COUNTY_AQI.table_name, source_file.name) == 1
