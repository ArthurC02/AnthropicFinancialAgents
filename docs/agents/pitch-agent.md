# 🎯 Pitch Agent（提案簡報）

> **用途**：投行提案助理，針對一個交易/併購標的蒐集可比公司與估值，最終產出含估值模型與品牌簡報的提案包。

`目標公司＋情境 → 自動拉同業比較（comps）/先例＋建現金流折現（DCF）/足球場估值＋產出品牌提案簡報`

| 家族 | 用戶 | 頻率 | 風險 |
|---|---|---|---|
| 客戶經營與顧問（投行） | MD／資深 banker | 要一份第一版 pitch 時 | 🟡 中 |

## 一、Workflow（產出物最複雜：Excel 模型＋簡報）

```
 目標公司 + 一句話情境
     │
     ▼
①界定 ─►②情境概述 ─►③拉資料 ─►④spread同業 ─►⑤LBO ─►⑥建模型 ─►⑦足球場 ─►⑧填簡報 ─►⑨簡報QC
        sector-     CapIQ      comps-        lbo-    dcf/      高/中/低   pitch-    ib-check-
        overview               analysis      model   3-stmt    疊圖       deck      deck
                                                                                       │
                                                            (模型後·簡報後各停一次)    ▼
                                                                                  banker審 👤
```
> 足球場（football field）：把各估值法的高/中/低疊成橫條圖比較　|　可比公司（comps）／先例交易（precedents）／現金流折現（DCF）／槓桿收購（LBO）　|　刻意不做：改既有簡報（直接用 pitch-deck 技能）

**步驟拆解**
1. **界定範圍** — 把目標公司、產業跟情境確認清楚，圈出 5–8 家性質相近的可比公司，跟幾筆類似的過往交易。
   - 步驟說明：先框定目標、產業跟情境的邊界，圈出 5–8 家可比公司（comps）跟 5–10 筆先例交易（precedents），當作後面分析的範圍。
2. **寫情境概述** — 草擬這家公司的快照，跟為什麼現在值得談：在做什麼、市場地位、有什麼變化。
   - 步驟說明：產業總覽加 narrative——產出公司快照跟策略理由（在做什麼、市場地位、有何變化、為何是現在）（用 `sector-overview` 這個 skill）。
3. **蒐集資料** — 把估值倍數、過往類似交易，還有目標公司最新財報拿到手。
   - 步驟說明：接 MCP 拉資料——用 CapIQ MCP 抓交易倍數、先例交易數據跟目標公司最新財報，財報要載入全文、不做摘要。
4. **比較同業** — 把可比公司跟過往交易攤開比一比，看合理估值大概落在哪個區間。
   - 步驟說明：spread 同業加標離群——用一致的指標定義把可比公司跟先例交易 spread 出來、標出離群值（outlier），推估估值區間（用 `comps-analysis` 這個 skill）。
5. **做收購示意模型** — 用市場常見的舉債水準，試算一份收購（槓桿收購）大概能有多少報酬。
   - 步驟說明：示意 LBO 建模——用市場的舉債水準試算槓桿收購（LBO）的進出場假設、來源與用途、報酬敏感度（用 `lbo-model` 這個 skill）。
6. **補齊其他模型** — 再補上現金流折現跟三大報表那些模型。
   - 步驟說明：補建 DCF 跟三表，並照 `audit-xls` 的稽核慣例走（藍輸入／黑公式／綠連結、計算格不寫死、含平衡檢查）（用 `dcf-model`、`3-statement-model` 這兩個 skill）。
7. **畫估值區間圖** — 把各種方法算出的高／中／低估值疊成一張「足球場」橫條圖，跟現價對照。
   - 步驟說明：疊足球場圖——把 comps／先例／DCF／LBO 各法的最小／中位／最大值疊成橫條圖，再標上現價對照（football field）。
8. **製作簡報** — 套上銀行的簡報 template，把分析填進去，每個數字都要對得回前面的模型。
   - 步驟說明：產簡報加可追溯——套上銀行 template 填入分析，簡報上每個數字都能 trace 回 workbook 的具名範圍（named range）（用 `pitch-deck` 這個 skill）。
9. **簡報複查** — 核對加總、註腳、日期都正確又一致。
   - 步驟說明：簡報 QC——核對加總對得起來、註腳齊全、日期一致（用 `ib-check-deck` 這個 skill）。

## 二、風險與把關

```
 agent ──Excel+簡報──► banker（內部）    ✗ 無 email/通訊工具，不對外聯絡

 發行人財報(外來) ──► 載入全文·不摘要 ──► 流程
```
> guardrail：每個數字都要有出處，查不到就標 `[UNSOURCED]`　|　最後防線：沒有對外通訊;模型後/簡報後各停一次給人審

## 三、技術架構

**技能鏈**
```
sector-overview ─► comps-analysis ─► lbo/dcf/3-statement ─► pitch-deck ─► ib-check-deck
情境概述          spread同業/先例    建模型                填簡報        簡報QC
```
**Skill（共 11 支）**　`sector-overview` · `comps-analysis` · `lbo-model` · `dcf-model` · `3-statement-model` · `audit-xls` · `pitch-deck` 填簡報 · `ib-check-deck` 簡報QC · `deck-refresh` 重整圖表 · `xlsx-author` 產 Excel · `pptx-author` 產簡報檔（後兩支 deck-writer 寫檔用）
**可加掛的模型**　併購提案要算 accretion／dilution 可加掛 `merger-model`（怎麼掛見 [Models.md](../Models.md)）
**MCP**　`capiq`（CMA 版另加 `daloopa`）;`capiq` 在 vertical `.mcp.json` 已定義，指向本機 mock（`mock-mcp/`，假 CSV），要上線把 url 改指你的 CapIQ／S&P feed，`daloopa` 是公開供應商

> 工具：讀＋**寫檔**＋CapIQ MCP　|　模型：opus-4-7

**外掛 vs CMA（兩種安裝）**
```
 外掛版 (真人盯)         CMA版 (雲端·無頭)
 ┌───────────┐          ┌──────────────────────────┐
 │ 單一agent │          │ 主代理 (不寫)            │
 │ 可直接寫檔│          │  ├ researcher  拉資料/研究│
 └───────────┘          │  ├ modeler     建模      │
                        │  └ deck-writer 唯一可寫  │
                        └──────────────────────────┘
```
> 🎯 招牌設計：流程最長（9 步），而且算跟寫分離——modeler 用 Python（via bash）跑 DCF／LBO 算出 JSON、不寫檔;deck-writer 才是唯一能寫的，把簡報上每個數字都綁回 workbook 的具名範圍（named range），確保圖表跟模型 sync。

**改哪裡（快速 map）**

| 想改 | 動這個檔 |
|---|---|
| 流程／兩個 stop 點／守則 | `agents/pitch-agent.md` 的 Workflow／Guardrails |
| 用哪些 skill | 同檔的 Skills 行（加掛 merger-model 見 [Models.md](../Models.md)） |
| 投行簡報版型 | `pitch-deck/SKILL.md` 真本（＋`/ppt-template`）→ sync |
| 幾個 sub-agent | `cookbooks/pitch-agent/agent.yaml` 的 callable_agents |
| researcher 輸出限制 | `subagents/researcher.yaml` 的 output_schema |

> 通用改法見 [Customizing.md](../Customizing.md);上線要補的見下方 §四。

**跨 agent**　客戶經營與顧問家族 ┄ end-to-end 把多個 skill 串起來;跟〔meeting-prep〕同屬前台，但產出物複雜得多

## 四、上線前要補齊（客製化）

```
 Anthropic 參考骨架    ＋    貴公司要補的    ＝    可實際上線
```
- 🔌 **接資料訂閱**：`daloopa` 是公開供應商，**要訂閱／API key**;`capiq` 在 vertical `.mcp.json` 已定義、指向本機 mock（`mock-mcp/`，假 CSV）——想離線 demo 跑 `python3 mock-mcp/run_all_http.py`，要上線把 url 改指你的 CapIQ／S&P feed（伺服器名跟 frontmatter `tools:` 都不要改）
- 🎨 **銀行 PPT template（關鍵）**：用 `/ppt-template` 把貴銀行的版型教給 Claude → `pitch-deck` 才套得對 → `plugins/vertical-plugins/investment-banking/skills/pitch-deck/SKILL.md`
- 📐 **comps/先例慣例**：指標定義、同業圈選 → `plugins/vertical-plugins/financial-analysis/skills/comps-analysis/SKILL.md`
- ✏️ **調整範圍** → `plugins/agent-plugins/pitch-agent/agents/pitch-agent.md`
- 👤 **人工 review 不變**：模型後/簡報後各停一次，banker 核准才往下

> ⚠️ skill 一律改 `vertical-plugins/` 的 source（真本），改完跑 `python3 scripts/sync-agent-skills.py` 做 sync。

## 五、導入評估

| 面向 | 評估 |
|---|---|
| **導入風險** | 🟡 中 — 提案簡報（pitch）是對外要給客戶看的正式文件，會影響投資跟併購決策的溝通，但有 banker 在模型後、簡報後各簽核一次把關，不是法規強制過帳那種，所以算中度。 |
| **導入成本** | 🟡 中（偏高） — 資料端 `capiq` 在 vertical `.mcp.json` 已接本機 mock，要上線把 url 改指你的 CapIQ／S&P feed（或其他公開 source，訂閱＋API key）;更重的是要重度客製投行簡報 template（PPT 版型）、QC 規則跟財務模型慣例（comps／先例指標定義、建模配色稽核），整合工程不輕鬆。 |
| **適用單位** | 投資銀行部前台（併購／企業融資）、產業組（Coverage） |
| **單位中角色** | 資深 banker／董事總經理（下情境指令＋兩次簽核把關）· 分析師／經理（覆核模型與簡報數字）· 助理（草稿與資料加工） |

**最有機會成功的場景**
1. **初次接觸客戶的第一版 pitch** — banker 要快速生一份結構完整、含同業比較（comps）跟估值的提案初稿，省下一堆手工拉資料跟排版，再讓人覆核收尾，CP 值最高。
2. **既有覆蓋客戶的定期更新提案** — 對已往來的客戶定期刷新估值跟市場格局，沿用既有 template 跟模型慣例，客製成本攤提後邊際效益高。
3. **臨時併購想法的快速估值草稿** — 內部要對某個標的快速跑出足球場（football field）估值區間做可行性判斷，先有草稿再人工把關。
