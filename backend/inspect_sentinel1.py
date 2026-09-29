import ee

PROJECT_ID = "cycloneshield-ai-510103"

ee.Initialize(project=PROJECT_ID)

region = ee.Geometry.Rectangle([
    87.5, 21.5,
    89.0, 23.0
])

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


def print_scenes(collection, label):
    scenes = collection.sort("system:time_start").toList(100)
    count = collection.size().getInfo()

    print(f"\n===== {label} =====")
    print("Scene count:", count)

    for i in range(min(count, 100)):
        image = ee.Image(scenes.get(i))

        info = image.toDictionary([
            "system:index",
            "system:time_start",
            "orbitProperties_pass",
            "relativeOrbitNumber_start",
            "resolution_meters",
            "platform_number",
        ]).getInfo()

        print(info)


before = sentinel1.filterDate(
    "2020-05-10",
    "2020-05-20"
)

after = sentinel1.filterDate(
    "2020-05-21",
    "2020-06-01"
)

print_scenes(before, "BEFORE AMPHAN")
print_scenes(after, "AFTER AMPHAN")