# -*- coding: utf-8 -*-
"""TSMC valuation football-field chart (scenario implied ADR vs market)."""
import os
os.makedirs("./out/charts", exist_ok=True)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
NAVY="#0B1F3A"; BLUE="#1F4E79"; ACCENT="#2E9BD6"; TEAL="#14A38C"; AMBER="#E89A1C"; RED="#C03A2B"; GREY="#8A97A6"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"figure.dpi":150,
                     "axes.grid":True,"grid.color":"#EAEDF1"})
scen=[("Bear",220.67,RED),("Base",340.19,ACCENT),("Bull",462.70,TEAL)]
fig,ax=plt.subplots(figsize=(7,3.4))
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False); ax.set_axisbelow(True)
ys=[0,1,2]
for y,(nm,v,c) in zip(ys,scen):
    ax.barh(y,v,color=c,height=0.55)
    ax.text(v+6,y,f"${v:.0f}",va="center",fontsize=9,fontweight="bold",color=NAVY)
ax.set_yticks(ys); ax.set_yticklabels([s[0] for s in scen])
ax.axvline(380,color=BLACK if False else "#333333",linestyle="--",linewidth=1.5)
ax.text(380,2.65,"Market ~$380",ha="center",fontsize=8,color="#333333",fontweight="bold")
ax.axvline(399,color=AMBER,linestyle=":",linewidth=1.4)
ax.text(399,-0.75,"BofA PT ~$399",ha="center",fontsize=8,color=AMBER)
ax.set_xlim(0,520); ax.set_xlabel("Implied value per ADR (US$)")
ax.set_title("TSMC DCF — Scenario Implied Value vs. Market (per ADR)",fontweight="bold",color=NAVY)
ax.text(0,-0.22,"WACC 9.95% fixed; scenarios vary growth/margin/capex/terminal-g. Net cash added back.",
        transform=ax.transAxes,fontsize=7,color=GREY)
fig.tight_layout(); fig.savefig("./out/charts/11_football.png",bbox_inches="tight"); plt.close(fig)
print("saved 11_football.png")
