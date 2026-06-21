# -*- coding: utf-8 -*-
"""TSMC Q1-2026 earnings charts — built from MCP pulls (mock/dev).

3 張關鍵圖:
  1. beat/miss vs consensus(營收/毛利率/EPS)
  2. 平台別營收組合(daloopa,加總 = 100%)
  3. 技術節點別營收組合(daloopa,N3+N5+7nm = Advanced 74%)
資料源:../mcp_pulls/*.json(實際 MCP 拉回)。
"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
PULLS = os.path.normpath(os.path.join(HERE, "..", "mcp_pulls"))
CHARTS = os.path.normpath(os.path.join(HERE, "..", "out", "charts"))
os.makedirs(CHARTS, exist_ok=True)

# CJK font (fall back gracefully)
for cand in ["Microsoft JhengHei", "Microsoft YaHei", "PMingLiU", "DejaVu Sans"]:
    try:
        font_manager.findfont(cand, fallback_to_default=False)
        plt.rcParams["font.family"] = cand
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False

def load(name):
    with open(os.path.join(PULLS, name), encoding="utf-8") as f:
        return json.load(f)["result"]

fund = {r["metric"]: r["value"] for r in load("02_factset_fundamentals_TSM_Q1-2026.json")}
cons = {r["metric"]: r for r in load("04_factset_consensus_TSM_Q1-2026.json")}
plat = load("11_daloopa_TSM_mix_platform.json")
node = load("12_daloopa_TSM_mix_node.json")

NAVY = "#1F4E79"; AMBER = "#E0A800"; GREEN = "#2E7D32"; GREY = "#9BAFC4"

# ---- Chart 1: beat/miss vs consensus -------------------------------------
metrics = ["營收\n(US$bn)", "毛利率\n(%)", "EPS\n(NT$)"]
consensus_vals = [cons["revenue"]["consensus"], cons["gross_margin"]["consensus"]*100, cons["eps_ntd"]["consensus"]]
actual_vals = [fund["revenue"], fund["gross_margin"]*100, fund["eps"]]
fig, axes = plt.subplots(1, 3, figsize=(10, 4))
beat_labels = [f"+{actual_vals[0]/consensus_vals[0]-1:.1%}",
               f"+{(fund['gross_margin']-cons['gross_margin']['consensus'])*10000:.0f}bps",
               f"+{actual_vals[2]/consensus_vals[2]-1:.1%}"]
for ax, m, cv, av, bl in zip(axes, metrics, consensus_vals, actual_vals, beat_labels):
    bars = ax.bar(["市場預期", "實際"], [cv, av], color=[GREY, NAVY], width=0.6)
    ax.set_title(m, fontsize=11, fontweight="bold")
    ax.text(1, av, bl, ha="center", va="bottom", color=GREEN, fontweight="bold", fontsize=11)
    for b, v in zip(bars, [cv, av]):
        ax.text(b.get_x()+b.get_width()/2, v*0.5, f"{v:.2f}", ha="center", va="center", color="white", fontsize=9)
    ax.set_ylim(0, max(cv, av)*1.18)
    ax.spines[["top", "right"]].set_visible(False)
fig.suptitle("台積電 TSMC Q1'26:實際 vs. 市場預期(beat/miss)  [mock 資料]", fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(CHARTS, "01_beat_miss.png"), dpi=150)
plt.close(fig)

# ---- Chart 2: platform mix -----------------------------------------------
labels = [it["line_item"] for it in plat]
vals = [it["value"] for it in plat]
colors = [NAVY, AMBER, "#5B9BD5", GREEN, "#C55A11", GREY]
fig, ax = plt.subplots(figsize=(6.5, 5.5))
wedges, _, autotexts = ax.pie(vals, labels=labels, autopct=lambda p: f"{p:.0f}%",
                              colors=colors, startangle=90, counterclock=False,
                              wedgeprops=dict(width=0.42, edgecolor="white"))
for t in autotexts: t.set_color("white"); t.set_fontweight("bold"); t.set_fontsize=9
ax.set_title(f"Q1'26 平台別營收組合(daloopa,加總 {sum(vals):.0%})  [mock]", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "02_platform_mix.png"), dpi=150)
plt.close(fig)

# ---- Chart 3: node mix ---------------------------------------------------
nodes = {it["line_item"]: it["value"] for it in node}
order = ["3nm (N3)", "5nm (N5)", "7nm"]
nvals = [nodes[k] for k in order]
adv = nodes["Advanced (<=7nm)"]
fig, ax = plt.subplots(figsize=(7, 4.5))
bars = ax.bar(order, [v*100 for v in nvals], color=[NAVY, "#5B9BD5", AMBER], width=0.6)
for b, v in zip(bars, nvals):
    ax.text(b.get_x()+b.get_width()/2, v*100+0.6, f"{v:.0%}", ha="center", fontweight="bold")
ax.axhline(adv*100, color=GREEN, linestyle="--", linewidth=1.4)
ax.text(2.4, adv*100+0.6, f"Advanced <=7nm = {adv:.0%}", color=GREEN, fontweight="bold", ha="right")
ax.text(2.4, adv*100-3.2, f"(N3+N5+7nm = {sum(nvals):.0%}，對齊)", color=GREEN, ha="right", fontsize=9)
ax.set_ylabel("% wafer revenue")
ax.set_ylim(0, 80)
ax.set_title("Q1'26 技術節點別營收組合(daloopa)  [mock]", fontsize=12, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "03_node_mix.png"), dpi=150)
plt.close(fig)

print("SAVED charts:", os.listdir(CHARTS))
