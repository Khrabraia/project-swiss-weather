from __future__ import annotations

import os

from flask import Flask, jsonify, redirect, render_template, request, url_for

from services.cities import DEFAULT_CITY_ID, get_city, list_cities
from services.forecast_days import clamp_day_offset, current_local_hour, day_label, forecast_day_options
from services.forecast_cache import get_city_forecast
from services.map_weather import build_weather_bundle
from services.weather_processor import build_dashboard_view_model


def _city_view(city_id: str):
    city = get_city(city_id)
    forecast = get_city_forecast(city)
    return build_dashboard_view_model(city=city, forecast=forecast)


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        city_id = request.args.get("city", DEFAULT_CITY_ID)
        view = request.args.get("view", "dashboard")
        vm = _city_view(city_id)
        vm["active_view"] = view
        vm["forecast_days"] = forecast_day_options()
        vm["current_hour"] = current_local_hour()
        return render_template("weather.html", active_page="weather", **vm)

    @app.get("/dashboard")
    def dashboard():
        city = request.args.get("city", DEFAULT_CITY_ID)
        view = request.args.get("view", "dashboard")
        return redirect(url_for("index", city=city, view=view))

    @app.get("/tables")
    def tables():
        city = request.args.get("city", DEFAULT_CITY_ID)
        return redirect(url_for("index", city=city, view="table"))

    @app.get("/api/cities")
    def api_cities():
        return jsonify(list_cities())

    @app.get("/api/weather")
    def api_weather_city():
        city_id = request.args.get("city", DEFAULT_CITY_ID)
        return jsonify(_city_view(city_id))

    @app.get("/weather")
    def weather_all():
        day_offset = clamp_day_offset(request.args.get("day", 0, type=int))
        hour = request.args.get("hour", type=int)
        return jsonify(build_weather_bundle(day_offset=day_offset, hour=hour))

    @app.get("/api/recommendations")
    def api_recommendations():
        day_offset = clamp_day_offset(request.args.get("day", 0, type=int))
        bundle = build_weather_bundle(day_offset=day_offset, hour=12)
        return jsonify(
            {
                "day_offset": bundle["day_offset"],
                "day_label": bundle["day_label"],
                "recommendations": bundle["recommendations"],
            }
        )

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=True)
