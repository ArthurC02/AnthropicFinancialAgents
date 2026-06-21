# -*- coding: utf-8 -*-
"""獨立重算 VRT DCF 基準情境,驗證 build_dcf.py 的活公式邏輯並取得可報告數字。

純 Python 重算,輸入與 build_dcf.py 完全一致(全部錨定 mcp_pulls/)。Mock / dev only。
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PULLS = os.path.join(os.path.dirname(HERE), "mcp_pulls")


def load(name):
    with open(os.path.join(PULLS, name), encoding="utf-8") as f:
        return json.load(f)["result"]


fund = {(r["period"], r["metric"]): r["value"] for r in load("06_factset_get_fundamentals_VRT.json")}
est = {(r["period"], r["metric"]): r["value"] for r in load("04_capiq_get_estimates_VRT.json")}
quote = load("02_capiq_get_quote_VRT.json")

REV_FY25 = fund[("FY2025", "revenue")]
EBITDA_FY25 = fund[("FY2025", "ebitda")]
NETDEBT = fund[("FY2025", "net_debt")]
REV_FY26E = est[("FY2026", "revenue")]
REV_FY27E = est[("FY2027", "revenue")]
PRICE = quote["price"]
MKTCAP = quote["mktcap_usd_bn"]
SHARES = round(MKTCAP / PRICE, 3)

WACC = 0.10; G = 0.035; EXM = 22.0; TAX = 0.21
DAr = 0.026; CXr = 0.023; NWCr = 0.08

g26 = round(REV_FY26E / REV_FY25 - 1, 3)
g27 = round(REV_FY27E / REV_FY26E - 1, 3)
# Base 情境(對齊 build_dcf.py)
growth = [g26, g27, 0.18, 0.13, 0.09]
margin = [0.20, 0.21, 0.22, 0.225, 0.23]

rev = REV_FY25
fcffs, pvs, ebitdas = [], [], []
for i in range(5):
    rev_prev = rev
    rev = rev_prev * (1 + growth[i])
    ebit = rev * margin[i]
    nopat = ebit * (1 - TAX)
    da = rev * DAr
    capex = rev * CXr
    dnwc = (rev - rev_prev) * NWCr
    fcff = nopat + da - capex - dnwc
    df = 1 / (1 + WACC) ** (i + 1)
    fcffs.append(fcff); pvs.append(fcff * df); ebitdas.append(ebit + da)

pv_explicit = sum(pvs)
ebitda_fy30 = ebitdas[-1]
df5 = 1 / (1 + WACC) ** 5
tv_exit = ebitda_fy30 * EXM
pv_tv = tv_exit * df5
ev = pv_explicit + pv_tv
equity = ev - NETDEBT
ps_exit = equity / SHARES
upside = ps_exit / PRICE - 1

tv_perp = fcffs[-1] * (1 + G) / (WACC - G)
pv_tv_perp = tv_perp * df5
ev_perp = pv_explicit + pv_tv_perp
ps_perp = (ev_perp - NETDEBT) / SHARES

ebitda_fy26 = ebitdas[0]
implied_ev_ebitda = ev / ebitda_fy26
tv_share = pv_tv / ev

print("=== VRT DCF 重算(基準情境;輸入皆來自 mcp_pulls)===")
print(f"FY25A 營收 ${REV_FY25:.2f}B  EBITDA ${EBITDA_FY25:.2f}B  淨負債 ${NETDEBT:.1f}B")
print(f"股數 {SHARES:.3f}bn (=市值 {MKTCAP}/價 {PRICE})  現價 ${PRICE:.2f}")
print(f"FY26 成長 +{g26:.1%}  FY27 成長 +{g27:.1%}")
print(f"FY30E 營收 ${rev:.2f}B  FY30E EBITDA ${ebitda_fy30:.2f}B")
print(f"顯性期 PV(FCFF) ${pv_explicit:.2f}B")
print(f"終值 TV(Exit 22x) ${tv_exit:.2f}B  其現值 ${pv_tv:.2f}B")
print(f"企業價值 EV ${ev:.2f}B  股權價值 ${equity:.2f}B")
print(f"每股價值(Exit Mult.) ${ps_exit:.2f}  vs 現價 ${PRICE:.2f}  => {upside:+.1%}")
print(f"每股價值(永續成長 g={G:.1%}) ${ps_perp:.2f}")
print(f"DCF 隱含 EV/EBITDA(FY26E) {implied_ev_ebitda:.1f}x  (現行 ~51x)")
print(f"終值占 EV 比重 {tv_share:.1%}  (健康 50–70%)")
