from __future__ import annotations

from datetime import datetime
from typing import Any


WEATHER_CODE_LABELS: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def _safe_get(d: dict[str, Any], path: list[str], default=None):
    cur: Any = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def _fmt_time_iso8601(s: str) -> str:
    # Open-Meteo returns ISO-ish strings, e.g. 2026-04-28T13:00
    # Keep it stable and display-friendly.
    try:
        dt = datetime.fromisoformat(s)
        return dt.strftime("%a %H:%M")
    except Exception:
        return s


def weather_label(code: int | None) -> str:
    if code is None:
        return "Unknown"
    return WEATHER_CODE_LABELS.get(int(code), f"Code {code}")


def build_dashboard_view_model(*, city: dict[str, Any], forecast: dict[str, Any]) -> dict[str, Any]:
    current = forecast.get("current", {}) or {}
    units = forecast.get("current_units", {}) or {}

    current_code = current.get("weather_code")
    current_time = current.get("time")

    hourly = forecast.get("hourly", {}) or {}
    hourly_units = forecast.get("hourly_units", {}) or {}

    times = hourly.get("time", []) or []
    temps = hourly.get("temperature_2m", []) or []
    prec = hourly.get("precipitation", []) or []
    pop = hourly.get("precipitation_probability", []) or []
    wind = hourly.get("wind_speed_10m", []) or []

    # Next 24 hours
    n = min(24, len(times), len(temps), len(prec), len(pop), len(wind))
    series = {
        "labels": [_fmt_time_iso8601(t) for t in times[:n]],
        "temperature": temps[:n],
        "precipitation": prec[:n],
        "precipitation_probability": pop[:n],
        "wind_speed": wind[:n],
        "units": {
            "temperature": hourly_units.get("temperature_2m", "°C"),
            "precipitation": hourly_units.get("precipitation", "mm"),
            "precipitation_probability": hourly_units.get("precipitation_probability", "%"),
            "wind_speed": hourly_units.get("wind_speed_10m", "km/h"),
        },
    }

    daily = forecast.get("daily", {}) or {}
    daily_units = forecast.get("daily_units", {}) or {}

    d_time = daily.get("time", []) or []
    tmax = daily.get("temperature_2m_max", []) or []
    tmin = daily.get("temperature_2m_min", []) or []
    psum = daily.get("precipitation_sum", []) or []
    pmax = daily.get("precipitation_probability_max", []) or []
    wmax = daily.get("wind_speed_10m_max", []) or []
    d_code = daily.get("weather_code", []) or []

    days_count = min(5, len(d_time), len(tmax), len(tmin), len(psum), len(pmax), len(wmax), len(d_code))
    days: list[dict[str, Any]] = []
    for i in range(days_count):
        days.append(
            {
                "date": d_time[i],
                "weather": weather_label(d_code[i] if i < len(d_code) else None),
                "tmax": tmax[i],
                "tmin": tmin[i],
                "precip_sum": psum[i],
                "precip_prob_max": pmax[i],
                "wind_max": wmax[i],
            }
        )

    # Derived “simple” insights
    trend = "stable"
    if len(series["temperature"]) >= 8:
        a = series["temperature"][0]
        b = series["temperature"][7]
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if b - a >= 2:
                trend = "warming"
            elif a - b >= 2:
                trend = "cooling"

    wet_hours = 0
    for x in series["precipitation"]:
        if isinstance(x, (int, float)) and x > 0.1:
            wet_hours += 1
    wet_label = "dry" if wet_hours <= 1 else ("showery" if wet_hours <= 6 else "wet")

    return {
        "city": city,
        "cities": None,  # set by template via /api/cities fetch, or server side later
        "meta": {
            "source": "Open-Meteo MeteoSwiss ICON",
            "doc_url": "https://open-meteo.com/en/docs/meteoswiss-api",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "current": {
            "time": current_time,
            "weather": weather_label(current_code),
            "temperature": current.get("temperature_2m"),
            "apparent_temperature": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "wind_speed": current.get("wind_speed_10m"),
            "wind_gusts": current.get("wind_gusts_10m"),
            "cloud_cover": current.get("cloud_cover"),
            "units": {
                "temperature": units.get("temperature_2m", "°C"),
                "humidity": units.get("relative_humidity_2m", "%"),
                "precipitation": units.get("precipitation", "mm"),
                "wind_speed": units.get("wind_speed_10m", "km/h"),
                "wind_gusts": units.get("wind_gusts_10m", "km/h"),
                "cloud_cover": units.get("cloud_cover", "%"),
            },
        },
        "insights": {"trend_8h": trend, "wetness_24h": wet_label},
        "series24h": series,
        "days": days,
        "daily_units": {
            "tmax": daily_units.get("temperature_2m_max", "°C"),
            "tmin": daily_units.get("temperature_2m_min", "°C"),
            "precip_sum": daily_units.get("precipitation_sum", "mm"),
            "precip_prob_max": daily_units.get("precipitation_probability_max", "%"),
            "wind_max": daily_units.get("wind_speed_10m_max", "km/h"),
        },
    }

