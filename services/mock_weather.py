from __future__ import annotations

import hashlib
from typing import Any

from services.cities import CITIES, City
from services.weather_classifier import classify_weather, status_display

DAY_OFFSETS = (0, 1, 3)
DAY_LABELS = {0: "Today", 1: "Tomorrow", 3: "In 3 days"}


def normalize_hour(hour: int | None) -> int | None:
    if hour is None:
        return None
    return max(0, min(24, int(hour)))


def hourly_index(hour: int) -> int:
    """Map 0–24 display hour to hourly array index (0–23)."""
    return min(normalize_hour(hour) or 0, 23)


def _seed(*parts: str | int) -> int:
    raw = "|".join(str(p) for p in parts).encode()
    return int(hashlib.md5(raw).hexdigest()[:8], 16)


def _mock_values(city_id: str, day_offset: int, hour: int) -> tuple[float, float, float, float]:
    s = _seed(city_id, day_offset, hour)
    temp = 5 + (s % 2600) / 100.0
    rain = round((s % 400) / 100.0, 1)
    wind = round(1 + (s % 1200) / 100.0, 1)
    cloud = float(s % 101)
    return temp, rain, wind, cloud


def _classify_point(temp: float, rain: float, wind: float, cloud: float) -> dict[str, Any]:
    score, label = classify_weather(temp, rain, wind, cloud)
    return {
        "temp": round(temp, 1),
        "rain": rain,
        "wind": wind,
        "cloud": round(cloud, 0),
        "score": score,
        **status_display(label),
    }


def mock_city_weather(city: City, day_offset: int) -> dict[str, Any]:
    hourly: list[dict[str, Any]] = []
    for hour in range(24):
        temp, rain, wind, cloud = _mock_values(city["id"], day_offset, hour)
        hourly.append({"hour": hour, **_classify_point(temp, rain, wind, cloud)})

    # Daily snapshot: noon hour
    daily = hourly[12]
    return {
        "id": city["id"],
        "name": city["name"],
        "lat": city["lat"],
        "lon": city["lon"],
        "day_offset": day_offset,
        "day_label": DAY_LABELS.get(day_offset, f"+{day_offset} days"),
        "daily": {k: daily[k] for k in ("temp", "rain", "wind", "cloud", "score", "status", "emoji", "color")},
        "hourly": hourly,
    }


def all_cities_weather(*, day_offset: int = 0, hour: int | None = None) -> dict[str, Any]:
    cities_out: list[dict[str, Any]] = []
    for city in CITIES:
        row = mock_city_weather(city, day_offset)
        if hour is not None:
            h = normalize_hour(hour) or 0
            point = row["hourly"][hourly_index(h)]
            row["current"] = {
                "hour": h,
                **{k: point[k] for k in ("temp", "rain", "wind", "cloud", "score", "status", "emoji", "color")},
            }
        else:
            row["current"] = row["daily"]
        cities_out.append(row)

    return {
        "day_offset": day_offset,
        "day_label": DAY_LABELS.get(day_offset, f"+{day_offset} days"),
        "hour": hour,
        "cities": cities_out,
    }


def top_walk_recommendations(*, day_offset: int = 0, limit: int = 3) -> list[dict[str, Any]]:
    ranked: list[tuple[int, str, dict[str, Any]]] = []
    for city in CITIES:
        data = mock_city_weather(city, day_offset)
        d = data["daily"]
        ranked.append((d["score"], city["name"], {**data, "rank_score": d["score"]}))

    ranked.sort(key=lambda x: (-x[0], x[1]))
    out: list[dict[str, Any]] = []
    for score, _name, payload in ranked[:limit]:
        if score < 0 and len(out) >= limit:
            break
        out.append(
            {
                "id": payload["id"],
                "name": payload["name"],
                "lat": payload["lat"],
                "lon": payload["lon"],
                "score": payload["daily"]["score"],
                "status": payload["daily"]["status"],
                "emoji": payload["daily"]["emoji"],
                "temp": payload["daily"]["temp"],
                "rain": payload["daily"]["rain"],
                "wind": payload["daily"]["wind"],
                "cloud": payload["daily"]["cloud"],
            }
        )
    return out[:limit]
