# 🎯 投行提案（pitch-agent）— 執行紀錄

## 安裝與初始指令

```text
❯ /plugin install pitch-agent@fsi-local
  ⎿  ✓ Installed pitch-agent. Run /reload-plugins to apply.
```

> 使用者：幫我對 Vertiv（VRT）做一份併購提案初稿：拉同業比較與先例交易、建 DCF 與示意 LBO、做一張足球場估值區間圖，最後填進提案簡報

你裝了 pitch-agent。我來做 Vertiv (VRT) 併購提案初稿:同業比較 + 先例交易 + DCF + 示意 LBO + 足球場估值圖 → 提案簡報。

先說明框架假設(初稿):以「潛在收購方評估收購 VRT」角度,DCF/comps/先例交易為策略買方視角、LBO 為財務買方(PE)視角。先抓先例交易資料並載入 LBO skill,DCF 可沿用先前已建好的 VRT 模型。

## 研究與技能載入

```text
● Agent(Research cooling M&A precedents)
  ⎿  Done (15 tool uses · 48.3k tokens · 2m 11s)

● Skill(pitch-agent:lbo-model)
  ⎿  Successfully loaded skill
```

先例交易資料齊全(來源完整)。我先用 Python 把所有估值法的區間算準(含 LBO 與 ability-to-pay),確保足球場圖、Excel、簡報三者一致。

## 估值區間試算

```bash
cd "<repo>" && python - <<'PY'
px=320.0; sh=0.382; nd=1.9; mcap=px*sh; EV=mcap+nd…
PY
```

```text
mcap $122.2B EV $124.1B | FY26E EBITDA $3.11B | fwd EV/EBITDA 40x

COMPS (25-40x FY26E EBITDA): $198 - $320
… +10 lines (ctrl+o to expand)
```

LBO ability-to-pay($162–$189)遠低於現價 $320——這就是提案的核心張力。先精算我將寫進工作簿的完整 LBO(含掃債),取得驗證數字作為單一真實來源。

```bash
cd "<repo>" && python - <<'PY'
sh=0.382; nd0=1.9; offer=400.0; tax=0.21; rate=0.08; lev=6.0…
PY
```

```text
Entry EBITDA $3.11B | debt $18.64B | sponsor equity $139.9B | uses $158.5B
Exit FY31 EBITDA $6.86B, end net debt $5.89B
Exit EV (22x) $151.0B | exit equity $145.1B
… +4 lines (ctrl+o to expand)
```

LBO 確認:示意報價 $400(+25%)→ MOIC 1.04x、IRR 0.7%(不可行);ability-to-pay(20–25% IRR)= $168–$196,遠低於現價 $320。這就是提案核心。現在建併購估值工作簿(含活公式 LBO)。

## 建立估值工作簿

```text
● Write(build_vrt_ma.py)
  ⎿  Wrote 222 lines to build_vrt_ma.py
```

```python
# -*- coding: utf-8 -*-
"""Vertiv (VRT) M&A proposal — valuation workbook: Comps, Precedents, DCF summary,
illustrative LBO (live formulas), Football Field summary."""
import os
os.makedirs("./out", exist_ok=True)
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter
# … +212 lines (ctrl+o to expand)
```

```bash
cd "<repo>" && python build_vrt_ma.py 2>&1
```

```text
SAVED ./out/VRT_MA_Valuation.xlsx  sheets: ['Football Field', 'LBO', 'Comps', 'Precedent Txns', 'DCF Summary']
```

工作簿完成(5 分頁,LBO 為活公式)。現在做足球場估值圖。

## 足球場估值圖

```text
● Write(build_vrt_football.py)
  ⎿  Wrote 38 lines to build_vrt_football.py
```

```python
# -*- coding: utf-8 -*-
"""VRT football-field valuation chart."""
import os
os.makedirs("./out/charts", exist_ok=True)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
NAVY="#0B1F3A"; BLUE="#1F4E79"; ACCENT="#2E9BD6"; TEAL="#14A38C"; AMBER="#E89A1C"; RED="#C03A2B"; GREY="#9AA7B4"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"figure.dpi":150})

# (label, low, high, color)  ordered top->bottom visually
# … +28 lines (ctrl+o to expand)
```

```bash
cd "<repo>" && python build_vrt_football.py 2>&1
```

```text
saved vrt_football.png
```

足球場圖完成。最後組裝提案簡報 PPTX。

## 組裝提案簡報 PPTX

```text
● Write(build_vrt_pitch.py)
  ⎿  Wrote 213 lines to build_vrt_pitch.py
```

```python
# -*- coding: utf-8 -*-
"""Vertiv (VRT) M&A proposal deck (first draft)."""
import os
os.makedirs("./out", exist_ok=True)
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
# … +203 lines (ctrl+o to expand)
```

```bash
cd "<repo>" && python build_vrt_pitch.py 2>&1 && echo "---" && ls -la out/VRT_M*.pptx out/VRT_MA_Valuation.xlsx out/charts/vr…
```

```text
SAVED ./out/VRT_M&A_Proposal_Draft.pptx slides: 10
---
84129 out/charts/vrt_football.png
… +2 lines (ctrl+o to expand)
```

## 初稿交付清單

全部完成 ✅。Vertiv 併購提案初稿交付清單(out\\):

| 交付物 | 檔案 | 內容 |
| --- | --- | --- |
| 提案簡報 | VRT_M&A_Proposal_Draft.pptx | 10 頁:封面 → 框架/聲明 → 執行摘要 → 標的快照 → 足球場圖 → Comps → 先例交易 → DCF → 示意 LBO → 結論/後續 |
| 估值工作簿 | VRT_MA_Valuation.xlsx | 5 分頁:Football Field、LBO(活公式+掃債+ability-to-pay)、Comps、Precedent Txns、DCF Summary |
| 足球場圖 | out/charts/vrt_football.png | 6 法估值區間 vs 現價/報價 |

足球場估值區間(每股 US$)

| 方法 | 區間 |
| --- | --- |
| 同業比較(25–40x) | $198–$320 |
| 先例交易(20–28x) | $158–$223 |
| DCF(永續/出場22x) | $100–$245 |
| LBO ability-to-pay(25–20% IRR) | $168–$196 |
| 現價 / 示意報價 | $320 / $400(+25%) |

### 核心結論(誠實、未粉飾)

策略誘人、估值是硬傷。 內在(DCF)、先例交易、LBO ability-to-pay 三法一致群聚 $158–$245,全部低於現價 $320。意涵:收購 VRT = 對「已偏貴的價格」再付控制溢價,只有情緒類參考(52週高、樂觀 PT)能觸及 $400。

示意 LBO 證明不可行:$400 報價下進場 ~50x EBITDA、發起人須寫 ~$140bn 股權、MOIC 1.04x / IRR ~0.7%;要達 20–25% IRR,進場價需 $168–$196(現價的 4–5 折)。

建議方向:① 暫不推進全額收購;② 改採少數股權/合資/可轉換結構;③ 列入觀察、設估值修正觸發(EV/EBITDA 回 ~25–30x);④ 平行評估較便宜的純標的(Auras 3324、AVC 3017、私有液冷資產)。

### 兩個提醒

- 框架假設(已寫進簡報第 2 頁):以「收購方評估收購 VRT」為視角,示意報價 $400(+25% 溢價)。
- 數據待校正:現價/股數/淨負債/EBITDA、同業與交易倍數均為第三方/估計值;先例交易已附來源但須以 FactSet/Bloomberg 與申報文件核實。LBO 因 VRT ~$122bn 規模實務不可行,僅作報酬數學示範(簡報已標註)。

需要的話我可以:建綜效情境(策略買方若有成本/營收綜效可上修 ability-to-pay)、把 LBO 加 5×5 IRR 敏感度表、或用 ib-check-deck 對這份簡報做一次客戶前數字一致性檢查。

## 第二輪：綜效情境 + 5×5 IRR 敏感度 + 一致性檢查

> 使用者：執行

「執行」= 把我提的三項都做:① LBO 加綜效情境、② 加 5×5 IRR 敏感度表、③ 用 ib-check-deck 檢查簡報數字一致性。

先在工作簿加綜效 ability-to-pay 與 IRR 敏感度表。

```text
● Update(build_vrt_ma.py)
  ⎿  Added 44 lines
```

```python
# ============================ Synergies & Sensitivity ============================
sy=sheet("Synergies & Sensitivity")
sy.merge_cells("A1:H1"); sy["A1"]="綜效 Ability-to-Pay 與 IRR 敏感度（連結 LBO 分頁）"; sy["A1"].font=Fh(12); sy["A1"].fill=fill(HDR)
sy["A1"].alignment=Alignment(horizontal="left",vertical="center")
sy.merge_cells("A2:H2"); sy["A2"]="US$bn(每股除外)| 綠=連結 LBO | 假設:出場淨負債保守維持基準(不計綜效額外掃債)"; sy["A2"].font=Ff(8)
sy["A2"].alignment=Alignment(horizontal="left",vertical="center")

# Synergy ability-to-pay @ target IRR
hdr(sy,"A4:F4","綜效 Ability-to-Pay（@ 20% IRR,出場 22x）")
W(sy,"A5","綜效(run-rate, $bn)",Ff(9,True),al=CEN,fl=SUB); W(sy,"B5","出場EBITDA",Ff(9,True),al=CEN,fl=SUB)
W(sy,"C5","出場股權",Ff(9,True),al=CEN,fl=SUB); W(sy,"D5","進場股權@20%",Ff(9,True),al=CEN,fl=SUB)
W(sy,"E5","進場EV",Ff(9,True),al=CEN,fl=SUB); W(sy,"F5","每股 $",Ff(9,True),al=CEN,fl=SUB)
for r,S in enumerate([0,0.5,1.0,1.5,2.0]):
    rr=6+r
    W(sy,f"A{rr}",S,Fi(),USD,al=CEN,fl=INP)
    W(sy,f"B{rr}",f"=LBO!$H$21+A{rr}",Ff(),USD,al=CEN)   # exit EBITDA + synergy
    W(sy,f"C{rr}",f"=B{rr}*LBO!$B$14-LBO!$H$31",Ff(),USD,al=CEN)  # exit equity
    W(sy,f"D{rr}",f"=C{rr}/(1+0.2)^5",Ff(),USD,al=CEN)
    W(sy,f"E{rr}",f"=D{rr}+LBO!$H$6",Ff(),USD,al=CEN)
    W(sy,f"F{rr}",f"=(E{rr}-LBO!$B$8)/LBO!$B$7",Ff(10,True),SH2,al=CEN,fl=(OUT if r==2 else WHITE))
W(sy,"A12","解讀:即使綜效 $2.0bn(≈進場 EBITDA 的 64%),@20% IRR 的進場價仍僅 ~$243,低於現價 $320。",Ff(9,True),al=LEF)
sy.merge_cells("A12:F12")
W(sy,"A13","反推:要在 20% IRR 下 justify $320,需 run-rate 綜效約 $5.3bn(≈進場 EBITDA 1.7 倍)——不切實際。",Ff(9,True),al=LEF)
sy.merge_cells("A13:F13")

# 5x5 IRR sensitivity: offer price x exit multiple (centered 400 / 22x)
hdr(sy,"A15:H15","IRR 敏感度:報價/股 × 出場 EV/EBITDA（中心=基準 $400 / 22x）")
W(sy,"A16","報價↓ / 倍數→",Ff(9,True),al=CEN,fl=SUB)
exits=[18,20,22,24,26]
for j,m in enumerate(exits): W(sy,f"{get_column_letter(2+j)}16",m,Fi(9),MULT,al=CEN,fl=SUB)
offers=[320,360,400,440,480]
for i,of in enumerate(offers):
    rr=17+i; W(sy,f"A{rr}",of,Fi(9),SH0,al=CEN,fl=SUB)
    for j,m in enumerate(exits):
        col=get_column_letter(2+j)
        # sponsor equity = offer*shares*(1+fee)+netdebt-debt ; exit equity = m*exitEBITDA - exitND
        f=(f"=(({m}*LBO!$H$21-LBO!$H$31)/($A{rr}*LBO!$B$7*(1+LBO!$B$13)+LBO!$B$8-LBO!$H$6))^(1/5)-1")
        ctr=(i==2 and j==2)
        W(sy,f"{col}{rr}",f,Ff(10,ctr),PCT,al=CEN,fl=(OUT if ctr else (INP if (i+j)%2 else WHITE)))
W(sy,"A23","中心格($400/22x)應≈LBO 分頁 IRR(~0.7%)。即便出場 26x + 報價降至 $320,IRR 仍遠低於 PE 門檻(~20–25%)。",Ff(8),al=LEF)
sy.merge_cells("A23:H24")
sy.column_dimensions["A"].width=16
for c in "BCDEFGH": sy.column_dimensions[c].width=12

if "Sheet" in wb.sheetnames: wb.remove(wb["Sheet"])
wb.save("./out/VRT_MA_Valuation.xlsx")
print("SAVED ./out/VRT_MA_Valuation.xlsx  sheets:", wb.sheetnames)
```

```bash
cd "<repo>" && python build_vrt_ma.py 2>&1 && python - <<'PY'
# validate synergy ability-to-pay and IRR sensitivity center…
PY
```

```text
SAVED ./out/VRT_MA_Valuation.xlsx  sheets: ['Football Field', 'LBO', 'Comps', 'Precedent Txns', 'DCF Summary', 'Synergies & Sensitivity']
Synergy ability-to-pay @20%:  {'$0b': 196, '$0.5b': 208, '$1.0b': 220, '$1.5b': 231, '$2.0b': 243}
IRR center (400,22x) = 0.73%  (LBO base ~0.7%)
IRR (320,26x) = 9.7% | (480,18x) = -7.2%
```

綜效與敏感度驗證通過(中心 0.73% ✓;即便 $320/26x,IRR 僅 9.7%)。把綜效發現補進簡報 LBO 頁,再跑一致性檢查。

```text
● Update(build_vrt_pitch.py)
  ⎿  Added 5 lines, removed 4 lines
```

```python
  ["25% IRR","~$168"],
  ["現價(對照)","$320"]],
 [Inches(3.3),Inches(2.0)],rowh=Inches(0.44),fs=11)
txt(s,Inches(0.55),Inches(5.2),Inches(12.3),Inches(1.5),
    [[("解讀(含綜效情境)",13,True,NAVY)],
     [("• 示意 $400 報價 IRR ~0–1%(進場 ~50x、槓桿空間極小、發起人需寫 ~$140bn 股權)。要達 20–25% IRR 進場價需 ~$168–$196。",12,False,DARK)],
     [("• 綜效情境(@20% IRR):綜效 $0 → $196;$1.0bn → $220;$2.0bn → $243——即便 $2bn 綜效(≈進場 EBITDA 64%)仍 < 現價 $320。",12,False,DARK)],
     [("• 反推:要 justify $320 需 run-rate 綜效 ~$5.3bn(不切實際)。完整綜效表與 5×5 IRR 敏感度見工作簿 Synergies 分頁。",12,True,RED)]],line_sp=1.16)

# 10 CONCLUSION
s=prs.slides.add_slide(BLANK); header(s,"RECOMMENDATION & NEXT STEPS","結論、風險與後續",10)
```

```bash
cd "<repo>" && python build_vrt_pitch.py 2>&1
```

```text
SAVED ./out/VRT_M&A_Proposal_Draft.pptx slides: 10
```

### ③ 載入 QC 技能並跑一致性檢查

```text
● Skill(pitch-agent:ib-check-deck)
  ⎿  Successfully loaded skill
```

我來抽取簡報每頁文字,寫成 markdown,再跑數字一致性腳本。

```bash
cd "<repo>" && python - <<'PY'
from pptx import Presentation…
PY
```

```text
wrote /tmp/deck_content.md 156 lines
extract_numbers.py
```

```bash
cd "<repo>" && python "plugins/agent-plugins/pitch-agent/skills/ib-check-deck/scripts/extract_numbers.py" /tmp/deck_content.m…
```

```text
Error: File not found: <temp>/deck_content.md
```

路徑在 Windows/Git-Bash 間不一致,改用本地相對路徑。

```bash
cd "<repo>" && python - <<'PY'
from pptx import Presentation…
PY
```

```text
ok
Traceback (most recent call last):
  File "<repo>\plugins\agent-plugins\pitch-agent\skills\ib-check-deck\scripts\extract_numbers.py", line 305, in <module>
… +8 lines (ctrl+o to expand)
```

腳本以系統 cp950 編碼讀檔,遇中文失敗。用 PYTHONUTF8=1 強制 UTF-8。

```bash
cd "<repo>" && PYTHONUTF8=1 python "plugins/agent-plugins/pitch-agent/skills/ib-check-deck/scripts/extract_numbers.py" "./out…
```

```text
=== POTENTIAL INCONSISTENCIES DETECTED ===

Category: EBITDA
… +116 lines (ctrl+o to expand)
```

自動腳本的分類很粗(把所有「x 倍數」「%」各併成一類),因此那些 high/medium 多為誤報——不同公司/不同估值法本來就有不同倍數與成長率。我改用人工逐項核對關鍵重複數字,只找到一個值得修的真實項目。

人工一致性核對結果:

- 現價 $320、報價 $400(+25%)、VRT EV/EBITDA ~40x/51x、FY25 營收 $10.84bn(+28%)、FY26E $13.75bn、FY26E EBITDA $3.1bn、LBO MOIC 1.04x / IRR 0.7%、ability-to-pay $168–$196、Comps $198–$320、先例 $158–$223 — 跨頁全部一致 ✓
- 唯一真實問題(Important):封面/摘要/足球場頁的標題寫公允值「$158–$245」,但 DCF 低端其實達 $100(DCF 頁與足球場圖都顯示 $100)。標題與視覺不完全對齊。

我來修這一項(標註 DCF 低端 $100),保持三頁與圖一致。

```bash
cd "<repo>" && python - <<'PY'
import re,io…
PY
```

```text
patched
saved vrt_football.png
SAVED ./out/VRT_M&A_Proposal_Draft.pptx slides: 10
```

### 第二輪結果

三項都執行完畢 ✅

#### ① + ② LBO 強化（VRT_MA_Valuation.xlsx 新增 Synergies & Sensitivity 分頁）

綜效 ability-to-pay(@20% IRR,活公式連結 LBO 分頁):

| Run-rate 綜效 | $0 | $0.5bn | $1.0bn | $1.5bn | $2.0bn |
| --- | --- | --- | --- | --- | --- |
| 進場價/股 | $196 | $208 | $220 | $231 | $243 |

即便 $2bn 綜效(≈進場 EBITDA 的 64%),進場價仍僅 ~$243 < 現價 $320。反推:要 justify $320 需 ~$5.3bn 綜效(進場 EBITDA 的 1.7 倍,不切實際)。

5×5 IRR 敏感度(報價 × 出場倍數,中心 $400/22x = 0.73% ✓): 即便報價降至 $320 + 出場 26x,IRR 也只有 9.7%,遠低於 PE 20–25% 門檻。

#### ③ 簡報數字一致性檢查（ib-check-deck）

- 自動腳本:把所有倍數/百分比各併成單一類別,故 high/medium 旗標幾乎全是誤報(不同公司、不同估值法本來就不同)。已說明其侷限。
- 人工逐項核對:現價 $320、報價 $400、EV/EBITDA 40x/51x、FY25 $10.84bn、FY26E $13.75bn / EBITDA $3.1bn、MOIC 1.04x、IRR 0.7%、ability-to-pay $168–$196、Comps $198–$320、先例 $158–$223 — 跨頁全部一致。
- 找到並修正 1 項(Important):封面/摘要/足球場頁標題的「公允值 $158–$245」與 DCF 視覺低端 $100 未對齊 → 已三頁 + 圖一併補上「(DCF 低端 $100)」。無 Critical。

Vertiv 併購提案最終交付(out\\):

- VRT_M&A_Proposal_Draft.pptx — 10 頁(已修正一致性)
- VRT_MA_Valuation.xlsx — 6 分頁(Football Field、LBO、Comps、Precedent Txns、DCF Summary、Synergies & Sensitivity)
- out/charts/vrt_football.png — 足球場圖(已更新)

一句話結論不變:VRT 是最優質的 AI 散熱資產,但收購經濟學不成立——內在/交易/LBO 三法即便加上慷慨綜效仍低於現價 $320。建議走少數股權/合資/結構性方案,或等估值修正。

需要的話我可以把 Synergies 的 5×5 IRR 表也畫成熱力圖貼進簡報,或對整套檔案做最後打包。

## 第三輪：IRR 熱力圖 + 打包

> 使用者：執行

「執行」= 把 5×5 IRR 表畫成熱力圖貼進簡報,並打包整套檔案。先做熱力圖。

```text
● Write(build_vrt_heatmap.py)
  ⎿  Wrote 33 lines to build_vrt_heatmap.py
```

```python
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
# … +23 lines (ctrl+o to expand)
```

```bash
cd "<repo>" && python build_vrt_heatmap.py 2>&1
```

```text
saved vrt_irr_heatmap.png
```

Now insert the heatmap slide into the deck (after the LBO slide) and renumber the conclusion to slide 11.

```text
● Update(build_vrt_pitch.py)
  ⎿  Added 15 lines, removed 2 lines
```

```python
     [("• 綜效情境(@20% IRR):綜效 $0 → $196;$1.0bn → $220;$2.0bn → $243——即便 $2bn 綜效(≈進場 EBITDA 64%)仍 < 現價 $320。",12,False,DARK)],
     [("• 反推:要 justify $320 需 run-rate 綜效 ~$5.3bn(不切實際)。完整綜效表與 5×5 IRR 敏感度見工作簿 Synergies 分頁。",12,True,RED)]],line_sp=1.16)

# 10 IRR HEATMAP
s=prs.slides.add_slide(BLANK); header(s,"LBO SENSITIVITY","LBO IRR 敏感度:報價 × 出場倍數",10)
s.shapes.add_picture("./out/charts/vrt_irr_heatmap.png",Inches(0.6),Inches(1.4),width=Inches(8.4))
txt(s,Inches(9.2),Inches(1.5),Inches(3.8),Inches(5.2),
    [[("讀法",14,True,NAVY)],
     [("• 縱軸=報價/股,橫軸=出場 EV/EBITDA;格內為 5 年 IRR。",11,False,DARK)],
     [("• 基準($400 / 22x,框線)= ~0.7% IRR。",11,True,RED)],
     [("• 整張表無任一組合達 PE 門檻(~20–25%)。",11,False,DARK)],
     [("• 即便報價降至 $320 + 出場 26x,IRR 也僅 ~10%。",11,False,DARK)],
     [("",6,False,DARK)],
     [("意涵",13,True,NAVY)],
     [("LBO 報酬對『進場價』高度敏感,但 VRT 在現價附近的進場根本無法產生 PE 等級報酬——財務買方路徑不通。",11,True,BLUE)]],line_sp=1.16)

# 11 CONCLUSION
s=prs.slides.add_slide(BLANK); header(s,"RECOMMENDATION & NEXT STEPS","結論、風險與後續",11)
txt(s,Inches(0.55),Inches(1.45),Inches(6.1),Inches(5.2),
    [[("建議",14,True,NAVY)],
     [("① 暫不推進對 VRT 的全額現金收購——估值缺口過大。",12,False,DARK)],
```

```text
● Update(build_vrt_pitch.py)
  ⎿  Added 2 lines
```

```python
    [[("免責:初稿,示意性,非投資建議或要約;財務數字為估計值,須獨立查核。",10,True,GREY)]])

prs.save("./out/VRT_M&A_Proposal_Draft.pptx")
import os as _os
_os.remove("./out/deck_content.md") if _os.path.exists("./out/deck_content.md") else None
print("SAVED ./out/VRT_M&A_Proposal_Draft.pptx slides:",len(prs.slides._sldIdLst))
```

```bash
cd "<repo>" && python build_vrt_pitch.py 2>&1 && echo "--- packaging ---" && rm -f out/deck_content.md && python - <<'PY'
imp…
PY
```

```text
SAVED ./out/VRT_M&A_Proposal_Draft.pptx slides: 11
--- packaging ---
zipped -> out/FSI_Deliverables_2026-06-18.zip
… +5 lines (ctrl+o to expand)
```

打包完成,但 *.docx 沒列出來——讓我確認 out/ 完整內容(先前的 TSMC docx 應該還在)。

```bash
cd "<repo>" && echo "=== out/ files ===" && ls -la out/ | awk '{print $5, $9}' && echo "=== zip contents ===" && python -c "i…
```

```text
=== out/ files ===

0 .
… +10 lines (ctrl+o to expand)
```

out/ 裡先前的檔案(散熱簡報/comps/DCF、TSMC 全套)都不見了——只剩這次的 VRT 檔案與兩張 VRT 圖。先前那些是未追蹤檔,在某個環節被清掉了。好消息是建構腳本都還在,我可以全部重生。先確認腳本在位:

```bash
cd "<repo>" && ls -la build_*.py 2>&1 | awk '{print $9}'
```

```text
build_vrt_football.py
build_vrt_heatmap.py
build_vrt_ma.py
build_vrt_pitch.py
```

兩項都執行了,但發現一個重要狀況必須如實告知:

✅ 已完成
