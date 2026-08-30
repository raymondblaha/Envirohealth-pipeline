from __future__ import annotations


def county_fips_from_parts(state_code: int | str, county_code: int | str) -> str:
    return f"{int(state_code):02d}{int(county_code):03d}"


def county_fips_from_location_id(location_id: int | str) -> str:
    return f"{int(location_id):05d}"

