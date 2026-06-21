# -*- coding: utf-8 -*-
"""Valuation review compute engine — reads ONLY the mcp_pulls/ JSON snapshots.

Independent recompute behind the LP report draft + xlsx workpaper:
  - policy review of each GP mark (P1-P4)
  - NAV bridge (as-reported vs policy-adjusted)
  - returns (MOIC / TVPI / DPI / RVPI / XIRR)
  - independent 8% compound preferred-return recompute
  - 3-scenario European whole-fund waterfall (carry / LP split)

No fabricated numbers: every input is loaded from the live portfolio MCP pulls.
Mock / dev data only.
"""
from __future__ import annotations

import json
import os
from datetime import date

PULLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mcp_pulls")


def load(name):
    with open(os.path.join(PULLS, name), encoding="utf-8") as f:
        return json.load(f)["result"]


positions = load("02_get_positions.json")
nav_build = load("03_get_fund_nav_build.json")
flows = load("04_get_capital_flows.json")
terms = load("05_get_fund_terms.json")["terms"]
policy = load("06_get_valuation_policy.json")

pos = positions["positions"]
total_cost = positions["total_cost"]
total_reported_fv = positions["total_reported_fv"]

# ---- helpers -------------------------------------------------------------
def navline(item):
    for l in nav_build["lines"]:
        if l["item"] == item:
            return l["amount"]
    return None

cash = navline("Cash")
other = navline("Other Assets")
accrued = navline("Accrued Liabilities")
nav_reported = navline("NAV (as-reported)")

# ---- 1. policy review ----------------------------------------------------
# Each mark judged against P1-P4. Adjustment is the *quantifiable* delta to FV.
review = []
for p in pos:
    co, cost, prior, rep = p["company"], p["cost"], p["prior_fv"], p["reported_fv"]
    method, last = p["method"], p["last_updated"]
    up = rep > prior
    flags, verdict, adj = [], "PASS", 0
    # P1 stale: last_updated > 2 quarters before as_of quarter (2026-03)
    stale = last < "2025-09"
    if stale:
        flags.append("P1 stale")
        verdict = "RE-REVIEW"
    # P2 mark-up needs supportable method/trigger; 'other' = mgmt estimate insufficient
    if up and method == "other":
        flags.append("P2 unsupported mark-up")
        verdict = "REJECT MARK-UP"
        adj = prior - rep  # roll back to prior FV
    # P3 valuation above last round needs committee approval (informational for mark-ups by method)
    if up and method == "market_multiple":
        flags.append("P3 confirm vs last round / committee doc")
    review.append({
        "company": co, "cost": cost, "prior_fv": prior, "reported_fv": rep,
        "method": method, "last_updated": last, "qoq": p["qoq_pct"],
        "flags": flags, "verdict": verdict, "adjustment": adj,
        "adjusted_fv": rep + adj,
    })

adj_portfolio = sum(r["adjusted_fv"] for r in review)
total_adjustment = sum(r["adjustment"] for r in review)
nav_adjusted = nav_reported + total_adjustment

# ---- 2. returns ----------------------------------------------------------
contributed = terms["contributed"]
distributions = terms["distributions_to_date"]

def moic(nav):
    return (distributions + nav) / contributed

tvpi_rep = moic(nav_reported)
tvpi_adj = moic(nav_adjusted)
dpi = distributions / contributed
rvpi_rep = nav_reported / contributed
rvpi_adj = nav_adjusted / contributed
gross_moic_rep = total_reported_fv / total_cost
gross_moic_adj = adj_portfolio / total_cost

# XIRR (Newton) on contributions/distribution + ending NAV
def xirr(cfs, guess=0.1):
    d0 = cfs[0][0]
    def npv(r):
        return sum(a / (1 + r) ** ((d - d0).days / 365.0) for d, a in cfs)
    def dnpv(r):
        return sum(-((d - d0).days / 365.0) * a / (1 + r) ** ((d - d0).days / 365.0 + 1) for d, a in cfs)
    r = guess
    for _ in range(200):
        f = npv(r)
        df = dnpv(r)
        if abs(df) < 1e-12:
            break
        rn = r - f / df
        if abs(rn - r) < 1e-10:
            return rn
        r = rn
    return r

def parse(d):
    y, m, dd = (int(x) for x in d.split("-"))
    return date(y, m, dd)

base_cfs = []
for f in flows:
    if f["event"] == "Ending NAV (as-reported)":
        continue
    base_cfs.append((parse(f["date"]), f["amount"]))
end_date = date(2026, 3, 31)
irr_rep = xirr(base_cfs + [(end_date, nav_reported)])
irr_adj = xirr(base_cfs + [(end_date, nav_adjusted)])

# ---- 3. independent 8% compound preferred return -------------------------
rate = terms["preferred_return"]
def yearfrac(d):
    return (end_date - d).days / 365.0
fv_contrib = sum((-f["amount"]) * (1 + rate) ** yearfrac(parse(f["date"]))
                 for f in flows if f["event"] == "Contribution")
fv_dist = sum(f["amount"] * (1 + rate) ** yearfrac(parse(f["date"]))
              for f in flows if f["event"] == "Distribution")
net_contrib = contributed - distributions
pref_recomputed = fv_contrib - fv_dist - net_contrib
pref_provided = terms["preferred_accrued_to_date"]
pref_gap = pref_recomputed - pref_provided

# ---- 4. waterfall (European whole-fund) ----------------------------------
carry_rate = terms["carry"]

def waterfall(nav, pref):
    total_value = distributions + nav
    after_capital = max(total_value - contributed, 0)
    ret_capital = min(total_value, contributed)
    pref_paid = min(after_capital, pref)
    after_pref = after_capital - pref_paid
    # 100% catch-up to bring GP to carry% of (pref + catchup); target = carry/(1-carry)*pref
    if pref_paid >= pref and after_pref > 0:
        catchup_target = carry_rate / (1 - carry_rate) * pref
        catchup = min(after_pref, catchup_target)
    else:
        catchup = 0
    after_catchup = after_pref - catchup
    lp_split = after_catchup * (1 - carry_rate)
    gp_split = after_catchup * carry_rate
    gp_carry = catchup + gp_split
    lp_total = ret_capital + pref_paid + lp_split
    return {
        "total_value": total_value, "return_capital": ret_capital,
        "pref_paid": pref_paid, "catchup": catchup,
        "lp_split": lp_split, "gp_split": gp_split,
        "gp_carry": gp_carry, "lp_total": lp_total,
        "check": round(gp_carry + lp_total - total_value, 0),
    }

wf_A = waterfall(nav_reported, pref_provided)        # GP package
wf_B = waterfall(nav_adjusted, pref_provided)        # policy-adjusted, pref 35M
wf_C = waterfall(nav_adjusted, pref_recomputed)      # policy-adjusted + independent pref

# ---- output --------------------------------------------------------------
out = {
    "fund": positions["fund"], "as_of": positions["as_of"],
    "total_cost": total_cost, "total_reported_fv": total_reported_fv,
    "nav_reported": nav_reported, "nav_adjusted": nav_adjusted,
    "adj_portfolio": adj_portfolio, "total_adjustment": total_adjustment,
    "review": review,
    "contributed": contributed, "distributions": distributions,
    "tvpi_rep": tvpi_rep, "tvpi_adj": tvpi_adj, "dpi": dpi,
    "rvpi_rep": rvpi_rep, "rvpi_adj": rvpi_adj,
    "gross_moic_rep": gross_moic_rep, "gross_moic_adj": gross_moic_adj,
    "irr_rep": irr_rep, "irr_adj": irr_adj,
    "pref_recomputed": pref_recomputed, "pref_provided": pref_provided, "pref_gap": pref_gap,
    "fv_contrib": fv_contrib, "fv_dist": fv_dist, "net_contrib": net_contrib,
    "wf_A": wf_A, "wf_B": wf_B, "wf_C": wf_C,
}

if __name__ == "__main__":
    def m(x):
        return f"{x:,.0f}"
    print("=== POLICY REVIEW ===")
    for r in review:
        print(f"  {r['company']:<22} {r['method']:<15} verdict={r['verdict']:<16} "
              f"adj={m(r['adjustment'])}  flags={r['flags']}")
    print(f"\nadjusted portfolio FV = {m(adj_portfolio)}  (reported {m(total_reported_fv)}, delta {m(total_adjustment)})")
    print(f"NAV reported = {m(nav_reported)} | NAV adjusted = {m(nav_adjusted)}")
    print(f"\n=== RETURNS ===")
    print(f"  Gross MOIC  rep {gross_moic_rep:.3f}x  adj {gross_moic_adj:.3f}x")
    print(f"  TVPI        rep {tvpi_rep:.3f}x  adj {tvpi_adj:.3f}x")
    print(f"  DPI {dpi:.3f}x | RVPI rep {rvpi_rep:.3f}x adj {rvpi_adj:.3f}x")
    print(f"  Net IRR     rep {irr_rep*100:.2f}%  adj {irr_adj*100:.2f}%  (hurdle 8%)")
    print(f"\n=== PREF RECOMPUTE (8% compound) ===")
    print(f"  FV contrib {m(fv_contrib)} - FV dist {m(fv_dist)} - net contrib {m(net_contrib)}")
    print(f"  = recomputed pref {m(pref_recomputed)} | provided {m(pref_provided)} | gap {m(pref_gap)}")
    print(f"\n=== WATERFALL (carry / LP) ===")
    for nm, w in [("A GP-pkg", wf_A), ("B adj+35M", wf_B), ("C adj+indep", wf_C)]:
        print(f"  {nm:<12} carry={m(w['gp_carry']):>14}  LP={m(w['lp_total']):>16}  "
              f"pref_paid={m(w['pref_paid'])}  catchup={m(w['catchup'])}  check={w['check']}")

    with open(os.path.join(os.path.dirname(__file__), "analysis_result.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
