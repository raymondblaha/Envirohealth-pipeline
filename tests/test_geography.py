from envirohealth.geography import county_fips_from_location_id, county_fips_from_parts


def test_county_fips_from_parts_pads_state_and_county_codes() -> None:
    assert county_fips_from_parts(6, 1) == "06001"


def test_county_fips_from_location_id_pads_to_five_digits() -> None:
    assert county_fips_from_location_id(1001) == "01001"

