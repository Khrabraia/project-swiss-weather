from __future__ import annotations

import threading
import time
from typing import Any

from services.cities import CITIES, City
from services.weather_api import fetch_all_cities_forecast

_lock = threading.Lock()
_cache: dict[str, dict[str, Any]] | None = None
_cache_at: float = 0.0
CACHE_TTL_SECONDS = 3600


def get_all_city_forecasts(*, force: bool = False) -> dict[str, dict[str, Any]]:
    """One Open-Meteo batch request for all cities; reused across map, picks, dashboard."""
    global _cache, _cache_at
    with _lock:
        if (
            not force
            and _cache is not None
            and (time.time() - _cache_at) < CACHE_TTL_SECONDS
        ):
            return _cache

        _cache = fetch_all_cities_forecast(cities=CITIES)
        _cache_at = time.time()
        return _cache


def get_city_forecast(city: City, *, force: bool = False) -> dict[str, Any]:
    forecasts = get_all_city_forecasts(force=force)
    return forecasts[city["id"]]
