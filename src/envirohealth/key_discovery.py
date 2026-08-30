from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from envirohealth.paths import OUTPUTS_DIR, RAW_DATA_DIR

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class CandidateKey:
    dataset: str
    name: str
    columns: tuple[str, ...]


CANDIDATE_KEYS = [
    CandidateKey(
        dataset="cdc_places_county",
        name="county_measure_year_value_type",
        columns=("LocationID", "MeasureId", "Year", "DataValueTypeID"),
    ),
    CandidateKey(
        dataset="epa_county_aqi",
        name="state_county_year",
        columns=("State", "County", "Year"),
    ),
    CandidateKey(
        dataset="epa_cbsa_aqi",
        name="cbsa_code_year",
        columns=("CBSA Code", "Year"),
    ),
    CandidateKey(
        dataset="epa_monitor_concentration",
        name="physical_monitor_site",
        columns=("State Code", "County Code", "Site Num"),
    ),
    CandidateKey(
        dataset="epa_monitor_concentration",
        name="measurement_candidate_without_metric",
        columns=(
            "State Code",
            "County Code",
            "Site Num",
            "Parameter Code",
            "POC",
            "Year",
            "Sample Duration",
            "Pollutant Standard",
            "Event Type",
        ),
    ),
    CandidateKey(
        dataset="epa_monitor_concentration",
        name="measurement_candidate_with_metric",
        columns=(
            "State Code",
            "County Code",
            "Site Num",
            "Parameter Code",
            "POC",
            "Year",
            "Sample Duration",
            "Pollutant Standard",
            "Metric Used",
            "Event Type",
        ),
    ),
    CandidateKey(
        dataset="epa_monitor_concentration",
        name="measurement_candidate_with_method",
        columns=(
            "State Code",
            "County Code",
            "Site Num",
            "Parameter Code",
            "POC",
            "Year",
            "Sample Duration",
            "Pollutant Standard",
            "Metric Used",
            "Method Name",
            "Event Type",
        ),
    ),
]


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def read_and_append(files: list[Path]) -> pd.DataFrame:
    frames = []
    for path in files:
        frame = pd.read_csv(path, low_memory=False)
        frame["source_file"] = path.name
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def load_datasets(raw_data_dir: Path = RAW_DATA_DIR) -> dict[str, pd.DataFrame]:
    return {
        "cdc_places_county": read_and_append(sorted((raw_data_dir / "cdc").glob("*.csv"))),
        "epa_county_aqi": read_and_append(sorted((raw_data_dir / "epa").glob("annual_aqi_by_county_*.csv"))),
        "epa_cbsa_aqi": read_and_append(sorted((raw_data_dir / "epa").glob("annual_aqi_by_cbsa_*.csv"))),
        "epa_monitor_concentration": read_and_append(
            sorted((raw_data_dir / "epa").glob("annual_conc_by_monitor_*.csv"))
        ),
    }


def analyze_candidate_key(frame: pd.DataFrame, candidate: CandidateKey) -> dict[str, object]:
    key_frame = frame.loc[:, candidate.columns]
    null_key_rows = int(key_frame.isna().any(axis=1).sum())
    unique_keys = int(key_frame.drop_duplicates().shape[0])
    row_count = len(frame)
    duplicate_excess_rows = row_count - unique_keys

    duplicate_group_sizes = (
        key_frame.groupby(list(candidate.columns), dropna=False).size().reset_index(name="row_count")
    )
    duplicated_groups = duplicate_group_sizes[duplicate_group_sizes["row_count"] > 1]

    return {
        "dataset": candidate.dataset,
        "candidate_key": candidate.name,
        "columns": " | ".join(candidate.columns),
        "rows": row_count,
        "unique_keys": unique_keys,
        "null_key_rows": null_key_rows,
        "duplicate_key_groups": len(duplicated_groups),
        "duplicate_excess_rows": int(duplicate_excess_rows),
        "is_unique": duplicate_excess_rows == 0 and null_key_rows == 0,
    }


def monitor_site_attribute_report(frame: pd.DataFrame) -> list[dict[str, object]]:
    site_key = ["State Code", "County Code", "Site Num"]
    attributes = [
        "Latitude",
        "Longitude",
        "Datum",
        "Local Site Name",
        "Address",
        "State Name",
        "County Name",
        "City Name",
        "CBSA Name",
    ]

    rows: list[dict[str, object]] = []
    grouped = frame.groupby(site_key, dropna=False)
    for attribute in attributes:
        distinct_counts = grouped[attribute].nunique(dropna=True)
        conflicting_sites = distinct_counts[distinct_counts > 1]
        rows.append(
            {
                "dataset": "epa_monitor_concentration",
                "site_key": " | ".join(site_key),
                "attribute": attribute,
                "sites_with_conflicting_values": len(conflicting_sites),
                "max_distinct_values_for_one_site": int(distinct_counts.max()) if len(distinct_counts) else 0,
            }
        )
    return rows


def write_csv(rows: list[dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_path, index=False)
    LOGGER.info("Wrote %s", output_path)


def run_key_discovery(output_dir: Path = OUTPUTS_DIR / "validation") -> None:
    datasets = load_datasets()
    key_rows = [
        analyze_candidate_key(datasets[candidate.dataset], candidate) for candidate in CANDIDATE_KEYS
    ]
    write_csv(key_rows, output_dir / "candidate_key_report.csv")
    write_csv(
        monitor_site_attribute_report(datasets["epa_monitor_concentration"]),
        output_dir / "monitor_site_attribute_report.csv",
    )


def main() -> None:
    configure_logging()
    run_key_discovery()


if __name__ == "__main__":
    main()

