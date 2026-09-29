import json
import time
from pathlib import Path

import requests


# ==========================================================
# REAL OPENSTREETMAP / OVERPASS INFRASTRUCTURE SERVICE
# ==========================================================

# Public Overpass instances.
# We use them sequentially, never in parallel.
OVERPASS_ENDPOINTS = [
    "https://overpass.private.coffee/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]


# Identify our application as recommended by OSM.
HEADERS = {
    "User-Agent": (
        "CycloneShieldAI/1.0 "
        "(hackathon disaster-risk research)"
    )
}


# ==========================================================
# LOCAL CACHE
# ==========================================================

# Caching real OSM responses makes the demo much more
# reliable and avoids repeatedly hitting public Overpass
# servers. The cached data is still real OpenStreetMap data.

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"

CACHE_FILE = CACHE_DIR / "infrastructure_cache.json"

CACHE_MAX_AGE_SECONDS = 6 * 60 * 60


# ==========================================================
# CACHE HELPERS
# ==========================================================

def _load_cache():
    if not CACHE_FILE.exists():
        return None

    try:
        with open(
            CACHE_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            cached = json.load(file)

        timestamp = cached.get(
            "timestamp",
            0,
        )

        if (
            time.time() - timestamp
            > CACHE_MAX_AGE_SECONDS
        ):
            return None

        return cached.get(
            "data"
        )

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return None


def _save_cache(data):
    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "timestamp": time.time(),
        "data": data,
    }

    with open(
        CACHE_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            payload,
            file,
            ensure_ascii=False,
            indent=2,
        )


# ==========================================================
# OVERPASS REQUEST
# ==========================================================

def _query_overpass(
    query: str,
):
    last_error = None

    for endpoint in OVERPASS_ENDPOINTS:

        # Retry this endpoint up to 2 times.
        for attempt in range(2):

            try:

                response = requests.post(
                    endpoint,
                    data={
                        "data": query,
                    },
                    headers=HEADERS,
                    timeout=150,
                )


                # --------------------------------------------------
                # RATE LIMIT
                # --------------------------------------------------

                if response.status_code == 429:

                    last_error = (
                        f"HTTP 429 from {endpoint}"
                    )

                    # OSM recommends pausing when a 429
                    # or 406 response is received.
                    #
                    # We wait longer on the second attempt.

                    wait_seconds = (
                        35
                        if attempt == 0
                        else 60
                    )

                    print(
                        f"Overpass rate limited "
                        f"{endpoint}."
                    )

                    print(
                        f"Waiting {wait_seconds} "
                        f"seconds before retry..."
                    )

                    time.sleep(
                        wait_seconds
                    )

                    continue


                response.raise_for_status()

                return response.json()


            except requests.RequestException as exc:

                last_error = (
                    f"{endpoint}: {exc}"
                )

                # Move to another endpoint after
                # a normal network/server failure.

                break


    raise RuntimeError(
        "All Overpass servers failed. "
        f"Last error: {last_error}"
    )


# ==========================================================
# FETCH REAL OSM INFRASTRUCTURE
# ==========================================================

def get_infrastructure(
    west: float,
    south: float,
    east: float,
    north: float,
):
    """
    Fetch real infrastructure from OpenStreetMap
    using Overpass API.

    No synthetic infrastructure is generated.
    """

    # ======================================================
    # CACHE CHECK
    # ======================================================

    cached = _load_cache()

    if cached is not None:

        cached_region = cached.get(
            "region",
            {},
        )

        same_region = (
            cached_region.get("west") == west
            and cached_region.get("south") == south
            and cached_region.get("east") == east
            and cached_region.get("north") == north
        )

        if same_region:

            print(
                "Using cached real "
                "OpenStreetMap data."
            )

            return cached


    bbox = (
        f"{south},{west},{north},{east}"
    )


    # ======================================================
    # QUERY 1 — CRITICAL FACILITIES
    # ======================================================

    facilities_query = f"""
[out:json][timeout:120];

(
  nwr["amenity"="hospital"]({bbox});
  nwr["amenity"="clinic"]({bbox});
  nwr["amenity"="doctors"]({bbox});

  nwr["amenity"="fire_station"]({bbox});
  nwr["emergency"="fire_station"]({bbox});
  nwr["emergency"="ambulance_station"]({bbox});
  nwr["amenity"="police"]({bbox});

  nwr["amenity"="shelter"]({bbox});
  nwr["emergency"="shelter"]({bbox});

  nwr["amenity"="school"]({bbox});

  nwr["power"="substation"]({bbox});
  nwr["power"="plant"]({bbox});
);

out center tags;
"""


    print(
        "Querying real OpenStreetMap "
        "critical facilities..."
    )


    facilities_data = _query_overpass(
        facilities_query
    )


    # ======================================================
    # QUERY 2 — MAJOR ROADS
    # ======================================================

    roads_query = f"""
[out:json][timeout:120];

way
  ["highway"~"motorway|trunk|primary|secondary"]
  ({bbox});

out center tags;
"""


    print(
        "Querying real OpenStreetMap "
        "major roads..."
    )


    roads_data = _query_overpass(
        roads_query
    )


    # ======================================================
    # COMBINE RESULTS
    # ======================================================

    elements = (
        facilities_data.get(
            "elements",
            []
        )
        +
        roads_data.get(
            "elements",
            []
        )
    )


    infrastructure = []


    # ======================================================
    # PROCESS ELEMENTS
    # ======================================================

    for element in elements:

        tags = element.get(
            "tags",
            {}
        )


        element_type = element.get(
            "type"
        )

        element_id = element.get(
            "id"
        )


        # ==================================================
        # COORDINATES
        # ==================================================

        lat = None
        lon = None


        if element_type == "node":

            lat = element.get(
                "lat"
            )

            lon = element.get(
                "lon"
            )

        else:

            center = element.get(
                "center"
            )

            if center:

                lat = center.get(
                    "lat"
                )

                lon = center.get(
                    "lon"
                )


        if (
            lat is None
            or lon is None
        ):
            continue


        # ==================================================
        # CLASSIFY
        # ==================================================

        category = "other"

        subtype = "facility"


        # --------------------------------------------------
        # MEDICAL
        # --------------------------------------------------

        if tags.get(
            "amenity"
        ) in [
            "hospital",
            "clinic",
            "doctors",
        ]:

            category = "medical"

            subtype = tags.get(
                "amenity"
            )


        # --------------------------------------------------
        # FIRE
        # --------------------------------------------------

        elif (
            tags.get(
                "amenity"
            )
            == "fire_station"
            or
            tags.get(
                "emergency"
            )
            == "fire_station"
        ):

            category = "emergency"

            subtype = "fire_station"


        # --------------------------------------------------
        # AMBULANCE
        # --------------------------------------------------

        elif (
            tags.get(
                "emergency"
            )
            == "ambulance_station"
        ):

            category = "emergency"

            subtype = (
                "ambulance_station"
            )


        # --------------------------------------------------
        # POLICE
        # --------------------------------------------------

        elif (
            tags.get(
                "amenity"
            )
            == "police"
        ):

            category = "emergency"

            subtype = "police"


        # --------------------------------------------------
        # SHELTER
        # --------------------------------------------------

        elif (
            tags.get(
                "amenity"
            )
            == "shelter"
            or
            tags.get(
                "emergency"
            )
            == "shelter"
        ):

            category = "shelter"

            subtype = (
                tags.get(
                    "shelter_type"
                )
                or
                "shelter"
            )


        # --------------------------------------------------
        # SCHOOL
        # --------------------------------------------------

        elif (
            tags.get(
                "amenity"
            )
            == "school"
        ):

            category = "public"

            subtype = "school"


        # --------------------------------------------------
        # POWER
        # --------------------------------------------------

        elif (
            tags.get(
                "power"
            )
            in [
                "substation",
                "plant",
            ]
        ):

            category = "power"

            subtype = tags.get(
                "power"
            )


        # --------------------------------------------------
        # ROAD
        # --------------------------------------------------

        elif (
            tags.get(
                "highway"
            )
            in [
                "motorway",
                "trunk",
                "primary",
                "secondary",
            ]
        ):

            category = "road"

            subtype = tags.get(
                "highway"
            )


        # ==================================================
        # NAME
        # ==================================================

        name = (
            tags.get(
                "name"
            )
            or
            tags.get(
                "official_name"
            )
            or
            tags.get(
                "short_name"
            )
            or
            "Unnamed feature"
        )


        # ==================================================
        # ADD FEATURE
        # ==================================================

        infrastructure.append({

            "osm_type":
                element_type,

            "osm_id":
                element_id,

            "name":
                name,

            "category":
                category,

            "subtype":
                subtype,

            "latitude":
                lat,

            "longitude":
                lon,

            "tags":
                tags,

        })


    # ======================================================
    # REMOVE DUPLICATES
    # ======================================================

    unique = {}

    for feature in infrastructure:

        key = (
            feature["osm_type"],
            feature["osm_id"],
        )

        unique[key] = feature


    infrastructure = list(
        unique.values()
    )


    # ======================================================
    # COUNTS
    # ======================================================

    counts = {

        "medical":
            sum(
                item["category"]
                == "medical"
                for item in infrastructure
            ),

        "emergency":
            sum(
                item["category"]
                == "emergency"
                for item in infrastructure
            ),

        "shelter":
            sum(
                item["category"]
                == "shelter"
                for item in infrastructure
            ),

        "public":
            sum(
                item["category"]
                == "public"
                for item in infrastructure
            ),

        "power":
            sum(
                item["category"]
                == "power"
                for item in infrastructure
            ),

        "road":
            sum(
                item["category"]
                == "road"
                for item in infrastructure
            ),

        "total":
            len(infrastructure),

    }


    # ======================================================
    # FINAL RESULT
    # ======================================================

    result = {

        "source":
            "OpenStreetMap / Overpass API",

        "region": {

            "west":
                west,

            "south":
                south,

            "east":
                east,

            "north":
                north,

        },

        "counts":
            counts,

        "features":
            infrastructure,

    }


    # ======================================================
    # SAVE REAL DATA TO CACHE
    # ======================================================

    _save_cache(
        result
    )


    return result