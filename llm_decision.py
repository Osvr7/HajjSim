"""Modular LLM decision layer for HajjSim pedestrian (pilgrim) agents.

This module is the *only* place that knows how to talk to a language model.
Everything else in the project (``hajj_agents.py``, ``app.py``) just calls
:func:`llm_decide_action` with a plain environment dictionary and a list of
valid actions, and gets one validated action string back.

Design goals
------------
1. **Modular / swappable.** A provider is a small class implementing
   :class:`BaseLLMProvider`. Gemini, OpenAI-compatible and Anthropic
   implementations ship here; :func:`register_provider` adds more without
   touching the simulation. Switching model = one environment variable.
2. **Zero hard dependencies.** All HTTP goes through ``urllib.request`` from
   the standard library, matching the rest of this project (a stdlib-only
   Python server + vanilla JS frontend).
3. **Never crashes the simulation.** Missing key, bad key, network error,
   timeout, malformed JSON, hallucinated action -- every failure path returns
   the caller's rule-based fallback action and records *why*.
4. **No secrets in source.** The API key is read from the ``LLM_API_KEY``
   environment variable only. It is never written to disk or into a log.
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Dict, Optional, Sequence


# ============================================================
# 0) .env loading
# ------------------------------------------------------------
# Putting the key in a ".env" file is what everyone expects to work, so the
# app loads it. Kept dependency-free (no python-dotenv) and deliberately
# non-overriding: a variable already exported in the real environment always
# wins, so a CI/production value is never silently replaced by a dev file.
# ============================================================

def load_env_file(path) -> int:
    """Load ``KEY=VALUE`` pairs from a .env file into ``os.environ``.

    Returns how many variables were set. Missing file, unreadable file, or a
    malformed line are all non-fatal -- configuration should never be the
    reason the simulation fails to start.
    """
    from pathlib import Path

    env_path = Path(path)
    if not env_path.is_file():
        return 0

    loaded = 0
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return 0

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        # "export FOO=bar" is a common shape in hand-written .env files.
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        name, _, value = line.partition("=")
        name = name.strip()
        value = value.strip()
        # Strip one matching pair of surrounding quotes, if present.
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if not name or name in os.environ:
            # Never override a variable the operator exported explicitly.
            continue
        os.environ[name] = value
        loaded += 1
    return loaded


# ============================================================
# 1) Configuration (environment variables only -- no hard-coded keys)
# ============================================================

def _env_flag(name: str, default: bool) -> bool:
    """Read a boolean-ish environment variable."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on", "enabled"}


def _env_int(name: str, default: int) -> int:
    """Read an integer environment variable, ignoring malformed values."""
    try:
        return int((os.environ.get(name) or "").strip())
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    """Read a float environment variable, ignoring malformed values."""
    try:
        return float((os.environ.get(name) or "").strip())
    except (TypeError, ValueError):
        return default


@dataclass
class LLMSettings:
    """All tunables for the LLM decision layer, read from the environment."""

    # --- credentials / model selection -------------------------------------
    api_key: str = ""
    provider: str = "gemini"
    model: str = "gemini-flash-lite-latest"
    base_url: str = ""

    # --- behavior ----------------------------------------------------------
    enabled: bool = True
    timeout_seconds: float = 12.0
    max_retries: int = 1
    temperature: float = 0.2
    max_output_tokens: int = 300

    # --- cost / volume control ---------------------------------------------
    # A full run is 240 ticks; with hundreds of pilgrims an unbounded
    # "one LLM call per agent per tick" policy would mean six-figure API
    # calls. These three knobs keep a run affordable and fast while still
    # giving genuinely dynamic, per-step LLM decisions to the agents that
    # matter. Set LLM_MAX_AGENTS=0 to drive the entire population.
    max_agents: int = 10
    max_calls_per_tick: int = 40
    cache_enabled: bool = True

    # --- circuit breaker ----------------------------------------------------
    # When a provider is definitively broken (bad key, wrong model, outage)
    # every agent every tick would otherwise pay full network latency for a
    # guaranteed failure, which is what makes a run appear to freeze. After
    # this many consecutive failures the engine stops calling out entirely and
    # serves the rule-based fallback instantly, retrying one probe call after
    # the cooldown. 0 disables the breaker.
    circuit_failure_threshold: int = 5
    circuit_cooldown_seconds: float = 60.0

    # --- rate limiting ------------------------------------------------------
    # Provider free tiers are measured in requests per MINUTE (Gemini's free
    # flash tier is single digits). One tick can easily ask for more than that,
    # so without pacing the run just collects 429s. When the minute's budget is
    # spent the engine serves the rule-based decision instantly instead of
    # making a call it knows will be rejected. 0 = unlimited.
    max_requests_per_minute: int = 0

    @classmethod
    def from_env(cls) -> "LLMSettings":
        """Build settings from environment variables (see README)."""
        provider = (os.environ.get("LLM_PROVIDER") or "gemini").strip().lower()
        default_models = {
            "gemini": "gemini-flash-lite-latest",
            "google": "gemini-flash-lite-latest",
            "openai": "gpt-4o-mini",
            "openai_compatible": "gpt-4o-mini",
            "anthropic": "claude-haiku-4-5-20251001",
            "claude": "claude-haiku-4-5-20251001",
            "echo": "echo-test",
        }
        # LLM_API_KEY is the documented name; GEMINI_API_KEY is accepted as a
        # fallback so the pre-existing narrative feature keeps working.
        api_key = (os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()
        return cls(
            api_key=api_key,
            provider=provider,
            model=(os.environ.get("LLM_MODEL") or default_models.get(provider, "")).strip(),
            base_url=(os.environ.get("LLM_BASE_URL") or "").strip(),
            enabled=_env_flag("LLM_ENABLED", True),
            timeout_seconds=_env_float("LLM_TIMEOUT_SECONDS", 12.0),
            max_retries=_env_int("LLM_MAX_RETRIES", 1),
            temperature=_env_float("LLM_TEMPERATURE", 0.2),
            max_output_tokens=_env_int("LLM_MAX_OUTPUT_TOKENS", 300),
            max_agents=_env_int("LLM_MAX_AGENTS", 10),
            max_calls_per_tick=_env_int("LLM_MAX_CALLS_PER_TICK", 40),
            cache_enabled=_env_flag("LLM_CACHE_ENABLED", True),
            circuit_failure_threshold=_env_int("LLM_CIRCUIT_FAILURE_THRESHOLD", 5),
            circuit_cooldown_seconds=_env_float("LLM_CIRCUIT_COOLDOWN_SECONDS", 60.0),
            max_requests_per_minute=_env_int("LLM_MAX_REQUESTS_PER_MINUTE", 0),
        )

    def is_configured(self) -> bool:
        """True when the layer has everything it needs to make a real call."""
        if not self.enabled:
            return False
        if self.provider == "echo":
            return True
        return bool(self.api_key)

    def to_status_payload(self) -> dict:
        """Describe the configuration for the dashboard, without the secret."""
        return {
            "enabled": self.enabled,
            "configured": self.is_configured(),
            "provider": self.provider,
            "model": self.model,
            "api_key_present": bool(self.api_key),
            "max_agents": self.max_agents,
            "max_calls_per_tick": self.max_calls_per_tick,
            "cache_enabled": self.cache_enabled,
            "timeout_seconds": self.timeout_seconds,
            "circuit_failure_threshold": self.circuit_failure_threshold,
            "circuit_cooldown_seconds": self.circuit_cooldown_seconds,
            "max_requests_per_minute": self.max_requests_per_minute,
        }


# ============================================================
# 2) Providers -- one small class per model vendor
# ============================================================

# HTTP statuses where trying again might genuinely work. Everything else is a
# permanent error (bad key, wrong model name, malformed request): retrying it
# just doubles the cost and the delay for a guaranteed second failure.
# NOTE: 429 is deliberately NOT here. A quota error will not clear in the
# fraction of a second an inline retry takes, and retrying spends another
# request against the very quota that is exhausted. Pacing is the RPM
# limiter's job instead.
RETRYABLE_HTTP_STATUSES = frozenset({408, 409, 425, 500, 502, 503, 504})


class LLMProviderError(RuntimeError):
    """Raised when a provider cannot return usable text.

    ``retryable`` tells the engine whether a second attempt is worth making.
    A 401 is not: the key will still be wrong a moment later.
    """

    def __init__(self, message: str, status_code: Optional[int] = None, retryable: bool = True):
        super().__init__(message)
        self.status_code = status_code
        self.retryable = retryable


class BaseLLMProvider:
    """Interface every model backend implements.

    To plug in a different model later, subclass this, implement
    :meth:`complete`, and call :func:`register_provider`. Nothing in the
    simulation code needs to change.
    """

    name = "base"

    def __init__(self, settings: LLMSettings):
        self.settings = settings

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Return the model's raw text response."""
        raise NotImplementedError

    def _post_json(self, url: str, payload: dict, headers: Dict[str, str]) -> dict:
        """POST a JSON body and decode the JSON response (stdlib only)."""
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=body, method="POST")
        request.add_header("Content-Type", "application/json")
        for header_name, header_value in headers.items():
            request.add_header(header_name, header_value)
        try:
            with urllib.request.urlopen(request, timeout=self.settings.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:400]
            raise LLMProviderError(
                f"HTTP {error.code} from {self.name}: {detail}",
                status_code=error.code,
                retryable=error.code in RETRYABLE_HTTP_STATUSES,
            ) from error
        except urllib.error.URLError as error:
            # Network blips and timeouts are exactly what retries are for.
            raise LLMProviderError(
                f"Network error calling {self.name}: {error.reason}", retryable=True
            ) from error
        except json.JSONDecodeError as error:
            raise LLMProviderError(
                f"{self.name} returned a non-JSON payload", retryable=False
            ) from error


class GeminiProvider(BaseLLMProvider):
    """Google Gemini via the Generative Language REST API."""

    name = "gemini"

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        base = self.settings.base_url or "https://generativelanguage.googleapis.com/v1beta"
        url = f"{base}/models/{self.settings.model}:generateContent"
        # Google's documented way to authenticate is the x-goog-api-key header,
        # and it is the ONLY thing that works for the current "auth key" format
        # (prefix "AQ.") that AI Studio now issues. The older "?key=" query
        # parameter is legacy, and sending an AQ. key as a bearer token is
        # rejected with 401 ACCESS_TOKEN_TYPE_UNSUPPORTED -- Google reads it as
        # an OAuth access token, which it is not.
        # Keeping the key out of the URL is also simply safer: query strings
        # end up in proxy logs and browser history, headers do not.
        headers: Dict[str, str] = {"x-goog-api-key": self.settings.api_key}

        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": self.settings.temperature,
                "maxOutputTokens": self.settings.max_output_tokens,
                "responseMimeType": "application/json",
            },
        }
        data = self._post_json(url, payload, headers)
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as error:
            raise LLMProviderError(f"Unexpected Gemini response shape: {str(data)[:300]}") from error


class OpenAICompatibleProvider(BaseLLMProvider):
    """OpenAI Chat Completions, and any API that mirrors that shape."""

    name = "openai"

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        base = self.settings.base_url or "https://api.openai.com/v1"
        payload = {
            "model": self.settings.model,
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_output_tokens,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {"Authorization": f"Bearer {self.settings.api_key}"}
        data = self._post_json(f"{base}/chat/completions", payload, headers)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise LLMProviderError(f"Unexpected OpenAI response shape: {str(data)[:300]}") from error


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude via the Messages API."""

    name = "anthropic"

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        base = self.settings.base_url or "https://api.anthropic.com"
        payload = {
            "model": self.settings.model,
            "max_tokens": self.settings.max_output_tokens,
            "temperature": self.settings.temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        headers = {
            "x-api-key": self.settings.api_key,
            "anthropic-version": "2023-06-01",
        }
        data = self._post_json(f"{base}/v1/messages", payload, headers)
        try:
            return data["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as error:
            raise LLMProviderError(f"Unexpected Anthropic response shape: {str(data)[:300]}") from error


class EchoProvider(BaseLLMProvider):
    """Offline stand-in used by tests and demos with no API key.

    It performs no network call. It picks a sensible action from the catalogue
    the environment supplied, which exercises every prompt-building, parsing,
    validation and logging path in this module without spending a token.
    """

    name = "echo"

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        try:
            observation = json.loads(user_prompt)
        except json.JSONDecodeError:
            return json.dumps({"action": "REST", "reason": "echo provider default"})
        actions = observation.get("available_actions") or []
        if not actions:
            return json.dumps({"action": "REST", "reason": "no actions offered"})
        risk_level = (observation.get("risk") or {}).get("level", "none")
        preferred_kinds = ("avoid", "rest") if risk_level in {"high", "severe"} else ("advance", "reroute")
        for kind in preferred_kinds:
            for candidate in actions:
                if candidate.get("kind") == kind:
                    return json.dumps({
                        "action": candidate["action"],
                        "reason": f"echo provider picked a '{kind}' action at risk level '{risk_level}'",
                    })
        return json.dumps({
            "action": actions[0]["action"],
            "reason": "echo provider fell back to the first offered action",
        })


# Registry so a new model backend can be added without editing the engine.
PROVIDERS: Dict[str, type] = {
    "gemini": GeminiProvider,
    "google": GeminiProvider,
    "openai": OpenAICompatibleProvider,
    "openai_compatible": OpenAICompatibleProvider,
    "anthropic": AnthropicProvider,
    "claude": AnthropicProvider,
    "echo": EchoProvider,
}


def register_provider(name: str, provider_class: type) -> None:
    """Register a custom provider class under ``name`` (selected by LLM_PROVIDER)."""
    PROVIDERS[name.strip().lower()] = provider_class


def build_provider(settings: LLMSettings) -> Optional[BaseLLMProvider]:
    """Instantiate the provider named by the settings, or None if unknown."""
    provider_class = PROVIDERS.get(settings.provider)
    if provider_class is None:
        return None
    return provider_class(settings)


# ============================================================
# 3) Environment -> prompt conversion
# ============================================================

SYSTEM_PROMPT = (
    "You are the decision-making brain of ONE pedestrian agent (a pilgrim) inside a Hajj "
    "crowd-simulation digital twin. Each simulation step you receive a JSON snapshot of what "
    "this pilgrim can currently observe, plus the exact list of actions the simulation engine "
    "is able to execute for it right now.\n"
    "\n"
    "Your job: analyse the situation and choose the SINGLE best action.\n"
    "\n"
    "Weigh these factors, roughly in this order:\n"
    "1. Immediate physical safety -- panic, stampede risk, crowd bottlenecks, extreme heat.\n"
    "2. The pilgrim's own vitals -- stress, fatigue, hydration -- and their vulnerability "
    "(age, health status, chronic conditions, mobility).\n"
    "3. Congestion and hazards on the current node versus the candidate destinations.\n"
    "4. Progress toward the current ritual obligation, which is time-boxed: falling behind "
    "the ritual window has a real cost, so do not stall without a safety reason.\n"
    "5. Distance (hops) and accessibility -- some destinations need a bus and will queue.\n"
    "6. The pilgrim's recent actions -- avoid oscillating between two nodes, and avoid "
    "changing route repeatedly when nothing in the environment has changed.\n"
    "\n"
    "HARD RULES:\n"
    "- You MUST choose one action whose value appears exactly in available_actions[].action.\n"
    "- Never invent an action, never modify the spelling, never return more than one.\n"
    "- Respond with ONLY a JSON object, no prose and no code fences:\n"
    '  {"action": "<exact action string>", "reason": "<one short sentence>"}'
)


def build_decision_prompt(environment_state: dict, available_actions: Sequence[dict]) -> Dict[str, str]:
    """Convert a raw environment snapshot into the system/user prompt pair.

    ``environment_state`` is the observation dict built by
    :meth:`hajj_agents.PilgrimAgent.build_observation`; ``available_actions``
    is the catalogue from :meth:`hajj_agents.PilgrimAgent.available_actions`.
    Both are plain JSON-safe structures, which keeps this function reusable
    for any other simulation that can describe itself the same way.
    """
    observation = dict(environment_state)
    observation["available_actions"] = list(available_actions)
    observation["response_format"] = {"action": "<one value from available_actions[].action>", "reason": "<why>"}
    user_prompt = json.dumps(observation, ensure_ascii=False, indent=1, default=str)
    return {"system": SYSTEM_PROMPT, "user": user_prompt}


# ============================================================
# 4) Response parsing and action validation
# ============================================================

_JSON_OBJECT_PATTERN = re.compile(r"\{.*\}", re.DOTALL)


@dataclass
class ParsedDecision:
    """Result of parsing + validating one raw model response."""

    action: Optional[str] = None
    reason: str = ""
    error: str = ""


def parse_llm_decision(raw_text: str, valid_actions: Sequence[str]) -> ParsedDecision:
    """Extract and validate the ``action`` field from a raw model response.

    Tolerates the three things models actually do wrong in practice: wrapping
    JSON in ``` fences, adding a sentence before the JSON, and returning the
    bare action string with no JSON at all. Anything that still does not
    resolve to a member of ``valid_actions`` is reported as an error so the
    caller can fall back.
    """
    valid_set = set(valid_actions)
    if not raw_text or not raw_text.strip():
        return ParsedDecision(error="empty response from model")

    text = raw_text.strip()
    # Strip ``` / ```json fences before looking for the object.
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()

    payload = None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        match = _JSON_OBJECT_PATTERN.search(text)
        if match:
            try:
                payload = json.loads(match.group(0))
            except json.JSONDecodeError:
                payload = None

    if isinstance(payload, dict):
        action = payload.get("action")
        reason = str(payload.get("reason") or "").strip()
        if not isinstance(action, str) or not action.strip():
            return ParsedDecision(error=f"response JSON has no usable 'action' field: {text[:160]}")
        action = action.strip()
        if action in valid_set:
            return ParsedDecision(action=action, reason=reason)
        # One forgiving pass for case/whitespace drift before rejecting.
        for candidate in valid_set:
            if candidate.lower() == action.lower():
                return ParsedDecision(action=candidate, reason=reason)
        return ParsedDecision(error=f"model returned an action outside the allowed set: {action!r}")

    # No JSON at all -- accept a bare, exactly-matching action string.
    bare = text.strip().strip('"').strip()
    if bare in valid_set:
        return ParsedDecision(action=bare, reason="model returned a bare action string")
    return ParsedDecision(error=f"could not parse a decision from response: {text[:160]}")


# ============================================================
# 5) Decision engine (budget, cache, retries, fallback, stats)
# ============================================================

@dataclass
class LLMDecision:
    """One decision, however it was reached, with full provenance for logging."""

    action: str
    reason: str = ""
    # llm | cache | fallback_error | fallback_invalid | fallback_budget | disabled
    source: str = "fallback_error"
    fallback_action: str = ""
    error: str = ""
    latency_ms: int = 0
    provider: str = ""
    model: str = ""
    cached: bool = False
    raw_response: str = ""

    @property
    def used_llm(self) -> bool:
        """True when the executed action actually came from the model."""
        return self.source in {"llm", "cache"}

    def to_payload(self) -> dict:
        """JSON-safe form used by the API, the decision log and the report."""
        return {
            "action": self.action,
            "reason": self.reason,
            "source": self.source,
            "fallback_action": self.fallback_action,
            "error": self.error,
            "latency_ms": self.latency_ms,
            "provider": self.provider,
            "model": self.model,
            "cached": self.cached,
        }


class LLMDecisionEngine:
    """Owns the provider, the per-tick call budget, the cache and the stats.

    Thread-safe: the dashboard runs on a ``ThreadingHTTPServer``, so several
    requests can touch the engine at once.
    """

    def __init__(self, settings: Optional[LLMSettings] = None):
        self.settings = settings or LLMSettings.from_env()
        self.provider = build_provider(self.settings)
        self._lock = threading.Lock()
        self._cache: Dict[str, ParsedDecision] = {}
        self._calls_this_tick = 0
        self._current_tick = -1
        # Circuit breaker state: consecutive failures, and the timestamp the
        # circuit may next be probed.
        self._consecutive_failures = 0
        self._circuit_open_until = 0.0
        # Timestamps of calls made in the last 60s, for the RPM limiter.
        self._recent_call_times: list = []
        self.stats: Dict[str, int] = {
            "calls_attempted": 0,
            "calls_succeeded": 0,
            "calls_failed": 0,
            "cache_hits": 0,
            "budget_skips": 0,
            "invalid_responses": 0,
            "circuit_trips": 0,
            "circuit_skips": 0,
            "rate_limit_skips": 0,
            "total_latency_ms": 0,
            "decisions_total": 0,
            "decisions_from_llm": 0,
            "decisions_from_fallback": 0,
        }
        self.last_error: str = ""

    # -- lifecycle ----------------------------------------------------------
    def begin_tick(self, tick: int) -> None:
        """Reset the per-tick call budget at the start of a simulation step."""
        with self._lock:
            self._current_tick = tick
            self._calls_this_tick = 0

    def reset(self) -> None:
        """Clear cache and counters (used by the dashboard reset endpoints)."""
        with self._lock:
            self._cache.clear()
            self._calls_this_tick = 0
            self._current_tick = -1
            self._consecutive_failures = 0
            self._circuit_open_until = 0.0
            self._recent_call_times.clear()
            for key in self.stats:
                self.stats[key] = 0
            self.last_error = ""

    def reload_settings(self) -> None:
        """Re-read the environment so a key can be supplied without a restart."""
        with self._lock:
            self.settings = LLMSettings.from_env()
            self.provider = build_provider(self.settings)
            self._cache.clear()
            # A reload usually means the operator just fixed the key, so give
            # the new configuration a clean circuit.
            self._consecutive_failures = 0
            self._circuit_open_until = 0.0

    @property
    def is_active(self) -> bool:
        """True when a real (or echo) provider is ready to be called."""
        return self.settings.is_configured() and self.provider is not None

    def status_payload(self) -> dict:
        """Configuration + live counters for the dashboard status endpoint."""
        with self._lock:
            stats = dict(self.stats)
            circuit_retry_in = max(0.0, self._circuit_open_until - time.monotonic())
            cutoff = time.monotonic() - 60.0
            requests_last_minute = len([t for t in self._recent_call_times if t > cutoff])
        circuit_open = circuit_retry_in > 0
        succeeded = max(1, stats["calls_succeeded"])
        return {
            **self.settings.to_status_payload(),
            "provider_ready": self.provider is not None,
            "active": self.is_active,
            "stats": stats,
            "avg_latency_ms": round(stats["total_latency_ms"] / succeeded, 1) if stats["calls_succeeded"] else 0.0,
            "last_error": self.last_error,
            "circuit_open": circuit_open,
            "circuit_retry_in_seconds": round(circuit_retry_in, 1),
            "requests_last_minute": requests_last_minute,
        }

    # -- the main entry point ----------------------------------------------
    def decide(
        self,
        environment_state: dict,
        available_actions: Sequence[dict],
        fallback_action: str = "",
    ) -> LLMDecision:
        """Choose one action for the current step; never raises.

        Order of resolution: disabled -> no valid actions -> cache -> budget ->
        live model call (with retries) -> validation -> fallback.
        """
        action_values = [entry["action"] for entry in available_actions if entry.get("action")]
        safe_fallback = fallback_action if fallback_action in action_values else (
            action_values[0] if action_values else fallback_action
        )

        def _record(decision: LLMDecision) -> LLMDecision:
            with self._lock:
                self.stats["decisions_total"] += 1
                if decision.used_llm:
                    self.stats["decisions_from_llm"] += 1
                else:
                    self.stats["decisions_from_fallback"] += 1
            return decision

        if not self.is_active:
            return _record(LLMDecision(
                action=safe_fallback,
                reason="LLM layer is disabled or not configured; used the rule-based decision.",
                source="disabled",
                fallback_action=safe_fallback,
                provider=self.settings.provider,
                model=self.settings.model,
            ))

        if not action_values:
            return _record(LLMDecision(
                action=safe_fallback,
                reason="The simulation offered no selectable actions this step.",
                source="fallback_invalid",
                fallback_action=safe_fallback,
                error="empty available_actions",
                provider=self.settings.provider,
                model=self.settings.model,
            ))

        cache_key = self._cache_key(environment_state, action_values)
        if self.settings.cache_enabled and cache_key:
            with self._lock:
                cached = self._cache.get(cache_key)
            if cached and cached.action in action_values:
                with self._lock:
                    self.stats["cache_hits"] += 1
                return _record(LLMDecision(
                    action=cached.action,
                    reason=cached.reason,
                    source="cache",
                    fallback_action=safe_fallback,
                    provider=self.settings.provider,
                    model=self.settings.model,
                    cached=True,
                ))

        # Circuit breaker: if the provider has failed repeatedly, do not pay
        # network latency for a call that is almost certainly going to fail
        # again. This is what keeps a run moving at full speed when the key is
        # wrong, instead of every tick stalling on timeouts.
        with self._lock:
            circuit_open = self._circuit_open_until > time.monotonic()
            opens_in = max(0.0, self._circuit_open_until - time.monotonic())
            if circuit_open:
                self.stats["circuit_skips"] += 1
        if circuit_open:
            return _record(LLMDecision(
                action=safe_fallback,
                reason=(
                    "LLM calls are paused after repeated failures; using the rule-based decision. "
                    f"Retrying in {opens_in:.0f}s."
                ),
                source="fallback_circuit_open",
                fallback_action=safe_fallback,
                error=self.last_error,
                provider=self.settings.provider,
                model=self.settings.model,
            ))

        # Per-minute budget: provider free tiers are measured in requests per
        # minute, and one tick can ask for more than a whole minute's worth.
        # Spending the call anyway just collects a 429.
        if self.settings.max_requests_per_minute > 0:
            now = time.monotonic()
            with self._lock:
                cutoff = now - 60.0
                self._recent_call_times = [t for t in self._recent_call_times if t > cutoff]
                rate_limited = len(self._recent_call_times) >= self.settings.max_requests_per_minute
                if rate_limited:
                    self.stats["rate_limit_skips"] += 1
                    wait_for = max(0.0, 60.0 - (now - self._recent_call_times[0]))
            if rate_limited:
                return _record(LLMDecision(
                    action=safe_fallback,
                    reason=(
                        f"Per-minute LLM request budget "
                        f"({self.settings.max_requests_per_minute}/min) is spent; used the rule-based "
                        f"decision. Budget frees up in {wait_for:.0f}s."
                    ),
                    source="fallback_rate_limit",
                    fallback_action=safe_fallback,
                    provider=self.settings.provider,
                    model=self.settings.model,
                ))

        # Per-tick budget: protects a long run from an unbounded API bill.
        with self._lock:
            if self.settings.max_calls_per_tick > 0 and self._calls_this_tick >= self.settings.max_calls_per_tick:
                self.stats["budget_skips"] += 1
                over_budget = True
            else:
                self._calls_this_tick += 1
                over_budget = False
        if over_budget:
            return _record(LLMDecision(
                action=safe_fallback,
                reason="Per-tick LLM call budget reached; used the rule-based decision.",
                source="fallback_budget",
                fallback_action=safe_fallback,
                provider=self.settings.provider,
                model=self.settings.model,
            ))

        if self.settings.max_requests_per_minute > 0:
            with self._lock:
                self._recent_call_times.append(time.monotonic())

        prompts = build_decision_prompt(environment_state, available_actions)
        raw_text = ""
        error_text = ""
        started = time.perf_counter()
        for attempt in range(max(1, self.settings.max_retries + 1)):
            with self._lock:
                self.stats["calls_attempted"] += 1
            retryable = True
            try:
                raw_text = self.provider.complete(prompts["system"], prompts["user"])
                error_text = ""
                break
            except LLMProviderError as error:
                error_text = str(error)
                retryable = error.retryable
            except Exception as error:  # noqa: BLE001 -- the simulation must continue regardless
                error_text = f"unexpected {type(error).__name__}: {error}"
                retryable = False
            with self._lock:
                self.stats["calls_failed"] += 1
            # A bad key or a wrong model name will fail identically on the
            # second attempt, so do not pay for it (or for the backoff sleep).
            if not retryable:
                break
            if attempt < self.settings.max_retries:
                time.sleep(0.4 * (attempt + 1))
        latency_ms = int((time.perf_counter() - started) * 1000)

        if error_text:
            self.last_error = error_text
            tripped = self._register_failure()
            if tripped:
                print(
                    f"LLM circuit breaker OPEN after {self.settings.circuit_failure_threshold} consecutive "
                    f"failures -- pausing calls for {self.settings.circuit_cooldown_seconds:.0f}s. "
                    f"Last error: {error_text[:200]}"
                )
            return _record(LLMDecision(
                action=safe_fallback,
                reason="LLM call failed; used the rule-based safety decision instead.",
                source="fallback_error",
                fallback_action=safe_fallback,
                error=error_text,
                latency_ms=latency_ms,
                provider=self.settings.provider,
                model=self.settings.model,
            ))

        with self._lock:
            self.stats["calls_succeeded"] += 1
            self.stats["total_latency_ms"] += latency_ms
            # A good call clears the breaker entirely.
            self._consecutive_failures = 0
            self._circuit_open_until = 0.0

        parsed = parse_llm_decision(raw_text, action_values)
        if parsed.action is None:
            with self._lock:
                self.stats["invalid_responses"] += 1
            self.last_error = parsed.error
            return _record(LLMDecision(
                action=safe_fallback,
                reason="LLM returned an unusable or out-of-set action; used the rule-based decision.",
                source="fallback_invalid",
                fallback_action=safe_fallback,
                error=parsed.error,
                latency_ms=latency_ms,
                provider=self.settings.provider,
                model=self.settings.model,
                raw_response=raw_text[:500],
            ))

        if self.settings.cache_enabled and cache_key:
            with self._lock:
                # Bound the cache so a long run cannot grow it without limit.
                if len(self._cache) > 4000:
                    self._cache.clear()
                self._cache[cache_key] = parsed

        return _record(LLMDecision(
            action=parsed.action,
            reason=parsed.reason,
            source="llm",
            fallback_action=safe_fallback,
            latency_ms=latency_ms,
            provider=self.settings.provider,
            model=self.settings.model,
            raw_response=raw_text[:500],
        ))

    def _register_failure(self) -> bool:
        """Count a failure and open the circuit once the threshold is crossed.

        Returns True only on the transition into the open state, so the caller
        logs it once rather than on every subsequent failure.
        """
        threshold = self.settings.circuit_failure_threshold
        if threshold <= 0:
            return False
        with self._lock:
            self._consecutive_failures += 1
            if self._consecutive_failures >= threshold and self._circuit_open_until <= time.monotonic():
                self._circuit_open_until = time.monotonic() + self.settings.circuit_cooldown_seconds
                self._consecutive_failures = 0
                self.stats["circuit_trips"] += 1
                return True
        return False

    @staticmethod
    def _cache_key(environment_state: dict, action_values: Sequence[str]) -> str:
        """Build a coarse signature so identical situations reuse one answer.

        Deliberately lossy: vitals are bucketed into tens and only the fields
        that actually change a decision are included. Two pilgrims standing in
        the same place, in the same risk band, with the same option set get one
        API call between them instead of two.
        """
        location = environment_state.get("location") or {}
        risk = environment_state.get("risk") or {}
        vitals = environment_state.get("vitals") or {}
        ritual = environment_state.get("ritual") or {}
        try:
            parts = [
                str(location.get("current_node")),
                str(location.get("zone")),
                str(ritual.get("target_node")),
                str(ritual.get("window_open")),
                str(risk.get("level")),
                str(environment_state.get("conditions", {}).get("hazard")),
                str(int(float(vitals.get("stress", 0)) // 10)),
                str(int(float(vitals.get("fatigue", 0)) // 10)),
                str(int(float(vitals.get("hydration", 100)) // 10)),
                "|".join(sorted(action_values)),
            ]
        except (TypeError, ValueError):
            return ""
        return "~".join(parts)


# ============================================================
# 6) Module-level convenience API
# ============================================================

# A single shared engine is what the simulation uses by default. Tests and
# alternative front-ends can build their own LLMDecisionEngine instead.
_DEFAULT_ENGINE: Optional[LLMDecisionEngine] = None
_DEFAULT_ENGINE_LOCK = threading.Lock()


def get_default_engine() -> LLMDecisionEngine:
    """Return (creating on first use) the process-wide decision engine."""
    global _DEFAULT_ENGINE
    with _DEFAULT_ENGINE_LOCK:
        if _DEFAULT_ENGINE is None:
            _DEFAULT_ENGINE = LLMDecisionEngine()
        return _DEFAULT_ENGINE


def set_default_engine(engine: LLMDecisionEngine) -> None:
    """Replace the shared engine (used to swap in a different model/provider)."""
    global _DEFAULT_ENGINE
    with _DEFAULT_ENGINE_LOCK:
        _DEFAULT_ENGINE = engine


def llm_decide_action(
    environment_state: dict,
    available_actions: Sequence[dict],
    fallback_action: str = "",
    engine: Optional[LLMDecisionEngine] = None,
) -> LLMDecision:
    """Choose one valid action for the current environment state.

    This is the function the simulation calls. It:
      1. receives the current environment state,
      2. receives the valid available actions,
      3. builds a structured prompt,
      4. asks the LLM to analyse the environment,
      5. returns exactly one action,
      6. validates that action against ``available_actions``,
      7. falls back to ``fallback_action`` (the rule-based decision) on any
         API failure or invalid response, so the simulation always continues.

    Returns an :class:`LLMDecision` -- use ``.action`` for the action string
    and ``.reason`` / ``.source`` for logging and the analytical report.
    """
    return (engine or get_default_engine()).decide(
        environment_state=environment_state,
        available_actions=available_actions,
        fallback_action=fallback_action,
    )
