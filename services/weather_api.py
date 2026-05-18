from __future__ import annotations

from typing import Any

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

from services.cities import City


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

_cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
_retry_session = retry(_cache_session, retries=5, backoff_factor=0.2)
_openmeteo = openmeteo_requests.Client(session=_retry_session)

_CURRENT_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "snowfall",
    "weather_code",
    "cloud_cover",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
]
_HOURLY_VARS = [
    "temperature_2m",
    "apparent_temperature",
    "precipitation",
    "precipitation_probability",
    "weather_code",
    "cloud_cover",
    "wind_speed_10m",
]
_DAILY_VARS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "wind_speed_10m_max",
    "weather_code",
    "sunrise",
    "sunset",
]


def _iso_times_from_unix(start_s: int, end_s: int, interval_s: int) -> list[str]:
    idx = pd.date_range(
        start=pd.to_datetime(start_s, unit="s", utc=True),
        end=pd.to_datetime(end_s, unit="s", utc=True),
        freq=pd.Timedelta(seconds=interval_s),
        inclusive="left",
    )
    return [t.isoformat(timespec="minutes") for t in idx]


def _as_list(x) -> list:
    if x is None:
        return []
    tolist = getattr(x, "tolist", None)
    if callable(tolist):
        try:
            v = tolist()
            return v if isinstance(v, list) else [v]
        except Exception:
            pass
    try:
        return list(x)
    except Exception:
        return [x]


def _forecast_params(
    *,
    latitude: str | float,
    longitude: str | float,
    timezone: str,
    forecast_days: int,
    model: str,
) -> dict[str, Any]:
    return {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "forecast_days": forecast_days,
        "models": model,
        "current": _CURRENT_VARS,
        "hourly": _HOURLY_VARS,
        "daily": _DAILY_VARS,
    }


def _response_to_forecast(response: Any, *, timezone: str) -> dict[str, Any]:
    current = response.Current()
    current_units: dict[str, Any] = {
        "temperature_2m": "°C",
        "relative_humidity_2m": "%",
        "apparent_temperature": "°C",
        "precipitation": "mm",
        "rain": "mm",
        "snowfall": "cm",
        "weather_code": "",
        "cloud_cover": "%",
        "wind_speed_10m": "km/h",
        "wind_direction_10m": "°",
        "wind_gusts_10m": "km/h",
    }
    current_data: dict[str, Any] = {"time": None}
    try:
        current_data["time"] = (
            pd.to_datetime(current.Time(), unit="s", utc=True)
            .to_pydatetime()
            .replace(tzinfo=None)
            .isoformat(timespec="minutes")
        )
    except Exception:
        current_data["time"] = None

    for i, v in enumerate(_CURRENT_VARS):
        var = current.Variables(i)
        current_data[v] = var.Value()

    hourly = response.Hourly()
    hourly_times = _iso_times_from_unix(hourly.Time(), hourly.TimeEnd(), hourly.Interval())
    hourly_units: dict[str, Any] = {
        "time": "iso8601",
        "temperature_2m": "°C",
        "apparent_temperature": "°C",
        "precipitation": "mm",
        "precipitation_probability": "%",
        "weather_code": "",
        "cloud_cover": "%",
        "wind_speed_10m": "km/h",
    }
    hourly_data: dict[str, Any] = {"time": hourly_times}
    for i, v in enumerate(_HOURLY_VARS):
        var = hourly.Variables(i)
        hourly_data[v] = _as_list(var.ValuesAsNumpy())

    daily = response.Daily()
    daily_times = _iso_times_from_unix(daily.Time(), daily.TimeEnd(), daily.Interval())
    daily_units: dict[str, Any] = {
        "time": "iso8601",
        "temperature_2m_max": "°C",
        "temperature_2m_min": "°C",
        "precipitation_sum": "mm",
        "precipitation_probability_max": "%",
        "wind_speed_10m_max": "km/h",
        "weather_code": "",
        "sunrise": "iso8601",
        "sunset": "iso8601",
    }
    daily_data: dict[str, Any] = {"time": daily_times}
    for i, v in enumerate(_DAILY_VARS):
        var = daily.Variables(i)
        daily_data[v] = _as_list(var.ValuesAsNumpy())

    return {
        "latitude": response.Latitude(),
        "longitude": response.Longitude(),
        "timezone": timezone,
        "current": current_data,
        "current_units": current_units,
        "hourly": hourly_data,
        "hourly_units": hourly_units,
        "daily": daily_data,
        "daily_units": daily_units,
    }

def fetch_all_cities_forecast(
    *,
    cities: list[City],
    timezone: str = "Europe/Zurich",
    forecast_days: int = 5,
    model: str = "meteoswiss_icon_ch2",
) -> dict[str, dict[str, Any]]:
    """Single HTTP request for all city coordinates."""
    if not cities:
        return {}

    params = _forecast_params(
        latitude=",".join(str(c["lat"]) for c in cities),
        longitude=",".join(str(c["lon"]) for c in cities),
        timezone=timezone,
        forecast_days=forecast_days,
        model=model,
    )
    responses = _openmeteo.weather_api(OPEN_METEO_URL, params=params)
    if len(responses) != len(cities):
        raise RuntimeError(f"Expected {len(cities)} forecasts, got {len(responses)}")

    return {
        city["id"]: _response_to_forecast(response, timezone=timezone)
        for city, response in zip(cities, responses, strict=True)
    }
