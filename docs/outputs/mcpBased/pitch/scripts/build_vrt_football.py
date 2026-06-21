# -*- coding: utf-8 -*-
"""VRT football-field valuation chart (mcpBased run).

Bands are the same ones written into the workbook Football Field sheet, all
traceable to mcp_pulls/ + flagged assumptions. Mock / dev only.
"""
import os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
CHARTS=os.path.join(ROOT,"out","charts"); os.makedirs(CHARTS,exist_ok=True)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
NAVY="#0B1F3A"; BLUE="#1F4E79"; ACCENT="#2E9BD6"; TEAL="#14A38C"; AMBER="#E89A1C"; RED="#C03A2B"; GREY="#9AA7B4"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"figure.dpi":150})

PRICE=320; OFFER=400
# (label, low, high, color)  top->bottom
bands=[
 ("52-wk range (pulled)",80,340,GREY),
 ("Comps 25-40x FY26E EBITDA",152,246,BLUE),
 ("DCF (perp / 22x exit)",97,191,TEAL),
 ("LBO ability-to-pay (25-20% IRR)",133,156,AMBER),
 ("Synergy ATP @20% IRR ($0-2bn)",156,202,ACCENT),
]
fig,ax=plt.subplots(figsize=(9.4,4.4))
ys=list(range(len(bands)))[::-1]
for y,(lab,lo,hi,col) in zip(ys,bands):
    ax.barh(y,hi-lo,left=lo,height=0.55,color=col,alpha=0.85,edgecolor="white")
    ax.text(lo-4,y,f"${lo}",va="center",ha="right",fontsize=8,color=NAVY)
    ax.text(hi+4,y,f"${hi}",va="center",ha="left",fontsize=8,color=NAVY)
ax.axvline(PRICE,color=RED,lw=2,ls="-"); ax.text(PRICE-4,len(bands)-0.75,f"Current ${PRICE}",color=RED,fontsize=9,fontweight="bold",ha="right")
ax.axvline(OFFER,color=NAVY,lw=1.6,ls="--"); ax.text(OFFER+4,len(bands)-0.75,f"Offer ${OFFER}",color=NAVY,fontsize=9,ha="left")
ax.set_yticks(ys); ax.set_yticklabels([b[0] for b in bands],fontsize=9)
ax.set_xlim(40,430); ax.set_ylim(-0.6,len(bands)-0.2); ax.set_xlabel("Implied value per share (US$)")
ax.set_title("Vertiv (VRT) — Football Field  |  source: capiq + daloopa MCP (mock)",fontsize=11,color=NAVY,fontweight="bold",loc="left",pad=12)
for s in ("top","right"): ax.spines[s].set_visible(False)
ax.grid(axis="x",color="#E6EAEF"); ax.set_axisbelow(True)
fig.tight_layout()
out=os.path.join(CHARTS,"vrt_football.png"); fig.savefig(out,bbox_inches="tight"); print("saved",out)
