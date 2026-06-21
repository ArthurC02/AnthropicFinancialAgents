# -*- coding: utf-8 -*-
"""VRT football-field valuation chart."""
import os
os.makedirs("./out/charts", exist_ok=True)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
NAVY="#0B1F3A"; BLUE="#1F4E79"; ACCENT="#2E9BD6"; TEAL="#14A38C"; AMBER="#E89A1C"; RED="#C03A2B"; GREY="#9AA7B4"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"figure.dpi":150})

# (label, low, high, color)  ordered top->bottom visually
methods=[
 ("Analyst PT (illustrative)",300,450,GREY),
 ("52-wk range (illustrative)",130,400,GREY),
 ("Trading Comps (25-40x)",198,320,ACCENT),
 ("Precedent Txns (20-28x)",158,223,BLUE),
 ("DCF (perp / exit 22x)",100,245,TEAL),
 ("LBO ability-to-pay (25-20% IRR)",168,196,AMBER),
]
fig,ax=plt.subplots(figsize=(8.2,4.2))
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False); ax.spines["left"].set_visible(False)
ys=list(range(len(methods)))[::-1]
for y,(lab,lo,hi,c) in zip(ys,methods):
    ax.barh(y,hi-lo,left=lo,height=0.52,color=c,alpha=0.9)
    ax.text(lo-4,y,f"${lo}",va="center",ha="right",fontsize=8,color="#333")
    ax.text(hi+4,y,f"${hi}",va="center",ha="left",fontsize=8,color="#333",fontweight="bold")
ax.set_yticks(ys); ax.set_yticklabels([m[0] for m in methods],fontsize=9)
ax.axvline(320,color=RED,linestyle="--",linewidth=1.6)
ax.text(320,len(methods)-0.3,"Current $320",ha="center",fontsize=8.5,color=RED,fontweight="bold")
ax.axvline(400,color="#222222",linestyle=":",linewidth=1.5)
ax.text(400,-0.85,"Illustrative offer $400 (+25%)",ha="center",fontsize=8,color="#222")
ax.set_xlim(60,480); ax.set_xlabel("Implied value per share (US$)")
ax.set_title("Vertiv (VRT) — Valuation Football Field",fontweight="bold",color=NAVY,fontsize=13)
ax.text(0,-0.16,"Intrinsic (DCF), precedent-txn and LBO methods cluster $158–$245 (DCF low tail $100) — below the $320 market price. "
        "A control premium (→$400) is reached only by sentiment-based references.",
        transform=ax.transAxes,fontsize=7.5,color=GREY)
ax.grid(axis="x",color="#EEF1F4"); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig("./out/charts/vrt_football.png",bbox_inches="tight"); plt.close(fig)
print("saved vrt_football.png")
