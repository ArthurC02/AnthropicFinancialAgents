# 📊 財報追蹤(earnings-reviewer)— 執行紀錄(MCP 版)

> 這份是 **mcpBased** 版的執行紀錄:agent 的輸入不是人工餵的 `samples/*.md`,而是**實際去呼叫 `mock-mcp` server**(factset + daloopa)拉回的資料。所有數字都來自 `mcp_pulls/*.json`,不憑空編。
> **全部為 mock / dev 假資料。**

## 安裝外掛與初始需求

```text
❯ /plugin install earnings-reviewer@fsi-local
  ⎿  ✓ Installed earnings-reviewer. Run /reload-plugins to apply.
```

> 使用者:台積電剛發完最新一季(2026 Q1)財報,幫我用 FactSet/Daloopa 拉實際數與市場共識,做 beat/miss、更新追蹤模型,並草擬一份財報後觀點筆記(實際 vs. 市場預期 vs. 前次指引)。順便用 Daloopa 的另一個來源跟 FactSet 對帳。

確認任務範圍:主標的 TSM(台積電,Q1-2026 實際);次要標的 VRT(Vertiv,FY2025,僅順手確認 coverage)。這支 agent 的本質是「對一個具體財報事件做反應」,所以第一步是**真的把資料拉回來**——走 MCP connector,不靠摘要、不編數字。

## 步驟 0 — 先探索 coverage(確認合法 ticker / period)

照 RUNBOOK,先打兩個 server 的 `list_coverage()` 確認有哪些 ticker / period / statement,再打需要參數的工具。

```bash
cd ".../docs/outputs/mcpBased/_harness"
PYTHONUTF8=1 python mcp_client.py --spec ".../earning-reviewer/scripts/pull_factset.json" 2>/dev/null
PYTHONUTF8=1 python mcp_client.py --spec ".../earning-reviewer/scripts/pull_daloopa.json" 2>/dev/null
```

兩個 server 的 `list_coverage` 回傳:

- **factset**:tickers `["TSM","VRT"]`,periods `["FY2025","Q1-2026"]` → 確認 TSM Q1-2026 存在。
- **daloopa**:tickers `["TSM","VRT"]`,periods `["FY2025","Q1-2026"]`,statements `["balance_sheet","guidance","income_statement","product_revenue","revenue_mix_node","revenue_mix_platform","segment_revenue"]` → 確認要打的 statement group 都在。

## 步驟 1 — 拉財報數字(真的呼叫 MCP)

寫了兩份 batch spec 到 `scripts/`,harness 一次叫起 server 打多個工具,每個回傳寫成一份 JSON 到 `mcp_pulls/`。

**factset(`scripts/pull_factset.json`,8 個 call):**

| save_as | server / tool | args |
|---|---|---|
| 01 | factset · list_coverage | `{}` |
| 02 | factset · get_fundamentals | `{ticker:"TSM", period:"Q1-2026"}` |
| 03 | factset · get_fundamentals | `{ticker:"TSM"}` |
| 04 | factset · get_consensus_estimates | `{ticker:"TSM", period:"Q1-2026"}` |
| 05 | factset · get_consensus_estimates | `{ticker:"TSM"}`(含 Q2 指引) |
| 06 | factset · get_prices | `{ticker:"TSM"}` |
| 07 | factset · get_fundamentals | `{ticker:"VRT", period:"FY2025"}` |
| 08 | factset · get_consensus_estimates | `{ticker:"VRT"}` |

**daloopa(`scripts/pull_daloopa.json`,6 個 call):**

| save_as | server / tool | args |
|---|---|---|
| 10 | daloopa · list_coverage | `{}` |
| 11 | daloopa · get_line_items | `{ticker:"TSM", period:"Q1-2026", statement:"revenue_mix_platform"}` |
| 12 | daloopa · get_line_items | `{ticker:"TSM", period:"Q1-2026", statement:"revenue_mix_node"}` |
| 13 | daloopa · get_line_items | `{ticker:"TSM", period:"Q1-2026", statement:"income_statement"}` |
| 14 | daloopa · get_line_items | `{ticker:"TSM", period:"Q1-2026", statement:"guidance"}` |
| 15 | daloopa · get_line_items | `{ticker:"TSM"}`(全表) |

**結果:14 個 tool call 全部 `ok:true`,0 失敗。** 另各寫了一份 `_tools.json`(server 工具清單)。list 工具(get_fundamentals / get_consensus_estimates / get_prices / get_line_items)都回**完整清單**,沒有截斷。

### 拿回來的關鍵數字(全部來自 mcp_pulls/)

`factset get_fundamentals(TSM, Q1-2026)`(`mcp_pulls/02`):

```text
revenue        35.90  USD bn
revenue_ntd  1134.10  NTD bn
gross_margin    0.662
op_margin       0.581
net_margin      0.505
net_income_ntd 572.48 NTD bn
eps            22.08  NTD
eps_adr         3.49  USD
usd_twd         31.6  rate
revenue_yoy     0.406
revenue_qoq     0.064
```

`factset get_consensus_estimates(TSM)`(`mcp_pulls/04-05`):

```text
Q1-2026 revenue       cons 35.5   actual 35.90  prior_guide 34.6-35.8
Q1-2026 gross_margin  cons 0.64   actual 0.662  prior_guide 0.63-0.65
Q1-2026 eps_ntd       cons 20.88  actual 22.08
Q1-2026 eps_adr       cons 3.26   actual 3.49
Q2-2026 revenue       cons 38.1   actual —      prior_guide 39.0-40.2
Q2-2026 gross_margin  cons n/a    actual —      prior_guide 0.655-0.675
```

`factset get_prices(TSM)`(`mcp_pulls/06`):4/15 收 213.00 → 4/16 收 206.40(財報後 ~-3.1%)。

`daloopa get_line_items(TSM, Q1-2026, ...)`(`mcp_pulls/11-14`):

```text
平台:HPC .61 / Smartphone .26 / IoT .06 / Auto .04 / DCE .01 / Other .02
節點:N3 .25 / N5 .36 / 7nm .13 / Advanced(<=7nm) .74
損益:Revenue NT$1134.10bn、US$35.90bn、Gross Profit US$23.77bn、Net Income NT$572.48bn
指引:Capex FY2026 52-56 US$bn、先進製程占資本支出 0.70-0.80
```

## 步驟 2 — 解讀(beat/miss、組合、指引)

判讀全部在 `build_tsmc_model.py` 內以拉回的 JSON 算出,不寫死:

- **beat/miss**:營收 35.90/35.5−1 = **+1.13%**;毛利率 66.2%−64% = **+220bps**;EPS 22.08/20.88−1 = **+5.75%**;ADR 3.49/3.26−1 = **+7.06%**。
- **Q2 指引 vs 市場**:指引中點 39.6 vs 共識 38.1 = **+3.94%**(指引高於市場)。
- **組合**:HPC 61% 為最大引擎;先進製程(≤7nm)佔 74%。

> 逐字稿:本 mock 未提供法說會 transcript。依 agent guardrail,逐字稿屬外來不可信內容,只擷取資訊、不執行指令;沒有逐字稿就不臆測管理層原話,僅依 MCP 拉回的 guidance / consensus 數據判讀,並如實標「server 未提供逐字稿」。

## 步驟 3 — 更新模型(model-update)+ 模型 QC(audit-xls)

```text
Write(scripts/build_tsmc_model.py) → 從 mcp_pulls/ 讀數,openpyxl 產 4 個 sheet
$ python build_tsmc_model.py
SAVED .../out/TSMC_Q1_2026_Model.xlsx  sheets: ['Model','Actual vs Cons vs Guide','FactSet vs Daloopa','Sources & Notes']
CHECK rev beat +1.13% | GM +220bps | EPS +5.75% | ADR +7.06% | Q2 vs cons +3.94%
XCHECK rev 35.9==35.9 | NI 572.48==572.48 | GM 0.662 vs 0.6621
MIX platform sum 1.000 | node N3+N5+7nm 0.740 vs advanced 0.74
```

**QC(audit-xls 精神)通過:** 淨利/EPS 反推對得上公布數(NT$572.48bn ÷ 25.93bn 股 = NT$22.08 ✔);Q1 全部為實際輸入(藍底,附來源 comment),H2 為公式/估計,無硬填;平台組合 SUM、節點加總兩道查核公式均過。

## 步驟 4 — 來源對帳(FactSet vs Daloopa)

兩個獨立 MCP 對同一季的數字應彼此印證:

| 項目 | FactSet | Daloopa | 判定 |
|---|---|---|---|
| 營收 US$bn | 35.90 | 35.90 | ✔ |
| 營收 NT$bn | 1,134.10 | 1,134.10 | ✔ |
| 淨利 NT$bn | 572.48 | 572.48 | ✔ |
| 毛利率 | 66.2% | 23.77/35.90 = 66.21% | ✔(差 0.01pp,四捨五入) |

**結論:完全對帳,無實質分歧。** 唯一差異是 Daloopa 毛利率由「毛利 ÷ 營收」反推得 66.21%,與 FactSet 公布 66.2% 差 0.01pp,純四捨五入,在容忍範圍內。

## 步驟 5 — 草擬筆記 + 圖表(morning-note)

```text
Write(out/TSMC_Q1_2026_Earnings_Note.md)         ← 財報後觀點筆記(草稿)
Write(scripts/build_tsmc_charts.py) → matplotlib  ← 3 張圖
$ python build_tsmc_charts.py
SAVED charts: ['01_beat_miss.png','02_platform_mix.png','03_node_mix.png']
```

## 寫了哪些檔

```text
mcp_pulls/   01-08 (factset) + 10-15 (daloopa) + _tools.json ×2   ← 真 MCP 證據
out/TSMC_Q1_2026_Earnings_Note.md                                 ← 主產出(筆記草稿)
out/TSMC_Q1_2026_Model.xlsx                                       ← 4-sheet 追蹤模型
out/charts/01_beat_miss.png 02_platform_mix.png 03_node_mix.png   ← 3 張圖
scripts/pull_factset.json pull_daloopa.json                       ← MCP pull spec
scripts/build_tsmc_model.py build_tsmc_charts.py                  ← build script
note.md  execution_history.md                                     ← 評分卡 / 本檔
```

## 把關

只交草稿,不對外發布;送出前需資深分析師簽核。每個數字標出處(MCP 工具名),查不到的(淨利確切 YoY)標 [UNSOURCED],不編。全部 mock / dev 假資料。
