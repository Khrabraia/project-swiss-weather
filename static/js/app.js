(() => {
  const citySelect = document.getElementById("citySelect");

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

  const chartColors = {
    text: "rgba(15, 23, 42, 0.65)",
    grid: "rgba(15, 23, 42, 0.08)",
    legend: "rgba(15, 23, 42, 0.8)",
    tempLine: "rgba(37, 99, 235, 0.95)",
    tempFill: "rgba(37, 99, 235, 0.12)",
    precipBar: "rgba(34, 197, 94, 0.35)",
    precipBorder: "rgba(34, 197, 94, 0.7)",
    probLine: "rgba(234, 179, 8, 0.9)",
    probFill: "rgba(234, 179, 8, 0.1)",
  };

  async function fetchCities() {
    const res = await fetch("/api/cities");
    if (!res.ok) throw new Error("Failed to load cities");
    return await res.json();
  }

  function getViewFromUrl() {
    const url = new URL(window.location.href);
    return url.searchParams.get("view") || bootstrap.activeView || "dashboard";
  }

  function setView(view, { pushState = true } = {}) {
    document.querySelectorAll(".viewTab").forEach((tab) => {
      tab.classList.toggle("isActive", tab.dataset.view === view);
    });
    document.querySelectorAll(".viewPanel").forEach((panel) => {
      const id = panel.id.replace("view-", "");
      panel.classList.toggle("isActive", id === view);
    });

    if (pushState) {
      const url = new URL(window.location.href);
      url.searchParams.set("view", view);
      window.history.replaceState({}, "", url);
    }

    if (window.WeatherMap?.onViewShown) {
      window.WeatherMap.onViewShown(view);
    }
  }

  function navigateCity(cityId) {
    const url = new URL(window.location.href);
    url.searchParams.set("city", cityId);
    window.location.assign(url.toString());
  }

  function createTempChart(series) {
    const ctx = document.getElementById("tempChart");
    if (!ctx) return null;
    return new Chart(ctx, {
      type: "line",
      data: {
        labels: series.labels,
        datasets: [
          {
            label: `Temp (${series.units.temperature})`,
            data: series.temperature,
            borderColor: chartColors.tempLine,
            backgroundColor: chartColors.tempFill,
            fill: true,
            tension: 0.3,
            pointRadius: 0,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: true, labels: { color: chartColors.legend } },
        },
        scales: {
          x: { ticks: { color: chartColors.text, maxTicksLimit: 8 } },
          y: { ticks: { color: chartColors.text }, grid: { color: chartColors.grid } },
        },
      },
    });
  }

  function createPrecipChart(series) {
    const ctx = document.getElementById("precipChart");
    if (!ctx) return null;
    return new Chart(ctx, {
      type: "bar",
      data: {
        labels: series.labels,
        datasets: [
          {
            label: `Precip (${series.units.precipitation})`,
            data: series.precipitation,
            backgroundColor: chartColors.precipBar,
            borderColor: chartColors.precipBorder,
            borderWidth: 1,
          },
          {
            label: `Prob (${series.units.precipitation_probability})`,
            data: series.precipitation_probability,
            type: "line",
            yAxisID: "y2",
            borderColor: chartColors.probLine,
            backgroundColor: chartColors.probFill,
            tension: 0.3,
            pointRadius: 0,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: true, labels: { color: chartColors.legend } },
        },
        scales: {
          x: { ticks: { color: chartColors.text, maxTicksLimit: 8 } },
          y: {
            ticks: { color: chartColors.text },
            grid: { color: chartColors.grid },
            title: { display: true, text: series.units.precipitation, color: chartColors.text },
          },
          y2: {
            position: "right",
            min: 0,
            max: 100,
            grid: { drawOnChartArea: false },
            ticks: { color: chartColors.text },
            title: {
              display: true,
              text: series.units.precipitation_probability,
              color: chartColors.text,
            },
          },
        },
      },
    });
  }

  function bindViewTabs() {
    document.querySelectorAll(".viewTab").forEach((tab) => {
      tab.addEventListener("click", () => setView(tab.dataset.view));
    });
  }

  async function init() {
    bindViewTabs();
    setView(getViewFromUrl(), { pushState: false });

    window.WeatherMap?.init?.();
    window.WeatherMap?.onViewShown?.(getViewFromUrl());

    if (!citySelect) return;

    const cities = await fetchCities();
    const currentCityId = (bootstrap.city && bootstrap.city.id) || "zurich";

    for (const c of cities) {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = c.name;
      if (c.id === currentCityId) opt.selected = true;
      citySelect.appendChild(opt);
    }

    citySelect.addEventListener("change", (e) => navigateCity(e.target.value));

    if (bootstrap.series24h) {
      createTempChart(bootstrap.series24h);
      createPrecipChart(bootstrap.series24h);
    }
  }

  init().catch((err) => {
    console.error(err);
  });
})();
