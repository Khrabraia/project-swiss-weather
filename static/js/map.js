(() => {
  const STATUS_COLORS = {
    walk: "#22c55e",
    ok: "#3b82f6",
    umbrella: "#f97316",
    stay_home: "#ef4444",
  };

  const REC_HOUR = 12;

  function getBootstrap() {
    const el = document.getElementById("bootstrap-data");
    if (!el) return {};
    try {
      return JSON.parse(el.textContent || "{}");
    } catch {
      return {};
    }
  }

  const bootstrap = getBootstrap();

  let map = null;
  let markerLayer = null;
  let mapDay = 0;
  let mapHour =
    typeof bootstrap.currentHour === "number" ? bootstrap.currentHour : new Date().getHours();
  let recDay = 0;
  let controlsBound = false;

  /** One fetch per day+hour; recommendations for that day come in the same response. */
  let weatherBundle = null;

  function formatHour(h) {
    return `${String(h).padStart(2, "0")}:00`;
  }

  function formatTemp(t) {
    const n = Number(t);
    return Number.isFinite(n) ? String(Math.round(n)) : "—";
  }

  function popupHtml(city, point, hour, dayLabel) {
    const time =
      hour !== undefined && hour !== null
        ? `${formatHour(hour)} · ${dayLabel || ""}`
        : "";
    return `
      <strong>${city.name}</strong><br/>
      ${time ? `${time}<br/>` : ""}
      Temperature: ${formatTemp(point.temp)}°C<br/>
      Rain: ${point.rain} mm<br/>
      Status: ${point.status} ${point.emoji}
    `;
  }

  function makeIcon(color) {
    return L.divIcon({
      className: "mapMarker",
      html: `<span style="background:${color}"></span>`,
      iconSize: [18, 18],
      iconAnchor: [9, 9],
    });
  }

  function ensureMap() {
    const el = document.getElementById("weatherMap");
    if (!el) return;
    if (map) return;

    map = L.map("weatherMap", { scrollWheelZoom: true }).setView([46.8, 8.2], 8);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
    }).addTo(map);
    markerLayer = L.layerGroup().addTo(map);
  }

  async function fetchWeatherBundle(day, hour) {
    const cacheKey = `${day}-${hour}`;
    if (weatherBundle && weatherBundle.key === cacheKey) {
      return weatherBundle.data;
    }

    const url = new URL("/weather", window.location.origin);
    url.searchParams.set("day", String(day));
    url.searchParams.set("hour", String(hour));
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to load weather data");
    const data = await res.json();
    weatherBundle = { key: cacheKey, data };
    return data;
  }

  /** Walk picks depend on day only — reuse bundle when we already fetched that day. */
  async function fetchBundleForDay(day) {
    const hourForMap = mapHour;
    if (weatherBundle && weatherBundle.key === `${day}-${hourForMap}`) {
      return weatherBundle.data;
    }
    return fetchWeatherBundle(day, hourForMap);
  }

  function renderMarkers(data) {
    ensureMap();
    if (!markerLayer) return;
    markerLayer.clearLayers();

    const displayHour = data.hour ?? mapHour;

    for (const city of data.cities) {
      const point = city.current || city.daily;
      const color = point.color || STATUS_COLORS[point.status] || "#64748b";
      const marker = L.marker([city.lat, city.lon], { icon: makeIcon(color) });
      marker.bindPopup(popupHtml(city, point, displayHour, data.day_label));
      marker.addTo(markerLayer);
    }

    const title = document.querySelector("#view-map .panel__title");
    if (title) {
      title.textContent = `Swiss cities · ${data.day_label} · ${formatHour(displayHour)}`;
    }

    if (map) {
      setTimeout(() => map.invalidateSize(), 100);
    }
  }

  function renderRecommendations(data, day) {
    const list = document.getElementById("recommendationsList");
    if (!list) return;

    const items = data.recommendations || [];
    const dayLabel = data.day_label || "";

    const title = document.querySelector("#view-recommendations .panel__title");
    if (title) {
      title.textContent = `Best cities to walk · ${dayLabel}`;
    }

    if (!items.length) {
      list.innerHTML = `<p class="recList__empty">No good walking days found for ${dayLabel}.</p>`;
      return;
    }

    list.innerHTML = items
      .map(
        (c, i) => `
        <article class="recCard">
          <div class="recCard__rank">#${i + 1}</div>
          <div class="recCard__body">
            <h3>${c.name} <span class="recCard__emoji">${c.emoji}</span></h3>
            <p class="recCard__status">${c.status} · ${formatHour(REC_HOUR)}</p>
            <p class="recCard__meta">
              ${formatTemp(c.temp)}°C · rain ${c.rain} mm · wind ${c.wind} m/s · clouds ${Math.round(c.cloud)}%
            </p>
          </div>
        </article>
      `
      )
      .join("");
  }

  function setMapLoading(loading) {
    const el = document.getElementById("weatherMap");
    if (!el) return;
    el.classList.toggle("map--loading", loading);
  }

  async function refreshMap() {
    setMapLoading(true);
    try {
      const data = await fetchWeatherBundle(mapDay, mapHour);
      renderMarkers(data);
    } finally {
      setMapLoading(false);
    }
  }

  function setActiveDayButtons(container, day) {
    if (!container) return;
    container.querySelectorAll(".dayBtn").forEach((btn) => {
      btn.classList.toggle("isActive", Number(btn.dataset.day) === day);
    });
  }

  function syncHourLabel() {
    const slider = document.getElementById("hourSlider");
    const hourLabel = document.getElementById("hourLabel");
    if (slider) mapHour = Number(slider.value);
    if (hourLabel) hourLabel.textContent = formatHour(mapHour);
  }

  function bindControls() {
    if (controlsBound) return;
    controlsBound = true;

    const mapDayBar = document.getElementById("mapDayBar");
    const recDayBar = document.getElementById("recDayBar");
    const slider = document.getElementById("hourSlider");

    mapDayBar?.addEventListener("click", (e) => {
      const btn = e.target.closest(".dayBtn");
      if (!btn || !mapDayBar.contains(btn)) return;
      mapDay = Number(btn.dataset.day);
      setActiveDayButtons(mapDayBar, mapDay);
      refreshMap().catch(console.error);
    });

    recDayBar?.addEventListener("click", (e) => {
      const btn = e.target.closest(".dayBtn");
      if (!btn || !recDayBar.contains(btn)) return;
      recDay = Number(btn.dataset.day);
      setActiveDayButtons(recDayBar, recDay);
      loadRecommendations(recDay).catch(console.error);
    });

    const onHourChange = () => {
      syncHourLabel();
      refreshMap().catch(console.error);
    };

    slider?.addEventListener("input", onHourChange);
    slider?.addEventListener("change", onHourChange);

    if (slider) slider.value = String(mapHour);
    syncHourLabel();
  }

  async function loadRecommendations(day) {
    const list = document.getElementById("recommendationsList");
    if (!list) return;

    list.innerHTML = `<p class="recList__loading">Loading…</p>`;
    try {
      const data = await fetchBundleForDay(day);
      renderRecommendations(data, day);
    } catch {
      list.innerHTML = `<p class="recList__error">Could not load recommendations.</p>`;
    }
  }

  window.WeatherMap = {
    init() {
      bindControls();
    },
    onViewShown(view) {
      if (view === "map") {
        setActiveDayButtons(document.getElementById("mapDayBar"), mapDay);
        syncHourLabel();
        refreshMap().catch(console.error);
      }
      if (view === "recommendations") {
        setActiveDayButtons(document.getElementById("recDayBar"), recDay);
        loadRecommendations(recDay).catch(console.error);
      }
    },
  };
})();
