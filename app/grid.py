"""Live German grid data from Energy-Charts (Fraunhofer ISE). Public API, no key needed."""

import json
import time
import urllib.request
from datetime import UTC, datetime

SOURCE_URL = "https://api.energy-charts.info/public_power?country=de"
CACHE_SECONDS = 300  # Energy-Charts updates every 15 minutes, so 5 minutes is fresh enough.

# Energy-Charts names -> the groups we show. Anything not listed counts as "Other".
GROUPS = {
    "Solar": "Solar",
    "Wind onshore": "Wind",
    "Wind offshore": "Wind",
    "Fossil gas": "Gas",
    "Fossil brown coal / lignite": "Coal",
    "Fossil hard coal": "Coal",
    "Fossil coal-derived gas": "Coal",
    "Biomass": "Biomass",
    "Hydro Run-of-River": "Hydro",
    "Hydro water reservoir": "Hydro",
    "Hydro pumped storage": "Hydro",
}
# Not generation: these are totals, shares, or power flowing out of Germany.
SKIP = {
    "Load",
    "Residual load",
    "Renewable share of load",
    "Renewable share of generation",
    "Cross border electricity trading",
    "Hydro pumped storage consumption",
}

_cache: dict = {"at": 0.0, "value": None}


def fetch_public_power() -> dict:
    with urllib.request.urlopen(SOURCE_URL, timeout=10) as res:
        return json.load(res)


def _latest(values: list) -> float | None:
    # The newest slots can still be empty, so take the last real number.
    for v in reversed(values):
        if v is not None:
            return v
    return None


def summarize(raw: dict) -> dict:
    by_name = {p["name"]: p["data"] for p in raw["production_types"]}
    sources: dict[str, float] = {}
    for name, data in by_name.items():
        if name in SKIP:
            continue
        mw = _latest(data)
        if mw is None or mw <= 0:
            continue
        group = GROUPS.get(name, "Other")
        sources[group] = sources.get(group, 0.0) + mw

    # Label with the newest slot that actually has a demand figure, not just the newest slot.
    load = by_name.get("Load", [])
    filled = [i for i, v in enumerate(load) if v is not None]
    stamp = raw["unix_seconds"][filled[-1] if filled else -1]

    return {
        "time": datetime.fromtimestamp(stamp, UTC).isoformat(),
        "renewable_share": _latest(by_name.get("Renewable share of generation", [])),
        "load_mw": _latest(by_name.get("Load", [])),
        "sources_mw": dict(sorted(((k, round(v, 1)) for k, v in sources.items()), key=lambda kv: -kv[1])),
    }


def current_grid() -> dict:
    now = time.monotonic()
    if _cache["value"] is None or now - _cache["at"] > CACHE_SECONDS:
        _cache["value"] = summarize(fetch_public_power())
        _cache["at"] = now
    return _cache["value"]
