from main import app
from fastapi.testclient import TestClient
import main


def test_wind_field_endpoint(monkeypatch):
    sample = {
        "source": "ECMWF ERA5 Hourly via Google Earth Engine",
        "dataset": "ECMWF/ERA5/HOURLY",
        "timestamp": "2020-05-18T12:00:00Z",
        "bbox": {"west": 65.0, "south": 5.0, "east": 105.0, "north": 32.0},
        "rows": 2,
        "cols": 2,
        "data": [
            {"i": 0, "j": 0, "lat": 5.0, "lon": 65.0, "u_ms": 1.0, "v_ms": 2.0, "speed_kt": 4.3, "mslp_hpa": 1010.0},
            {"i": 1, "j": 0, "lat": 5.0, "lon": 65.75, "u_ms": 1.0, "v_ms": 2.0, "speed_kt": 4.3, "mslp_hpa": 1010.0},
            {"i": 0, "j": 1, "lat": 5.75, "lon": 65.0, "u_ms": 1.0, "v_ms": 2.0, "speed_kt": 4.3, "mslp_hpa": 1008.0},
            {"i": 1, "j": 1, "lat": 5.75, "lon": 65.75, "u_ms": 1.0, "v_ms": 2.0, "speed_kt": 4.3, "mslp_hpa": 1008.0},
        ],
    }
    monkeypatch.setattr(main, "get_era5_wind_field", lambda *args, **kwargs: sample)
    response = TestClient(app).get("/wind-field")
    assert response.status_code == 200
    assert response.json()["dataset"] == "ECMWF/ERA5/HOURLY"
