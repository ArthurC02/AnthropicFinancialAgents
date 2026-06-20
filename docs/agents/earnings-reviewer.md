# 📊 Earnings Reviewer（財報審閱）

> **用途**：財報追蹤助理，公司發財報後解讀法說會、更新追蹤中的模型，最終產出財報後觀點筆記。

`財報事件 → 讀電話會議＋財報 → 更新追蹤標的的模型 → 草擬財報後筆記 → 分析師審`

| 家族 | 用戶 | 頻率 | 風險 |
|---|---|---|---|
| 研究與建模 | 股票研究分析師 | 每次追蹤的股票發財報 | 🟡 中 |

## 一、Workflow

```
 ticker + 報告期
     │
     ▼
┌────────┐  ┌────────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐
│①拉財報 │─►│②讀電話會議 │─►│③更新模型 │─►│④模型QC │─►│⑤草擬筆記 │
│FactSet │  │earnings-   │  │model-    │  │audit-  │  │morning-  │
│Daloopa │  │analysis    │  │update    │  │xls     │  │note      │
└────────┘  └────────────┘  └──────────┘  └────────┘  └────┬─────┘
                                                            ▼
                                                     資深分析師審 👤
```
> 刻意不做：單一標的的初次納入追蹤（用 model-builder／initiating）

**步驟拆解**
1. **取得財報數字** — 把公司剛公布的實際業績、市場原本的預期，還有完整的法說會（財報說明會）內容都拿到手，不要只看摘要。
   - 步驟說明：走 MCP connector 接資料——用 `factset`／`daloopa` MCP 抓實際業績、市場共識跟 10-Q／8-K 文件，法說會逐字稿要載入完整版（別靠摘要）。
2. **解讀法說會** — 從會議裡把公司對未來的展望、管理層的口風，還有他們刻意閃掉的問題都挖出來。
   - 步驟說明：解析逐字稿——用 `earnings-analysis` 這個 skill 把公司展望、管理層語氣跟被迴避的問題抓出來;逐字稿一律當不可信的 source 處理。
3. **更新模型** — 把新數字塞進原本在追這家公司的那份試算表模型。
   - 步驟說明：更新模型——用 `model-update` 這個 skill 把新數字寫進那份活的 workbook（持續追蹤用的試算表），每一格改動都要能 trace 回 source。
4. **檢查模型** — 回頭複查模型沒算錯、公式沒斷掉、也沒有人把數字硬填進去。
   - 步驟說明：模型品質檢查——用 `audit-xls` 這個 skill 跑平衡驗算、確認公式連結沒斷、計算格沒有寫死的數字。
5. **草擬筆記** — 寫一份財報後的觀點筆記，講清楚這次跟預期差在哪、該怎麼解讀。
   - 步驟說明：產筆記——用 `morning-note` 這個 skill 拉出筆記框架，把差異表（實際 vs. 共識 vs. 前估）跟對法說會的解讀填進去。
6. **送交審閱** — 模型跟筆記都以草稿交出去,不要直接對外發布。
   - 步驟說明：人工 review 把關——模型跟筆記只以草稿交付，永遠不對外發布;CMA 版還會把寫檔權隔離給 note-writer 這個 sub-agent，送出去前要資深分析師簽核。

## 二、風險與把關

```
 agent ──草稿──► 資深分析師（內部）      ✗ 永不對外發布

 逐字稿/新聞稿(外來) ──► 只當資料 ──► 流程
 (不可信)
```
> guardrail：每個數字都要有出處，查不到就標 `[UNSOURCED]`　|　最後防線：不發布（送出去要分析師簽核）

## 三、技術架構

**技能鏈**
```
earnings-analysis ──► model-update ──► audit-xls ──► morning-note
讀電話會議          更新模型         模型QC        草擬筆記
```
**Skill（共 5 支）**　`earnings-analysis` 讀會議 · `model-update` 更新模型 · `audit-xls` 模型QC · `morning-note` 寫筆記 · `earnings-preview` 財報前瞻
**MCP（2 個）**　`factset` · `daloopa`（都是公開財務資料供應商，core plugin 已經定義好）

> 工具：讀＋**寫檔**＋FactSet/Daloopa MCP　|　模型：opus-4-7

**外掛 vs CMA（兩種安裝）**
```
 外掛版 (真人盯)              CMA版 (雲端·無頭)
 ┌──────────────┐            ┌──────────────────────────┐
 │ 單一agent    │            │ 主代理 (不寫)            │
 │ 可直接寫檔   │            │  ├ transcript-reader 讀會議│
 └──────────────┘            │  ├ model-updater   更新   │
  低風險→放寬                │  └ note-writer     唯一可寫│
                            └──────────────────────────┘
```
> 跟 meeting-prep 一樣：plugin 版的主代理可以直接寫檔（研究草稿、風險中），CMA 版還是把寫檔權隔離給 note-writer

**跨 agent**　研究與建模家族 ┄ 跟〔market-researcher〕〔model-builder〕互補;初次納入追蹤交給別人做

## 四、上線前要補齊（客製化）

```
 Anthropic 參考骨架    ＋    貴公司要補的    ＝    可實際上線
```
- 🔌 **接資料訂閱**：`factset`/`daloopa` 在 core plugin 已經定義好，但**要先向供應商買訂閱／API key** 才會有資料
- 📈 **追蹤模型 template**：`model-update` 要對著貴公司「持續追蹤標的的活 workbook」格式 → `plugins/vertical-plugins/equity-research/skills/model-update/SKILL.md`
- 📝 **筆記 template**：研究筆記格式 → `plugins/vertical-plugins/equity-research/skills/morning-note/SKILL.md`
- ✏️ **調整範圍** → `plugins/agent-plugins/earnings-reviewer/agents/earnings-reviewer.md`
- 👤 **人工 review 不變**：只產草稿，資深分析師簽核才發布

> ⚠️ skill 一律改 `vertical-plugins/` 的 source（真本），改完跑 `python3 scripts/sync-agent-skills.py` 做 sync。

## 五、導入評估

| 面向 | 評估 |
|---|---|
| **導入風險** | 🟡 中 — 產出會影響研究觀點跟投資判斷，但只交草稿、不對外發布、不過帳;資深分析師簽核才發布，攔得住錯。風險在數字出處跟模型更新正不正確，不是法規簽核那種。 |
| **導入成本** | 🟡 中 — `factset`／`daloopa` 這兩個公開 connector 在 core 已經定義好，只要向供應商買訂閱／API key;另外要客製「持續追蹤標的的活 workbook」模型 template 跟研究筆記 template，不用自己蓋內部系統。 |
| **適用單位** | 賣方／買方股票研究部、投資團隊 |
| **單位中角色** | 股票研究分析師（下指令＋覆核模型與筆記＋簽核發布）· 資深分析師（最終簽核把關）· 研究助理（草稿與模型加工） |

**最有機會成功的場景**
1. **財報季密集覆蓋的標的更新** — 一個分析師同時追好幾檔股票，財報集中爆量時最缺人,自動拉數字＋更新模型＋草擬筆記省最多工，CP 值最高。
2. **法說會（財報說明會）逐字稿快速解讀** — 會議又臭又長，要在盤後第一時間把展望、管理層口風跟迴避的問題抓出來，搶時效先生一版初稿。
3. **模型更新後的品質自查** — 財報後用手改模型最容易公式斷掉或數字寫死，讓它自動跑平衡驗算跟連結檢查，交付前少出錯。
