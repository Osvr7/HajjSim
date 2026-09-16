// ============================================================
// Static configuration data
// ------------------------------------------------------------
// This block defines map coordinates, route overlays, form option lists,
// status colors, countries, and language defaults used by the dashboard.
// ============================================================

// Geographic coordinates for every simulation node displayed on the Leaflet map.
const siteGps = {
  // Global simulation start: the Hajj Terminal at King Abdulaziz International
  // Airport (KAIA), not a generic Jeddah point. The node id stays
  // "Jeddah_Airport" for backward compatibility with every other reference in
  // the codebase; only the displayed coordinates/label changed.
  Jeddah_Airport: { lat: 21.6796, lng: 39.1565, label: "KAIA Hajj Terminal" },
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

// Route overlays shown on the map so users can see major movement corridors.
const holyRoutes = [
  ["Jeddah_Airport", "Makkah_Arrival_Hub", "Masjid_al_Haram_Perimeter", "Tawaf_Area", "Mina_West_Gate", "Mina_Camps_Core", "Arafat_Main_Field", "Muzdalifah_Open_Area", "Jamarat_Complex", "Sacrifice_Zone"],
  ["Mina_Camp_4", "Jamarat_Bridge", "Jamarat_Complex", "Sacrifice_Zone", "Mina_Camps_Core"],
  ["Aziziyah_Zone", "Shade_Corridor", "Transit_Corridor", "Muzdalifah_Open_Area"]
];

// Form options for where a manually created pilgrim can start.
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

// Form options for the initial target before the ritual schedule takes over.
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

// Hazard options that can be injected into the simulation environment.
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

// Locations used to represent where the main group is currently visible.
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

// Safer fallback destinations used when an agent decides to avoid a crowd.
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

// Emergency destinations used when an agent enters panic mode.
const panicNodeOptions = [
  "Emergency_Point_1",
  "Emergency_Point_2",
  "Field_Hospital",
  "Police_Assist_Point",
  "Emergency_Point",
  "Mina_Camp_1",
  "Jamarat_Bridge"
];

// Shared color palette for marker and roster risk statuses.
const STATUS_COLORS = {
  stable: "#2b865f",
  needs_support: "#a67231",
  high_risk: "#c2402f",
  panicking: "#6d3fd1"
};

// Every pilgrim belongs to exactly one Hamlah, and each Hamlah has a fixed
// nationality -- these ten values mirror AgentFactory.DEFAULT_NATIONALITIES
// (hajj_agents.py) and hamlahs.json exactly, so every nationality choice here
// always resolves to a real, matching Hamlah. Nationality drives the Hamlah
// selection (see syncHamlahWithNationality), never the reverse.
const HAMLAH_NATIONALITIES = [
  "Saudi Arabia", "Indonesian", "Pakistani", "Indian", "Bangladeshi",
  "Egyptian", "Nigerian", "Turkish", "Malaysian", "Moroccan"
];

// Auto-select the matching default language after choosing a nationality.
const nationalityLanguageMap = {
  "Saudi Arabia": "Arabic",
  "Indonesian": "Bahasa Indonesia",
  "Pakistani": "Urdu",
  "Indian": "Hindi",
  "Bangladeshi": "Bengali",
  "Egyptian": "Arabic",
  "Nigerian": "English",
  "Turkish": "Turkish",
  "Malaysian": "Malay",
  "Moroccan": "Arabic"
};

// ============================================================
// DOM references and runtime state
// ------------------------------------------------------------
// This block collects page elements once, then stores frontend-only state such
// as loaded agents, map layers, filters, playback timers, and chart data.
// ============================================================

// Main DOM references used throughout rendering and event handling.
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
const environmentTimeLabel = document.querySelector("#environmentTimeLabel");
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
const generateReportButton = document.querySelector("#generateReportButton");
const analyticsReportBody = document.querySelector("#analyticsReportBody");
const analyticsNarrativeEl = document.querySelector("#analyticsNarrative");
const analyticsBarChartCanvas = document.querySelector("#analyticsBarChart");
const deploymentImpactChartCanvas = document.querySelector("#deploymentImpactChart");
const deploymentImpactChartWrap = document.querySelector("#deploymentImpactChartWrap");
const cameraModeButtons = document.querySelectorAll(".camera-mode-btn");
const recenterMapButton = document.querySelector("#recenterMapButton");
const fullscreenToggleButton = document.querySelector("#fullscreenToggleButton");
const deployButtons = document.querySelectorAll(".deploy-btn");
const placementModeBanner = document.querySelector("#placementModeBanner");
const playbackStateIndicator = document.querySelector("#playbackStateIndicator");
const llmStatusBar = document.querySelector("#llmStatusBar");
const llmReportBody = document.querySelector("#llmReportBody");
const generateLlmReportButton = document.querySelector("#generateLlmReportButton");
const mapWrapEl = document.querySelector(".map-wrap");

// Frontend runtime state mirrored from the backend API.
let agents = [];
let units = [];
let map;
let siteLayerGroup;
let mapLayerGroup;
let routeLayerGroup;
let busLayerGroup;
let marshalLayerGroup;
let policeLayerGroup;
let ambulanceLayerGroup;
let heatLayer;
let analyticsChart;
let agentMarkers = new Map();
let unitMarkers = new Map();
let currentEnvironment = null;
let summaryHistory = [];
let mapHasInitialFit = false;
let playbackTimer = null;
let simulationBusy = false;
let routeLayersReady = false;
let autoReportShownForRun = false;
let hotels = [];
let hamlahs = [];
let hotelLayerGroup;
let hotelMarkers = new Map();

// Camera control: Free Roam leaves the map exactly where the user left it;
// Focus Lock smoothly follows whichever pilgrim/unit was last clicked.
let cameraMode = "free_roam";
let focusedEntity = null; // { type: "pilgrim" | "unit", id: string } | null

// Click-to-place unit deployment: set while a "Deploy X" button is active,
// cleared on placement, cancel (Esc), or after a successful deploy.
let placementMode = null; // { unitType: string } | null

let analyticsBarChart;
let deploymentImpactChart;

// Live status of the LLM decision layer, refreshed on every dashboard refresh.
let llmStatus = null;
let llmReportShownForRun = false;

// Layer-visibility toggles, keyed by the data-layer values in index.html.
const UNIT_LAYER_GROUPS = {
  buses: () => busLayerGroup,
  marshals: () => marshalLayerGroup,
  police: () => policeLayerGroup,
  ambulances: () => ambulanceLayerGroup,
};

// Current roster filter/sort settings used by both cards and map markers.
const rosterFilters = {
  searchQuery: "",
  groupId: "all",
  health: "all",
  risk: "all",
  sortMode: "default"
};

// Approximate node capacities used to turn agent counts into heatmap intensity.
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

// ============================================================
// Setup helpers and small utilities
// ------------------------------------------------------------
// These functions populate form controls, normalize API access, derive risk
// labels, and manage playback controls.
// ============================================================

// Populate the nationality dropdown from the full country list.
function populateNationalityOptions() {
  const nationalitySelect = manualForm.elements.nationality;
  if (!nationalitySelect) {
    return;
  }

  nationalitySelect.innerHTML = "";

  HAMLAH_NATIONALITIES.forEach((nationality) => {
    const option = document.createElement("option");
    option.value = nationality;
    option.textContent = nationality;
    nationalitySelect.appendChild(option);
  });

  nationalitySelect.value = "Saudi Arabia";
}

// Update the language dropdown when the selected nationality has a known default.
function syncLanguageWithNationality() {
  const nationalitySelect = manualForm.elements.nationality;
  const languageSelect = manualForm.elements.language;
  if (!nationalitySelect || !languageSelect) {
    return;
  }

  nationalitySelect.addEventListener("change", () => {
    const language = nationalityLanguageMap[nationalitySelect.value] || "English";
    if ([...languageSelect.options].some((item) => item.value === language)) {
      languageSelect.value = language;
    } else {
      languageSelect.value = "English";
    }
    syncHamlahWithNationality();
  });
}

// Populate the Hamlah dropdown from the backend and keep it synced with
// whichever nationality is currently selected -- a Hamlah's nationality is
// fixed, so nationality drives the Hamlah choice, never the reverse.
let hamlahByNationality = new Map();

function populateHamlahOptions() {
  const hamlahSelect = manualForm.elements.hamlah_id;
  if (!hamlahSelect) {
    return;
  }

  hamlahByNationality = new Map(hamlahs.map((hamlah) => [hamlah.nationality, hamlah]));

  hamlahSelect.innerHTML = "";
  hamlahs.forEach((hamlah) => {
    const option = document.createElement("option");
    option.value = hamlah.hamlah_id;
    option.textContent = `${hamlah.name} (${hamlah.nationality})`;
    hamlahSelect.appendChild(option);
  });

  syncHamlahWithNationality();
}

// Select the one Hamlah whose nationality matches the form's current choice.
function syncHamlahWithNationality() {
  const nationalitySelect = manualForm.elements.nationality;
  const hamlahSelect = manualForm.elements.hamlah_id;
  if (!nationalitySelect || !hamlahSelect) {
    return;
  }

  const matchingHamlah = hamlahByNationality.get(nationalitySelect.value);
  if (matchingHamlah) {
    hamlahSelect.value = matchingHamlah.hamlah_id;
  }
}

// Replace a select element's options with a supplied list of simulation nodes.
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

// Initialize all node/hazard dropdowns with current scenario options.
function initializeScenarioOptions() {
  populateSelectOptions(manualForm, "initial_node", initialLocationOptions, "Jeddah_Airport");
  populateSelectOptions(manualForm, "target_node", targetLocationOptions, "Arafat_Main_Field");
  populateSelectOptions(environmentForm, "hazard", hazardOptions, "none");
  populateSelectOptions(environmentForm, "group_location", groupLocationOptions, "Jeddah_Airport");
  populateSelectOptions(environmentForm, "alternate_node", alternateNodeOptions, "Cooling_Station_1");
  populateSelectOptions(environmentForm, "panic_node", panicNodeOptions, "Emergency_Point_1");
}

// Fetch JSON from the backend and throw a readable error for failed requests.
async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

// Convert vitals into a dashboard risk category when the agent is not panicking.
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

// Choose the status color key for one agent.
function getAgentStatus(agent) {
  if (agent.state.is_panicking) {
    return "panicking";
  }
  return deriveOperationalRisk(agent);
}

// Build the small human-shaped Leaflet marker used for pilgrim positions.
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

// Build the wide rounded-rectangle Leaflet marker used for bus units.
function buildBusIcon() {
  return L.divIcon({
    className: "unit-icon-wrapper",
    iconSize: [26, 18],
    iconAnchor: [13, 14],
    popupAnchor: [0, -12],
    html:
      `<div class="unit-marker bus">` +
      `<span class="unit-body"></span>` +
      `<span class="unit-wheel left"></span><span class="unit-wheel right"></span>` +
      `</div>`
  });
}

// Build the pennant-shaped Leaflet marker used for marshal units.
function buildMarshalIcon() {
  return L.divIcon({
    className: "unit-icon-wrapper",
    iconSize: [18, 22],
    iconAnchor: [8, 22],
    popupAnchor: [0, -18],
    html:
      `<div class="unit-marker marshal">` +
      `<span class="unit-pole"></span><span class="unit-flag"></span>` +
      `</div>`
  });
}

// Build the shield-shaped Leaflet marker used for police units.
function buildPoliceIcon(crowdControlMode) {
  const modifier = crowdControlMode ? " crowd-control" : "";
  return L.divIcon({
    className: "unit-icon-wrapper",
    iconSize: [18, 20],
    iconAnchor: [9, 18],
    popupAnchor: [0, -16],
    html: `<div class="unit-marker police${modifier}"><span class="unit-body"></span></div>`
  });
}

// Build the square marker with a cross used for ambulance units.
function buildAmbulanceIcon() {
  return L.divIcon({
    className: "unit-icon-wrapper",
    iconSize: [20, 20],
    iconAnchor: [10, 18],
    popupAnchor: [0, -16],
    html:
      `<div class="unit-marker ambulance">` +
      `<span class="unit-body"></span><span class="unit-cross-v"></span><span class="unit-cross-h"></span>` +
      `</div>`
  });
}

// Build the badge-style Leaflet marker used for a Hamlah's base-camp hotel.
function buildHotelIcon(hotel) {
  const isFull = hotel.occupancy >= hotel.capacity && hotel.capacity > 0;
  return L.divIcon({
    className: "hotel-icon-wrapper",
    iconSize: [0, 0],
    iconAnchor: [0, 0],
    popupAnchor: [0, -26],
    html:
      `<div class="hotel-marker${isFull ? " is-full" : ""}">` +
      `<span class="hotel-icon-glyph">&#127976;</span>` +
      `<span class="hotel-occupancy-badge">${hotel.occupancy}/${hotel.capacity}</span>` +
      `</div>`
  });
}

// Create, update, and remove Leaflet markers for every Hamlah base-camp hotel.
function renderHotelMarkers(currentHotels) {
  if (!hotelLayerGroup) {
    return;
  }

  const visibleIds = new Set(currentHotels.map((hotel) => hotel.hotel_id));
  hotelMarkers.forEach((marker, hotelId) => {
    if (!visibleIds.has(hotelId)) {
      hotelLayerGroup.removeLayer(marker);
      hotelMarkers.delete(hotelId);
    }
  });

  currentHotels.forEach((hotel) => {
    const site = siteGps[hotel.node_id];
    if (!site) {
      return;
    }
    const latLng = L.latLng(site.lat, site.lng);
    const icon = buildHotelIcon(hotel);
    const tooltipHtml =
      `<strong>${hotel.name}</strong><br>&#127976; Occupancy: ${hotel.occupancy}/${hotel.capacity}`;

    let marker = hotelMarkers.get(hotel.hotel_id);
    if (!marker) {
      marker = L.marker(latLng, { icon, title: hotel.name });
      marker.bindTooltip(tooltipHtml, {
        direction: "top",
        offset: [0, -14],
        opacity: 0.95,
        sticky: true,
        className: "agent-hover-tooltip"
      });
      marker.on("mouseover", () => marker.openTooltip());
      marker.on("click", () => {
        const freshHotel = hotels.find((item) => item.hotel_id === hotel.hotel_id);
        if (freshHotel) {
          openHotelDetailSidebar(freshHotel);
        }
      });
      marker.addTo(hotelLayerGroup);
      hotelMarkers.set(hotel.hotel_id, marker);
      return;
    }

    marker.setIcon(icon);
    marker.setTooltipContent(tooltipHtml);
    marker.setLatLng(latLng);
  });
}

// Read the playback interval selected by the user.
function getPlaybackDelay() {
  return Number(playbackSpeedSelect?.value || 800);
}

// Enable/disable playback buttons based on whether auto-simulation is running.
function setPlaybackState(isPlaying) {
  if (startSimulationButton) {
    startSimulationButton.disabled = isPlaying;
  }
  if (pauseSimulationButton) {
    pauseSimulationButton.disabled = !isPlaying;
  }
  if (playbackStateIndicator) {
    playbackStateIndicator.textContent = isPlaying ? "Playing" : "Paused";
    playbackStateIndicator.classList.toggle("is-playing", isPlaying);
    playbackStateIndicator.classList.toggle("is-paused", !isPlaying);
  }
}

// Stop automatic simulation ticks and reset the playback buttons.
function stopPlayback() {
  if (playbackTimer) {
    clearInterval(playbackTimer);
    playbackTimer = null;
  }
  setPlaybackState(false);
}

// ============================================================
// Summary and map rendering
// ------------------------------------------------------------
// This block renders the hero metrics, initializes Leaflet, draws route/site
// layers, animates agent markers, and builds the pressure heatmap.
// ============================================================

// Render the top summary cards from aggregate backend metrics.
function renderSummary(summary) {
  summaryCards.innerHTML = "";
  // Prefer the readable GPS label, then fall back to the raw node id.
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
    // Each summary section is rebuilt from the latest backend snapshot.
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

// Create the Leaflet map once, then attach base tiles and static layers.
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
  busLayerGroup = L.layerGroup().addTo(map);
  marshalLayerGroup = L.layerGroup().addTo(map);
  policeLayerGroup = L.layerGroup().addTo(map);
  ambulanceLayerGroup = L.layerGroup().addTo(map);
  hotelLayerGroup = L.layerGroup().addTo(map);
  renderRoutes();
  renderSiteMarkers();

  // Heatmap radius/blur are zoom-responsive, so redraw whenever the zoom
  // level changes instead of waiting for the next simulation tick.
  map.on("zoomend", () => {
    renderHeatmap(getPedestrianAgents(agents), currentEnvironment);
  });

  // While a "Deploy X" button is active, the next map click places that
  // unit at the nearest known simulation node instead of panning/zooming.
  map.on("click", (event) => {
    if (!placementMode) {
      return;
    }
    deployUnitAt(event.latlng);
  });
}

// Find the simulation node whose GPS point is closest to a clicked latlng.
function findNearestNodeId(latlng) {
  let nearestNodeId = null;
  let nearestDistance = Infinity;
  Object.entries(siteGps).forEach(([nodeId, site]) => {
    const distance = Math.hypot(site.lat - latlng.lat, site.lng - latlng.lng);
    if (distance < nearestDistance) {
      nearestDistance = distance;
      nearestNodeId = nodeId;
    }
  });
  return nearestNodeId;
}

// Keep the airport and active route visible when agents start far from Makkah.
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

// Boarded/checked-in pilgrims aren't standing at a map node anymore -- they
// unrender from the map (roster cards keep showing them via travel_state)
// while a bus or hotel represents their position instead.
function getPedestrianAgents(currentAgents) {
  return currentAgents.filter(
    (agent) => (agent.state.travel_state || "PEDESTRIAN") === "PEDESTRIAN"
  );
}

// Redraw the map-dependent layers using the latest agents and environment.
function renderMap(currentAgents, environment) {
  ensureMap();
  const visibleAgents = getPedestrianAgents(getDisplayedAgents(currentAgents));
  renderHeatmap(visibleAgents, environment);
  renderAgentMarkers(visibleAgents);
  renderUnitMarkers(units);
  renderHotelMarkers(hotels);

  // Camera stays exactly where the operator left it in Free Roam; automatic
  // recentering is now only reachable via the manual Recenter button.
  if (cameraMode === "focus_lock") {
    applyFocusLock();
  }
}

// In Focus Lock, smoothly follow whichever pilgrim/unit was last clicked --
// including a pilgrim who just boarded a bus, by following the bus instead.
function applyFocusLock() {
  if (!map || !focusedEntity) {
    return;
  }

  let latLng = null;
  if (focusedEntity.type === "pilgrim") {
    const agent = agents.find((item) => item.profile.pilgrim_id === focusedEntity.id);
    if (agent && agent.state.boarded_unit_id) {
      latLng = unitMarkers.get(agent.state.boarded_unit_id)?.getLatLng() || null;
    }
    if (!latLng) {
      latLng = agentMarkers.get(focusedEntity.id)?.getLatLng() || null;
    }
  } else if (focusedEntity.type === "unit") {
    latLng = unitMarkers.get(focusedEntity.id)?.getLatLng() || null;
  }

  if (latLng) {
    map.panTo(latLng, { animate: true, duration: 0.6 });
  }
}

// Draw the major Hajj movement corridors once.
function renderRoutes() {
  if (routeLayersReady) {
    return;
  }
  holyRoutes.forEach((route, idx) => {
    // Convert route node ids into Leaflet latitude/longitude points.
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

// Add static landmark markers and let users click them to find agents there.
function renderSiteMarkers() {
  siteLayerGroup.clearLayers();
  Object.entries(siteGps).forEach(([nodeId, site]) => {
    const marker = L.marker([site.lat, site.lng], { title: site.label });
    marker.bindTooltip(site.label, { direction: "top" });
    marker.addTo(siteLayerGroup);
    marker.on("click", () => focusNodeAgents(nodeId));
  });
}

// Offset markers slightly so agents at the same node remain visible.
function getMarkerLatLng(agent, index) {
  const node = agent.state.current_node;
  const base = siteGps[node] || { lat: 21.392, lng: 39.924, label: "Fallback" };
  return L.latLng(
    base.lat + jitter(index, 0.0018),
    base.lng + jitter(index + 11, 0.0022)
  );
}

// Smoothly animate a marker between old and new map coordinates.
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

// Create, update, and remove Leaflet markers for the visible agent set.
function renderAgentMarkers(visibleAgents) {
  const visibleIds = new Set(visibleAgents.map((agent) => agent.profile.pilgrim_id));
  // Remove markers for agents hidden by filters or no longer present.
  agentMarkers.forEach((marker, agentId) => {
    if (!visibleIds.has(agentId)) {
      mapLayerGroup.removeLayer(marker);
      agentMarkers.delete(agentId);
    }
  });

  visibleAgents.forEach((agent, index) => {
    // New markers are created once; existing markers are updated and animated.
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
        const pilgrimId = agent.profile.pilgrim_id;
        focusedEntity = { type: "pilgrim", id: pilgrimId };
        scrollToAgent(pilgrimId);
        // Look up the current snapshot rather than closing over the agent
        // object from whenever this marker was first created.
        const freshAgent = agents.find((item) => item.profile.pilgrim_id === pilgrimId);
        if (freshAgent) {
          openPilgrimDetailSidebar(freshAgent);
        }
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

// Human-readable labels for support-unit types, shared by tooltips/sidebar.
const UNIT_TYPE_LABELS = {
  bus: "Bus",
  marshal: "Marshal",
  police: "Police",
  ambulance: "Ambulance"
};

const UNIT_ICON_BUILDERS = {
  bus: () => buildBusIcon(),
  marshal: () => buildMarshalIcon(),
  police: (unit) => buildPoliceIcon(unit.crowd_control_mode),
  ambulance: () => buildAmbulanceIcon()
};

const UNIT_TYPE_TO_LAYER_KEY = {
  bus: "buses",
  marshal: "marshals",
  police: "police",
  ambulance: "ambulances"
};

// Resolve a unit's Leaflet layer group from its unit_type.
function getUnitLayerGroup(unitType) {
  const layerKey = UNIT_TYPE_TO_LAYER_KEY[unitType];
  const getter = layerKey ? UNIT_LAYER_GROUPS[layerKey] : null;
  return getter ? getter() : null;
}

// Offset unit markers slightly so several units at the same node stay visible.
function getUnitMarkerLatLng(unit, index) {
  const base = siteGps[unit.current_node] || { lat: 21.392, lng: 39.924, label: "Fallback" };
  return L.latLng(
    base.lat + jitter(index + 200, 0.0016),
    base.lng + jitter(index + 233, 0.002)
  );
}

// A corridor bus mid-transit occupies a real in-between point instead of
// snapping between nodes -- interpolate along its from/to nodes by progress.
function getUnitDisplayLatLng(unit, index) {
  if (
    unit.unit_type === "bus" &&
    unit.status === "in_transit" &&
    unit.transit_from_node &&
    unit.transit_to_node
  ) {
    const from = siteGps[unit.transit_from_node];
    const to = siteGps[unit.transit_to_node];
    if (from && to) {
      const progress = Math.max(0, Math.min(1, Number(unit.transit_progress || 0)));
      return L.latLng(
        from.lat + (to.lat - from.lat) * progress,
        from.lng + (to.lng - from.lng) * progress
      );
    }
  }
  return getUnitMarkerLatLng(unit, index);
}

// Create, update, and remove Leaflet markers for every support unit.
function renderUnitMarkers(currentUnits) {
  const visibleIds = new Set(currentUnits.map((unit) => unit.unit_id));
  unitMarkers.forEach((marker, unitId) => {
    if (!visibleIds.has(unitId)) {
      getUnitLayerGroup(marker.unitType)?.removeLayer(marker);
      unitMarkers.delete(unitId);
    }
  });

  currentUnits.forEach((unit, index) => {
    const latLng = getUnitDisplayLatLng(unit, index);
    const iconBuilder = UNIT_ICON_BUILDERS[unit.unit_type] || UNIT_ICON_BUILDERS.bus;
    const icon = iconBuilder(unit);
    const typeLabel = UNIT_TYPE_LABELS[unit.unit_type] || unit.unit_type;
    const passengerLine = unit.unit_type === "bus"
      ? `<br>Passengers: ${unit.manifest_count || 0}/${unit.passenger_capacity}`
      : "";
    const tooltipHtml = `<strong>${unit.unit_id}</strong><br>${typeLabel}<br>Status: ${unit.status}${passengerLine}`;

    let marker = unitMarkers.get(unit.unit_id);
    if (!marker) {
      const layerGroup = getUnitLayerGroup(unit.unit_type);
      marker = L.marker(latLng, { icon, title: unit.unit_id });
      marker.unitType = unit.unit_type;
      marker.bindTooltip(tooltipHtml, {
        direction: "top",
        offset: [0, -8],
        opacity: 0.95,
        sticky: true,
        className: "agent-hover-tooltip"
      });
      marker.on("mouseover", () => marker.openTooltip());
      marker.on("click", () => {
        focusedEntity = { type: "unit", id: unit.unit_id };
        const freshUnit = units.find((item) => item.unit_id === unit.unit_id);
        if (freshUnit) {
          openUnitDetailSidebar(freshUnit);
        }
      });
      marker.addTo(layerGroup || mapLayerGroup);
      unitMarkers.set(unit.unit_id, marker);
      return;
    }

    marker.setIcon(icon);
    marker.setTooltipContent(tooltipHtml);
    animateMarkerTo(marker, latLng);
  });
}

// Render a pressure heatmap based on agent counts, density, and hazards.
function renderHeatmap(currentAgents, environment) {
  if (typeof L.heatLayer !== "function") {
    return;
  }

  if (heatLayer) {
    map.removeLayer(heatLayer);
  }

  const countsByNode = {};
  // Count visible pilgrims at each node before converting counts to heat values.
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
      // Pressure compares current count against a rough capacity baseline.
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

  // Tie the heat radius/blur to the current zoom level so density reads
  // accurately whether the map is zoomed out over all of Makkah or zoomed
  // into a single camp -- a fixed radius looks either too diffuse or too
  // blocky depending on scale.
  const zoom = map.getZoom();
  const radius = Math.max(14, Math.min(55, zoom * 3.2 - 12));
  const blur = Math.max(10, radius * 0.75);

  heatLayer = L.heatLayer(heatPoints, {
    radius,
    blur,
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

// ============================================================
// Roster, chart, and card rendering
// ------------------------------------------------------------
// This block filters/sorts agents, renders roster cards, updates card focus
// behavior, and draws the operational chart.
// ============================================================

// Rebuild group filter options from the currently loaded roster.
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

// Keep the sort dropdown in sync with the stored filter state.
function syncSortControl() {
  if (!sortRosterSelect) {
    return;
  }
  sortRosterSelect.value = rosterFilters.sortMode;
}

// Apply search, group, health, risk, and sort controls to the roster.
function getDisplayedAgents(currentAgents) {
  // Filtering is applied before sorting so the map and roster use the same
  // visible agent list.
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

// Show how many agents are visible after filtering.
function updateRosterMeta(visibleCount, totalCount) {
  if (!rosterMeta) {
    return;
  }

  rosterMeta.textContent = `Showing ${visibleCount} of ${totalCount} pilgrims`;
}

// Render the clickable agent roster cards.
function renderAgents(currentAgents) {
  const visibleAgents = getDisplayedAgents(currentAgents);
  agentGrid.innerHTML = "";

  // Empty-state rendering keeps the roster area informative when filters hide
  // every agent.
  if (!visibleAgents.length) {
    updateRosterMeta(0, currentAgents.length);
    agentGrid.innerHTML = `<div class="roster-empty">No pilgrims match the current filters.</div>`;
    return;
  }

  visibleAgents.forEach((agent) => {
    // Cards are cloned from the HTML template and populated with snapshot data.
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
      detailBlock("Travel status", describeTravelStatus(agent)),
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

// Render or update the operational line chart for stress and risk counts.
function renderChart(history) {
  const labels = history.map((entry) => `Tick ${entry.simulation_tick}`);
  const stressSeries = history.map((entry) => Number(entry.avg_stress || 0));
  const supportSeries = history.map((entry) => Number(entry.needs_support_agents || 0));
  const highRiskSeries = history.map((entry) => Number(entry.high_risk_agents || 0));
  const panickingSeries = history.map((entry) => Number(entry.panicking_agents || 0));

  if (!analyticsChart) {
    // First render creates the Chart.js instance with one vitals axis and one
    // pilgrim-count axis.
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
  // Later renders reuse the chart instance and replace only the data series.
  analyticsChart.data.datasets[0].data = stressSeries;
  analyticsChart.data.datasets[1].data = supportSeries;
  analyticsChart.data.datasets[2].data = highRiskSeries;
  analyticsChart.data.datasets[3].data = panickingSeries;
  analyticsChart.update();
}

// Render (or clear) the bar chart of peak bottleneck nodes vs. pressure ratio.
function renderBottleneckChart(peakBottlenecks) {
  if (!analyticsBarChartCanvas) {
    return;
  }
  const labels = peakBottlenecks.map((item) => siteGps[item.node]?.label || item.node.replaceAll("_", " "));
  const data = peakBottlenecks.map((item) => item.peak_ratio);

  if (!analyticsBarChart) {
    analyticsBarChart = new Chart(analyticsBarChartCanvas, {
      type: "bar",
      data: {
        labels,
        datasets: [{
          label: "Peak pressure ratio (x capacity)",
          data,
          backgroundColor: "rgba(194, 64, 47, 0.55)",
          borderColor: "rgba(194, 64, 47, 1)",
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, title: { display: true, text: "Peak Bottlenecks" } },
        scales: { y: { beginAtZero: true } }
      }
    });
    return;
  }

  analyticsBarChart.data.labels = labels;
  analyticsBarChart.data.datasets[0].data = data;
  analyticsBarChart.update();
}

// Render (or hide) the grouped before/after chart for manually deployed units.
function renderDeploymentImpactChart(deploymentImpact) {
  if (!deploymentImpactChartCanvas || !deploymentImpactChartWrap) {
    return;
  }

  if (!deploymentImpact.length) {
    deploymentImpactChartWrap.hidden = true;
    return;
  }
  deploymentImpactChartWrap.hidden = false;

  const labels = deploymentImpact.map((item) => `${item.unit_type} @ ${item.node_id.replaceAll("_", " ")}`);
  const beforeData = deploymentImpact.map((item) => item.ratio_before);
  const afterData = deploymentImpact.map((item) => item.ratio_after);

  if (!deploymentImpactChart) {
    deploymentImpactChart = new Chart(deploymentImpactChartCanvas, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Pressure before",
            data: beforeData,
            backgroundColor: "rgba(166, 114, 49, 0.55)",
            borderColor: "rgba(166, 114, 49, 1)",
            borderWidth: 1
          },
          {
            label: "Pressure after",
            data: afterData,
            backgroundColor: "rgba(32, 106, 78, 0.55)",
            borderColor: "rgba(32, 106, 78, 1)",
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: true }, title: { display: true, text: "Manual Deployment Impact" } },
        scales: { y: { beginAtZero: true } }
      }
    });
    return;
  }

  deploymentImpactChart.data.labels = labels;
  deploymentImpactChart.data.datasets[0].data = beforeData;
  deploymentImpactChart.data.datasets[1].data = afterData;
  deploymentImpactChart.update();
}

// Render the proactive analytics report: bottlenecks, strengths, suggestions.
function renderAnalyticsReport(report) {
  if (!analyticsReportBody) {
    return;
  }

  if (!report || !report.has_data) {
    analyticsReportBody.innerHTML =
      `<p class="analytics-empty">Run the simulation, then generate a report to see bottlenecks, strengths, and suggestions.</p>`;
    if (analyticsNarrativeEl) {
      analyticsNarrativeEl.hidden = true;
      analyticsNarrativeEl.innerHTML = "";
    }
    if (deploymentImpactChartWrap) {
      deploymentImpactChartWrap.hidden = true;
    }
    return;
  }

  if (analyticsNarrativeEl) {
    analyticsNarrativeEl.hidden = !report.narrative;
    analyticsNarrativeEl.innerHTML = report.narrative
      ? report.narrative
          .split("\n")
          .filter((paragraph) => paragraph.trim())
          .map((paragraph) => `<p>${paragraph}</p>`)
          .join("")
      : "";
  }
  renderBottleneckChart(report.peak_bottlenecks || []);
  renderDeploymentImpactChart(report.deployment_impact || []);

  const bottleneckItems = report.peak_bottlenecks.length
    ? report.peak_bottlenecks.map((item) => {
        const label = (siteGps[item.node]?.label || item.node.replaceAll("_", " "));
        return `<li><strong>${label}</strong> — peaked at ${item.peak_ratio}x capacity ` +
          `(${item.overload_ticks} overloaded ticks, around ${item.peak_day_label || `tick ${item.peak_tick}`})</li>`;
      }).join("")
    : `<li>No sustained bottlenecks detected.</li>`;

  const resilientItems = report.resilient_windows.length
    ? report.resilient_windows.map((item) =>
        `<li><strong>${item.day_label || `Tick ${item.tick}`}</strong> — severity index stayed at ${item.severity_index}%</li>`
      ).join("")
    : `<li>No especially low-pressure windows stood out in this run.</li>`;

  const bufferedLabel = report.well_buffered_locations.length
    ? report.well_buffered_locations.map((node) => siteGps[node]?.label || node.replaceAll("_", " ")).join(", ")
    : "None recorded";

  const suggestionItems = report.suggested_enhancements.map((text) => `<li>${text}</li>`).join("");

  analyticsReportBody.innerHTML = `
    <section>
      <h3 class="analytics-section-title">Peak Bottlenecks (Weaknesses)</h3>
      <ul class="analytics-list bottleneck">${bottleneckItems}</ul>
    </section>
    <section>
      <h3 class="analytics-section-title">Smooth Flow Metrics (Strengths)</h3>
      <ul class="analytics-list resilient">${resilientItems}</ul>
      <p class="environment-tick" style="margin-top: 8px;">Well-buffered locations: <strong>${bufferedLabel}</strong></p>
    </section>
    <section>
      <h3 class="analytics-section-title">Suggested Operational Enhancements</h3>
      <ul class="analytics-list suggestion">${suggestionItems}</ul>
    </section>
  `;
}

// Fetch the latest analytics report from the backend and render it.
async function fetchAndRenderAnalyticsReport() {
  const response = await fetchJson("/api/analytics/report");
  renderAnalyticsReport(response.report);
}

generateReportButton?.addEventListener("click", async () => {
  if (generateReportButton) {
    generateReportButton.disabled = true;
    generateReportButton.dataset.originalLabel = generateReportButton.textContent;
    generateReportButton.textContent = "Generating…";
  }
  try {
    await fetchAndRenderAnalyticsReport();
  } catch (error) {
    if (analyticsReportBody) {
      analyticsReportBody.innerHTML = `<p class="analytics-empty">Could not load the report: ${error.message}</p>`;
    }
  } finally {
    if (generateReportButton) {
      generateReportButton.disabled = false;
      generateReportButton.textContent = generateReportButton.dataset.originalLabel || "Generate Analytics Report";
    }
  }
});

// ============================================================
// LLM decision layer: status badge and after-action report
// ------------------------------------------------------------
// The backend decides every pedestrian action through llm_decide_action(); this
// section surfaces (a) whether the model is actually live, and (b) the
// six-section report built from the recorded decision log.
// ============================================================

// Render the model status strip above the LLM report.
function renderLlmStatus(status) {
  llmStatus = status || null;
  if (!llmStatusBar) {
    return;
  }
  if (!status) {
    llmStatusBar.innerHTML = `<span class="llm-badge llm-badge-off">Model status unavailable</span>`;
    return;
  }

  const stats = status.stats || {};
  const live = status.active;
  const stateBadge = live
    ? `<span class="llm-badge llm-badge-on">LLM active — ${status.provider} / ${status.model}</span>`
    : `<span class="llm-badge llm-badge-off">LLM inactive — ${
        status.api_key_present ? "enabled=false or unknown provider" : "no LLM_API_KEY set"
      } (agents fall back to rule-based decisions)</span>`;

  const driven = status.max_agents === 0 ? "all pilgrims" : `${status.max_agents} pilgrim(s)`;

  // When the provider keeps failing the engine stops calling it, so the run
  // keeps moving. Say so explicitly -- otherwise "0 model / N fallback" with a
  // stale error looks like the feature is simply broken.
  const circuitBadge = status.circuit_open
    ? `<span class="llm-badge llm-badge-paused">Calls paused after repeated failures — retrying in ${Math.ceil(status.circuit_retry_in_seconds)}s</span>`
    : "";

  llmStatusBar.innerHTML = `
    ${stateBadge}
    ${circuitBadge}
    <span class="llm-stat">Driving: <strong>${driven}</strong></span>
    <span class="llm-stat">Decisions: <strong>${stats.decisions_total || 0}</strong>
      (${stats.decisions_from_llm || 0} model / ${stats.decisions_from_fallback || 0} fallback)</span>
    <span class="llm-stat">API calls: <strong>${stats.calls_succeeded || 0}</strong> ok,
      ${stats.calls_failed || 0} failed, ${stats.cache_hits || 0} cached, ${stats.budget_skips || 0} over budget${
        stats.circuit_skips ? `, ${stats.circuit_skips} skipped while paused` : ""
      }${
        stats.rate_limit_skips ? `, ${stats.rate_limit_skips} rate-limited` : ""
      }</span>
    <span class="llm-stat">Avg latency: <strong>${status.avg_latency_ms || 0} ms</strong></span>
    ${status.last_error ? `<span class="llm-stat llm-error">Last error: ${status.last_error}</span>` : ""}
  `;
}

// Fetch just the model status (cheap; called on every dashboard refresh).
async function refreshLlmStatus() {
  try {
    const response = await fetchJson("/api/llm/status");
    renderLlmStatus(response.llm);
  } catch (error) {
    renderLlmStatus(null);
  }
}

// Turn one list of items into a bulleted analytics list.
function llmList(items, emptyText) {
  return items && items.length
    ? `<ul class="analytics-list">${items.map((item) => `<li>${item}</li>`).join("")}</ul>`
    : `<ul class="analytics-list"><li>${emptyText}</li></ul>`;
}

// Render the full six-section after-action report.
function renderLlmReport(report) {
  if (!llmReportBody) {
    return;
  }
  if (!report || !report.has_data) {
    llmReportBody.innerHTML =
      `<p class="analytics-empty">${report?.message || "No simulation data recorded yet — advance the simulation at least one tick."}</p>`;
    return;
  }

  const overview = report.overview;
  const decisions = report.decision_analysis;
  const risks = report.risk_analysis;
  const performance = report.agent_performance;
  const summary = report.final_summary;

  // 1) Overview
  const overviewHtml = `
    <div class="llm-metric-grid">
      ${statBlock("Duration", `${overview.ticks_recorded} ticks / ${overview.simulated_hours}h`)}
      ${statBlock("Decision steps", overview.decision_steps)}
      ${statBlock("From the LLM", `${overview.llm_decision_steps} (${overview.llm_share_percent}%)`)}
      ${statBlock("Movements", overview.movements)}
      ${statBlock("Risks detected", overview.risk_events_detected)}
      ${statBlock("Run completed", overview.run_completed ? "Yes" : "No")}
    </div>`;

  // 2) Decisions
  const actionRows = (decisions.action_counts || []).slice(0, 10).map((entry) =>
    `<tr><td><code>${entry.action}</code></td><td>${entry.count}</td><td>${entry.share_percent}%</td></tr>`
  ).join("");
  const keyPoints = (decisions.key_decision_points || []).slice(0, 5).map((point) =>
    `<strong>Tick ${point.tick}</strong> · ${point.pilgrim_id} at ${point.location} ` +
    `(risk ${point.risk_level} ${point.risk_score}, ${point.options_offered} options) → ` +
    `<strong>${point.action}</strong> — <em>${point.reason || "no reason given"}</em> ` +
    `(risk after: ${point.risk_score_after})`
  );
  const goodExamples = (decisions.successful_examples || []).map((item) =>
    `${item.pilgrim_id} chose <strong>${item.action}</strong> at ${item.location} → risk ${item.risk_score} → ${item.risk_score_after}`
  );
  const badExamples = (decisions.unsuccessful_examples || []).map((item) =>
    `${item.pilgrim_id} chose <strong>${item.action}</strong> at ${item.location} → risk ${item.risk_score} → ${item.risk_score_after}`
  );

  // 3) Risks
  const riskEvents = (risks.significant_events || []).slice(0, 5).map((event) => `
    <li>
      <strong>${event.event_id} — ${event.risk_type}</strong> (${event.pilgrim_id})<br />
      <span class="llm-muted">When:</span> tick ${event.opened_tick}, ${event.duration_ticks} tick(s) ·
      <span class="llm-muted">Where:</span> ${event.location}<br />
      <span class="llm-muted">Trigger:</span> ${(event.trigger_factors || []).join(", ") || "unspecified"}<br />
      <span class="llm-muted">Environment:</span> density ${event.environment?.crowd_density}, ${event.environment?.temperature_c}°C,
      hazard ${event.environment?.hazard || "none"}, node ${event.environment?.occupancy}/${event.environment?.capacity}<br />
      <span class="llm-muted">Severity:</span> opened ${event.opened_score}, peaked ${event.peak_score} (${event.peak_level})<br />
      <span class="llm-muted">Decisions:</span> ${event.decision_count}${
        event.first_response_action
          ? `, first response <code>${event.first_response_action}</code> after ${event.response_delay_ticks} tick(s)`
          : ", no protective action recorded"
      }<br />
      <span class="llm-muted">Aftermath:</span> ${event.outcome_detail}<br />
      <span class="llm-muted">Effective?</span> <strong>${event.effective ? "Yes" : "No"}</strong> (${event.outcome})
    </li>`).join("");

  // 4) Performance
  const avoidance = performance.risk_avoidance;
  const response = performance.response_time;
  const route = performance.route_changes;
  const efficiency = performance.movement_efficiency;
  const consistency = performance.decision_consistency;
  const problematic = performance.problematic_behavior;

  // 5) Improvements
  const improvementItems = (report.improvements || []).map((item) =>
    `<strong>${item.area}</strong> — ${item.suggestion}<br /><span class="llm-muted">Evidence: ${item.evidence}</span>`
  );

  llmReportBody.innerHTML = `
    <section>
      <h3 class="analytics-section-title">1. Simulation Overview</h3>
      ${overviewHtml}
    </section>
    <section>
      <h3 class="analytics-section-title">2. Decision Analysis</h3>
      <table class="llm-table">
        <thead><tr><th>Action</th><th>Count</th><th>Share</th></tr></thead>
        <tbody>${actionRows || `<tr><td colspan="3">No decisions recorded.</td></tr>`}</tbody>
      </table>
      <p class="environment-tick">Average model latency: <strong>${decisions.avg_latency_ms} ms</strong> ·
        fallbacks after failure/invalid output: <strong>${decisions.invalid_or_failed}</strong></p>
      <h4 class="llm-subtitle">Important decision points</h4>
      ${llmList(keyPoints, "No decision was taken while an agent was in a high or severe risk band.")}
      <h4 class="llm-subtitle">Successful decisions</h4>
      ${llmList(goodExamples, "None recorded.")}
      <h4 class="llm-subtitle">Unsuccessful decisions</h4>
      ${llmList(badExamples, "None recorded.")}
    </section>
    <section>
      <h3 class="analytics-section-title">3. Risk Analysis</h3>
      <p class="environment-tick">${risks.total_events} risk event(s), averaging ${risks.avg_duration_ticks || 0} tick(s).
        Outcomes: ${(risks.outcome_counts || []).map((entry) => `<strong>${entry.outcome}</strong> ${entry.count}`).join(", ") || "none"}</p>
      <ul class="analytics-list bottleneck">${riskEvents || "<li>No significant risk events were recorded.</li>"}</ul>
    </section>
    <section>
      <h3 class="analytics-section-title">4. Agent Performance</h3>
      <div class="llm-metric-grid">
        ${statBlock("Risk avoidance", `${avoidance.avoidance_rate_percent}%`)}
        ${statBlock("Avoided / reduced", `${avoidance.avoided} / ${avoidance.reduced}`)}
        ${statBlock("Worsened / unresolved", `${avoidance.worsened} / ${avoidance.unresolved}`)}
        ${statBlock("Avg response", `${response.avg_ticks_to_first_response} ticks`)}
        ${statBlock("Route changes", `${route.total} (${route.successful} good, ${route.unnecessary} wasted)`)}
        ${statBlock("Movement efficiency", `${efficiency.efficiency_percent}%`)}
        ${statBlock("Decision consistency", `${consistency.consistency_percent}%`)}
        ${statBlock("Oscillations", problematic.total_oscillation_events)}
      </div>
    </section>
    <section>
      <h3 class="analytics-section-title">5. Improvements / Enhancements</h3>
      ${llmList(improvementItems, "No systemic weakness surfaced in this run.")}
    </section>
    <section>
      <h3 class="analytics-section-title">6. Final Summary</h3>
      <p><strong>What happened.</strong> ${summary.what_happened}</p>
      <p><strong>How the agent behaved.</strong> ${summary.how_the_agent_behaved}</p>
      <p><strong>How it responded to risk.</strong> ${summary.how_it_responded_to_risk}</p>
      <h4 class="llm-subtitle">What worked well</h4>
      ${llmList(summary.what_worked_well, "Nothing stood out.")}
      <h4 class="llm-subtitle">What needs improvement</h4>
      ${llmList(summary.what_needs_improvement, "No systemic weaknesses surfaced.")}
      <h4 class="llm-subtitle">Recommended technical enhancements</h4>
      ${llmList(summary.recommended_technical_enhancements, "None.")}
      ${report.files?.markdown ? `<p class="environment-tick">Written to <code>${report.files.markdown}</code></p>` : ""}
    </section>
  `;
}

// Ask the backend to build (and persist) the after-action report.
async function fetchAndRenderLlmReport(persist = true) {
  const response = persist
    ? await fetchJson("/api/analytics/simulation-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      })
    : await fetchJson("/api/analytics/simulation-report");
  renderLlmReport(response.report);
  await refreshLlmStatus();
}

generateLlmReportButton?.addEventListener("click", async () => {
  generateLlmReportButton.disabled = true;
  const originalLabel = generateLlmReportButton.textContent;
  generateLlmReportButton.textContent = "Generating…";
  try {
    await fetchAndRenderLlmReport(true);
  } catch (error) {
    if (llmReportBody) {
      llmReportBody.innerHTML = `<p class="analytics-empty">Could not load the LLM report: ${error.message}</p>`;
    }
  } finally {
    generateLlmReportButton.disabled = false;
    generateLlmReportButton.textContent = originalLabel;
  }
});

// Explain, in words, which layer actually chose this pilgrim's last action.
function describeDecisionSource(source) {
  return {
    llm: "LLM (live model call)",
    cache: "LLM (cached identical situation)",
    rule_based: "Rule-based engine",
    disabled: "Rule-based engine (LLM not configured)",
    fallback_error: "Rule-based fallback (API call failed)",
    fallback_invalid: "Rule-based fallback (model returned an invalid action)",
    fallback_budget: "Rule-based fallback (per-tick LLM budget reached)",
    fallback_circuit_open: "Rule-based fallback (LLM calls paused after repeated failures)",
    fallback_rate_limit: "Rule-based fallback (per-minute LLM request budget spent)"
  }[source] || source || "Rule-based engine";
}

// Build a compact stat tile inside an agent card.
function statBlock(label, value) {
  return `<div class="mini-stat"><span>${label}</span><strong>${value}</strong></div>`;
}

// Build a label/value detail tile inside an agent card.
function detailBlock(label, value) {
  return `<div class="detail-item"><span>${label}</span><strong>${value}</strong></div>`;
}

// Translate an agent's travel_state into a human-readable roster/sidebar line.
function describeTravelStatus(agent) {
  const state = agent.state;
  switch (state.travel_state) {
    case "IN_TRANSIT":
      return `Boarded ${state.boarded_unit_id || "a bus"}`;
    case "AWAITING_TRANSPORT":
      return "Awaiting transport";
    case "CHECKED_IN_HOTEL": {
      const hotel = hotels.find((item) => item.hotel_id === state.checked_in_hotel_id);
      return `Checked in at ${hotel?.name || state.checked_in_hotel_id || "hotel"}`;
    }
    default:
      return "On foot";
  }
}

// ============================================================
// Detail sidebar
// ------------------------------------------------------------
// Slide-in panel shown when any pilgrim or support-unit marker is
// clicked, using the same detailBlock/statBlock helpers as roster cards.
// ============================================================

const detailSidebar = document.querySelector("#detailSidebar");
const detailSidebarTitle = document.querySelector("#detailSidebarTitle");
const detailSidebarBody = document.querySelector("#detailSidebarBody");
const detailSidebarClose = document.querySelector("#detailSidebarClose");

function openDetailSidebar(title, bodyHtml) {
  if (!detailSidebar) {
    return;
  }
  detailSidebarTitle.textContent = title;
  detailSidebarBody.innerHTML = bodyHtml;
  detailSidebar.classList.add("is-open");
}

function closeDetailSidebar() {
  detailSidebar?.classList.remove("is-open");
}

detailSidebarClose?.addEventListener("click", closeDetailSidebar);

// Show a pilgrim's full profile/state/memory in the slide-in sidebar.
function openPilgrimDetailSidebar(agent) {
  const statusKey = getAgentStatus(agent);
  const ritualProgress = agent.memory.long_term.ritual_progress || [];
  const ritualSchedule = agent.memory.long_term.ritual_schedule || [];
  const completedRitualCount = ritualSchedule.filter((step) => ritualProgress.includes(step.progress_key)).length;

  const bodyHtml = [
    statBlock("Status", statusKey.replaceAll("_", " ")),
    detailBlock("Nationality", agent.profile.nationality),
    detailBlock("Age", agent.profile.age),
    detailBlock("Group", agent.profile.group_id),
    detailBlock("Hamlah", agent.profile.hamlah_id || "Unassigned"),
    detailBlock("Travel status", describeTravelStatus(agent)),
    detailBlock("Current location", siteGps[agent.state.current_node]?.label || agent.state.current_node),
    detailBlock("Ritual location", siteGps[agent.state.target_node]?.label || agent.state.target_node),
    detailBlock("Current ritual", agent.state.current_ritual || "Not Started"),
    detailBlock("Next ritual", agent.state.next_ritual || "Tawaf Al-Qudoum (Arrival Tawaf)"),
    detailBlock("Stress", agent.state.stress.toFixed(1)),
    detailBlock("Fatigue", agent.state.fatigue.toFixed(1)),
    detailBlock("Hydration", agent.state.hydration.toFixed(1)),
    detailBlock("With group", agent.state.is_with_group ? "Yes" : "No"),
    detailBlock("Straggling", agent.state.is_straggling ? "Yes" : "No"),
    detailBlock("Ritual progress", `${completedRitualCount}/${ritualSchedule.length || 0} complete`),
    detailBlock("Last action", agent.state.last_action),
    detailBlock("Decided by", describeDecisionSource(agent.state.last_decision_source)),
    detailBlock("Decision reason", agent.state.last_decision_reason || "—"),
    detailBlock("Rule-based fallback", agent.state.last_fallback_action || "—"),
    detailBlock("Risk level", `${(agent.state.risk_level || "none").replaceAll("_", " ")} (${agent.state.risk_score ?? 0}/100)`),
    detailBlock("Risk factors", (agent.state.risk_factors || []).join("; ") || "None detected"),
    detailBlock("Memory", (agent.memory.short_term.recent_nodes || []).join(", ") || "Fresh agent")
  ].join("");

  openDetailSidebar(`${agent.profile.pilgrim_id} — ${agent.profile.nationality} pilgrim`, bodyHtml);
}

// Show a support unit's status/role-specific fields in the slide-in sidebar.
function openUnitDetailSidebar(unit) {
  const typeLabel = UNIT_TYPE_LABELS[unit.unit_type] || unit.unit_type;
  const rows = [
    statBlock("Status", unit.status.replaceAll("_", " ")),
    detailBlock("Current location", siteGps[unit.current_node]?.label || unit.current_node),
    detailBlock("Target location", siteGps[unit.target_node]?.label || unit.target_node),
    detailBlock("Last action", unit.last_action)
  ];

  if (unit.unit_type === "bus") {
    rows.push(detailBlock("Passenger capacity", unit.passenger_capacity));
    rows.push(detailBlock(
      "Route",
      (unit.assigned_route || []).map((node) => siteGps[node]?.label || node).join(" → ")
    ));
  } else if (unit.unit_type === "marshal") {
    rows.push(detailBlock(
      "Patrol zone",
      (unit.patrol_zone || []).map((node) => siteGps[node]?.label || node).join(", ")
    ));
    rows.push(detailBlock("Agents assisted", unit.agents_assisted_count));
  } else if (unit.unit_type === "police") {
    rows.push(detailBlock(
      "Patrol zone",
      (unit.patrol_zone || []).map((node) => siteGps[node]?.label || node).join(", ")
    ));
    rows.push(detailBlock("Crowd control mode", unit.crowd_control_mode ? "Active" : "Standby"));
  } else if (unit.unit_type === "ambulance") {
    rows.push(detailBlock("Home hospital", siteGps[unit.home_hospital_node]?.label || unit.home_hospital_node));
    rows.push(detailBlock("Responding to", unit.responding_to_pilgrim_id || "None"));
  }

  openDetailSidebar(`${unit.unit_id} — ${typeLabel}`, rows.join(""));
}

// Show a hotel's occupancy and roster of currently checked-in pilgrims.
function openHotelDetailSidebar(hotel) {
  const occupantLabels = (hotel.occupant_ids || [])
    .map((pilgrimId) => agents.find((agent) => agent.profile.pilgrim_id === pilgrimId)?.profile.pilgrim_id || pilgrimId);

  const bodyHtml = [
    statBlock("Occupancy", `${hotel.occupancy}/${hotel.capacity}`),
    detailBlock("Location", siteGps[hotel.node_id]?.label || hotel.node_id),
    detailBlock("Checked-in pilgrims", occupantLabels.join(", ") || "None currently checked in")
  ].join("");

  openDetailSidebar(`${hotel.name} — Hotel`, bodyHtml);
}

// Scroll to one agent card and briefly highlight it.
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

// Focus the first agent currently located at a clicked map node.
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

// Deterministic jitter value used for marker separation.
function jitter(seed, amount) {
  return ((Math.sin(seed * 12.9898) * 43758.5453) % 1) * amount;
}

// ============================================================
// Forms, API refresh, and event wiring
// ------------------------------------------------------------
// This block turns form input into API payloads, refreshes all dashboard panels,
// controls playback, and connects user actions to backend endpoints.
// ============================================================

// Convert the manual agent form into the API payload expected by the backend.
function getManualPayload() {
  const data = new FormData(manualForm);
  const payload = Object.fromEntries(data.entries());
  payload.chronic_conditions = data.getAll("chronic_conditions").filter(Boolean);
  payload.performs_sacrifice = manualForm.elements.performs_sacrifice.checked;
  return payload;
}

// Convert the environment controls form into a simulation payload.
function getEnvironmentPayload() {
  return Object.fromEntries(new FormData(environmentForm).entries());
}

// Restore the manual creation form to useful demo defaults.
function resetManualDefaults() {
  manualForm.reset();
  manualForm.group_id.value = "G_200";
  manualForm.age.value = "38";
  manualForm.health_status.value = "stable";
  manualForm.nationality.value = "Saudi Arabia";
  manualForm.language.value = "Arabic";
  syncHamlahWithNationality();
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

// Read filter controls, rerender the roster, and keep the map in sync.
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

// Apply only the selected sort mode to the current roster list.
function applyRosterSort() {
  rosterFilters.sortMode = sortRosterSelect?.value || "default";
  renderAgents(agents);
}

// Reset search/filter/sort controls and show the full roster again.
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

// Copy backend environment state back into the visible controls and labels.
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
  if (environmentTimeLabel && environment.simulated_time_label) {
    environmentTimeLabel.textContent = environment.simulated_time_label;
  }
}

// Move the map view to one agent's marker or current node.
function focusAgentOnMap(agentId) {
  ensureMap();
  focusedEntity = { type: "pilgrim", id: agentId };

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

// Fetch agents, summary, and environment together, then rerender the dashboard.
async function refreshAll() {
  // Fetch independent resources in parallel so the dashboard refresh stays fast.
  const [agentResponse, summaryResponse, environmentResponse, unitResponse, hamlahResponse, hotelResponse] =
    await Promise.all([
      fetchJson("/api/agents"),
      fetchJson("/api/summary"),
      fetchJson("/api/environment"),
      fetchJson("/api/units"),
      fetchJson("/api/hamlahs"),
      fetchJson("/api/hotels")
    ]);

  agents = agentResponse.agents;
  units = unitResponse.units || [];
  summaryHistory = summaryResponse.history || [];
  currentEnvironment = environmentResponse.environment;
  const hamlahsChanged = hamlahs.length !== (hamlahResponse.hamlahs || []).length;
  hamlahs = hamlahResponse.hamlahs || [];
  hotels = hotelResponse.hotels || [];
  if (hamlahsChanged) {
    populateHamlahOptions();
  }
  populateGroupFilterOptions(agents);
  renderSummary(summaryResponse.summary);
  renderMap(agents, currentEnvironment);
  renderAgents(agents);
  renderChart(summaryHistory);
  applyEnvironmentForm(environmentResponse.environment);
  await refreshLlmStatus();
}

// Advance the simulation by one ritual tick and refresh all UI panels.
async function runSimulationStep() {
  if (simulationBusy) {
    return;
  }

  // The busy flag prevents overlapping step requests from double-advancing the
  // simulation when users click quickly or playback is running.
  simulationBusy = true;
  try {
    await fetchJson("/api/simulate/step", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getEnvironmentPayload())
    });
    await refreshAll();

    // Proactively surface the analytics report the moment the simulation
    // reaches the end, in addition to the manual "Generate Report" button.
    if (!autoReportShownForRun && currentEnvironment?.current_ritual === "Hajj Complete") {
      autoReportShownForRun = true;
      await fetchAndRenderAnalyticsReport();
      document.querySelector(".analytics-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // The backend writes the LLM after-action report to reports/ automatically
    // at Hajj Complete; mirror it into the dashboard the same way.
    if (!llmReportShownForRun && currentEnvironment?.current_ritual === "Hajj Complete") {
      llmReportShownForRun = true;
      await fetchAndRenderLlmReport(false);
    }
  } finally {
    simulationBusy = false;
  }
}

// Start automatic repeated simulation steps at the selected speed.
function startPlayback() {
  if (playbackTimer) {
    clearInterval(playbackTimer);
  }

  // Playback repeatedly posts the current environment form values as each tick
  // is advanced.
  setPlaybackState(true);
  playbackTimer = setInterval(() => {
    runSimulationStep().catch((error) => {
      stopPlayback();
      summaryCards.innerHTML = `<div class="stat-card"><strong>Error</strong><span>${error.message}</span></div>`;
    });
  }, getPlaybackDelay());
}

// ============================================================
// Map layer filter panel and environment-controls accordion
// ------------------------------------------------------------
// Both reuse a simple max-height CSS transition for expand/collapse, so no
// animation library is needed; only visibility toggling requires JS.
// ============================================================

// Show/hide one Leaflet layer group without destroying its markers.
function toggleLayerGroup(layerGroup, isVisible) {
  if (!layerGroup || !map) {
    return;
  }
  const hasLayer = map.hasLayer(layerGroup);
  if (isVisible && !hasLayer) {
    map.addLayer(layerGroup);
  } else if (!isVisible && hasLayer) {
    map.removeLayer(layerGroup);
  }
}

// Map a layer-panel checkbox's data-layer value to the matching layer group.
function applyLayerVisibility(layerKey, isVisible) {
  if (layerKey === "pilgrims") {
    toggleLayerGroup(mapLayerGroup, isVisible);
    return;
  }
  if (layerKey === "routes") {
    toggleLayerGroup(routeLayerGroup, isVisible);
    return;
  }
  if (layerKey === "sites") {
    toggleLayerGroup(siteLayerGroup, isVisible);
    return;
  }
  if (layerKey === "hotels") {
    toggleLayerGroup(hotelLayerGroup, isVisible);
    return;
  }
  const getter = UNIT_LAYER_GROUPS[layerKey];
  if (getter) {
    toggleLayerGroup(getter(), isVisible);
  }
}

const mapLayersPanel = document.querySelector(".map-layers-panel");
const layersToggleButton = document.querySelector(".layers-toggle");

layersToggleButton?.addEventListener("click", () => {
  mapLayersPanel?.classList.toggle("is-collapsed");
});

document.querySelectorAll(".layers-body input[type='checkbox']").forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    applyLayerVisibility(checkbox.dataset.layer, checkbox.checked);
  });
});

// Expand/collapse each environment-controls section independently.
document.querySelectorAll(".accordion-header").forEach((header) => {
  header.addEventListener("click", () => {
    header.parentElement?.classList.toggle("is-open");
  });
});

// Wire roster controls to filtering/sorting behavior.
applyRosterFiltersButton?.addEventListener("click", applyRosterFilters);
applyRosterSortButton?.addEventListener("click", applyRosterSort);
clearRosterFiltersButton?.addEventListener("click", clearRosterFilters);
rosterSearchInput?.addEventListener("input", applyRosterFilters);
groupFilterSelect?.addEventListener("change", applyRosterFilters);
healthFilterSelect?.addEventListener("change", applyRosterFilters);
riskFilterSelect?.addEventListener("change", applyRosterFilters);
sortRosterSelect?.addEventListener("change", applyRosterFilters);

// Create one manual pilgrim from the form and reload dashboard data.
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

// Generate a random pilgrim population and add it to the active roster.
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

// Run a single simulation step when the environment form is submitted.
environmentForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await runSimulationStep();
});

// Start and pause the automatic playback loop.
startSimulationButton?.addEventListener("click", () => {
  startPlayback();
});

pauseSimulationButton?.addEventListener("click", () => {
  stopPlayback();
});

// Restart the interval if speed changes while playback is active.
playbackSpeedSelect?.addEventListener("change", () => {
  if (playbackTimer) {
    startPlayback();
  }
});

// Reset the ritual timeline but keep the current roster.
resetDaysButton?.addEventListener("click", async () => {
  stopPlayback();
  await fetchJson("/api/simulate/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({})
  });

  autoReportShownForRun = false;
  llmReportShownForRun = false;
  renderAnalyticsReport(null);
  renderLlmReport(null);
  await refreshAll();
});

// Reload the original seed agents and restore all dashboard controls.
restartDashboardButton?.addEventListener("click", async () => {
  stopPlayback();
  await fetchJson("/api/dashboard/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({})
  });

  autoReportShownForRun = false;
  llmReportShownForRun = false;
  renderAnalyticsReport(null);
  renderLlmReport(null);
  resetManualDefaults();
  clearRosterFilters();
  await refreshAll();
});

// ============================================================
// Camera control, fullscreen, and click-to-place unit deployment
// ------------------------------------------------------------
// Free Roam leaves the map exactly where the operator left it; Focus Lock
// follows the last-clicked pilgrim/unit. Deploy buttons arm "placement
// mode" so the next map click drops a new unit at the nearest node.
// ============================================================

// Switch between Free Roam and Focus Lock camera behavior.
cameraModeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    cameraMode = button.dataset.mode;
    cameraModeButtons.forEach((item) => item.classList.toggle("is-active", item === button));
    if (cameraMode === "focus_lock") {
      applyFocusLock();
    }
  });
});

// Manually recenter the map on the active route/agents (round-1 behavior),
// now opt-in instead of running automatically on every tick.
recenterMapButton?.addEventListener("click", () => {
  ensureMap();
  mapHasInitialFit = false;
  ensureAirportVisible(agents, currentEnvironment);
});

// Toggle fullscreen on the map area; Leaflet needs an explicit resize nudge
// once the browser finishes resizing the element.
fullscreenToggleButton?.addEventListener("click", () => {
  if (!mapWrapEl) {
    return;
  }
  if (document.fullscreenElement) {
    document.exitFullscreen();
  } else {
    mapWrapEl.requestFullscreen();
  }
});

document.addEventListener("fullscreenchange", () => {
  setTimeout(() => map?.invalidateSize(), 60);
});

// Enter/exit placement mode for one emergency-unit type.
function setPlacementMode(unitType) {
  placementMode = unitType ? { unitType } : null;
  deployButtons.forEach((button) => {
    button.classList.toggle("is-active", Boolean(unitType) && button.dataset.unitType === unitType);
  });
  if (mapWrapEl) {
    mapWrapEl.classList.toggle("placement-mode", Boolean(placementMode));
  }
  if (placementModeBanner) {
    placementModeBanner.hidden = !placementMode;
  }
}

deployButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const unitType = button.dataset.unitType;
    setPlacementMode(placementMode?.unitType === unitType ? null : unitType);
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && placementMode) {
    setPlacementMode(null);
  }
});

// Snap a map click to the nearest known node and deploy the armed unit there.
async function deployUnitAt(latlng) {
  const unitType = placementMode?.unitType;
  if (!unitType) {
    return;
  }
  const nodeId = findNearestNodeId(latlng);
  setPlacementMode(null);
  if (!nodeId) {
    return;
  }

  await fetchJson("/api/units/deploy", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ unit_type: unitType, node_id: nodeId })
  });
  await refreshAll();
}

// Initial UI state and first data load.
setPlaybackState(false);
refreshAll().catch((error) => {
  summaryCards.innerHTML = `<div class="stat-card"><strong>Error</strong><span>${error.message}</span></div>`;
});
