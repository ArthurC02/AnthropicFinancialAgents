# 🧮 Model Builder（建模）

> **用途**：估值建模助理，針對一家公司從零建立估值模型（現金流折現、槓桿收購、三大報表等），最終產出可供投資決策的 Excel 模型。

`ticker ＋ 假設 → 在 Excel 從零建出估值模型（現金流折現 DCF／槓桿收購 LBO／三表／同業比較 comps）`

| 家族 | 用戶 | 頻率 | 風險 |
|---|---|---|---|
| 研究與建模 | 分析師／建模專員 | 需要一個乾淨新模型時 | 🟡 中 |

## 一、Workflow

```
 ticker + 模型類型 + 假設
     │
     ▼
┌──────────┐  ┌──────────────┐  ┌────────┐  ┌────────────┐
│①拉輸入   │─►│②建模型       │─►│③稽核   │─►│④敏感度分析 │─► 使用者審 👤
│CapIQ     │  │dcf/lbo/      │  │audit-  │  │標準敏感度表│
│Daloopa   │  │3-stmt/comps  │  │xls     │  └────────────┘
└──────────┘  └──────────────┘  └────────┘
              藍/黑/綠色碼·計算格不打死數字
```
> 現金流折現估值（DCF）｜槓桿收購模型（LBO）｜三表＝損益/資產負債/現金流整合　|　刻意不做：更新既有模型（用 earnings-reviewer）

**步驟拆解**
1. **準備資料** — 把這家公司的歷史財務、市場預期跟公開申報資料拿到手，當作建模的基礎。
   - 步驟說明：接 MCP 拉資料——用 CapIQ／Daloopa MCP 拉歷史財務、市場預期（consensus）跟公開申報文件，當建模的 input。
2. **建立模型** — 看需求建出對應的估值模型（像現金流折現、槓桿收購、三大報表那些）。
   - 步驟說明：依模型類型挑一個 skill 來建——`dcf-model`／`lbo-model`／`3-statement-model`／`comps-analysis`，套上藍／黑／綠色碼，計算格一律用公式、不要寫死數字。
3. **檢查模型** — 回頭複查模型算得對、公式沒問題，每個結果都能 trace 回原始 input。
   - 步驟說明：自動稽核——用 `audit-xls` 跑平衡檢查、確認循環參照是刻意設的，再驗證每個 output 都能 trace 回 input。
4. **做敏感度分析** — 試算不同假設下結果會怎麼變，看模型對哪些變數最敏感。
   - 步驟說明：建出該模型類型的標準敏感度表（像 DCF 的 WACC／成長率、LBO 的 IRR／MOIC），呈現結果對關鍵變數的反應。
5. **交付審閱** — 模型建好先停住，使用者確認過才往後用。
   - 步驟說明：人工 review 把關——建完就停下來交付，使用者核准後才往下游用，敏感度跟後續步驟都要簽核。

## 二、風險與把關

```
 agent ──建好模型──► 使用者審        ✗ 建完先停，使用者核准才做敏感度

 財報(經 MCP) ──► 拉資料 ──► 建模
```
> guardrail：**每個 output 都是公式、計算格不要寫死數字;假設要標 `[ASSUMPTION]` 並附上來源**　|　最後防線：建完/稽核後都停下來給人審

## 三、技術架構

**技能鏈**
```
(dcf-model / lbo-model / 3-statement-model / comps-analysis) ──► audit-xls
依模型類型擇一建                                                  稽核
```
**Skill（共 6 支）**　`dcf-model` 折現估值 · `lbo-model` 槓桿收購 · `3-statement-model` 三表 · `comps-analysis` 同業倍數 · `audit-xls` 稽核Excel · `xlsx-author` 產出 Excel（builder 寫檔用）
**可加掛的模型**　現在是 dcf／lbo／3-statement／comps;要建併購案可加掛 `merger-model`、SaaS／訂閱型標的可加 `unit-economics`（怎麼掛見 [Models.md](../Models.md)）
**MCP（2 個）**　`capiq` · `daloopa`（`capiq` 在 vertical `.mcp.json` 已定義，指向本機 mock（`mock-mcp/`，假 CSV），要上線把 url 改指你的 CapIQ／S&P feed;`daloopa` 是公開供應商）

> 工具：讀＋**寫檔**＋CapIQ/Daloopa MCP　|　模型：opus-4-7

**外掛 vs CMA（兩種安裝）**
```
 外掛版 (真人盯)         CMA版 (雲端·無頭)
 ┌───────────┐          ┌──────────────────────────┐
 │ 單一agent │          │ 主代理 (不寫)            │
 │ 可直接寫檔│          │  ├ data-puller 拉資料    │
 └───────────┘          │  ├ builder     唯一可寫  │
                        │  └ auditor     稽核      │
                        └──────────────────────────┘
```
> 🎯 招牌設計：驗證 = 獨立的 auditor 重查那份 Excel——跑平衡檢查、把每個 output 追回 input。值得注意：這支沒有「髒文件 reader」，因為 input 全來自可信 MCP（capiq／daloopa），所以 data-puller 的 schema 是「乾淨結構化交棒」而非防注入。builder 拿到 bash 是刻意的（要跑算）。

**改哪裡（快速 map）**

| 想改 | 動這個檔 |
|---|---|
| 流程／stop 點／守則 | `agents/model-builder.md` 的 Workflow／Guardrails |
| 用哪些模型/skill | 同檔的 Skills 行（加掛新模型見 [Models.md](../Models.md)） |
| 建模慣例（WACC／色碼） | `dcf-model`／`lbo-model` 等 SKILL.md → sync |
| 幾個 sub-agent | `cookbooks/model-builder/agent.yaml` 的 callable_agents |
| data-puller 結構化輸出 | `subagents/data-puller.yaml` 的 output_schema |

> 通用改法見 [Customizing.md](../Customizing.md);上線要補的見下方 §四。

**跨 agent**　研究與建模家族 ┄ 跟〔earnings-reviewer〕（更新既有模型）劃清界線

## 四、上線前要補齊（客製化）

```
 Anthropic 參考骨架    ＋    貴公司要補的    ＝    可實際上線
```
- 🔌 **接資料訂閱**：`daloopa` 是公開供應商，**要訂閱／API key**;`capiq` 在 vertical `.mcp.json` 已定義、指向本機 mock（`mock-mcp/`，假 CSV）——想離線 demo 跑 `python3 mock-mcp/run_all_http.py`，要上線把 url 改指你的 CapIQ／S&P feed（伺服器名跟 frontmatter `tools:` 都不要改）
- 📐 **建模慣例**：WACC 組成、色碼、計算慣例、各模型 template → `plugins/vertical-plugins/financial-analysis/skills/dcf-model/SKILL.md`（還有 `lbo-model`、`3-statement-model`）
- ✏️ **調整範圍** → `plugins/agent-plugins/model-builder/agents/model-builder.md`
- 👤 **人工 review 不變**：建完先停，使用者核准才往下

> ⚠️ skill 一律改 `vertical-plugins/` 的 source（真本），改完跑 `python3 scripts/sync-agent-skills.py` 做 sync。

## 五、導入評估

| 面向 | 評估 |
|---|---|
| **導入風險** | 🟡 中 — 模型是拿去做投資決策用的，但建完就停、敏感度跟下游都要使用者核准才往下，不是法規強制簽核那種;每個 output 都是公式、可以 trace 回 input，再配上獨立的稽核（auditor）攔錯。風險在估值假設跟計算正不正確，靠人工 review 把關。 |
| **導入成本** | 🟡 中 — `daloopa` 要訂閱公開資料供應商（買訂閱＋API key）;`capiq` 已接本機 mock，要上線把 url 改指你的 CapIQ／S&P feed;還要客製建模慣例（WACC（加權平均資金成本）組成、藍／黑／綠色碼、計算慣例）跟各模型 template（DCF／LBO／三表）;不用自己蓋內部系統，整合很輕。 |
| **適用單位** | 投資銀行（IB）、股票研究部、私募股權（PE）／併購團隊、企業發展（corp dev）／財務規劃（FP&A） |
| **單位中角色** | 建模專員／分析師（下指令＋建模＋覆核）· 投資銀行家／投組經理（提需求＋核准模型）· 研究分析師（消費估值結論） |

**最有機會成功的場景**
1. **新標的的初版估值模型** — 接到一個沒建過模型的 ticker，要從零拉資料、建出乾淨的 DCF／LBO／三表，省下最多手工搭表的時間，CP（性價比）值最高。
2. **交易前的快速估值草稿** — 併購／投資案一啟動，要在短時間內生出一份結構完整、可追溯的初步估值給內部討論。
3. **同業比較（comps）與敏感度速建** — 需要一份標準 comps 倍數表加敏感度表（像 DCF 的 WACC／成長率），快速看估值對關鍵假設的反應。

## 六、它補的是哪一段（與成熟系統／自建的分工）

它不是建模 add-in、也不是範本庫，而是坐在那些系統「上面」做判斷的那一層。把建模拆兩段就清楚：

| 環節 | 誰做 |
|---|---|
| 抓歷史財務、套固定範本格式、填已知科目 | 🏦 成熟系統（Macabacus、FactSet 模型）或自建 Excel 範本——確定、格式穩、便宜 |
| 從零建出「公式化、可 trace」的 DCF／LBO／三表／comps（計算格用公式不寫死）、生成敏感度表 | 🤖 本 agent——規則列不完、要判斷的那段 |
| 拍板、核准模型才往下用 | 👤 建模專員／投資人 |

**優勢來源**
- **對成熟系統**：它們套好格式就停了，模型邏輯要人工填；agent 補的是「從零把公式寫出來、讓計算格可 trace」這段（系統本來留給人的工）。
- **對自建腳本**：不用把每個假設、每種模型結構寫死；讀得懂財報跟 MCP 資料後自行推理，換標的也不必改腳本。

**什麼時候用哪個**
- 套固定格式、科目清楚、大量重複 → 成熟系統範本。
- 從零建新標的的估值模型、需要公式可 trace、要生敏感度表 → agent。
- 更新既有模型的數字 → 用 earnings-reviewer（本 agent 刻意不做）。
- ❌ 純格式化填數字別用 agent（又貴、判斷又非確定）。

## 七、Skill 白話

每支 skill 是一份「給 AI 看的作業手冊」。算術與驗證都導向 Excel 公式，skill 只負責判斷與接線。

- **`dcf-model` 折現估值**：從歷史財務出發建 Bear／Base／Bull 三情境現金流預測，套 CAPM 算 WACC，折現後產 EV→每股股價，底部附三張敏感度表；計算格全部是公式、不寫死，交付前跑 recalc.py 確保零 formula 錯誤。
- **`lbo-model` 槓桿收購**：填 LBO 模型範本——來源與用途、營運預測、債務排程、IRR／MOIC 報酬；優先用使用者提供的範本，計算格全是公式，每節完成後停下來讓人確認再往下。
- **`3-statement-model` 三表**：在範本裡把損益表、資產負債表、現金流量表的公式補齊並勾通，跑平衡檢查（BS 平衡、CF 釘到 BS 現金）；歷史數字用藍色輸入格、預測用公式，分步驗證後才往下。
- **`comps-analysis` 同業倍數**：把可比公司的營運指標（收入／毛利率／EBITDA 倍數）拉成 Excel，用公式算各欄位比率，底部附 Max／75th／Median／25th／Min 統計；原始輸入格要附來源 comment。
- **`audit-xls` 稽核 Excel**：產出前健檢公式——抓 #REF!、藏在公式裡的死數字、漏行的 SUM、斷掉的連結，model scope 還跑 BS 平衡、CF 釘出、循環參照等完整財務模型稽核。
- **`xlsx-author` 產出 Excel**：無頭模式下用 Python 把 .xlsx 寫成檔（藍＝輸入、黑＝公式、綠＝跨表連結，計算格一律公式）；有開著的 Excel 時改用 office 工具直接操作。
