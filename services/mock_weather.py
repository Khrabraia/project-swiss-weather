from __future__ import annotations

import hashlib
from typing import Any

from services.cities import CITIES, City
from services.weather_classifier import classify_weather, round_degrees, round_wind_kmh, status_display

DAY_OFFSETS = (0, 1, 2, 3, 4)
DAY_LABELS = {0: "Today", 1: "Tomorrow"}


def _seed(*parts: str | int) -> int:
    raw = "|".join(str(p) for p in parts).encode()
    return int(hashlib.md5(raw).hexdigest()[:8], 16)


def _mock_values(city_id: str, day_offset: int, hour: int) -> tuple[float, float, float, float]:
    s = _seed(city_id, day_offset, hour)
    temp = 5 + (s % 2600) / 100.0
    precipitation = round((s % 400) / 100.0, 1)
    wind = round(1 + (s % 1200) / 100.0, 1)
    precipitation_probability = float(s % 101)
    return temp, precipitation, wind, precipitation_probability


def _classify_point(
    temp: float,
    precipitation: float,
    wind: float,
    precipitation_probability: float,
) -> dict[str, Any]:
    result = classify_weather(temp, precipitation, wind, precipitation_probability)
    return {
        "temp": round_degrees(temp),
        "precipitation": precipitation,
        "wind": round_wind_kmh(wind),
        "precipitation_probability": int(round(precipitation_probability, 0)),
        **result,
        **status_display(result["status"], result["reason"]),
    }
