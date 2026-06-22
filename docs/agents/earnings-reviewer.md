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
**Skill（共 6 支）**　`earnings-analysis` 讀會議 · `model-update` 更新模型 · `audit-xls` 模型QC · `morning-note` 寫筆記 · `earnings-preview` 財報前瞻 · `xlsx-author` 產 Excel（note-writer 寫檔用）
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

> 🎯 招牌設計：這支有真正的「髒文件 reader」——逐字稿是外來不可信內容，所以 transcript-reader 設成 `mcp_servers:[]` ＋ output_schema，把它框死來防 prompt injection。驗證走「自查」：audit-xls 做 foot check（平衡驗算），不另外設獨立 critic。

**跨 agent**　研究與建模家族 ┄ 跟〔market-researcher〕〔model-builder〕互補;初次納入追蹤交給別人做

## 四、要調什麼、改哪裡（業務內容調整表）

```
 Anthropic 參考骨架    ＋    貴公司要補的    ＝    可實際上線
 (提示詞·技能·流程)          (資料·規則·範本)
```

> 先分清楚：門檻、規則、清單多半設計成「執行時餵」就好；要變成公司預設才改 source。

| 想調的業務內容 | 改哪個檔 | 怎麼改 |
|---|---|---|
| 模型更新慣例（欄位對應、估值邏輯） | `vertical-plugins/equity-research/skills/model-update/SKILL.md` | 改值 → sync |
| 財報前瞻假設（bull/base/bear 情境參數） | `vertical-plugins/equity-research/skills/earnings-preview/SKILL.md` | 改值 → sync；臨時可直接 prompt 給 |
| 筆記格式／語氣（headline、beat/miss 表） | `vertical-plugins/equity-research/skills/morning-note/SKILL.md` | 改範本 → sync |
| Excel QC 驗算範圍（foot check 規則） | `vertical-plugins/equity-research/skills/audit-xls/SKILL.md` | 改規則 → sync |
| 流程／stop 點／守則 | `agents/earnings-reviewer.md` 的 Workflow／Guardrails | 直接改 agents 檔 |
| 用哪些 skill／幾個 sub-agent | `agents/earnings-reviewer.md` Skills 行；`cookbooks/earnings-reviewer/agent.yaml` callable_agents | 改 agents 檔或 agent.yaml |
| 接 factset／daloopa（真實資料） | core plugin 已定義，網址照用 | 申請訂閱＋API 金鑰，網址照用 |

**三條路線**
- ① 臨時（不改檔）：門檻／政策／清單直接在 prompt 或 `steering-examples.json` 給。
- ② 永久（改預設）：改 `vertical-plugins/` 的 SKILL.md 真本 → `python3 scripts/sync-agent-skills.py` → `check.py`（drift 會擋 commit；別手改 bundle 的 copy）。
- ③ 接系統：改 `.mcp.json` 的 url（外掛）或 env var（CMA）；**server 名別改**。

**接真實系統要做到**（上線必補）
- 🛠️ `factset`／`daloopa`：兩者皆為公開財務資料供應商，core plugin 已定義好 server；向供應商申請訂閱＋API 金鑰，網址照用，不需改 url。
- 👤 **人工覆核不變**：模型與筆記只交草稿，資深分析師簽核才發布；CMA 版寫檔權隔離給 note-writer sub-agent。

> 通用改法見 [Customizing.md](../Customizing.md)。這支刻意把公司專屬的東西留空，你填上去才算完整。

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

## 六、它補的是哪一段（與成熟系統／自建的分工）

它不是研究平台、也不是模型本身，而是坐在那些工具「上面」做讀取、判斷、更新的那一層。把財報處理拆幾段就清楚：

| 環節 | 誰做 |
|---|---|
| 提供共識預期、歷史財務、SEC 文件 | 🏦 成熟系統（Visible Alpha／FactSet）——結構化、即時、可查 |
| 讀懂法說會逐字稿、挖展望與管理層口風、把新數字正確更新進活的追蹤模型 | 🤖 本 agent——規則列不完、要判斷的那段 |
| 審核草稿、拍板觀點、簽核發布 | 👤 資深分析師 |

**優勢來源**
- **對成熟系統**：平台給資料就停了，讀會議紀錄、解讀管理層語氣、把新數字「接進既有模型的正確格」——這段要判斷，系統本來留給人手工做的。
- **對分析師自建 Excel 模型**：不用手動翻逐字稿、逐格貼數字；格式有變也不必改腳本，自動追到出處、每格改動可溯源。

**什麼時候用哪個**
- 拉共識、查歷史財務、取 SEC 文件 → 成熟系統（FactSet／Visible Alpha）。
- 讀法說會、解讀展望、更新追蹤模型、草擬財報後筆記 → agent。
- 大量跨股票的批次數字比對、容差套用 → 成熟系統或自建腳本。
- ❌ 直接對外發研究報告別用 agent（只交草稿，資深分析師簽核才發布）。

## 七、Skill 白話

每支 skill 是一份「給 AI 看的作業手冊」。算術與驗證都導向 Excel 公式，skill 只負責判斷與接線。

- **`earnings-analysis` 解讀法說會**：針對已在追蹤的公司，把財報說明會逐字稿精讀出來——重點是比較實際業績與市場預期的落差、管理層的展望語氣、以及刻意迴避的問題，輸出格式化的 beat/miss 分析與更新後的估值觀點（8–12 頁 DOCX）。
- **`model-update` 更新追蹤模型**：收到新一季的實際數字後，照出處把它們塞進活的追蹤 workbook——逐列比對舊估 vs. 實際、推算下期估值修正、更新目標價，每一格改動都能溯回 source。
- **`audit-xls` 模型品質檢查**：產出前健檢公式——抓 #REF!、藏在公式裡的死數字、漏行的 SUM、斷掉的連結，確保 foot check 是「活的」；財報後模型最容易出現公式斷掉或數字寫死的靜默 bug。
- **`morning-note` 草擬財報後筆記**：用晨間報告格式把財報事件整理成一頁可讀的觀點筆記——headline、beat/miss 快照表、管理層說了什麼、分析師的 take，以及評等是否調整，2 分鐘內讓 PM 讀完。
- **`earnings-preview` 財報前瞻**：財報公布前建立「要看什麼」框架——拉共識預期、整理關鍵指標優先序、建 bull／base／bear 三情境及各自股價隱含反應，讓分析師進場前就定好觀察點。
- **`xlsx-author` 產出 Excel 檔**：無頭模式下用 Python 把 .xlsx 寫成檔（藍＝輸入、黑＝公式、綠＝連結，計算格一律公式）；有開著的 Excel 時改用 office 工具直接操作。
