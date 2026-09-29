"""Lightweight status checks for the project's external real-data sources."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

SOURCES = {
    "GDACS": "https://www.gdacs.org/",
    "GDACS RSS": "https://data.gdacs.org/xml/rss_tc_7d.xml",
    "OpenStreetMap": "https://www.openstreetmap.org/",
    "CHIRPS": "https://www.chc.ucsb.edu/data/chirps",
    "Google Earth Engine": "https://earthengine.google.com/",
    "ECMWF ERA5": "https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5",
}


def _check(item):
    name, url = item
    started = time.perf_counter()
    try:
        response = requests.get(url, timeout=8, headers={"User-Agent": "CycloneShieldAI/2.0"})
        return {
            "name": name,
            "status": "online" if response.ok else "degraded",
            "http_status": response.status_code,
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "url": url,
        }
    except requests.RequestException as exc:
        return {
            "name": name,
            "status": "offline",
            "http_status": None,
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "url": url,
            "error": str(exc),
        }


def get_source_status():
    results = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(_check, item) for item in SOURCES.items()]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda row: row["name"])
    return {"sources": results, "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
