# Swiss Weather and Walks (Flask + Open-Meteo MeteoSwiss ICON)

A small full-stack web application that combines a weather dashboard with smart recommendations for walking in Switzerland.

The app allows users to:
- view current weather and forecasts
- explore weather conditions across cities
- and quickly decide where it is best to go for a walk

Instead of manually analyzing forecasts, the app processes weather data and provides simple, clear suggestions.

## Features

- Weather dashboard with current conditions and forecasts
- 24-hour forecast starting from the current time
- Multi-day forecast
- Interactive map with color-coded cities
- Walking suitability status for each location
- "Walk Picks" — best cities for walking for each day

## Walking Suitability

The backend evaluates weather conditions using:
- temperature
- precipitation
- wind
- cloud cover

Based on this, each city gets a status:

- **go out** – ideal conditions for a walk  
- **nice walk** – generally good weather  
- **short walk** – acceptable, but not perfect  
- **take umbrella** – rain likely  
- **stay home** – better to stay indoors  

## Data Source

Open-Meteo MeteoSwiss ICON API:  
https://open-meteo.com/en/docs/meteoswiss-api

## Tech Stack

- Backend: Python (Flask)
- Frontend: JavaScript
- Data: Open-Meteo API

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

