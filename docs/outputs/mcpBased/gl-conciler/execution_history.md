# ⚖️ 總帳對帳（gl-reconciler）— 執行紀錄（MCP 版）

> 這版跟 `fileBased/` 最大的差別:agent 的輸入**不是**人工餵的 `samples/*.md`,而是**即時打 MCP server 拉回來的**。所以證據在 `mcp_pulls/`(等同 fileBased 的 `samples/`)。資料全是 mock / dev。

## 1. 安裝外掛

```text
❯ /plugin install gl-reconciler@fsi-local
  ⎿  ✓ Installed gl-reconciler. Run /reload-plugins to apply.
```

掛上兩個唯讀 MCP:`internal-gl`(總帳側)、`subledger`(子帳/custody 側 + 佐證)。兩個都唯讀 —— 設計上就沒有 write/post 工具,符合「agent 永不過帳」的護欄。

## 2. GL ↔ 子帳對帳任務

> 使用者:幫 Aurora Growth Fund III 做 2026-04-30 的 GL vs 子帳對帳。逐筆比對找差異、追根因、做獨立複核濾掉誤報,產出例外報告。資料直接從 `internal-gl` 跟 `subledger` 兩個 MCP 拉。

### 2.1 先探索合法參數（`list_entities`）

不確定 fund / as_of 拼字,先打 `internal-gl` 的探索工具確認。

```text
● internal-gl ▸ list_entities()
  ⎿  gl_position_funds:  ["Aurora Growth Fund III"]
     gl_position_as_of:  ["2026-04-30"]
     trial_balance_entities: ["Aurora Capital Management LLC"]
```

確認 `fund = "Aurora Growth Fund III"`、`as_of = "2026-04-30"`。

### 2.2 拉兩邊的帳 + 三份佐證（批次,harness `--spec`）

用 harness(`docs/outputs/mcpBased/_harness/mcp_client.py`)批次叫起 server 打工具,原始 JSON 落地到 `mcp_pulls/`。

```text
● internal-gl ▸ get_gl_positions(fund="Aurora Growth Fund III", as_of="2026-04-30")
  ⎿  source=GL, basis=trade-date, 9 positions, total_mv_usd = 84,500,000
     → mcp_pulls/02_gl_positions.json

● subledger ▸ get_subledger_holdings(fund="Aurora Growth Fund III", as_of="2026-04-30")
  ⎿  source=Custody, basis=settlement-date, 9 positions, total_mv_usd = 82,650,300
     → mcp_pulls/03_subledger_holdings.json

● subledger ▸ get_pending_settlements(fund="Aurora Growth Fund III", as_of="2026-04-30")
  ⎿  TRD-9001 · FI-GB123 · Buy 500,000 · trade 2026-04-29 / settle 2026-05-02 (跨月底)
     → mcp_pulls/04_pending_settlements.json

● subledger ▸ get_fx_rates(as_of="2026-04-30")
  ⎿  EUR/USD · GL 1.08000 vs custody 1.08004
     → mcp_pulls/05_fx_rates.json

● subledger ▸ get_tolerance_policy()
  ⎿  absolute_mv_usd=0.01 · quantity=0 · fx_rounding_relative=0.0005 (0.05%)
     → mcp_pulls/06_tolerance_policy.json
```

實際呼叫方式(RUNBOOK 批次模式,絕對 Windows `out_dir`):

```bash
cd "<REPO>/docs/outputs/mcpBased/_harness"
PYTHONUTF8=1 python mcp_client.py --spec "<REPO>/docs/outputs/mcpBased/gl-conciler/scripts/pull_gl.json"        2>/dev/null
PYTHONUTF8=1 python mcp_client.py --spec "<REPO>/docs/outputs/mcpBased/gl-conciler/scripts/pull_subledger.json" 2>/dev/null
```

> 共 **6 個 MCP 工具呼叫**(1× `list_entities` + 1× `get_gl_positions` + 4× subledger),全部 `ok=true`,零失敗。兩個 server 各有一份 `_tools.json`(分別存成 `_tools_internal-gl.json` / `_tools_subledger.json`,因共用 `out_dir` 會互蓋)。

關鍵數字(直接取自 MCP result,沒有重算):

| | GL | 子帳 | 差異 |
|---|---:|---:|---:|
| total_mv_usd | 84,500,000 | 82,650,300 | **1,849,700** |

### 2.3 逐筆比對（fan-out:每類資產一個 reader）

把兩邊 `positions` 用 `sec_id` 對齊,逐筆算 `qty_face` 與 `mv_usd` 的差。9 筆裡 6 筆對不上:

- 3 筆一致:EQ-AAPL / EQ-MSFT / EQ-NVDA
- 6 筆有差:EQ-SPY、FI-BUND、FI-GB123、EQ-VRT、FI-XYZ、CA-USD

reader 的分類欄(`suspected_cause`)鎖成固定 enum(`temporal_cutoff` / `system_drift` / `reclass` / `unknown`),不給自由發揮。

### 2.4 追根因 + 獨立 critic 複核（濾誤報）

對每筆差異拿可信佐證(未交割清單 / 匯率表 / 容差政策)反查,critic 做對抗式 review:

- **EQ-SPY** → `asset_class` Equity vs Funds/ETF,但 qty/MV 一致 → **重分類**,淨額 0 → 濾。
- **FI-BUND** → MV +300;EUR/USD GL 1.08000 vs custody 1.08004,相對差 0.0037% < 0.05% 容差 → **FX 進位** → 濾。
- **FI-GB123** → MV −500,000 = `get_pending_settlements` 的 TRD-9001 買單(5/2 交割) → **時間差** → 濾。
- **EQ-VRT** → 子帳多 2,500 股,**不在**未交割清單 → 真實(GL 漏記買單)→ 留。
- **FI-XYZ** → GL 多 1,000,000 面額,不在未交割清單 → 真實(GL 未沖已處分)→ 留。
- **CA-USD** → 子帳現金少 600,000,非 FX(USD)、不在未交割清單 → 真實(不明)→ 留升級。

> **critic 自我修正(本次真實發生)**:第一版自動分類器把 **CA-USD 誤判成 FX 進位**(因為它 qty 兩邊都 0、只有 MV 差,而表上剛好有一個在容差內的 EUR/USD pair)。critic 反查發現:CA-USD 是 USD 現金、根本沒有外幣換算,且它自身 MV 相對差 600,000/3,000,000 = **20%**,遠超 0.05%。修正規則:FX 進位只適用於「該部位**自身**相對差也在容差內、且確為外幣部位」。修正後 CA-USD 正確歸為真實 break。這正是這支 agent 要有獨立第二雙眼的理由 —— 漏報(under-report)比誤報更危險。

### 2.5 產出例外報告

```text
● Write(out/gl_recon_exceptions_2026-04-30.md)
  ⎿  逐筆比對表 + 3 筆誤報佐證 + 3 筆真實 break 根因追蹤 + 升級清單
```

結果:9 筆 = 3 一致 / 3 誤報(濾除)/ 3 真實 break。

### 🟡 濾掉的誤報（附 MCP 佐證）

- **EQ-SPY** — 僅 `asset_class` 不同(Equity vs Funds/ETF),qty/MV 一致 → 重分類
- **FI-BUND** — MV +$300,相對 0.0037% < 0.05% FX 容差 → 匯率進位
- **FI-GB123** — −$500,000 = 未交割買單 TRD-9001(trade 4/29、settle 5/2)→ 時間差,5/2 後消除

### 🔴 真實例外（升級,淨額 $1,350,000）

| 優先 | 項目 | 金額 | 根因 |
|------|------|------|------|
| 1 | CA-USD 現金 | $600,000 | 保管較 GL 少,查無佐證 → 立即對銀行流水 |
| 2 | FI-XYZ 公司債 | $1,000,000 | GL 多 1,000,000 面額,疑已處分 GL 未沖 |
| 3 | EQ-VRT | $250,000 | 子帳多 2,500 股,疑買單 GL 未入帳 |

### 關鍵判讀

- 總差異 $1,849,700 = 已解釋 $499,700(時間差+FX)+ 真實 $1,350,000 ✓ 對得上
- 方向驗證:GB123 時間差會使**子帳現金偏高**,與現金實況**偏低 $600k** 方向相反 → 證明現金缺口是獨立真實 break,不能用該時間差打發
- 現金 $600k 列最高優先(金額大、無佐證);原因不明只標升級、不臆測
- **agent 永不過帳**:本報告只是給控制員簽核的例外清單

## 3. Excel 對帳底稿（live formulas,tie-out 檢查）

底稿的 build script **直接讀 `mcp_pulls/*.json`**,不寫死任何數字,確保底稿可溯源回 MCP 回傳。

```bash
cd "<REPO>/docs/outputs/mcpBased/gl-conciler/scripts" && PYTHONUTF8=1 python build_gl_recon.py
```

```text
SAVED .../out/GL_Recon_Workpaper_2026-04-30.xlsx  sheets: ['Break Analysis', 'Recon', 'Escalation']
total diff 1,849,700 | real 1,350,000 | explained 499,700 | real+expl 1,849,700 -> tie OK
categories: {EQ-AAPL: Match, EQ-MSFT: Match, EQ-NVDA: Match, EQ-SPY: FP-Reclass,
             FI-BUND: FP-FX, FI-GB123: FP-Timing, EQ-VRT: REAL, FI-XYZ: REAL, CA-USD: REAL}
```

底稿三頁:

- **Recon** — 9 筆逐筆比對,Category 分類(藍字可改),真實 break / 已解釋欄由公式自動拆解,含 2 個 tie-out 檢查(MV差合計 = GL−子帳;真實+已解釋 = MV差合計)
- **Break Analysis** — 總差異 $1,849,700 = 已解釋 $499,700 + 真實 $1,350,000,跨頁連結 + tie-out 檢查
- **Escalation** — 3 筆真實 break 升級清單 + GB123 監控(明寫「給控制員簽核;agent 不過帳」)

## 4. 完成

① 例外報告 ✅ `out/gl_recon_exceptions_2026-04-30.md`
② Excel 對帳底稿 ✅ `out/GL_Recon_Workpaper_2026-04-30.xlsx`(tie-out 通過)
③ MCP 原始證據 ✅ `mcp_pulls/*.json`(6 個工具回傳 + 2 份 `_tools` 清單)

6 個 MCP 工具呼叫全成功,埋的 3 真 3 假全數正確處理(留真、濾假),自動分類器一度把 CA-USD 誤判成 FX、由 critic 反查修正。
