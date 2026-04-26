const siteGps = {
  Jeddah_Airport: { lat: 21.6702, lng: 39.1525, label: "Jeddah Airport" },
  Pilgrim_Country_Airport: { lat: 24.7136, lng: 46.6753, label: "Pilgrim Country Airport" },
  Makkah_Arrival_Hub: { lat: 21.4858, lng: 39.1925, label: "Makkah Arrival Hub" },
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
  Sacrifice_Zone: { lat: 21.4212, lng: 39.8974, label: "Sacrifice Zone" },
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
  ["Jeddah_Airport", "Makkah_Arrival_Hub", "Masjid_al_Haram_Perimeter", "Tawaf_Area", "Mina_West_Gate", "Mina_Camps_Core", "Arafat_Main_Field", "Muzdalifah_Open_Area", "Jamarat_Complex", "Sacrifice_Zone"],
  ["Mina_Camp_4", "Jamarat_Bridge", "Jamarat_Complex", "Sacrifice_Zone", "Mina_Camps_Core"],
  ["Aziziyah_Zone", "Shade_Corridor", "Transit_Corridor", "Muzdalifah_Open_Area"]
];

const initialLocationOptions = [
  "Jeddah_Airport",
  "Pilgrim_Country_Airport",
  "Makkah_Arrival_Hub",
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
  "Jeddah_Airport",
  "Pilgrim_Country_Airport",
  "Makkah_Arrival_Hub",
  "Mina_Camp_1",
  "Mina_Camp_2",
  "Mina_Camp_4",
  "Mina_Camps_Core",
  "Sacrifice_Zone",
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
const rosterSearchInput = document.querySelector("#rosterSearchInput");
const groupFilterSelect = document.querySelector("#groupFilter");
const healthFilterSelect = document.querySelector("#healthFilter");
const riskFilterSelect = document.querySelector("#riskFilter");
const sortRosterSelect = document.querySelector("#sortRosterSelect");
const applyRosterFiltersButton = document.querySelector("#applyRosterFilters");
const applyRosterSortButton = document.querySelector("#applyRosterSort");
const clearRosterFiltersButton = document.querySelector("#clearRosterFilters");
const rosterMeta = document.querySelector("#rosterMeta");
const manualForm = document.querySelector("#manualForm");
const randomForm = document.querySelector("#randomForm");
const environmentForm = document.querySelector("#environmentForm");
const environmentTick = document.querySelector("#environmentTick");
const environmentDayLabel = document.querySelector("#environmentDayLabel");
const environmentLocationLabel = document.querySelector("#environmentLocationLabel");
const environmentRitualLabel = document.querySelector("#environmentRitualLabel");
const environmentNextRitualLabel = document.querySelector("#environmentNextRitualLabel");
const startSimulationButton = document.querySelector("#startSimulationButton");
const pauseSimulationButton = document.querySelector("#pauseSimulationButton");
const playbackSpeedSelect = document.querySelector("#playbackSpeedSelect");
const resetDaysButton = document.querySelector("#resetDaysButton");
const restartDashboardButton = document.querySelector("#restartDashboardButton");
const analyticsChartCanvas = document.querySelector("#analyticsChart");

let agents = [];
let map;
let siteLayerGroup;
let mapLayerGroup;
let routeLayerGroup;
let heatLayer;
let analyticsChart;
let agentMarkers = new Map();
let currentEnvironment = null;
let summaryHistory = [];
let mapHasInitialFit = false;
let playbackTimer = null;
let simulationBusy = false;
let routeLayersReady = false;

const rosterFilters = {
  searchQuery: "",
  groupId: "all",
  health: "all",
  risk: "all",
  sortMode: "default"
};

const NODE_PRESSURE_BASELINES = {
  Kaaba: 10,
  Masjid_al_Haram_Perimeter: 16,
  Tawaf_Area: 9,
  Sai_Corridor: 12,
  Aziziyah_Zone: 18,
  Makkah_Bus_Station: 14,
  Mina_Camp_1: 16,
  Mina_Camp_2: 16,
  Mina_Camp_4: 14,
  Mina_Camps_Core: 22,
  Mina_West_Gate: 12,
  Mina_East_Gate: 12,
  Jamarat_Bridge: 10,
  Jamarat_Complex: 13,
  Jamarat: 10,
  Arafat_Gate: 12,
  Arafat_Main_Field: 28,
  Arafat: 26,
  Muzdalifah_Open_Area: 24,
  Muzdalifah: 20,
  Cooling_Station_1: 8,
  Shade_Corridor: 9,
  Shade_Corridor_2: 9,
  Transit_Corridor: 10,
  Medical_Post_1: 7,
  Security_Checkpoint_1: 8,
  Emergency_Point_1: 6,
  Emergency_Point_2: 6,
  Field_Hospital: 8,
  Police_Assist_Point: 7,
  Emergency_Point: 6
};

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
  populateSelectOptions(manualForm, "initial_node", initialLocationOptions, "Jeddah_Airport");
  populateSelectOptions(manualForm, "target_node", targetLocationOptions, "Arafat_Main_Field");
  populateSelectOptions(environmentForm, "hazard", hazardOptions, "none");
  populateSelectOptions(environmentForm, "group_location", groupLocationOptions, "Jeddah_Airport");
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

  if (stress >= 88 || fatigue >= 86 || hydration <= 28) {
    return "high_risk";
  }
  if (stress >= 62 || fatigue >= 58 || hydration <= 62) {
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

function buildPilgrimIcon(status) {
  return L.divIcon({
    className: "pilgrim-icon-wrapper",
    iconSize: [22, 30],
    iconAnchor: [11, 24],
    popupAnchor: [0, -20],
    html:
      `<div class="pilgrim-marker ${status}">` +
      `<span class="pilgrim-head"></span>` +
      `<span class="pilgrim-body"></span>` +
      `</div>`
  });
}

function getPlaybackDelay() {
  return Number(playbackSpeedSelect?.value || 800);
}

function setPlaybackState(isPlaying) {
  if (startSimulationButton) {
    startSimulationButton.disabled = isPlaying;
  }
  if (pauseSimulationButton) {
    pauseSimulationButton.disabled = !isPlaying;
  }
}

function stopPlayback() {
  if (playbackTimer) {
    clearInterval(playbackTimer);
    playbackTimer = null;
  }
  setPlaybackState(false);
}

function renderSummary(summary) {
  summaryCards.innerHTML = "";
  const currentLocationLabel =
    siteGps[summary.leading_current_location]?.label ||
    summary.leading_current_location ||
    "None";

  const overviewItems = [
    ["Current day", summary.simulation_day_label],
    ["Current location", currentLocationLabel],
    ["Current ritual", summary.current_ritual || "None"],
    ["Next ritual", summary.next_ritual || "None"]
  ];

  const operationsItems = [
    ["Total agents", summary.total_agents],
    ["Stable", summary.stable_agents],
    ["Need support", summary.needs_support_agents],
    ["High risk", summary.high_risk_agents],
    ["Panicking", summary.panicking_agents],
    ["Ritual tick", summary.simulation_tick],
    ["Severity index", `${summary.severity_index}%`],
    ["Avg stress", summary.avg_stress],
    ["Avg hydration", summary.avg_hydration]
  ];

  [
    ["Summary Overview", overviewItems],
    ["Operational Snapshot", operationsItems]
  ].forEach(([title, items]) => {
    const section = document.createElement("section");
    section.className = "summary-section";
    section.innerHTML = `<h3 class="summary-section-title">${title}</h3>`;

    const grid = document.createElement("div");
    grid.className = "summary-grid";

    items.forEach(([label, value]) => {
      const row = document.createElement("div");
      row.className = "summary-row";
      row.innerHTML = `
        <span class="summary-label">${label}</span>
        <strong class="summary-value">${value}</strong>
      `;
      grid.appendChild(row);
    });

    section.appendChild(grid);
    summaryCards.appendChild(section);
  });
}

function ensureMap() {
  if (map) {
    return;
  }

  map = L.map(mapCanvas, {
    zoomControl: true,
    minZoom: 9,
    maxZoom: 18
  }).setView([21.49, 39.56], 10);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  routeLayerGroup = L.layerGroup().addTo(map);
  siteLayerGroup = L.layerGroup().addTo(map);
  mapLayerGroup = L.layerGroup().addTo(map);
  renderRoutes();
  renderSiteMarkers();
}

function ensureAirportVisible(currentAgents, environment) {
  if (!map || !siteGps.Jeddah_Airport) {
    return;
  }

  const routePoints = holyRoutes[0]
    .map((nodeId) => siteGps[nodeId])
    .filter(Boolean)
    .map((site) => [site.lat, site.lng]);

  currentAgents.forEach((agent) => {
    const site = siteGps[agent.state.current_node];
    if (site) {
      routePoints.push([site.lat, site.lng]);
    }
  });

  if (routePoints.length < 2) {
    return;
  }

  const airportLatLng = L.latLng(siteGps.Jeddah_Airport.lat, siteGps.Jeddah_Airport.lng);
  const routeBounds = L.latLngBounds(routePoints);
  const airportIsActive =
    environment?.group_location === "Jeddah_Airport" ||
    currentAgents.some((agent) => agent.state.current_node === "Jeddah_Airport");

  if (!mapHasInitialFit || (airportIsActive && !map.getBounds().pad(-0.08).contains(airportLatLng))) {
    map.fitBounds(routeBounds, {
      padding: [28, 28],
      maxZoom: 10
    });
    mapHasInitialFit = true;
  }
}

function renderMap(currentAgents, environment) {
  ensureMap();
  const visibleAgents = getDisplayedAgents(currentAgents);
  renderHeatmap(visibleAgents, environment);
  renderAgentMarkers(visibleAgents);

  ensureAirportVisible(currentAgents, environment);
}

function renderRoutes() {
  if (routeLayersReady) {
    return;
  }
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
  routeLayersReady = true;
}

function renderSiteMarkers() {
  siteLayerGroup.clearLayers();
  Object.entries(siteGps).forEach(([nodeId, site]) => {
    const marker = L.marker([site.lat, site.lng], { title: site.label });
    marker.bindTooltip(site.label, { direction: "top" });
    marker.addTo(siteLayerGroup);
    marker.on("click", () => focusNodeAgents(nodeId));
  });
}

function getMarkerLatLng(agent, index) {
  const node = agent.state.current_node;
  const base = siteGps[node] || { lat: 21.392, lng: 39.924, label: "Fallback" };
  return L.latLng(
    base.lat + jitter(index, 0.0018),
    base.lng + jitter(index + 11, 0.0022)
  );
}

function animateMarkerTo(marker, targetLatLng, duration = 420) {
  const start = marker.getLatLng();
  const startTime = performance.now();

  function step(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const lat = start.lat + (targetLatLng.lat - start.lat) * eased;
    const lng = start.lng + (targetLatLng.lng - start.lng) * eased;
    marker.setLatLng([lat, lng]);
    if (progress < 1) {
      requestAnimationFrame(step);
    }
  }

  requestAnimationFrame(step);
}

function renderAgentMarkers(visibleAgents) {
  const visibleIds = new Set(visibleAgents.map((agent) => agent.profile.pilgrim_id));
  agentMarkers.forEach((marker, agentId) => {
    if (!visibleIds.has(agentId)) {
      mapLayerGroup.removeLayer(marker);
      agentMarkers.delete(agentId);
    }
  });

  visibleAgents.forEach((agent, index) => {
    const node = agent.state.current_node;
    const base = siteGps[node] || { lat: 21.392, lng: 39.924, label: "Fallback" };
    const status = getAgentStatus(agent);
    const latLng = getMarkerLatLng(agent, index);
    const hoverStatus = status.replaceAll("_", " ");
    const popupHtml =
      `<strong>${agent.profile.pilgrim_id}</strong><br>${base.label}<br>` +
      `Stress: ${agent.state.stress.toFixed(1)} | Fatigue: ${agent.state.fatigue.toFixed(1)}`;
    const tooltipHtml =
      `<strong>${agent.profile.pilgrim_id}</strong><br>${agent.profile.nationality}<br>` +
      `Status: ${hoverStatus}<br>Stress: ${agent.state.stress.toFixed(1)}`;

    let marker = agentMarkers.get(agent.profile.pilgrim_id);
    if (!marker) {
      marker = L.marker(latLng, {
        icon: buildPilgrimIcon(status),
        title: agent.profile.pilgrim_id
      });
      marker.bindTooltip(tooltipHtml, {
        direction: "top",
        offset: [0, -8],
        opacity: 0.95,
        sticky: true,
        className: "agent-hover-tooltip"
      });
      marker.bindPopup(popupHtml);
      marker.addTo(mapLayerGroup);
      marker.on("mouseover", () => marker.openTooltip());
      marker.on("click", () => {
        marker.openPopup();
        scrollToAgent(agent.profile.pilgrim_id);
      });
      agentMarkers.set(agent.profile.pilgrim_id, marker);
      return;
    }

    marker.setIcon(buildPilgrimIcon(status));
    marker.setTooltipContent(tooltipHtml);
    marker.setPopupContent(popupHtml);
    animateMarkerTo(marker, latLng);
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

  const densityValue = Number(environment?.density || 5);
  const normalizedDensity = 0.75 + (Math.max(0, Math.min(10, densityValue)) / 10) * 0.6;
  const hazardMultiplier = ["crowd_bottleneck", "stampede_risk", "route_congestion"].includes(environment?.hazard)
    ? 1.18
    : 1;
  const heatPoints = Object.entries(countsByNode)
    .map(([nodeId, count]) => {
      const site = siteGps[nodeId];
      if (!site) {
        return null;
      }
      const nodeCapacity = NODE_PRESSURE_BASELINES[nodeId] || 12;
      const pressure = (count / nodeCapacity) * normalizedDensity * hazardMultiplier;
      if (pressure < 0.18) {
        return null;
      }
      const weight = Math.min(1, pressure);
      return [site.lat, site.lng, weight];
    })
    .filter(Boolean);

  if (!heatPoints.length) {
    return;
  }

  heatLayer = L.heatLayer(heatPoints, {
    radius: 26,
    blur: 20,
    maxZoom: 15,
    gradient: {
      0.18: "#6baed6",
      0.38: "#9fd38b",
      0.58: "#f2c45a",
      0.78: "#ec7b45",
      1.0: "#c73a2b"
    }
  });
  heatLayer.addTo(map);
}

function populateGroupFilterOptions(currentAgents) {
  if (!groupFilterSelect) {
    return;
  }

  const availableGroups = [...new Set(
    currentAgents
      .map((agent) => agent.profile.group_id)
      .filter(Boolean)
  )].sort((a, b) => a.localeCompare(b));

  groupFilterSelect.innerHTML = "";

  const allOption = document.createElement("option");
  allOption.value = "all";
  allOption.textContent = "All groups";
  groupFilterSelect.appendChild(allOption);

  availableGroups.forEach((groupId) => {
    const option = document.createElement("option");
    option.value = groupId;
    option.textContent = groupId;
    groupFilterSelect.appendChild(option);
  });

  if (!availableGroups.includes(rosterFilters.groupId)) {
    rosterFilters.groupId = "all";
  }

  groupFilterSelect.value = rosterFilters.groupId;
}

function syncSortControl() {
  if (!sortRosterSelect) {
    return;
  }
  sortRosterSelect.value = rosterFilters.sortMode;
}

function getDisplayedAgents(currentAgents) {
  const filteredAgents = currentAgents.filter((agent) => {
    const searchQuery = rosterFilters.searchQuery.trim().toLowerCase();
    const searchableFields = [
      agent.profile.pilgrim_id,
      agent.profile.nationality,
      agent.profile.group_id
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    const matchesSearch = !searchQuery || searchableFields.includes(searchQuery);
    const matchesGroup = rosterFilters.groupId === "all" || agent.profile.group_id === rosterFilters.groupId;
    const matchesHealth = rosterFilters.health === "all" || agent.profile.health_status === rosterFilters.health;
    const matchesRisk = rosterFilters.risk === "all" || getAgentStatus(agent) === rosterFilters.risk;
    return matchesSearch && matchesGroup && matchesHealth && matchesRisk;
  });

  switch (rosterFilters.sortMode) {
    case "stress_desc":
      return filteredAgents.sort((a, b) => Number(b.state.stress || 0) - Number(a.state.stress || 0));
    case "stress_asc":
      return filteredAgents.sort((a, b) => Number(a.state.stress || 0) - Number(b.state.stress || 0));
    case "hydration_desc":
      return filteredAgents.sort((a, b) => Number(b.state.hydration || 0) - Number(a.state.hydration || 0));
    case "hydration_asc":
      return filteredAgents.sort((a, b) => Number(a.state.hydration || 0) - Number(b.state.hydration || 0));
    default:
      return filteredAgents;
  }
}

function updateRosterMeta(visibleCount, totalCount) {
  if (!rosterMeta) {
    return;
  }

  rosterMeta.textContent = `Showing ${visibleCount} of ${totalCount} pilgrims`;
}

function renderAgents(currentAgents) {
  const visibleAgents = getDisplayedAgents(currentAgents);
  agentGrid.innerHTML = "";

  if (!visibleAgents.length) {
    updateRosterMeta(0, currentAgents.length);
    agentGrid.innerHTML = `<div class="roster-empty">No pilgrims match the current filters.</div>`;
    return;
  }

  visibleAgents.forEach((agent) => {
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
    card.tabIndex = 0;
    card.setAttribute("role", "button");
    card.setAttribute("title", "Focus this pilgrim on the map");
    fragment.querySelector(".agent-id").textContent = agent.profile.pilgrim_id;
    fragment.querySelector(".agent-title").textContent = `${agent.profile.nationality} pilgrim`;
    fragment.querySelector(".status-pill").textContent = status;

    const miniStats = fragment.querySelector(".mini-stats");
    miniStats.innerHTML = [
      statBlock("Age", agent.profile.age),
      statBlock("Stress", agent.state.stress.toFixed(1)),
      statBlock("Hydration", agent.state.hydration.toFixed(1))
    ].join("");

    const detailGrid = fragment.querySelector(".detail-grid");
    const ritualProgress = agent.memory.long_term.ritual_progress || [];
    const ritualSchedule = agent.memory.long_term.ritual_schedule || [];
    const completedRitualCount = ritualSchedule.filter((step) => ritualProgress.includes(step.progress_key)).length;
    detailGrid.innerHTML = [
      detailBlock("Current day", agent.state.ritual_day_label || "Upon Arrival in Jeddah"),
      detailBlock("Current ritual", agent.state.current_ritual || "Not Started"),
      detailBlock("Next ritual", agent.state.next_ritual || "Tawaf Al-Qudoum (Arrival Tawaf)"),
      detailBlock("Next ritual day", agent.state.next_ritual_day_label || "Upon Arrival in Jeddah"),
      detailBlock("Schedule status", agent.state.ritual_window_open ? "Ready on this tick" : "Waiting for next tick"),
      detailBlock("Current location", siteGps[agent.state.current_node]?.label || agent.state.current_node),
      detailBlock("Ritual location", siteGps[agent.state.target_node]?.label || agent.state.target_node),
      detailBlock("Group", agent.profile.group_id),
      detailBlock("Mobility", agent.profile.mobility),
      detailBlock("Language", agent.profile.language),
      detailBlock("Sacrifice", agent.profile.performs_sacrifice ? "Participating" : "Optional skip"),
      detailBlock("Fatigue", agent.state.fatigue.toFixed(1)),
      detailBlock("Ritual progress", `${completedRitualCount}/${ritualSchedule.length || 0} complete`),
      detailBlock("Memory", (agent.memory.short_term.recent_nodes || []).join(", ") || "Fresh agent"),
      detailBlock("Conditions", (agent.profile.chronic_conditions || []).join(", ") || "None")
    ].join("");

    card.addEventListener("click", () => {
      focusAgentOnMap(agent.profile.pilgrim_id);
    });
    card.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        focusAgentOnMap(agent.profile.pilgrim_id);
      }
    });

    agentGrid.appendChild(fragment);
  });

  updateRosterMeta(visibleAgents.length, currentAgents.length);
}

function renderChart(history) {
  const labels = history.map((entry) => `Tick ${entry.simulation_tick}`);
  const stressSeries = history.map((entry) => Number(entry.avg_stress || 0));
  const supportSeries = history.map((entry) => Number(entry.needs_support_agents || 0));
  const highRiskSeries = history.map((entry) => Number(entry.high_risk_agents || 0));
  const panickingSeries = history.map((entry) => Number(entry.panicking_agents || 0));

  if (!analyticsChart) {
    analyticsChart = new Chart(analyticsChartCanvas, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Average stress",
            data: stressSeries,
            borderColor: "rgba(32, 106, 78, 1)",
            backgroundColor: "rgba(32, 106, 78, 0.12)",
            yAxisID: "y",
            tension: 0.28,
            fill: true
          },
          {
            label: "Needs support",
            data: supportSeries,
            borderColor: "rgba(166, 114, 49, 1)",
            backgroundColor: "rgba(166, 114, 49, 0.08)",
            yAxisID: "y1",
            tension: 0.28
          },
          {
            label: "High risk",
            data: highRiskSeries,
            borderColor: "rgba(194, 64, 47, 1)",
            backgroundColor: "rgba(194, 64, 47, 0.08)",
            yAxisID: "y1",
            tension: 0.28
          },
          {
            label: "Panicking",
            data: panickingSeries,
            borderColor: "rgba(109, 63, 209, 1)",
            backgroundColor: "rgba(109, 63, 209, 0.08)",
            yAxisID: "y1",
            tension: 0.28
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true }
        },
        scales: {
          y: {
            position: "left",
            beginAtZero: true,
            suggestedMax: 100,
            title: {
              display: true,
              text: "Average stress"
            }
          },
          y1: {
            position: "right",
            beginAtZero: true,
            ticks: { precision: 0 },
            grid: {
              drawOnChartArea: false
            },
            title: {
              display: true,
              text: "Pilgrim count"
            }
          }
        }
      }
    });
    return;
  }

  analyticsChart.data.labels = labels;
  analyticsChart.data.datasets[0].data = stressSeries;
  analyticsChart.data.datasets[1].data = supportSeries;
  analyticsChart.data.datasets[2].data = highRiskSeries;
  analyticsChart.data.datasets[3].data = panickingSeries;
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
  const visibleAgents = getDisplayedAgents(agents);
  const matching = visibleAgents.filter((agent) => agent.state.current_node === nodeId);
  const fallback = agents.filter((agent) => agent.state.current_node === nodeId);
  const targetAgents = matching.length ? matching : fallback;
  if (!targetAgents.length) {
    return;
  }
  scrollToAgent(targetAgents[0].profile.pilgrim_id);
}

function jitter(seed, amount) {
  return ((Math.sin(seed * 12.9898) * 43758.5453) % 1) * amount;
}

function getManualPayload() {
  const data = new FormData(manualForm);
  const payload = Object.fromEntries(data.entries());
  payload.chronic_conditions = data.getAll("chronic_conditions").filter(Boolean);
  payload.performs_sacrifice = manualForm.elements.performs_sacrifice.checked;
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
  manualForm.initial_node.value = "Jeddah_Airport";
  manualForm.target_node.value = "Arafat_Main_Field";
  manualForm.elements.performs_sacrifice.checked = true;
  const chronicConditions = manualForm.elements.chronic_conditions;
  if (chronicConditions) {
    [...chronicConditions.options].forEach((option) => {
      option.selected = false;
    });
  }
}

function applyRosterFilters() {
  rosterFilters.searchQuery = rosterSearchInput?.value || "";
  rosterFilters.groupId = groupFilterSelect?.value || "all";
  rosterFilters.health = healthFilterSelect?.value || "all";
  rosterFilters.risk = riskFilterSelect?.value || "all";
  rosterFilters.sortMode = sortRosterSelect?.value || "default";
  renderAgents(agents);
  if (currentEnvironment) {
    renderMap(agents, currentEnvironment);
  }
}

function applyRosterSort() {
  rosterFilters.sortMode = sortRosterSelect?.value || "default";
  renderAgents(agents);
}

function clearRosterFilters() {
  rosterFilters.searchQuery = "";
  rosterFilters.groupId = "all";
  rosterFilters.health = "all";
  rosterFilters.risk = "all";
  rosterFilters.sortMode = "default";

  if (rosterSearchInput) {
    rosterSearchInput.value = "";
  }
  if (groupFilterSelect) {
    groupFilterSelect.value = "all";
  }
  if (healthFilterSelect) {
    healthFilterSelect.value = "all";
  }
  if (riskFilterSelect) {
    riskFilterSelect.value = "all";
  }
  if (sortRosterSelect) {
    sortRosterSelect.value = "default";
  }
  renderAgents(agents);
  if (currentEnvironment) {
    renderMap(agents, currentEnvironment);
  }
}

populateNationalityOptions();
syncLanguageWithNationality();
initializeScenarioOptions();
syncSortControl();

function applyEnvironmentForm(environment) {
  environmentForm.density.value = environment.density;
  environmentForm.temperature.value = environment.temperature;
  environmentForm.hazard.value = environment.hazard || "none";
  environmentForm.group_location.value = environment.group_location;
  environmentForm.alternate_node.value = environment.alternate_node;
  environmentForm.panic_node.value = environment.panic_node;
  environmentTick.textContent = environment.tick;
  if (environmentDayLabel) {
    environmentDayLabel.textContent = environment.simulation_day_label;
  }
  if (environmentLocationLabel) {
    environmentLocationLabel.textContent =
      siteGps[environment.group_location]?.label || environment.group_location || "None";
  }
  if (environmentRitualLabel) {
    environmentRitualLabel.textContent = environment.current_ritual || "Not Started";
  }
  if (environmentNextRitualLabel) {
    environmentNextRitualLabel.textContent = environment.next_ritual || "Tawaf Al-Qudoum (Arrival Tawaf)";
  }
}

function focusAgentOnMap(agentId) {
  ensureMap();

  const marker = agentMarkers.get(agentId);
  if (marker) {
    const latLng = marker.getLatLng();
    map.flyTo(latLng, Math.max(map.getZoom(), 13), {
      animate: true,
      duration: 0.9
    });
    marker.openPopup();
    marker.openTooltip();
    mapCanvas?.scrollIntoView({ behavior: "smooth", block: "center" });
    return;
  }

  const agent = agents.find((item) => item.profile.pilgrim_id === agentId);
  if (!agent) {
    return;
  }

  const site = siteGps[agent.state.current_node];
  if (!site) {
    return;
  }

  map.flyTo([site.lat, site.lng], Math.max(map.getZoom(), 13), {
    animate: true,
    duration: 0.9
  });
  mapCanvas?.scrollIntoView({ behavior: "smooth", block: "center" });
}

async function refreshAll() {
  const [agentResponse, summaryResponse, environmentResponse] = await Promise.all([
    fetchJson("/api/agents"),
    fetchJson("/api/summary"),
    fetchJson("/api/environment")
  ]);

  agents = agentResponse.agents;
  summaryHistory = summaryResponse.history || [];
  currentEnvironment = environmentResponse.environment;
  populateGroupFilterOptions(agents);
  renderSummary(summaryResponse.summary);
  renderMap(agents, currentEnvironment);
  renderAgents(agents);
  renderChart(summaryHistory);
  applyEnvironmentForm(environmentResponse.environment);
}

async function runSimulationStep() {
  if (simulationBusy) {
    return;
  }

  simulationBusy = true;
  try {
    await fetchJson("/api/simulate/step", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getEnvironmentPayload())
    });
    await refreshAll();
  } finally {
    simulationBusy = false;
  }
}

function startPlayback() {
  if (playbackTimer) {
    clearInterval(playbackTimer);
  }

  setPlaybackState(true);
  playbackTimer = setInterval(() => {
    runSimulationStep().catch((error) => {
      stopPlayback();
      summaryCards.innerHTML = `<div class="stat-card"><strong>Error</strong><span>${error.message}</span></div>`;
    });
  }, getPlaybackDelay());
}

applyRosterFiltersButton?.addEventListener("click", applyRosterFilters);
applyRosterSortButton?.addEventListener("click", applyRosterSort);
clearRosterFiltersButton?.addEventListener("click", clearRosterFilters);
rosterSearchInput?.addEventListener("input", applyRosterFilters);
groupFilterSelect?.addEventListener("change", applyRosterFilters);
healthFilterSelect?.addEventListener("change", applyRosterFilters);
riskFilterSelect?.addEventListener("change", applyRosterFilters);
sortRosterSelect?.addEventListener("change", applyRosterFilters);

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
  await runSimulationStep();
});

startSimulationButton?.addEventListener("click", () => {
  startPlayback();
});

pauseSimulationButton?.addEventListener("click", () => {
  stopPlayback();
});

playbackSpeedSelect?.addEventListener("change", () => {
  if (playbackTimer) {
    startPlayback();
  }
});

resetDaysButton?.addEventListener("click", async () => {
  stopPlayback();
  await fetchJson("/api/simulate/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({})
  });

  await refreshAll();
});

restartDashboardButton?.addEventListener("click", async () => {
  stopPlayback();
  await fetchJson("/api/dashboard/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({})
  });

  resetManualDefaults();
  clearRosterFilters();
  await refreshAll();
});

setPlaybackState(false);
refreshAll().catch((error) => {
  summaryCards.innerHTML = `<div class="stat-card"><strong>Error</strong><span>${error.message}</span></div>`;
});
