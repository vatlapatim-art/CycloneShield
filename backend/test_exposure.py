from services.infrastructure import get_infrastructure
from services.exposure import calculate_real_exposure


# ============================================================
# REAL FLOOD STUDY REGION
# ============================================================

WEST = 87.5
SOUTH = 21.5
EAST = 89.0
NORTH = 23.0


# ============================================================
# LOAD REAL OSM INFRASTRUCTURE
# ============================================================

print(
    "Loading real OpenStreetMap infrastructure..."
)

infrastructure = get_infrastructure(
    WEST,
    SOUTH,
    EAST,
    NORTH,
)


# ============================================================
# CALCULATE REAL EXPOSURE
# ============================================================

result = calculate_real_exposure(
    infrastructure
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("REAL INFRASTRUCTURE FLOOD EXPOSURE")
print("=" * 60)

print(
    f"Critical infrastructure: "
    f"{result['total_critical']}"
)

print(
    f"Directly on flood candidate: "
    f"{result['direct_exposed_count']}"
)

print(
    f"Within "
    f"{result['nearby_distance_meters']} m "
    f"of candidate: "
    f"{result['nearby_exposed_count']}"
)

print(
    f"Direct candidate exposure: "
    f"{result['direct_exposure_percentage']:.2f}%"
)

print(
    f"Nearby candidate exposure: "
    f"{result['nearby_exposure_percentage']:.2f}%"
)


# ============================================================
# CATEGORY BREAKDOWN
# ============================================================

print()
print("CATEGORY BREAKDOWN")
print("-" * 60)

for category, stats in sorted(
    result["by_category"].items()
):

    print(
        f"{category.upper():<12} "
        f"Total: {stats['total']:<5} "
        f"Direct: {stats['direct_exposed']:<5} "
        f"Nearby: {stats['nearby_exposed']}"
    )


# ============================================================
# NEARBY EXPOSED FACILITIES
# ============================================================

print()
print("=" * 60)
print("INFRASTRUCTURE NEAR FLOOD CANDIDATES")
print("=" * 60)

nearby = result[
    "nearby_exposed_features"
]

if not nearby:

    print(
        "No critical infrastructure points "
        f"were found within "
        f"{result['nearby_distance_meters']} m "
        "of the satellite-derived flood candidate."
    )

else:

    print(
        f"Found {len(nearby)} facilities "
        "near flood candidates."
    )

    print()

    for i, feature in enumerate(
        nearby[:30],
        start=1
    ):

        print(
            f"{i}. "
            f"{feature['name']} | "
            f"{feature['category']} | "
            f"Lat: {feature['latitude']:.6f} | "
            f"Lon: {feature['longitude']:.6f}"
        )


# ============================================================
# INTERPRETATION
# ============================================================

print()
print("=" * 60)
print("INTERPRETATION")
print("=" * 60)

print(
    "Direct = the exact infrastructure point "
    "falls on a flood-candidate pixel."
)

print(
    "Nearby = a flood-candidate pixel occurs "
    f"within {result['nearby_distance_meters']} m."
)

print(
    "All infrastructure locations come from "
    "real OpenStreetMap data."
)

print(
    "Flood candidates come from real Sentinel-1 "
    "and Dynamic World observations."
)

print(
    "The result is a candidate exposure indicator, "
    "not a confirmed flood observation."
)

print("=" * 60)