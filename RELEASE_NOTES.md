# CycloneShield Professional — Hackathon Full Upgrade

## Added
- Real ERA5 10 m U/V + MSLP meteorological field retained and improved in the UI.
- Full-storm timeline/replay control using the real IBTrACS observation sequence.
- Map wind probe for local ERA5 speed/direction/pressure samples.
- Parametric coastal storm-surge potential using IBTrACS intensity/pressure plus NASADEM/JRC context.
- CHIRPS + NASADEM rainfall-to-damage pathway hotspots.
- Real-data critical asset risk watchlist using OSM + IBTrACS + CHIRPS + NASADEM.
- Planning risk score and driver breakdown.
- Dispatch-ready early-warning advisory drafts for municipal, health, power and transport/shelter teams.
- Optional SMTP dispatch with explicit opt-in (`AUTO_DISPATCH_ENABLED=false` by default).
- Gemini multimodal reasoning endpoint with optional image evidence and configurable model/fallback.
- AI command center UI with scenario analysis, AI brief, advisories, surge/pathways and asset watchlist.
- Map overlays for surge hotspots, rainfall pathways and high-risk assets.
- Existing real-data flood, terrain, rainfall, cyclone, OSM and GDACS features preserved.

## Data and honesty policy
Observed data remain labeled as observed (IBTrACS / ERA5 / CHIRPS / GEE / OSM / GDACS). Derived risk, surge and pathway outputs are labeled planning/model outputs and are not presented as certified forecasts or emergency warnings.


## Stability / scalability patch

- Increased Earth Engine `maxPixels` budget from 100,000,000 to 500,000,000 (5x).
- Batched asset-risk Earth Engine sampling into 500-feature requests to avoid collection-query limits.
- Disabled Leaflet zoom/marker transform animation and tile refresh during zooming for stable map anchors.
- Wind-flow canvas is frozen/hidden during pan/zoom and reprojected once after movement ends.
- Removed unnecessary wind-layer rebuilds when storm replay changes the active marker.
- Replaced index-based asset marker keys with stable OSM/location keys to reduce remount flicker.


## Stability / scalability release

- `EE_MAX_PIXELS` is now 500,000,000 (5x the previous 100,000,000).
- `/risk/assets` samples Earth Engine context in 500-feature batches and reports failed batches instead of exceeding the large-collection aggregation limit.
- Leaflet manual zoom animation, marker zoom animation, and tile refresh during zoom are disabled to prevent anchor drift/flicker with a heavy real-data overlay stack.
- Wind-field canvases are hidden during pan/zoom and reprojected once after movement settles; unnecessary rebuilds during storm replay are removed.
- OSM asset marker keys are stable, reducing React remount flicker.

## Gemini resilience patch

- Uses the documented `x-goog-api-key` request header instead of query-string API-key authentication.
- Retries transient Gemini 408/429/5xx responses up to two times per model with bounded exponential backoff and honors `Retry-After` when supplied.
- Cascades across the configured primary, fallback and optional retry models before using the local evidence-based fallback.
- Exposes retry configuration in `/ai/status` and shows clearer temporary-unavailable messaging in the UI.
- Added tests for header authentication and 503 retry behavior.

## Gemini resilient API handling

- Gemini requests now use the documented `x-goog-api-key` header.
- Added automatic bounded retries for transient 408/429/5xx responses, with `Retry-After` support.
- Added configurable retry-model cascade via `GEMINI_RETRY_MODELS`.
- Updated the example configuration to prefer stable Gemini 3.8 Flash, then 3.7 Flash, then 3.6 Flash / 3.5 Flash-Lite.
- The AI UI now distinguishes a temporary Gemini outage from an unconfigured key and reports how many automatic attempts were made.
