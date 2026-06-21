# -*- coding: utf-8 -*-
"""internal-gl MCP server (mock) — read-only General Ledger.

Stands in for the `internal-gl` MCP (env var GL_MCP_URL) used by:
  - month-end-closer : pull trial balance, drill journal entries, query balances
  - gl-reconciler    : pull position-level GL balances (one side of the recon)

Serves fake data from ./data/*.csv. Mock / dev only — never production.
Read-only by design: this server exposes no write/post tools (the agents must
never post to the ledger).
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

from mcp.server.fastmcp import FastMCP

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
DEFAULT_PORT = 8001


def _to_num(v):
    """Coerce a CSV string to int/float where it looks numeric; else return it."""
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


mcp = FastMCP("internal-gl", host="127.0.0.1", port=DEFAULT_PORT)


@mcp.tool()
def list_entities() -> dict:
    """List the entities/funds available in this ledger and the periods on file.

    Use this first to discover what `entity` / `fund` / `period` values the other
    tools accept.
    """
    tb = _raw("trial_balance.csv")
    pos = _raw("gl_positions.csv")
    return {
        "trial_balance_entities": sorted({r["entity"] for r in tb}),
        "trial_balance_periods": sorted({r["period"] for r in tb}),
        "gl_position_funds": sorted({r["fund"] for r in pos}),
        "gl_position_as_of": sorted({r["as_of"] for r in pos}),
    }


@mcp.tool()
def get_trial_balance(entity: str, period: str) -> dict:
    """Return the trial balance for an entity and period (YYYY-MM).

    Each line has the prior-month and current-month YTD balance plus the computed
    movement (for flux / variance analysis). Also returns the debit=credit balance
    check. Pre-close figures (accruals not yet booked).
    """
    rows = [r for r in _raw("trial_balance.csv") if _eq(r, "entity", entity) and _eq(r, "period", period)]
    out = []
    total_dr = total_cr = 0.0
    for r in rows:
        prior = _to_num(r["prior_ytd"]) or 0
        cur = _to_num(r["current_ytd"]) or 0
        movement = cur - prior
        pct = (movement / prior) if prior else None
        if r["normal_balance"] == "Dr":
            total_dr += cur
        else:
            total_cr += cur
        out.append({
            "account": r["account"], "name": r["name"], "type": r["type"],
            "normal_balance": r["normal_balance"],
            "prior_ytd": prior, "current_ytd": cur,
            "movement": movement,
            "movement_pct": round(pct, 4) if pct is not None else None,
        })
    diff = round(total_dr - total_cr, 2)
    return {
        "entity": entity, "period": period, "status": "pre-close",
        "currency": "USD", "lines": out,
        "total_debits": total_dr, "total_credits": total_cr,
        "difference": diff, "balanced": abs(diff) < 0.01,
    }


@mcp.tool()
def get_journal_entries(entity: str, account: str = "", start_date: str = "",
                        end_date: str = "", source: str = "") -> list:
    """Return journal-entry lines, optionally filtered.

    Filters (all optional, combined with AND):
      - account    : GL account code, e.g. "6200"
      - start_date : ISO date inclusive lower bound, e.g. "2026-04-01"
      - end_date   : ISO date inclusive upper bound
      - source     : posting source, e.g. "Payroll", "AP", "Billing", "Manual", "Bank"
    Use this to explain a flux: drill the account that moved.
    """
    rows = [r for r in _raw("journal_entries.csv") if _eq(r, "entity", entity)]
    if account:
        rows = [r for r in rows if _eq(r, "account", account)]
    if source:
        rows = [r for r in rows if _eq(r, "source", source)]
    if start_date:
        rows = [r for r in rows if r["date"] >= start_date]
    if end_date:
        rows = [r for r in rows if r["date"] <= end_date]
    return _typed(rows)


@mcp.tool()
def get_account_balance(entity: str, account: str, period: str) -> dict:
    """Return the prior and current YTD balance for a single GL account."""
    for r in _raw("trial_balance.csv"):
        if _eq(r, "entity", entity) and _eq(r, "period", period) and _eq(r, "account", account):
            prior = _to_num(r["prior_ytd"]) or 0
            cur = _to_num(r["current_ytd"]) or 0
            return {
                "entity": entity, "period": period, "account": account,
                "name": r["name"], "normal_balance": r["normal_balance"],
                "prior_ytd": prior, "current_ytd": cur, "movement": cur - prior,
            }
    return {"error": f"account {account} not found for {entity} / {period}"}


@mcp.tool()
def get_gl_positions(fund: str, as_of: str) -> dict:
    """Return position-level GL balances for a fund (the GL side of a reconciliation).

    `as_of` is an ISO date, e.g. "2026-04-30". Each row is a security with quantity/
    face and market value as carried in the General Ledger (trade-date basis).
    """
    rows = [r for r in _raw("gl_positions.csv") if _eq(r, "fund", fund) and _eq(r, "as_of", as_of)]
    total = sum((_to_num(r["mv_usd"]) or 0) for r in rows)
    return {"fund": fund, "as_of": as_of, "basis": "trade-date", "currency": "USD",
            "source": "GL", "positions": _typed(rows), "total_mv_usd": total}


def main():
    ap = argparse.ArgumentParser(description="internal-gl mock MCP server")
    ap.add_argument("--http", action="store_true", help="serve over streamable-http instead of stdio")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()
    if args.http:
        mcp.settings.host = "127.0.0.1"
        mcp.settings.port = args.port
        print(f"internal-gl MCP on http://127.0.0.1:{args.port}/mcp", file=sys.stderr)
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
