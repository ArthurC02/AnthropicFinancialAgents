# 🧾 Statement Auditor（對帳單稽核）

> **用途**：對帳單稽核助理，在出資人對帳單寄出去前逐欄核對基金淨值，最後產一份例外清單跟放行建議。

`出資人（LP）對帳單 → 對照基金淨值（NAV）核對 → 揪差異 → 過/留建議（分送前最後把關）`

| 家族 | 用戶 | 頻率 | 風險 |
|---|---|---|---|
| 基金行政 | 基金會計 | 出資人對帳單分送前 | 🔴 高 |

## 一、Workflow

```
 對帳單批次 + 基金 NAV pack
     │
     ▼
┌────────────┐  ┌──────────┐  ┌────────┐
│①讀對帳單   │─►│②逐欄核對 │─►│③標差異 │─► IR 分送（人工簽核後）
│reader      │  │NAV MCP   │  │flagger │
│碰髒·無MCP  │  │          │  │產清單  │
└────────────┘  └──────────┘  └────────┘
```
> 基金淨值（NAV）｜出資人（LP，把錢交給基金的機構）　|　用途：對帳單寄出去前的最後一道檢查

**步驟拆解**
1. **讀對帳單** — 把每位出資人對帳單上回報的餘額讀出來。
   - 步驟說明：把髒資料隔離開——由 statement-reader 這個 sub-agent（只能 Read／Grep、沒有 MCP）來讀，對帳單一律當成不可信的外來資料，免得污染後面的核對流程。
2. **逐欄核對** — 拿每個欄位跟基金的官方淨值資料一一比對，這是這個 agent 最核心的工作。
   - 步驟說明：用 MCP 逐欄比對，比對本身就是驗證——透過 `nav` MCP（基金淨值來源，唯讀）用 `nav-tieout` 這個 skill 逐欄對 NAV pack 比，這個 tie-out 動作本身就是驗證（agent 自己就是驗證者）。
3. **標出差異** — 把對不上的地方整理成一份例外清單，並給出「可放行／需再查」的建議。
   - 步驟說明：產例外清單——由 flagger 把對不上的欄位整理成例外清單跟簽核表，標上疑似原因跟過／留建議（`audit-xls` 檢查、`xlsx-author` 產出報告檔）。

## 二、風險與把關

```
 agent ──pass/hold建議──► IR 人工簽核 ⚖️      ✗ agent 不分送

 LP對帳單(外來·可能來自不可控的上游系統) ──► reader(只Read/Grep·無MCP) ──► 核對
 (不可信)
```
> 最後防線：不分送（IR 簽核後才寄）

## 三、技術架構

**技能鏈**
```
nav-tieout ──► (audit-xls / xlsx-author)
逐欄對 NAV     檢查／產出報告
```
**Skill（共 3 支）**　`nav-tieout` 對帳單 vs NAV 逐欄核對 · `audit-xls` 檢查Excel · `xlsx-author` 產出報告檔
**MCP（1 個）**　`nav` 基金淨值來源（唯讀）

> 工具：讀／搜尋＋NAV MCP　⚠️ 不能寫檔·不能委派　|　模型：opus-4-7

**外掛 vs CMA（兩種安裝）**
```
 外掛版 (真人盯)         CMA版 (雲端·無頭)
 ┌────────────┐         ┌──────────────────────────┐
 │ 單一agent  │         │ 主代理 (不寫·不碰髒)     │
 │ 工具收窄   │         │  ├ statement-reader 讀單·碰髒│
 └────────────┘         │  ├ reconciler   核對     │
                        │  └ flagger      唯一可寫 │
                        └──────────────────────────┘
```
> 🎯 招牌設計：整支 agent 本身就是「驗證者」——它的工作就是 tie-out（逐欄把 LP 對帳單對 NAV pack），驗證是核心功能、不是附加步驟。statement-reader 的 schema 可一次收到 2000 個 LP，撐得住批量分送場景

**改哪裡（快速 map）**

| 想改 | 動這個檔 |
|---|---|
| 流程／stop 點／守則 | `agents/statement-auditor.md` 的 Workflow／Guardrails |
| 用哪些 skill | 同檔的 Skills 行 |
| 欄位對應／容差 | `nav-tieout/SKILL.md` 真本 → sync |
| 幾個 sub-agent | `cookbooks/statement-auditor/agent.yaml` 的 callable_agents |
| statement-reader 輸出限制 | `subagents/statement-reader.yaml` 的 output_schema |

> 通用改法見 [Customizing.md](../Customizing.md);上線要補的見下方 §四。

**跨 agent**　基金行政家族 ┄ 跟〔valuation-reviewer〕一樣都是季末/分送前的把關

## 四、上線前要補齊（客製化）

```
 Anthropic 參考骨架    ＋    貴公司要補的    ＝    可實際上線
```
- 🔌 **接真實 NAV 來源**：`nav` MCP 還是 placeholder（佔位，repo 裡沒定義）
  - 外掛 → 新增 `plugins/vertical-plugins/fund-admin/.mcp.json`（目前不存在）
  - CMA → 設 env var `NAV_MCP_URL`（或改 `managed-agent-cookbooks/statement-auditor/agent.yaml`）
  - 🛠️ MCP 要做到：依基金/LP/欄位查 NAV pack 的數值（給逐欄比對用；規格見 `nav-tieout` 這個 skill）
- 📐 **欄位對應**：LP 對帳單欄位 ↔ NAV pack 欄位的對應表 → `plugins/vertical-plugins/fund-admin/skills/nav-tieout/SKILL.md`
- ✏️ **調整範圍** → `plugins/agent-plugins/statement-auditor/agents/statement-auditor.md`
- 👤 **人工覆核不變**：只建議 pass/hold，要 IR 簽核才分送

> ⚠️ skill 一律改 `vertical-plugins/` 的 source(真本)，改完跑 `python3 scripts/sync-agent-skills.py` sync。

## 五、導入評估

| 面向 | 評估 |
|---|---|
| **導入風險** | 🔴 高 — 這是出資人（LP）對帳單對外分送前的最後一道把關，數字核對錯了，直接影響對 LP 的正式財務報告跟機構誠信；雖然 agent 只給 pass/hold 建議、要等投資人關係（IR）人工簽核才寄出，但這是合規等級的對外文件，不容差錯。 |
| **導入成本** | 🔴 高 — `nav` MCP 還是 placeholder（佔位），要實接基金淨值（NAV）來源（依基金／LP／欄位查 NAV pack 數值）；還要客製 LP 對帳單欄位 ↔ NAV pack 欄位的對應表跟比對容差，這是要自建內部系統整合的重度工程。 |
| **適用單位** | 基金行政部、基金會計、投資人關係（IR） |
| **單位中角色** | 基金會計（下指令＋審例外清單）· 投資人關係（IR，簽核＋對外分送）· 行政主管（覆核過／留決定） |

**最有機會成功的場景**
1. **季末／月末對帳單批次分送前的逐欄把關** — 例行的大批量對帳單寄出前，自動逐欄對 NAV pack 揪差異，把人工核對變成只審例外清單，省時又少漏。
2. **新基金或新 LP 上線的首次對帳驗收** — 欄位對應跟容差還沒穩定的時候，用它跑一遍揪出系統性的對應錯誤，當作上線前的驗收關卡。
3. **稽核／合規抽查的差異留痕** — 要對外或對內部稽核拿出對帳依據時，自動產例外清單跟簽核表，留下可追溯的核對紀錄。
