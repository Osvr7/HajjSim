const mapPositions = {
  Mina_Camp_1: { x: 16, y: 68 },
  Mina_Camp_2: { x: 28, y: 63 },
  Mina_Camp_4: { x: 38, y: 58 },
  Jamarat_Bridge: { x: 52, y: 74 },
  Arafat_Gate: { x: 76, y: 46 },
  Arafat: { x: 82, y: 35 },
  Muzdalifah: { x: 68, y: 18 },
  Jamarat: { x: 49, y: 82 },
  Shade_Corridor: { x: 57, y: 50 },
  Transit_Corridor: { x: 60, y: 42 },
  Emergency_Point: { x: 22, y: 24 }
};

const summaryCards = document.querySelector("#summaryCards");
const mapCanvas = document.querySelector("#mapCanvas");
const agentGrid = document.querySelector("#agentGrid");
const agentCardTemplate = document.querySelector("#agentCardTemplate");
const manualForm = document.querySelector("#manualForm");
const randomForm = document.querySelector("#randomForm");

let agents = [];

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
    ["Avg stress", summary.avg_stress],
    ["Avg fatigue", summary.avg_fatigue]
  ];

  items.forEach(([label, value]) => {
    const card = document.createElement("div");
    card.className = "stat-card";
    card.innerHTML = `<strong>${value}</strong><span>${label}</span>`;
    summaryCards.appendChild(card);
  });
}

function renderMap(currentAgents) {
  mapCanvas.innerHTML = "";

  Object.entries(mapPositions).forEach(([name, position]) => {
    const label = document.createElement("div");
    label.className = "node-label";
    label.style.left = `${position.x}%`;
    label.style.top = `${position.y}%`;
    label.textContent = name.replaceAll("_", " ");
    mapCanvas.appendChild(label);
  });

  currentAgents.forEach((agent, index) => {
    const node = agent.state.current_node;
    const base = mapPositions[node] || fallbackPosition(index);
    const dot = document.createElement("button");
    const moodClass = agent.state.is_panicking
      ? "panic"
      : agent.profile.health_status === "stable"
        ? "stable"
        : "support";

    dot.className = `agent-dot ${moodClass}`;
    dot.style.left = `${base.x + jitter(index, 2.8)}%`;
    dot.style.top = `${base.y + jitter(index + 5, 2.4)}%`;
    dot.title = `${agent.profile.pilgrim_id} | ${node}`;
    dot.addEventListener("click", () => scrollToAgent(agent.profile.pilgrim_id));
    mapCanvas.appendChild(dot);
  });
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
      detailBlock("Memory", (agent.memory.short_term.recent_nodes || []).join(", ") || "Fresh agent"),
      detailBlock("Social", (agent.memory.social.known_companions || []).slice(0, 3).join(", ") || "Solo"),
      detailBlock("Conditions", (agent.profile.chronic_conditions || []).join(", ") || "None")
    ].join("");

    agentGrid.appendChild(fragment);
  });
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

function fallbackPosition(index) {
  return {
    x: 15 + ((index * 11) % 70),
    y: 15 + ((index * 7) % 70)
  };
}

function jitter(seed, amount) {
  return ((Math.sin(seed * 12.9898) * 43758.5453) % 1) * amount;
}

async function refreshAll() {
  const [agentResponse, summary] = await Promise.all([
    fetchJson("/api/agents"),
    fetchJson("/api/summary")
  ]);
  agents = agentResponse.agents;
  renderSummary(summary);
  renderMap(agents);
  renderAgents(agents);
}

manualForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = Object.fromEntries(new FormData(manualForm).entries());

  await fetchJson("/api/agents", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData)
  });

  manualForm.reset();
  manualForm.group_id.value = "G_200";
  manualForm.age.value = "40";
  manualForm.mobility.value = "0.85";
  manualForm.nationality.value = "Saudi";
  manualForm.language.value = "Arabic";
  manualForm.health_status.value = "stable";
  manualForm.risk_tolerance.value = "0.5";
  manualForm.initial_node.value = "Mina_Camp_4";
  manualForm.target_node.value = "Arafat";
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

refreshAll().catch((error) => {
  summaryCards.innerHTML = `<div class="stat-card"><strong>Error</strong><span>${error.message}</span></div>`;
});
