const siteGps = {
  Kaaba: { lat: 21.4225, lng: 39.8262, label: "Al Kaabah" },
  Masjid_al_Haram_Perimeter: { lat: 21.4202, lng: 39.8279, label: "Masjid al-Haram Perimeter" },
  Tawaf_Area: { lat: 21.4227, lng: 39.8263, label: "Tawaf Area" },
  Sai_Corridor: { lat: 21.4244, lng: 39.8291, label: "Sa'i Corridor" },
  Aziziyah_Zone: { lat: 21.3971, lng: 39.8754, label: "Aziziyah Zone" },
  Makkah_Bus_Station: { lat: 21.4298, lng: 39.8059, label: "Makkah Bus Station" },
  Mina_Camp_1: { lat: 21.4209, lng: 39.8952, label: "Mina Camp 1" },
  Mina_Camp_2: { lat: 21.4188, lng: 39.9003, label: "Mina Camp 2" },
  Mina_Camp_4: { lat: 21.4159, lng: 39.9055, label: "Mina Camp 4" },
  Mina_Camps_Core: { lat: 21.4174, lng: 39.9018, label: "Mina Camps Core" },
  Mina_West_Gate: { lat: 21.4217, lng: 39.8888, label: "Mina West Gate" },
  Mina_East_Gate: { lat: 21.4139, lng: 39.9135, label: "Mina East Gate" },
  Jamarat_Bridge: { lat: 21.4235, lng: 39.8939, label: "Jamarat Bridge" },
  Jamarat_Complex: { lat: 21.424, lng: 39.8928, label: "Jamarat Complex" },
  Jamarat: { lat: 21.4231, lng: 39.8942, label: "Jamarat" },
  Arafat_Gate: { lat: 21.3744, lng: 39.9528, label: "Arafat Gate" },
  Arafat_Main_Field: { lat: 21.3559, lng: 39.9832, label: "Arafat Main Field" },
  Arafat: { lat: 21.3548, lng: 39.9847, label: "Arafat" },
  Muzdalifah_Open_Area: { lat: 21.3892, lng: 39.9465, label: "Muzdalifah Open Area" },
  Muzdalifah: { lat: 21.3899, lng: 39.9448, label: "Muzdalifah" },
  Cooling_Station_1: { lat: 21.4012, lng: 39.9168, label: "Cooling Station 1" },
  Shade_Corridor: { lat: 21.4045, lng: 39.919, label: "Shade Corridor" },
  Shade_Corridor_2: { lat: 21.4005, lng: 39.9231, label: "Shade Corridor 2" },
  Transit_Corridor: { lat: 21.3961, lng: 39.9322, label: "Transit Corridor" },
  Medical_Post_1: { lat: 21.4064, lng: 39.9098, label: "Medical Post 1" },
  Security_Checkpoint_1: { lat: 21.4101, lng: 39.9072, label: "Security Checkpoint 1" },
  Emergency_Point_1: { lat: 21.4087, lng: 39.9114, label: "Emergency Point 1" },
  Emergency_Point_2: { lat: 21.4038, lng: 39.9177, label: "Emergency Point 2" },
  Field_Hospital: { lat: 21.4068, lng: 39.9059, label: "Field Hospital" },
  Police_Assist_Point: { lat: 21.4113, lng: 39.9042, label: "Police Assist Point" },
  Emergency_Point: { lat: 21.4087, lng: 39.9114, label: "Emergency Point" }
};

const holyRoutes = [
  ["Kaaba", "Masjid_al_Haram_Perimeter", "Mina_West_Gate", "Mina_Camps_Core", "Arafat_Main_Field", "Muzdalifah_Open_Area", "Jamarat_Complex", "Kaaba"],
  ["Mina_Camp_4", "Jamarat_Bridge", "Arafat_Gate", "Arafat_Main_Field"],
  ["Aziziyah_Zone", "Shade_Corridor", "Transit_Corridor", "Muzdalifah_Open_Area"]
];

const initialLocationOptions = [
  "Masjid_al_Haram_Perimeter",
  "Aziziyah_Zone",
  "Makkah_Bus_Station",
  "Mina_West_Gate",
  "Mina_East_Gate",
  "Mina_Camp_1",
  "Mina_Camp_2",
  "Mina_Camp_4",
  "Mina_Camps_Core",
  "Jamarat_Bridge",
  "Arafat_Gate",
  "Muzdalifah"
];

const targetLocationOptions = [
  "Tawaf_Area",
  "Sai_Corridor",
  "Mina_Camps_Core",
  "Jamarat_Complex",
  "Arafat_Main_Field",
  "Muzdalifah_Open_Area",
  "Arafat",
  "Muzdalifah",
  "Jamarat"
];

const hazardOptions = [
  "none",
  "extreme_heat",
  "route_congestion",
  "stampede_risk",
  "medical_overload",
  "transport_delay",
  "lost_group_member",
  "heat_stress",
  "crowd_bottleneck",
  "medical_incident",
  "route_closure"
];

const groupLocationOptions = [
  "Mina_Camp_1",
  "Mina_Camp_2",
  "Mina_Camp_4",
  "Mina_Camps_Core",
  "Jamarat_Bridge",
  "Jamarat_Complex",
  "Arafat_Gate",
  "Arafat_Main_Field",
  "Muzdalifah_Open_Area",
  "Medical_Post_1",
  "Field_Hospital",
  "Masjid_al_Haram_Perimeter"
];

const alternateNodeOptions = [
  "Cooling_Station_1",
  "Shade_Corridor",
  "Shade_Corridor_2",
  "Transit_Corridor",
  "Medical_Post_1",
  "Security_Checkpoint_1",
  "Mina_Camp_2",
  "Arafat_Gate"
];

const panicNodeOptions = [
  "Emergency_Point_1",
  "Emergency_Point_2",
  "Field_Hospital",
  "Police_Assist_Point",
  "Emergency_Point",
  "Mina_Camp_1",
  "Jamarat_Bridge"
];

const STATUS_COLORS = {
  stable: "#2b865f",
  needs_support: "#a67231",
  high_risk: "#c2402f",
  panicking: "#6d3fd1"
};

const allCountries = [
  "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia",
  "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium",
  "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria",
  "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad",
  "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica", "Cote d'Ivoire", "Croatia", "Cuba", "Cyprus",
  "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic",
  "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji",
  "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala",
  "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran",
  "Iraq", "Ireland", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati",
  "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein",
  "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands",
  "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco",
  "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger",
  "Nigeria", "North Korea", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama",
  "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia",
  "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino",
  "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore",
  "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain",
  "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Tajikistan", "Tanzania", "Thailand",
  "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda",
  "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu",
  "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe", "Kosovo"
];

const countryLanguageMap = {
  "Saudi Arabia": "Arabic",
  "Egypt": "Arabic",
  "Morocco": "Arabic",
  "Algeria": "Arabic",
  "Tunisia": "Arabic",
  "Jordan": "Arabic",
  "Iraq": "Arabic",
  "Syria": "Arabic",
  "Lebanon": "Arabic",
  "Yemen": "Arabic",
  "Palestine": "Arabic",
  "United Arab Emirates": "Arabic",
  "Qatar": "Arabic",
  "Kuwait": "Arabic",
  "Oman": "Arabic",
  "Bahrain": "Arabic",
  "Pakistan": "Urdu",
  "India": "Hindi",
  "Bangladesh": "Bengali",
  "Indonesia": "Bahasa Indonesia",
  "Turkey": "Turkish",
  "Malaysia": "Malay",
  "Nigeria": "English",
  "United States": "English",
  "United Kingdom": "English"
};

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

function populateNationalityOptions() {
  const nationalitySelect = manualForm.elements.nationality;
  if (!nationalitySelect) {
    return;
  }

  nationalitySelect.innerHTML = "";
  const sortedCountries = [...allCountries].sort((a, b) => a.localeCompare(b));

  sortedCountries.forEach((country) => {
    const option = document.createElement("option");
    option.value = country;
    option.textContent = country;
    nationalitySelect.appendChild(option);
  });

  nationalitySelect.value = "Saudi Arabia";
}

function syncLanguageWithNationality() {
  const nationalitySelect = manualForm.elements.nationality;
  const languageSelect = manualForm.elements.language;
  if (!nationalitySelect || !languageSelect) {
    return;
  }

  nationalitySelect.addEventListener("change", () => {
    const language = countryLanguageMap[nationalitySelect.value] || "English";
    if ([...languageSelect.options].some((item) => item.value === language)) {
      languageSelect.value = language;
    } else {
      languageSelect.value = "English";
    }
  });
}

function populateSelectOptions(formRef, name, options, defaultValue) {
  const select = formRef?.elements?.[name];
  if (!select) {
    return;
  }

  select.innerHTML = "";
  options.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });

  if (defaultValue && options.includes(defaultValue)) {
    select.value = defaultValue;
  }
}

function initializeScenarioOptions() {
  populateSelectOptions(manualForm, "initial_node", initialLocationOptions, "Mina_Camp_4");
  populateSelectOptions(manualForm, "target_node", targetLocationOptions, "Arafat_Main_Field");
  populateSelectOptions(environmentForm, "hazard", hazardOptions, "none");
  populateSelectOptions(environmentForm, "group_location", groupLocationOptions, "Mina_Camp_4");
  populateSelectOptions(environmentForm, "alternate_node", alternateNodeOptions, "Cooling_Station_1");
  populateSelectOptions(environmentForm, "panic_node", panicNodeOptions, "Emergency_Point_1");
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function deriveOperationalRisk(agent) {
  const stress = Number(agent.state.stress || 0);
  const fatigue = Number(agent.state.fatigue || 0);
  const hydration = Number(agent.state.hydration || 100);

  if (agent.state.is_panicking || stress >= 75 || fatigue >= 80 || hydration <= 35) {
    return "high_risk";
  }
  if (stress >= 55 || fatigue >= 60 || hydration <= 55) {
    return "needs_support";
  }
  return "stable";
}

function getAgentStatus(agent) {
  if (agent.state.is_panicking) {
    return "panicking";
  }
  return deriveOperationalRisk(agent);
}

function renderSummary(summary) {
  summaryCards.innerHTML = "";
  const items = [
    ["Total agents", summary.total_agents],
    ["Stable", summary.stable_agents],
    ["Need support", summary.needs_support_agents],
    ["High risk", summary.high_risk_agents],
    ["Panicking", summary.panicking_agents],
    ["Scenario tick", summary.simulation_tick],
    ["Severity index", `${summary.severity_index}%`],
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
    const status = getAgentStatus(agent);
    const moodColor = STATUS_COLORS[status] || STATUS_COLORS.stable;

    const lat = base.lat + jitter(index, 0.0018);
    const lng = base.lng + jitter(index + 11, 0.0022);

    const circle = L.circleMarker([lat, lng], {
      radius: 6,
      color: "#ffffff",
      weight: 1,
      fillColor: moodColor,
      fillOpacity: 0.9
    });

    const hoverStatus = status.replaceAll("_", " ");
    circle.bindTooltip(
      `<strong>${agent.profile.pilgrim_id}</strong><br>${agent.profile.nationality}<br>` +
      `Status: ${hoverStatus}<br>Stress: ${agent.state.stress.toFixed(1)}`,
      {
        direction: "top",
        offset: [0, -8],
        opacity: 0.95,
        sticky: true,
        className: "agent-hover-tooltip"
      }
    );

    circle.bindPopup(
      `<strong>${agent.profile.pilgrim_id}</strong><br>${base.label}<br>` +
      `Stress: ${agent.state.stress.toFixed(1)} | Fatigue: ${agent.state.fatigue.toFixed(1)}`
    );

    circle.addTo(mapLayerGroup);
    circle.on("mouseover", () => circle.openTooltip());
    circle.on("click", () => {
      circle.openPopup();
      scrollToAgent(agent.profile.pilgrim_id);
    });
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
    const statusKey = getAgentStatus(agent);
    const status = statusKey.replaceAll("_", " ");
    const riskClass = statusKey === "panicking"
      ? "risk-panicking"
      : statusKey === "high_risk"
      ? "risk-high"
      : statusKey === "needs_support"
        ? "risk-support"
        : "risk-stable";

    card.dataset.agentId = agent.profile.pilgrim_id;
    card.classList.add(riskClass);
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
  document.querySelectorAll(".agent-card-focus").forEach((item) => {
    item.classList.remove("agent-card-focus");
  });

  const card = document.querySelector(`[data-agent-id="${agentId}"]`);
  if (card) {
    card.scrollIntoView({ behavior: "smooth", block: "center" });
    card.classList.add("agent-card-focus");
    setTimeout(() => {
      card.classList.remove("agent-card-focus");
    }, 2200);
    card.animate(
      [
        { transform: "scale(1)", boxShadow: "0 0 0 rgba(0,0,0,0)" },
        { transform: "scale(1.03)", boxShadow: "0 22px 48px rgba(166, 75, 42, 0.25)" },
        { transform: "scale(1)", boxShadow: "0 0 0 rgba(0,0,0,0)" }
      ],
      { duration: 900, easing: "ease" }
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
  manualForm.nationality.value = "Saudi Arabia";
  manualForm.language.value = "Arabic";
  manualForm.mobility.value = "0.90";
  manualForm.risk_tolerance.value = "0.5";
  manualForm.initial_node.value = "Mina_Camp_4";
  manualForm.target_node.value = "Arafat_Main_Field";
}

populateNationalityOptions();
syncLanguageWithNationality();
initializeScenarioOptions();

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
