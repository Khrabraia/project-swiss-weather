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
    {"id": "winterthur", "name": "Winterthur", "lat": 47.4988, "lon": 8.7237},
    {"id": "lucerne", "name": "Lucerne", "lat": 47.0502, "lon": 8.3093},
    {"id": "st_gallen", "name": "St. Gallen", "lat": 47.4245, "lon": 9.3767},
    {"id": "lugano", "name": "Lugano", "lat": 46.0037, "lon": 8.9511},
    {"id": "biel", "name": "Biel/Bienne", "lat": 47.1368, "lon": 7.2468},

    {"id": "interlaken", "name": "Interlaken", "lat": 46.6863, "lon": 7.8632},
    {"id": "zermatt", "name": "Zermatt", "lat": 46.0207, "lon": 7.7491},
    {"id": "davos", "name": "Davos", "lat": 46.8020, "lon": 9.8360},
    {"id": "st_moritz", "name": "St. Moritz", "lat": 46.4908, "lon": 9.8355},
    {"id": "sion", "name": "Sion", "lat": 46.2331, "lon": 7.3606},
    {"id": "chur", "name": "Chur", "lat": 46.8508, "lon": 9.5320},
    {"id": "arosa", "name": "Arosa", "lat": 46.7833, "lon": 9.6833},
    {"id": "grindelwald", "name": "Grindelwald", "lat": 46.6242, "lon": 8.0414},

    {"id": "thun", "name": "Thun", "lat": 46.7512, "lon": 7.6217},
    {"id": "fribourg", "name": "Fribourg", "lat": 46.8065, "lon": 7.1619},
    {"id": "neuchatel", "name": "Neuchatel", "lat": 46.9918, "lon": 6.9310},
    {"id": "schaffhausen", "name": "Schaffhausen", "lat": 47.6973, "lon": 8.6349},
    {"id": "zug", "name": "Zug", "lat": 47.1662, "lon": 8.5155},
    {"id": "altdorf", "name": "Altdorf", "lat": 46.8815, "lon": 8.6444},
    {"id": "bellinzona", "name": "Bellinzona", "lat": 46.1951, "lon": 9.0222},
    {"id": "montreux", "name": "Montreux", "lat": 46.4312, "lon": 6.9107}
]

DEFAULT_CITY_ID = "zurich"


def list_cities() -> list[City]:
    return CITIES


def get_city(city_id: str) -> City:
    for c in CITIES:
        if c["id"] == city_id:
            return c
    return CITIES[0]

