# -*- coding: utf-8 -*-
"""VRT LBO IRR sensitivity heatmap: offer price x exit multiple (mcpBased run).

Single source of truth = the same LBO math written into the workbook, which is
built off pulled capiq FY26E EBITDA + flagged LBO assumptions. Mock / dev only.
"""
import os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
CHARTS=os.path.join(ROOT,"out","charts"); os.makedirs(CHARTS,exist_ok=True)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
NAVY="#0B1F3A"
# LBO params consistent with workbook (exit EBITDA / exit ND / debt from the same model)
exitE=5.45; exitND=3.08; debt=14.39; sh=0.3813; ndnow=2.0; fee=0.025
exits=[18,20,22,24,26]; offers=[320,360,400,440,480]
import numpy as np
M=np.zeros((len(offers),len(exits)))
for i,of in enumerate(offers):
    for j,m in enumerate(exits):
        spon=of*sh*(1+fee)+ndnow-debt
        ee=m*exitE-exitND
        M[i,j]=(ee/spon)**(1/5)-1
cmap=LinearSegmentedColormap.from_list("rg",["#C03A2B","#F4D58D","#14A38C"])
fig,ax=plt.subplots(figsize=(7.6,4.4))
im=ax.imshow(M,cmap=cmap,vmin=-0.12,vmax=0.10,aspect="auto")
ax.set_xticks(range(len(exits))); ax.set_xticklabels([f"{m}x" for m in exits])
ax.set_yticks(range(len(offers))); ax.set_yticklabels([f"${o}" for o in offers])
ax.set_xlabel("Exit EV/EBITDA"); ax.set_ylabel("Offer / share")
for i in range(len(offers)):
    for j in range(len(exits)):
        ax.text(j,i,f"{M[i,j]*100:.0f}%",ha="center",va="center",fontsize=9,
                color=("white" if abs(M[i,j])>0.07 else NAVY),fontweight="bold")
# highlight base $400/22x
ax.add_patch(plt.Rectangle((2-0.5,2-0.5),1,1,fill=False,edgecolor=NAVY,lw=2.5))
ax.set_title("VRT LBO 5yr IRR sensitivity (base $400 / 22x)  |  capiq+daloopa MCP (mock)",
             fontsize=10,color=NAVY,fontweight="bold",loc="left")
fig.colorbar(im,ax=ax,label="5yr IRR",fraction=0.046,pad=0.04)
fig.tight_layout()
out=os.path.join(CHARTS,"vrt_irr_heatmap.png"); fig.savefig(out,bbox_inches="tight"); print("saved",out)
