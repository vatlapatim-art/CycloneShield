import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from services.earth_engine import (
    get_elevation_stats,
    get_rainfall_stats,
    get_cyclone_track,
    get_flood_candidate,
    get_flood_tile,
    get_era5_wind_field,
)

from services.infrastructure import (
    get_infrastructure,
)

from services.exposure import (
    calculate_real_exposure,
)
from services.live_cyclones import get_live_cyclones
from services.source_status import get_source_status
from services.intelligence import (
    build_risk_summary,
    project_storm_scenario,
    get_surge_grid,
    get_rainfall_pathways,
    get_asset_risk_watchlist,
    generate_advisories,
    dispatch_advisories,
    gemini_status,
    generate_gemini_brief,
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="CycloneShield AI",
    description=(
        "Real-data cyclone impact and "
        "infrastructure exposure analysis"
    ),
    version="4.1.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REAL FLOOD / EXPOSURE STUDY REGION
# ============================================================

FLOOD_WEST = 87.5
FLOOD_SOUTH = 21.5
FLOOD_EAST = 89.0
FLOOD_NORTH = 23.0


# ============================================================
# REAL CYCLONE
# ============================================================

CYCLONE_SID = "2020136N10088"


# ============================================================
# REAL FLOOD ANALYSIS DATES
# ============================================================

FLOOD_BEFORE_START = "2020-05-16T00:00:00"
FLOOD_BEFORE_END = "2020-05-20T00:00:00"

FLOOD_AFTER_START = "2020-05-20T00:00:00"
FLOOD_AFTER_END = "2020-05-24T00:00:00"


# ============================================================
# REAL CHIRPS RAINFALL DATES
# ============================================================

RAINFALL_START = "2020-05-16"
RAINFALL_END = "2020-05-25"


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "name": "CycloneShield AI",
        "status": "online",
        "data_policy": "real_data_only",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "CycloneShield AI API",
    }


# ============================================================
# TERRAIN
# ============================================================

@app.get("/terrain")
def terrain():

    try:

        return get_elevation_stats(
            FLOOD_WEST,
            FLOOD_SOUTH,
            FLOOD_EAST,
            FLOOD_NORTH,
        )

    except Exception as e:

        print(
            f"TERRAIN ERROR: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# RAINFALL
# ============================================================

@app.get("/rainfall")
def rainfall():

    try:

        return get_rainfall_stats(
            FLOOD_WEST,
            FLOOD_SOUTH,
            FLOOD_EAST,
            FLOOD_NORTH,
            RAINFALL_START,
            RAINFALL_END,
        )

    except Exception as e:

        print(
            f"RAINFALL ERROR: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# CYCLONE TRACK
# ============================================================

@app.get("/cyclone/{sid}")
def cyclone(
    sid: str
):

    try:

        return get_cyclone_track(
            sid
        )

    except Exception as e:

        print(
            f"CYCLONE ERROR: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# LIVE CYCLONE FEED (GDACS)
# ============================================================

@app.get("/cyclones/live")
def live_cyclones():
    try:
        return get_live_cyclones()
    except Exception as e:
        print(f"LIVE CYCLONES ERROR: {e}")
        raise HTTPException(status_code=502, detail=f"Live GDACS feed unavailable: {e}")


# ============================================================
# REAL METEOROLOGICAL WIND FIELD
# ============================================================

@app.get("/wind-field")
def wind_field():
    try:
        return get_era5_wind_field(
            CYCLONE_SID,
            west=65.0,
            south=5.0,
            east=105.0,
            north=32.0,
            step_deg=0.75,
        )
    except Exception as e:
        print(f"WIND FIELD ERROR: {e}")
        raise HTTPException(status_code=502, detail=str(e))


# ============================================================
# DATA-SOURCE STATUS
# ============================================================

@app.get("/data-sources/status")
def data_sources_status():
    try:
        return get_source_status()
    except Exception as e:
        print(f"SOURCE STATUS ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# FLOOD CANDIDATE
# ============================================================

@app.get("/flood")
def flood():

    try:

        return get_flood_candidate(
            FLOOD_WEST,
            FLOOD_SOUTH,
            FLOOD_EAST,
            FLOOD_NORTH,
            FLOOD_BEFORE_START,
            FLOOD_BEFORE_END,
            FLOOD_AFTER_START,
            FLOOD_AFTER_END,
        )

    except Exception as e:

        print(
            f"FLOOD ERROR: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# FLOOD MAP TILES
# ============================================================

@app.get(
    "/flood/tiles/{z}/{x}/{y}"
)
def flood_tile(
    z: int,
    x: int,
    y: int,
):

    try:

        content, content_type = get_flood_tile(
            x,
            y,
            z,
        )

        return Response(
            content=content,
            media_type=content_type,
            headers={
                "Cache-Control":
                "public, max-age=3600"
            },
        )

    except Exception as e:

        print(
            f"FLOOD TILE ERROR: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# REAL OSM INFRASTRUCTURE
# ============================================================

@app.get("/infrastructure")
def infrastructure():

    try:

        return get_infrastructure(
            FLOOD_WEST,
            FLOOD_SOUTH,
            FLOOD_EAST,
            FLOOD_NORTH,
        )

    except Exception as e:

        print(
            f"INFRASTRUCTURE ERROR: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# REAL INFRASTRUCTURE EXPOSURE
# ============================================================

@app.get("/exposure")
def exposure():

    try:

        infrastructure_data = (
            get_infrastructure(
                FLOOD_WEST,
                FLOOD_SOUTH,
                FLOOD_EAST,
                FLOOD_NORTH,
            )
        )

        result = calculate_real_exposure(
            infrastructure_data
        )

        return result

    except Exception as e:

        print(
            f"EXPOSURE ERROR: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )



# ============================================================
# DECISION-SUPPORT INTELLIGENCE
# ============================================================

@app.get("/risk/summary")
def risk_summary():
    try:
        cyclone_data = get_cyclone_track(CYCLONE_SID)
        flood_data = get_flood_candidate(FLOOD_WEST, FLOOD_SOUTH, FLOOD_EAST, FLOOD_NORTH, FLOOD_BEFORE_START, FLOOD_BEFORE_END, FLOOD_AFTER_START, FLOOD_AFTER_END)
        terrain_data = get_elevation_stats(FLOOD_WEST, FLOOD_SOUTH, FLOOD_EAST, FLOOD_NORTH)
        rainfall_data = get_rainfall_stats(FLOOD_WEST, FLOOD_SOUTH, FLOOD_EAST, FLOOD_NORTH, RAINFALL_START, RAINFALL_END)
        infrastructure_data = get_infrastructure(FLOOD_WEST, FLOOD_SOUTH, FLOOD_EAST, FLOOD_NORTH)
        exposure_data = calculate_real_exposure(infrastructure_data)
        return build_risk_summary(cyclone=cyclone_data, flood=flood_data, rainfall=rainfall_data, terrain=terrain_data, exposure=exposure_data)
    except Exception as e:
        print(f"RISK SUMMARY ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/risk/scenario")
def risk_scenario(lead_hours: int = 12):
    try:
        return project_storm_scenario(get_cyclone_track(CYCLONE_SID), lead_hours=lead_hours)
    except Exception as e:
        print(f"RISK SCENARIO ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/surge/grid")
def surge_grid():
    try:
        return get_surge_grid(sid=CYCLONE_SID)
    except Exception as e:
        print(f"SURGE ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rainfall/pathways")
def rainfall_pathways():
    try:
        return get_rainfall_pathways()
    except Exception as e:
        print(f"PATHWAY ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/risk/assets")
def risk_assets():
    try:
        return get_asset_risk_watchlist(sid=CYCLONE_SID)
    except Exception as e:
        print(f"ASSET RISK ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/advisories")
def advisories():
    try:
        cyclone_data = get_cyclone_track(CYCLONE_SID)
        flood_data = get_flood_candidate(FLOOD_WEST, FLOOD_SOUTH, FLOOD_EAST, FLOOD_NORTH, FLOOD_BEFORE_START, FLOOD_BEFORE_END, FLOOD_AFTER_START, FLOOD_AFTER_END)
        terrain_data = get_elevation_stats(FLOOD_WEST, FLOOD_SOUTH, FLOOD_EAST, FLOOD_NORTH)
        rainfall_data = get_rainfall_stats(FLOOD_WEST, FLOOD_SOUTH, FLOOD_EAST, FLOOD_NORTH, RAINFALL_START, RAINFALL_END)
        infrastructure_data = get_infrastructure(FLOOD_WEST, FLOOD_SOUTH, FLOOD_EAST, FLOOD_NORTH)
        exposure_data = calculate_real_exposure(infrastructure_data)
        risk = build_risk_summary(cyclone=cyclone_data, flood=flood_data, rainfall=rainfall_data, terrain=terrain_data, exposure=exposure_data)
        return generate_advisories(risk=risk)
    except Exception as e:
        print(f"ADVISORY ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/advisories/status")
def advisories_status():
    return {
        "smtp_configured": bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_USERNAME") and os.getenv("SMTP_PASSWORD")),
        "auto_dispatch_enabled": os.getenv("AUTO_DISPATCH_ENABLED", "false").lower() == "true",
    }


@app.post("/advisories/dispatch")
def advisories_dispatch(payload: dict):
    try:
        return dispatch_advisories(payload.get("advisories", []), payload.get("recipients", []))
    except Exception as e:
        print(f"ADVISORY DISPATCH ERROR: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/ai/status")
def ai_status():
    return gemini_status()


@app.post("/ai/brief")
def ai_brief(payload: dict):
    try:
        context = payload.get("context") if isinstance(payload, dict) else {}
        image_base64 = payload.get("image_base64") if isinstance(payload, dict) else None
        mime_type = payload.get("mime_type", "image/png") if isinstance(payload, dict) else "image/png"
        return generate_gemini_brief(context or {}, image_base64=image_base64, mime_type=mime_type)
    except Exception as e:
        print(f"AI BRIEF ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# PAYLOAD-DRIVEN DECISION SUPPORT (FRONTEND USE)
# ============================================================

@app.post("/risk/summary")
def risk_summary_from_payload(payload: dict):
    try:
        return build_risk_summary(
            cyclone=payload.get("cyclone") or {},
            flood=payload.get("flood"),
            rainfall=payload.get("rainfall"),
            terrain=payload.get("terrain"),
            exposure=payload.get("exposure"),
        )
    except Exception as e:
        print(f"RISK SUMMARY PAYLOAD ERROR: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/advisories/generate")
def advisories_from_payload(payload: dict):
    try:
        risk = build_risk_summary(
            cyclone=payload.get("cyclone") or {},
            flood=payload.get("flood"),
            rainfall=payload.get("rainfall"),
            terrain=payload.get("terrain"),
            exposure=payload.get("exposure"),
        )
        return generate_advisories(risk=risk)
    except Exception as e:
        print(f"ADVISORY PAYLOAD ERROR: {e}")
        raise HTTPException(status_code=400, detail=str(e))
