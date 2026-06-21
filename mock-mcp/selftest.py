# -*- coding: utf-8 -*-
"""Data-integrity self-test for the mock MCP servers.

Loads every data/*.csv and asserts the invariants the agents rely on (trial balance
balances, NAV ties to LP accounts, recon totals, planted test cases present, ...).
Pure stdlib — does NOT import the mcp SDK, so it runs even without `pip install mcp`.

Run:  python selftest.py
"""
from __future__ import annotations

import csv
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_failures = []
_checks = 0


def _num(v):
    s = str(v).strip()
    if s == "" or s.lower() == "n/a":
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def rows(rel):
    with open(os.path.join(HERE, rel), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check(label, cond):
    global _checks
    _checks += 1
    if cond:
        print(f"  OK   {label}")
    else:
        print(f"  FAIL {label}")
        _failures.append(label)


print("== CSV parse / inventory ==")
csvs = sorted(glob.glob(os.path.join(HERE, "*", "data", "*.csv")))
check(f"found {len(csvs)} data CSVs (expected 29)", len(csvs) == 29)
for path in csvs:
    try:
        with open(path, newline="", encoding="utf-8") as f:
            n = len(list(csv.DictReader(f)))
        check(f"parse {os.path.relpath(path, HERE)} ({n} rows)", n >= 1)
    except Exception as e:  # noqa: BLE001
        check(f"parse {os.path.relpath(path, HERE)} — {e}", False)

print("\n== internal-gl ==")
tb = rows("internal-gl/data/trial_balance.csv")
dr = sum(_num(r["current_ytd"]) for r in tb if r["normal_balance"] == "Dr")
cr = sum(_num(r["current_ytd"]) for r in tb if r["normal_balance"] == "Cr")
check(f"trial balance debits=credits ({dr:,.0f})", abs(dr - cr) < 0.01)
check("trial balance total = 21,380,000", abs(dr - 21380000) < 0.01)
gl = rows("internal-gl/data/gl_positions.csv")
check("GL positions total = 84,500,000", abs(sum(_num(r["mv_usd"]) for r in gl) - 84500000) < 1)

print("\n== subledger ==")
sub = rows("subledger/data/subledger_holdings.csv")
check("subledger total = 82,650,300", abs(sum(_num(r["mv_usd"]) for r in sub) - 82650300) < 1)
gl_by = {r["sec_id"]: _num(r["qty_face"]) for r in gl}
sub_by = {r["sec_id"]: _num(r["qty_face"]) for r in sub}
check("planted VRT qty break (GL 50000 vs custody 52500)",
      gl_by["EQ-VRT"] == 50000 and sub_by["EQ-VRT"] == 52500)

print("\n== nav (statement-auditor) ==")
nb = rows("nav/data/nav_build.csv")
nav_val = next(_num(r["amount"]) for r in nb if "NAV" in r["item"])
lp = rows("nav/data/lp_capital_accounts.csv")
ending_sum = sum(_num(r["ending"]) for r in lp)
check(f"LP ending sum ({ending_sum:,.0f}) = NAV ({nav_val:,.0f})", abs(ending_sum - nav_val) < 0.01)
for r in lp:
    foot = (_num(r["beginning"]) + _num(r["contributions"]) - _num(r["distributions"])
            + _num(r["net_gain_loss"]) - _num(r["mgmt_fee"]))
    check(f"{r['lp_id']} foots to ending", abs(foot - _num(r["ending"])) < 0.01)

print("\n== portfolio (valuation-reviewer) ==")
pkg = rows("portfolio/data/gp_valuation_package.csv")
check("GP reported FV total = 330,000,000", abs(sum(_num(r["reported_fv"]) for r in pkg) - 330000000) < 1)
check("invested cost total = 250,000,000", abs(sum(_num(r["cost"]) for r in pkg) - 250000000) < 1)
nova = next(r for r in pkg if r["company"] == "Nova Biotech")
check("planted P2 breach: Nova Biotech method=other, +62%", nova["method"] == "other" and _num(nova["qoq_pct"]) > 0.6)
zephyr = next(r for r in pkg if r["company"] == "Zephyr Retail")
check("planted P1 breach: Zephyr last_updated 2025-03 (stale)", zephyr["last_updated"] == "2025-03")

print("\n== screening (kyc-screener) ==")
sanc = rows("screening/data/sanctions.csv")
check("sanctions has Ivan Petrov 1970-03-15 Russia",
      any(r["name"] == "Ivan Petrov" and r["dob"] == "1970-03-15" and r["country"] == "Russia" for r in sanc))
mg = next(r for r in sanc if r["name"] == "Maria Garcia")
check("Maria Garcia on list is 1955/Colombia (→ false positive vs 1988/Spain applicant)",
      mg["dob"] == "1955-07-22" and mg["country"] == "Colombia")
pep = rows("screening/data/pep.csv")
check("PEP has Adewale Okonkwo (Nigeria)", any(r["name"] == "Adewale Okonkwo" for r in pep))

print("\n== crm (meeting-prep) ==")
hold = rows("crm/data/holdings.csv")
total = sum(_num(r["mv_usd"]) for r in hold)
eq = sum(_num(r["mv_usd"]) for r in hold if r["asset_class"] == "Equity")
check(f"holdings total = 12,000,000", abs(total - 12000000) < 1)
check(f"equity weight 72% (IPS band 55-65% breach) [{eq/total:.0%}]", abs(eq / total - 0.72) < 0.005)
comm = rows("crm/data/communications.csv")
check("planted prompt-injection flagged in communications",
      any(r["flag"] == "suspected_prompt_injection" for r in comm))

print("\n== capiq ==")
comps = rows("capiq/data/comps.csv")
check("comps has 14 names", len(comps) == 14)
check("comps includes VRT", any(r["ticker"] == "VRT" for r in comps))

print("\n== factset ==")
fund = rows("factset/data/fundamentals.csv")
check("TSM Q1-2026 revenue = 35.90", any(r["ticker"] == "TSM" and r["metric"] == "revenue"
      and r["period"] == "Q1-2026" and _num(r["value"]) == 35.90 for r in fund))

print("\n== daloopa ==")
li = rows("daloopa/data/line_items.csv")
plat = [r for r in li if r["ticker"] == "TSM" and r["statement"] == "revenue_mix_platform"]
check(f"TSM platform mix sums to ~1.0 ({sum(_num(r['value']) for r in plat):.2f})",
      abs(sum(_num(r["value"]) for r in plat) - 1.0) < 0.001)

print(f"\n{'='*40}\n{_checks - len(_failures)}/{_checks} checks passed")
if _failures:
    print("FAILURES:")
    for f in _failures:
        print("  -", f)
    sys.exit(1)
print("ALL GREEN")
