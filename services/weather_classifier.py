from __future__ import annotations

WALK_LABELS = ("walk", "ok", "umbrella", "stay_home")

STATUS_EMOJI: dict[str, str] = {
    "walk": "🚶",
    "ok": "🙂",
    "umbrella": "☂️",
    "stay_home": "🏠",
}

STATUS_COLORS: dict[str, str] = {
    "walk": "#22c55e",
    "ok": "#3b82f6",
    "umbrella": "#f97316",
    "stay_home": "#ef4444",
}


def classify_weather(temp: float, rain: float, wind: float, cloud: float) -> tuple[int, str]:
    """
    Score weather for walking.

    wind: m/s
    rain: mm
    cloud: %
    """
    score = 0

    if 18 <= temp <= 25:
        score += 2
    if temp < 5 or temp > 30:
        score -= 2
    if rain > 1:
        score -= 3
    if wind > 8:
        score -= 1
    if cloud > 70:
        score -= 1

    if score >= 2:
        label = "walk"
    elif score >= 0:
        label = "ok"
    elif score >= -2:
        label = "umbrella"
    else:
        label = "stay_home"

    return score, label


def round_degrees(value: float | int | None) -> int:
    if value is None:
        return 0
    return int(round(float(value), 0))


def status_display(label: str) -> dict[str, str]:
    return {
        "status": label,
        "emoji": STATUS_EMOJI.get(label, ""),
        "color": STATUS_COLORS.get(label, "#64748b"),
    }
