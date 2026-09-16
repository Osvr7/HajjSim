# 🕋 HajjSim Agent Studio

![Status](https://img.shields.io/badge/Status-Prototype-blue)
![Python](https://img.shields.io/badge/Backend-Python-green)
![JavaScript](https://img.shields.io/badge/Frontend-JS%20%7C%20Leaflet-yellow)

**HajjSim Agent Studio** is a predictive digital twin simulation platform utilizing Multi-Agent Swarm Intelligence to model pilgrim movement, stress, and crowd-risk conditions across Hajj locations. 

Current crowd management is heavily reactive; HajjSim aims to make it **proactive**. By simulating the behavior of millions of pilgrims under varying environmental pressures and a rigid spatial-temporal ritual schedule, this system allows operators to anticipate bottlenecks, density waves, and panic cascades before they occur in the real world.

## 📸 Dashboard Preview

![HajjSim Dashboard](assets/dashboard_map.png)

## ✨ Core Features
* **4-Layer Agent Anatomy:** Pilgrim agents operate with distinct cognitive profiles: Static (DNA), Dynamic (Vitals), Memory, and a Behavior Engine (*Perceive → Decide → Act* loop).
* **Ritual Progression Logic:** Agents navigate a spatial-temporal graph governed by an event-driven, macro-temporal tick engine. 1 tick = 1 distinct ritual stage.
* **Live GPS & Heatmapping:** Real-time visualization of crowd movement and density stress using Leaflet.js.
* **LLM-Driven Decisions:** Pedestrian agents observe their surroundings (congestion, hazards, distances, risk) and ask a language model which of the engine's valid actions to take, with the rule-based ladder as a safe fallback.
* **Adversarial Testing:** Ability to dynamically inject environmental hazards (e.g., blocked gates, dropped luggage) to test swarm resilience.
* **Operational Analytics:** Live charting of the overall "Severity Index" and individual agent roster inspection.

## 🏗️ Technical Architecture
* **Backend:** Python HTTP server (`app.py`) running an event-driven simulation engine (`hajj_agents.py`).
* **Frontend:** Interactive Single-Page Application (SPA) built with Vanilla JavaScript, HTML5, and CSS3.
* **Libraries:** Leaflet.js, Leaflet.heat, Chart.js.
* **Data Storage:** JSON-based state management (`pilgrims.json`).

![Agent Architecture](assets/agent_diagram.png)

## 🚀 Quick Start

```bash
git clone https://github.com/Osvr7/HajjSim.git
cd HajjSim
python app.py
```

Then open <http://127.0.0.1:8000>. There are no third-party dependencies — the
backend is standard-library Python and the frontend is vanilla JS.

To drive the agents with a language model, set `LLM_API_KEY` first (next section).
Without it the simulation runs exactly as before, on the rule-based engine.

To run the terminal version instead:

```bash
python main.py
```

Type `step` to advance a tick, `generate 20` to add pilgrims, or a pilgrim ID to
inspect one.

---

## 🧠 LLM-Driven Pedestrian Decisions

Each pilgrim now **observes its environment and asks a language model what to do**
instead of only following a fixed rule ladder. The rule engine still runs first
every tick and its answer is handed to the model as the safe fallback, so a
missing key, a timeout, or a hallucinated action degrades to the original
behavior rather than breaking the run.

### Where the API key goes

**Only in an environment variable named `LLM_API_KEY`.** It is never read from a
source file, never written to disk, and never included in any API response, log
or report.

1. Copy the template and fill in your key:

   ```bash
   cp .env.example .env
   ```

2. `.env` is git-ignored. The server does **not** auto-load it — it reads real
   environment variables, so export them in the shell you launch `app.py` from.

   **Windows PowerShell**

   ```powershell
   $env:LLM_API_KEY = "your-key-here"
   $env:LLM_PROVIDER = "gemini"
   python app.py
   ```

   **Windows CMD**

   ```cmd
   set LLM_API_KEY=your-key-here
   set LLM_PROVIDER=gemini
   python app.py
   ```

   **macOS / Linux**

   ```bash
   export LLM_API_KEY="your-key-here"
   export LLM_PROVIDER="gemini"
   python app.py
   ```

The dashboard's **LLM Agent Intelligence** panel shows whether the model is
actually live. If you set the key after starting the server, `POST /api/llm/reload`
re-reads the environment without a restart.

### Configuring the LLM

| Variable | Default | What it does |
| --- | --- | --- |
| `LLM_API_KEY` | _(none)_ | **Required.** Your key/token. `GEMINI_API_KEY` is accepted as a fallback. |
| `LLM_PROVIDER` | `gemini` | `gemini`, `openai`, `anthropic`, or `echo` (offline test — no key, no network). |
| `LLM_MODEL` | per provider | e.g. `gemini-1.5-flash`, `gpt-4o-mini`, `claude-haiku-4-5-20251001`. |
| `LLM_BASE_URL` | _(vendor)_ | Override for a self-hosted or proxied endpoint. |
| `LLM_ENABLED` | `1` | Set to `0` to run the original rule-based agents. |
| `LLM_MAX_AGENTS` | `10` | How many pilgrims the model drives. `0` = the entire roster. |
| `LLM_MAX_CALLS_PER_TICK` | `40` | Hard ceiling on live API calls per tick. `0` = unlimited. |
| `LLM_CACHE_ENABLED` | `1` | Reuse one answer across near-identical situations. |
| `LLM_TIMEOUT_SECONDS` | `12` | Per-call timeout. |
| `LLM_MAX_RETRIES` | `1` | Retries before falling back to the rule-based action. |
| `LLM_TEMPERATURE` | `0.2` | Sampling temperature. |

> **Cost note.** A full run is ~240 ticks. With `LLM_MAX_AGENTS=0` and a large
> roster that means a very large number of API calls. The defaults keep a demo
> run in the low hundreds of calls; raise them deliberately.

### Trying it with no key at all

```bash
LLM_PROVIDER=echo LLM_MAX_AGENTS=0 python app.py
```

`echo` is an offline stand-in provider that makes no network call but exercises
every prompt-building, parsing, validation, logging and reporting path.

### How one decision is made

```
PilgrimAgent.step()
  -> perceive environment          (vitals, hazards, group)
  -> assess_risk()                 -> risk level / score / named factors
  -> BehaviorEngine.decide_action()
       -> _rule_based_decision()   -> the SAFE FALLBACK action
       -> llm_override(...)        -> app.llm_pilgrim_override()
            build_observation()    -> what the pilgrim can see
            available_actions()    -> what the engine can actually execute
            llm_decide_action()    -> structured prompt -> model -> JSON
                                   -> validate against available_actions
                                   -> on any failure: return the fallback
  -> _execute_action()             -> the world changes
  -> decision log records the outcome
```

The model must answer with JSON and may only pick a value that appears in the
supplied action list:

```json
{ "action": "AVOID_CROWD", "reason": "The current node is over capacity while the relief node is clear." }
```

Anything else — prose, a fenced block, an invented action, a timeout, an HTTP
error — is caught, the rule-based action is used instead, and the reason is
recorded in the log.

### What the model sees each step

The pilgrim's current location and zone; its current path and every connected
road; distance in hops to each candidate destination; whether a destination
requires a bus; live occupancy/capacity and a congestion label per node; the
active hazard with a plain-language description; the detected risk level with the
named factors that produced it; full vitals (stress, fatigue, hydration, panic);
group status; and the pilgrim's recent nodes, recent events and repeated visits.

### Available actions

The engine only ever offers actions it can genuinely execute, so a valid choice
can never be un-executable:

| Action | Meaning |
| --- | --- |
| `WAIT_FOR_RITUAL_WINDOW` | Stay in the current place. |
| `REST` | Stop and recover fatigue, stress and hydration. |
| `MOVE_TO_<ritual target>` | Continue on the planned route. |
| `MOVE_TO_<neighbour>` | Change to another connected road/location. |
| `AVOID_CROWD` | Divert to the designated lower-pressure relief node. |
| `MOVE_TO_<group node>` | Move to rejoin the group. |
| `STRAGGLE` | Break from the group on a short unplanned detour. |
| `ENTER_PANIC_MODE` | Emergency evacuation (offered only in genuine danger). |

When the convoy coordinator owns the pilgrim (`IN_TRANSIT`, or queued for a
corridor bus) there is no real choice, so no API call is made at all.

### Swapping in a different model

`llm_decision.py` is the only file that talks to a model. To add a backend:

```python
from llm_decision import BaseLLMProvider, register_provider

class MyProvider(BaseLLMProvider):
    name = "mine"

    def complete(self, system_prompt, user_prompt):
        return my_client.generate(system_prompt, user_prompt)  # raw text back

register_provider("mine", MyProvider)   # then set LLM_PROVIDER=mine
```

Nothing in the simulation, the logging, or the report needs to change.

### Logging and the automatic report

Every model decision and every significant risk is recorded as it happens in
`simulation_log.py`, so the report is built from what actually occurred rather
than from assumptions:

* **Decision log** — the environment seen, the options offered, the action
  chosen, the reason, the source (`llm` / `cache` / `fallback_*`), the latency,
  and the post-execution result (where the pilgrim ended up, how risk and vitals
  moved).
* **Risk events** — a lifecycle, not a point in time: opens when a pilgrim
  crosses into a high/severe risk band, collects every decision taken while it is
  open, and closes with an outcome verdict (`avoided`, `reduced`, `unchanged` or
  `worsened`).

When the run reaches **Hajj Complete** the six-section analytical report is
generated automatically and written to `reports/` as Markdown + JSON, alongside
the raw decision log. The dashboard renders the same report in the **LLM Agent
Intelligence** panel, and the *Generate LLM Simulation Report* button forces it
at any time.

Report sections: **1** Simulation overview · **2** Decision analysis (action
frequencies, important decision points, successful and unsuccessful examples) ·
**3** Risk analysis (when, where, cause, environment, decision, aftermath and
effectiveness for each event) · **4** Agent performance (risk avoidance,
consistency, response time, unnecessary vs. successful route changes, movement
efficiency, oscillation) · **5** Concrete improvement suggestions, each with the
evidence that produced it · **6** Final summary.

### API endpoints added

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/llm/status` | Provider, model and live counters. Never returns the key. |
| `POST` | `/api/llm/reload` | Re-read `LLM_*` env vars without restarting. |
| `GET` | `/api/logs/decisions?limit=N` | Recent decision records. |
| `GET` | `/api/logs/risks` | All risk-event lifecycles. |
| `GET` | `/api/logs/simulation` | Decisions + risks + per-tick aggregates. |
| `GET` | `/api/analytics/simulation-report` | The report as JSON (read-only). |
| `GET` | `/api/analytics/simulation-report.md` | The same report as Markdown. |
| `POST` | `/api/analytics/simulation-report` | Build it **and** write it to `reports/`. |

### Files added by this feature

| File | Role |
| --- | --- |
| `llm_decision.py` | Providers, prompt building, parsing, validation, budget, cache, fallback. |
| `simulation_log.py` | Decision records, risk-event lifecycles, per-tick aggregates. |
| `analysis_report.py` | The six-section report, as a dict and as Markdown. |
| `.env.example` | Template for `LLM_API_KEY` and the other `LLM_*` settings. |
