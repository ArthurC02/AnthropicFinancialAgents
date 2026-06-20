# 💰 Valuation Reviewer（估值複核）

> **用途**：投組估值複核助理，季末幫你複核投資標的估值、算收益分配，最後產一份給出資人的報告包。

`普通合夥人（GP）估值包 → 跑估值模板 → 算收益分配（waterfall）→ 備妥出資人（LP）報告（季末複核）`

| 家族 | 用戶 | 頻率 | 風險 |
|---|---|---|---|
| 基金行政 | 基金會計主管 | 季底投組估值複核 | 🔴 高 |

## 一、Workflow

```
 基金 + as-of 日期
     │
     ▼
┌──────────────┐  ┌──────────────────┐  ┌────────────┐  ┌──────────┐
│①讀GP估值包   │─►│②跑估值模板       │─►│③算waterfall│─►│④備LP報告 │─► IR+CCO簽核 ⚖️
│package-reader│  │returns-analysis  │  │NAV+分配    │  │publisher │
│碰髒·無MCP    │  │portfolio-monitor │  │            │  └──────────┘
└──────────────┘  └──────────────────┘  └────────────┘
                   把reported marks對照policy
```
> 普通合夥人／基金管理人（GP）｜收益分配（waterfall）：基金收益依約定順序，分給 GP 的績效分成（carry）與出資人（LP）　|　刻意不做：交易時的承做估值（用 model-builder）

**步驟拆解**
1. **讀估值資料** — 從每家被投資公司的估值報告裡，讀出回報的估值數字。
   - 步驟說明：把外來資料隔離開來讀——由 package-reader 這個 sub-agent（只能 Read/Grep、沒有 MCP）來解析各被投資公司的估值輸入，GP 估值包算不可信來源，所以隔離起來碰這些髒資料。
2. **複核估值** — 拿這些數字對照公司的估值政策，檢查合不合理。
   - 步驟說明：對照政策複核——透過 portfolio MCP（投組資料，唯讀）接資料源，用 `returns-analysis`、`portfolio-monitoring` 這兩個 skill 把回報估值（marks）對照估值政策檢查。
3. **計算收益分配** — 算出基金整體淨值、管理團隊的績效分成，以及每位出資人分得多少。
   - 步驟說明：算收益分配——算基金層淨值（NAV）、績效分成（carry）跟出資人（LP）分配（`ic-memo` 這個 skill）。
4. **備妥出資人報告** — 整理成給出資人的報告包，準備送審。
   - 步驟說明：產報告等送審——交給 publisher 用 `xlsx-author` 產出、備好 LP 報告包，等 IR＋CCO 簽核後才分送。

## 二、風險與把關

```
 agent ──備好LP報告──► IR + CCO 人工簽核 ⚖️      ✗ agent 不對外分送

 GP估值包(外來) ──► package-reader(只Read/Grep·無MCP) ──► 跑模板
 (不可信)
```
> 守則：GP 報的估值要對照公司政策（不照單全收）　|　最後防線：不對外分送（要 IR+CCO 簽核）

## 三、技術架構

**技能鏈**
```
returns-analysis ──► portfolio-monitoring ──► (ic-memo / xlsx-author)
報酬分析           對照政策監控            備忘錄／產出報告
```
**Skill（共 4 支）**　`returns-analysis` IRR/MOIC 報酬 · `portfolio-monitoring` 對照政策監控 · `ic-memo` 投資委員會備忘錄 · `xlsx-author` 產出報告檔
**MCP（1 個）**　`portfolio` 投組資料來源（唯讀）

> 工具：讀／搜尋＋Portfolio MCP　⚠️ 不能寫檔·不能委派　|　模型：opus-4-7

**外掛 vs CMA（兩種安裝）**
```
 外掛版 (真人盯)         CMA版 (雲端·無頭)
 ┌────────────┐         ┌──────────────────────────┐
 │ 單一agent  │         │ 主代理 (不寫·不碰髒)     │
 │ 工具收窄   │         │  ├ package-reader 讀GP包·碰髒│
 └────────────┘         │  ├ valuation-runner 跑模板│
                        │  └ publisher      唯一可寫 │
                        └──────────────────────────┘
```
> 內部報酬率（IRR）、投入本金倍數（MOIC），這兩個都是私募基金（PE）拿來衡量績效的指標

**跨 agent**　基金行政家族 ┄ 跟〔statement-auditor〕一樣是季末把關；跟〔model-builder〕（承做估值）劃清邊界

## 四、上線前要補齊（客製化）

```
 Anthropic 參考骨架    ＋    貴公司要補的    ＝    可實際上線
```
- 🔌 **接真實投組來源**：`portfolio` MCP 還是 placeholder（佔位，repo 裡沒定義）
  - 外掛 → 新增 `plugins/vertical-plugins/private-equity/.mcp.json`（目前不存在）
  - CMA → 設 env var `PORTFOLIO_MCP_URL`（或改 `managed-agent-cookbooks/valuation-reviewer/agent.yaml`）
  - 🛠️ MCP 要做到：依基金/投組公司查估值輸入跟政策標記（給對照政策用；規格見 `portfolio-monitoring`）
- 📐 **估值政策／waterfall 條款**：估值方法門檻、carry 分配條款 → `plugins/vertical-plugins/private-equity/skills/portfolio-monitoring/SKILL.md`、`returns-analysis/SKILL.md`
- ✏️ **調整範圍** → `plugins/agent-plugins/valuation-reviewer/agents/valuation-reviewer.md`
- 👤 **人工覆核不變**：只備 LP 報告，要 IR+CCO 簽核才分送

> ⚠️ skill 一律改 `vertical-plugins/` 的 source(真本)，改完跑 `python3 scripts/sync-agent-skills.py` sync。

## 五、導入評估

| 面向 | 評估 |
|---|---|
| **導入風險** | 🔴 高 — 季末估值複核跟收益分配（waterfall）直接決定管理團隊的績效分成（carry）跟每位出資人（LP）分多少錢，而且產出是對外的正式報告。雖然 agent 只備稿、要等投資人關係（IR）＋法遵長（CCO）人工簽核才分送，但還是落在財務誠信＋對外文件的高風險範疇。 |
| **導入成本** | 🔴 高 — 要自建內部系統整合：`portfolio` MCP 還是 placeholder（佔位），要接真實的投組（portfolio）資料來源；還要客製估值政策、分配 waterfall 邏輯（carry 條款）跟出資人報告 template，整合工程不小。 |
| **適用單位** | 基金行政／基金會計部、私募基金（PE）後台營運 |
| **單位中角色** | 基金會計主管（下指令＋覆核估值與分配）· 投資人關係（IR）（覆核並簽核 LP 報告）· 法遵長（CCO）（合規簽核＋對外分送把關） |

**最有機會成功的場景**
1. **季末投組估值複核** — 週期固定、流程明確的季底估值對照政策檢查，把 GP 報的 marks 對照估值政策攔錯，CP 值最高。
2. **收益分配（waterfall）試算備稿** — 算基金淨值（NAV）、carry 跟各 LP 分配，產出一份給 IR＋CCO 覆核的草稿，省下大把人工試算。
3. **出資人（LP）季報報告包初稿** — 把複核後的數字整理成一份 structured 的 LP 報告包初稿，等人工簽核後分送。
