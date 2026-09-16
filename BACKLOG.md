# MANSAK / HajjSim — Feature Backlog (Single Source of Truth)

_Last verified against the codebase: 2026-09-15._

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

## 4. Official course "Future Plan" roadmap (`Documents/HajjSim_Agent_Studio_Presentation.pdf`, slide 8)

This slide is the team's own stated next-stage roadmap — distinct from, and mostly not covered by, Rounds 1-2 above.

| # | Feature (as promised on the slide) | Status | Evidence | Notes |
|---|---|---|---|---|
| 4.1 | **Leader Agents** — guide groups, keep members together, share instructions | 🟡 Partial (data only) | `Memory.social.leader_id` is assigned per group (`_link_social_groups`) | Write-only: `leader_id` is never read anywhere to influence movement/decisions. No agent actually "leads" — it's an unused label. |
| 4.2 | **Transportation Agents** — buses, shuttles, delays, movement between sites | ✅ Done | Round 2 §3.4-3.7 | Fully delivered by Round 2's convoy system. |
| 4.3 | **Housing Agents** — camps, hotels, room flow, accommodation pressure | ✅ Done | Round 2 §3.2 | Fully delivered by Round 2's Hotel system. |
| 4.4 | **Agent Communication** — share warnings, route updates, help requests | ⬜ Not started | `Memory.social.help_contacts` exists but is a static seeded list (`["Medical_Desk_1"]`), never dynamically updated; no message-passing between agents anywhere | Real gap: no agent ever sends/receives anything from another agent. |
| 4.5 | **Next Stage** — more agents, larger populations, smarter prediction | 🟡 Partial | 500-agent cap per `/api/agents/random` call (§1.6); "smarter prediction" partly addressed by Round 2's LLM narrative (§3.10) | No load-testing done at scale; "smarter prediction" is the Gemini narrative at best, not a forecasting model. |

## 5. MiroFish-inspired adoption ideas (proposed, not requested as a formal round)

| # | Idea | Status | Evidence | Notes |
|---|---|---|---|---|
| 5.1 | Wire up the `llm_override` hook for LLM-driven pilgrim decisions | ⬜ Not started | `BehaviorEngine.llm_override`/`_apply_llm_override()` fully plumbed through every constructor, but `app.py` never passes a real callable | The hook is real and ready to receive a function; nothing calls it. |
| 5.2 | Upgrade plain BFS `ROUTE_GRAPH` to real GraphRAG retrieval | ⬜ Not started | `plan_route()` is textbook BFS over a static adjacency dict | No embeddings, no retrieval, no knowledge graph — despite "digital twin" framing implying more. |
| 5.3 | Richer hazard-informed memory (past hazards shape future routing) | 🟡 Partial (write-only) | `Memory.long_term.known_hazards[node] = hazard` is written on perceive (`hajj_agents.py`) but never read back anywhere to avoid a hazardous node or bias a route choice | Same write-only pattern as `leader_id` (§4.1) — data capture without behavioral use. |
| 5.4 | ReportAgent-style automated narrative report | ✅ Done | Round 2 §3.10 (`generate_narrative_via_llm`/`_template_narrative`) | This is the one MiroFish idea Round 2 actually delivered. |
| 5.5 | Deep/interactive drill-in on one pilgrim's *reasoning* | 🟡 Partial | `openPilgrimDetailSidebar()` shows full profile/state/memory snapshot | Shows *what* the agent's state is, not *why* it chose its last action — decisions are rule-based with no explanation trace to surface. |
| 5.6 | Keep the simulation core open/auditable (B2G trust) | ✅ Done (by construction) | Entire stack is a stdlib Python server + vanilla JS, no closed-source dependency, no external calls unless `GEMINI_API_KEY` is deliberately set | Not a coded "feature" so much as an architectural property that already holds. |

## 6. Cross-cutting gaps and debt found during the last audit

- **README is stale on tick semantics** (§1.2) — still describes "1 tick = 1 ritual stage," true only before Round 1.
- **No aggregate Hamlah view** (§2.2) — `declared_pilgrim_count` vs `actual_pilgrim_count` is modeled but invisible to an operator.
- **Two write-only memory fields** (`leader_id` §4.1, `known_hazards` §5.3) — data is captured every tick but never read back into any decision, making two "planned" features look implemented in the data model while doing nothing behaviorally. `learned_preferences` is similarly written in `_seed_memory` but not obviously read elsewhere — not yet fully audited.
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
