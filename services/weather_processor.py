from __future__ import annotations

from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from services.weather_classifier import round_degrees, round_wind_kmh


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

def _fmt_time_iso8601(s: str) -> str:
    # Open-Meteo returns ISO-ish strings, e.g. 2026-04-28T13:00
    # Keep it stable and display-friendly.
    try:
        dt = datetime.fromisoformat(s)
        return dt.strftime("%a %H:%M")
    except Exception:
        return s


def parse_hourly_time(s: Any, tz: ZoneInfo) -> datetime | None:
    """Open-Meteo returns naive ISO strings in the requested timezone."""
    if not isinstance(s, str):
        return None
    try:
    
        dt = datetime.fromisoformat(s)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))

        return dt.astimezone(tz) 
    except Exception:
        return None

def _fmt_hourly_label_local(s: Any, tz: ZoneInfo) -> str:
    instant = parse_hourly_time(s, tz)
    if instant is None:
        return _fmt_time_iso8601(str(s)) if isinstance(s, str) else str(s)
    return instant.strftime("%a %H:%M")


def _fmt_daily_date_dmy(s: Any) -> str:
    if not isinstance(s, str):
        return str(s)
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%d-%m-%Y")
    except Exception:
        return s


def _fmt_daily_date_dmy_local(s: Any, tz: ZoneInfo) -> str:
    instant = parse_hourly_time(s, tz)
    if instant is None:
        return _fmt_daily_date_dmy(s)
    return instant.strftime("%d-%m-%Y")


def _forecast_tz(forecast: dict[str, Any]) -> ZoneInfo:
    name = forecast.get("timezone")
    if isinstance(name, str) and name:
        try:
            return ZoneInfo(name)
        except Exception:
            pass
    return ZoneInfo("Europe/Zurich")


def find_hourly_index(
    forecast: dict[str, Any],
    target_date: date,
    target_hour: int,
) -> int | None:
    hourly = forecast.get("hourly") or {}
    times: list[Any] = hourly.get("time") or []
    tz = _forecast_tz(forecast)
    hour = max(0, min(23, int(target_hour)))

    for i, t in enumerate(times):
        dt = parse_hourly_time(t, tz)
        if dt and dt.date() == target_date and dt.hour == hour:
            return i

    best_i: int | None = None
    best_dist = 999
    for i, t in enumerate(times):
        dt = parse_hourly_time(t, tz)
        if dt and dt.date() == target_date:
            dist = abs(dt.hour - hour)
            if dist < best_dist:
                best_dist = dist
                best_i = i
    return best_i


def _start_index_next_24h(times: list[Any], tz: ZoneInfo) -> int:
    """First hourly slot at or after the start of the current hour in `tz`."""
    now = datetime.now(tz)
    hour_start = now.replace(minute=0, second=0, microsecond=0)
    for i, t in enumerate(times):
        instant = parse_hourly_time(t, tz)
        if instant is None:
            continue
        if instant >= hour_start:
            return i
    return 0


def _start_index_daily_from_today(d_times: list[Any], tz: ZoneInfo) -> int:
    """First daily row whose local calendar day (in `tz`) is today or later."""
    today = datetime.now(tz).date()
    for i, t in enumerate(d_times):
        instant = parse_hourly_time(t, tz)
        if instant is None:
            continue
        if instant.date() >= today:
            return i
    return 0


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

    # Next 24 hours from current hour (in forecast timezone)
    tz = _forecast_tz(forecast)
    i0 = _start_index_next_24h(times, tz)
    span = min(24, len(times) - i0, len(temps) - i0, len(prec) - i0, len(pop) - i0, len(wind) - i0)
    span = max(0, span)
    i1 = i0 + span
    series = {
        "labels": [_fmt_hourly_label_local(t, tz) for t in times[i0:i1]],
        "temperature": [round_degrees(t) for t in temps[i0:i1]],
        "precipitation": prec[i0:i1],
        "precipitation_probability": pop[i0:i1],
        "wind_speed": [round_wind_kmh(w) for w in wind[i0:i1]],
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

    j0 = _start_index_daily_from_today(d_time, tz)
    span_d = min(5, len(d_time) - j0)
    j1 = j0 + span_d
  
    days: list[dict[str, Any]] = []
    for i in range(j0, j1):
        days.append(
            {
                "date": _fmt_daily_date_dmy_local(d_time[i], tz),
                "weather": weather_label(d_code[i] if i < len(d_code) else None),
                "tmax": round_degrees(tmax[i] if i < len(tmax) else None),
                "tmin": round_degrees(tmin[i] if i < len(tmin) else None),
                "precip_sum": psum[i] if i < len(psum) else None,
                "precip_prob_max": pmax[i] if i < len(pmax) else None,
                "wind_max": round_wind_kmh(wmax[i] if i < len(wmax) else None),
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
            "temperature": round_degrees(current.get("temperature_2m")),
            "apparent_temperature": round_degrees(current.get("apparent_temperature")),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "wind_speed": round_wind_kmh(current.get("wind_speed_10m")),
            "wind_gusts": round_wind_kmh(current.get("wind_gusts_10m")),
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

