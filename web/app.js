const siteGps = {
  Kaaba: { lat: 21.4225, lng: 39.8262, label: "Al Kaabah" },
  Mina_Camp_1: { lat: 21.4209, lng: 39.8952, label: "Mina Camp 1" },
  Mina_Camp_2: { lat: 21.4188, lng: 39.9003, label: "Mina Camp 2" },
  Mina_Camp_4: { lat: 21.4159, lng: 39.9055, label: "Mina Camp 4" },
  Jamarat_Bridge: { lat: 21.4235, lng: 39.8939, label: "Jamarat Bridge" },
  Jamarat: { lat: 21.4231, lng: 39.8942, label: "Jamarat" },
  Arafat_Gate: { lat: 21.3744, lng: 39.9528, label: "Arafat Gate" },
  Arafat: { lat: 21.3548, lng: 39.9847, label: "Arafat" },
  Muzdalifah: { lat: 21.3899, lng: 39.9448, label: "Muzdalifah" },
  Shade_Corridor: { lat: 21.4045, lng: 39.919, label: "Shade Corridor" },
  Transit_Corridor: { lat: 21.3961, lng: 39.9322, label: "Transit Corridor" },
  Emergency_Point: { lat: 21.4087, lng: 39.9114, label: "Emergency Point" }
};

const holyRoutes = [
  ["Kaaba", "Mina_Camp_1", "Arafat", "Muzdalifah", "Jamarat", "Kaaba"],
  ["Mina_Camp_4", "Jamarat_Bridge", "Arafat_Gate", "Arafat"],
  ["Mina_Camp_2", "Shade_Corridor", "Transit_Corridor", "Muzdalifah"]
];

const summaryCards = document.querySelector("#summaryCards");
const mapCanvas = document.querySelector("#mapCanvas");
const agentGrid = document.querySelector("#agentGrid");
const agentCardTemplate = document.querySelector("#agentCardTemplate");
const manualForm = document.querySelector("#manualForm");
const randomForm = document.querySelector("#randomForm");
const environmentForm = document.querySelector("#environmentForm");
const environmentTick = document.querySelector("#environmentTick");
const analyticsChartCanvas = document.querySelector("#analyticsChart");

let agents = [];
let map;
let mapLayerGroup;
let routeLayerGroup;
let heatLayer;
let analyticsChart;

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function renderSummary(summary) {
  summaryCards.innerHTML = "";
  const items = [
    ["Total agents", summary.total_agents],
    ["Panicking", summary.panicking_agents],
    ["Need support", summary.needs_support_agents],
    ["High risk", summary.high_risk_agents],
    ["Avg stress", summary.avg_stress],
    ["Avg hydration", summary.avg_hydration]
  ];

  items.forEach(([label, value]) => {
    const card = document.createElement("div");
    card.className = "stat-card";
    card.innerHTML = `<strong>${value}</strong><span>${label}</span>`;
    summaryCards.appendChild(card);
  });
}

function ensureMap() {
  if (map) {
    return;
  }

  map = L.map(mapCanvas, {
    zoomControl: true,
    minZoom: 10,
    maxZoom: 18
  }).setView([21.392, 39.924], 12);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  routeLayerGroup = L.layerGroup().addTo(map);
  mapLayerGroup = L.layerGroup().addTo(map);
}

function renderMap(currentAgents, environment) {
  ensureMap();
  routeLayerGroup.clearLayers();
  mapLayerGroup.clearLayers();
  renderRoutes();
  renderHeatmap(currentAgents, environment);

  Object.entries(siteGps).forEach(([nodeId, site]) => {
    const marker = L.marker([site.lat, site.lng], { title: site.label });
    marker.bindTooltip(site.label, { direction: "top" });
    marker.addTo(mapLayerGroup);
    marker.on("click", () => focusNodeAgents(nodeId));
  });

  currentAgents.forEach((agent, index) => {
    const node = agent.state.current_node;
    const base = siteGps[node] || { lat: 21.392, lng: 39.924, label: "Fallback" };
    const moodColor = agent.state.is_panicking
      ? "#c2402f"
      : agent.profile.health_status === "stable"
        ? "#2b865f"
        : "#a67231";

    const lat = base.lat + jitter(index, 0.0018);
    const lng = base.lng + jitter(index + 11, 0.0022);

    const circle = L.circleMarker([lat, lng], {
      radius: 6,
      color: "#ffffff",
      weight: 1,
      fillColor: moodColor,
      fillOpacity: 0.9
    });

    circle.bindPopup(
      `<strong>${agent.profile.pilgrim_id}</strong><br>${base.label}<br>` +
      `Stress: ${agent.state.stress.toFixed(1)} | Fatigue: ${agent.state.fatigue.toFixed(1)}`
    );

    circle.addTo(mapLayerGroup);
    circle.on("click", () => scrollToAgent(agent.profile.pilgrim_id));
  });
}

function renderRoutes() {
  holyRoutes.forEach((route, idx) => {
    const points = route
      .map((nodeId) => siteGps[nodeId])
      .filter(Boolean)
      .map((site) => [site.lat, site.lng]);

    if (points.length < 2) {
      return;
    }

    const polyline = L.polyline(points, {
      color: idx === 0 ? "#006f54" : idx === 1 ? "#8a5b16" : "#1f5f9d",
      weight: 4,
      opacity: 0.65,
      dashArray: idx === 0 ? "" : "7 8",
      lineCap: "round"
    });
    polyline.bindTooltip(`Route ${idx + 1}`, { sticky: true });
    polyline.addTo(routeLayerGroup);
  });
}

function renderHeatmap(currentAgents, environment) {
  if (typeof L.heatLayer !== "function") {
    return;
  }

  if (heatLayer) {
    map.removeLayer(heatLayer);
  }

  const countsByNode = {};
  currentAgents.forEach((agent) => {
    const node = agent.state.current_node;
    countsByNode[node] = (countsByNode[node] || 0) + 1;
  });

  const maxCount = Math.max(1, ...Object.values(countsByNode));
  const densityScale = Math.max(0.2, Math.min(1.6, Number(environment?.density || 5) / 5));
  const heatPoints = Object.entries(countsByNode)
    .map(([nodeId, count]) => {
      const site = siteGps[nodeId];
      if (!site) {
        return null;
      }
      const weight = Math.min(1, (count / maxCount) * densityScale);
      return [site.lat, site.lng, weight];
    })
    .filter(Boolean);

  heatLayer = L.heatLayer(heatPoints, {
    radius: 34,
    blur: 24,
    maxZoom: 15,
    gradient: {
      0.2: "#2b83ba",
      0.4: "#abdda4",
      0.6: "#fdae61",
      0.85: "#f46d43",
      1.0: "#d73027"
    }
  });
  heatLayer.addTo(map);
}

function renderAgents(currentAgents) {
  agentGrid.innerHTML = "";

  currentAgents.forEach((agent) => {
    const fragment = agentCardTemplate.content.cloneNode(true);
    const card = fragment.querySelector(".agent-card");
    const status = agent.state.is_panicking ? "Panicking" : agent.profile.health_status.replaceAll("_", " ");

    card.dataset.agentId = agent.profile.pilgrim_id;
    fragment.querySelector(".agent-id").textContent = agent.profile.pilgrim_id;
    fragment.querySelector(".agent-title").textContent = `${agent.profile.nationality} pilgrim`;
    fragment.querySelector(".status-pill").textContent = status;

    const miniStats = fragment.querySelector(".mini-stats");
    miniStats.innerHTML = [
      statBlock("Age", agent.profile.age),
      statBlock("Stress", agent.state.stress.toFixed(1)),
      statBlock("Fatigue", agent.state.fatigue.toFixed(1))
    ].join("");

    const detailGrid = fragment.querySelector(".detail-grid");
    detailGrid.innerHTML = [
      detailBlock("Route", `${agent.state.current_node} -> ${agent.state.target_node}`),
      detailBlock("Group", agent.profile.group_id),
      detailBlock("Mobility", agent.profile.mobility),
      detailBlock("Language", agent.profile.language),
      detailBlock("Memory", (agent.memory.short_term.recent_nodes || []).join(", ") || "Fresh agent"),
      detailBlock("Conditions", (agent.profile.chronic_conditions || []).join(", ") || "None")
    ].join("");

    agentGrid.appendChild(fragment);
  });
}

function renderChart(currentAgents) {
  const counts = {};

  currentAgents.forEach((agent) => {
    const node = agent.state.current_node;
    counts[node] = (counts[node] || 0) + 1;
  });

  const sortedEntries = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 8);
  const labels = sortedEntries.map(([node]) => siteGps[node]?.label || node.replaceAll("_", " "));
  const values = sortedEntries.map(([, count]) => count);

  if (!analyticsChart) {
    analyticsChart = new Chart(analyticsChartCanvas, {
      type: "bar",
      data: {
        labels,
        datasets: [{
          label: "Pilgrims per location",
          data: values,
          backgroundColor: "rgba(43, 134, 95, 0.75)",
          borderColor: "rgba(25, 77, 55, 1)",
          borderWidth: 1,
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 }
          }
        }
      }
    });
    return;
  }

  analyticsChart.data.labels = labels;
  analyticsChart.data.datasets[0].data = values;
  analyticsChart.update();
}

function statBlock(label, value) {
  return `<div class="mini-stat"><span>${label}</span><strong>${value}</strong></div>`;
}

function detailBlock(label, value) {
  return `<div class="detail-item"><span>${label}</span><strong>${value}</strong></div>`;
}

function scrollToAgent(agentId) {
  const card = document.querySelector(`[data-agent-id="${agentId}"]`);
  if (card) {
    card.scrollIntoView({ behavior: "smooth", block: "center" });
    card.animate(
      [
        { transform: "scale(1)", boxShadow: "0 0 0 rgba(0,0,0,0)" },
        { transform: "scale(1.02)", boxShadow: "0 18px 40px rgba(166, 75, 42, 0.18)" },
        { transform: "scale(1)", boxShadow: "0 0 0 rgba(0,0,0,0)" }
      ],
      { duration: 650, easing: "ease" }
    );
  }
}

function focusNodeAgents(nodeId) {
  const matching = agents.filter((agent) => agent.state.current_node === nodeId);
  if (!matching.length) {
    return;
  }
  scrollToAgent(matching[0].profile.pilgrim_id);
}

function jitter(seed, amount) {
  return ((Math.sin(seed * 12.9898) * 43758.5453) % 1) * amount;
}

function getManualPayload() {
  const data = new FormData(manualForm);
  const payload = Object.fromEntries(data.entries());
  payload.chronic_conditions = data.getAll("chronic_conditions").filter(Boolean);
  return payload;
}

function getEnvironmentPayload() {
  return Object.fromEntries(new FormData(environmentForm).entries());
}

function resetManualDefaults() {
  manualForm.reset();
  manualForm.group_id.value = "G_200";
  manualForm.age.value = "38";
  manualForm.health_status.value = "stable";
  manualForm.nationality.value = "Saudi";
  manualForm.language.value = "Arabic";
  manualForm.mobility.value = "0.90";
  manualForm.risk_tolerance.value = "0.5";
  manualForm.initial_node.value = "Mina_Camp_4";
  manualForm.target_node.value = "Arafat";
}

function applyEnvironmentForm(environment) {
  environmentForm.density.value = environment.density;
  environmentForm.temperature.value = environment.temperature;
  environmentForm.hazard.value = environment.hazard;
  environmentForm.group_location.value = environment.group_location;
  environmentForm.alternate_node.value = environment.alternate_node;
  environmentForm.panic_node.value = environment.panic_node;
  environmentTick.textContent = environment.tick;
}

async function refreshAll() {
  const [agentResponse, summary, environmentResponse] = await Promise.all([
    fetchJson("/api/agents"),
    fetchJson("/api/summary"),
    fetchJson("/api/environment")
  ]);

  agents = agentResponse.agents;
  renderSummary(summary);
  renderMap(agents, environmentResponse.environment);
  renderAgents(agents);
  renderChart(agents);
  applyEnvironmentForm(environmentResponse.environment);
}

manualForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formPayload = getManualPayload();

  await fetchJson("/api/agents", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formPayload)
  });

  resetManualDefaults();
  await refreshAll();
});

randomForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = Object.fromEntries(new FormData(randomForm).entries());

  await fetchJson("/api/agents/random", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData)
  });

  await refreshAll();
});

environmentForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = getEnvironmentPayload();

  await fetchJson("/api/simulate/step", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  await refreshAll();
});

refreshAll().catch((error) => {
  summaryCards.innerHTML = `<div class="stat-card"><strong>Error</strong><span>${error.message}</span></div>`;
});
