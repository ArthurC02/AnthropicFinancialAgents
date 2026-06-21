# -*- coding: utf-8 -*-
"""portfolio MCP server (mock) — PE portfolio data source (read-only).

Stands in for the `portfolio` MCP (env var PORTFOLIO_MCP_URL) used by:
  - valuation-reviewer : pull GP-reported marks to review against the valuation
                         policy, fund NAV build, capital flows (for IRR/MOIC), and
                         waterfall terms (for carry / LP allocation).

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
DEFAULT_PORT = 8003


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


mcp = FastMCP("portfolio", host="127.0.0.1", port=DEFAULT_PORT)


@mcp.tool()
def list_funds() -> dict:
    """List funds and as-of dates available in this portfolio source."""
    rows = _raw("gp_valuation_package.csv")
    return {
        "funds": sorted({r["fund"] for r in rows}),
        "as_of": sorted({r["as_of"] for r in rows}),
    }


@mcp.tool()
def get_positions(fund: str, as_of: str) -> dict:
    """Return the GP-reported valuations (marks) per portfolio company to be reviewed.

    `as_of` is a quarter-end ISO date, e.g. "2026-03-31". These marks are the *object
    of review* — treat as untrusted and check each against the valuation policy (use
    get_valuation_policy). `method` is one of: market_multiple, dcf, recent_round,
    cost, other.
    """
    rows = [r for r in _raw("gp_valuation_package.csv") if _eq(r, "fund", fund) and _eq(r, "as_of", as_of)]
    total_cost = sum((_to_num(r["cost"]) or 0) for r in rows)
    total_fv = sum((_to_num(r["reported_fv"]) or 0) for r in rows)
    return {"fund": fund, "as_of": as_of, "currency": "USD",
            "positions": _typed(rows),
            "total_cost": total_cost, "total_reported_fv": total_fv}


@mcp.tool()
def get_fund_nav_build(fund: str, as_of: str) -> dict:
    """Return the fund-level NAV build (portfolio FV + cash + other − liabilities)."""
    rows = [r for r in _raw("fund_nav_build.csv") if _eq(r, "fund", fund) and _eq(r, "as_of", as_of)]
    return {"fund": fund, "as_of": as_of, "currency": "USD", "lines": _typed(rows)}


@mcp.tool()
def get_capital_flows(fund: str) -> list:
    """Return contributions / distributions / ending-NAV history (for IRR & MOIC).

    Contributions are negative (cash out from LPs), distributions positive.
    """
    return _typed([r for r in _raw("capital_flows.csv") if _eq(r, "fund", fund)])


@mcp.tool()
def get_fund_terms(fund: str) -> dict:
    """Return fund economics & waterfall terms (commitments, hurdle, catch-up, carry)."""
    rows = [r for r in _raw("fund_terms.csv") if _eq(r, "fund", fund)]
    return {"fund": fund, "terms": {r["key"]: _to_num(r["value"]) for r in rows}}


@mcp.tool()
def get_valuation_policy(fund: str) -> list:
    """Return the valuation policy rules used to review the GP marks (P1–P4)."""
    return [{"policy_id": r["policy_id"], "rule": r["rule"]}
            for r in _raw("valuation_policy.csv") if _eq(r, "fund", fund)]


def main():
    ap = argparse.ArgumentParser(description="portfolio mock MCP server")
    ap.add_argument("--http", action="store_true", help="serve over streamable-http instead of stdio")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()
    if args.http:
        mcp.settings.host = "127.0.0.1"
        mcp.settings.port = args.port
        print(f"portfolio MCP on http://127.0.0.1:{args.port}/mcp", file=sys.stderr)
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
