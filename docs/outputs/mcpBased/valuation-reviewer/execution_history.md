# 💰 估值複核（valuation-reviewer）— 執行紀錄（mcpBased）

> 這版跟 `fileBased/valuation-reviewer/` 同一支 agent,差別在**輸入來源**:不再餵 `samples/*.md`,而是**真的去打 `portfolio` MCP server**(stdio),把回傳的 JSON 留存到 `mcp_pulls/` 當證據,再從那批 JSON 跑估值複核。全為假資料 / dev。

## 安裝外掛

```text
❯ /plugin install valuation-reviewer@fsi-local
  ⎿  ✓ Installed valuation-reviewer. Run /reload-plugins to apply.
```

## 任務指派

> 使用者:複核 Aurora Growth Fund III 的 GP 估值(對照估值政策)、算 NAV 與報酬指標、跑收益分配 waterfall(carry 與各 LP 分配),備一份給 IR/CCO 的 LP 報告草稿。資料從 `portfolio` MCP 即時拉,不要餵檔。

新任務:從 MCP 拉 GP 估值包與基金資料 → 對照政策複核 → 算 NAV/報酬/waterfall → 備 LP 報告草稿。先探索 server、確認合法 fund / as_of,再批次拉。

## 步驟 0 — 探索 server,確認合法參數

先用 harness 一次性模式打 `list_funds`,拿到合法的 fund 字串與 as-of 日期(避免硬編錯字)。

```bash
cd ".../docs/outputs/mcpBased/_harness" && PYTHONUTF8=1 python mcp_client.py \
  ".../mock-mcp/portfolio/server.py" list_funds '{}' 2>/dev/null
```

```json
{ "funds": ["Aurora Growth Fund III, L.P."], "as_of": ["2026-03-31"] }
```

確認:`fund = "Aurora Growth Fund III, L.P."`、`as_of = "2026-03-31"`。

## 步驟 1 — 批次拉 MCP（一次叫起 server,打 6 個工具）

寫 `scripts/pull.json`(`out_dir` 用絕對 Windows 路徑),跑批次:

```bash
cd ".../_harness" && PYTHONUTF8=1 python mcp_client.py --spec \
  ".../mcpBased/valuation-reviewer/scripts/pull.json" 2>/dev/null
```

| # | server | tool | args | 結果 | 存檔 |
|---|---|---|---|---|---|
| 1 | portfolio | `list_funds` | `{}` | ok | `mcp_pulls/01_list_funds.json` |
| 2 | portfolio | `get_positions` | `{"fund":"Aurora Growth Fund III, L.P.","as_of":"2026-03-31"}` | ok | `02_get_positions.json` |
| 3 | portfolio | `get_fund_nav_build` | `{"fund":"...","as_of":"2026-03-31"}` | ok | `03_get_fund_nav_build.json` |
| 4 | portfolio | `get_capital_flows` | `{"fund":"..."}` | ok | `04_get_capital_flows.json` |
| 5 | portfolio | `get_fund_terms` | `{"fund":"..."}` | ok | `05_get_fund_terms.json` |
| 6 | portfolio | `get_valuation_policy` | `{"fund":"..."}` | ok | `06_get_valuation_policy.json` |

6 個工具全部 `ok: true`,另存 `_tools.json`(server 工具清單)。**沒有失敗的呼叫。**

### ⚠️ harness 序列化盲點(發現並已中央修正)

`get_capital_flows` 與 `get_valuation_policy` 在 server 端回傳的是 **Python `list`**;FastMCP 把 list 拆成「每個元素一個 content block」,而共用 harness 一開始的 `_extract()` 只取 `content[0]` → 這兩支被**截成只剩第一筆**(只看到 2022 那筆出資、只看到 P1)。

這會直接弄壞 IRR(少了後面的出資/分配)與政策複核(少了 P2–P4),不能將就。**已在 `_harness/mcp_client.py` 中央修正**(依「已知會回 list 的工具集」把所有 content block 重組回完整 list)。重跑標準 `scripts/pull.json`(同一支 client、同一份 spec)即拿到完整 list:

```bash
cd ".../_harness" && PYTHONUTF8=1 python mcp_client.py --spec ../valuation-reviewer/scripts/pull.json 2>/dev/null
# 04_get_capital_flows.json: 5 rows
# 06_get_valuation_policy.json: 4 rows
```

覆寫後:capital_flows 5 筆(3 出資 + 1 分配 + 期末 NAV)、valuation_policy 4 條(P1–P4)齊全。**數字全來自 server,只是把被截斷的 list 補回完整。**

## 步驟 2 — 拿回的關鍵數字（全部出自 `mcp_pulls/`）

- **`get_positions`**:5 家被投資公司,`total_cost = 250,000,000`、`total_reported_fv = 330,000,000`。method 欄是 server enum(`market_multiple/dcf/recent_round/cost/other`)。Nova 報 `other`(管理層估計)、Zephyr `last_updated=2025-03`。
- **`get_fund_nav_build`**:投組 FV 330M + 現金 20M + 其他 5M − 應付 5M = **NAV 350M (as-reported)**。
- **`get_capital_flows`**:−100M(2022-06)、−100M(2023-06)、−100M(2024-06)、+40M(2025-06)、期末 NAV 350M。
- **`get_fund_terms`**:committed 500M、contributed 300M、invested_cost 250M、fees 50M、distributions 40M、`European whole-fund`、pref 8%、catch-up 100%、carry 20%、`preferred_accrued_to_date = 35,000,000`。
- **`get_valuation_policy`**:P1 stale 重估 / P2 上調須佐證 / P3 高於輪價須核准 / P4 不符以調整後值計 NAV。

## 步驟 3 — 估值複核 + 算 NAV / 報酬 / waterfall

寫 `scripts/analyze.py`,**只讀 `mcp_pulls/` 的 JSON**,做政策複核、NAV 橋接、報酬、pref 獨立重算、三情境 waterfall。

```bash
cd ".../scripts" && PYTHONUTF8=1 python analyze.py
```

```text
=== POLICY REVIEW ===
  Helios Software      market_multiple  PASS            adj=0          (P3 待委員會文件)
  Orion Logistics      recent_round     PASS            adj=0
  Nova Biotech         other            REJECT MARK-UP  adj=-25,000,000 (P2 無方法/無觸發)
  Titan Manufacturing  dcf              PASS            adj=0
  Zephyr Retail        cost             RE-REVIEW       adj=0          (P1 stale)
adjusted portfolio FV = 305,000,000 | NAV reported 350M → adjusted 325M
=== RETURNS ===
  Gross MOIC rep 1.320x / adj 1.220x | TVPI 1.300x / 1.217x | DPI 0.133x
  Net IRR    rep 10.18% / adj 7.56%  (hurdle 8%)
=== PREF RECOMPUTE (8% compound) ===
  FV contrib 371,518,001 − FV dist 42,379,000 − net contrib 260,000,000
  = recomputed pref 69,139,002 | provided 35,000,000 | gap 34,139,002
=== WATERFALL ===
  A GP-pkg     carry 18,000,000  LP 372,000,000  check 0
  B adj+35M    carry 13,000,000  LP 352,000,000  check 0
  C adj+indep  carry          0  LP 365,000,000  check 0
```

**判讀(agent 的複核結論):**
- 抓到 **Nova(P2)** 與 **Zephyr(P1)** 兩筆違規;**Helios 不誤殺**(有 comps + 新一輪佐證,只附帶要 P3 文件);Orion、Titan 放行。
- Nova 那筆 +25M 未佐證上調,**直接撐出 GP 的 carry**:政策調回後利潤縮水,carry 從 18M → 13M。
- 再往下追:GP 提供的 pref 35M,我獨立以 8% 複利重算 ~69M;且調整後 **Net IRR 7.56% < 8% hurdle** → **carry 可能根本尚未賺得(=0)**。這是本季最該給 CCO 看的連動。
- **守 guardrail**:Zephyr 是「未複核」流程問題,**不亂改數字**,只 flag 重新複核;pref 差異定性為**待對帳事項,非斷定錯誤**;LP 名冊 server 沒給 → **不瞎掰各 LP 分配**,flag 給 IR。

## 步驟 4 — 產出 LP 報告草稿

```text
Write(out/LP_Report_Draft_2026-Q1.md)
```

含:執行摘要、P1–P4 逐筆複核表、NAV 橋接、報酬指標、三情境 waterfall、優先報酬重算意見、各 LP 缺口、IR/CCO 例外清單與簽核欄。維持「GP 報告值不照單全收」「只備草稿、須 IR＋CCO 簽核才分送」。

## 步驟 5 — 產出 Excel 覆核底稿（活公式 + 跨頁連結）

寫 `scripts/build_val_review.py`,**讀 `analysis_result.json`**(由 analyze.py 從 MCP 快照算出),用 openpyxl 產活公式底稿:

```bash
cd ".../scripts" && PYTHONUTF8=1 python build_val_review.py
# SAVED .../out/Fund_III_Valuation_Review_2026-Q1.xlsx
#   sheets: ['NAV Bridge','Source','Valuation Review','Returns','Pref Recompute','Waterfall']
```

6 個分頁:**Source**(資料來源/MCP 工具/快照路徑,可追溯)、**NAV Bridge**(350M→325M,連結估值表)、**Valuation Review**(5 家逐筆 P1–P4 檢核、違規紅底、調整後 FV=公式)、**Returns**(TVPI/DPI/RVPI + XIRR,自動標 <8% hurdle)、**Pref Recompute**(YEARFRAC + 8% 複利重算 ~69M vs 35M,差異紅底)、**Waterfall**(A/B/C 三情境逐層 MIN/MAX/IF,carry 與 LP+GP=總價值檢查)。

本機無 LibreOffice headless,故以獨立 Python 鏡像驗證 waterfall 公式鏈:

```text
A: carry 18,000,000 | LP 372,000,000 | check 0
B: carry 13,000,000 | LP 352,000,000 | check 0
C: carry          0 | LP 365,000,000 | check 0
```

三情境 LP+GP 皆 = 總價值 ✓(XIRR/YEARFRAC 由 Excel 開檔時計算)。

## 產出清單

```text
mcpBased/valuation-reviewer/
├─ mcp_pulls/         01..06_*.json + _tools.json   ← 真實 MCP 回傳快照(證據)
├─ execution_history.md                              ← 本檔
├─ note.md                                           ← 答案卡 + 埋雷對照
├─ out/
│  ├─ LP_Report_Draft_2026-Q1.md                     ← LP 報告 / 複核備忘草稿
│  └─ Fund_III_Valuation_Review_2026-Q1.xlsx         ← 覆核底稿(6 分頁,活公式)
└─ scripts/
   ├─ pull.json            ← 批次 MCP pull spec
   ├─ analyze.py           ← 複核計算引擎(只讀 mcp_pulls)
   ├─ analysis_result.json ← 計算結果(供 build script)
   └─ build_val_review.py  ← 產 xlsx
```

估值複核完成 ✅ — MCP 工具呼叫 7 次(`list_funds` ×2 含探索、`get_positions/get_fund_nav_build/get_capital_flows/get_fund_terms/get_valuation_policy` 各 1),全部成功,無失敗呼叫。
