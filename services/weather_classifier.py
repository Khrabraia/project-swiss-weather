from __future__ import annotations

from typing import Any

STATUSES = ("go_out", "nice_walk", "short_walk", "take_umbrella", "stay_home")

STATUS_EMOJI: dict[str, str] = {
    "go_out": "🌞",
    "nice_walk": "🚶",
    "short_walk": "🙂",
    "take_umbrella": "☂️",
    "stay_home": "🏠",
}

STATUS_COLORS: dict[str, str] = {
    "go_out": "#22c55e",
    "nice_walk": "#3b82f6",
    "short_walk": "#eab308",
    "take_umbrella": "#f97316",
    "stay_home": "#ef4444",
}

STATUS_LABELS: dict[str, str] = {
    "go_out": "Go out",
    "nice_walk": "Nice walk",
    "short_walk": "Short walk",
    "take_umbrella": "Take umbrella",
    "stay_home": "Stay home",
}

REASON_LABELS: dict[str, str] = {
    "perfect_weather": "Perfect weather",
    "rain": "Rain expected",
    "heavy_rain": "Heavy rain",
    "wind": "Strong wind",
    "cold": "Cold weather",
    "hot": "Hot weather",
    "warm": "Warm",
    "chilly": "Chilly",
    "cloudy": "High rain chance",
    "storm": "Storm",
    "snow": "Snow"
}


def round_degrees(value: float | int | None) -> int:
    if value is None:
        return 0
    return int(round(float(value), 0))


def round_wind_kmh(value: float | int | None) -> int:
    if value is None:
        return 0
    return round(float(value), 1)


def classify_weather(
    temp: float,
    precipitation: float,
    wind: float,
    precipitation_probability: float,
) -> dict[str, Any]:
    """
    Score walking conditions.

    temp: °C
    precipitation: mm
    wind: km/h
    precipitation_probability: %
    """
    score = 0
    reason = "perfect_weather"

    if precipitation > 5:
        if wind > 10:
            return {"score": -10, "status": "stay_home", "reason": "storm"}
        return {"score": -10, "status": "stay_home", "reason": "heavy_rain"}

    if temp < 0:
        reason = "cold"
    elif temp > 30:
        reason = "hot"
    elif 18 <= temp <= 25:
        score += 3
    elif 10 <= temp < 18 or 25 < temp <= 30:
        score += 2
        reason = "warm"
    else:
        score += 1
        reason = "chilly"
    

    if precipitation > 1:
        score -= 3
        if reason == "cold":
            reason = "snow"
        else:
            reason = "rain"

    if wind > 10:
        if reason in ["perfect_weather", "warm", "chilly"]:
            reason = "wind"
            score = 0
        elif reason in ["cold", "hot"]:
            reason = "wind"
            score -= 3

    if precipitation_probability > 70 and reason in ["perfect_weather", "warm", "chilly"]:
        score -= 1
        reason = "cloudy"

    if 1 < precipitation <= 5 and score >= -2:
        return {"score": score, "status": "take_umbrella", "reason": "rain"}

    if score >= 3:
        status = "go_out"
        if reason == "perfect_weather" or (18 <= temp <= 25 and precipitation == 0 and  precipitation_probability <= 70):
            reason = "perfect_weather"
    elif score >= 2:
        status = "nice_walk"
    elif score >= 0:
        status = "short_walk"
    elif score >= -2:
        status = "take_umbrella"
        if reason == "perfect_weather":
            reason = "rain"
    else:
        status = "stay_home"

    return {"score": score, "status": status, "reason": reason}


def status_display(status: str, reason: str) -> dict[str, str]:
    return {
        "status": status,
        "status_label": STATUS_LABELS.get(status, status.replace("_", " ").title()),
        "reason": reason,
        "reason_label": REASON_LABELS.get(reason, reason.replace("_", " ").title()),
        "emoji": STATUS_EMOJI.get(status, ""),
        "color": STATUS_COLORS.get(status, "#64748b"),
    }