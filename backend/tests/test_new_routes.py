from fastapi.testclient import TestClient
import main


def sample_payload():
    return {
        "cyclone": {"track": {"properties": {"name": "Amphan", "season": 2020}}, "observations": [{"lat": 15, "lon": 85, "wmo_wind_kt": 130, "wmo_pressure_mb": 920, "storm_speed_kt": 12, "storm_direction_deg": 30}]},
        "flood": {"candidate_area_km2": 300},
        "terrain": {"elevation_mean_m": 15},
        "rainfall": {"rainfall_max_mm": 220},
        "exposure": {"total_critical": 1000, "nearby_exposed_count": 15},
    }


def test_payload_risk_and_advisory_routes():
    client = TestClient(main.app)
    payload = sample_payload()
    risk = client.post("/risk/summary", json=payload)
    advisory = client.post("/advisories/generate", json=payload)
    assert risk.status_code == 200
    assert "risk_score" in risk.json()
    assert advisory.status_code == 200
    assert len(advisory.json()["advisories"]) == 4


def test_ai_status_is_safe_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    client = TestClient(main.app)
    result = client.get("/ai/status")
    assert result.status_code == 200
    assert result.json()["configured"] is False


def test_scenario_route(monkeypatch):
    monkeypatch.setattr(main, "get_cyclone_track", lambda sid: {
        "observations": [{"lat": 15, "lon": 85, "wmo_wind_kt": 100, "storm_speed_kt": 12, "storm_direction_deg": 30, "wmo_pressure_mb": 960}]
    })
    client = TestClient(main.app)
    response = client.get("/risk/scenario?lead_hours=6")
    assert response.status_code == 200
    assert response.json()["available"] is True
