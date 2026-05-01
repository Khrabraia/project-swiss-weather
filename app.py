from __future__ import annotations

import os

from flask import Flask, jsonify, redirect, render_template, request, url_for

from services.cities import DEFAULT_CITY_ID, get_city, list_cities
from services.weather_api import fetch_meteoswiss_forecast
from services.weather_processor import build_dashboard_view_model


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return redirect(url_for("dashboard"))

    @app.get("/dashboard")
    def dashboard():
        city_id = request.args.get("city", DEFAULT_CITY_ID)
        city = get_city(city_id)

        forecast = fetch_meteoswiss_forecast(
            latitude=city["lat"],
            longitude=city["lon"],
            timezone="Europe/Zurich",
            forecast_days=5,
        )
        vm = build_dashboard_view_model(city=city, forecast=forecast)
        return render_template("dashboard.html", active_page="dashboard", **vm)

    @app.get("/tables")
    def tables():
        city_id = request.args.get("city", DEFAULT_CITY_ID)
        city = get_city(city_id)

        forecast = fetch_meteoswiss_forecast(
            latitude=city["lat"],
            longitude=city["lon"],
            timezone="Europe/Zurich",
            forecast_days=5,
        )
        vm = build_dashboard_view_model(city=city, forecast=forecast)
        return render_template("tables.html", active_page="tables", **vm)

    @app.get("/api/cities")
    def api_cities():
        return jsonify(list_cities())

    @app.get("/api/weather")
    def api_weather():
        city_id = request.args.get("city", DEFAULT_CITY_ID)
        city = get_city(city_id)
        forecast = fetch_meteoswiss_forecast(
            latitude=city["lat"],
            longitude=city["lon"],
            timezone="Europe/Zurich",
            forecast_days=5,
        )
        vm = build_dashboard_view_model(city=city, forecast=forecast)
        return jsonify(vm)

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=True)
