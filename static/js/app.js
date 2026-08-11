const state = {
  scoreChart: null,
  inputChart: null,
  map: null,
  markerLayer: null,
  autoRefreshTimer: null,
};

function renderUnavailableState(node, message) {
  if (!node) return;
  const tagName = node.tagName?.toLowerCase();
  if (tagName === "canvas") {
    const parent = node.parentElement;
    if (!parent) return;

    let fallback = parent.querySelector("[data-fallback-for='" + node.id + "']");
    if (!fallback) {
      fallback = document.createElement("div");
      fallback.dataset.fallbackFor = node.id;
      fallback.className = "empty-state";
      parent.appendChild(fallback);
    }
    node.style.display = "none";
    fallback.innerHTML = `<strong>${message}</strong>`;
    return;
  }

  node.innerHTML = `
    <div class="empty-state">
      <strong>${message}</strong>
    </div>
  `;
}

function titleCase(value) {
  return String(value || "")
    .split(" ")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function setStatus(message, kind = "idle") {
  const banner = document.getElementById("statusBanner");
  if (!banner) return;

  banner.textContent = message;
  banner.classList.remove("is-loading", "is-error");
  if (kind === "loading" || kind === "warning") banner.classList.add("is-loading");
  if (kind === "error") banner.classList.add("is-error");
}

function updateDashboardVisibility(data) {
  const panel = document.getElementById("dashboardPanel");
  if (!panel) return;

  const hasData = Boolean(data);
  panel.classList.toggle("has-data", hasData);
  panel.classList.toggle("is-empty", !hasData);
}

function updateDatasetInfo(dataset) {
  const countNode = document.getElementById("summaryDatasetCount");
  if (countNode) {
    countNode.textContent = dataset?.record_count ?? 0;
  }
}

function renderBestMatch(best) {
  const node = document.getElementById("bestMatchCard");
  if (!node) return;

  if (!best) {
    node.innerHTML = `
      <div class="empty-state">
        <strong>No shelters available.</strong>
        <div class="mt-2">Adjust criteria to find available shelters.</div>
      </div>
    `;
    return;
  }

  const isAltBadge = best.is_alternative
    ? `<span class="tag-pill" style="background: rgba(255, 183, 3, 0.18); color: #ffd000;">⚠️ Alternative Recommendation (Farther / Capacity Limit)</span>`
    : `<span class="tag-pill" style="background: rgba(16, 185, 129, 0.18); color: #34d399;">✓ Direct Scenario Match</span>`;

  node.innerHTML = `
    <div class="best-header">
      <div>
        <p class="eyebrow mb-1">Top Ranked Match</p>
        <h2 class="best-title">${best.name}</h2>
        <div class="best-meta">
          <span class="meta-pill">📍 ${best.distance} km away</span>
          <span class="meta-pill">🛏️ ${best.available_beds} beds available</span>
          <span class="meta-pill">♿ ${titleCase(best.accessibility)} access</span>
        </div>
      </div>
      <div class="best-score">${best.score}</div>
    </div>
    <div class="best-tags">
      ${isAltBadge}
      <span class="tag-pill">Elevation: ${titleCase(best.elevation_level)}</span>
      <span class="tag-pill">Water Proximity: ${titleCase(best.proximity_to_water)}</span>
      <span class="tag-pill">Medical: ${titleCase(best.medical_facility)}</span>
    </div>
  `;
}

function renderSummary(summary) {
  document.getElementById("summaryCount").textContent = summary?.count ?? 0;
  document.getElementById("summaryDistance").textContent = `${summary?.max_distance_km ?? 0} km`;
  document.getElementById("summaryAccessibility").textContent = titleCase(summary?.requested_accessibility || "-");
}

function renderResults(recommendations) {
  const node = document.getElementById("resultsList");
  if (!node) return;

  if (!recommendations || recommendations.length === 0) {
    node.innerHTML = `
      <div class="empty-state">
        <strong>No shelters found nearby.</strong>
        <div class="mt-2">Try increasing travel distance or bed capacity requirements.</div>
      </div>
    `;
    return;
  }

  node.innerHTML = recommendations
    .map(
      (shelter, index) => `
        <article class="result-item">
          <div class="result-head">
            <div>
              <span class="result-rank">Rank #${index + 1}</span>
              <h4 class="result-name">${shelter.name}</h4>
            </div>
            <div class="result-score">${shelter.score}</div>
          </div>
          <div class="score-track">
            <div class="score-fill" style="width: ${shelter.score}%"></div>
          </div>
          <div class="result-line">
            📍 ${shelter.distance} km away, 🛏️ ${shelter.available_beds} beds free, ♿ ${titleCase(shelter.accessibility)} access
          </div>
          <div class="result-tags">
            ${
              shelter.is_alternative
                ? '<span class="mini-tag" style="background: rgba(255, 183, 3, 0.18); color: #ffd000; font-weight: 700;">⚠️ Alternative Recommendation</span>'
                : '<span class="mini-tag" style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-weight: 700;">✓ Direct Match</span>'
            }
            <span class="mini-tag">Elevation ${titleCase(shelter.elevation_level)}</span>
            <span class="mini-tag">Water ${titleCase(shelter.proximity_to_water)}</span>
            <span class="mini-tag">Medical ${titleCase(shelter.medical_facility)}</span>
          </div>
        </article>
      `
    )
    .join("");
}

function destroyChart(chartRef) {
  if (chartRef) {
    chartRef.destroy();
  }
}

function buildScoreChart(recommendations) {
  const canvas = document.getElementById("scoreChart");
  if (!canvas) return;

  if (typeof Chart === "undefined") {
    renderUnavailableState(canvas, "Score chart unavailable because Chart.js did not load.");
    return;
  }

  canvas.style.display = "";
  canvas.parentElement?.querySelector("[data-fallback-for='scoreChart']")?.remove();

  destroyChart(state.scoreChart);
  if (!recommendations || recommendations.length === 0) {
    state.scoreChart = null;
    return;
  }

  state.scoreChart = new Chart(canvas, {
    type: "bar",
    data: {
      labels: recommendations.map((item) => item.name),
      datasets: [
        {
          data: recommendations.map((item) => item.score),
          borderRadius: 8,
          backgroundColor: recommendations.map((item) =>
            item.is_alternative ? "#ffb703" : "#00f2fe"
          ),
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: {
          ticks: { color: "#94a3b8" },
          grid: { display: false },
        },
        y: {
          beginAtZero: true,
          max: 100,
          ticks: { color: "#94a3b8" },
          grid: { color: "rgba(56, 189, 248, 0.12)" },
        },
      },
    },
  });
}

function buildInputChart(inputs) {
  const canvas = document.getElementById("inputChart");
  if (!canvas) return;

  if (typeof Chart === "undefined") {
    renderUnavailableState(canvas, "Input chart unavailable because Chart.js did not load.");
    return;
  }

  canvas.style.display = "";
  canvas.parentElement?.querySelector("[data-fallback-for='inputChart']")?.remove();

  destroyChart(state.inputChart);
  if (!inputs) {
    state.inputChart = null;
    return;
  }

  state.inputChart = new Chart(canvas, {
    type: "radar",
    data: {
      labels: ["Distance", "Accessibility", "Elevation", "Water Proximity", "Medical"],
      datasets: [
        {
          data: [
            inputs.distance || 0,
            inputs.accessibility || 0,
            inputs.elevation || 0,
            inputs.proximity || 0,
            inputs.medical || 0,
          ],
          fill: true,
          backgroundColor: "rgba(0, 242, 254, 0.16)",
          borderColor: "#00f2fe",
          pointBackgroundColor: "#ffb703",
          pointBorderColor: "#050b14",
          pointRadius: 5,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        r: {
          suggestedMin: 0,
          suggestedMax: 10,
          ticks: {
            stepSize: 2,
            color: "#94a3b8",
            backdropColor: "transparent",
          },
          grid: { color: "rgba(56, 189, 248, 0.14)" },
          angleLines: { color: "rgba(56, 189, 248, 0.14)" },
          pointLabels: { color: "#f0f7ff", font: { family: "Outfit", size: 12 } },
        },
      },
    },
  });
}

function ensureMap() {
  if (typeof L === "undefined") {
    return null;
  }

  if (state.map) return state.map;

  state.map = L.map("map", {
    zoomControl: false,
  }).setView([20.306, 85.82], 12);

  L.control.zoom({ position: "bottomright" }).addTo(state.map);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(state.map);

  state.markerLayer = L.layerGroup().addTo(state.map);
  return state.map;
}

function buildMap(recommendations) {
  const mapNode = document.getElementById("map");
  if (!mapNode) return;

  const map = ensureMap();
  if (!map) {
    renderUnavailableState(mapNode, "Map unavailable because Leaflet did not load.");
    return;
  }

  state.markerLayer.clearLayers();

  if (!recommendations || recommendations.length === 0) {
    map.setView([20.306, 85.82], 12);
    return;
  }

  const bounds = [];
  recommendations.forEach((item, index) => {
    const marker = L.marker([item.lat, item.lng]).addTo(state.markerLayer);
    const tagText = item.is_alternative ? "⚠️ Alternative Recommendation" : "✓ Direct Match";
    marker.bindPopup(
      `<strong>${item.name}</strong><br/>${tagText}<br/>Rank #${index + 1}<br/>Score: ${item.score}<br/>Distance: ${item.distance} km<br/>Beds Free: ${item.available_beds}`
    );
    bounds.push([item.lat, item.lng]);
  });

  if (bounds.length === 1) {
    map.setView(bounds[0], 13);
  } else {
    map.fitBounds(bounds, { padding: [28, 28] });
  }

  setTimeout(() => map.invalidateSize(), 120);
}

function renderDashboard(data) {
  updateDashboardVisibility(data);
  updateDatasetInfo(data?.dataset || window.DATASET_INFO || null);
  renderBestMatch(data?.best || null);
  renderSummary(data?.summary || null);
  renderResults(data?.recommendations || []);
  buildScoreChart(data?.recommendations || []);
  buildInputChart(data?.inputs_numeric || null);
  buildMap(data?.recommendations || []);

  if (data?.summary?.notice_message) {
    setStatus(data.summary.notice_message, "warning");
  } else if (data?.recommendations?.length) {
    setStatus(`Updated ${data.recommendations.length} shelter recommendations.`, "idle");
  }
}

function serializeForm(form) {
  const formData = new FormData(form);
  return {
    num_people: Number(formData.get("num_people")),
    distance_level: formData.get("distance_level"),
    accessibility_required: formData.get("accessibility_required"),
    elevation_input: formData.get("elevation_input"),
    proximity_input: formData.get("proximity_input"),
    medical_input: formData.get("medical_input"),
  };
}

async function fetchRecommendations(form) {
  const payload = serializeForm(form);
  if (!Number.isInteger(payload.num_people) || payload.num_people < 1) {
    setStatus("People count must be a whole number greater than zero.", "error");
    return;
  }

  setStatus("Recomputing fuzzy ranking...", "loading");

  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify(payload),
    });

    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      const text = await response.text();
      console.error("Non-JSON response received:", text);
      throw new Error(`Server returned ${response.status} ${response.statusText} as HTML. Check server logs.`);
    }

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Request failed.");
    }

    renderDashboard(data);
  } catch (error) {
    console.error("Recommendation error:", error);
    setStatus(error.message, "error");
  }
}

function scheduleRefresh(form) {
  window.clearTimeout(state.autoRefreshTimer);
  state.autoRefreshTimer = window.setTimeout(() => {
    fetchRecommendations(form).catch((error) => {
      setStatus(error.message, "error");
    });
  }, 260);
}

function resetForm(form) {
  form.reset();
  form.querySelector("#num_people").value = "1";
  scheduleRefresh(form);
}

(() => {
  const form = document.getElementById("recommendForm");
  if (!form) return;

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    fetchRecommendations(form).catch((error) => {
      setStatus(error.message, "error");
    });
  });

  form.addEventListener("input", (event) => {
    if (event.target.matches("input, select")) {
      scheduleRefresh(form);
    }
  });

  form.addEventListener("change", (event) => {
    if (event.target.matches("select")) {
      scheduleRefresh(form);
    }
  });

  document.getElementById("resetButton")?.addEventListener("click", () => resetForm(form));

  if (window.RECOMMENDATION_DATA) {
    renderDashboard(window.RECOMMENDATION_DATA);
  } else {
    renderDashboard(null);
  }
})();
