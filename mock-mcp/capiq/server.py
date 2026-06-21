# -*- coding: utf-8 -*-
"""capiq MCP server (mock) — market data: comps, quotes, events, estimates (read-only).

Stands in for the `capiq` MCP (env var CAPIQ_MCP_URL) used by:
  - market-researcher : peer comps with consistent metric definitions
  - model-builder     : market data / quotes to seed a model
  - pitch-agent       : comps + market context for a pitch
  - meeting-prep-agent: market events touching a client's holdings

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
DEFAULT_PORT = 8007


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


mcp = FastMCP("capiq", host="127.0.0.1", port=DEFAULT_PORT)


@mcp.tool()
def get_comps(sector: str = "", tickers: str = "") -> dict:
    """Return a comparable-company set with consistent metric definitions.

    Filters (optional): `sector` (e.g. "AI Data Center Cooling") and/or `tickers`
    (comma-separated, e.g. "VRT,NVT,SU.PA"). With no filter, returns the full set.
    Metrics: mktcap (USD bn), rev_yoy, op_margin, fwd_pe, ev_ebitda, ev_rev, ret_1y.
    Note: EV multiples are not comparable across component vs system/ODM business models.
    """
    rows = _raw("comps.csv")
    if sector:
        rows = [r for r in rows if _eq(r, "sector", sector)]
    if tickers:
        want = {t.strip().lower() for t in tickers.split(",") if t.strip()}
        rows = [r for r in rows if r["ticker"].strip().lower() in want]
    return {"sector": sector or "AI Data Center Cooling", "count": len(rows),
            "as_of": "2026-06-18", "comps": _typed(rows),
            "caveat": "Free-source estimates; n/a where unavailable; EV/Rev not comparable "
                      "across component vs ODM/OEM models."}


@mcp.tool()
def get_quote(ticker: str) -> dict:
    """Return a current quote (price, market cap, 52-week range) for a ticker."""
    for r in _raw("quotes.csv"):
        if _eq(r, "ticker", ticker):
            return _typed([r])[0]
    return {"error": f"no quote for {ticker}"}


@mcp.tool()
def get_market_events(ticker: str = "") -> list:
    """Return recent market events; optionally filter to one `ticker`."""
    rows = _raw("market_events.csv")
    if ticker:
        rows = [r for r in rows if _eq(r, "ticker", ticker)]
    return _typed(rows)


@mcp.tool()
def get_estimates(ticker: str, period: str = "") -> list:
    """Return forward street estimates for a ticker; optionally filter by `period`."""
    rows = [r for r in _raw("estimates.csv") if _eq(r, "ticker", ticker)]
    if period:
        rows = [r for r in rows if _eq(r, "period", period)]
    return _typed(rows)


def main():
    ap = argparse.ArgumentParser(description="capiq mock MCP server")
    ap.add_argument("--http", action="store_true", help="serve over streamable-http instead of stdio")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()
    if args.http:
        mcp.settings.host = "127.0.0.1"
        mcp.settings.port = args.port
        print(f"capiq MCP on http://127.0.0.1:{args.port}/mcp", file=sys.stderr)
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
