# 🌪️ CycloneShield AI

### AI-Powered Cyclone Impact, Flood Intelligence & Infrastructure Vulnerability Platform

> **From cyclone tracking to infrastructure-level impact intelligence.**

CycloneShield AI is a geospatial disaster-intelligence platform designed to analyze the potential impact of tropical cyclones by combining **meteorological observations, satellite-derived flood evidence, rainfall, terrain, storm-surge scenarios, wind fields, and real-world infrastructure data** into a unified interactive system.

Instead of looking at a cyclone as only a moving point on a map, CycloneShield attempts to build a broader picture:

**Where is the cyclone? → What hazards are associated with it? → What areas may be exposed? → Which infrastructure may be affected? → What should decision-makers investigate first?**

The platform combines data from **NOAA IBTrACS, ERA5, Sentinel-1, CHIRPS, NASADEM, OpenStreetMap, Google Earth Engine, and Google Gemini** to create an integrated cyclone-impact intelligence workflow.

---

## 🛰️ What is CycloneShield?

CycloneShield is a **multi-layer geospatial decision-support system** for cyclone and flood impact analysis.

The system brings together several normally separated information layers:

```text
                         CYCLONE
                            │
                            ▼
                  ┌──────────────────┐
                  │ Storm Track      │
                  │ Wind             │
                  │ Pressure         │
                  │ Intensity        │
                  └────────┬─────────┘
                           │
                           ▼
                  ENVIRONMENTAL HAZARDS
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
       Rainfall          Flood          Terrain
          │             Evidence           │
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                    EXPOSURE ANALYSIS
                           │
                 ┌─────────┼─────────┐
                 ▼         ▼         ▼
              Medical   Emergency   Power
                 │         │         │
                 └─────────┼─────────┘
                           ▼
                     RISK ENGINE
                           │
                           ▼
                  GEMINI REASONING
                           │
                           ▼
                IMPACT INTELLIGENCE
                           │
                           ▼
                EARLY-WARNING ADVISORIES
```

This architecture allows the platform to move beyond simple weather visualization toward **hazard + exposure + infrastructure intelligence**.

---

# 🎯 Problem

Cyclone response requires decisions to be made using information from many different systems.

A disaster-management team may need to simultaneously understand:

- Current cyclone location
- Storm intensity
- Minimum pressure
- Wind conditions
- Rainfall
- Flooding
- Terrain
- Coastal exposure
- Hospitals
- Emergency facilities
- Power infrastructure
- Shelters
- Roads
- Potentially affected assets

The challenge is that these datasets are often disconnected.

A cyclone track by itself does not tell us which hospitals may be exposed.

A rainfall map does not directly tell us which power infrastructure is nearby.

A satellite image does not automatically explain what the observed environmental change means for critical infrastructure.

CycloneShield addresses this problem by bringing these layers into a **single geospatial intelligence workflow**.

---

# 💡 Our Solution

CycloneShield combines:

### 🌪️ Meteorological Intelligence
Cyclone tracks, wind, pressure and intensity.

### 🛰️ Earth Observation
Satellite-derived environmental and flood evidence.

### 🌧️ Hydrological Context
Rainfall and terrain information.

### 🏥 Infrastructure Intelligence
Real-world infrastructure retrieved from OpenStreetMap.

### 🗺️ Geospatial Analysis
Spatial intersection and proximity-based exposure analysis.

### 🤖 AI Reasoning
Gemini-powered multimodal interpretation of structured hazard evidence.

### 🚨 Decision Support
Risk summaries and early-warning advisory drafts.

---

# ✨ Core Features

## 🌪️ 1. Cyclone Track Intelligence

CycloneShield reconstructs and visualizes cyclone movement using storm observations.

The track interface provides:

- Historical storm trajectory
- Observation points
- Storm timestamps
- Wind observations
- Atmospheric pressure
- Peak intensity
- Storm replay
- Interactive map navigation

Users can inspect the storm spatially and move through its observed evolution.

---

# 💨 2. Meteorological Wind Field

CycloneShield provides a spatial wind-field visualization around the cyclone.

Instead of displaying only the storm track, the system creates a field representation showing:

- Wind direction
- Wind circulation
- Wind magnitude
- Spatial variation
- Storm-scale atmospheric structure

This provides additional context for understanding the region surrounding the cyclone.

---

# 📊 3. Storm Intensity Analysis

The platform exposes key storm-intensity indicators including:

- Maximum observed wind
- Minimum observed pressure
- Peak storm intensity
- Storm position
- Observation history

The dashboard presents these values alongside the spatial cyclone visualization.

---

# 🛰️ 4. Satellite Flood Intelligence

One of the core components of CycloneShield is its satellite-derived flood analysis.

The platform uses Sentinel-1-based processing through Google Earth Engine to identify potential new-water / inundation candidates.

The resulting information can be visualized geographically and combined with infrastructure data.

### Important distinction

CycloneShield refers to these results as **flood candidates** rather than automatically treating them as confirmed flooding.

This distinction is important because satellite-derived classifications can contain uncertainty.

---

# 🌧️ 5. Rainfall Intelligence

Rainfall information is integrated into the environmental analysis pipeline.

CycloneShield uses rainfall data to understand the additional loading that can occur during cyclone events.

Rainfall information can be combined with:

- Terrain
- Flood evidence
- Infrastructure
- Storm conditions

to provide a more complete impact context.

---

# 🏔️ 6. Terrain Intelligence

Terrain information is incorporated into the flood and rainfall analysis.

Elevation can influence:

- Water accumulation
- Drainage
- Flood susceptibility
- Low-lying exposure
- Rainfall impact pathways

CycloneShield uses terrain information as an environmental context layer rather than relying on cyclone intensity alone.

---

# 🌧️ → 🏚️ 7. Rainfall-to-Damage Pathways

CycloneShield provides a pathway-oriented view of how rainfall and terrain can potentially contribute to localized impacts.

The system conceptually connects:

```text
Rainfall
   ↓
Terrain
   ↓
Potential Water Pathways
   ↓
Exposure
   ↓
Infrastructure Risk
```

This helps users investigate not only **where rain occurs**, but also how environmental conditions may interact with exposed infrastructure.

---

# 🌊 8. Storm-Surge Scenario

The platform includes a parametric storm-surge component for coastal impact analysis.

It combines available storm and environmental information to estimate a scenario-oriented coastal potential.

The system clearly distinguishes this from a full hydrodynamic forecast.

This allows the surge layer to be used as an **analytical scenario**, rather than presenting it as an authoritative prediction.

---

# 🏥 9. Critical Infrastructure Intelligence

CycloneShield integrates real-world infrastructure information from OpenStreetMap.

The system currently considers categories such as:

### 🚑 Emergency
Emergency and response facilities.

### 🏥 Medical
Hospitals and medical infrastructure.

### ⚡ Power
Power-related infrastructure.

### 🏠 Shelter
Shelters and related facilities.

### 🛣️ Roads
Important transportation infrastructure.

This infrastructure is mapped directly alongside environmental hazard layers.

---

# 📍 10. Infrastructure Exposure Analysis

CycloneShield doesn't simply display infrastructure.

It analyzes the relationship between infrastructure and hazard evidence.

The system calculates exposure using spatial relationships.

### Direct Exposure

An infrastructure point intersects the satellite-derived flood candidate.

```text
Infrastructure Point
        ●
        │
        ▼
Flood Candidate Area
████████████████
██████●█████████
████████████████
```

### Nearby Exposure

The infrastructure does not directly intersect the candidate area, but flood-candidate pixels occur within the configured proximity range.

```text
Flood Candidate
██████████████

        250m
<---------------->

              ● Infrastructure
```

This distinction allows CycloneShield to provide more useful exposure information than a simple inside/outside classification.

---

# 🧠 11. Risk Intelligence

CycloneShield combines multiple hazard and exposure signals into structured risk information.

Conceptually:

```text
Cyclone Hazard
      +
Wind
      +
Rainfall
      +
Flood Evidence
      +
Terrain
      +
Storm Surge
      +
Infrastructure Exposure
      │
      ▼
Risk Context
```

The risk engine can then provide information about:

- Overall risk
- Risk category
- Environmental drivers
- Infrastructure exposure
- Scenario-based risk
- Asset-level exposure

---

# 🤖 12. Gemini Multimodal Reasoning

CycloneShield uses Google Gemini as an **AI interpretation layer**.

Gemini can receive structured information from the platform and optionally incorporate satellite/map imagery.

The AI layer can synthesize information from:

- Cyclone intensity
- Risk score
- Flood evidence
- Rainfall
- Infrastructure exposure
- Asset categories
- Environmental conditions

and produce a structured **AI impact brief**.

### Example workflow

```text
Cyclone Data
      │
      ▼
Risk Engine
      │
      ├── Risk Score
      ├── Flood Evidence
      ├── Rainfall
      ├── Asset Exposure
      └── Environmental Context
               │
               ▼
        Gemini Multimodal Model
               │
               ▼
        Impact Intelligence
```

---

# 🧩 AI Reliability & Fallback

CycloneShield is designed so that the core platform does not depend entirely on Gemini availability.

If Gemini is unavailable, the application can fall back to structured locally generated intelligence based on the available evidence.

```text
                 AI IMPACT REQUEST
                         │
                         ▼
                  Gemini Available?
                    /          \
                  YES           NO
                   │             │
                   ▼             ▼
              Gemini AI      Local Fallback
              Reasoning      Structured Risk
                   │             │
                   └──────┬──────┘
                          ▼
                    Impact Brief
```

This prevents the application from becoming completely unusable when an external AI service is temporarily unavailable.

---

# 🚨 13. Early-Warning Advisory Engine

CycloneShield generates structured advisory drafts for different operational groups.

### Municipal / Disaster Management

Focus:

- General preparedness
- Emergency coordination
- Infrastructure readiness

### Health / Hospital Coordination

Focus:

- Medical facility readiness
- Critical medical infrastructure
- Continuity planning

### Power / Grid Operations

Focus:

- Power infrastructure exposure
- Utility preparedness
- Hardening priorities

### Roads / Transport / Shelter Coordination

Focus:

- Accessibility
- Transportation
- Shelter readiness

These advisories are designed to support human decision-making.

They are **not automatically issued as official emergency warnings**.

---

# 🗺️ Interactive Geospatial Dashboard

The frontend provides a unified map-based interface.

Users can interact with multiple visualization layers including:

- Cyclone Track
- Flood Evidence
- Critical Infrastructure
- Exposure Zone
- Peak Intensity
- Wind Field
- Rainfall Pathways
- Asset Risk
- Storm Surge
- Meteorological overlays

The map allows users to inspect the relationship between hazards and infrastructure spatially.

---

# 🕐 Storm Replay

CycloneShield supports temporal storm analysis.

The storm replay interface allows users to move through historical observations and examine how the storm evolved.

This can be used to understand:

- Track movement
- Intensity changes
- Pressure changes
- Spatial hazard evolution

---

# 🏗️ System Architecture

CycloneShield follows a frontend/backend architecture.

```text
┌──────────────────────────────────────────────────────────┐
│                     CYCLONESHIELD AI                     │
└──────────────────────────────────────────────────────────┘

                         FRONTEND
                            │
                     React + Vite
                            │
                     Interactive UI
                            │
                       REST APIs
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│                         BACKEND                          │
│                         FastAPI                          │
└──────────────────────────────────────────────────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
   Cyclone        Earth          Exposure       AI
   Services      Observation     Engine        Intelligence
        │             │             │             │
        ▼             ▼             ▼             ▼
   IBTrACS       Earth Engine   OpenStreetMap  Gemini
   ERA5          Sentinel-1      Infrastructure  API
                 CHIRPS
                 NASADEM
```

---

# 🔄 Data Pipeline

CycloneShield processes information through multiple stages.

## Stage 1 — Data Acquisition

The backend retrieves information from external data sources.

```text
IBTrACS
ERA5
Sentinel-1
CHIRPS
NASADEM
OpenStreetMap
Google Earth Engine
```

## Stage 2 — Environmental Processing

Raw environmental data is transformed into usable analytical layers.

Examples:

- Flood candidates
- Rainfall information
- Terrain information
- Wind fields
- Storm-surge scenarios

## Stage 3 — Spatial Analysis

Hazard layers are compared against infrastructure.

```text
Hazard Raster
      +
Infrastructure Points
      ↓
Spatial Relationship
      ↓
Exposure
```

## Stage 4 — Risk Analysis

Exposure and hazard information are combined into structured risk information.

## Stage 5 — AI Interpretation

Gemini can interpret the structured evidence and produce an impact brief.

## Stage 6 — Visualization

The frontend renders the results through the interactive dashboard.

---

# 🧰 Technology Stack

## Frontend

| Technology | Purpose |
|---|---|
| React | UI architecture |
| Vite | Development/build tooling |
| JavaScript | Application logic |
| CSS | Interface styling |
| Interactive mapping | Geospatial visualization |

## Backend

| Technology | Purpose |
|---|---|
| Python | Core backend |
| FastAPI | REST API |
| Uvicorn | ASGI server |
| Pydantic | Data validation |
| Pytest | Testing |

## AI

| Technology | Purpose |
|---|---|
| Google Gemini | Multimodal reasoning |
| Gemini API | AI integration |

## Geospatial / Earth Observation

| Technology / Dataset | Purpose |
|---|---|
| Google Earth Engine | Remote-sensing processing |
| Sentinel-1 | Flood/water evidence |
| CHIRPS | Rainfall |
| NASADEM | Terrain |
| OpenStreetMap | Infrastructure |
| NOAA IBTrACS | Cyclone observations |
| ERA5 | Meteorological context |

---

# 📡 Data Sources

## NOAA IBTrACS

Used for tropical cyclone track and observation information.

Provides information including:

- Storm position
- Time
- Wind
- Pressure
- Historical track

## Sentinel-1

Used as the primary satellite observation source for flood/water-related analysis.

Its radar-based observations provide useful information for detecting changes in surface water conditions.

## Google Earth Engine

Used to access and process large-scale Earth observation datasets.

## CHIRPS

Used for rainfall information.

## NASADEM

Used for elevation and terrain context.

## OpenStreetMap

Used for real-world infrastructure information.

Infrastructure categories are queried and mapped geographically.

---

# 📁 Project Structure

```text
CycloneShield/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── .env.example
│   │
│   ├── services/
│   │   ├── earth_engine.py
│   │   ├── exposure.py
│   │   ├── infrastructure.py
│   │   ├── intelligence.py
│   │   ├── live_cyclones.py
│   │   └── source_status.py
│   │
│   └── tests/
│       ├── test_exposure_helpers.py
│       ├── test_intelligence.py
│       ├── test_live_cyclones.py
│       ├── test_new_routes.py
│       ├── test_smoke.py
│       ├── test_stability.py
│       └── test_wind_field.py
│
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── .env.example
│   ├── public/
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       ├── index.css
│       └── main.jsx
│
├── README.md
├── GEMINI_RELIABILITY.md
├── RELEASE_NOTES.md
└── .gitignore
```

---

# ⚙️ Installation

## Prerequisites

Make sure the following are installed:

- Python 3.10+
- Node.js 18+
- npm
- Git

Required external services:

- Google Earth Engine
- Google Gemini API

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scriptsctivate
pip install -r requirements.txt
```

## Backend Environment

Create:

```text
backend/.env
```

using:

```text
backend/.env.example
```

as the template.

Example:

```env
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=your_model
GEMINI_FALLBACK_MODEL=your_fallback_model
```

Additional Earth Engine authentication/configuration should be configured according to the environment in which the application is being run.

**Never commit real API keys to GitHub.**

## Frontend Setup

```bash
cd frontend
npm install
```

Create the frontend environment file using:

```text
frontend/.env.example
```

as the template.

---

# ▶️ Running CycloneShield

CycloneShield requires both the backend and frontend to be running.

### Terminal 1 — Backend

```bash
cd backend
.venv\Scriptsctivate
python -m uvicorn main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

---

# 🧪 Testing

CycloneShield includes a backend test suite using Pytest.

```bash
cd backend
pytest
```

Tests cover areas including:

- Exposure calculations
- Intelligence services
- Cyclone services
- Wind-field generation
- API routes
- Stability
- Smoke testing

---

# 🔍 Example Analysis Workflow

A typical CycloneShield workflow looks like this:

### 01 — Select / Load Storm
The application loads cyclone observations.

### 02 — Inspect Track
The storm trajectory and historical observations are displayed.

### 03 — Inspect Intensity
Wind and pressure information are displayed.

### 04 — Analyze Environmental Conditions
Rainfall, terrain and flood evidence are loaded.

### 05 — Inspect Infrastructure
Critical infrastructure is mapped around the affected region.

### 06 — Calculate Exposure
Infrastructure is compared against hazard evidence.

### 07 — Generate Risk Context
The system produces structured risk information.

### 08 — Generate AI Impact Brief
Gemini interprets the available evidence.

### 09 — Review Advisories
Operational advisory drafts are generated for relevant sectors.

---

# 🧠 Reliability Philosophy

CycloneShield separates different forms of information instead of treating every output as equally certain.

```text
OBSERVATION
     │
     ▼
DERIVED DATA
     │
     ▼
CANDIDATE EVIDENCE
     │
     ▼
RISK ANALYSIS
     │
     ▼
AI INTERPRETATION
```

For example:

**Satellite flood candidate ≠ confirmed flood**

and

**AI advisory ≠ official emergency warning**

This separation is fundamental to the design of the system.

---

# ⚠️ Limitations

CycloneShield is a disaster-intelligence prototype and should not be treated as an autonomous emergency-response system.

### Satellite Analysis
Satellite-derived flood candidates can contain uncertainty.

### Infrastructure Coverage
OpenStreetMap coverage varies depending on location and available mapping data.

### Storm Surge
The surge component is parametric and does not represent a complete hydrodynamic coastal model.

### AI
Gemini-generated information can contain errors and must be reviewed.

### Meteorological Data
Environmental datasets have their own temporal and spatial resolution limitations.

### Operational Decisions
Emergency decisions should always be validated against authoritative observations and official warnings.

---

# 🛡️ Responsible Use

CycloneShield is intended to **augment human decision-making**, not replace it.

The system should be used alongside:

- Official meteorological warnings
- Emergency-management authorities
- Local ground observations
- Engineering assessments
- Verified satellite interpretation
- Domain experts

AI-generated information should be treated as analytical assistance rather than authoritative emergency instruction.

---

# 🚀 Future Scope

Potential future directions include:

- Higher-resolution flood modelling
- More advanced hydrodynamic storm-surge modelling
- Additional satellite sources
- Real-time cyclone monitoring
- Automated infrastructure prioritization
- Road accessibility analysis
- Evacuation-route intelligence
- Population exposure modelling
- More detailed asset vulnerability models
- Multi-storm comparison
- Historical disaster validation
- More advanced multimodal AI reasoning
- Real-time alert integrations

---

# 🌍 Vision

CycloneShield is built around a simple idea:

> **A cyclone forecast becomes more useful when it can be connected to the real-world systems and infrastructure that may be affected.**

Instead of presenting isolated datasets, CycloneShield attempts to connect:

```text
Weather
   +
Earth Observation
   +
Terrain
   +
Flood Evidence
   +
Infrastructure
   +
Risk
   +
AI
```

into one operational intelligence workflow.

The goal is to help transform disaster analysis from:

```text
"What is happening?"
```

into:

```text
"What is happening,
what may be exposed,
and what should we investigate next?"
```

---

# 📌 Project Status

CycloneShield AI is a functional prototype demonstrating an integrated workflow for cyclone monitoring, environmental analysis, infrastructure exposure assessment, risk intelligence, and AI-assisted impact interpretation.

---

# 👨‍💻 Project

**CycloneShield AI**

**Cyclone Impact & Infrastructure Vulnerability Forecaster**

Built as a geospatial disaster-intelligence prototype combining:

**React + FastAPI + Google Earth Engine + Sentinel-1 + OpenStreetMap + Meteorological Data + Gemini AI**

---

## License

This project is developed as a prototype for the Cyclone Impact & Infrastructure Vulnerability Forecaster challenge.

See the repository for project-specific licensing and usage information.
