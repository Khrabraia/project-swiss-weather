from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

FORECAST_DAY_COUNT = 5
TZ = ZoneInfo("Europe/Zurich")


def forecast_day_options() -> list[dict[str, int | str]]:
    today = datetime.now(TZ).date()
    days: list[dict[str, int | str]] = []
    for offset in range(FORECAST_DAY_COUNT):
        d = today + timedelta(days=offset)
        if offset == 0:
            label = "Today"
        elif offset == 1:
            label = "Tomorrow"
        else:
            label = d.strftime("%A")
        days.append({"offset": offset, "label": label})
    return days


def clamp_day_offset(offset: int) -> int:
    return max(0, min(FORECAST_DAY_COUNT - 1, int(offset)))


def current_local_hour() -> int:
    return datetime.now(TZ).hour


def day_label(offset: int) -> str:
    offset = clamp_day_offset(offset)
    for d in forecast_day_options():
        if d["offset"] == offset:
            return str(d["label"])
    return f"+{offset} days"
