# CycloneShield AI — enhanced real-data build

CycloneShield is a real-data cyclone impact and infrastructure exposure dashboard. The enhanced build keeps the existing Earth Engine / NOAA IBTrACS / Sentinel-1 / Dynamic World / CHIRPS / NASADEM / OpenStreetMap pipeline and adds reliability and situational-awareness features inspired by the public CycloneAI reference architecture.

## Preserved real-data pipeline

- NOAA IBTrACS cyclone track and WMO intensity observations
- Sentinel-1 GRD + Dynamic World satellite-derived flood candidate
- CHIRPS rainfall statistics
- NASADEM terrain statistics
- OpenStreetMap / Overpass infrastructure inventory
- Earth Engine tile rendering for the flood candidate
- Real infrastructure exposure calculation against the satellite-derived candidate

## Added / improved

- **GDACS live cyclone feed**: `/cyclones/live`, filtered to the India / Indian Ocean view
- **GDACS RSS fallback** when the primary API cannot be reached
- **External source status**: `/data-sources/status`
- **Partial-refresh behavior** so one unavailable source does not discard successful results
- **Refresh control** in the UI
- **Printable report** control using the browser print/PDF flow
- Live GDACS cyclone markers and event cards
- All real critical OSM assets displayed on the map; only flood-candidate-nearby assets are highlighted as exposed
- Event-aligned flood analysis with wider Dynamic World fallback windows when a narrow cloud-filtered window has no scenes
- Flood candidate uses Sentinel-1 SAR change plus Dynamic World water/flooded-vegetation support when available, with a real Sentinel-1-only fallback rather than a synthetic image
- Connected-pixel cleanup to reduce isolated SAR speckle
- Intensity-coloured historical Amphan track segments based on real WMO wind observations
- Environment-configurable API URL and CORS origins
- Lazy Earth Engine initialization so the backend can boot, expose health/docs, and run unit tests without an EE credential at import time
- Proper pytest isolation: the existing real-data scripts remain available, while unit/smoke tests live under `backend/tests/`

## Important data interpretation

The flood layer is explicitly a **satellite-derived flood candidate**, not a verified official flood extent. GDACS live cyclone information is a situational-awareness feed. Official IMD/NDMA advisories should be used for operational warnings and emergency decisions.

## Run from Windows CMD

### Backend

```cmd
cd /d "%USERPROFILE%\Desktop\CycloneShield_Professional_Windflow_ZOOMSTABLE_FINAL\backend"
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn main:app --reload --port 8000
```

Set `EARTH_ENGINE_PROJECT` in `backend\.env` and authenticate/configure Google Earth Engine before calling the terrain/flood/exposure endpoints.

### Frontend (second CMD window)

```cmd
cd /d "%USERPROFILE%\Desktop\CycloneShield_Professional_Windflow_ZOOMSTABLE_FINAL\frontend"
npm install
copy .env.example .env
npm run dev
```

The default frontend API is `http://127.0.0.1:8000`; override it with `VITE_API_BASE_URL`.

Open `http://localhost:5173`.

## Tests

```cmd
cd /d "%USERPROFILE%\Desktop\CycloneShield_Professional_Windflow_ZOOMSTABLE_FINAL\backend"
.venv\Scripts\activate
pytest -q
python -m compileall -q .
```

The files named `backend/test_*.py` are retained as manual real-data integration scripts from the original project. They are intentionally excluded from pytest collection by `backend/pytest.ini` because they contact Earth Engine/OSM directly and require external credentials/network access.

## Reference

The upgrade takes architectural inspiration from the public CycloneAI repository, especially its live cyclone feed, data-source status, historical-analysis/reporting direction, and disaster-response-oriented UX, while retaining CycloneShield's existing real-data implementation rather than replacing it with synthetic demo data.

## Analysis notes

The Amphan study is aligned to the documented 20 May 2020 landfall period. Sentinel-1 uses median VV composites across all available IW scenes rather than a single hard-coded relative orbit. Dynamic World is cloud-filtered, so the implementation checks the requested event window and progressively wider real-data windows if no usable scenes exist. When Dynamic World scenes are available, post-event water probability and flooded-vegetation support the SAR change signal; when optical scenes are unavailable, the system falls back to the real SAR candidate instead of crashing or inventing data.

The infrastructure map displays all real critical OSM features (medical, emergency, power, and shelter). The exposure calculation separately highlights only facilities within 250 m of the satellite-derived flood candidate.

Live cyclone ingestion tries the GDACS API first and falls back to the GDACS 7-day RSS feed; a GDACS network outage no longer breaks the rest of the dashboard.


## Visual realism update

The dashboard includes an optional broadcast-style cyclone vortex at the observed peak-intensity center. It uses the real IBTrACS peak wind and pressure as labels and animates a counter-clockwise circulation around that observed center. The vortex is a visualization aid, not a measured wind-vector field or official wind-radius product; IBTrACS position/intensity observations are the underlying evidence.

The flood pipeline is also defensive against empty cloud-filtered Dynamic World windows: it checks scene availability, uses widened real event windows when needed, and combines the result with Sentinel-1 SAR change and a persistent-water mask.


### Meteorological Wind Flow

The map includes a broadcast-style meteorological wind visualization built from the real ECMWF ERA5 10 m U/V field and MSLP, with a bounded, track-aware cyclone intensity envelope derived from the real IBTrACS observed WMO winds along the complete storm track. Animated streamlines show the environmental flow across the full map and are locally bent by the derived cyclone circulation and storm-motion direction. The colored envelope is a visualization aid: it communicates relative storm intensity along the observed path, but it is not presented as a measured wind-radius product.


### Wind Field API
`GET /wind-field` returns a regular ECMWF ERA5 Hourly grid around the historical cyclone peak. The map combines the real ERA5 10 m U/V components and mean sea-level pressure with the real IBTrACS center/track. The browser interpolates the grid to animate continuous flow streaks and draws pressure contours from the returned MSLP values.

## Wind-flow zoom stability

The meteorological wind canvases are attached directly to the Leaflet map container rather than a transform-sensitive custom pane. The flow scene is re-projected on map move/zoom events and throttled during interaction, then rebuilt at full density after movement stops. This prevents the wind field from freezing, drifting, or disappearing after zooming.

## Decision-support features

The Professional build adds a planning-risk layer, parametric coastal surge potential, CHIRPS+terrain rainfall pathways, local critical-asset risk ranking, dispatch-ready early-warning advisory drafts, and a Gemini multimodal reasoning endpoint. These derived outputs are explicitly labeled as planning indicators rather than certified forecasts.

### Gemini

Set `GEMINI_API_KEY` to enable the Gemini reasoning layer. `GEMINI_MODEL` defaults to the hackathon-requested model string (`gemini-3.7-flash`) and can be changed to the model exposed by your Google AI account. `GEMINI_FALLBACK_MODEL` defaults to `gemini-3.8-flash`.

The AI endpoint accepts an optional base64-encoded image so a user can provide a satellite/map image for multimodal evidence review.

### Advisory dispatch

Email dispatch is opt-in. Set SMTP variables and `AUTO_DISPATCH_ENABLED=true` only after configuring a verified recipient list. The dashboard generates drafts first; external sending requires explicit operator action.


## 4.1 stability patch

This build keeps the real-data pipeline and adds a stability/scalability layer: Leaflet zoom/marker transform animation is disabled for deterministic map anchors; wind canvases are hidden during map movement and rebuilt after movement ends; vector asset keys are stable; Earth Engine's `maxPixels` budget is 500,000,000 (5x the previous 100,000,000); and asset-risk Earth Engine sampling is batched into 500-feature requests.
