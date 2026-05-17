# Swiss Weather Dashboard (Flask + Open‑Meteo MeteoSwiss ICON)

Small Flask web app that fetches Swiss weather data from Open‑Meteo’s **MeteoSwiss ICON** models, processes it server-side, and presents it in a simple dashboard with charts. The app also includes an interactive map that visualizes weather conditions across Swiss cities. Each location is color-coded based on how suitable the weather is for a walk, making it easy to quickly compare conditions across regions.

In addition to raw weather data and charts, the backend computes a walking suitability status for each city using factors such as temperature, precipitation, wind, and cloud cover.

The possible statuses are:

- **go_out** – ideal conditions for a walk  
- **nice_walk** – generally good weather  
- **short_walk** – acceptable, but not perfect  
- **take_umbrella** – rain likely  
- **stay_home** – better to stay indoors  

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

