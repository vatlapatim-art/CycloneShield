import ee

PROJECT_ID = "cycloneshield-ai-510103"

ee.Initialize(project=PROJECT_ID)

# Real coastal region near the Amphan track
# This is a broad test region covering the coastal
# West Bengal / Sundarbans area.
region = ee.Geometry.Rectangle([
    87.5, 21.5,
    89.0, 23.0
])

# REAL Sentinel-1 SAR imagery
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
    .select("VV")
)

# Before Amphan
before = (
    sentinel1
    .filterDate("2020-05-10", "2020-05-20")
)

# After Amphan
after = (
    sentinel1
    .filterDate("2020-05-21", "2020-06-01")
)

print("REAL SENTINEL-1 DATA")
print("Before-event images:", before.size().getInfo())
print("After-event images:", after.size().getInfo())

# Calculate regional mean radar backscatter
before_image = before.median()
after_image = after.median()

before_stats = before_image.reduceRegion(
    reducer=ee.Reducer.mean().combine(
        reducer2=ee.Reducer.minMax(),
        sharedInputs=True,
    ),
    geometry=region,
    scale=1000,
    maxPixels=2_000_000,
)

after_stats = after_image.reduceRegion(
    reducer=ee.Reducer.mean().combine(
        reducer2=ee.Reducer.minMax(),
        sharedInputs=True,
    ),
    geometry=region,
    scale=1000,
    maxPixels=2_000_000,
)

print("\nBEFORE EVENT VV STATISTICS:")
print(before_stats.getInfo())

print("\nAFTER EVENT VV STATISTICS:")
print(after_stats.getInfo())