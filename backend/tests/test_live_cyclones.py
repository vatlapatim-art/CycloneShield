from services import live_cyclones


def test_live_cyclone_parser_filters_region(monkeypatch):
    class FakeResponse:
        content = b""
        def raise_for_status(self):
            return None
        def json(self):
            return {"features": [
                {"id": "inside", "geometry": {"coordinates": [88.0, 22.0]}, "properties": {"name": "TEST", "alertlevel": "Orange"}},
                {"id": "outside", "geometry": {"coordinates": [150.0, 22.0]}, "properties": {"name": "NOPE"}},
            ]}
    monkeypatch.setattr(live_cyclones.requests, "get", lambda *a, **k: FakeResponse())
    result = live_cyclones.get_live_cyclones()
    assert result["count"] == 1
    assert result["events"][0]["name"] == "TEST"
    assert result["events"][0]["latitude"] == 22.0


def test_rss_fallback(monkeypatch):
    class ApiResponse:
        content = b""
        def raise_for_status(self):
            raise RuntimeError("API blocked")
    class RssResponse:
        content = b"<rss><channel><item><title>TEST RSS</title><guid>rss-1</guid><pubDate>Mon, 01 Jun 2026 00:00:00 GMT</pubDate><point>22.5 88.5</point></item></channel></rss>"
        def raise_for_status(self):
            return None
    def fake_get(url, *args, **kwargs):
        return ApiResponse() if "gdacsapi" in url else RssResponse()
    monkeypatch.setattr(live_cyclones.requests, "get", fake_get)
    result = live_cyclones.get_live_cyclones()
    assert result["count"] == 1
    assert result["fallback_used"] is True
    assert result["source"] == "GDACS RSS"
