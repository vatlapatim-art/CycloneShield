import ee

PROJECT_ID = "cycloneshield-ai-510103"

ee.Initialize(project=PROJECT_ID)

# Real NOAA IBTrACS dataset
cyclones = ee.FeatureCollection("NOAA/IBTrACS/v4")

# Real Cyclone Amphan (2020)
amphan = (
    cyclones
    .filter(ee.Filter.eq("SID", "2020136N10088"))
    .sort("ISO_TIME")
)

count = amphan.size().getInfo()

print("REAL CYCLONE: AMPHAN (2020)")
print("Track observations:", count)

features = amphan.getInfo()["features"]

print("\nTRACK:\n")

for feature in features:
    properties = feature["properties"]
    geometry = feature.get("geometry")

    coords = None

    if geometry and geometry.get("coordinates"):
        coords = geometry["coordinates"]

    print({
        "time": properties.get("ISO_TIME"),
        "name": properties.get("NAME"),
        "wind_wmo": properties.get("WMO_WIND"),
        "pressure_wmo": properties.get("WMO_PRES"),
        "wind_usa": properties.get("USA_WIND"),
        "pressure_usa": properties.get("USA_PRES"),
        "coordinates": coords,
    })