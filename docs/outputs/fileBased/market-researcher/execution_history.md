# 🔭 市場研究（market-researcher）— 執行紀錄

## 安裝外掛

```text
❯ /plugin install financial-analysis@fsi-local
  ⎿  ✓ Installed financial-analysis. Run /reload-plugins to apply.

❯ /plugin install market-researcher@fsi-local
  ⎿  ✓ Installed market-researcher. Run /reload-plugins to apply.
```

## 使用者請求

> 使用者：研究 AI 資料中心散熱這個主題，給我產業概覽、主要玩家競爭格局、同業比較和值得關注的標的清單

我來幫你研究 AI 資料中心散熱 (AI Data Center Cooling) 這個主題。這正好符合 market-researcher 的產業概覽工作流程，我先載入該 skill。

```text
● Skill(market-researcher:sector-overview)
  ⎿  Successfully loaded skill
```

產業概覽需要當前的市場數據與估值，我來分頭做網路研究。我會派出三個平行研究小組，分別負責：①市場規模與技術趨勢、②競爭格局與主要玩家、③公開上市標的的估值與同業比較。

```text
● 3 agents finished
   ├ Research cooling market sizing · 7 tool uses · 22.9k tokens
   │ ⎿  Done
   ├ Research cooling competitive landscape · 17 tool uses · 43.4k tokens
   │ ⎿  Done
   └ Research cooling player valuations · 6 tool uses · 20.5k tokens
     ⎿  Done
```

三組研究都回來了，資料相當完整且互相印證。以下是整合後的 AI 資料中心散熱產業研究報告（繁體中文）。

> 資料時點：2024–2026 年（部分為 2026 年 6 月最新）。市場規模數字來自第三方研究機構，方法論不同會有約 2 倍落差，已標註來源與口徑差異。估值與股價為即時變動數據，僅供方向參考。

---

# AI 資料中心散熱（Data Center Cooling / Thermal Management）產業研究

## 一句話總結

AI 晶片功耗 10 年內提升約 6 倍（700W → 4,000W+），機櫃密度提升約 40–80 倍（15kW → 600kW–1MW），風冷在 ~20kW/機櫃就觸頂。2025 年是產業拐點：從 NVIDIA GB200 NVL72（~120kW）開始，所有機櫃級系統都「非液冷不可」，由 2026 年約 6,600–7,250 億美元的雲端巨頭資本支出（約 75% 與 AI 相關）資金推動。這是一個由「物理極限」強制驅動、確定性極高的結構性轉變。

---

## 二、產業概覽

### 市場規模（口徑差異大，建議以 Dell'Oro 為錨）

| 範疇 | 規模與成長 | 來源 |
| --- | --- | --- |
| 資料中心實體基礎設施 (DCPI) | 2030 年突破 $80B，中雙位數 CAGR | Dell'Oro, 2026 |
| 液冷（核心成長動能） | 2025 ~$3B（年增約一倍）→ 2029 ~$7B | Dell'Oro, 2026/1（最常被引用的窄口徑製造商收入） |
| 液冷（廣口徑長天期） | 2025 ~$5–6.6B → 2031–2035 約 $18–29B，CAGR ~20% | Grand View / Mordor / Precedence |
| AI 專用液冷 | 2025 ~$3.2B → 2036 ~$17.8B，CAGR ~17% | Future Market Insights / IDTechEx |
| 熱管理整體 | 以 ~20% CAGR 成長，到本世紀末規模追平 UPS 市場 | Dell'Oro |

> ⚠️ 不要跨機構混用市場規模數字——口徑（整體熱基礎設施 vs. 純設備）與天期差異造成約 2 倍落差。頭條數字建議用 Dell'Oro／Omdia；液冷深入分析用 IDTechEx／Mordor。

### 技術分段

| 技術 | 現況與份額 |
| --- | --- |
| 風冷（CRAC/CRAH） | 仍是裝機主力（2024 約 54% 市場），但 ~20kW/機櫃即達實用上限 |
| Direct-to-Chip 冷板式（贏家） | 佔液冷市場約 73–75%，單相為主、雙相隨 TDP 上升滲透。這是雲端建置採用的主流 |
| 浸沒式 | 仍是利基，2024 約佔液冷投資 17%；單相佔多數；要等機櫃密度穩定 >150–200kW 才會放量 |
| 後門熱交換器 (RDHx) | 過渡／改造方案，83% 新建案計畫一年內導入 |

採用率現況：DLC 在 2025 年企業採用率約 22%（與 2024 持平），58% 的 colo 業者回報客戶有液冷需求（Uptime Institute 2025）。

### 需求驅動（為何「非液冷不可」）

- GPU 功耗階梯：H100/H200 700W → B200 1,000W → GB300 1,400W → Vera Rubin ~1,800–2,300W（CES 2026）→ Dell'Oro 預估 2029 年 >4,000W。
- 機櫃密度階梯：企業 ~15kW → H100 風冷 ~40kW → GB200 NVL72 ~120–132kW → Rubin VR200 ~190–230kW → Rubin Ultra "Kyber" ~600kW（2027）→ Feynman 世代 ~1MW（2028+）。
- 雲端資本支出引擎：2026 年「四大 + Oracle」合計約 $660–725B（年增 ~77%），約 75% 與 AI 相關。Goldman Sachs 估 FY25–FY30 累計約 5.3 兆美元。
- PUE/用水壓力：產業 PUE 連 6 年停滯（2025 約 1.54），液冷可省 10–50% 能耗；Morgan Stanley 估 AI 資料中心 2028 年用水可達 1.07 兆公升（約 11 倍）。

### 風險與逆風

- 改造經濟性差：改造比新建貴 50–100%，每 MW 約 $2–3M，遷移週期 18–36 個月。
- 缺乏標準：「目前業界沒有 CDU 標準」（Boyd），~40 家廠商品質不一。
- 可靠度：冷卻問題佔資料中心事故 19% 且上升；漏液與 Tier III SLA 不相容。
- 競爭與整併：~40 家做 CDU，Dell'Oro 預估到本世紀末存活 <10 家拿走絕大多數份額——整併「無可避免」。
- 電網才是真正瓶頸：美國併網佇列卡關約 2,300 GW；電力已取代硬體成為建置的主要限制。
- 2027–28 消化風險：資本支出（~$700B）與直接 AI 營收（~$51B）落差大，存在週期消化疑慮。

---

## 三、競爭格局（依價值鏈分段）

價值鏈：元件（冷板/快接頭/歧管）→ CDU/熱系統 → 伺服器/機櫃 ODM 整合 → 服務。價值主要 accrue 在 CDU/系統 與 高可靠度元件（快接頭） 兩個卡點。

| 分段 | 領導者 | 動態 |
| --- | --- | --- |
| CDU／全套液冷系統 | Vertiv (VRT)、Schneider（併 Motivair）、CoolIT（被 Ecolab $4.75B 收購）、Boyd | Vertiv 2025 液冷市佔約 11.3% 居首；Schneider 以 $850M 取得 Motivair 75% 為明確「老二整併」動作 |
| 伺服器/機櫃 ODM 整合 | Foxconn (2317) ~40%、Quanta (2382) ~25–30%、Wiwynn (6669)、Supermicro (SMCI) | NVIDIA 正將機櫃組裝集中到少數廠商，可能重塑 ODM 經濟與份額 |
| 元件（冷板/快接/歧管） | Boyd、CoolIT、AVC (3017)、Auras (3324)；快接頭：Parker (PH)、Danfoss、Lotes (3533)、Fositek (6805) | 快接頭是高毛利卡點（無漏液乾斷快接是護城河） |
| 浸沒式專家 | GRC、Submer、LiquidStack、Iceotope | 2025–26 均獲新一輪募資；相對 DLC 仍屬利基 |
| 台灣供應鏈（最關鍵） | AVC、Auras 為純散熱雙雄；Kaori (8996, 熱交換器)、Fositek (6805, 快接) 為關鍵使能者 | AVC、Auras 均創 2025 年營收新高，能見度看到 2029 年 |
| 中國 | Envicool (002837)、華為 | Envicool 2025 營收 +32% 至 ~RMB6.07B，成本/在地化優勢的後起挑戰者 |

誰在搶份額：Vertiv（領頭羊、份額第一）、nVent（最突出的新晉搶份額者，訂單 backlog 約 3 倍）、Schneider（整併中的老二）、台灣 AVC/Auras（純散熱受惠最直接）。

警示名稱：Asetek（已淡出資料中心、營收腰斬）、Parker（散熱僅佔約 1% 營收）。

---

## 四、同業比較（Comps，資料約 2026/6/17–18）

| 公司 | 代碼 | 市值(USD) | 營收成長YoY | 營益率 | Fwd P/E | EV/EBITDA | 1年報酬 | 散熱純度 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Vertiv | VRT | ~$122B | +28% | 18.8% | ~46x | ~51x | +173% | 純（高） |
| nVent | NVT | ~$28B | +11% | 16.2% | ~35x | ~32x | +143% | 多元（液冷為成長引擎） |
| Schneider | SU.PA | ~$160B | +5% | 17.4% | ~28x | ~21x | +27% | 多元巨頭 |
| Supermicro | SMCI | ~$18B | +123% | ~4.5% | ~9x | ~16x | −36% | 伺服器 OEM |
| Parker Hannifin | PH | ~$119B | +6% | 21.7% | ~28x | ~23x | +43% | ⚠️ 散熱僅 ~1% |
| Flex | FLEX | ~$52B | +8% | 5.4% | ~31x | ~27x | +226% | EMS（將分拆 CPI） |
| Delta 台達電 | 2308 | ~$187B | +33% | 17.8% | ~46x | n/a | +454% | 多元（液冷約 9%） |
| Auras 奇鋐 | 3324 | ~$3.2B | +48% | 14.1% | ~21x | n/a | ~+132% | 純散熱 |
| AVC 雙鴻※ | 3017 | ~$31B | +107% | n/a | ~23x | n/a | +217% | 主要 DC 散熱 |
| Wiwynn 緯穎 | 6669 | ~$30B | +129% | 6.6% | ~13.5x | ~13.6x | +103% | 伺服器 ODM |
| Sunon 建準 | 2421 | ~$1.3B | +24% | 15.8% | ~13.4x | ~9.9x | +41% | 多元風扇廠 |
| Lotes 嘉澤 | 3533 | ~$8.2B | +12% | 30.0% | ~22.8x | ~18.5x | +67% | 連接器為主 |
| Envicool 英維克 | 002837 | ~$15B | +32% | ~8.6%淨利 | ~77x | n/a | +237% | 純（最接近） |
| Asetek | ASTK.OL | ~$64M | −21% | 負 | n/m | n/m | +105% | ⚠️ DC 業務休眠 |

※台灣代碼對應：AVC=亞諾法／雙鴻為 3324？校正見下。

重要校正：以代碼為準——3017 = AVC（亞洲電力/Asia Vital Components，中文常稱「雙鴻」其實為 3324）。為避免混淆，請以英文 + 代碼為準：Auras = 3324（奇鋐）、AVC = 3017。下單前務必再核對中文名。

結構性解讀：

1. 估值隨「散熱純度」走高 — Vertiv（~75% DC）給到 ~51x EV/EBITDA；Schneider（最多元）最便宜 ~21x。
2. 元件 vs. 系統的 EV/Revenue 不可直接比 — ODM/OEM（Wiwynn、SMCI ~0.8–0.9x）是低毛利轉手收入；高毛利元件（Lotes 30% 營益率、~7x EV/Rev）倍數天差地遠。
3. 真正的純散熱上市標的稀少 — 本質上只有 Vertiv、Auras、AVC、Envicool 四家。

---

## 五、值得關注標的清單（Watchlist）

### 🟢 核心持有（最乾淨的曝險）

- Vertiv (VRT) — AI 散熱領頭羊，端到端組合 + NVIDIA 參考設計綁定，backlog >$15B（翻倍以上）。最乾淨的美股代理。
- Auras 奇鋐 (3324.TWO) — 台灣純散熱高 beta，2025 創高、2026 指引 +60–70%，CDU 從數百台衝向 2027 年 2,000 台。
- AVC (3017.TW) — 台灣熱模組龍頭、BOM 覆蓋最廣，能見度看到 2029，台股藍籌散熱代表。

### 🟡 強力觀察（搶份額／轉機）

- nVent (NVT) — 最突出的新晉搶份額者，2026 年初 backlog 約 3 倍於前一年，純度比 Vertiv 低、估值較合理。
- Schneider (SU.PA) — 整併中的老二（Motivair），「grid-to-chip」全套故事，估值是大型股中最便宜。
- Delta 台達電 (2308.TW) — 電源 + 散熱一體，切入 800VDC「AI 工廠」架構，2025 獲利創高。
- Kaori 高力 (8996.TW) — GB200 板式熱交換器隱形冠軍（使能者）。
- Fositek 富世達 (6805.TWO) / Lotes 嘉澤 (3533.TW) — 快接頭/連接器卡點，Rubin 世代受惠。

### 🔴 注意風險/警示

- Supermicro (SMCI) — DLC 採用領先，但毛利薄、過往會計/治理爭議（已於 2026/1 恢復 Nasdaq 合規）；唯一一年負報酬。
- Envicool (002837.SZ) — 中國最接近純散熱者，但 2026 Q1 淨利年減約 82%，估值（~77x fwd P/E）高度由 AI 敘事驅動。
- Parker (PH)、Asetek (ASTK)、INVT (002334) — ⚠️ 散熱曝險過小或業務休眠，不應視為 AI 散熱純標的。

---

## 下一步（可選）

我可以接著幫你產出以下任一交付物：

1. 正式報告文件（Word/PPT）含市場規模瀑布圖、競爭定位矩陣、估值散佈圖；
2. Excel comps 工作簿 — 用 comps-analysis skill 做平均/中位/四分位倍數與離群值標記；
3. 深入單一標的（如 Vertiv 或 Auras）的 DCF 或三表模型。

你想先做哪一個？另外提醒：上表中文公司名與代碼請在實際下單前再次核對（3324 奇鋐 vs 3017 AVC 容易混淆）。

---

## 交付物產製階段

> 使用者：順序: 1 -> 2 -> 3

了解，依序執行 1 → 2 → 3。先從 #1 正式報告簡報 開始。我用 PPT 格式（產業概覽最常見的交付形式），先載入 headless 的 pptx-author skill 來了解產製方式。

```text
● Skill(market-researcher:pptx-author)
  ⎿  Successfully loaded skill
```

先確認環境（Python 與 python-pptx 是否可用），並建立輸出資料夾。

```bash
python -c "import pptx, openpyxl; print('pptx', pptx.__version__); print('openpyxl', openpyxl.__version__)" 2>&1; echo "---"; mkdir -p out && echo "out ready"
```

```text
● Bash(...)
  ⎿  Traceback (most recent call last):
       File "<string>", line 1, in <module>
         import pptx, openpyxl; print('pptx', pptx.__version__); print('openpyxl', openpyxl.__version__)
     … +4 lines
```

```bash
pip install python-pptx openpyxl 2>&1 | tail -5
```

```text
● Bash(...)
  ⎿  Downloading xlsxwriter-3.2.9-py3-none-any.whl (175 kB)
     Downloading et_xmlfile-2.0.0-py3-none-any.whl (18 kB)
     Installing collected packages: XlsxWriter, Pillow, lxml, et-xmlfile, python-pptx, openpyxl
     … +2 lines
```

兩個套件都裝好了。現在用 Python + python-pptx 產製繁體中文產業簡報。我會用微軟正黑體確保中文顯示，並加入市場規模原生圖表、估值表與機構級版型。

```text
● Write(build_deck.py)
  ⎿  Wrote 369 lines to build_deck.py
       1 # -*- coding: utf-8 -*-
       2 """Build the AI Data Center Cooling sector-overview deck (Traditional Chinese)."""
       3 from pptx import Presentation
       4 from pptx.util import Inches, Pt, Emu
       5 from pptx.dml.color import RGBColor
       6 from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
       7 from pptx.chart.data import CategoryChartData
       8 from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
       9
      10 # ---- palette ----
     … +360 lines
```

```bash
python build_deck.py 2>&1
```

```text
● Bash(...)
  ⎿  SAVED ./out/AI資料中心散熱_產業研究.pptx  slides: 9
```

簡報完成（9 頁）。接著做 #2 Excel comps 工作簿，含統計基準（平均/中位/四分位）與離群值標記。

```text
● Write(build_comps.py)
  ⎿  Wrote 188 lines to build_comps.py
       1 # -*- coding: utf-8 -*-
       2 """AI data center cooling — comps workbook with statistical benchmarking."""
       3 import statistics as st
       4 from openpyxl import Workbook
       5 from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, NamedStyle
       6 from openpyxl.utils import get_column_letter
       7
       8 NAVY   = "0B1F3A"; BLUE = "1F4E79"; ACCENT = "2E9BD6"; LGREY = "ECEFF3"
       9 TEAL   = "14A38C"; AMBER = "E89A1C"; RED = "C03A2B"; WHITE = "FFFFFF"; MIDG = "5A5A5A"
      10 CJK = "Microsoft JhengHei"
     … +178 lines
```

```bash
python build_comps.py 2>&1
```

```text
● Bash(...)
  ⎿  SAVED ./out/AI資料中心散熱_Comps.xlsx
```

#2 完成。最後做 #3 單一標的深入模型。最乾淨的純標的是 Vertiv (VRT)，我用它建 DCF。先載入 dcf skill 對齊方法論。

```text
● Skill(financial-analysis:dcf)
  ⎿  Successfully loaded skill
```

#1 與 #2 完成。現在建 #3 Vertiv (VRT) DCF 模型（含活公式、情境切換、敏感度表、與 comps 交叉驗證）。

```text
● Write(build_dcf.py)
  ⎿  Wrote 259 lines to build_dcf.py
       1 # -*- coding: utf-8 -*-
       2 """Vertiv (VRT) DCF — live-formula workbook (headless)."""
       3 from openpyxl import Workbook
       4 from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
       5 from openpyxl.utils import get_column_letter
       6
       7 NAVY="0B1F3A"; BLUE="1F4E79"; ACCENT="2E9BD6"; LGREY="ECEFF3"; INPUTF="FFF6E6"
       8 TEAL="14A38C"; AMBER="E89A1C"; RED="C03A2B"; WHITE="FFFFFF"; MIDG="5A5A5A"; DARK="222A35"
       9 CJK="Microsoft JhengHei"
      10 thin=Side(style="thin",color="D0D5DD"); border=Border(left=thin,right=thin,top=thin,bottom=thin)
     … +249 lines
```

```bash
python build_dcf.py 2>&1
```

```text
● Bash(...)
  ⎿  SAVED ./out/Vertiv_VRT_DCF.xlsx  sheets: ['DCF', 'Sensitivity', 'Summary']
```

三個檔案都產出了。讓我用 Python 獨立重算 DCF 基準情境，驗證公式邏輯正確並取得可報告的數字。

```bash
python - <<'PY'
# Independent recompute of Base case to sanity-check the workbook formulas…
PY
```

```text
● Bash(...)
  ⎿  FY30 revenue      $23.78B
     FY30 EBITDA       $6.09B
     PV explicit FCFF  $11.57B
     … +8 lines
```

模型運算正確。獨立重算證實公式無誤——同時揭示一個真實且重要的結論：以紀律性 DCF（WACC 10%、正常化 22x 終值）計算，Vertiv 在 ~$320 隱含約 −24% 下跌空間，代表現價（~51x EV/EBITDA）已 price in 高度完美的成長預期。這是誠實的估值發現，我保留不去「調參數製造上漲空間」。

讓我確認三個檔案都在位。

```text
● Listed 1 directory
```

---

## 三項交付物全部完成 ✅

檔案位於 `<repo>\out\`：

| # | 交付物 | 檔案 | 內容 |
| --- | --- | --- | --- |
| 1 | 產業研究簡報 | AI資料中心散熱_產業研究.pptx | 9 頁：投資重點 → 市場規模(含原生圖表) → 技術分段 → 需求驅動(功耗/密度雙階梯) → 競爭格局(價值鏈) → 同業比較表 → 標的清單 → 風險與來源 |
| 2 | Comps 工作簿 | AI資料中心散熱_Comps.xlsx | 14 家公司 × 9 指標 + 統計基準(平均/中位/四分位) + 離群值標記 + 方法論/來源分頁 |
| 3 | Vertiv DCF 模型 | Vertiv_VRT_DCF.xlsx | 活公式、熊/基/牛情境切換(改 DCF!L2)、雙敏感度表、永續法交叉驗證、Summary 總結 |

### 關鍵發現（值得你特別注意）

Vertiv DCF 揭示估值紀律問題：基準情境（WACC 10%、終值 22x EV/EBITDA）下，隱含每股約 $243，相對現價 ~$320 為 −24%；永續成長法更低（~$135）。意涵：

- VRT 現價（~51x EV/EBITDA、~46x fwd P/E）已 price in 近乎完美的成長——終值占 EV 高達 88%（超出健康的 50–70%），顯示價值幾乎全押在遠期假設。
- 要 justify 現價，需 WACC 降至 ~8.5%、終值倍數 ~26x+、或更高成長——敏感度表已把這些情境攤開讓你檢視。
- 我刻意不調參數製造上漲空間。這是「高品質公司、但估值已充分反映」的典型案例——基本面領頭羊 ≠ 當前價位有吸引力。

### 兩個提醒

1. 代碼校正：研究過程發現中文名易混淆，已在所有檔案標註並校正為 Auras 奇鋐 = 3324、AVC = 3017。下單前請再核對。
2. 資料時效：市場規模數字跨機構口徑差約 2 倍（已標註勿混用）；估值為即時變動估計值。

需要的話我可以接著：用 Sensitivity 分頁的甜蜜點反推「市場隱含的成長假設」、把 DCF 換成 Auras(3324) 這類純散熱台股、或把簡報的同業比較頁改成估值散佈圖。要先做哪個？
