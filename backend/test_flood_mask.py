import ee

PROJECT_ID = "cycloneshield-ai-510103"

ee.Initialize(project=PROJECT_ID)

# ==========================================================
# REAL EVENT REGION
# ==========================================================

region = ee.Geometry.Rectangle([
    87.5, 21.5,
    89.0, 23.0
])


# ==========================================================
# REAL SENTINEL-1 DATA
# ==========================================================

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


# ==========================================================
# BEFORE / AFTER MATCHED COLLECTIONS
# ==========================================================

before_collection = sentinel1.filterDate(
    "2020-05-19T00:00:00",
    "2020-05-20T00:00:00"
)

after_collection = sentinel1.filterDate(
    "2020-05-31T00:00:00",
    "2020-06-01T00:00:00"
)

print("BEFORE SCENES:", before_collection.size().getInfo())
print("AFTER SCENES:", after_collection.size().getInfo())


# ==========================================================
# USE REAL SATELLITE OBSERVATIONS
# ==========================================================

before = before_collection.median().clip(region)
after = after_collection.median().clip(region)


# ==========================================================
# REAL SENTINEL-1 CHANGE
# ==========================================================

change = after.subtract(before)

change_stats = change.reduceRegion(
    reducer=ee.Reducer.mean().combine(
        reducer2=ee.Reducer.minMax(),
        sharedInputs=True
    ),
    geometry=region,
    scale=1000,
    maxPixels=2_000_000
)

print("\nREAL VV CHANGE:")
print(change_stats.getInfo())


# ==========================================================
# REAL DYNAMIC WORLD WATER INFORMATION
# ==========================================================

dynamic_world = (
    ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
    .filterBounds(region)
    .filterDate(
        "2020-05-21",
        "2020-06-01"
    )
)

print(
    "\nREAL DYNAMIC WORLD IMAGES:",
    dynamic_world.size().getInfo()
)

water_probability = (
    dynamic_world
    .select("water")
    .median()
    .clip(region)
)


# ==========================================================
# FLOOD CANDIDATE MASK
# ==========================================================

# Candidate inundation signal:
# Sentinel-1 VV decrease greater than 3 dB
# combined with high Dynamic World water probability.
#
# This is a research/demo threshold, NOT an official
# universal flood threshold.

vv_decrease = change.lt(-3)

water_mask = water_probability.gt(0.5)

flood_candidate = (
    vv_decrease
    .And(water_mask)
    .selfMask()
)


# ==========================================================
# FLOOD CANDIDATE AREA
# ==========================================================

# Use a coarser scale only for the regional area
# aggregation so Earth Engine does not process
# hundreds of millions of pixels at once.

flood_area = (
    ee.Image.pixelArea()
    .updateMask(flood_candidate)
    .reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=region,
        scale=100,
        maxPixels=3_000_000,
        tileScale=4
    )
)

area_m2 = flood_area.get("area").getInfo()

if area_m2 is None:
    area_km2 = 0.0
else:
    area_km2 = area_m2 / 1_000_000


print("\nREAL FLOOD CANDIDATE AREA:")
print(f"{area_km2:.4f} km²")