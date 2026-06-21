# 🧾 對帳單稽核（statement-auditor）— 執行紀錄（MCP 版）

> 這份對應 fileBased 的 `execution_history.md`，差別在：核對基準不再是人工餵的 `nav_pack.md`，
> 而是 **即時從 `nav` MCP server 拉**。`mcp_pulls/` 就是「真的有跑過 MCP」的證據。
> 全程 mock / dev 假資料。

## 安裝外掛

```text
❯ /plugin install statement-auditor@fsi-local
  ⎿  ✓ Installed statement-auditor. Run /reload-plugins to apply.
```

設定接 `nav` MCP（mock）：`mock-mcp/nav/server.py`（stdio，唯讀，基金 NAV 來源）。

## 使用者請求

> 使用者：手上有一份草稿 LP 對帳單要在分送前核對。請去 `nav` MCP 拉官方 NAV pack，逐欄 tie-out，
> 確認基金 NAV 對得上各 LP 期末合計、每位 LP 的資本帳各自 foot，把對不上的整理成例外清單，
> 給每筆「可放行／需再查」建議。

這正好對應 statement-auditor 的 `nav-tieout` 工作流程。心智模型：**我自己就是驗證者**——草稿對帳單是不可信外來輸入，
真值要去 MCP 拉，tie-out 這個動作本身就是稽核。

## ① 先探索:確認合法的 fund / as_of

照 RUNBOOK，先打 `list_funds` 拿合法參數,再打需要參數的工具。用 harness 批次模式（一次叫起 server 打三個工具）。

**MCP 呼叫清單（server = `nav`，stdio，透過 `_harness/mcp_client.py`）**

| # | tool | args | save_as | ok |
|---|---|---|---|---|
| 1 | `list_funds` | `{}` | `01_list_funds` | ✅ |
| 2 | `get_nav_build` | `{"fund":"Aurora Growth Fund","as_of":"2026-03-31"}` | `02_get_nav_build` | ✅ |
| 3 | `get_lp_capital_accounts` | `{"fund":"Aurora Growth Fund","as_of":"2026-03-31"}`（不帶 lp_id = 全部 LP） | `03_get_lp_capital_accounts` | ✅ |

pull spec:`scripts/pull.json`。執行指令:

```bash
cd ".../docs/outputs/mcpBased/_harness"
PYTHONUTF8=1 python mcp_client.py --spec ".../mcpBased/statement-auditor/scripts/pull.json" 2>/dev/null
```

harness 回報三筆 `ok: true`,原始 JSON 落地到 `mcp_pulls/`,另含 `_tools.json`(server 工具清單)。

`list_funds` 確認:`funds=["Aurora Growth Fund"]`、`as_of=["2026-03-31"]` —— 與任務給的 KEY IDENTIFIERS 一致,後兩個工具的參數合法。

## ② 拿回的關鍵數字(全部來自 MCP,沒有自己編)

**`get_nav_build`(基金層)**

- Total Assets 115,500,000 − Total Liabilities 3,062,500 = **Net Assets (NAV) 112,437,500** ✓(MCP 直接也給了 NAV 這一列,且自洽)
- Accrued Management Fee Payable = 562,500(待會跟各 LP 管理費合計對)

**`get_lp_capital_accounts`(各 LP + 欄位合計)**

| LP | 期初 | 出資 | 分配 | 損益 | 管理費 | 期末 |
|---|---:|---:|---:|---:|---:|---:|
| LP-001 | 40,000,000 | 5,000,000 | 2,000,000 | 4,000,000 | 250,000 | 46,750,000 |
| LP-002 | 30,000,000 | 0 | 1,500,000 | 3,000,000 | 187,500 | 31,312,500 |
| LP-003 | 20,000,000 | 2,000,000 | 0 | 2,000,000 | 125,000 | 23,875,000 |
| LP-004 | 10,000,000 | 0 | 500,000 | 1,000,000 | 0 | 10,500,000 |
| **totals** | 100,000,000 | 7,000,000 | 4,000,000 | 10,000,000 | **562,500** | **112,437,500** |

server 還回了 `totals` 物件(欄位合計),省得自己加。

## ③ 跑 tie-out(`scripts/audit.py`,以 MCP 拉回的數字當真值)

把計算寫成 script,避免手算出錯;真值一律讀 `mcp_pulls/*.json`。四道檢核:

- **CHECK 0｜MCP 基準自洽**:NAV 112,437,500 = Σ LP 期末 112,437,500 ✓;Total Assets − Total Liabilities = 112,437,500 ✓;四列各自 foot ✓。→ **基準本身完全乾淨**,可以拿來當尺。
- **CHECK 1｜草稿逐列 foot**:LP-002 **不 foot**(期初+出資−分配+損益−費 = 31,312,500,但草稿期末寫 31,321,500);其餘三列以各自(含錯誤)輸入自洽。
- **CHECK 2｜逐欄對 MCP**:抓到 5 個 cell 差異 → LP-001 管理費(−50,000)連帶期末(+50,000)、LP-002 期末(+9,000)、LP-003 出資(+500,000)連帶期末(+500,000)。
- **CHECK 3｜基金 NAV tie-out**:草稿合計期末 112,996,500 − NAV 112,437,500 = **+559,000**,不 tie。破口拆解:50,000 + 9,000 + 500,000 = 559,000,三筆 line item 完全解釋總缺口。

## ④ agent 怎麼判讀

- 三個根因(LP-001 費、LP-002 期末、LP-003 出資)全抓到,且點出合計兜不攏(+559,000)。
- LP-002 特別標出「自己加總也不 foot」(內部 footing 失敗),不是只跟基準比。
- LP-004 完全 tie,**判可放行,沒誤報**(對照組正確)。
- LP-001/LP-003 雖然「橫向 foot 會過」,但因為對 MCP 基準逐欄比,還是抓到 → 證明逐欄 tie-out 比只看 foot 更嚴。
- 守 guardrail:只給 pass/hold 建議,**未改對帳單、未分送**,等 IR 簽核。

## ⑤ 寫了哪些檔

```text
mcp_pulls/01_list_funds.json
mcp_pulls/02_get_nav_build.json
mcp_pulls/03_get_lp_capital_accounts.json
mcp_pulls/_tools.json
scripts/pull.json          ← MCP pull spec
scripts/audit.py           ← tie-out 計算(讀 mcp_pulls,印四道檢核)
scripts/build_xlsx.py      ← 產 Excel 底稿
out/result.md              ← 例外稽核報告(主產出)
out/audit_workpaper.xlsx   ← Tie-out / Exceptions / NAV_Build 三分頁底稿
execution_history.md / note.md
```

> 結論:整批 **不可分送(DO NOT DISTRIBUTE)**,LP-001/002/003 三筆更正後合計即 tie 回 112,437,500。
> 依規範未修改對帳單、未分送,flag 供 IR 複核。
