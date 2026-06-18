# 🏗️ 技術總覽 — 一套方案怎麼運作

> 這份文件回答四個工程問題：**①** 為什麼同一個 agent 可以變成兩種產品？**②** 「外掛」和「CMA」到底差在哪？**③** 十個 agent 各自要接哪些資料來源（MCP）？**④** 怎麼佈署、怎麼維護？
> 名詞先講白話：**MCP（模型情境協定，Model Context Protocol）** 就是「讓 agent 接到外部系統（總帳、CRM、行情）的標準插座」；**CMA（Claude 託管代理，Claude Managed Agents）** 就是「把 agent 部署到 Anthropic 的雲端，由它代跑、用 API 呼叫」。

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

**技能（Skill）只有一份真本，其餘都是副本：**

```
真本（唯一可編輯）                               副本（自動產生，禁止手改）
plugins/vertical-plugins/<vertical>/skills/  ──►  plugins/agent-plugins/<slug>/skills/
                          │  python3 scripts/sync-agent-skills.py
                          └─ 整個資料夾砍掉重建（rmtree＋copytree 全覆蓋）
```

> ⚠️ **鐵則**：技能一律改 `vertical-plugins/` 裡的真本，再跑同步腳本。直接改 agent 包裡的副本，`check.py` 會擋下來（偵測到「漂移 drift」就讓提交失敗）。

---

## 二、Agent 是什麼？外掛 vs CMA

**一個 agent ＝ 系統提示（怎麼想）＋ 技能（怎麼做特定事）＋ 工具（能動什麼）＋ MCP（能讀什麼外部資料）。** 同一份 agent，裝在兩種執行環境裡，行為差異主要來自「**有沒有人在旁邊**」。

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

> 對照表內的「風險 ↔ 寫檔權」規律，和各 agent 單檔文件裡的「風險與把關」一致：🟢🟡 前台/研究產出是內部草稿，主代理可直接寫；🔴 後台/合規牽涉法規與財務誠信，主代理一律無寫檔。

---

## 三、十個 Agent 各需要哪些 MCP

每個 agent 在系統提示的 `tools:` 那行就宣告了它要接哪些 MCP。下表把十個整理在一起，並標明這個插座是**公開連接器（網路上現成、repo 已填好網址）**還是**佔位名稱（placeholder，repo 沒定義，要你自己接公司內部系統）**。

| Agent | 需要的 MCP | 性質 | 這個 MCP 必須能提供… |
|---|---|---|---|
| 📊 earnings-reviewer | `factset`、`daloopa` | 🌐 公開 | 財報實際值、市場共識、10-Q/8-K、電話會議逐字稿 |
| 🔭 market-researcher | `capiq`、`factset` | ⚠️ capiq 佔位／factset 公開 | 同業倍數、產業數據、公司基本面 |
| 🧮 model-builder | `capiq`、`daloopa` | ⚠️ capiq 佔位／daloopa 公開 | 歷史財務、共識、申報文件（建模輸入） |
| 🎯 pitch-agent | `capiq`（CMA 另加 `daloopa`） | ⚠️ 佔位 | 交易倍數、先例交易、標的最新申報文件 |
| 🤝 meeting-prep-agent | `crm`、`capiq` | ⚠️ 佔位 | 客戶關係史/持倉/未結事項、相關市場事件 |
| 🔍 kyc-screener | `screening` | ⚠️ 佔位 | 制裁/政治公眾人物（PEP）/負面新聞篩查 |
| ⚖️ gl-reconciler | `internal-gl`、`subledger` | ⚠️ 佔位 | 總帳與子帳餘額、傳票（含過帳日/來源系統/批號/製單人） |
| 📅 month-end-closer | `internal-gl` | ⚠️ 佔位 | 指定主體與期間的試算表 |
| 🧾 statement-auditor | `nav` | ⚠️ 佔位 | 基金淨值（NAV）資料包，供逐欄核對 |
| 💰 valuation-reviewer | `portfolio` | ⚠️ 佔位 | 投組公司估值、報酬、收益分配（waterfall）輸入 |

**只有三個 vertical 帶 `.mcp.json`，其中兩個還是空的：**

```
plugins/vertical-plugins/financial-analysis/.mcp.json  ← 唯一真正填了公開連接器
   daloopa, morningstar, sp-global(kensho), factset, moodys,
   mtnewswire, aiera, lseg, pitchbook, chronograph, egnyte, box
plugins/vertical-plugins/investment-banking/.mcp.json  ← { "mcpServers": {} } 空
plugins/vertical-plugins/private-equity/.mcp.json      ← { "mcpServers": {} } 空
（operations / fund-admin / wealth-management 等其餘 vertical：根本沒有 .mcp.json）
```

### 最容易誤會的點：「裝全部外掛」只救得到公開連接器

很直覺會以為「把所有外掛都裝上，financial-analysis 的 `.mcp.json` 就會啟動這些 server，別包的 agent 也順帶受惠」。**這對『公開連接器』完全正確，但救不到『佔位』**——因為佔位 server 在整個 repo 裡**沒有任何 `.mcp.json` 定義過**，沒有人提供，裝再多包也變不出來。

agent 在 `tools:` 引用的名字，實際分成三種命運：

| agent 引用的 server | 誰定義了它？ | 裝好全部外掛後… | 你要做什麼 |
|---|---|---|---|
| `factset`、`daloopa` | ✅ financial-analysis 已填網址 | **可用** | 啥都不用做（裝上 financial-analysis 即可） |
| `capiq` | ❌ 沒有人 | ⚠️ **還是沒有** | 自己補同名定義（它感覺像市場資料，但 repo 沒定義過） |
| `crm`、`screening`、`internal-gl`、`subledger`、`nav`、`portfolio` | ❌ 沒有人 | ⚠️ **還是沒有** | 自己接公司內部系統 |

```
公開（factset/daloopa）→ 裝上 financial-analysis 即可，按名字共用，不碰 frontmatter
佔位（capiq/crm/...）   → 你要「自己當提供方」，補一把同名鑰匙指到真實伺服器
                          ★ 兩種情況都不需要去改 agent 的 frontmatter 名稱 ★
```

> 結果就是：earnings-reviewer 這種純市場資料的 agent，裝好（＋修下方 JSON bug）就能動；後台那幾支 🔴 agent 因為全靠佔位的內部 server，**裝好也仍然不能動**，要等你接上內部系統。

> ⚠️ **兩個要注意的點**：
> **(1) `capiq` 是佔位名稱**——多個 agent 寫著要 `mcp__capiq__*`，但沒有任何 `.mcp.json` 定義過 `capiq`。要嘛接你公司的 CapIQ 來源、要嘛把它改成 `factset`/`sp-global` 這類已定義的連接器。
> **(2) repo 現有一個 JSON 語法錯誤**：[financial-analysis/.mcp.json](../plugins/vertical-plugins/financial-analysis/.mcp.json) 裡 `egnyte` 區塊後缺逗號、`box` 區塊缺收尾大括號（commit #187 引入），`json.load` 會直接失敗。實際接公開連接器前要先修好這個檔。

### 缺漏的 MCP ↔ 哪支 agent 在用 ↔ 概念上歸哪個 vertical

下表是「裝好全部外掛仍然沒有、要你自己補」的清單。`capiq` 跨多支 agent 共用，補一份就好。

| 佔位 MCP | 哪些 agent 在用 | 概念歸屬 vertical | 對應的 CMA 環境變數 |
|---|---|---|---|
| `capiq` | market-researcher、model-builder、pitch-agent、meeting-prep-agent | 跨領域（市場資料） | `${CAPIQ_MCP_URL}` |
| `crm` | meeting-prep-agent | wealth-management | `${CRM_MCP_URL}` |
| `screening` | kyc-screener | operations | `${SCREENING_MCP_URL}` |
| `internal-gl` | gl-reconciler、month-end-closer | fund-admin | `${GL_MCP_URL}` |
| `subledger` | gl-reconciler | fund-admin | `${SUBLEDGER_MCP_URL}` |
| `nav` | statement-auditor | fund-admin | `${NAV_MCP_URL}` |
| `portfolio` | valuation-reviewer | fund-admin | `${PORTFOLIO_MCP_URL}` |

> 註：`fund-admin` / `operations` / `wealth-management` 這幾個 vertical 目前**根本沒有 `.mcp.json`**，走「選項 B」要先新建。

### 要把這些補在哪個檔？三個選項（別亂塞 private-equity）

MCP 是按**名字**在 session 範圍解析，放哪個檔在機制上都行，差別只在「語意是否合理」與「安裝範圍」。

| 選項 | 路徑 | 適合 | 代價 |
|---|---|---|---|
| **A. agent 自己的包** | `plugins/agent-plugins/<slug>/.mcp.json`（新增） | 想讓每支 agent 自帶連接器、單獨安裝就能跑 | 共用的 `capiq` 要在多支包重複定義 |
| **B. 對應 vertical 包** | `plugins/vertical-plugins/<vertical>/.mcp.json` | 想按業務領域歸類、領域內共用（如 `internal-gl`→fund-admin） | 得連那個 vertical 一起裝；多數 vertical 還沒這個檔，要新建 |
| **C. 你的實際專案／使用者層級** | 專案根 `.mcp.json` 或 `claude mcp add` | **實際上線最省事**：一次定義，整個 session 全 agent 共享 | 不在 repo 裡，換機器要重設 |

```
外掛版（A/B/C 任一）：補一把「同名鑰匙」
        { "<佔位名稱>": { "type": "http", "url": "<你的 MCP 網址>" } }
CMA 版：agent.yaml 已寫好 url: ${GL_MCP_URL} 之類的環境變數佔位，
        佈署時把上表那些環境變數指到你的內部 MCP 伺服器即可。
```

> ⚠️ **不要全丟進 `private-equity/.mcp.json`**——它只是剛好有這個檔，跟上面這些 agent 大多無關；名字雖照樣解析得到，但語意錯亂，日後沒人懂「GL 對帳的 server 為何定義在私募股權底下」。要走選項 B 就放進**概念歸屬**那欄的 vertical。
> 🔑 **三個選項都不要改 agent 的 frontmatter 名稱**——你是補同名鑰匙，不是改鎖。

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

> 📌 **最常見的維護動作就是改技能**。永遠記得：**改真本 → 跑 sync → 跑 check**。少了 sync，check 會擋；直接改副本，check 也會擋。這條紀律就是「一個來源」能成立的關鍵。

---

> 📎 想看單一 agent 的完整 Workflow／風險把關／技術架構／上線要補齊的東西，見同資料夾各別 `*.md`；想看十個 agent 怎麼串成一個商業故事，見 [AgentSummary.md](AgentSummary.md)。
