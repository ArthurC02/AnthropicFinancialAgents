# 🏗️ 技術總覽 — 一套方案怎麼運作

> 這份文件回答四個工程問題：**①** 為什麼同一個 agent 可以變成兩種產品？**②** 「外掛」跟「CMA」到底差在哪？**③** 十個 agent 各自要接哪些資料來源（MCP）？**④** 怎麼 deploy、怎麼維護？
> 名詞先講白話：**MCP（模型情境協定，Model Context Protocol）** 就是「讓 agent 接到外部系統（總帳、CRM、行情）的標準插座」；**CMA（Claude 託管代理，Claude Managed Agents）** 就是「把 agent deploy 到 Anthropic 的雲端，由它代跑、用 API 呼叫」。

---

## 一、一個來源，兩個輸出

整套方案的核心設計：**每個 agent 只寫一次系統提示（agent 的「人格與工作守則」），外面套兩層不同的殼，就變成兩種可交付的產品。**

```
                         ┌──────────────────────────────────┐
                         │   唯一來源（canonical source）     │
                         │  agents/<slug>.md                  │
                         │  ＝ 系統提示：角色、流程、紀律、     │
                         │     可用工具、子代理規則            │
                         └──────────────┬───────────────────┘
                                        │ 同一份內容，套兩種殼
                  ┌─────────────────────┴─────────────────────┐
                  ▼                                            ▼
   ┌──────────────────────────────┐          ┌──────────────────────────────┐
   │ 殼 A：外掛（Plugin）           │          │ 殼 B：CMA 食譜（Cookbook）     │
   │ plugins/agent-plugins/<slug>/ │          │ managed-agent-cookbooks/<slug>/│
   │  ├ .claude-plugin/plugin.json │          │  ├ agent.yaml（system＋skills）│
   │  ├ agents/<slug>.md  ←來源    │          │  ├ subagents/*.yaml（葉子工人）│
   │  └ skills/（同步來的副本）     │          │  └ steering-examples.json      │
   └──────────────┬───────────────┘          └──────────────┬───────────────┘
                  ▼                                          ▼
       在 Cowork / Claude Code 裡用                在 Anthropic 雲端跑、用 API 呼叫
       （人坐在旁邊監督）                           （無人值守、後端程式驅動）
```

**技能（Skill）只有一份 source（真本），其餘都是 copy（副本）：**

```
真本（唯一可編輯）                               副本（自動產生，禁止手改）
plugins/vertical-plugins/<vertical>/skills/  ──►  plugins/agent-plugins/<slug>/skills/
                          │  python3 scripts/sync-agent-skills.py
                          └─ 整個資料夾砍掉重建（rmtree＋copytree 全覆蓋）
```

> ⚠️ **鐵則**：skill 一律改 `vertical-plugins/` 裡的 source（真本），再跑 sync 腳本。直接改 agent 包裡的 copy（副本），`check.py` 會擋下來（偵測到「漂移 drift」就讓 commit 失敗）。

---

## 二、Agent 是什麼？外掛 vs CMA

**一個 agent ＝ 系統提示（怎麼想）＋ skill（怎麼做特定事）＋ 工具（能動什麼）＋ MCP（能讀什麼外部資料）。** 同一份 agent，裝在兩種執行環境裡，行為差在哪，主要看「**有沒有人在旁邊**」。

```
            外掛（Plugin）                          CMA（託管代理）
       ┌───────────────────────┐            ┌───────────────────────────┐
       │ 跑在你的 Claude Code/  │            │ 跑在 Anthropic 雲端        │
       │ Cowork（你的電腦/IDE） │            │（PaaS，無人值守）          │
       └───────────────────────┘            └───────────────────────────┘
 觸發    你打 /指令 或對話                     你的後端程式 POST /v1/agents
 監督    人全程在旁，每步可攔                   沒有人，靠「結構」自我約束
 子代理  ✗ 無 Task/Agent 工具                  ✓ agent.yaml 靜態宣告
         → 主代理「就地」做完                     callable_agents（葉子工人）
         （需要分工時靠人開新對話）              每個子代理權限獨立隔離
 寫檔權  低風險agent主代理可直接寫               高風險agent主代理「無寫檔」，
         （內部草稿，放寬）                       只交給單一葉子工人寫
 回傳    對話訊息 ＋ 產出檔案                    SSE 事件流（伺服器推送事件）
```

**為什麼外掛沒有子代理、CMA 才有？**

```
外掛：Claude Code 執行外掛時，「整個外掛本身就已經是一個受監督的代理」。
      需要分工，人可以隨時介入、開新對話 → 安全靠「人」這道閘。

CMA：無人值守，沒有人可以攔。安全只能靠「結構」：
      把高風險動作（例如寫檔、升級）切到一個權限被縮到最小的葉子子代理，
      靜態宣告、跑前就鎖死 → 安全靠「架構」這道閘。
```

> 對照表裡那條「風險 ↔ 寫檔權」的規律，跟各 agent 單檔文件裡的「風險與把關」是一致的：🟢🟡 前台/研究產出是內部草稿，主代理可以直接寫；🔴 後台/合規牽涉法規跟財務誠信，主代理一律無寫檔。

---

## 三、十個 Agent 各需要哪些 MCP

每個 agent 在系統提示的 `tools:` 那行就宣告了它要接哪些 MCP。**這些 MCP 現在全都已經在某個 vertical 的 `.mcp.json` 定義好了**，沒有一個是「repo 裡查無此名」。差別只在它**現在指到哪裡**：

- **真實廠商網址**：`.mcp.json` 已填好供應商的正式網址（如 `factset`、`daloopa`），要你自己的訂閱金鑰才有資料。
- **本機 mock**：`.mcp.json` 指到 repo 內建的本機假伺服器（[`mock-mcp/`](../mock-mcp/)，跑在 `127.0.0.1:800x`、餵假 CSV），零金鑰就能離線把 agent 跑一遍。

| Agent | 需要的 MCP | 現在指到 | 這個 MCP 必須能提供… |
|---|---|---|---|
| 📊 earnings-reviewer | `factset`、`daloopa` | 🌐 真實廠商 | 財報實際值、市場共識、10-Q/8-K、電話會議逐字稿 |
| 🔭 market-researcher | `capiq`、`factset` | capiq 本機 mock／factset 真實廠商 | 同業倍數、產業數據、公司基本面 |
| 🧮 model-builder | `capiq`、`daloopa` | capiq 本機 mock／daloopa 真實廠商 | 歷史財務、共識、申報文件（建模輸入） |
| 🎯 pitch-agent | `capiq`（CMA 另加 `daloopa`） | capiq 本機 mock／daloopa 真實廠商 | 交易倍數、先例交易、標的最新申報文件 |
| 🤝 meeting-prep-agent | `crm`、`capiq` | 🖥️ 本機 mock | 客戶關係史/持倉/未結事項、相關市場事件 |
| 🔍 kyc-screener | `screening` | 🖥️ 本機 mock | 制裁/政治公眾人物（PEP）/負面新聞篩查 |
| ⚖️ gl-reconciler | `internal-gl`、`subledger` | 🖥️ 本機 mock | 總帳與子帳餘額、傳票（含過帳日/來源系統/批號/製單人） |
| 📅 month-end-closer | `internal-gl` | 🖥️ 本機 mock | 指定主體與期間的試算表 |
| 🧾 statement-auditor | `nav` | 🖥️ 本機 mock | 基金淨值（NAV）資料包，供逐欄核對 |
| 💰 valuation-reviewer | `portfolio` | 🖥️ 本機 mock | 投組公司估值、報酬、收益分配（waterfall）輸入 |

**七個 vertical，六個帶 `.mcp.json`（equity-research 沒帶；investment-banking 帶了但內容是空的）：**

```
financial-analysis/.mcp.json   capiq（本機 mock）＋ 12 個真實廠商連接器
                               (daloopa, morningstar, sp-global, factset, moodys,
                                mtnewswire, aiera, lseg, pitchbook, chronograph, egnyte, box)
fund-admin/.mcp.json           internal-gl, subledger, nav   （都指本機 mock）
private-equity/.mcp.json       portfolio                     （本機 mock）
operations/.mcp.json           screening                     （本機 mock）
wealth-management/.mcp.json    crm                           （本機 mock）
investment-banking/.mcp.json   { "mcpServers": {} }          （空的；IB 提案工作流的資料源借自 financial-analysis 的 capiq/daloopa）
```
> equity-research vertical 沒有 `.mcp.json`——用它的 earnings-reviewer 走 financial-analysis 的 `factset`／`daloopa`，所以不需要自帶。

### 兩種插座、兩種上線做法

agent 在 `tools:` 引用的名字，實際分兩種命運：

| agent 引用的 server | 現在指到 | 要正式上線你要做的 |
|---|---|---|
| `factset`、`daloopa`（及 morningstar/sp-global/moodys…） | ✅ financial-analysis 已填**真實廠商網址** | 向供應商買訂閱＋API 金鑰（網址不用改） |
| `capiq`、`crm`、`screening`、`internal-gl`、`subledger`、`nav`、`portfolio` | 🖥️ repo 內建**本機 mock**（`mock-mcp/`） | demo：跑 `python3 mock-mcp/run_all_http.py` 就離線跑得動；上線：把 `.mcp.json` 那把 url 從 `127.0.0.1:800x` 改指你公司真實系統／真實廠商 |

```
真實廠商（factset/daloopa…）→ 申請金鑰，網址照用
本機 mock（capiq/internal-gl/…）→ 先跑 mock-mcp 就能 demo；上線改 url 指真實來源
                          ★ 兩種都不需要去改 agent frontmatter 的 server 名稱 ★
```

> 結果是：**裝好外掛＋跑起 `mock-mcp/`，十支 agent（連後台那幾支 🔴）都能離線完整跑一遍**——repo 的 [`docs/outputs/mcpBased/`](outputs/mcpBased/) 就是十支跑 mock 的實跑紀錄。要**正式上線**才需要把對應的 mock 換成真實來源（後台那幾支因為要接內部系統、又牽涉法規與帳目正確性，工程量最大）。

### 指到本機 mock 的 7 個 MCP：上線要改指真實來源

下表是「目前指到本機 mock、上線要你改指真實系統」的清單。`capiq` 跨多支 agent 共用，改一處就好。

| 本機 mock MCP | 哪些 agent 在用 | 定義在哪個 vertical `.mcp.json` | 對應的 CMA 環境變數 |
|---|---|---|---|
| `capiq` | market-researcher、model-builder、pitch-agent、meeting-prep-agent | financial-analysis | `${CAPIQ_MCP_URL}` |
| `crm` | meeting-prep-agent | wealth-management | `${CRM_MCP_URL}` |
| `screening` | kyc-screener | operations | `${SCREENING_MCP_URL}` |
| `internal-gl` | gl-reconciler、month-end-closer | fund-admin | `${GL_MCP_URL}` |
| `subledger` | gl-reconciler | fund-admin | `${SUBLEDGER_MCP_URL}` |
| `nav` | statement-auditor | fund-admin | `${NAV_MCP_URL}` |
| `portfolio` | valuation-reviewer | private-equity | `${PORTFOLIO_MCP_URL}` |

### 上線時改哪裡

MCP 是按**名字**在 session 範圍解析，這些名字都已經接到本機 mock；上線就是把同一把名字**改指真實來源**。

| 殼 | 改哪裡 | 怎麼改 |
|---|---|---|
| **外掛（Plugin）** | 對應 vertical 的 `.mcp.json` | 把那把 server 的 `url` 從 `127.0.0.1:800x` 改成真實來源；或在專案根 `.mcp.json` / `claude mcp add` 用**同名** server 覆蓋掉（一次定義、整個 session 共享） |
| **CMA（託管代理）** | 佈署時的環境變數 | `agent.yaml` 已用 `${..._MCP_URL}` 佔位（上表那欄），把環境變數指到真實來源即可。repo 附的 [`mock-mcp/mock.env`](../mock-mcp/mock.env) 把這些變數設成本機 mock，可當範本 |

> 🔑 **不管走哪種，都不要改 agent frontmatter 的 server 名稱**——你是把同一把名字指到不同網址，不是換名字。

---

## 四、佈署與維護

### 佈署：兩種輸出、兩條路

```
外掛（Plugin）                              CMA（託管代理）
─────────────────                          ─────────────────
經 marketplace.json 註冊                    scripts/deploy-managed-agent.sh <slug>
→ 使用者在 Cowork/Claude Code 安裝          → 腳本把 agent.yaml 轉成 API 載荷：
→ 改 markdown 即時生效，                      · system.file  → 內嵌成字串
  不需重新編譯                                · skills.path  → 上傳，換成 skill_id
                                              · callable_agents.manifest → 先建子代理再引用
                                            → POST /v1/agents（beta 標頭）
                                            先設好環境變數：ANTHROPIC_API_KEY、
                                            各 MCP 的 ${..._MCP_URL}
                                            （可先 --dry-run 看載荷不真的送出）
```

`deploy-managed-agent.sh` 的環境變數代換有白名單防護：值只允許 `[A-Za-z0-9._/:@-]`，含其他字元會直接拒絕，避免把奇怪內容注進載荷。

### 維護：改一處，自動傳播，提交前自檢

```
① 改技能       編輯 plugins/vertical-plugins/<vertical>/skills/<skill>/SKILL.md（真本）
                   │
② 同步         python3 scripts/sync-agent-skills.py   （覆蓋進各 agent 包的副本）
                   │
③ 自檢         python3 scripts/check.py
                   ├ 校驗每份 manifest（plugin.json / agent.yaml）
                   ├ 確認 system.file / skills.path / callable_agents.manifest 都解析得到
                   ├ 偵測 agent 包副本有沒有「漂移」（和真本不一致就 fail）
                   └ 自動裝好 pre-commit 掛鉤（git config core.hooksPath .githooks）
                   │
④ 版本號       pre-commit 掛鉤自動把動到的 plugin.json version 補一個 patch
                （整條分支只比 main 多一個 patch，不是每次 commit 都加；
                  version 是「推送更新給已安裝使用者」的閘）
                  └ GitHub Action「version-bump」在 PR 上再把同規則檢一次當後盾
                  └ 單次提交要跳過：git commit --no-verify
```

> 📌 **最常見的維護動作就是改 skill**。永遠記得：**改真本 → 跑 sync → 跑 check**。少了 sync，check 會擋；直接改副本，check 也會擋。這條紀律就是「一個來源」能成立的關鍵。

---

> 📎 想看單一 agent 的完整 Workflow／風險把關／技術架構／上線要補齊的東西，見同資料夾各別 `*.md`；想看十個 agent 怎麼串成一個商業故事，見 [AgentSummary.md](AgentSummary.md)。
> 📎 模型清單與怎麼換模型見 [Models.md](Models.md);要動手改 agent(改哪個檔、注意事項、三道安全閘)見 [Customizing.md](Customizing.md)。
