# -*- coding: utf-8 -*-
"""subledger MCP server (mock) — custody / position sub-ledger.

Stands in for the `subledger` MCP (env var SUBLEDGER_MCP_URL) used by:
  - gl-reconciler : the custody side of the reconciliation, plus the reference
                    data (pending settlements, FX rates, tolerance policy) needed
                    to trace which breaks are real vs timing/rounding/reclass.

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
DEFAULT_PORT = 8002


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


mcp = FastMCP("subledger", host="127.0.0.1", port=DEFAULT_PORT)


@mcp.tool()
def get_subledger_holdings(fund: str, as_of: str) -> dict:
    """Return custody/sub-ledger holdings for a fund (the custody side of a recon).

    `as_of` is an ISO date, e.g. "2026-04-30". Settlement-date basis. This is upstream
    custody data — in the reconciliation flow it is treated as untrusted external input.
    """
    rows = [r for r in _raw("subledger_holdings.csv") if _eq(r, "fund", fund) and _eq(r, "as_of", as_of)]
    total = sum((_to_num(r["mv_usd"]) or 0) for r in rows)
    return {"fund": fund, "as_of": as_of, "basis": "settlement-date", "currency": "USD",
            "source": "Custody", "positions": _typed(rows), "total_mv_usd": total}


@mcp.tool()
def get_pending_settlements(fund: str, as_of: str) -> list:
    """Return trades executed but not yet settled as of the date (timing-break evidence).

    A buy/sell that has traded but not settled across the cut-off explains a GL-vs-custody
    difference that is *timing*, not a real break.
    """
    rows = [r for r in _raw("pending_settlements.csv") if _eq(r, "fund", fund) and _eq(r, "as_of", as_of)]
    return _typed(rows)


@mcp.tool()
def get_fx_rates(as_of: str, pair: str = "") -> list:
    """Return GL vs custody FX rates for a date (FX-rounding-break evidence).

    Different decimal precision between GL and custody books produces tiny translation
    differences on foreign-currency positions that are rounding, not real breaks.
    Optionally filter by `pair`, e.g. "EUR/USD".
    """
    rows = [r for r in _raw("fx_rates.csv") if _eq(r, "as_of", as_of)]
    if pair:
        rows = [r for r in rows if _eq(r, "pair", pair)]
    return _typed(rows)


@mcp.tool()
def get_tolerance_policy() -> dict:
    """Return the reconciliation tolerance policy (what counts as a break)."""
    return {
        "absolute_mv_usd": 0.01,
        "quantity": 0,
        "fx_rounding_relative": 0.0005,
        "note": "Foreign-currency MV differences within 0.05% attributable to GL vs custody "
                "FX decimal precision are treated as rounding, not breaks.",
    }


def main():
    ap = argparse.ArgumentParser(description="subledger mock MCP server")
    ap.add_argument("--http", action="store_true", help="serve over streamable-http instead of stdio")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()
    if args.http:
        mcp.settings.host = "127.0.0.1"
        mcp.settings.port = args.port
        print(f"subledger MCP on http://127.0.0.1:{args.port}/mcp", file=sys.stderr)
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
