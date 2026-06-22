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
> 🎯 招牌設計：這裡的驗證＝對照政策——把 GP 報的 marks 比對公司估值政策，不照單全收。package-reader 的 method 欄鎖成 enum（`market_multiple`／`dcf`／`recent_round`／`cost`／`other`），注入塞不進來。簽核是 IR＋CCO 雙簽，是全 10 支裡最高的簽核層級

> 內部報酬率（IRR）、投入本金倍數（MOIC），這兩個都是私募基金（PE）拿來衡量績效的指標

**跨 agent**　基金行政家族 ┄ 跟〔statement-auditor〕一樣是季末把關；跟〔model-builder〕（承做估值）劃清邊界

## 四、要調什麼、改哪裡（業務內容調整表）

```
 Anthropic 參考骨架    ＋    貴公司要補的    ＝    可實際上線
 (提示詞·技能·流程)          (資料·規則·範本)
```

> 先分清楚：門檻、規則、清單多半設計成「執行時餵」就好；要變成公司預設才改 source。

| 想調的業務內容 | 改哪個檔 | 怎麼改 |
|---|---|---|
| 估值政策／marks 對照規則 | `portfolio-monitoring` SKILL.md · Policy 段 | 臨時 prompt 給；永久改值 → sync |
| IRR／MOIC 假設（進場倍數·持有期·槓桿） | `returns-analysis` SKILL.md · Assumptions 段 | 改假設值 → sync |
| Waterfall／carry／hurdle 條款 | `returns-analysis` SKILL.md · Waterfall 段 | 改條款定義 → sync |
| IC 備忘錄格式與欄位 | `ic-memo` SKILL.md | 改結構與欄位 → sync |
| 報告範本（xlsx 格式） | `xlsx-author` SKILL.md | 換範本 → sync |
| 流程／stop 點／守則／掛哪些 skill | `agents/valuation-reviewer.md`（Workflow／Skills 行） | 直接改劇本（外掛＋CMA 同時生效） |
| 接真實投組系統（外掛） | `plugins/vertical-plugins/private-equity/.mcp.json` | `portfolio` server 的 `url` 從 `127.0.0.1:8003` 改指真實系統（別改 server 名） |
| 接真實投組系統（CMA） | `managed-agent-cookbooks/valuation-reviewer/agent.yaml` | 設 env var `PORTFOLIO_MCP_URL` |
| sub-agent 數量／reader 輸出限制 | `agent.yaml`／`subagents/package-reader.yaml` | 改 callable_agents／output_schema |

**三條路線**
- ① 臨時（不改檔）：門檻／政策／清單直接在 prompt 或 `steering-examples.json` 給。
- ② 永久（改預設）：改 `vertical-plugins/` 的 SKILL.md 真本 → `python3 scripts/sync-agent-skills.py` → `check.py`（drift 會擋 commit；別手改 bundle 的 copy）。
- ③ 接系統：改 `.mcp.json` 的 url（外掛）或 env var（CMA）；**server 名別改**。

**接真實系統要做到**（上線必補）
- 🛠️ `portfolio`：依基金／投組公司查估值輸入與政策標記（給對照政策複核用；規格見 `portfolio-monitoring` SKILL.md）
- 👤 **人工覆核不變**：只備 LP 報告，IR＋CCO 簽核後才對外分送（agent 不對外分送）

> 通用改法見 [Customizing.md](../Customizing.md)。這支刻意把公司專屬的東西留空，你填上去才算完整。

## 五、導入評估

| 面向 | 評估 |
|---|---|
| **導入風險** | 🔴 高 — 季末估值複核跟收益分配（waterfall）直接決定管理團隊的績效分成（carry）跟每位出資人（LP）分多少錢，而且產出是對外的正式報告。雖然 agent 只備稿、要等投資人關係（IR）＋法遵長（CCO）人工簽核才分送，但還是落在財務誠信＋對外文件的高風險範疇。 |
| **導入成本** | 🔴 高 — `portfolio` MCP 雖然已接好本地 mock（可離線端到端跑），但上線要把它從 mock repoint 到真實的投組（portfolio）資料來源；還要客製估值政策、分配 waterfall 邏輯（carry 條款）跟出資人報告 template，整合工程不小。 |
| **適用單位** | 基金行政／基金會計部、私募基金（PE）後台營運 |
| **單位中角色** | 基金會計主管（下指令＋覆核估值與分配）· 投資人關係（IR）（覆核並簽核 LP 報告）· 法遵長（CCO）（合規簽核＋對外分送把關） |

**最有機會成功的場景**
1. **季末投組估值複核** — 週期固定、流程明確的季底估值對照政策檢查，把 GP 報的 marks 對照估值政策攔錯，CP 值最高。
2. **收益分配（waterfall）試算備稿** — 算基金淨值（NAV）、carry 跟各 LP 分配，產出一份給 IR＋CCO 覆核的草稿，省下大把人工試算。
3. **出資人（LP）季報報告包初稿** — 把複核後的數字整理成一份 structured 的 LP 報告包初稿，等人工簽核後分送。

## 六、它補的是哪一段（與成熟系統／自建的分工）

它不是投組監控平台（Chronograph、Burgiss／iLEVEL）、也不是基金行政系統，而是坐在那些系統「上面」做判斷的那一層。把季末估值複核拆兩段就清楚：

| 環節 | 誰做 |
|---|---|
| 收 GP 報的 marks、存投組資料、算 NAV 與分配的確定性計算 | 🏦 成熟系統（投組監控平台、基金行政）或自建腳本——確定、量大、便宜 |
| 拿 marks 對照估值政策複核（不照單全收）、算 waterfall 與 carry、備 LP 報告 | 🤖 本 agent——要判斷、要對政策的那段 |
| 拍板、簽核後對外 | 👤 投資人關係（IR）＋法遵長（CCO） |

**優勢來源**
- **對成熟系統**：它們把 GP 報的 marks 收進來、攤給你看就停了，不會替你判這個 mark 合不合估值政策；agent 補的正是「對照政策複核＋算分配＋備報告」這段。
- **對自建腳本**：不用把每條估值方法門檻、每種 carry waterfall 條款寫死；讀得懂投組財報、估值佐證去推理，條款或格式一變也不必改 code。

**什麼時候用哪個**
- 量大、估值方法明確、格式穩定 → 成熟系統／腳本。
- 估值要對政策判斷、佐證雜亂、要算 waterfall 並產報告 → agent。
- 要當官方估值來源、要正式記帳 → 成熟系統（agent 不對外分送）。
- ❌ 純高量固定彙總別用 agent（又貴、判斷又非確定）。

## 七、Skill 白話

每支 skill 是一份「給 AI 看的作業手冊」。算術與驗證都導向 Excel 公式，skill 只負責判斷與接線。

- **`returns-analysis` IRR／MOIC 報酬**：依進場／槓桿／出場倍數、成長、持有期算 MOIC、IRR，做報酬歸因（成長／倍數擴張／還債貢獻）跟雙因子敏感度與情境表，產出可放 IC deck 的報酬摘要。
- **`portfolio-monitoring` 對照政策監控**：吃投組公司財報包，抽 KPI（營收、EBITDA、淨負債、槓桿、契約遵循）對 budget 比，用綠／黃／紅標差異，產一份董事會等級的摘要跟給管理層的問題清單。
- **`ic-memo` 投資委員會備忘錄**：把盡調、財務分析、交易條款整理成一份結構化的 IC 備忘錄（執行摘要、投資論點、條款、報酬、風險與建議），表格要 tie，多空兩面都據實寫。
- **`xlsx-author` 產出報告檔**：無頭模式下用 Python 把 .xlsx 寫成檔（藍＝輸入、黑＝公式、綠＝連結，計算格一律公式）；有開著的 Excel 時改用 office 工具直接操作。
