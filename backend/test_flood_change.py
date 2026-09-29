import ee

PROJECT_ID = "cycloneshield-ai-510103"

ee.Initialize(project=PROJECT_ID)

# Coastal Sundarbans / West Bengal region
region = ee.Geometry.Rectangle([
    87.5, 21.5,
    89.0, 23.0
])

# Real Sentinel-1 VV data
sentinel1 = (
    ee.ImageCollection("COPERNICUS/S1_GRD")
    .filterBounds(region)
    .filter(ee.Filter.eq("instrumentMode", "IW"))
    .filter(
        ee.Filter.listContains(
            "transmitterReceiverPolarisation",
            "VV"
        )
    )
    .filter(
        ee.Filter.eq(
            "orbitProperties_pass",
            "ASCENDING"
        )
    )
    .filter(
        ee.Filter.eq(
            "relativeOrbitNumber_start",
            12
        )
    )
    .select("VV")
)

# Before Amphan
before_collection = (
    sentinel1
    .filterDate(
        "2020-05-19T00:00:00",
        "2020-05-20T00:00:00"
    )
)

# After Amphan
after_collection = (
    sentinel1
    .filterDate(
        "2020-05-31T00:00:00",
        "2020-06-01T00:00:00"
    )
)

print("MATCHED SENTINEL-1 DATA")
print(
    "Before scenes:",
    before_collection.size().getInfo()
)
print(
    "After scenes:",
    after_collection.size().getInfo()
)

before = before_collection.first()
after = after_collection.first()

# Difference in VV backscatter.
# Negative values indicate a decrease after the event.
difference = after.subtract(before)

stats = difference.reduceRegion(
    reducer=ee.Reducer.mean().combine(
        reducer2=ee.Reducer.minMax(),
        sharedInputs=True
    ),
    geometry=region,
    scale=1000,
    maxPixels=2_000_000
)

print("\nREAL BEFORE/AFTER VV CHANGE:")
print(stats.getInfo())