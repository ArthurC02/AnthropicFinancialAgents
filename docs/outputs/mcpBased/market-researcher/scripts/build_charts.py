# -*- coding: utf-8 -*-
"""從 MCP 拉到的 comps JSON 產兩張圖:估值散佈圖 + 1年報酬長條。Mock / dev only。"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PULLS = os.path.join(ROOT, "mcp_pulls")
OUT = os.path.join(ROOT, "out")
os.makedirs(OUT, exist_ok=True)

# 嘗試載入中文字體;找不到就退回預設(英文標籤仍可讀)
CJK = None
for cand in ["Microsoft JhengHei", "Microsoft YaHei", "SimHei", "PMingLiU"]:
    try:
        font_manager.findfont(cand, fallback_to_default=False)
        CJK = cand
        break
    except Exception:
        continue
if CJK:
    plt.rcParams["font.sans-serif"] = [CJK]
plt.rcParams["axes.unicode_minus"] = False


def num(v):
    if isinstance(v, (int, float)):
        return v
    return None


with open(os.path.join(PULLS, "01_capiq_get_comps.json"), encoding="utf-8") as f:
    comps = json.load(f)["result"]["comps"]

NAVY = "#0B1F3A"; ACCENT = "#2E9BD6"; TEAL = "#14A38C"; AMBER = "#E89A1C"; RED = "#C03A2B"

# --- 圖1:估值散佈 EV/EBITDA vs 營收成長(僅有 EV/EBITDA 數值者)---
pts = []
for r in comps:
    ev = num(r.get("ev_ebitda")); g = num(r.get("rev_yoy"))
    if ev is not None and g is not None:
        pts.append((g, ev, r["ticker"], num(r.get("mktcap_usd_bn")) or 5))
fig, ax = plt.subplots(figsize=(8, 5.2), dpi=130)
for g, ev, t, mc in pts:
    color = TEAL if t == "VRT" else ACCENT
    ax.scatter(g*100, ev, s=max(40, min(mc*2, 400)), color=color, alpha=0.75,
               edgecolors=NAVY, linewidths=0.6, zorder=3)
    ax.annotate(t, (g*100, ev), fontsize=8, xytext=(4, 4), textcoords="offset points")
ax.set_xlabel("營收成長 YoY (%)" if CJK else "Revenue YoY (%)")
ax.set_ylabel("EV / EBITDA (x)")
title = "AI 資料中心散熱 — 估值散佈(僅含有 EV/EBITDA 數值者)" if CJK else "AI DC Cooling - EV/EBITDA vs Growth"
ax.set_title(title, color=NAVY, fontsize=12, fontweight="bold")
sub = f"資料:capiq MCP · {len(pts)}/14 家有 EV/EBITDA(其餘 n/a 已排除)· 氣泡=市值 · mock/dev"
ax.text(0.0, -0.16, sub, transform=ax.transAxes, fontsize=8, color="#5A5A5A")
ax.grid(True, alpha=0.25, zorder=0)
fig.tight_layout()
p1 = os.path.join(OUT, "chart_valuation_scatter.png")
fig.savefig(p1, bbox_inches="tight"); plt.close(fig)

# --- 圖2:1年報酬長條(全 14 家,有數值者)---
bars = [(r["ticker"], num(r.get("ret_1y"))) for r in comps if num(r.get("ret_1y")) is not None]
bars.sort(key=lambda x: x[1], reverse=True)
fig, ax = plt.subplots(figsize=(9, 5), dpi=130)
labels = [b[0] for b in bars]
vals = [b[1]*100 for b in bars]
colors = [RED if v < 0 else (TEAL if labels[i] == "VRT" else ACCENT) for i, v in enumerate(vals)]
ax.bar(labels, vals, color=colors, edgecolor=NAVY, linewidth=0.5)
ax.axhline(0, color="#5A5A5A", linewidth=0.8)
ax.set_ylabel("1 年報酬 (%)" if CJK else "1Y Return (%)")
title2 = "AI 資料中心散熱 — 同業 1 年報酬" if CJK else "AI DC Cooling - 1Y Return"
ax.set_title(title2, color=NAVY, fontsize=12, fontweight="bold")
for i, v in enumerate(vals):
    ax.text(i, v + (8 if v >= 0 else -16), f"{v:+.0f}%", ha="center", fontsize=7.5)
ax.text(0.0, -0.22, "資料:capiq MCP get_comps · 14/14 家有 ret_1y · 綠=VRT/正,紅=負 · mock/dev",
        transform=ax.transAxes, fontsize=8, color="#5A5A5A")
plt.xticks(rotation=40, ha="right", fontsize=8)
ax.grid(True, axis="y", alpha=0.25)
fig.tight_layout()
p2 = os.path.join(OUT, "chart_1y_return.png")
fig.savefig(p2, bbox_inches="tight"); plt.close(fig)

print("SAVED", p1)
print("SAVED", p2)
print(f"scatter points (有 EV/EBITDA): {len(pts)}/14;  return bars: {len(bars)}/14;  CJK font: {CJK}")
