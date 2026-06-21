# -*- coding: utf-8 -*-
"""screening MCP server (mock) — sanctions / PEP screening (read-only).

Stands in for the `screening` MCP (env var SCREENING_MCP_URL) used by:
  - kyc-screener : screen onboarding names against sanctions & PEP watchlists and
                   classify each hit (confirmed vs false positive vs PEP).

Serves fake data from ./data/*.csv. Mock / dev only. Read-only.

The screen_name tool does identifier-aware matching: a name match alone is a
POTENTIAL hit; it is only CONFIRMED when DOB and country also line up. A name match
with a different DOB/country is a likely false positive (must be cleared, not
auto-rejected). PEP matches route to EDD, never auto-reject.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

from mcp.server.fastmcp import FastMCP

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
DEFAULT_PORT = 8006


def _to_num(v):
    if v is None:
        return None
    s = str(v).strip()
    if s == "" or s.lower() == "n/a":
        return s
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        return s


def _raw(fname):
    with open(os.path.join(DATA, fname), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _typed(rows):
    return [{k: _to_num(v) for k, v in r.items()} for r in rows]


def _norm(s):
    return str(s or "").strip().lower()


def _name_match(query, target):
    q, t = _norm(query), _norm(target)
    if not q or not t:
        return False
    return q == t or q in t or t in q


mcp = FastMCP("screening", host="127.0.0.1", port=DEFAULT_PORT)


@mcp.tool()
def screen_name(name: str, dob: str = "", country: str = "") -> dict:
    """Screen a name against the sanctions & PEP lists with identifier-aware matching.

    Provide `dob` (YYYY-MM-DD) and `country` when known so a name hit can be confirmed
    or cleared. Returns one entry per candidate with a classification:
      - confirmed_sanctions_match : name + DOB + country all align → action R4 (reject/escalate)
      - potential_sanctions_match : name aligns but DOB/country not supplied → needs identifiers
      - likely_false_positive     : name aligns but DOB or country differ → clear, do NOT reject
      - pep_match                 : politically exposed person → action R5 (EDD, not auto-reject)
    """
    matches = []

    for r in _raw("sanctions.csv"):
        if not _name_match(name, r["name"]):
            continue
        same_dob = bool(dob) and _norm(dob) == _norm(r["dob"])
        same_ctry = bool(country) and _norm(country) == _norm(r["country"])
        if dob and country:
            if same_dob and same_ctry:
                cls, reason, action = ("confirmed_sanctions_match",
                                       "name + DOB + country all match",
                                       "R4: reject / escalate to MLRO")
            else:
                diffs = []
                if not same_dob:
                    diffs.append(f"DOB {dob} vs {r['dob']}")
                if not same_ctry:
                    diffs.append(f"country {country} vs {r['country']}")
                cls, reason, action = ("likely_false_positive",
                                       "name matches but identifiers differ: " + "; ".join(diffs),
                                       "clear after review; do NOT auto-reject")
        else:
            cls, reason, action = ("potential_sanctions_match",
                                   "name matches; supply DOB + country to confirm or clear",
                                   "request identifiers")
        matches.append({"list": "sanctions", "list_id": r["list_id"], "name": r["name"],
                        "dob": r["dob"], "country": r["country"], "program": r["program"],
                        "classification": cls, "reason": reason, "action": action})

    for r in _raw("pep.csv"):
        if not _name_match(name, r["name"]):
            continue
        matches.append({"list": "pep", "list_id": r["list_id"], "name": r["name"],
                        "position": r["position"], "country": r["country"], "type": r["type"],
                        "classification": "pep_match",
                        "reason": "politically exposed person",
                        "action": "R5: enhanced due diligence (EDD); not an auto-reject"})

    confirmed = any(m["classification"] == "confirmed_sanctions_match" for m in matches)
    pep = any(m["classification"] == "pep_match" for m in matches)
    if confirmed:
        overall = "HIT_SANCTIONS"
    elif pep:
        overall = "HIT_PEP"
    elif matches:
        overall = "REVIEW"
    else:
        overall = "CLEAR"
    return {"query": {"name": name, "dob": dob, "country": country},
            "overall": overall, "match_count": len(matches), "matches": matches}


@mcp.tool()
def get_sanctions_list() -> list:
    """Return the full sanctions watchlist (OFAC/UN/EU style)."""
    return _typed(_raw("sanctions.csv"))


@mcp.tool()
def get_pep_list() -> list:
    """Return the full politically-exposed-persons (PEP) watchlist."""
    return _typed(_raw("pep.csv"))


def main():
    ap = argparse.ArgumentParser(description="screening mock MCP server")
    ap.add_argument("--http", action="store_true", help="serve over streamable-http instead of stdio")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()
    if args.http:
        mcp.settings.host = "127.0.0.1"
        mcp.settings.port = args.port
        print(f"screening MCP on http://127.0.0.1:{args.port}/mcp", file=sys.stderr)
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
