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

**跨 agent**　客戶經營與顧問家族 ┄ end-to-end 把多個 skill 串起來;跟〔meeting-prep〕同屬前台，但產出物複雜得多

## 四、要調什麼、改哪裡（業務內容調整表）

```
 Anthropic 參考骨架    ＋    貴公司要補的    ＝    可實際上線
 (提示詞·技能·流程)          (資料·規則·範本)
```

> 先分清楚：門檻、規則、清單多半設計成「執行時餵」就好；要變成公司預設才改 source。

| 想調的業務內容 | 改哪個檔 | 怎麼改 |
|---|---|---|
| 建模慣例（WACC·色碼·LBO 假設·三表勾稽） | `dcf-model`／`lbo-model`／`3-statement-model` SKILL.md | 臨時 prompt 給；永久改值 → sync |
| comps／先例慣例（指標定義·同業圈選·離群判定） | `comps-analysis` SKILL.md | 改 → sync |
| 投行簡報版型 | `pitch-deck` SKILL.md（先用 `/ppt-template` 把版型教給 Claude）／`pptx-author` 範本 | 改 → sync |
| QC 規則（簡報四維審查·Excel 稽核範圍） | `ib-check-deck`／`audit-xls` SKILL.md | 改 → sync |
| 既有 deck 刷新行為（只改值不動格式） | `deck-refresh` SKILL.md | 改 → sync |
| 流程／兩個 stop 點／守則／掛哪些 skill | `agents/pitch-agent.md`（Workflow／Skills 行） | 直接改劇本（外掛＋CMA 同時生效；加掛 merger-model 見 [Models.md](../Models.md)） |
| 接真實資料（外掛） | `financial-analysis/.mcp.json` | `capiq` 的 url 從本機 mock 改指你的 CapIQ／S&P feed（capiq 借自 financial-analysis，別改 server 名） |
| 接真實資料（CMA） | `cookbooks/pitch-agent/agent.yaml` | 設對應 env var（CMA 版另加 `daloopa`；別改 server 名） |
| sub-agent 數量／researcher 輸出限制 | `agent.yaml`／`subagents/researcher.yaml` | 改 callable_agents／output_schema |

**三條路線**
- ① 臨時（不改檔）：門檻／政策／清單直接在 prompt 或 `steering-examples.json` 給。
- ② 永久（改預設）：改 `vertical-plugins/` 的 SKILL.md 真本 → `python3 scripts/sync-agent-skills.py` → `check.py`（drift 會擋 commit；別手改 bundle 的 copy）。
- ③ 接系統：改 `.mcp.json` 的 url（外掛）或 env var（CMA）；**server 名別改**。

**接真實系統要做到**（上線必補；現都已接本地 mock，跑 `python3 mock-mcp/run_all_http.py` 可離線端到端跑）
- 🛠️ `capiq`：在 `financial-analysis/.mcp.json` 已定義、指向本機 mock（假 CSV），上線把 url 改指你的 CapIQ／S&P feed
- 🛠️ `daloopa`：CMA 版另加的公開供應商，**要買訂閱＋API key** 才接得上
- 👤 **人工覆核不變**：模型後／簡報後各停一次，對外發布前要 banker 審核才往下

> 通用改法見 [Customizing.md](../Customizing.md)。這支刻意把公司專屬的東西留空，你填上去才算完整。

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

## 六、它補的是哪一段（與成熟系統／自建的分工）

它不是簡報自動化工具、也不是投行 deck 範本庫，而是坐在那些系統「上面」做判斷的那一層。把提案製作拆兩段就清楚：

| 環節 | 誰做 |
|---|---|
| 套固定 PPT 版型、格式化已知數字、批次更新既有 deck | 🏦 成熟系統（Pitch 自動化平台、deck 範本工具）或 associate 手工做版——確定、格式穩、便宜 |
| 端到端串研究＋建模＋簡報：從 comps／DCF／LBO 到足球場圖再到品牌簡報，每個數字都能 trace 回 workbook 具名範圍 | 🤖 本 agent——規則列不完、要判斷的那段 |
| 拍板、對外發布前簽核 | 👤 資深 banker／MD |

**優勢來源**
- **對成熟系統**：它們處理格式與版型，但把研究、建模、敘事端到端串起來還是人工；agent 補的是「從產業概述到足球場到品牌 deck 一條龍、數字可追溯」這段。
- **對自建 associate 流程**：不用把每個 comps 指標定義、每張 slide 的格式規則寫死；換標的也不必重新教流程。

**什麼時候用哪個**
- 純格式刷新、更新既有 deck 的數字 → 成熟系統或 `deck-refresh` 技能。
- 從零生一份結構完整的初版 pitch（comps＋模型＋足球場＋簡報） → agent。
- 更新既有簡報的圖表配色或重整版面 → 成熟系統（agent 刻意不做改既有簡報）。
- ❌ 純簡報排版別用 agent（又貴、判斷又非確定）。

## 七、Skill 白話

每支 skill 是一份「給 AI 看的作業手冊」。算術與驗證都導向 Excel 公式，skill 只負責判斷與接線。

- **`sector-overview` 產業概述**：生成產業總覽，包含市場規模（含來源）、競爭格局、主要驅動因素與風險，以及可比公司一覽表；輸出供後續 pitch 填入的敘事底稿。
- **`comps-analysis` 同業倍數**：把可比公司與先例交易的營運指標（收入／EBITDA 倍數等）拉成 Excel，用公式算各欄位比率，底部附 Max／75th／Median／25th／Min 統計，標出離群值；原始輸入格附來源 comment。
- **`lbo-model` 槓桿收購**：填 LBO 模型範本——來源與用途、營運預測、債務排程、IRR／MOIC 報酬敏感度；優先用使用者提供的範本，計算格全是公式，每節完成後停下確認再往下。
- **`dcf-model` 折現估值**：從歷史財務出發建 Bear／Base／Bull 三情境現金流預測，套 CAPM 算 WACC，折現後產 EV→每股股價，底部附敏感度表；計算格全是公式、不寫死，交付前跑 recalc.py 確保零 formula 錯誤。
- **`3-statement-model` 三表**：補齊損益表、資產負債表、現金流量表公式並勾通，跑平衡檢查；歷史數字藍色輸入格、預測用公式，分步驗證後才往下。
- **`audit-xls` 稽核 Excel**：產出前健檢公式——抓 #REF!、藏在公式裡的死數字、漏行的 SUM、斷掉的連結，model scope 還跑 BS 平衡、CF 釘出、循環參照等完整財務模型稽核。
- **`pitch-deck` 填簡報**：把分析資料套進銀行 PPT 範本，每個數字都綁回 workbook 具名範圍（named range）確保圖表與模型同步；消除佔位符色塊、產真正的表格物件，最後提醒用 PowerPoint 驗收（LibreOffice 渲染有差異）。
- **`ib-check-deck` 簡報 QC**：對 pitch deck 做四維度審查——跨 slide 數字一致性、資料與敘事對齊、投行語言規格、視覺格式；嚴重／重要／小問題分級，Critical 問題不消則不能交客戶。
- **`deck-refresh` 重整圖表**：用新數字更新既有 deck（季報刷新、comps 滾動、換底稿數字）；先 show 變更計畫讓人確認再動，只改值不動格式，最後視覺驗證有無溢出。
- **`xlsx-author` 產出 Excel**：無頭模式下用 Python 把 .xlsx 寫成檔（藍＝輸入、黑＝公式、綠＝跨表連結，計算格一律公式）；有開著的 Excel 時改用 office 工具直接操作。
- **`pptx-author` 產出簡報檔**：無頭模式下用 Python 把 .pptx 寫成檔；每張 slide 標題寫結論、數字釘回模型、有範本就套範本；有開著的 PowerPoint 時改用 office 工具。
