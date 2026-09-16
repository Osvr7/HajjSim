# MANSAK / HajjSim — Feature Backlog (Single Source of Truth)

_Last verified against the codebase: 2026-09-16 (bus behaviour round)._

This is the canonical status list for every feature promised anywhere for this project — the README, the course pitch deck's "Future Plan" roadmap slide, the two implemented upgrade rounds, and the MiroFish-inspired adoption ideas — consolidated into one table per source. Every status below was verified by reading the actual code (not just recalled from a plan or a chat), but **it will drift the moment the code changes again without this file being refreshed.** Treat a "Done" row as a claim, not a guarantee — re-check the cited evidence (file/function names) before relying on it for something important.

**Status legend**: ✅ Done — implemented and behaviorally verified · 🟡 Partial — implemented but incomplete, cosmetic, or write-only · ⚠️ Done-but-unverified — code path exists but never exercised against the real dependency it needs · ⬜ Not started — no code for it exists.

## 1. Baseline platform (README "Core Features" + course pitch deck, slides 1-7)

| # | Feature (as promised) | Status | Evidence | Notes |
|---|---|---|---|---|
| 1.1 | 4-Layer Agent Anatomy (Static/Dynamic/Memory/Behavior, Perceive→Decide→Act) | ✅ Done | `hajj_agents.py`: `StaticProfile`/`DynamicState`/`Memory`/`BehaviorEngine`, `PilgrimAgent.step()` | Core model, unchanged in spirit since before Round 1. |
| 1.2 | Ritual Progression Logic over a spatial-temporal graph | ✅ Done | `HAJJ_RITUAL_SCHEDULE`, `ROUTE_GRAPH`/`plan_route()` (plain BFS, see 5.2), `get_ritual_window_for_minutes()` | README still says "1 tick = 1 distinct ritual stage" — **stale**; ticks have been time-based since Round 1 (20 min) and are now 60 min (Round 2). README not corrected. |
| 1.3 | Live GPS & Heatmapping | ✅ Done | `web/app.js`: `siteGps`, Leaflet + Leaflet.heat, `renderHeatmap()` | |
| 1.4 | "Adversarial Testing" — dynamically inject hazards | 🟡 Partial | `environmentForm` hazard dropdown, `EnvironmentState.apply_updates()` | Only one global hazard active at a time via a dropdown; no scripted adversarial scenarios, no automated stress-test/red-team agent. Literal claim ("inject hazards") holds; "adversarial" framing is marketing. |
| 1.5 | Operational Analytics (severity index chart + roster) | ✅ Done | `renderChart()`, agent roster cards, `generate_analytics_report()` | Substantially extended in Round 2 (see 3.10-3.12). |
| 1.6 | Scale claim: "1.28M Active Pilgrims" (pitch deck mockup stat) | ⬜ Not started / aspirational | `app.py`: `/api/agents/random` caps at `min(500, count)` per call | Real practical ceiling is low hundreds per call; the deck's 1.28M figure is a UI mockup, not a tested capacity. |

## 2. Round 1 upgrade (2026-09-15)

| # | Feature | Status | Evidence | Notes |
|---|---|---|---|---|
| 2.1 | Time-based tick engine (minutes/tick, ritual windows, straggling) | ✅ Done | `SIMULATED_MINUTES_PER_TICK`, `get_ritual_window_for_minutes()`, `DynamicState.is_straggling` | Superseded twice on tick length (20→60 min in Round 2); logic itself intact. |
| 2.2 | Hamlah (campaign) architecture | ✅ Done (core) / 🟡 Partial (visibility) | `hajj_units.py`: `Hamlah`/`HamlahRegistry` | `declared_pilgrim_count` vs. live `actual_pilgrim_count` is tracked server-side but **never surfaced in the UI** — no Hamlah roster/detail view exists at all, only a per-pilgrim "Hamlah: H_00x" text line in the pilgrim sidebar. |
| 2.3 | Heterogeneous units (Bus/Marshal/Police/Ambulance classes) | ✅ Done | `hajj_units.py`: `OperationalUnit` subclasses, `UnitFactory` | |
| 2.4 | KAIA Hajj Terminal spawn coordinates | ✅ Done | `web/app.js`: `siteGps.Jeddah_Airport` | Cosmetic-only change, node id kept for compatibility. |
| 2.5 | Map/filter/sidebar UI (layer toggles, detail sidebar) | ✅ Done | `.map-layers-panel`, `#detailSidebar`, `openPilgrimDetailSidebar`/`openUnitDetailSidebar` | Extended in Round 2 with hotels layer + `openHotelDetailSidebar`. |
| 2.6 | Environment controls redesign (accordion sections) | ✅ Done | `.accordion-section` x4 in `index.html` | Not further restyled in Round 2. |
| 2.7 | Analytics report (bottlenecks/strengths/suggestions) | ✅ Done | `generate_analytics_report()` (bullet-point version) | Superseded/extended by Round 2's narrative + charts (3.10-3.11). |

## 3. Round 2 upgrade (2026-09-15)

| # | Feature | Status | Evidence | Notes |
|---|---|---|---|---|
| 3.1 | Mandatory, nationality-locked Hamlah membership | ✅ Done | `StaticProfile.__post_init__` raises if missing; `normalize_nationality`/`NATIONALITY_ALIASES` | Manual-creation form restricted to the 10 valid nationalities (bug found + fixed — see §6). |
| 3.2 | Hotel = Hamlah base camp, capacity/occupancy | ✅ Done | `hajj_units.py`: `Hotel`/`HotelRegistry`, `sync_hotel_occupancy()` | Occupancy badge renders live on the map. |
| 3.3 | Heterogeneous entity sidebar | ✅ Done | (same as 2.5, now +hotels) | |
| 3.4 | Macro-tick time engine (1 tick = 1 hour) + corridor travel delays | ✅ Done | `SIMULATED_MINUTES_PER_TICK = 60`, `INTERCITY_CORRIDOR_MINUTES`, `corridor_ticks()` | |
| 3.5 | Shared corridor bus fleet (not Hamlah-owned), cohort travel | ✅ Done | `ConvoyDispatchCoordinator`, 9-bus fleet in `UnitFactory` | Buses are shared/fixed-route; pilgrims from one Hamlah board together as a cohort. |
| 3.6 | Contextual movement (pedestrian-only in-zone, bus-only cross-zone) + pathfinding | ✅ Done | `zone_of()`, `next_hop_zone()` (BFS), `_rule_based_decision` gating | **Two stall bugs found and fixed** — see §6. Verified by a full run to "Hajj Complete" (240 ticks) with zero permanent stalls. |
| 3.7 | Smooth visual interpolation (no teleporting) | ✅ Done | `animateMarkerTo()` (pilgrims), `getUnitDisplayLatLng()` interpolating `transit_progress` (buses) | Verified pixel-exact match between computed and rendered bus position mid-transit. |
| 3.8 | Camera control (Free Roam / Focus Lock, no auto-fitBounds) | ✅ Done | `cameraMode`, `applyFocusLock()`, `ensureAirportVisible()` moved behind manual Recenter button | |
| 3.9 | Immersive dashboard: fullscreen map, click-to-place units, Play/Pause indicator | ✅ Done | `mapWrapEl.requestFullscreen()`, `setPlacementMode()`/`deployUnitAt()`, `#playbackStateIndicator` | Control *panel* itself is still Round 1's accordion, not further restyled — "redesigned" is light-touch (an indicator + buttons added), not a visual overhaul. |
| 3.10 | Narrative Data Generation (NLG) | ✅ Done (template) / ⚠️ Unverified (Gemini) | `generate_narrative_via_llm()` checks `GEMINI_API_KEY`; `_template_narrative()` fallback | Template path fully verified live. Gemini path (`gemini-1.5-flash` via `google-generativeai`) was written from stable public patterns with no bundled reference for this environment and has never been run against a real key — verify the current SDK shape before enabling. |
| 3.11 | Graphical Data Representation (bar charts) | ✅ Done | `renderBottleneckChart()`, `renderDeploymentImpactChart()` (Chart.js) | |
| 3.12 | Dynamic Response Tracking (deployment before/after impact) | ✅ Done | `evaluate_deployment_impact()` | Deployed a police unit mid-run, saw a real before/after ratio in the chart and narrative. |

## 3b. Round 3 upgrade (2026-09-16) — LLM decision layer

| # | Feature | Status | Evidence | Notes |
|---|---|---|---|---|
| 3b.1 | LLM chooses the pedestrian action each step | ✅ Done | `llm_decision.py`: `llm_decide_action()`; `app.py`: `llm_pilgrim_override()` wired into `build_agent_from_record`/`generate_agents`/`build_manual_agent` | Rule ladder runs first and is passed in as the fallback, so the model *replaces* the decision rather than bypassing the engine. |
| 3b.2 | Environment → prompt conversion | ✅ Done | `PilgrimAgent.build_observation()`; `llm_decision.build_decision_prompt()` | Location, zone, connected roads, per-destination hop distance and bus requirement, live occupancy/capacity + congestion label, hazard with plain-language description, risk level/score/factors, vitals, group state, recent nodes/events/repeated visits. |
| 3b.3 | Action catalogue restricted to executable actions | ✅ Done | `PilgrimAgent.available_actions()` | Every entry maps to a real branch of `_execute_action()`. Convoy-owned states (`IN_TRANSIT`, queued `AWAITING_TRANSPORT`) collapse to one locked entry and skip the API call entirely. |
| 3b.4 | Structured JSON output + action validation | ✅ Done | `parse_llm_decision()` | Tolerates fences, leading prose and bare strings; rejects any action outside `available_actions`. 9 parser cases verified. |
| 3b.5 | Error handling and safe fallback | ✅ Done | `LLMDecisionEngine.decide()` — sources `fallback_error` / `fallback_invalid` / `fallback_budget` / `disabled` | Verified against injected HTTP 401, an unexpected `ZeroDivisionError`, a hallucinated action, an empty action set, a missing key, and budget exhaustion. The simulation never raises. |
| 3b.6 | Modular / swappable provider layer | ✅ Done | `BaseLLMProvider` + `PROVIDERS` + `register_provider()`; Gemini, OpenAI-compatible, Anthropic, and an offline `echo` provider | Stdlib `urllib` only — no new dependency. Swapping models is one env var. |
| 3b.7 | API key handling | ✅ Done | `LLMSettings.from_env()` reads `LLM_API_KEY` only; `.env` + `reports/` git-ignored; `status_payload()` reports `api_key_present` but never the value | No key is ever written to source, disk, log, or API response. |
| 3b.8 | Explicit risk model | ✅ Done | `assess_risk()`, `HAZARD_RISK_WEIGHTS`, `classify_risk_level()`, `SIGNIFICANT_RISK_LEVELS` | 0-100 score with named contributing factors, computed every tick right after perception, before the decision. |
| 3b.9 | Decision logging | ✅ Done | `simulation_log.DecisionRecord`, opened pre-execution and closed post-execution by `finalize_agent_decision` | Records what was seen, what was offered, what was chosen, why, by which source, and the resulting node + risk/vitals deltas. |
| 3b.10 | Risk-event logging | ✅ Done | `simulation_log.RiskEvent`, `observe_risk()` / `_close_risk()` | A lifecycle, not a point: opens on entry to a high/severe band, accumulates the decisions taken while open, closes with an `avoided`/`reduced`/`unchanged`/`worsened` verdict. |
| 3b.11 | Automatic six-section analytical report | ✅ Done | `analysis_report.build_simulation_report()` / `render_markdown()`; `maybe_finalize_run()` fires at "Hajj Complete" | Written to `reports/` as Markdown + JSON plus the raw log. Verified end-to-end on a 239-tick run producing 8,673 decisions and 794 risk events. |
| 3b.12 | Dashboard surface | ✅ Done | `web/index.html` LLM Agent Intelligence panel; `renderLlmStatus()` / `renderLlmReport()`; pilgrim sidebar decision fields | Status strip (live/inactive, calls, cache hits, failures, latency), all six report sections, and per-pilgrim *Decided by / Decision reason / Rule-based fallback / Risk level / Risk factors*. |
| 3b.13 | Cost / volume control | ✅ Done | `LLM_MAX_AGENTS`, `LLM_MAX_CALLS_PER_TICK`, `LLM_CACHE_ENABLED`; `refresh_llm_agent_selection()` | Necessary, not cosmetic: a 240-tick run over the full roster would otherwise mean six-figure API calls. Defaults keep a demo in the low hundreds. |
| 3b.14 | Verified against a real paid API | ⚠️ Not verified | Gemini/OpenAI/Anthropic request shapes written from their documented REST contracts; only the offline `echo` provider has actually been run | **The same caveat as §3.10.** Every code path around the call is verified, but no live key has been used. Confirm the model name and response shape on first real run. |

## 3c. Round 4 upgrade (2026-09-16) — demand-driven, route-bound buses

| # | Feature | Status | Evidence | Notes |
|---|---|---|---|---|
| 3c.1 | Bus will not move below a minimum rider count | ✅ Done | `MIN_RIDERS_TO_MOVE = 5`; `BusUnit.has_minimum_riders()`; `_dispatch_from_stops` | Verified at 0/1/3/4/5/6/20 riders. Replaces round 2's `MAX_IDLE_TICKS_BEFORE_EMPTY_DISPATCH`, which dispatched empty buses after 2 idle ticks. |
| 3c.2 | Capacity is never exceeded | ✅ Done | `BusUnit.is_full` / `remaining_capacity`; boarding loop | Surplus pilgrims stay queued rather than being dropped. A 500-seat bus with 2 riders still waits — high capacity does not force movement. |
| 3c.3 | Movement restricted to the bus's own route | ✅ Done | `BusUnit.is_valid_next_hop()`, `_depart()` refuses and logs | A fabricated segment is refused, no event is emitted, and the bus stays put. Verified over a full run: **0** off-route positions across 239 ticks. |
| 3c.4 | Sequential route with reversal at the end | ✅ Done | `route_stops`/`route_zones`/`route_index`, `next_route_index()`, `peek_next_stop()` | A→B→C→D→C→B→A verified on a 4-stop route. Existing corridor buses are 2-stop routes, so their behaviour is unchanged. |
| 3c.5 | Create a new route only when necessary | ✅ Done | `BusRouteRegistry.create_route_for()`, `_plan_routes_for_unmet_demand()` | Existing routes are checked first; a new route is built from the corridor graph and validated segment-by-segment. A full run generated **0** routes (all 6 corridors already served), which is the correct outcome. |
| 3c.6 | Demand-driven movement | ✅ Done | `_collect_demand()`, `_should_reposition()` | |
| 3c.7 | Fixed decision priority order | ✅ Done | `ConvoyDispatchCoordinator.step()` docstring + `_dispatch_from_stops` ordering | Count → capacity → route → demand → existing route → new route → valid segment. |
| 3c.8 | Bus behaviour logging | ✅ Done | `bus_log()`, `BUS_LOG` env var | Silenceable with `BUS_LOG=0`. |
| 3c.9 | Dashboard surface | ✅ Done | `openUnitDetailSidebar` bus branch | Riders/seats, movement state ("Holding — 2/5 riders"), minimum, full route, heading. |
| 3c.10 | Two deliberate exceptions to the strict minimum | ⚠️ By design | `MAX_WAIT_TICKS_BEFORE_UNDERFULL_DISPATCH`, `ALLOW_EMPTY_REPOSITIONING` | **A strict reading of "never move below the minimum" deadlocks the run.** Both exceptions are narrow, configurable and logged. Over a full run all 52 under-minimum departures were attributable to one of them; 0 unexplained. Set both to 0/False for strict enforcement — and expect stranded pilgrims. |

## 4. Official course "Future Plan" roadmap (`Documents/HajjSim_Agent_Studio_Presentation.pdf`, slide 8)

This slide is the team's own stated next-stage roadmap — distinct from, and mostly not covered by, Rounds 1-2 above.

| # | Feature (as promised on the slide) | Status | Evidence | Notes |
|---|---|---|---|---|
| 4.1 | **Leader Agents** — guide groups, keep members together, share instructions | 🟡 Partial (data only) | `Memory.social.leader_id` is assigned per group (`_link_social_groups`); now surfaced in `build_observation()` under `group.leader_id` | Still not a leader: no agent's action is influenced by being or having a leader. The id is now *visible to the model in the prompt*, which is a prerequisite for real leader behaviour, not the behaviour itself. |
| 4.2 | **Transportation Agents** — buses, shuttles, delays, movement between sites | ✅ Done | Round 2 §3.4-3.7 | Fully delivered by Round 2's convoy system. |
| 4.3 | **Housing Agents** — camps, hotels, room flow, accommodation pressure | ✅ Done | Round 2 §3.2 | Fully delivered by Round 2's Hotel system. |
| 4.4 | **Agent Communication** — share warnings, route updates, help requests | ⬜ Not started | `Memory.social.help_contacts` exists but is a static seeded list (`["Medical_Desk_1"]`), never dynamically updated; no message-passing between agents anywhere | Real gap: no agent ever sends/receives anything from another agent. |
| 4.5 | **Next Stage** — more agents, larger populations, smarter prediction | 🟡 Partial | 500-agent cap per `/api/agents/random` call (§1.6); "smarter prediction" partly addressed by Round 2's LLM narrative (§3.10) | No load-testing done at scale; "smarter prediction" is the Gemini narrative at best, not a forecasting model. |

## 5. MiroFish-inspired adoption ideas (proposed, not requested as a formal round)

| # | Idea | Status | Evidence | Notes |
|---|---|---|---|---|
| 5.1 | Wire up the `llm_override` hook for LLM-driven pilgrim decisions | ✅ Done | `app.py`: `llm_pilgrim_override()` is passed into every agent factory path; `llm_decision.py` | Delivered by Round 3 (see §3b). The rule ladder still runs first and is handed to the model as the fallback, so behaviour with `LLM_ENABLED=0` is byte-for-byte the old behaviour. |
| 5.2 | Upgrade plain BFS `ROUTE_GRAPH` to real GraphRAG retrieval | ⬜ Not started | `plan_route()` is textbook BFS over a static adjacency dict | No embeddings, no retrieval, no knowledge graph — despite "digital twin" framing implying more. |
| 5.3 | Richer hazard-informed memory (past hazards shape future routing) | 🟡 Partial (read by the LLM only) | `build_observation()` now emits `history.remembered_hazards` and `location.known_hazard_here`; `_describe_node()` emits `known_hazard_there` per candidate | No longer purely write-only: an LLM-driven pilgrim sees its remembered hazards and can route around them. The **rule-based** ladder still never reads `known_hazards`, so with `LLM_ENABLED=0` this remains write-only. |
| 5.4 | ReportAgent-style automated narrative report | ✅ Done | Round 2 §3.10 (`generate_narrative_via_llm`/`_template_narrative`) | This is the one MiroFish idea Round 2 actually delivered. |
| 5.5 | Deep/interactive drill-in on one pilgrim's *reasoning* | ✅ Done (for LLM-driven agents) | `openPilgrimDetailSidebar()` now shows *Decided by*, *Decision reason*, *Rule-based fallback*, *Risk level* and *Risk factors* | The model returns a one-sentence reason with every action, so the sidebar shows why, what the rule engine would have done instead, and the risk picture that drove it. A rule-based agent still has no explanation trace (there is nothing to explain — the ladder is deterministic). |
| 5.6 | Keep the simulation core open/auditable (B2G trust) | ✅ Done (by construction) | Entire stack is a stdlib Python server + vanilla JS, no closed-source dependency, no external calls unless `GEMINI_API_KEY` is deliberately set | Not a coded "feature" so much as an architectural property that already holds. |

## 6. Cross-cutting gaps and debt found during the last audit

- **README is stale on tick semantics** (§1.2) — still describes "1 tick = 1 ritual stage," true only before Round 1. The rest of the README was rewritten in Round 3; this one line in Core Features was not.
- **The LLM path has never met a real API** (§3b.14) — all four providers are written from documented REST contracts and every failure path is tested with injected faults, but the only provider actually exercised end-to-end is the offline `echo` stand-in. Treat the first live run as the real verification.
- **Only a subset of pilgrims is model-driven by default** (`LLM_MAX_AGENTS=10`) — report figures like "movement efficiency" describe that subset, not the whole population. Set it to 0 for a whole-roster run, and expect the API bill to scale accordingly.
- **Report quality depends on the model** — a full echo-provider run showed 44.8% movement efficiency and 3,286 oscillation events, but the echo provider is a fixed heuristic that always prefers a reroute. Those numbers measure the stand-in, not a real model; re-baseline them on the first live run.
- **No aggregate Hamlah view** (§2.2) — `declared_pilgrim_count` vs `actual_pilgrim_count` is modeled but invisible to an operator.
- **Two write-only memory fields** (`leader_id` §4.1, `known_hazards` §5.3) — data is captured every tick but never read back into any decision, making two "planned" features look implemented in the data model while doing nothing behaviorally. `learned_preferences` is similarly written in `_seed_memory` but not obviously read elsewhere — not yet fully audited.
- **A third movement-stall bug**, same shape as the first two and found the same way (a full run, not a short one): the new empty-repositioning guard treated *any* bus parked in the target zone as coverage, including buses on unrelated routes. Buses serving Mina↔Arafat and Mina↔Muzdalifah were parked in Mina, so the Aziziyah↔Mina bus never repositioned and 18 pilgrims queued for Mina→Aziziyah were stranded. Fixed by narrowing the check to buses whose route actually contains that corridor. End-of-run stranded pilgrims: 10 → 1 (pre-change baseline was 2).
- **Two real movement-stall bugs**, found only by running a *full* simulation to "Hajj Complete" in the browser (not caught by short test runs or unit-level checks):
  1. `ConvoyDispatchCoordinator` grouped waiting pilgrims by `(current_zone, final_target_zone)` directly; the corridor graph is a path with no edges between non-adjacent zones (e.g. Haram↔Arafat), so any multi-hop trip queued forever. Fixed with `next_hop_zone()` (BFS) in `hajj_agents.py`.
  2. A pilgrim whose ritual target changed to their *current* zone while already `AWAITING_TRANSPORT` had no way back to `PEDESTRIAN` (the coordinator skips same-zone pairs by design) and stalled permanently. Fixed in `_rule_based_decision`.
  - Any future change to convoy/zone logic should be re-verified with a full run to completion, not a handful of ticks — both bugs took 40-120+ ticks to manifest.
- **Manual-creation nationality/Hamlah mismatch bug**, found and fixed: the nationality `<select>` was being silently overwritten at page load with a 200-country list (country names like "Indonesia") that didn't match the Hamlah nationality strings (adjective forms like "Indonesian"), which would have 400'd 9 of 10 nationalities the moment Hamlah membership became mandatory in Round 2. Fixed by constraining the dropdown to the exact 10 valid nationalities.

---

## How to keep this file current

This file is only as accurate as its last audit. **It does not update itself** — whenever the code changes, someone has to ask Claude to re-check it.

- **After finishing new work**: tell Claude *"update BACKLOG.md with what changed"* — it'll edit the relevant row(s)/section instead of creating a new file, then commit.
- **Before planning new work**: tell Claude *"check BACKLOG.md first"* — it'll read the current status before proposing anything, so you don't re-plan something already done or half-done.
- **Periodic re-audit** (recommended every few rounds, or whenever something feels off): tell Claude *"re-audit BACKLOG.md against the current code"* — it will re-verify every row against the actual code (not just trust the table) and correct anything stale.
- Either teammate can ask for any of the above — since this file lives in the repo, `git pull` before asking and `git push` (or let Claude push) after, so both laptops stay in sync.
