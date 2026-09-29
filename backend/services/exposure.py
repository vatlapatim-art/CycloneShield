import os

from services.earth_engine import build_flood_candidate


PROJECT_ID = os.getenv("EARTH_ENGINE_PROJECT", "cycloneshield-ai-510103")

# Keep the exposure service self-contained. These are the same real-data
# study-region bounds used by the FastAPI endpoints in main.py.
FLOOD_WEST = 87.5
FLOOD_SOUTH = 21.5
FLOOD_EAST = 89.0
FLOOD_NORTH = 23.0


def ensure_ee():
    """Initialize Earth Engine only when the flood mask is actually requested."""
    import ee
    try:
        ee.Initialize(project=PROJECT_ID)
    except Exception:
        # A second initialize can be harmless in environments where EE is already ready.
        try:
            ee.data.getAssetRoots()
        except Exception:
            raise
    return ee


# ============================================================
# EXPOSURE SEARCH DISTANCE
# ============================================================

# Infrastructure is considered "near a flood candidate"
# when a candidate pixel occurs within this distance.
NEARBY_DISTANCE_METERS = 250


# ============================================================
# CRITICAL INFRASTRUCTURE CATEGORIES
# ============================================================

CRITICAL_CATEGORIES = {
    "medical",
    "emergency",
    "shelter",
    "power",
}


# ============================================================
# BUILD THE SAME REAL FLOOD-CANDIDATE MASK
# ============================================================

def build_shared_flood_candidate():
    """Reuse the exact flood mask implementation used by /flood."""
    built = build_flood_candidate(
        FLOOD_WEST,
        FLOOD_SOUTH,
        FLOOD_EAST,
        FLOOD_NORTH,
        "2020-05-16T00:00:00",
        "2020-05-20T00:00:00",
        "2020-05-20T00:00:00",
        "2020-05-24T00:00:00",
    )
    return built["mask"]


# ============================================================
# EXTRACT COORDINATES
# ============================================================

def extract_coordinates(feature):
    """
    Extract latitude / longitude from an OSM feature.
    """

    if not isinstance(feature, dict):
        return None, None

    lat = feature.get("lat")
    lon = feature.get("lon")

    if lat is None:
        lat = feature.get("latitude")

    if lon is None:
        lon = feature.get("longitude")

    if lon is None:
        lon = feature.get("lng")

    if lat is not None and lon is not None:
        try:
            return float(lat), float(lon)
        except (TypeError, ValueError):
            pass

    geometry = feature.get("geometry")

    if isinstance(geometry, dict):

        coordinates = geometry.get("coordinates")

        if (
            isinstance(coordinates, list)
            and len(coordinates) >= 2
        ):
            try:
                # GeoJSON:
                # [longitude, latitude]

                return (
                    float(coordinates[1]),
                    float(coordinates[0]),
                )

            except (TypeError, ValueError):
                pass

    return None, None


# ============================================================
# EXTRACT CATEGORY
# ============================================================

def extract_category(feature):
    """
    Extract infrastructure category.
    """

    if not isinstance(feature, dict):
        return None

    category = feature.get("category")

    if category is None:
        category = feature.get("type")

    if category is None:

        properties = feature.get("properties")

        if isinstance(properties, dict):

            category = properties.get(
                "category"
            )

            if category is None:

                category = properties.get(
                    "type"
                )

    if category is None:
        return None

    return str(category).strip().lower()


# ============================================================
# EXTRACT NAME
# ============================================================

def extract_name(feature):
    """
    Get the OSM feature name.
    """

    if not isinstance(feature, dict):
        return "Unnamed facility"

    name = feature.get("name")

    if name is None:

        properties = feature.get("properties")

        if isinstance(properties, dict):
            name = properties.get("name")

    if name is None:
        return "Unnamed facility"

    if str(name).strip() == "":
        return "Unnamed facility"

    return str(name)


# ============================================================
# CALCULATE REAL INFRASTRUCTURE EXPOSURE
# ============================================================

def calculate_real_exposure(infrastructure):
    ee = ensure_ee()
    """
    Calculate exposure of real OSM critical infrastructure
    to the real satellite-derived flood candidate.

    Two exposure measurements are produced:

    1. Direct exposure
       The exact infrastructure point intersects
       the flood-candidate mask.

    2. Nearby exposure
       A flood-candidate pixel occurs within 250 m
       of the infrastructure point.

    No synthetic infrastructure or synthetic flood
    data is generated.
    """

    if not isinstance(infrastructure, dict):
        raise ValueError(
            "Infrastructure data must be a dictionary."
        )

    # --------------------------------------------------------
    # GET FEATURES
    # --------------------------------------------------------

    features = infrastructure.get("features")

    if features is None:
        features = infrastructure.get("data")

    if features is None:
        features = []

    if not isinstance(features, list):
        raise ValueError(
            "Infrastructure feature list is invalid."
        )

    # --------------------------------------------------------
    # FILTER CRITICAL FEATURES
    # --------------------------------------------------------

    critical_features = []

    for feature in features:

        category = extract_category(feature)

        if category not in CRITICAL_CATEGORIES:
            continue

        lat, lon = extract_coordinates(feature)

        if lat is None or lon is None:
            continue

        # Restrict to actual flood-analysis region.

        if not (
            FLOOD_WEST <= lon <= FLOOD_EAST
            and
            FLOOD_SOUTH <= lat <= FLOOD_NORTH
        ):
            continue

        critical_features.append(
            {
                "original": feature,
                "category": category,
                "lat": lat,
                "lon": lon,
                "name": extract_name(feature),
            }
        )

    print(
        f"Critical infrastructure features: "
        f"{len(critical_features)}"
    )

    # --------------------------------------------------------
    # EMPTY RESULT
    # --------------------------------------------------------

    if not critical_features:

        return {
            "total_critical": 0,
            "direct_exposed_count": 0,
            "nearby_exposed_count": 0,
            "direct_non_exposed_count": 0,
            "nearby_non_exposed_count": 0,
            "direct_exposure_percentage": 0.0,
            "nearby_exposure_percentage": 0.0,
            "nearby_distance_meters": NEARBY_DISTANCE_METERS,
            "by_category": {},
            "direct_exposed_features": [],
            "nearby_exposed_features": [],
        }

    # --------------------------------------------------------
    # BUILD REAL FLOOD CANDIDATE
    # --------------------------------------------------------

    flood_candidate = build_shared_flood_candidate()

    # --------------------------------------------------------
    # DIRECT CANDIDATE IMAGE
    # --------------------------------------------------------

    direct_image = (
        flood_candidate
        .unmask(0)
        .rename("direct_candidate")
    )

    # --------------------------------------------------------
    # NEARBY CANDIDATE IMAGE
    # --------------------------------------------------------
    #
    # The neighborhood maximum expands the real flood
    # candidate pixels by the specified distance.
    #
    # A facility gets nearby_candidate = 1 when at least
    # one real flood-candidate pixel occurs inside the
    # 250 m neighborhood.
    # --------------------------------------------------------

    nearby_image = direct_image.reduceNeighborhood(
        reducer=ee.Reducer.max(),
        kernel=ee.Kernel.circle(
            radius=NEARBY_DISTANCE_METERS,
            units="meters",
        ),
    ).rename("nearby_candidate")

    # --------------------------------------------------------
    # COMBINE BOTH BANDS
    # --------------------------------------------------------

    sample_image = ee.Image.cat(
        [
            direct_image,
            nearby_image,
        ]
    )

    # --------------------------------------------------------
    # CREATE EARTH ENGINE POINTS
    # --------------------------------------------------------

    ee_features = []

    for item in critical_features:

        point = ee.Geometry.Point(
            [
                item["lon"],
                item["lat"],
            ]
        )

        ee_feature = ee.Feature(
            point,
            {
                "name": item["name"],
                "category": item["category"],
                "latitude": item["lat"],
                "longitude": item["lon"],
            },
        )

        ee_features.append(
            ee_feature
        )

    points = ee.FeatureCollection(
        ee_features
    )

    # --------------------------------------------------------
    # SAMPLE BOTH EXPOSURE TYPES
    # --------------------------------------------------------

    print(
        "Sampling real flood-candidate pixels "
        "at infrastructure locations..."
    )

    print(
        f"Checking candidate pixels within "
        f"{NEARBY_DISTANCE_METERS} m..."
    )

    sampled = sample_image.reduceRegions(
        collection=points,
        reducer=ee.Reducer.first(),
        scale=10,
        tileScale=4,
    )

    results = sampled.getInfo()

    # --------------------------------------------------------
    # PROCESS RESULTS
    # --------------------------------------------------------

    direct_exposed_features = []
    nearby_exposed_features = []

    direct_non_exposed_features = []
    nearby_non_exposed_features = []

    category_stats = {}

    result_features = results.get(
        "features",
        []
    )

    for feature in result_features:

        properties = feature.get(
            "properties",
            {}
        )

        category = properties.get(
            "category",
            "unknown"
        )

        name = properties.get(
            "name",
            "Unnamed facility"
        )

        lat = properties.get(
            "latitude"
        )

        lon = properties.get(
            "longitude"
        )

        direct_value = properties.get(
            "direct_candidate",
            0
        )

        nearby_value = properties.get(
            "nearby_candidate",
            0
        )

        try:

            direct_value = float(
                direct_value
                if direct_value is not None
                else 0
            )

        except (TypeError, ValueError):

            direct_value = 0.0

        try:

            nearby_value = float(
                nearby_value
                if nearby_value is not None
                else 0
            )

        except (TypeError, ValueError):

            nearby_value = 0.0

        is_direct_exposed = (
            direct_value > 0
        )

        is_nearby_exposed = (
            nearby_value > 0
        )

        record = {
            "name": name,
            "category": category,
            "latitude": lat,
            "longitude": lon,
            "direct_flood_candidate": is_direct_exposed,
            "nearby_flood_candidate": is_nearby_exposed,
            "nearby_distance_meters": (
                NEARBY_DISTANCE_METERS
            ),
        }

        # ----------------------------------------------------
        # CATEGORY INITIALIZATION
        # ----------------------------------------------------

        if category not in category_stats:

            category_stats[category] = {
                "total": 0,
                "direct_exposed": 0,
                "nearby_exposed": 0,
                "direct_non_exposed": 0,
                "nearby_non_exposed": 0,
            }

        category_stats[category]["total"] += 1

        # ----------------------------------------------------
        # DIRECT EXPOSURE
        # ----------------------------------------------------

        if is_direct_exposed:

            category_stats[category][
                "direct_exposed"
            ] += 1

            direct_exposed_features.append(
                record
            )

        else:

            category_stats[category][
                "direct_non_exposed"
            ] += 1

            direct_non_exposed_features.append(
                record
            )

        # ----------------------------------------------------
        # NEARBY EXPOSURE
        # ----------------------------------------------------

        if is_nearby_exposed:

            category_stats[category][
                "nearby_exposed"
            ] += 1

            nearby_exposed_features.append(
                record
            )

        else:

            category_stats[category][
                "nearby_non_exposed"
            ] += 1

            nearby_non_exposed_features.append(
                record
            )

    # --------------------------------------------------------
    # OVERALL COUNTS
    # --------------------------------------------------------

    total_critical = len(
        result_features
    )

    direct_exposed_count = len(
        direct_exposed_features
    )

    nearby_exposed_count = len(
        nearby_exposed_features
    )

    direct_non_exposed_count = len(
        direct_non_exposed_features
    )

    nearby_non_exposed_count = len(
        nearby_non_exposed_features
    )

    # --------------------------------------------------------
    # PERCENTAGES
    # --------------------------------------------------------

    if total_critical > 0:

        direct_exposure_percentage = (
            direct_exposed_count
            / total_critical
            * 100
        )

        nearby_exposure_percentage = (
            nearby_exposed_count
            / total_critical
            * 100
        )

    else:

        direct_exposure_percentage = 0.0
        nearby_exposure_percentage = 0.0

    # --------------------------------------------------------
    # PRINT RESULT
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("REAL INFRASTRUCTURE EXPOSURE RESULT")
    print("=" * 60)

    print(
        f"Total critical infrastructure: "
        f"{total_critical}"
    )

    print(
        f"Directly on flood candidate: "
        f"{direct_exposed_count}"
    )

    print(
        f"Within {NEARBY_DISTANCE_METERS} m of candidate: "
        f"{nearby_exposed_count}"
    )

    print(
        f"Direct candidate exposure: "
        f"{direct_exposure_percentage:.2f}%"
    )

    print(
        f"Nearby candidate exposure: "
        f"{nearby_exposure_percentage:.2f}%"
    )

    print()
    print("BY CATEGORY:")

    for category in sorted(
        category_stats
    ):

        stats = category_stats[
            category
        ]

        print(
            f"  {category}: "
            f"{stats['nearby_exposed']} nearby / "
            f"{stats['total']} total "
            f"(direct: "
            f"{stats['direct_exposed']})"
        )

    print()
    print(
        "NOTE:"
    )

    print(
        "Direct exposure means the exact OSM "
        "infrastructure point intersects the "
        "satellite-derived flood candidate."
    )

    print(
        f"Nearby exposure means at least one "
        f"flood-candidate pixel occurs within "
        f"{NEARBY_DISTANCE_METERS} m of the "
        f"infrastructure point."
    )

    print(
        "These are candidate exposure indicators, "
        "not confirmed flood observations."
    )

    print("=" * 60)

    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {
        "total_critical": total_critical,

        "direct_exposed_count": (
            direct_exposed_count
        ),

        "nearby_exposed_count": (
            nearby_exposed_count
        ),

        "direct_non_exposed_count": (
            direct_non_exposed_count
        ),

        "nearby_non_exposed_count": (
            nearby_non_exposed_count
        ),

        "direct_exposure_percentage": round(
            direct_exposure_percentage,
            2,
        ),

        "nearby_exposure_percentage": round(
            nearby_exposure_percentage,
            2,
        ),

        "nearby_distance_meters": (
            NEARBY_DISTANCE_METERS
        ),

        "by_category": category_stats,

        "direct_exposed_features": (
            direct_exposed_features
        ),

        "nearby_exposed_features": (
            nearby_exposed_features
        ),
    }