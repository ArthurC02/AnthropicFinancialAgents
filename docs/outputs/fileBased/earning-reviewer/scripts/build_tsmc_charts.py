# -*- coding: utf-8 -*-
"""Generate charts for the TSMC Q1 2026 earnings update report."""
import os
os.makedirs("./out/charts", exist_ok=True)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

NAVY="#0B1F3A"; BLUE="#1F4E79"; ACCENT="#2E9BD6"; TEAL="#14A38C"; AMBER="#E89A1C"; RED="#C03A2B"; GREY="#8A97A6"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.edgecolor":"#CCCCCC",
                     "axes.grid":True,"grid.color":"#EAEdF1","grid.linewidth":0.8,"figure.dpi":150})
def style(ax):
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.set_axisbelow(True)
def save(fig,name):
    fig.tight_layout(); fig.savefig(f"./out/charts/{name}.png",bbox_inches="tight"); plt.close(fig)

Q=["Q1'25","Q2'25","Q3'25","Q4'25","Q1'26","Q2'26","Q3'26","Q4'26"]
rev=[25.53,30.07,32.0,33.73,35.90,39.60,42.77,45.33]
status=["A","A","A","A","A","G","E","E"]   # actual / guidance / estimate
gm=[58.5,58.6,59.5,62.3,66.2,66.5,65.5,65.0]
eps=[13.95,16.5,18.2,19.5,22.08,23.97,25.62,26.88]
colmap={"A":BLUE,"G":ACCENT,"E":GREY}

# 1. Quarterly revenue
fig,ax=plt.subplots(figsize=(7,3.6)); style(ax)
bars=ax.bar(Q,rev,color=[colmap[s] for s in status])
for b,v in zip(bars,rev): ax.text(b.get_x()+b.get_width()/2,v+0.4,f"{v:.1f}",ha="center",fontsize=8,fontweight="bold")
ax.set_ylabel("Revenue (US$ bn)"); ax.set_title("Quarterly Revenue — Q1'26 Actual, Q2'26 Guidance, H2'26E",fontweight="bold",color=NAVY)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=BLUE,label="Actual"),Patch(color=ACCENT,label="Guidance (Q2)"),Patch(color=GREY,label="Estimate")],
          frameon=False,fontsize=8,loc="upper left")
ax.text(0,-0.18,"2025 quarters approximate; Q1'26 & Q4'25 = reported actuals.",transform=ax.transAxes,fontsize=7,color=GREY)
save(fig,"01_revenue")

# 2. Gross margin trend
fig,ax=plt.subplots(figsize=(7,3.6)); style(ax)
ax.plot(Q,gm,marker="o",color=BLUE,linewidth=2.2)
ax.fill_between(Q,gm,min(gm)-2,color=ACCENT,alpha=0.08)
for x,v,s in zip(Q,gm,status):
    ax.text(x,v+0.5,f"{v:.1f}%",ha="center",fontsize=8,fontweight="bold",color=NAVY if s=="A" else GREY)
ax.axhspan(63,65,color=AMBER,alpha=0.10)
ax.text(0.5,64,"Q1'26 guide 63–65%",fontsize=7,color=AMBER)
ax.set_ylabel("Gross margin (%)"); ax.set_ylim(min(gm)-2,max(gm)+2.5)
ax.set_title("Gross Margin — 66.2% in Q1'26 beat top of guide by ~120bps",fontweight="bold",color=NAVY)
save(fig,"02_grossmargin")

# 3. Quarterly EPS
fig,ax=plt.subplots(figsize=(7,3.6)); style(ax)
bars=ax.bar(Q,eps,color=[colmap[s] for s in status])
for b,v in zip(bars,eps): ax.text(b.get_x()+b.get_width()/2,v+0.3,f"{v:.1f}",ha="center",fontsize=8,fontweight="bold")
ax.set_ylabel("Diluted EPS (NT$)"); ax.set_title("Quarterly EPS (NT$) — Q1'26 NT$22.08, +58% YoY",fontweight="bold",color=NAVY)
save(fig,"03_eps")

# 4. Platform mix
fig,ax=plt.subplots(figsize=(7,3.4)); style(ax)
plat=[("HPC",61),("Smartphone",26),("IoT",6),("Automotive",4),("DCE",1),("Other",2)]
names=[p[0] for p in plat][::-1]; vals=[p[1] for p in plat][::-1]
cols=[ACCENT if n=="HPC" else BLUE for n in names]
b=ax.barh(names,vals,color=cols)
for bb,v in zip(b,vals): ax.text(v+0.6,bb.get_y()+bb.get_height()/2,f"{v}%",va="center",fontsize=8,fontweight="bold")
ax.set_xlabel("% of Q1'26 revenue"); ax.set_title("Revenue by Platform — HPC 61% leads the mix",fontweight="bold",color=NAVY)
save(fig,"04_platform")

# 5. Node mix
fig,ax=plt.subplots(figsize=(7,3.4)); style(ax)
node=[("3nm (N3)",25),("5nm (N5)",36),("7nm",13),("≥10nm / mature",26)]
nm=[n[0] for n in node]; nv=[n[1] for n in node]
cols=[ACCENT,ACCENT,BLUE,GREY]
bars=ax.bar(nm,nv,color=cols)
for bb,v in zip(bars,nv): ax.text(bb.get_x()+bb.get_width()/2,v+0.5,f"{v}%",ha="center",fontsize=8,fontweight="bold")
ax.set_ylabel("% of wafer revenue"); ax.set_title("Revenue by Node — Advanced (≤7nm) = 74%",fontweight="bold",color=NAVY)
save(fig,"05_node")

# 6. Beat/miss revenue & EPS (Actual vs Consensus vs Prior guide)
fig,axes=plt.subplots(1,2,figsize=(7.2,3.4))
# revenue
ax=axes[0]; style(ax)
labels=["Prior\nguide-mid","Consensus","Actual"]; vals=[35.2,35.5,35.90]; cols=[GREY,AMBER,TEAL]
b=ax.bar(labels,vals,color=cols)
for bb,v in zip(b,vals): ax.text(bb.get_x()+bb.get_width()/2,v+0.05,f"{v:.2f}",ha="center",fontsize=8,fontweight="bold")
ax.set_ylim(34.5,36.3); ax.set_title("Q1'26 Revenue (US$bn)",fontsize=9,fontweight="bold",color=NAVY)
# eps
ax=axes[1]; style(ax)
vals=[20.88,22.08]; b=ax.bar(["Consensus","Actual"],vals,color=[AMBER,TEAL])
for bb,v in zip(b,vals): ax.text(bb.get_x()+bb.get_width()/2,v+0.1,f"{v:.2f}",ha="center",fontsize=8,fontweight="bold")
ax.set_ylim(20,23); ax.set_title("Q1'26 EPS (NT$) — +5.7% beat",fontsize=9,fontweight="bold",color=NAVY)
fig.suptitle("Beat vs. Consensus & Prior Guidance",fontweight="bold",color=NAVY,y=1.02)
save(fig,"06_beatmiss")

# 7. Q2 guide vs consensus
fig,ax=plt.subplots(figsize=(7,3.2)); style(ax)
b=ax.bar(["Consensus","Guidance\nmidpoint","Guidance\nhigh"],[38.1,39.6,40.2],color=[AMBER,TEAL,BLUE])
for bb,v in zip(b,[38.1,39.6,40.2]): ax.text(bb.get_x()+bb.get_width()/2,v+0.05,f"{v:.1f}",ha="center",fontsize=8,fontweight="bold")
ax.set_ylim(37,41); ax.set_ylabel("US$ bn")
ax.set_title("Q2'26 Revenue Guide ~4% Above Consensus",fontweight="bold",color=NAVY)
save(fig,"07_q2guide")

# 8. FY revenue & growth
fig,ax=plt.subplots(figsize=(7,3.6)); style(ax)
fy=["2024A","2025A~","2026E"]; fyrev=[90.1,121.3,163.6]; cols=[BLUE,BLUE,GREY]
b=ax.bar(fy,fyrev,color=cols)
for bb,v in zip(b,fyrev): ax.text(bb.get_x()+bb.get_width()/2,v+1.5,f"${v:.0f}b",ha="center",fontsize=8,fontweight="bold")
ax2=ax.twinx(); growth=[None,34.6,34.9]; ax2.plot(fy,growth,marker="o",color=AMBER,linewidth=2)
for x,g in zip(fy,growth):
    if g: ax2.text(x,g+1,f"+{g:.0f}%",ha="center",fontsize=8,color=AMBER,fontweight="bold")
ax2.set_ylim(0,55); ax2.set_ylabel("YoY growth (%)",color=AMBER); ax2.grid(False)
ax.set_ylabel("Revenue (US$ bn)"); ax.set_title("FY Revenue — FY26E '>30%' growth (AI-driven)",fontweight="bold",color=NAVY)
ax.text(0,-0.18,"2025/2026 approximate; FY26E built from Q1'26A + Q2'26 guide + H2'26E.",transform=ax.transAxes,fontsize=7,color=GREY)
save(fig,"08_fyrevenue")

# 9. Capex & intensity
fig,ax=plt.subplots(figsize=(7,3.6)); style(ax)
yrs=["2024A","2025A~","2026E"]; capex=[29.8,40.0,55.0]
b=ax.bar(yrs,capex,color=[BLUE,BLUE,RED])
for bb,v in zip(b,capex): ax.text(bb.get_x()+bb.get_width()/2,v+0.7,f"${v:.0f}b",ha="center",fontsize=8,fontweight="bold")
ax2=ax.twinx(); inten=[33,33,34]; ax2.plot(yrs,inten,marker="s",color=AMBER,linewidth=2)
for x,v in zip(yrs,inten): ax2.text(x,v+0.6,f"{v}%",ha="center",fontsize=8,color=AMBER,fontweight="bold")
ax2.set_ylim(0,45); ax2.set_ylabel("Capex intensity (% rev)",color=AMBER); ax2.grid(False)
ax.set_ylabel("Capex (US$ bn)"); ax.set_title("2026 Capex US$52–56bn (high end) — the sell-the-news trigger",fontweight="bold",color=NAVY)
save(fig,"09_capex")

# 10. Gross margin walk H2 dilution
fig,ax=plt.subplots(figsize=(7,3.6)); style(ax)
steps=["Q1'26\n66.2%","Util/\nmix","N2 ramp\ndilution","Overseas\ndilution","FY26E\n~65.8%"]
vals=[66.2,-0.2,-0.6,-0.4,65.8]
cum=66.2; xs=range(len(steps))
ax.bar(0,66.2,color=BLUE);
running=66.2
for i,(s,v) in enumerate(zip(steps[1:-1],vals[1:-1]),start=1):
    col=RED if v<0 else TEAL
    ax.bar(i,abs(v),bottom=running+ (v if v<0 else 0),color=col)
    running+=v
ax.bar(4,65.8,color=ACCENT)
ax.set_xticks(list(xs)); ax.set_xticklabels(steps,fontsize=8)
ax.set_ylim(63,67.5); ax.set_ylabel("Gross margin (%)")
ax.set_title("FY26E Gross Margin Walk — H2 N2 + overseas dilution (~2–3% FY)",fontweight="bold",color=NAVY)
ax.text(0,-0.2,"Illustrative; magnitudes per management commentary (N2+overseas ~2–3% FY dilution).",transform=ax.transAxes,fontsize=7,color=GREY)
save(fig,"10_gmwalk")

print("Charts saved to ./out/charts/", len(os.listdir("./out/charts")),"files")
