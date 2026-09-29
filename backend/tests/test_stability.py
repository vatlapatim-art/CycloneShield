from services import earth_engine
from services.intelligence import _normalize, _haversine_km


def test_earth_engine_pixel_budget_is_five_times_previous_limit():
    assert earth_engine.EE_MAX_PIXELS == 500_000_000


def test_stability_helpers_remain_deterministic():
    assert _normalize(35, 35, 140) == 0.0
    assert round(_haversine_km(0, 0, 0, 1), 1) == 111.2
