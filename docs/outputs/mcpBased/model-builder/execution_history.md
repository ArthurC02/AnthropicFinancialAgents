# 🧮 估值建模（model-builder）— 執行紀錄（MCP 版）

> 這份是「真的去打 `mock-mcp` server」的執行紀錄。輸入不再是人工餵的 `samples/*.md`,而是用 harness(`docs/outputs/mcpBased/_harness/mcp_client.py`)以 stdio 把 `capiq` / `daloopa` 兩支 server 叫起來,跑真正的 MCP `initialize + list_tools + call_tool`,把回傳存成 `mcp_pulls/*.json`。全部 mock / dev 假資料。

## 安裝與第一句指令

```text
❯ /plugin install model-builder@fsi-local
  ⎿  ✓ Installed model-builder. Run /reload-plugins to apply.
```

> 使用者:幫 Vertiv（VRT）從零建一份現金流折現（DCF）估值模型。歷史財務從 Daloopa 拉、前瞻假設用 CapIQ estimates 跟 comps 倍數做 sanity check,列出關鍵假設,做一張 WACC × 永續成長率敏感度表,並做 comps 足球場交叉檢查。

我用 model-builder 的 `dcf-model` skill 從零建。先載 skill 對齊慣例(藍=輸入/黑=公式/綠=連結色碼、WACC 組成、期中折現、永續終值、EV→equity 橋接、football field)。

```text
● Skill(model-builder:dcf-model)
  ⎿  Successfully loaded skill
```

## 步驟①:接 MCP 拉資料

按 RUNBOOK,寫兩份 batch spec(`out_dir` 用絕對 Windows 路徑),分別打 `daloopa` 跟 `capiq`。

**Daloopa pull**(`scripts/pull_daloopa.json`):先 `list_coverage()` 確認合法 ticker/period/statement,再逐個 statement 拉 VRT。

```bash
cd ".../mcpBased/_harness" && PYTHONUTF8=1 python mcp_client.py \
  --spec ".../mcpBased/model-builder/scripts/pull_daloopa.json" 2>/dev/null
```

| call | tool | args | save_as | ok |
|---|---|---|---|---|
| 1 | `list_coverage` | `{}` | 01_daloopa_list_coverage | ✅ |
| 2 | `get_line_items` | `{"ticker":"VRT"}` | 02_daloopa_vrt_all_line_items | ✅ |
| 3 | `get_line_items` | `{"ticker":"VRT","period":"FY2025","statement":"income_statement"}` | 03_…income_statement | ✅ |
| 4 | `get_line_items` | `{…"statement":"segment_revenue"}` | 04_…segment_revenue | ✅ |
| 5 | `get_line_items` | `{…"statement":"product_revenue"}` | 05_…product_revenue | ✅ |
| 6 | `get_line_items` | `{…"statement":"balance_sheet"}` | 06_…balance_sheet | ✅ |

`list_coverage()` 回傳:tickers `[TSM, VRT]`、periods `[FY2025, Q1-2026]`、statements 含 `income_statement / segment_revenue / product_revenue / balance_sheet / guidance / revenue_mix_*`。確認 VRT 只有 FY2025。

**CapIQ pull**(`scripts/pull_capiq.json`):

```bash
cd ".../mcpBased/_harness" && PYTHONUTF8=1 python mcp_client.py \
  --spec ".../mcpBased/model-builder/scripts/pull_capiq.json" 2>/dev/null
```

| call | tool | args | save_as | ok |
|---|---|---|---|---|
| 7 | `get_comps` | `{"sector":"AI Data Center Cooling"}` | 07_capiq_comps_cooling | ✅ |
| 8 | `get_comps` | `{"tickers":"VRT,NVT,SU.PA,2308.TW,3324.TWO"}` | 08_capiq_comps_peerset | ✅ |
| 9 | `get_quote` | `{"ticker":"VRT"}` | 09_capiq_quote_vrt | ✅ |
| 10 | `get_estimates` | `{"ticker":"VRT"}` | 10_capiq_estimates_vrt | ✅ |

**合計 10 個 MCP tool call,全部成功,0 失敗。** 原始 JSON 與 `_tools.json` 都在 `mcp_pulls/`。

## 步驟①.5:判讀拉回來的關鍵數字

- **Daloopa(歷史,真的有的)**:FY2025 營收 **$8.0bn**、營業利益 **$1.5bn**(利潤率 18.75%)、backlog **$15.0bn**;分部 Americas 4.6 / APAC 1.8 / EMEA 1.6(合計 8.0 ✓);產品線 Power 3.0 / Thermal 2.5 / Rack 1.5 / Services 1.0(合計 8.0 ✓)。
- **CapIQ quote**:現價 **$320.00**、市值 **$122bn** → 隱含稀釋股數 122/320 = **0.38125bn**。
- **CapIQ estimates**:FY2026E 營收 **$10.9bn**(EBITDA margin 22%、EPS $3.60)、FY2027E 營收 **$13.5bn**(margin 23%)。
- **CapIQ comps**:VRT EV/EBITDA **51x**、fwd P/E 46x、1 年報酬 +173%(→ 支持高 beta 假設);同業 NVT 32x、SU.PA 21x(供 football field)。

**Daloopa 沒給的**(誠實點名,全部標 `[ASSUMPTION]`):總負債、現金、淨負債、D&A、capex、ΔNWC、稅率、beta、無風險利率、ERP、股數。

> ⚠️ **發現一個要誠實處理的落差**:file-based 版用 FY25A 營收 **$10.84bn** 起算,但這次 Daloopa mock 真的回傳的是 **$8.0bn**。RUNBOOK guardrail 寫得很白:「數字一律來自實際拉到的 JSON——不要編」。所以本模型一律以 **$8.0bn** 為歷史基準,不沿用 file-based 的數字。前兩年成長率改成「直接錨定 CapIQ estimates」(8.0→10.9→13.5),這樣每個 output 都能 trace 回 pull 檔。

## 步驟②:建模型(dcf-model skill 慣例)

```text
● Write(scripts/build_vrt_dcf_mcp.py)
  ⎿  Wrote build script;讀 mcp_pulls/*.json → openpyxl 產活公式 xlsx
```

腳本第一件事是 `load()` 把三個 pull 檔讀進來,所有「來源數字」都是從 JSON 取值,不在程式裡寫死:

```python
REV_FY25  = dal_get("income_statement","Revenue")     # 8.0  ← Daloopa
PRICE     = quote["price"]                             # 320  ← CapIQ
SHARES    = round(MKTCAP/PRICE, 5)                     # 0.38125 ← CapIQ 市值/現價
REV_FY26E = est_get("FY2026","revenue")               # 10.9 ← CapIQ
G_FY26    = round(REV_FY26E/REV_FY25 - 1, 4)          # +36.25% (8.0→10.9)
```

結構:**DCF 分頁**(情境選擇器熊/基/牛 → MCP 來源資料區(綠字 provenance)→ 三情境假設塊 + CHOOSE 整合列 → 全域假設 → 財務預測(含 FY26/27 vs CapIQ cross-check 列)→ FCFF 建構 → 期中折現 → EV→equity 橋接 → 隱含股價 → **足球場 football field** → 5×5 WACC×g 敏感度表)+ **WACC 分頁**(CAPM 完整推導)。藍=輸入、黑=公式、綠=連結/MCP 來源;計算格全公式、不打死。

```bash
cd "…/model-builder/scripts" && PYTHONUTF8=1 python build_vrt_dcf_mcp.py
```

```text
MCP inputs: REV25=8.0 OP25=1.5 (m=18.75%) backlog=15.0 price=320.0 mcap=122
  -> shares=0.38125 | FY26E=10.9 (g=36.25%) FY27E=13.5 (g=23.85%)
SAVED …/out/VRT_DCF_Model.xlsx  sheets: ['DCF', 'WACC']
```

一次過,沒有合併儲存格或目錄錯誤(這版預先 `os.makedirs(OUT)` 並把表頭改成獨立 `put()`)。

## 步驟③:稽核 / 獨立重算驗證

本機沒有 LibreOffice,改用獨立 Python 重算鏡像工作表公式(取代 skill 的 recalc.py),確認:WACC、隱含股價、終值占 EV%、敏感度中心格、以及 FY26/27 vs CapIQ 的 cross-check。

```text
CoE 11.5500% | after-tax CoD 4.3450% | wE 98.47%/wD 1.53% | WACC 11.4395%
Revenue: [8.0, 10.9, 13.5, 15.525, 17.232, 18.611]
  FY26 model 10.90 vs CapIQ 10.9  diff +0.000   ← cross-check 對齊
  FY27 model 13.50 vs CapIQ 13.5  diff -0.000   ← cross-check 對齊
ΣPV FCFF 9.03 | TV 39.71 | PV TV 24.39
EV 33.42 | Equity 31.52 | shares 0.38125
Implied price $82.68  vs $320.0  => -74.2%
TV % of EV 73.0% | implied EV/EBITDA(FY26E) 13.9x
  FF VRT 51x   : px $317.26 (-1%)
  FF NVT 32x   : px $197.21 (-38%)
  FF SU.PA 21x : px $127.70 (-60%)
```

並 `load_workbook` 抽查公式格與字體顏色,確認:`C43=C8`(連結 Daloopa)、`D43=C43*(1+D29)`(公式)、`C69=C67/C68`(隱含股價公式)、敏感度中心格是完整 DCF 重算式;C8/C39 綠字、D18/C33 藍字、D43 黑字——色碼正確。

驗證完成 ✅ — 中心格 $82.68 與隱含股價一致;FY26/FY27 營收與 CapIQ estimates 差異 = 0;模型自洽。

## 步驟④:敏感度 + 足球場(已含在 xlsx)

- 5×5 WACC×g 敏感度表($67–$107),基準置中高亮 = $82.68。
- 足球場:VRT 自身 51x → ~$317(≈現價,自洽);DCF 13.9x → $82.68。

## 步驟⑤:交付,建完即停

交付清單:
- `mcp_pulls/*.json`(10 個 call + `_tools.json`)
- `out/VRT_DCF_Model.xlsx`(活公式雙分頁)、`out/VRT_DCF_Model.md`(摘要)
- `scripts/`(兩份 pull spec + build script)
- 本檔 + `note.md`

依 guardrail **停在這裡等使用者核准**才往下游用。若要縮小與現價的差距,建議改建 10 年顯性期或 WACC ~9% 版本——待核准。
