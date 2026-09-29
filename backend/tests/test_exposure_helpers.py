from services.exposure import extract_category, extract_coordinates, extract_name


def test_osm_helpers():
    feature = {"lat": "22.1", "lon": "88.2", "name": "Hospital", "category": "medical"}
    assert extract_coordinates(feature) == (22.1, 88.2)
    assert extract_category(feature) == "medical"
    assert extract_name(feature) == "Hospital"
