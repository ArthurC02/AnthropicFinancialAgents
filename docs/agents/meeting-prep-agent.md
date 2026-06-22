# 🤝 Meeting Prep Agent（會前準備）

> **用途**：客戶會前準備助理，會議前彙整客戶關係、持倉與相關市場動態，最終產出給顧問的會前資料包。

`會前抓 CRM 關係＋持倉＋市場動態 → 簡報包給顧問`

| 家族 | 用戶 | 頻率 | 風險 |
|---|---|---|---|
| 前台顧問 | 財富顧問 | 每次客戶會議前 | 🟢 低（內部參考） |

## 一、Workflow

```
 客戶ID + 行事曆會議
     │
     ▼
┌────────┐  ┌────────┐  ┌────────────┐  ┌────────────┐
│①拉關係 │─►│②拉市場 │─►│③讀近期通訊 │─►│④草擬簡報包 │
│CRM歷史 │  │CapIQ   │  │news-reader │  │給顧問      │
│持倉    │  │動態    │  │摘要        │  └─────┬──────┘
└────────┘  └────────┘  └────────────┘        │
                                               ▼
                                         顧問會前審 👤
```
> 客戶關係管理系統（CRM）　|　市場資料平台（CapIQ）　|　常由行事曆會議觸發

**步驟拆解**
1. **整理客戶關係** — 從客戶系統調出往來歷史、目前持有的部位、還沒處理完的事項。
   - 步驟說明：接 CRM 拉資料——用客戶關係管理系統（CRM）MCP 把關係歷史、持倉跟未結項拉出來。
2. **掌握市場動態** — 找出近期跟這位客戶持有部位有關的市場大事。
   - 步驟說明：接市場事件——用市場資料平台（CapIQ）MCP 撈出會影響這位客戶持倉的市場事件。
3. **回顧近期往來** — 把客戶最近的信件跟筆記摘要一下，掌握最新狀況。
   - 步驟說明：sub-agent 做摘要——由 news-reader 這個 sub-agent 摘要近期客戶信件跟筆記，客戶內容一律當不可信、只摘要、不執行裡面的指令。
4. **草擬會議資料包** — 把客戶關係摘要跟持倉說明寫好，整理成一份會前資料。
   - 步驟說明：組 skill 加寫檔——用 `client-review` 產關係摘要、`client-report` 產持倉段落（需要的話再加 `investment-proposal`、`pptx-author`），plugin 版主代理可直接寫檔（風險最低故放寬）。
5. **交顧問過目** — 只出草稿，會議前讓顧問確認。
   - 步驟說明：人工 review——只產草稿、不對外發送，會議前交給顧問確認。

## 二、風險與把關

```
 agent ──簡報包──► 顧問（內部用）      ✗ 永不直接發送給客戶

 客戶來信/新聞 ──►[格式防火牆]──► 乾淨摘要 ──► 流程
 (不可信)
```
> guardrail：績效差就直說、不要粉飾　|　最後防線：不對外發送

## 三、技術架構

**技能鏈**
```
client-review ──► client-report ──► (investment-proposal / pptx-author)
關係摘要         持倉績效         提案／做簡報檔
```
**Skill（共 4 支）**　`client-review` 關係摘要 · `client-report` 持倉績效 · `investment-proposal` 提案 · `pptx-author` 做簡報檔
**MCP（2 個）**　`crm` 客戶關係系統 · `capiq` 市場資料平台

> 工具：讀＋**寫檔**＋CRM MCP＋CapIQ MCP　|　模型：opus-4-7

**外掛 vs CMA（兩種安裝）— ⭐ 有特例**
```
 外掛版 (真人盯)              CMA版 (雲端·無頭)
 ┌──────────────┐            ┌─────────────────────────┐
 │ 單一agent    │            │ 主代理 (不寫)           │
 │ 可直接寫檔 ★ │            │  ├ profiler    拉關係   │
 └──────────────┘            │  ├ news-reader 讀信·碰髒 │
  低風險 → 放寬               │  └ pack-writer 唯一可寫 │
                             └─────────────────────────┘
                              即使低風險仍隔離（零成本）
```
> 🎯 招牌設計：風險最低（🟢）卻照樣隔離——它是少數風險最低、但 CMA 端仍把寫檔權隔離出來的例子。plugin 版主代理直接握有寫檔權（低風險、產出是內部簡報，故放寬;market／model／pitch／earnings 的 plugin tools 其實也都有 Write），但 CMA 版仍只給 pack-writer 寫;profiler 讀可信源（無 schema）、news-reader 碰髒（有 schema）。**安全層級會隨風險高低調整**，不是一刀切。

**改哪裡（快速 map）**

| 想改 | 動這個檔 |
|---|---|
| 流程／stop 點／守則 | `agents/meeting-prep-agent.md` 的 Workflow／Guardrails |
| 用哪些 skill | 同檔的 Skills 行 |
| IPS／再平衡門檻 | `client-review/SKILL.md` 真本 → sync |
| 幾個 sub-agent | `cookbooks/meeting-prep-agent/agent.yaml` 的 callable_agents |
| news-reader 輸出限制 | `subagents/news-reader.yaml` 的 output_schema |

> 通用改法見 [Customizing.md](../Customizing.md);上線要補的見下方 §四。

**跨 agent**　前台顧問型，跟後台作業家族（對帳／結帳／開戶）相對

## 四、上線前要補齊的（客製化）

```
 Anthropic 參考骨架    ＋    貴公司要補的    ＝    可實際上線
 (提示詞·技能·流程)          (資料·規則·範本)
```

- 🔌 **接真實系統**：`crm`／`capiq` 都已在 vertical `.mcp.json` 定義、指向本機 mock（`mock-mcp/`，假 CSV）——想離線 demo 跑 `python3 mock-mcp/run_all_http.py` 就能連 mock
  - plugin → 把 `plugins/vertical-plugins/wealth-management/.mcp.json` 裡 `crm` 的 url 從本機 mock 改指你的 CRM 系統（伺服器名跟 frontmatter `tools:` 都不要改）
  - CMA → 設 env var `CRM_MCP_URL`／`CAPIQ_MCP_URL`（或改 `managed-agent-cookbooks/meeting-prep-agent/agent.yaml`）
  - 🛠️ `crm` 要能：依客戶ID查 關係歷史·持倉·未結項·近期通訊（規格見 `client-review`、`client-report`）
  - 🛠️ `capiq` 要能：查會影響這位客戶持倉的市場事件／報價（要上線把 url 改指你的 CapIQ／S&P feed）
- 📐 **IPS／再平衡門檻**（偏離預設 `3–5%`） → `plugins/vertical-plugins/wealth-management/skills/client-review/SKILL.md`
- 🎨 **品牌簡報 template**：用 `/ppt-template` 指令產一支 template skill（指令底層是 `ppt-template-creator`，實際渲染簡報用 `plugins/vertical-plugins/financial-analysis/skills/pptx-author/`）
- ✏️ **調整 agent 範圍** → `plugins/agent-plugins/meeting-prep-agent/agents/meeting-prep-agent.md`
- ⚖️ **合規＋人工 review 不變**：只給顧問、永遠不對外發送

> ⚠️ skill 一律改 `vertical-plugins/` 的 **source（真本）**，改完跑 `python3 scripts/sync-agent-skills.py` sync 到 agent。這個 agent 刻意把公司專屬的內容留空，填上去才完整。

## 五、導入評估

| 面向 | 評估 |
|---|---|
| **導入風險** | 🟢 低 — 產出是會前的內部簡報，只給財富顧問參考、永遠不直接發給客戶;不碰法規簽核、財務過帳或對外正式文件，顧問會前 review 一下就能攔錯。 |
| **導入成本** | 🟡 中（偏高，CRM 要接內部系統） — `crm` 已在 vertical `.mcp.json` 接本機 mock，要上線把 url 改指貴公司的客戶關係系統（查關係歷史·持倉·未結項·近期通訊）;`capiq` 同樣已接本機 mock，要上線把 url 改指你的市場資料平台（CapIQ／S&P feed）;另外要客製投資政策聲明（IPS）／再平衡偏離門檻跟品牌簡報 template。 |
| **適用單位** | 財富管理／私人銀行前台、理財顧問團隊 |
| **單位中角色** | 財富顧問（下指令＋會前覆核草稿·對客戶溝通）· 投組經理（提持倉與再平衡需求）· 助理顧問（草稿加工·彙整行事曆會議） |

**最有機會成功的場景**
1. **例行客戶檢視會議前的資料包** — 顧問每次客戶會議前都要快速彙整關係歷史＋持倉＋市場動態，省下一堆人工蒐集，是最高頻、最穩的場景。
2. **持倉受市場大事衝擊時的緊急會前準備** — 客戶部位碰到突發市場事件，顧問臨時要約談，馬上需要一份持倉影響說明＋溝通要點。
3. **季度／年度再平衡諮詢會議** — 偏離 IPS 門檻觸發再平衡討論，會前自動產出偏離分析跟提案草稿給顧問定稿。
