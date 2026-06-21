# -*- coding: utf-8 -*-
"""nav MCP server (mock) — fund NAV pack (read-only, source of truth).

Stands in for the `nav` MCP (env var NAV_MCP_URL) used by:
  - statement-auditor : the authoritative NAV pack (fund NAV build + per-LP capital
                        accounts) that draft LP statements are checked against.

Serves fake data from ./data/*.csv. Mock / dev only. Read-only.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

from mcp.server.fastmcp import FastMCP

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
DEFAULT_PORT = 8004


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


def _eq(row, field, value):
    return str(row.get(field, "")).strip().lower() == str(value).strip().lower()


mcp = FastMCP("nav", host="127.0.0.1", port=DEFAULT_PORT)


@mcp.tool()
def list_funds() -> dict:
    """List funds and as-of dates available in the NAV pack."""
    rows = _raw("nav_build.csv")
    return {"funds": sorted({r["fund"] for r in rows}),
            "as_of": sorted({r["as_of"] for r in rows})}


@mcp.tool()
def get_nav_build(fund: str, as_of: str) -> dict:
    """Return the authoritative fund-level NAV build (assets − liabilities = NAV).

    This is the source of truth — draft LP statements get checked against it.
    `as_of` is a quarter-end ISO date, e.g. "2026-03-31".
    """
    rows = [r for r in _raw("nav_build.csv") if _eq(r, "fund", fund) and _eq(r, "as_of", as_of)]
    return {"fund": fund, "as_of": as_of, "currency": "USD", "lines": _typed(rows)}


@mcp.tool()
def get_lp_capital_accounts(fund: str, as_of: str, lp_id: str = "") -> dict:
    """Return per-LP capital accounts (the correct figures to audit statements against).

    Each row: beginning + contributions − distributions + net_gain_loss − mgmt_fee =
    ending. Optionally filter to one `lp_id` (e.g. "LP-001"). Also returns column totals
    so the auditor can tie the roll-up to NAV.
    """
    rows = [r for r in _raw("lp_capital_accounts.csv") if _eq(r, "fund", fund) and _eq(r, "as_of", as_of)]
    if lp_id:
        rows = [r for r in rows if _eq(r, "lp_id", lp_id)]
    typed = _typed(rows)
    cols = ["beginning", "contributions", "distributions", "net_gain_loss", "mgmt_fee", "ending"]
    totals = {c: round(sum((r.get(c) or 0) for r in typed), 2) for c in cols}
    return {"fund": fund, "as_of": as_of, "currency": "USD",
            "accounts": typed, "totals": totals}


def main():
    ap = argparse.ArgumentParser(description="nav mock MCP server")
    ap.add_argument("--http", action="store_true", help="serve over streamable-http instead of stdio")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()
    if args.http:
        mcp.settings.host = "127.0.0.1"
        mcp.settings.port = args.port
        print(f"nav MCP on http://127.0.0.1:{args.port}/mcp", file=sys.stderr)
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
