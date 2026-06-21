# 📅 月底結帳（month-end-closer）— 執行紀錄（MCP 版）

> 這版跟 fileBased 的差別:agent 的輸入**不再是手餵的 `samples/*.md`**,而是從 `internal-gl`
> MCP（唯讀總帳)**即時拉**。所以下面看到的是 **MCP tool call + args**,不是 file read。
> 原始 MCP 回傳全部存在 `./mcp_pulls/*.json`(等同 fileBased 的 `samples/`)。全部 mock / dev 假資料。

## 安裝外掛

```text
❯ /plugin install month-end-closer@fsi-local
  ⎿  ✓ Installed month-end-closer. Run /reload-plugins to apply.
```

## 使用者請求

> 使用者:幫 Aurora Capital Management LLC 跑 2026-04 月結。資料直接從 `internal-gl` GL MCP 拉
> (試算表 + 分錄),估列應計、做應付費用結轉、對變動大的科目寫差異說明,組裝成結帳包給控制員簽。

月結任務,資料源是 MCP。先用 harness 探索 server,確認合法的 entity / period。

## 步驟①:探索 + 拉試算表（GL MCP,唯讀）

harness:`docs/outputs/mcpBased/_harness/mcp_client.py`(真正的 stdio MCP client)。
寫 spec 到 `scripts/pull.json`,批次模式一次叫起 server 打多個工具,`out_dir` 用絕對 Windows 路徑。

```bash
cd ".../docs/outputs/mcpBased/_harness" && PYTHONUTF8=1 \
  python mcp_client.py --spec ".../month-end-closer/scripts/pull.json" 2>/dev/null
```

**MCP 工具呼叫(server = `internal-gl`):**

```text
call_tool list_entities()
  ⎿  trial_balance_entities: ["Aurora Capital Management LLC"]
     trial_balance_periods : ["2026-04"]
     gl_position_funds     : ["Aurora Growth Fund III"]
→ 確認 entity / period 合法。
```

```text
call_tool get_trial_balance(entity="Aurora Capital Management LLC", period="2026-04")
  ⎿  status: "pre-close"  currency: USD  18 lines
     total_debits  : 21,380,000
     total_credits : 21,380,000
     difference: 0.0   balanced: true ✓
```

→ 試算表本身已平衡(Dr=Cr=21,380,000),狀態 pre-close(應計未估列)。結帳工作在此之上做。

## 步驟②:drill 大變動科目的分錄(解釋 flux 的證據)

對 movement 最大的科目逐一 `get_journal_entries` drill。從 TB 看,費用端跳最大的是
專業服務費(+350k / +87.5%)、差旅(+200k / +133%)、薪酬(+150萬)、IT(+100k);
負債端 2100 應付費用 −200k(沖回)。針對這些打分錄:

```text
call_tool get_journal_entries(entity=..., account="6200")   # 專業服務費
call_tool get_journal_entries(entity=..., account="6400")   # 差旅
call_tool get_journal_entries(entity=..., account="6300")   # IT
call_tool get_journal_entries(entity=..., account="6000")   # 薪酬
call_tool get_journal_entries(entity=..., account="2100")   # 應付費用(沖回)
call_tool get_journal_entries(entity=..., account="6600")   # 折舊
call_tool get_journal_entries(entity=..., account="6100")   # 租金
call_tool get_journal_entries(entity=..., start_date="2026-04-01", end_date="2026-04-30")  # 全月
call_tool get_account_balance(entity=..., account="2100", period="2026-04")
call_tool get_account_balance(entity=..., account="6200", period="2026-04")
```

**harness bug(發現並已中央修正):** 共用 `mcp_client.py` 一開始的 `_extract()` 只讀
`CallToolResult.content[0]`。對「回純量/dict」的工具沒問題,但 `get_journal_entries` 回的是
**list**,FastMCP 會把 list 每個元素序列化成「**一個獨立的 content block**」。我直接驗證:

```text
get_journal_entries(account="6200") → CallToolResult.content blocks = 2 (structuredContent = None)
舊版 harness 只存到 content[0] → 6200 只看到 1 筆(JE-4012),漏了 JE-4025。
```

→ 這不是 server bug,是 harness 對 list 型工具的解析不完整。**已在 `_harness/mcp_client.py` 中央修正**
(依「已知會回 list 的工具集」把所有 content block 重組回完整 list)。重跑標準 `scripts/pull.json`
(同一支 client、同一份 spec)就拿到完整 JE,**不需要任何 per-agent 補丁**:

```text
03_je_6200_professional_fees: 2 JE line(s)   ← JE-4012 220k + JE-4025 130k = 350k ✓
04_je_6400_travel            : 1 JE line(s)   ← JE-4018 200k
10_je_all_april              : 10 JE line(s)  ← 全月 big movers
```

**drill 拿回的關鍵分錄(這就是 flux 的底層解釋):**

| 科目 | JE | 說明 | 金額 |
|---|---|---|---:|
| 6200 專業服務費 | JE-4012 | 外部法律顧問費用(併購盡調) | 220,000 |
| 6200 專業服務費 | JE-4025 | FY2026 審計進度帳單 | 130,000 |
| 6400 差旅 | JE-4018 | 投資人年會及募資差旅 | 200,000 |
| 6300 資訊技術 | JE-4022 | 雲端基礎設施與資安訂閱 | 100,000 |
| 6000 薪酬 | JE-4001 | 4月固定薪資與福利 | 1,500,000 |
| 2100 應付費用 | JE-4002 | 沖回3月應計(發票已到並支付) | 200,000 (Dr) |
| 6600 折舊 | JE-4031 | 固定資產月折舊(Manual) | 50,000 |

→ **重點:** fileBased 那版把專業服務費 ~350k、差旅 200k 標成「來源不明、需查 GL」。
這次因為 drill 了 MCP 分錄,**兩條都查到底層 JE 了**——專業服務費 = 法律盡調 + 審計帳單,
差旅 = 投資人年會。這就是接上真實 GL MCP 後,「flux 可解釋性」實際發生的地方。

## 步驟②.5:內建自我驗證 — 分錄對得上試算表嗎?

agent 沒有外部 critic,驗證內建在「對得上」。我把每個科目的 4 月 JE 淨額(換算到正常餘額方向)
跟 MCP 試算表的 movement 逐一比對:

```text
2000(Cr) JE→bal +200,000  TB movement +200,000  ✓
2100(Cr) JE→bal -200,000  TB movement -200,000  ✓
4000(Cr) JE→bal +2,200,000 TB movement +2,200,000 ✓
6000(Dr) JE→bal +1,500,000 TB movement +1,500,000 ✓
6100 +200,000 ✓  6200 +350,000 ✓  6300 +100,000 ✓
6400 +200,000 ✓  6500 +80,000 ✓   6600 +50,000 ✓
→ 10/10 科目全對。GL 資料一致。
```

> 註:JE big-mover 表自身 Σ Dr(2,680,000)≠ Σ Cr(2,400,000)——正常,因為它只收「異動大的單邊」,
> 對手科目(現金/應收等)不在表內(README 載明)。我們驗的是「每科目 JE 淨額 = TB movement」。

## 步驟③:建應計 + 結轉 + 差異說明

- **應計(A1/A2/A3,合計 +275,000)**:`internal-gl` 是唯讀總帳、不提供應計排程工具,故三筆
  比照公司應計政策 / 任務輸入(IT 75k 自動沖回、分紅 100k、審計 100k),全 Dr 費用 / Cr 2100。
- **2100 結轉**:期初 1,200,000(MCP `get_account_balance.prior_ytd`)− 沖回 200,000(JE-4002)
  + 新估列 275,000 = **期末 1,275,000**;結帳前 1,000,000 與 MCP TB 2100 餘額逐一吻合。**foot ✓**
- **差異說明**:用「4 月當月(JE drill 加總)vs 前 3 月平均月跑率」判讀。租金/IT/薪酬/其他營運
  皆持平跑率(正常);專業服務費、差旅雖超門檻,但**已由 MCP JE 完全解釋**;**折舊**因 MCP 僅
  2026-04 在檔、看不到 1–3 月,留**時點疑慮**標示待查(原因不明就標,不瞎掰)。

## 步驟④:組裝結帳包(markdown + xlsx,agent 永不過帳)

```text
Write(out/close_package_2026-04.md)        # 7 節:摘要/應計/結轉/TB影響/flux/tie-out/簽核欄
Bash(python scripts/build_close_pack.py)   # 用 mcp_pulls 的 JSON 產 Excel 活公式工作底稿
```

```text
SAVED out/Close_Package_2026-04.xlsx
sheets: ['Accruals & JEs','Trial Balance','Roll-forward 2100','Variance','JE Drill (MCP)']
---- foot checks (python recompute) ----
pre-close  Dr=21,380,000  Cr=21,380,000  balanced=True
post-close Dr=21,655,000  Cr=21,655,000  balanced=True
2100 roll-forward: 1,200,000 -200,000 + 275,000 = 1,275,000 (pre-close 1,000,000 = TB ✓)
YTD net income pre=200,000 -> post=-75,000
```

本機無 LibreOffice,故以獨立 Python 重算驗證公式邏輯(藍字=MCP 輸入、綠字=活公式);
xlsx 內亦放 `=IF(ROUND(...))` 的 foot-check,controller 改任一輸入會自動重算。
分錄維持**草稿未過帳**狀態。

## 產出檔案

```text
mcp_pulls/
  ├─ _tools.json                       ← internal-gl 工具清單(5 個)
  ├─ 01_list_entities.json
  ├─ 02_trial_balance.json             ← Dr=Cr=21,380,000 ✓
  ├─ 03_je_6200_professional_fees.json ← 2 筆(法律盡調 + 審計帳單)
  ├─ 04..09_je_*.json                  ← 各科目 drill
  ├─ 10_je_all_april.json              ← 全月 10 筆 big movers
  └─ 11/12_balance_*.json              ← 2100 / 6200 單科目餘額
out/
  ├─ close_package_2026-04.md          ← 主產出(結帳包)
  └─ Close_Package_2026-04.xlsx        ← 5 分頁活公式工作底稿 + foot-check tie-out
scripts/
  ├─ pull.json                         ← MCP pull spec(批次)
  └─ build_close_pack.py              ← 從 mcp_pulls 產 xlsx,內含 python 重算驗證
```

月結完成。Dr=Cr 平衡、2100 結轉對得上 1,275,000、分錄 10/10 對上 TB movement、flux 大多由
MCP JE 解釋(僅折舊時點留 flag)。分錄全為草稿,**等 controller 簽核才過帳**。
