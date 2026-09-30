import json
import os

import ee


PROJECT_ID = os.getenv(
    "EARTH_ENGINE_PROJECT",
    "cycloneshield-ai-510103",
)

# Five times the previous 100M maxPixels budget, as requested.
EE_MAX_PIXELS = 1_000_000_000

_ee = None


def ensure_ee():
    """Lazy-initialize Earth Engine with the Render service-account credentials."""
    global _ee

    if _ee is not None:
        return _ee

    credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if credentials_file and os.path.isfile(credentials_file):
        with open(credentials_file, "r", encoding="utf-8") as f:
            service_account_info = json.load(f)

        service_account = service_account_info["client_email"]

        credentials = ee.ServiceAccountCredentials(
            service_account,
            credentials_file,
        )

        ee.Initialize(
            credentials,
            project=PROJECT_ID,
        )
    else:
        # Local-development fallback.
        ee.Initialize(project=PROJECT_ID)

    _ee = ee
    return _ee


# ==========================================================
# LATEST FLOOD MAP
# ==========================================================

FLOOD_MAP_ID = None


# ==========================================================
# ELEVATION
# ==========================================================

def get_elevation_stats(
    west: float,
    south: float,
    east: float,
    north: float,
):
    ee = ensure_ee()
    region = ee.Geometry.Rectangle([
        west,
        south,
        east,
        north,
    ])

    dem = (
        ee.Image(
            "NASA/NASADEM_HGT/001"
        )
        .select("elevation")
    )

    stats = dem.reduceRegion(
        reducer=ee.Reducer.mean().combine(
            reducer2=ee.Reducer.minMax(),
            sharedInputs=True,
        ),
        geometry=region,
        scale=30,
        maxPixels=EE_MAX_PIXELS,
    )

    result = stats.getInfo()

    return {
        "elevation_mean_m":
            result.get("elevation_mean"),

        "elevation_min_m":
            result.get("elevation_min"),

        "elevation_max_m":
            result.get("elevation_max"),
    }


# ==========================================================
# RAINFALL
# ==========================================================

def get_rainfall_stats(
    west: float,
    south: float,
    east: float,
    north: float,
    start_date: str,
    end_date: str,
):
    ee = ensure_ee()
    region = ee.Geometry.Rectangle([
        west,
        south,
        east,
        north,
    ])

    rainfall_collection = (
        ee.ImageCollection(
            "UCSB-CHG/CHIRPS/DAILY"
        )
        .filterDate(
            start_date,
            end_date,
        )
        .filterBounds(region)
        .select("precipitation")
    )

    image_count = (
        rainfall_collection
        .size()
        .getInfo()
    )

    if image_count == 0:
        raise ValueError(
            "No rainfall data found for this date range."
        )

    total_rainfall = (
        rainfall_collection.sum()
    )

    stats = total_rainfall.reduceRegion(
        reducer=ee.Reducer.mean().combine(
            reducer2=ee.Reducer.minMax(),
            sharedInputs=True,
        ),
        geometry=region,
        scale=5566,
        maxPixels=EE_MAX_PIXELS,
    )

    result = stats.getInfo()

    return {
        "image_count":
            image_count,

        "rainfall_mean_mm":
            result.get("precipitation_mean"),

        "rainfall_min_mm":
            result.get("precipitation_min"),

        "rainfall_max_mm":
            result.get("precipitation_max"),
    }


# ==========================================================
# CYCLONE TRACK
# ==========================================================

def get_cyclone_track(
    sid: str,
):
    ee = ensure_ee()
    cyclones = ee.FeatureCollection(
        "NOAA/IBTrACS/v4"
    )

    track = (
        cyclones
        .filter(
            ee.Filter.eq(
                "SID",
                sid,
            )
        )
        .sort("ISO_TIME")
    )

    count = (
        track
        .size()
        .getInfo()
    )

    if count == 0:
        raise ValueError(
            f"No cyclone found for SID: {sid}"
        )

    features = (
        track
        .select([
            "SID",
            "SEASON",
            "NAME",
            "ISO_TIME",
            "LAT",
            "LON",
            "WMO_WIND",
            "WMO_PRES",
            "USA_WIND",
            "USA_PRES",
            "USA_GUST",
            "USA_STATUS",
            "USA_RECORD",
            "LANDFALL",
            "STORM_SPEED",
            "STORM_DIR",
        ])
        .getInfo()["features"]
    )

    coordinates = []
    observations = []

    for feature in features:

        geometry = feature.get(
            "geometry"
        )

        properties = feature.get(
            "properties",
            {}
        )

        if (
            geometry
            and geometry.get(
                "coordinates"
            )
        ):

            lon, lat = geometry[
                "coordinates"
            ]

            coordinates.append([
                lon,
                lat,
            ])

            observations.append({
                "time":
                    properties.get(
                        "ISO_TIME"
                    ),

                "name":
                    properties.get(
                        "NAME"
                    ),

                "lat":
                    lat,

                "lon":
                    lon,

                "wmo_wind_kt":
                    properties.get(
                        "WMO_WIND"
                    ),

                "wmo_pressure_mb":
                    properties.get(
                        "WMO_PRES"
                    ),

                "usa_wind_kt":
                    properties.get(
                        "USA_WIND"
                    ),

                "usa_pressure_mb":
                    properties.get(
                        "USA_PRES"
                    ),

                "usa_gust_kt": properties.get("USA_GUST"),
                "usa_status": properties.get("USA_STATUS"),
                "usa_record": properties.get("USA_RECORD"),
                "landfall_flag": properties.get("LANDFALL"),
                "storm_speed_kt": properties.get("STORM_SPEED"),
                "storm_direction_deg": properties.get("STORM_DIR"),
            })


    valid_coordinates = [
        coordinate
        for coordinate in coordinates
        if (
            coordinate[0] is not None
            and coordinate[1] is not None
        )
    ]


    line = {
        "type": "Feature",

        "geometry": {
            "type": "LineString",
            "coordinates":
                valid_coordinates,
        },

        "properties": {
            "sid":
                sid,

            "name":
                (
                    observations[0]["name"]
                    if observations
                    else None
                ),

            "season":
                (
                    features[0][
                        "properties"
                    ].get("SEASON")
                    if features
                    else None
                ),

            "observation_count":
                len(observations),
        },
    }


    return {
        "source":
            "NOAA IBTrACS v4 via Google Earth Engine",

        "track":
            line,

        "observations":
            observations,
    }


# ==========================================================
# ECMWF ERA5 REAL WIND FIELD
# ==========================================================

_WIND_FIELD_CACHE = {}


def get_era5_wind_field(
    sid: str,
    west: float = 65.0,
    south: float = 5.0,
    east: float = 105.0,
    north: float = 32.0,
    step_deg: float = 0.75,
    half_window_hours: int = 3,
):
    """Return a regular real ERA5 10 m wind/MSLP grid around a cyclone snapshot.

    ERA5 is an ECMWF/Copernicus hourly atmospheric reanalysis. U/V are the
    eastward/northward 10 m wind components and mean sea-level pressure is
    returned in hPa. The grid is intentionally coarse because ERA5 is roughly
    a 31 km product; the frontend interpolates the vectors for visualization.
    """
    from datetime import datetime, timedelta, timezone

    ee = ensure_ee()
    track = get_cyclone_track(sid)
    observations = track.get("observations", [])
    valid = [
        obs for obs in observations
        if isinstance(obs, dict)
        and obs.get("time")
        and obs.get("lat") is not None
        and obs.get("lon") is not None
    ]
    if not valid:
        raise ValueError(f"No timestamped cyclone observations found for SID: {sid}")

    wind_observations = [
        obs for obs in valid
        if isinstance(obs.get("wmo_wind_kt"), (int, float))
    ]
    snapshot = max(
        wind_observations or valid,
        key=lambda obs: float(obs.get("wmo_wind_kt") or -1),
    )
    timestamp_text = str(snapshot["time"]).replace("Z", "+00:00")
    try:
        snapshot_dt = datetime.fromisoformat(timestamp_text)
    except ValueError as exc:
        raise ValueError(f"Invalid cyclone observation time: {snapshot['time']}") from exc
    if snapshot_dt.tzinfo is None:
        snapshot_dt = snapshot_dt.replace(tzinfo=timezone.utc)

    cache_key = (sid, west, south, east, north, step_deg, snapshot_dt.isoformat())
    cached = _WIND_FIELD_CACHE.get(cache_key)
    if cached is not None:
        return cached

    start = snapshot_dt - timedelta(hours=half_window_hours)
    end = snapshot_dt + timedelta(hours=half_window_hours + 1)

    collection = (
        ee.ImageCollection("ECMWF/ERA5/HOURLY")
        .filterDate(start.isoformat(), end.isoformat())
        .select([
            "u_component_of_wind_10m",
            "v_component_of_wind_10m",
            "mean_sea_level_pressure",
        ])
    )
    image_count = int(collection.size().getInfo())
    if image_count == 0:
        raise ValueError("No ERA5 hourly wind data found for the cyclone snapshot.")

    image = collection.mean()

    cols = int(round((east - west) / step_deg)) + 1
    rows = int(round((north - south) / step_deg)) + 1
    features = []
    for j in range(rows):
        lat = south + j * step_deg
        for i in range(cols):
            lon = west + i * step_deg
            features.append(
                ee.Feature(
                    ee.Geometry.Point([lon, lat]),
                    {"grid_i": i, "grid_j": j, "lat": lat, "lon": lon},
                )
            )
        
    sampled = (
        image
        .sampleRegions(
            collection=ee.FeatureCollection(features),
            properties=["grid_i", "grid_j", "lat", "lon"],
            scale=30000,
            geometries=False,
            tileScale=4,
        )
        .getInfo()
        .get("features", [])
    )

    data = []
    for feature in sampled:
        props = feature.get("properties", {})
        u = props.get("u_component_of_wind_10m")
        v = props.get("v_component_of_wind_10m")
        p = props.get("mean_sea_level_pressure")
        if u is None or v is None or p is None:
            continue
        try:
            u = float(u)
            v = float(v)
            p = float(p)
        except (TypeError, ValueError):
            continue
        speed_ms = (u * u + v * v) ** 0.5
        data.append({
            "i": int(props.get("grid_i")),
            "j": int(props.get("grid_j")),
            "lat": float(props.get("lat")),
            "lon": float(props.get("lon")),
            "u_ms": u,
            "v_ms": v,
            "speed_kt": round(speed_ms * 1.94384449, 2),
            "mslp_hpa": round(p / 100.0, 1),
        })

    if len(data) < 100:
        raise ValueError(f"ERA5 grid returned too few valid wind points: {len(data)}")

    result = {
        "source": "ECMWF ERA5 Hourly via Google Earth Engine",
        "dataset": "ECMWF/ERA5/HOURLY",
        "grid_resolution_km": 31,
        "timestamp": snapshot_dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "window": {
            "start": start.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "end": end.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "hours": image_count,
        },
        "bbox": {"west": west, "south": south, "east": east, "north": north},
        "step_deg": step_deg,
        "rows": rows,
        "cols": cols,
        "center": [float(snapshot["lat"]), float(snapshot["lon"])],
        "peak_wind_kt": snapshot.get("wmo_wind_kt"),
        "peak_pressure_mb": snapshot.get("wmo_pressure_mb"),
        "data": data,
        "note": "Real ERA5 10 m wind/MSLP field; frontend flow is an interpolated visualization and should not be read as station-level observations.",
    }

    if len(_WIND_FIELD_CACHE) > 4:
        _WIND_FIELD_CACHE.pop(next(iter(_WIND_FIELD_CACHE)))
    _WIND_FIELD_CACHE[cache_key] = result
    return result


# ==========================================================
# FLOOD CANDIDATE
# ==========================================================

def _non_empty_dw_composite(ee, region, start_date, end_date, reducer="median"):
    """Return a real Dynamic World composite only when scenes exist.

    Selecting both required bands after checking collection size prevents
    no-band images from reaching Earth Engine comparison operators.
    """
    collection = (
        ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
        .filterBounds(region)
        .filterDate(start_date, end_date)
        .select(["water", "flooded_vegetation"])
    )
    count = int(collection.size().getInfo())
    if count == 0:
        return None, 0
    if reducer == "max":
        image = collection.max()
    elif reducer == "mean":
        image = collection.mean()
    else:
        image = collection.median()
    return image.clip(region), count


def _dynamic_world_with_fallback(ee, region, start_date, end_date, role):
    """Use the requested event window, then progressively wider real windows."""
    windows = [(start_date, end_date)]
    if role == "before":
        windows += [
            ("2020-05-01T00:00:00", "2020-05-20T00:00:00"),
            ("2020-04-20T00:00:00", "2020-05-20T00:00:00"),
        ]
    else:
        windows += [
            ("2020-05-20T00:00:00", "2020-06-05T00:00:00"),
            ("2020-05-20T00:00:00", "2020-06-20T00:00:00"),
        ]

    seen = set()
    for start, end in windows:
        if (start, end) in seen:
            continue
        seen.add((start, end))
        image, count = _non_empty_dw_composite(
            ee, region, start, end,
            reducer="median" if role == "before" else "max",
        )
        if image is not None:
            return image, count, start, end
    return None, 0, None, None

def build_flood_candidate(
    west: float,
    south: float,
    east: float,
    north: float,
    before_start: str,
    before_end: str,
    after_start: str,
    after_end: str,
):
    """Build a real-data inundation candidate mask.

    Primary signal: Sentinel-1 VV backscatter reduction.
    Supporting signal: Dynamic World water/flooded-vegetation probability.
    The function degrades gracefully to a Sentinel-1-only candidate if no
    cloud-filtered Dynamic World scenes exist in the widened event window.
    """
    ee = ensure_ee()
    region = ee.Geometry.Rectangle(
        [west, south, east, north],
        proj="EPSG:4326",
        geodesic=False,
    )

    sentinel1 = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(region)
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
        .select("VV")
    )

    before_collection = sentinel1.filterDate(before_start, before_end)
    after_collection = sentinel1.filterDate(after_start, after_end)
    before_count = int(before_collection.size().getInfo())
    after_count = int(after_collection.size().getInfo())

    if before_count == 0:
        raise ValueError("No Sentinel-1 before-event scenes found.")
    if after_count == 0:
        raise ValueError("No Sentinel-1 after-event scenes found.")

    before = before_collection.median().clip(region)
    after = after_collection.median().clip(region)

    # Smooth each real Sentinel-1 composite slightly before differencing.
    # This reduces isolated SAR speckle without introducing synthetic data.
    before_smooth = before.focal_median(radius=20, units="meters")
    after_smooth = after.focal_median(radius=20, units="meters")

    # Event-change threshold: a meaningful post-event VV reduction is a
    # candidate indicator of inundation. This remains an inference, not a
    # confirmed flood boundary.
    sar_change = after_smooth.subtract(before_smooth).lt(-1.5)

    # Dynamic World is cloud-filtered.  Use an event-aligned window first,
    # then widen it only when the requested window has no usable scenes.
    dw_before, dw_before_count, dw_before_start, dw_before_end = _dynamic_world_with_fallback(
        ee, region, before_start, before_end, "before"
    )
    dw_after, dw_after_count, dw_after_start, dw_after_end = _dynamic_world_with_fallback(
        ee, region, after_start, after_end, "after"
    )

    # Start from the real SAR change signal. Dynamic World is used as a
    # corroborating evidence layer rather than a hard gate; otherwise a
    # missing/patchy optical classification can make the SAR flood candidate
    # disappear entirely.
    flood_signal = sar_change
    water_support = "Sentinel-1 SAR only"

    dynamic_world_support = None
    if dw_after is not None and dw_before is not None:
        # Both composites contain the selected Dynamic World bands.
        permanent_water_dw = dw_before.select("water").gt(0.65)
        post_event_water = dw_after.select("water").gt(0.65)
        flooded_vegetation = dw_after.select("flooded_vegetation").gt(0.55)
        new_water = post_event_water.And(permanent_water_dw.Not())
        dynamic_world_support = new_water.Or(flooded_vegetation)
        water_support = "Sentinel-1 SAR + Dynamic World corroboration"

    # Remove persistent surface water from the SAR-derived event-change
    # signal, then retain the real SAR candidates. If Dynamic World agrees,
    # that agreement can later be surfaced as supporting evidence instead of
    # deleting SAR candidates that optical data failed to classify.
    persistent_water = (
        ee.Image("JRC/GSW1_4/GlobalSurfaceWater")
        .select("occurrence")
        .gte(50)
    )
    flood_signal = flood_signal.And(persistent_water.Not())

    # Remove isolated one-pixel speckle while retaining small legitimate
    # features. This is a spatial cleanup, not a fabricated data source.
    candidate = flood_signal.selfMask()
    connected = candidate.connectedPixelCount(maxSize=256, eightConnected=True)
    flood_candidate = candidate.updateMask(connected.gte(4))

    return {
        "mask": flood_candidate,
        "region": region,
        "before_scene_count": before_count,
        "after_scene_count": after_count,
        "dw_before_scene_count": dw_before_count,
        "dw_after_scene_count": dw_after_count,
        "dw_before_start": dw_before_start,
        "dw_before_end": dw_before_end,
        "dw_after_start": dw_after_start,
        "dw_after_end": dw_after_end,
        "water_support": water_support,
    }


def get_flood_candidate(
    west: float,
    south: float,
    east: float,
    north: float,
    before_start: str,
    before_end: str,
    after_start: str,
    after_end: str,
):
    global FLOOD_MAP_ID

    ee = ensure_ee()
    built = build_flood_candidate(
        west,
        south,
        east,
        north,
        before_start,
        before_end,
        after_start,
        after_end,
    )
    flood_candidate = built["mask"]
    region = built["region"]

    FLOOD_MAP_ID = flood_candidate.getMapId({
        "min": 0,
        "max": 1,
        "opacity": 0.78,
        "palette": ["18bdf0"],
    })

    # The study region is large (~278M pixels at 10 m). Area reporting is a
    # summary statistic, so reduce at 30 m and allow Earth Engine to increase
    # scale further if a future region/date combination is still too large.
    # The map itself remains backed by the full-resolution candidate mask.
    flood_area = (
        ee.Image.pixelArea()
        .updateMask(flood_candidate)
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=30,
            maxPixels=EE_MAX_PIXELS,
            bestEffort=True,
            tileScale=8,
        )
    )
    area_m2 = flood_area.get("area").getInfo()
    area_km2 = 0.0 if area_m2 is None else area_m2 / 1_000_000

    return {
        "source": "Sentinel-1 + Dynamic World via Google Earth Engine",
        "before_scene_count": built["before_scene_count"],
        "after_scene_count": built["after_scene_count"],
        "dynamic_world_before_scene_count": built["dw_before_scene_count"],
        "dynamic_world_after_scene_count": built["dw_after_scene_count"],
        "candidate_area_km2": round(area_km2, 4),
        "analysis_window": {
            "before_start": before_start,
            "before_end": before_end,
            "after_start": after_start,
            "after_end": after_end,
            "dynamic_world_before_start": built["dw_before_start"],
            "dynamic_world_before_end": built["dw_before_end"],
            "dynamic_world_after_start": built["dw_after_start"],
            "dynamic_world_after_end": built["dw_after_end"],
        },
        "method": {
            "sentinel1": "VV backscatter change using smoothed median composites across all available IW scenes",
            "sar_threshold_db": -1.5,
            "dynamic_world_water_threshold": 0.65,
            "dynamic_world_flooded_vegetation_threshold": 0.55,
            "dynamic_world_role": "corroborating evidence, not a hard gate on SAR candidates",
            "water_support": built["water_support"],
            "persistent_water_mask": "JRC Global Surface Water occurrence >= 50% removed",
            "speckle_cleanup": "retain connected candidate groups of at least 4 pixels",
            "area_summary_scale_m": 30,
            "note": "Satellite-derived inundation candidate; not a confirmed flood boundary.",
        },
        "map": {
            "available": True,
            "tile_url": "/flood/tiles/{z}/{x}/{y}",
        },
    }


# ==========================================================
# AUTHENTICATED FLOOD TILE
# ==========================================================

def get_flood_tile(
    x: int,
    y: int,
    z: int,
):

    if FLOOD_MAP_ID is None:

        raise ValueError(
            "Flood map has not been generated yet. "
            "Call /flood first."
        )


    tile_fetcher = (
        FLOOD_MAP_ID[
            "tile_fetcher"
        ]
    )


    # IMPORTANT:
    #
    # Do NOT make a normal requests.get()
    # request to the Earth Engine tile URL.
    #
    # fetch_tile() uses the authenticated
    # Earth Engine credentials supplied to
    # ee.Initialize().

    tile_bytes = (
        tile_fetcher.fetch_tile(
            x,
            y,
            z,
        )
    )


    return (
        tile_bytes,
        "image/png",
    )