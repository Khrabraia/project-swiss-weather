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

  async function fetchCities() {
    const res = await fetch("/api/cities");
    if (!res.ok) throw new Error("Failed to load cities");
    return await res.json();
  }

  function setQueryParam(key, value) {
    const url = new URL(window.location.href);
    url.searchParams.set(key, value);
    window.location.assign(url.toString());
  }

  function createTempChart(series) {
    const ctx = document.getElementById("tempChart");
    return new Chart(ctx, {
      type: "line",
      data: {
        labels: series.labels,
        datasets: [
          {
            label: `Temp (${series.units.temperature})`,
            data: series.temperature,
            borderColor: "rgba(104, 194, 255, 0.95)",
            backgroundColor: "rgba(104, 194, 255, 0.12)",
            fill: true,
            tension: 0.3,
            pointRadius: 0,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: true, labels: { color: "rgba(255,255,255,0.8)" } },
        },
        scales: {
          x: { ticks: { color: "rgba(255,255,255,0.6)", maxTicksLimit: 8 } },
          y: { ticks: { color: "rgba(255,255,255,0.6)" }, grid: { color: "rgba(255,255,255,0.08)" } },
        },
      },
    });
  }

  function createPrecipChart(series) {
    const ctx = document.getElementById("precipChart");
    return new Chart(ctx, {
      type: "bar",
      data: {
        labels: series.labels,
        datasets: [
          {
            label: `Precip (${series.units.precipitation})`,
            data: series.precipitation,
            backgroundColor: "rgba(156, 255, 150, 0.24)",
            borderColor: "rgba(156, 255, 150, 0.55)",
            borderWidth: 1,
          },
          {
            label: `Prob (${series.units.precipitation_probability})`,
            data: series.precipitation_probability,
            type: "line",
            yAxisID: "y2",
            borderColor: "rgba(255, 214, 102, 0.9)",
            backgroundColor: "rgba(255, 214, 102, 0.08)",
            tension: 0.3,
            pointRadius: 0,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: true, labels: { color: "rgba(255,255,255,0.8)" } },
        },
        scales: {
          x: { ticks: { color: "rgba(255,255,255,0.6)", maxTicksLimit: 8 } },
          y: {
            ticks: { color: "rgba(255,255,255,0.6)" },
            grid: { color: "rgba(255,255,255,0.08)" },
            title: { display: true, text: series.units.precipitation, color: "rgba(255,255,255,0.6)" },
          },
          y2: {
            position: "right",
            min: 0,
            max: 100,
            grid: { drawOnChartArea: false },
            ticks: { color: "rgba(255,255,255,0.6)" },
            title: { display: true, text: series.units.precipitation_probability, color: "rgba(255,255,255,0.6)" },
          },
        },
      },
    });
  }

  async function init() {
    const cities = await fetchCities();
    const currentCityId = (bootstrap.city && bootstrap.city.id) || "zurich";

    for (const c of cities) {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = c.name;
      if (c.id === currentCityId) opt.selected = true;
      citySelect.appendChild(opt);
    }

    citySelect.addEventListener("change", (e) => setQueryParam("city", e.target.value));

    if (bootstrap.series24h) {
      createTempChart(bootstrap.series24h);
      createPrecipChart(bootstrap.series24h);
    }
  }

  init().catch((err) => {
    // Avoid breaking the whole page; show minimal signal.
    console.error(err);
  });
})();

