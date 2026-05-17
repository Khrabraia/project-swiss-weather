from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from services.cities import CITIES, City
from services.forecast_cache import get_all_city_forecasts
from services.forecast_days import TZ, clamp_day_offset, current_local_hour, day_label
from services.weather_classifier import (
    classify_weather,
    round_degrees,
    round_wind_kmh,
    status_display,
)
from services.weather_processor import find_hourly_index


def normalize_hour(hour: int | None) -> int | None:
    if hour is None:
        return None
    return max(0, min(24, int(hour)))


def _target_date(day_offset: int) -> date:
    return datetime.now(TZ).date() + timedelta(days=day_offset)


def _read_hourly_values(hourly: dict[str, Any], index: int) -> tuple[float, float, float, float]:
    def at(key: str, default: float = 0.0) -> float:
        arr = hourly.get(key) or []
        if index >= len(arr):
            return default
        v = arr[index]
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    temp = at("temperature_2m")
    precipitation = at("precipitation")
    wind = at("wind_speed_10m")
    precipitation_probability = at("precipitation_probability")
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
        "precipitation": round(precipitation, 1),
        "wind": round_wind_kmh(wind),
        "precipitation_probability": int(round(precipitation_probability, 0)),
        **result,
        **status_display(result["status"], result["reason"]),
    }


def point_from_forecast(
    *,
    city: City,
    forecast: dict[str, Any],
    day_offset: int,
    hour: int,
) -> dict[str, Any] | None:
    idx = find_hourly_index(forecast, _target_date(day_offset), hour)
    if idx is None:
        return None

    hourly = forecast.get("hourly") or {}
    temp, precipitation, wind, precipitation_probability = _read_hourly_values(hourly, idx)
    h = normalize_hour(hour) or 0
    return {
        "id": city["id"],
        "name": city["name"],
        "lat": city["lat"],
        "lon": city["lon"],
        "current": {
            "hour": h,
            **_classify_point(temp, precipitation, wind, precipitation_probability),
        },
    }


def _recommendation_from_point(city: City, cur: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": city["id"],
        "name": city["name"],
        "lat": city["lat"],
        "lon": city["lon"],
        "score": cur["score"],
        "status": cur["status"],
        "status_label": cur["status_label"],
        "reason": cur["reason"],
        "reason_label": cur["reason_label"],
        "emoji": cur["emoji"],
        "temp": cur["temp"],
        "precipitation": cur["precipitation"],
        "wind": cur["wind"],
        "precipitation_probability": cur["precipitation_probability"],
    }


def build_weather_bundle(*, day_offset: int = 0, hour: int | None = None) -> dict[str, Any]:
    day_offset = clamp_day_offset(day_offset)
    h = normalize_hour(hour) if hour is not None else current_local_hour()
    forecasts = get_all_city_forecasts()

    cities_out: list[dict[str, Any]] = []
    ranked: list[tuple[int, str, dict[str, Any]]] = []

    for city in CITIES:
        forecast = forecasts.get(city["id"])
        if not forecast:
            continue

        row = point_from_forecast(city=city, forecast=forecast, day_offset=day_offset, hour=h)
        if row:
            cities_out.append(row)

        noon = point_from_forecast(city=city, forecast=forecast, day_offset=day_offset, hour=12)
        if noon:
            cur = noon["current"]
            ranked.append((cur["score"], city["name"], _recommendation_from_point(city, cur)))

    cities_out.sort(key=lambda c: c["name"])
    ranked.sort(key=lambda x: (-x[0], x[1]))
    recommendations = [item for _score, _name, item in ranked[:3]]

    return {
        "day_offset": day_offset,
        "day_label": day_label(day_offset),
        "hour": h,
        "cities": cities_out,
        "recommendations": recommendations,
    }


def all_cities_weather(*, day_offset: int = 0, hour: int | None = None) -> dict[str, Any]:
    return build_weather_bundle(day_offset=day_offset, hour=hour)


def top_walk_recommendations(*, day_offset: int = 0, limit: int = 3) -> list[dict[str, Any]]:
    bundle = build_weather_bundle(day_offset=day_offset, hour=12)
    return bundle["recommendations"][:limit]
