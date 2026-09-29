from services.infrastructure import (
    get_infrastructure,
)


# ==========================================================
# REAL FLOOD ANALYSIS REGION
# ==========================================================

WEST = 87.5
SOUTH = 21.5
EAST = 89.0
NORTH = 23.0


# ==========================================================
# QUERY REAL OSM DATA
# ==========================================================

result = get_infrastructure(
    west=WEST,
    south=SOUTH,
    east=EAST,
    north=NORTH,
)


# ==========================================================
# PRINT SUMMARY
# ==========================================================

print(
    "\n=============================================="
)

print(
    "REAL OPENSTREETMAP INFRASTRUCTURE"
)

print(
    "=============================================="
)


print(
    f"Source: {result['source']}"
)


print(
    "\nCOUNTS:"
)


for key, value in result["counts"].items():

    print(
        f"{key}: {value}"
    )


print(
    "\nFIRST 20 REAL FEATURES:"
)


for feature in result["features"][:20]:

    print(
        {
            "name":
                feature["name"],

            "category":
                feature["category"],

            "subtype":
                feature["subtype"],

            "latitude":
                feature["latitude"],

            "longitude":
                feature["longitude"],
        }
    )