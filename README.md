# Swiss Weather Dashboard (Flask + Open‑Meteo MeteoSwiss ICON)

Small Flask web app that fetches Swiss weather data from Open‑Meteo’s **MeteoSwiss ICON** models, processes it server-side, and presents it in a simple dashboard with charts.

Data source docs: https://open-meteo.com/en/docs/meteoswiss-api

## Run

Create a virtualenv and install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Start the server:

```bash
python app.py
```

Open:
- http://127.0.0.1:5000

## Endpoints

- `/` dashboard
- `/api/cities` list available Swiss cities
- `/api/weather?city=zurich` processed dashboard JSON

