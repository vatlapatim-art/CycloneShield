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
# BEFORE AND AFTER SENTINEL-1
# ==========================================================

before_collection = sentinel1.filterDate(
    "2020-05-19T00:00:00",
    "2020-05-20T00:00:00"
)

after_collection = sentinel1.filterDate(
    "2020-05-31T00:00:00",
    "2020-06-01T00:00:00"
)

before_count = before_collection.size().getInfo()
after_count = after_collection.size().getInfo()

print("SENTINEL-1 BEFORE SCENES:", before_count)
print("SENTINEL-1 AFTER SCENES:", after_count)


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

print("\nREAL SENTINEL-1 VV CHANGE:")
print(change_stats.getInfo())


# ==========================================================
# REAL DYNAMIC WORLD - BEFORE EVENT
# ==========================================================

dw_before_collection = (
    ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
    .filterBounds(region)
    .filterDate(
        "2020-05-01",
        "2020-05-19"
    )
)

print(
    "\nDYNAMIC WORLD BEFORE IMAGES:",
    dw_before_collection.size().getInfo()
)

dw_before_water = (
    dw_before_collection
    .select("water")
    .median()
    .clip(region)
)


# ==========================================================
# REAL DYNAMIC WORLD - AFTER EVENT
# ==========================================================

dw_after_collection = (
    ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
    .filterBounds(region)
    .filterDate(
        "2020-05-21",
        "2020-06-01"
    )
)

print(
    "DYNAMIC WORLD AFTER IMAGES:",
    dw_after_collection.size().getInfo()
)

dw_after_water = (
    dw_after_collection
    .select("water")
    .median()
    .clip(region)
)


# ==========================================================
# PERMANENT WATER
# ==========================================================

# Pixels that already had high water probability
# before the cyclone are treated as existing water.

permanent_water = dw_before_water.gt(0.5)


# ==========================================================
# NEW WATER AFTER THE EVENT
# ==========================================================

new_water = (
    dw_after_water.gt(0.5)
    .And(
        permanent_water.Not()
    )
)


# ==========================================================
# SENTINEL-1 CHANGE MASK
# ==========================================================

# Initial research/demo threshold:
# VV decrease greater than 3 dB.

sar_change = change.lt(-3)


# ==========================================================
# FLOOD CANDIDATE MASK V2
# ==========================================================

flood_candidate_v2 = (
    sar_change
    .And(new_water)
    .selfMask()
)


# ==========================================================
# AREA CALCULATION
# ==========================================================

flood_area = (
    ee.Image.pixelArea()
    .updateMask(flood_candidate_v2)
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


# ==========================================================
# OUTPUT
# ==========================================================

print("\nNEW FLOOD CANDIDATE AREA:")
print(f"{area_km2:.4f} km²")