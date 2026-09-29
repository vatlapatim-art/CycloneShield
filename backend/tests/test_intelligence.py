from services.intelligence import build_risk_summary, project_storm_scenario, generate_advisories


def sample_data():
    cyclone = {
        "track": {"properties": {"name": "Amphan", "season": 2020}},
        "observations": [
            {"lat": 15.0, "lon": 85.0, "wmo_wind_kt": 90, "wmo_pressure_mb": 970, "storm_speed_kt": 10, "storm_direction_deg": 25},
            {"lat": 16.0, "lon": 86.0, "wmo_wind_kt": 130, "wmo_pressure_mb": 920, "storm_speed_kt": 12, "storm_direction_deg": 30},
        ],
    }
    flood = {"candidate_area_km2": 300}
    rainfall = {"rainfall_max_mm": 240}
    terrain = {"elevation_mean_m": 18}
    exposure = {"total_critical": 1000, "nearby_exposed_count": 12}
    return cyclone, flood, rainfall, terrain, exposure


def test_risk_summary_and_scenario():
    cyclone, flood, rainfall, terrain, exposure = sample_data()
    risk = build_risk_summary(cyclone=cyclone, flood=flood, rainfall=rainfall, terrain=terrain, exposure=exposure)
    assert 0 <= risk["risk_score"] <= 100
    assert risk["risk_band"] in {"MODERATE", "ELEVATED", "HIGH", "EXTREME"}

    scenario = project_storm_scenario(cyclone, lead_hours=12)
    assert scenario["available"] is True
    assert scenario["projected_position"]["lat"] != cyclone["observations"][-1]["lat"]


def test_advisory_drafts_are_dispatch_ready():
    cyclone, flood, rainfall, terrain, exposure = sample_data()
    risk = build_risk_summary(cyclone=cyclone, flood=flood, rainfall=rainfall, terrain=terrain, exposure=exposure)
    advisories = generate_advisories(risk=risk)
    assert advisories["dispatch_ready"] is True
    assert len(advisories["advisories"]) == 4


class _FakeResponse:
    def __init__(self, status_code, payload, headers=None, reason="Service Unavailable"):
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {}
        self.reason = reason

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(f"{self.status_code} {self.reason}")


def test_gemini_uses_header_auth_and_retries_503(monkeypatch):
    import services.intelligence as intelligence

    monkeypatch.setenv("GEMINI_API_KEY", "secret-test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-primary-test")
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "gemini-fallback-test")
    monkeypatch.setenv("GEMINI_RETRY_MODELS", "")

    calls = []
    responses = [
        _FakeResponse(503, {"error": {"code": 503, "status": "UNAVAILABLE", "message": "high demand"}}),
        _FakeResponse(200, {"candidates": [{"content": {"parts": [{"text": "GENUINE GEMINI RESPONSE"}]}}]}),
    ]

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        return responses.pop(0)

    monkeypatch.setattr("requests.post", fake_post)
    monkeypatch.setattr(intelligence.time, "sleep", lambda seconds: None)

    result = intelligence.generate_gemini_brief({"risk": {"risk_score": 50, "risk_band": "ELEVATED"}})

    assert result["mode"] == "gemini"
    assert result["attempts"] == 2
    assert result["retryable"] is True
    assert calls[0][0].endswith("/models/gemini-primary-test:generateContent")
    assert "key=" not in calls[0][0]
    assert calls[0][1]["headers"]["x-goog-api-key"] == "secret-test-key"
    assert calls[0][1]["headers"]["Content-Type"] == "application/json"


def test_gemini_status_reports_retry_configuration(monkeypatch):
    import services.intelligence as intelligence

    monkeypatch.setenv("GEMINI_API_KEY", "secret-test-key")
    monkeypatch.delenv("GEMINI_RETRY_MODELS", raising=False)
    status = intelligence.gemini_status()
    assert status["configured"] is True
    assert status["automatic_retry"] is True
    assert status["max_retries_per_model"] == 2
    assert "gemini-3.6-flash" in status["retry_models"]
