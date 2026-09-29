"""CycloneShield decision-support intelligence.

All numeric environmental inputs come from the application's real-data
pipeline. Derived scores are explicitly labeled as planning/model outputs.
"""
from __future__ import annotations

import math
import os
import smtplib
import time
from email.message import EmailMessage
from typing import Any

from services.earth_engine import ensure_ee, get_cyclone_track
from services.infrastructure import get_infrastructure

FLOOD_WEST = 87.5
FLOOD_SOUTH = 21.5
FLOOD_EAST = 89.0
FLOOD_NORTH = 23.0
RAINFALL_START = "2020-05-16"
RAINFALL_END = "2020-05-25"
CRITICAL_CATEGORIES = {"medical", "emergency", "power", "shelter", "school", "road", "bridge"}


def _num(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
        return number if math.isfinite(number) else default
    except (TypeError, ValueError):
        return default


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _normalize(value: float, low: float, high: float) -> float:
    if high <= low:
        return 0.0
    return _clamp((value - low) / (high - low), 0.0, 1.0)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0088
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(min(1.0, math.sqrt(a)))


def _valid_track_observations(cyclone: dict) -> list[dict]:
    observations = cyclone.get("observations", []) if isinstance(cyclone, dict) else []
    out = []
    for o in observations:
        if not isinstance(o, dict):
            continue
        lat = _num(o.get("lat"), math.nan)
        lon = _num(o.get("lon"), math.nan)
        if math.isfinite(lat) and math.isfinite(lon):
            out.append(o)
    return out


def _nearest_observation(lat: float, lon: float, observations: list[dict]) -> tuple[dict | None, float]:
    best = None
    best_dist = float("inf")
    for obs in observations:
        d = _haversine_km(lat, lon, _num(obs.get("lat")), _num(obs.get("lon")))
        if d < best_dist:
            best = obs
            best_dist = d
    return best, best_dist


def _sample_image_in_batches(ee, image, points: list, *, properties: list[str],
                             scale: int, tile_scale: int = 8, batch_size: int = 500) -> tuple[list[dict], int]:
    """Sample a real EE image at point features in bounded requests.

    Earth Engine can abort large FeatureCollection aggregations once the
    request accumulates thousands of elements. Batching keeps each request
    comfortably below that limit while preserving the full real dataset.
    """
    samples: list[dict] = []
    failed_batches = 0
    for start in range(0, len(points), max(1, batch_size)):
        batch_points = points[start:start + batch_size]
        try:
            batch = (
                image
                .sampleRegions(
                    ee.FeatureCollection(batch_points),
                    properties=properties,
                    scale=scale,
                    geometries=False,
                    tileScale=tile_scale,
                )
                .getInfo()
                .get("features", [])
            )
            samples.extend(batch)
        except Exception as exc:
            failed_batches += 1
            print(f"ASSET RISK SAMPLE BATCH ERROR ({start // max(1, batch_size) + 1}): {exc}")
    return samples, failed_batches


def build_risk_summary(*, cyclone: dict, flood: dict | None, rainfall: dict | None,
                       terrain: dict | None, exposure: dict | None, surge: dict | None = None) -> dict:
    observations = _valid_track_observations(cyclone)
    winds = [_num(o.get("wmo_wind_kt")) for o in observations if _num(o.get("wmo_wind_kt")) > 0]
    pressures = [_num(o.get("wmo_pressure_mb")) for o in observations if _num(o.get("wmo_pressure_mb")) > 0]
    peak_wind = max(winds) if winds else 0.0
    min_pressure = min(pressures) if pressures else None
    rain_max = _num((rainfall or {}).get("rainfall_max_mm"))
    flood_area = _num((flood or {}).get("candidate_area_km2"))
    nearby = int(_num((exposure or {}).get("nearby_exposed_count")))
    critical = int(_num((exposure or {}).get("total_critical")))
    mean_elev = _num((terrain or {}).get("elevation_mean_m"), 50)
    surge_max = _num((surge or {}).get("max_surge_potential_m"))

    wind_score = _normalize(peak_wind, 35, 140) * 100
    rain_score = _normalize(rain_max, 60, 350) * 100
    flood_score = _normalize(flood_area, 20, 800) * 100
    exposure_score = (nearby / max(1, critical)) * 100 * 18.0
    terrain_score = _clamp((40.0 - mean_elev) / 40.0, 0, 1) * 100
    surge_score = _normalize(surge_max, 0.3, 3.5) * 100 if surge else 0

    score = (
        wind_score * 0.27
        + rain_score * 0.18
        + flood_score * 0.18
        + exposure_score * 0.17
        + terrain_score * 0.06
        + surge_score * 0.14
    )
    score = round(_clamp(score, 0, 100), 1)
    if score >= 80:
        band = "EXTREME"
    elif score >= 65:
        band = "HIGH"
    elif score >= 45:
        band = "ELEVATED"
    else:
        band = "MODERATE"

    return {
        "model": "CycloneShield Planning Risk v1 (derived)",
        "risk_score": score,
        "risk_band": band,
        "inputs": {
            "peak_wmo_wind_kt": peak_wind,
            "minimum_wmo_pressure_mb": min_pressure,
            "rainfall_max_mm": rain_max,
            "flood_candidate_area_km2": flood_area,
            "critical_assets": critical,
            "nearby_candidate_exposed_assets": nearby,
            "mean_elevation_m": mean_elev,
            "max_parametric_surge_m": surge_max,
        },
        "drivers": [
            {"name": "Wind hazard", "score": round(wind_score, 1), "weight": 0.27},
            {"name": "Rainfall loading", "score": round(rain_score, 1), "weight": 0.18},
            {"name": "Flood candidate", "score": round(flood_score, 1), "weight": 0.18},
            {"name": "Infrastructure exposure", "score": round(_clamp(exposure_score, 0, 100), 1), "weight": 0.17},
            {"name": "Low-elevation sensitivity", "score": round(terrain_score, 1), "weight": 0.06},
            {"name": "Storm-surge potential", "score": round(surge_score, 1), "weight": 0.14},
        ],
        "planning_note": "Derived planning indicator from real observations/products; not a certified forecast or emergency warning model.",
    }


def project_storm_scenario(cyclone: dict, lead_hours: int = 12) -> dict:
    observations = _valid_track_observations(cyclone)
    if not observations:
        return {"available": False, "reason": "No cyclone observations available."}
    recent = observations[-1]
    wind = _num(recent.get("wmo_wind_kt"))
    direction = _num(recent.get("storm_direction_deg"), 0)
    speed_kt = _num(recent.get("storm_speed_kt"))
    lat = _num(recent.get("lat"))
    lon = _num(recent.get("lon"))
    lead_hours = int(_clamp(lead_hours, 1, 48))
    distance_km = speed_kt * 1.852 * lead_hours
    heading = math.radians(direction)
    dlat = (distance_km * math.cos(heading)) / 111.32
    denom = max(0.1, 111.32 * math.cos(math.radians(lat)))
    dlon = (distance_km * math.sin(heading)) / denom
    scenario_wind = max(35.0, wind * math.exp(-lead_hours / 72.0))
    return {
        "available": True,
        "lead_hours": lead_hours,
        "current_position": {"lat": lat, "lon": lon},
        "projected_position": {"lat": round(lat + dlat, 4), "lon": round(lon + dlon, 4)},
        "storm_motion_kt": speed_kt,
        "storm_direction_deg": direction,
        "scenario_wind_kt": round(scenario_wind, 1),
        "note": "Planning scenario based on the most recent observed motion/intensity; not a meteorological forecast track.",
    }


def get_surge_grid(*, sid: str, west: float = FLOOD_WEST, south: float = FLOOD_SOUTH,
                   east: float = FLOOD_EAST, north: float = FLOOD_NORTH,
                   step_deg: float = 0.05) -> dict:
    ee = ensure_ee()
    cyclone = get_cyclone_track(sid)
    observations = _valid_track_observations(cyclone)
    if not observations:
        raise ValueError("No cyclone observations available for surge simulation.")

    peak = max(observations, key=lambda o: _num(o.get("wmo_wind_kt")))
    points = []
    point_props = []
    i = 0
    j = 0
    lat = south
    while lat <= north + 1e-9:
        lon = west
        i = 0
        while lon <= east + 1e-9:
            props = {"i": i, "j": j, "lat": lat, "lon": lon}
            points.append(ee.Feature(ee.Geometry.Point([lon, lat]), props))
            point_props.append(props)
            i += 1
            lon += step_deg
        j += 1
        lat += step_deg

    fc = ee.FeatureCollection(points)
    dem = ee.Image("NASA/NASADEM_HGT/001").select("elevation")
    water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")
    dem_samples = dem.sampleRegions(fc, properties=["i", "j", "lat", "lon"], scale=90, geometries=False, tileScale=4).getInfo().get("features", [])
    water_samples = water.sampleRegions(fc, properties=["i", "j", "lat", "lon"], scale=1000, geometries=False, tileScale=4).getInfo().get("features", [])

    dem_by_key = {}
    water_by_key = {}
    for f in dem_samples:
        p = f.get("properties", {})
        dem_by_key[(int(p.get("i", -1)), int(p.get("j", -1)))] = _num(p.get("elevation"))
    for f in water_samples:
        p = f.get("properties", {})
        water_by_key[(int(p.get("i", -1)), int(p.get("j", -1)))] = _num(p.get("occurrence"))

    raw = []
    for p in point_props:
        key = (int(p["i"]), int(p["j"]))
        elev = dem_by_key.get(key, 0.0)
        water_occ = water_by_key.get(key, 0.0)
        lat0 = _num(p["lat"])
        lon0 = _num(p["lon"])
        nearest, dist = _nearest_observation(lat0, lon0, observations)
        wind = _num((nearest or peak).get("wmo_wind_kt"))
        pressure = _num((nearest or peak).get("wmo_pressure_mb"), 1013)
        storm_factor = math.exp(-((dist / 520.0) ** 2))
        lowland_factor = math.exp(-max(elev, 0.0) / 30.0)
        coast_factor = 1.0 if water_occ >= 35 else 0.55
        # Small coastal smoothing: a nearby water cell within the grid increases relevance.
        nearby_water = False
        for di, dj in ((1,0),(-1,0),(0,1),(0,-1)):
            if water_by_key.get((key[0] + di, key[1] + dj), 0) >= 35:
                nearby_water = True
                break
        if nearby_water:
            coast_factor = max(coast_factor, 0.85)
        pressure_deficit = max(0.0, 1013.0 - pressure)
        inverse_barometer = 0.01 * pressure_deficit * storm_factor * coast_factor * lowland_factor
        wind_setup = 0.018 * max(0.0, wind - 35.0) * storm_factor * coast_factor * lowland_factor
        surge = _clamp(inverse_barometer + wind_setup, 0.0, 5.0)
        raw.append({
            "lat": round(lat0, 4), "lon": round(lon0, 4), "elevation_m": round(elev, 1),
            "water_occurrence_pct": round(water_occ, 1), "distance_to_storm_km": round(dist, 1),
            "wind_proxy_kt": round(wind, 1), "pressure_proxy_mb": round(pressure, 1),
            "surge_potential_m": round(surge, 2),
        })

    def surge_class(value: float) -> str:
        if value >= 2.5: return "severe"
        if value >= 1.5: return "high"
        if value >= 0.7: return "moderate"
        return "low"

    for item in raw:
        item["class"] = surge_class(item["surge_potential_m"])
    hotspots = sorted(raw, key=lambda item: item["surge_potential_m"], reverse=True)[:30]
    max_surge = max((r["surge_potential_m"] for r in raw), default=0.0)

    return {
        "source": "NASADEM + JRC Global Surface Water + IBTrACS",
        "model": "Parametric coastal surge potential v1",
        "bbox": {"west": west, "south": south, "east": east, "north": north},
        "step_deg": step_deg,
        "peak_observation": {"lat": _num(peak.get("lat")), "lon": _num(peak.get("lon")), "wind_kt": _num(peak.get("wmo_wind_kt")), "pressure_mb": _num(peak.get("wmo_pressure_mb"))},
        "max_surge_potential_m": round(max_surge, 2),
        "hotspots": hotspots,
        "grid": raw,
        "note": "Derived coastal surge potential for planning. Not a hydrodynamic ocean model and not an official inundation forecast.",
    }


def get_rainfall_pathways(*, west: float = FLOOD_WEST, south: float = FLOOD_SOUTH,
                          east: float = FLOOD_EAST, north: float = FLOOD_NORTH,
                          start: str = RAINFALL_START, end: str = RAINFALL_END,
                          step_deg: float = 0.08) -> dict:
    ee = ensure_ee()
    points = []
    point_props = []
    i = 0
    j = 0
    lat = south
    while lat <= north + 1e-9:
        lon = west
        i = 0
        while lon <= east + 1e-9:
            props = {"i": i, "j": j, "lat": lat, "lon": lon}
            points.append(ee.Feature(ee.Geometry.Point([lon, lat]), props))
            point_props.append(props)
            i += 1
            lon += step_deg
        j += 1
        lat += step_deg
    fc = ee.FeatureCollection(points)
    rainfall = (ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").filterDate(start, end).filterBounds(ee.Geometry.Rectangle([west, south, east, north])).select("precipitation").sum())
    dem = ee.Image("NASA/NASADEM_HGT/001").select("elevation")
    slope = ee.Terrain.slope(dem)
    rain_samples = rainfall.sampleRegions(fc, properties=["i", "j", "lat", "lon"], scale=6000, geometries=False, tileScale=4).getInfo().get("features", [])
    terrain_samples = dem.addBands(slope.rename("slope_deg")).sampleRegions(fc, properties=["i", "j", "lat", "lon"], scale=90, geometries=False, tileScale=4).getInfo().get("features", [])
    rain_by_key = {}
    terrain_by_key = {}
    for f in rain_samples:
        p = f.get("properties", {}); rain_by_key[(int(p.get("i", -1)), int(p.get("j", -1)))] = _num(p.get("precipitation"))
    for f in terrain_samples:
        p = f.get("properties", {}); terrain_by_key[(int(p.get("i", -1)), int(p.get("j", -1)))] = (_num(p.get("elevation")), _num(p.get("slope_deg")))

    grid = []
    for p in point_props:
        key = (int(p["i"]), int(p["j"]))
        rain = rain_by_key.get(key, 0.0); elev, slope_deg = terrain_by_key.get(key, (0.0, 0.0))
        rain_norm = _normalize(rain, 50, 300)
        lowland = math.exp(-max(elev, 0.0) / 35.0)
        wetness = _clamp(rain_norm * 0.7 + lowland * 0.3, 0, 1)
        if rain >= 160 and elev <= 25:
            pathway = "surface-water accumulation"
        elif rain >= 140 and slope_deg <= 5:
            pathway = "road-access disruption"
        elif rain >= 120 and slope_deg >= 12:
            pathway = "slope-instability watch"
        else:
            pathway = "rainfall loading"
        grid.append({
            "lat": round(_num(p["lat"]), 4), "lon": round(_num(p["lon"]), 4),
            "rainfall_mm": round(rain, 1), "elevation_m": round(elev, 1),
            "slope_deg": round(slope_deg, 1), "pathway_score": round(wetness * 100, 1),
            "pathway": pathway,
        })
    hotspots = sorted(grid, key=lambda x: x["pathway_score"], reverse=True)[:25]
    return {
        "source": "CHIRPS Daily + NASADEM via Google Earth Engine",
        "window": {"start": start, "end": end},
        "hotspots": hotspots,
        "grid": grid,
        "note": "Derived local impact pathway indicator linking observed rainfall loading to terrain context; not a calibrated runoff model.",
    }


def get_asset_risk_watchlist(*, sid: str) -> dict:
    ee = ensure_ee()
    cyclone = get_cyclone_track(sid)
    observations = _valid_track_observations(cyclone)
    infra = get_infrastructure(FLOOD_WEST, FLOOD_SOUTH, FLOOD_EAST, FLOOD_NORTH)
    features = infra.get("features", []) if isinstance(infra, dict) else []
    # Real event-wide rainfall and terrain context, sampled at asset points.
    points = []
    cleaned = []
    for idx, feature in enumerate(features):
        category = str(feature.get("category", "")).lower()
        if category not in CRITICAL_CATEGORIES:
            continue
        lat = _num(feature.get("latitude"), math.nan)
        lon = _num(feature.get("longitude"), math.nan)
        if not (math.isfinite(lat) and math.isfinite(lon)):
            continue
        cleaned.append((feature, lat, lon, idx))
        points.append(ee.Feature(ee.Geometry.Point([lon, lat]), {"asset_i": idx, "lat": lat, "lon": lon}))
    if not points:
        return {"model": "CycloneShield Asset Risk v1 (derived)", "assets": [], "top": []}
    rain = (ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").filterDate(RAINFALL_START, RAINFALL_END).select("precipitation").sum())
    dem = ee.Image("NASA/NASADEM_HGT/001").select("elevation")
    context_image = rain.addBands(dem.rename("elevation_m"))

    # Earth Engine can abort a large FeatureCollection request after ~5000
    # accumulated elements. Keep each request comfortably below that limit
    # and combine the real samples client-side. This also handles datasets
    # that contain many arterial-road features without dropping them.
    samples, failed_batches = _sample_image_in_batches(
        ee,
        context_image,
        points,
        properties=["asset_i", "lat", "lon"],
        scale=6000,
        tile_scale=8,
        batch_size=500,
    )
    sample_by_idx = {int(f.get("properties", {}).get("asset_i", -1)): f.get("properties", {}) for f in samples}

    results = []
    for feature, lat, lon, idx in cleaned:
        nearest, dist = _nearest_observation(lat, lon, observations)
        peak_wind = _num((nearest or {}).get("wmo_wind_kt"))
        local_rain = _num(sample_by_idx.get(idx, {}).get("precipitation"))
        elev = _num(sample_by_idx.get(idx, {}).get("elevation_m"))
        wind_proxy = 0.0 if dist == float("inf") else peak_wind * math.exp(-((dist / 220.0) ** 2))
        category = str(feature.get("category", "unknown")).lower()
        sensitivity = {"medical": 1.0, "emergency": 0.95, "power": 0.95, "shelter": 0.85, "road": 0.8, "bridge": 0.9, "school": 0.7}.get(category, 0.65)
        score = 100 * (0.48 * _normalize(wind_proxy, 35, 130) + 0.28 * _normalize(local_rain, 60, 300) + 0.14 * _clamp(math.exp(-max(elev, 0) / 30), 0, 1) + 0.10 * sensitivity)
        results.append({
            "name": feature.get("name") or "Unnamed facility",
            "category": category,
            "latitude": lat, "longitude": lon,
            "wind_proxy_kt": round(wind_proxy, 1),
            "rainfall_mm": round(local_rain, 1),
            "elevation_m": round(elev, 1),
            "distance_to_track_km": round(dist, 1),
            "risk_score": round(_clamp(score, 0, 100), 1),
            "risk_band": "EXTREME" if score >= 80 else "HIGH" if score >= 65 else "ELEVATED" if score >= 45 else "MODERATE",
            "source": "OSM + IBTrACS + CHIRPS + NASADEM",
        })
    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return {
        "model": "CycloneShield Asset Risk v1 (derived)",
        "count": len(results),
        "sampled_asset_count": len(sample_by_idx),
        "failed_sample_batches": failed_batches,
        "top": results[:40],
        "note": "Local asset risk is a planning model using real datasets; not a certified engineering assessment.",
    }


def generate_advisories(*, risk: dict, watchlist: dict | None = None, surge: dict | None = None,
                        pathways: dict | None = None) -> dict:
    score = _num(risk.get("risk_score"))
    band = str(risk.get("risk_band", "MODERATE"))
    top_assets = (watchlist or {}).get("top", [])[:8]
    surge_max = _num((surge or {}).get("max_surge_potential_m"))
    pathway_hotspots = (pathways or {}).get("hotspots", [])[:5]
    asset_counts = {}
    for asset in top_assets:
        asset_counts[asset.get("category", "other")] = asset_counts.get(asset.get("category", "other"), 0) + 1
    common = "Prepare pre-landfall protective actions and verify readiness of critical facilities."
    advisory_list = [
        {
            "id": "municipal-control-room",
            "priority": "CRITICAL" if score >= 75 else "HIGH" if score >= 60 else "WATCH",
            "audience": "Municipal / disaster management control room",
            "subject": f"CycloneShield early-warning advisory — risk {band}",
            "message": f"CycloneShield planning risk is {round(score,1)}/100 ({band}). {common} Review exposed infrastructure, rainfall pathways and surge-potential hotspots before the next operational window.",
        },
        {
            "id": "health-facilities",
            "priority": "HIGH" if asset_counts.get("medical", 0) else "WATCH",
            "audience": "Health / hospital coordination",
            "subject": "Critical medical-facility readiness advisory",
            "message": f"Top asset watchlist includes {asset_counts.get('medical',0)} medical facilities. Confirm emergency staffing, backup power, water, transport access and patient relocation procedures.",
        },
        {
            "id": "power-network",
            "priority": "HIGH" if asset_counts.get("power", 0) else "WATCH",
            "audience": "Power utility / grid operations",
            "subject": "Power infrastructure hardening advisory",
            "message": f"Top asset watchlist includes {asset_counts.get('power',0)} power assets. Pre-stage crews, inspect vulnerable feeders, and verify backup generation and isolation procedures.",
        },
        {
            "id": "roads-shelters",
            "priority": "HIGH" if pathway_hotspots else "WATCH",
            "audience": "Roads, transport and shelter coordination",
            "subject": "Access and shelter readiness advisory",
            "message": f"The pathway model identified {len(pathway_hotspots)} priority rainfall/terrain hotspots. Review vulnerable access routes and confirm shelter accessibility before peak conditions.",
        },
    ]
    return {
        "generated_by": "CycloneShield rule-based advisory engine",
        "dispatch_ready": True,
        "risk_band": band,
        "surge_potential_m": surge_max,
        "advisories": advisory_list,
        "smtp_configured": bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_USERNAME") and os.getenv("SMTP_PASSWORD")),
        "auto_dispatch_enabled": os.getenv("AUTO_DISPATCH_ENABLED", "false").lower() == "true",
        "note": "Advisories are planning drafts generated from current real-data/derived indicators; human authorization is required before external dispatch.",
    }


def dispatch_advisories(advisories: list[dict], recipients: list[str] | None = None) -> dict:
    if os.getenv("AUTO_DISPATCH_ENABLED", "false").lower() != "true":
        raise RuntimeError("AUTO_DISPATCH_ENABLED is false. Enable it explicitly before dispatch.")
    host = os.getenv("SMTP_HOST")
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("ALERT_FROM") or username
    if not host or not username or not password or not sender:
        raise RuntimeError("SMTP configuration is incomplete.")
    env_recipients = [x.strip() for x in os.getenv("ALERT_RECIPIENTS", "").split(",") if x.strip()]
    targets = list(dict.fromkeys((recipients or []) + env_recipients))
    if not targets:
        raise RuntimeError("No advisory recipients configured.")
    sent = []
    with smtplib.SMTP_SSL(host, int(os.getenv("SMTP_PORT", "465"))) as server:
        server.login(username, password)
        for advisory in advisories:
            message = EmailMessage()
            message["From"] = sender
            message["To"] = ", ".join(targets)
            message["Subject"] = advisory.get("subject", "CycloneShield advisory")
            message.set_content(advisory.get("message", "CycloneShield advisory"))
            server.send_message(message)
            sent.append(advisory.get("id"))
    return {"sent": sent, "recipients": targets, "count": len(sent)}


def gemini_status() -> dict:
    extra = [
        m.strip()
        for m in os.getenv("GEMINI_RETRY_MODELS", "gemini-3.6-flash,gemini-3.5-flash-lite").split(",")
        if m.strip()
    ]
    return {
        "configured": bool(os.getenv("GEMINI_API_KEY")),
        "model": os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        "fallback_model": os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.7-flash"),
        "retry_models": extra,
        "multimodal": True,
        "automatic_retry": True,
        "max_retries_per_model": 2,
    }


def _gemini_error_text(response: Any) -> str:
    """Return a compact, non-secret Gemini API error description."""
    try:
        data = response.json()
        error = data.get("error", {}) if isinstance(data, dict) else {}
        code = error.get("code", response.status_code)
        status = error.get("status")
        message = error.get("message") or response.reason or "Gemini request failed."
        bits = [str(code)]
        if status:
            bits.append(str(status))
        bits.append(str(message))
        return ": ".join(bits[:2]) + (f" — {bits[2]}" if len(bits) > 2 else "")
    except Exception:
        return f"{response.status_code} {response.reason or 'Gemini request failed.'}".strip()


def _is_retryable_gemini_status(status_code: int) -> bool:
    return status_code in {408, 429, 500, 502, 503, 504}


def generate_gemini_brief(context: dict, image_base64: str | None = None, mime_type: str = "image/png") -> dict:
    import requests

    api_key = os.getenv("GEMINI_API_KEY")
    primary = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
    fallback = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.7-flash").strip()
    extra_models = [
        m.strip()
        for m in os.getenv("GEMINI_RETRY_MODELS", "gemini-3.6-flash,gemini-3.5-flash-lite").split(",")
        if m.strip()
    ]
    models: list[str] = []
    for model in [primary, fallback, *extra_models]:
        if model and model not in models:
            models.append(model)

    prompt = (
        "You are CycloneShield's disaster-risk reasoning assistant. Use the supplied real-data context "
        "and optional map/satellite image. Produce a concise operational brief with: situation, key evidence, "
        "highest-risk hazards, infrastructure implications, 0-6h/6-24h priorities, uncertainty/limitations. "
        "Do not invent observations, coordinates, forecast certainty, or official warnings. Clearly mark derived "
        "planning metrics as derived.\n\nCONTEXT:\n" + str(context)
    )
    if not api_key:
        risk = context.get("risk", {}) if isinstance(context, dict) else {}
        return {
            "available": False,
            "mode": "local-fallback",
            "model": None,
            "attempts": 0,
            "retryable": False,
            "text": (
                f"CycloneShield planning brief: risk {risk.get('risk_score','—')}/100 ({risk.get('risk_band','—')}). "
                "Primary drivers are the observed cyclone intensity, rainfall loading, satellite-derived flood candidate, "
                "and critical-infrastructure exposure. Use the map and asset watchlist to prioritize readiness actions. "
                "Gemini is not configured; this summary was generated locally from the structured evidence."
            ),
            "image_used": bool(image_base64),
        }

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }
    parts = [{"text": prompt}]
    if image_base64:
        parts.append({"inline_data": {"mime_type": mime_type, "data": image_base64}})
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 900},
    }

    last_error = None
    total_attempts = 0
    had_retryable_error = False
    for model_index, model in enumerate(models):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        for attempt in range(3):
            total_attempts += 1
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                if _is_retryable_gemini_status(response.status_code):
                    had_retryable_error = True
                    last_error = _gemini_error_text(response)
                    if attempt < 2:
                        retry_after = response.headers.get("Retry-After")
                        try:
                            delay = min(max(float(retry_after), 1.0), 8.0) if retry_after else (2 ** attempt)
                        except (TypeError, ValueError):
                            delay = 2 ** attempt
                        time.sleep(delay)
                        continue
                    break
                response.raise_for_status()
                data = response.json()
                text_parts = []
                for candidate in data.get("candidates", []):
                    for part in (candidate.get("content", {}).get("parts", []) or []):
                        if part.get("text"):
                            text_parts.append(part["text"])
                text = "\n".join(text_parts).strip()
                if text:
                    return {
                        "available": True,
                        "mode": "gemini",
                        "model": model,
                        "text": text,
                        "image_used": bool(image_base64),
                        "attempts": total_attempts,
                        "retryable": had_retryable_error,
                    }
                last_error = "Gemini returned no text."
                break
            except requests.RequestException as exc:
                last_error = str(exc)
                # Network timeouts/connection resets are worth retrying, but do not loop forever.
                if attempt < 2:
                    had_retryable_error = True
                    time.sleep(2 ** attempt)
                    continue
                break
            except Exception as exc:
                last_error = str(exc)
                break

    return {
        "available": False,
        "mode": "local-fallback",
        "model": None,
        "error": last_error,
        "attempts": total_attempts,
        "retryable": had_retryable_error,
        "text": (
            "Gemini is temporarily unavailable after automatic retries. "
            "Use the structured risk, surge, rainfall and asset panels while the external model is unavailable."
        ),
        "image_used": bool(image_base64),
    }

