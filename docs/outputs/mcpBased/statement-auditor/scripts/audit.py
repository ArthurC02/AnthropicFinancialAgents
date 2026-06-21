# -*- coding: utf-8 -*-
"""statement-auditor tie-out — audit a draft LP statement against the live `nav` MCP pull.

SOURCE OF TRUTH = the JSON pulled from the nav MCP server (mcp_pulls/).
UNDER TEST      = the draft LP statement (the fileBased sample lp_statement.md),
                  treated as untrusted upstream input.

Two checks (per the agent's nav-tieout workflow):
  1) Each LP row foots: beginning + contributions - distributions + net_gain_loss - mgmt_fee = ending
  2) Fund NAV ties to the sum of LP ending capital
…run on BOTH the NAV pack (to prove the source is internally consistent) and the
draft statement (to surface planted errors). Tolerance = 0.01. Mock/dev data only.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PULLS = os.path.join(os.path.dirname(HERE), "mcp_pulls")
TOL = 0.01

# ---- 1. Load the authoritative figures from the live MCP pull ----------------
with open(os.path.join(PULLS, "02_get_nav_build.json"), encoding="utf-8") as f:
    nav_build = json.load(f)["result"]
with open(os.path.join(PULLS, "03_get_lp_capital_accounts.json"), encoding="utf-8") as f:
    lp = json.load(f)["result"]

nav_lines = {ln["item"]: ln["amount"] for ln in nav_build["lines"]}
NAV = nav_lines["Net Assets (NAV)"]
truth = {a["lp_id"]: a for a in lp["accounts"]}
truth_totals = lp["totals"]

# ---- 2. The draft LP statement under test (transcribed from the sample) ------
# Cols: beginning, contributions, distributions, net_gain_loss, mgmt_fee, ending, ownership_pct
draft = {
    "LP-001": dict(lp_name="University Endowment", beginning=40000000, contributions=5000000,
                   distributions=2000000, net_gain_loss=4000000, mgmt_fee=200000,
                   ending=46800000, ownership_pct=41.58),
    "LP-002": dict(lp_name="State Pension Plan", beginning=30000000, contributions=0,
                   distributions=1500000, net_gain_loss=3000000, mgmt_fee=187500,
                   ending=31321500, ownership_pct=27.85),
    "LP-003": dict(lp_name="Family Office LLC", beginning=20000000, contributions=2500000,
                   distributions=0, net_gain_loss=2000000, mgmt_fee=125000,
                   ending=24375000, ownership_pct=21.23),
    "LP-004": dict(lp_name="GP Commitment", beginning=10000000, contributions=0,
                   distributions=500000, net_gain_loss=1000000, mgmt_fee=0,
                   ending=10500000, ownership_pct=9.34),
}
draft_total_ending = sum(r["ending"] for r in draft.values())

COLS = ["beginning", "contributions", "distributions", "net_gain_loss", "mgmt_fee", "ending"]


def foots(r):
    """Does this row satisfy beginning + contrib - distrib + nGL - fee = ending?"""
    calc = r["beginning"] + r["contributions"] - r["distributions"] + r["net_gain_loss"] - r["mgmt_fee"]
    return abs(calc - r["ending"]) <= TOL, calc


print("=" * 78)
print("CHECK 0 — NAV pack internal consistency (the SOURCE OF TRUTH, from live MCP)")
print("=" * 78)
sum_truth_ending = sum(a["ending"] for a in truth.values())
print(f"  Sum of LP ending (live pull)      = {sum_truth_ending:,}")
print(f"  totals.ending (live pull)         = {truth_totals['ending']:,}")
print(f"  Fund NAV (Net Assets, live pull)  = {NAV:,}")
print(f"  NAV == Sum LP ending ?            -> {'PASS' if abs(NAV - sum_truth_ending) <= TOL else 'FAIL'}")
print(f"  Total Assets - Total Liabilities  = {nav_lines['Total Assets'] - nav_lines['Total Liabilities']:,}  (== NAV: {nav_lines['Total Assets'] - nav_lines['Total Liabilities'] == NAV})")
for lp_id, a in truth.items():
    ok, calc = foots(a)
    print(f"  {lp_id} foots? {'PASS' if ok else 'FAIL'}  (calc {calc:,} vs ending {a['ending']:,})")

print()
print("=" * 78)
print("CHECK 1 — Per-LP footing of the DRAFT statement (under test)")
print("=" * 78)
for lp_id, r in draft.items():
    ok, calc = foots(r)
    tag = "FOOTS" if ok else "DOES NOT FOOT"
    print(f"  {lp_id}: beginning+contrib-distrib+nGL-fee = {calc:,}  vs stated ending {r['ending']:,}  -> {tag}")

print()
print("=" * 78)
print("CHECK 2 — Column-by-column: DRAFT vs NAV pack (live MCP)")
print("=" * 78)
exceptions = []
for lp_id in draft:
    d, t = draft[lp_id], truth[lp_id]
    for c in COLS + ["ownership_pct"]:
        if abs(d[c] - t[c]) > TOL:
            diff = d[c] - t[c]
            exceptions.append((lp_id, c, d[c], t[c], diff))
            print(f"  {lp_id} {c:14s} draft={d[c]:>12,}  nav={t[c]:>12,}  diff={diff:>+12,}")
if not exceptions:
    print("  (no per-cell differences)")

print()
print("=" * 78)
print("CHECK 3 — Fund-level tie-out: DRAFT total ending vs NAV")
print("=" * 78)
print(f"  Draft TOTAL ending = {draft_total_ending:,}")
print(f"  Fund NAV (truth)   = {NAV:,}")
diff = draft_total_ending - NAV
print(f"  Difference         = {diff:>+,}")
print(f"  Ties out?          -> {'PASS' if abs(diff) <= TOL else 'FAIL (DO NOT DISTRIBUTE)'}")

# reconcile the total break against the sum of per-cell exception diffs that hit ending/inputs
print()
print("  Reconciliation of the +%s break:" % f"{diff:,}")
print("   LP-001 mgmt_fee understated by 50,000 -> ending overstated 50,000")
print("   LP-002 ending mis-stated +9,000 (row does not foot)")
print("   LP-003 contributions overstated 500,000 -> ending overstated 500,000")
print("   50,000 + 9,000 + 500,000 = 559,000  == total break: %s" % (50000 + 9000 + 500000 == diff))

print()
print("=" * 78)
print("VERDICT")
print("=" * 78)
clean = [lp_id for lp_id in draft if all(abs(draft[lp_id][c] - truth[lp_id][c]) <= TOL for c in COLS)]
dirty = [lp_id for lp_id in draft if lp_id not in clean]
print(f"  PASS (releasable): {clean}")
print(f"  HOLD (re-check):   {dirty}")
print(f"  Fund NAV tie-out:  {'PASS' if abs(diff) <= TOL else 'FAIL'}")
print(f"  Overall:           {'CLEAR TO DISTRIBUTE' if not dirty and abs(diff) <= TOL else 'DO NOT DISTRIBUTE (pending IR sign-off after corrections)'}")
