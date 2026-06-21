# -*- coding: utf-8 -*-
"""daloopa MCP server (mock) — granular as-reported filing line items (read-only).

Stands in for the `daloopa` MCP (env var DALOOPA_MCP_URL) used by:
  - earnings-reviewer : granular line items (revenue mix by platform/node) to update a model
  - model-builder     : historical line items to build a model from scratch
  - pitch-agent       : segment detail for the pitch model

NOTE: daloopa has a *real* vendor URL in
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
DEFAULT_PORT = 8009


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


mcp = FastMCP("daloopa", host="127.0.0.1", port=DEFAULT_PORT)


@mcp.tool()
def list_coverage() -> dict:
    """List tickers, periods and statement groups available in this mock."""
    rows = _raw("line_items.csv")
    return {"tickers": sorted({r["ticker"] for r in rows}),
            "periods": sorted({r["period"] for r in rows}),
            "statements": sorted({r["statement"] for r in rows})}


@mcp.tool()
def get_line_items(ticker: str, period: str = "", statement: str = "") -> list:
    """Return granular as-reported line items for a ticker.

    Filters (optional): `period` (e.g. "Q1-2026", "FY2025") and `statement`
    (a group such as "revenue_mix_platform", "revenue_mix_node", "income_statement",
    "segment_revenue", "product_revenue", "guidance"). Call list_coverage() to see groups.
    """
    rows = [r for r in _raw("line_items.csv") if _eq(r, "ticker", ticker)]
    if period:
        rows = [r for r in rows if _eq(r, "period", period)]
    if statement:
        rows = [r for r in rows if _eq(r, "statement", statement)]
    return _typed(rows)


def main():
    ap = argparse.ArgumentParser(description="daloopa mock MCP server")
    ap.add_argument("--http", action="store_true", help="serve over streamable-http instead of stdio")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()
    if args.http:
        mcp.settings.host = "127.0.0.1"
        mcp.settings.port = args.port
        print(f"daloopa MCP on http://127.0.0.1:{args.port}/mcp", file=sys.stderr)
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
