from __future__ import annotations

from typing import TypedDict


class City(TypedDict):
    id: str
    name: str
    lat: float
    lon: float


CITIES: list[City] = [
    {"id": "zurich", "name": "Zurich", "lat": 47.3769, "lon": 8.5417},
    {"id": "geneva", "name": "Geneva", "lat": 46.2044, "lon": 6.1432},
    {"id": "basel", "name": "Basel", "lat": 47.5596, "lon": 7.5886},
    {"id": "bern", "name": "Bern", "lat": 46.9480, "lon": 7.4474},
    {"id": "lausanne", "name": "Lausanne", "lat": 46.5197, "lon": 6.6323},
    {"id": "st_gallen", "name": "St. Gallen", "lat": 47.4245, "lon": 9.3767},
    {"id": "lugano", "name": "Lugano", "lat": 46.0037, "lon": 8.9511},
]

DEFAULT_CITY_ID = "zurich"


def list_cities() -> list[City]:
    return CITIES


def get_city(city_id: str) -> City:
    for c in CITIES:
        if c["id"] == city_id:
            return c
    return CITIES[0]

