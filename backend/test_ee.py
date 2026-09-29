import ee

PROJECT_ID = "cycloneshield-ai-510103"

ee.Initialize(project=PROJECT_ID)

# Real NASADEM elevation dataset
dem = ee.Image("NASA/NASADEM_HGT/001").select("elevation")

# Real coastal region: Chennai
chennai = ee.Geometry.Rectangle([
    80.20, 12.80,
    80.40, 13.20
])

stats = dem.reduceRegion(
    reducer=ee.Reducer.mean().combine(
        reducer2=ee.Reducer.minMax(),
        sharedInputs=True
    ),
    geometry=chennai,
    scale=30,
    maxPixels=2_000_000
)

print("REAL NASADEM statistics for Chennai:")
print(stats.getInfo())