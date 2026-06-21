# -*- coding: utf-8 -*-
"""factset MCP server (mock) — fundamentals, consensus estimates, prices (read-only).

Stands in for the `factset` MCP (env var FACTSET_MCP_URL) used by:
  - earnings-reviewer : pull reported actuals + consensus to plug an existing model
  - market-researcher : fundamentals for the comp set

NOTE: factset has a *real* vendor URL in
plugins/vertical-plugins/financial-analysis/.mcp.json. This is a local mock so the
agents run offline; swap back to the vendor URL when you have credentials.

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
DEFAULT_PORT = 8008


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


mcp = FastMCP("factset", host="127.0.0.1", port=DEFAULT_PORT)


@mcp.tool()
def list_coverage() -> dict:
    """List tickers and periods available in this mock."""
    f = _raw("fundamentals.csv")
    return {"tickers": sorted({r["ticker"] for r in f}),
            "periods": sorted({r["period"] for r in f})}


@mcp.tool()
def get_fundamentals(ticker: str, period: str = "") -> list:
    """Return reported fundamentals (long format: metric/value/unit) for a ticker.

    Optionally filter by `period`, e.g. "Q1-2026" or "FY2025". Metrics include
    revenue, gross_margin, op_margin, net_margin, eps, eps_adr, net_income, usd_twd,
    revenue_yoy, revenue_qoq.
    """
    rows = [r for r in _raw("fundamentals.csv") if _eq(r, "ticker", ticker)]
    if period:
        rows = [r for r in rows if _eq(r, "period", period)]
    return _typed(rows)


@mcp.tool()
def get_consensus_estimates(ticker: str, period: str = "") -> list:
    """Return consensus vs actual vs prior guidance per metric (for beat/miss analysis).

    Optionally filter by `period`. `actual` is blank for future periods.
    """
    rows = [r for r in _raw("consensus_estimates.csv") if _eq(r, "ticker", ticker)]
    if period:
        rows = [r for r in rows if _eq(r, "period", period)]
    return _typed(rows)


@mcp.tool()
def get_prices(ticker: str) -> list:
    """Return recent closing prices for a ticker (with context notes)."""
    return _typed([r for r in _raw("prices.csv") if _eq(r, "ticker", ticker)])


def main():
    ap = argparse.ArgumentParser(description="factset mock MCP server")
    ap.add_argument("--http", action="store_true", help="serve over streamable-http instead of stdio")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()
    if args.http:
        mcp.settings.host = "127.0.0.1"
        mcp.settings.port = args.port
        print(f"factset MCP on http://127.0.0.1:{args.port}/mcp", file=sys.stderr)
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
