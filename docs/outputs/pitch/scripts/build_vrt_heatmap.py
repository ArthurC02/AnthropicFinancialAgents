# -*- coding: utf-8 -*-
"""VRT LBO IRR sensitivity heatmap: offer price x exit multiple."""
import os
os.makedirs("./out/charts", exist_ok=True)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
NAVY="#0B1F3A"
# LBO params (single source of truth, matches workbook)
exitE=6.86; exitND=5.89; debt=18.64; sh=0.382; ndnow=1.9; fee=0.025
offers=[320,360,400,440,480]; exits=[18,20,22,24,26]
def irr(of,m):
    spon=of*sh*(1+fee)+ndnow-debt; exiteq=m*exitE-exitND
    return (exiteq/spon)**(1/5)-1
grid=[[irr(of,m) for m in exits] for of in offers]
fig,ax=plt.subplots(figsize=(7.4,4.0))
cmap=LinearSegmentedColormap.from_list("rg",["#C0392B","#E8A317","#F2E394","#86C28B","#14A38C"])
im=ax.imshow(grid,cmap=cmap,vmin=-0.10,vmax=0.30,aspect="auto")
ax.set_xticks(range(len(exits))); ax.set_xticklabels([f"{m}x" for m in exits])
ax.set_yticks(range(len(offers))); ax.set_yticklabels([f"${o}" for o in offers])
ax.set_xlabel("Exit EV/EBITDA"); ax.set_ylabel("Offer price / share")
for i in range(len(offers)):
    for j in range(len(exits)):
        v=grid[i][j]
        ax.text(j,i,f"{v:+.0%}",ha="center",va="center",fontsize=10,fontweight="bold",
                color="#111" if -0.02<v<0.22 else "white")
# highlight base 400/22 (i=2,j=2)
ax.add_patch(plt.Rectangle((1.5,1.5),1,1,fill=False,edgecolor=NAVY,linewidth=2.5))
ax.set_title("VRT Illustrative LBO — 5Y IRR Sensitivity (Offer × Exit Multiple)",fontweight="bold",color=NAVY,fontsize=12)
ax.text(0,-0.32,"Base case $400 / 22x (boxed) = ~0.7% IRR. PE return threshold ~20–25% reached at none of these combinations.",
        transform=ax.transAxes,fontsize=7.5,color="#8A97A6")
fig.tight_layout(); fig.savefig("./out/charts/vrt_irr_heatmap.png",bbox_inches="tight",dpi=150); plt.close(fig)
print("saved vrt_irr_heatmap.png")
