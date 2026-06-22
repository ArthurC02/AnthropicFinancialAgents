# 📅 Month-End Closer（月底結帳）

> **用途**：月結作業助理，幫你算應計與結轉、說明科目差異，最後產一份月結包給控制員簽。

`跑月底結帳（應計／結轉／差異說明）→ 結帳包給控制員簽核`

| 家族 | 用戶 | 頻率 | 風險 |
|---|---|---|---|
| 後台作業（基金行政） | 控制員 | 每月底 | 🔴 高 |

## 一、Workflow

```
 實體 + 期間 (YYYY-MM)
     │
     ▼
┌──────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│①拉試算表 │─►│②建應計+結轉│─►│③差異說明   │─►│④組裝結帳包 │
│GL總帳    │  │必須對得上  │  │解釋為什麼  │  │poster組裝  │
│          │  │foot check  │  │不瞎掰      │  └─────┬──────┘
└──────────┘  └─────▲──────┘  └────────────┘        │
                    │                                ▼
                內建自我驗證                   控制員簽核 ⚖️
```
> 應計＝已發生未付的費用先估列入帳　|　結轉＝證明「期初＋變動＝期末」對得上　|　刻意不做：日常對帳

**步驟拆解**
1. **拉出試算表** — 依指定公司與月份，調出該月的試算表（全部科目餘額一覽），當作結帳起點。
   - 步驟說明：拉總帳資料——透過 GL MCP（`internal-gl` 內部總帳，唯讀）指定 entity 跟 period（YYYY-MM），把那個期間的全科目餘額抓出來當結帳基礎。
2. **算應計與結轉** — 把這個月該認列卻還沒入帳的費用先估列（應計），並把各科目從月初推算到月底（結轉），確認前後對得上。
   - 步驟說明：建應計與結轉表＋內建驗算——用 `accrual-schedule` 估列應計（accrual）、`roll-forward` 推算結轉（roll-forward），再用內建的 foot check 驗「期初＋變動－沖回＝期末」一定要對得上（自我驗證，沒有外部 critic）。
3. **說明差異** — 對變動較大的科目，從實際發生的事情解釋為什麼變這麼多，不硬湊數字。
   - 步驟說明：差異說明（flux）——`variance-commentary` 對超過重大性（materiality）門檻的科目做差異分析，從底層實際活動解釋為什麼變動，原因不明就直接標示，不瞎掰。
4. **組裝結帳包** — 檢查無誤後，把前面成果整理成一份結帳包，暫存等主管簽核。
   - 步驟說明：組裝結帳包——由 poster 用 `audit-xls`（檢查 Excel）跟 `xlsx-author`（產出報告檔）把前面成果整理成結帳包，先暫存等控制員簽核（agent 永遠不過帳）。

## 二、風險與把關

```
 agent ──草擬分錄──► 控制員 ⚖️ 核准後才過帳    ✗ agent 永不過帳

 發票/對帳單(外來) ──► reader(無MCP·無寫) ──► 結構化 ──► 流程
 (不可信)
```
> 守則：對不上就攤開、不硬湊 · 原因不明就標示、不瞎掰　|　最後防線：不 post（不過帳）

## 三、技術架構

**技能鏈**
```
accrual-schedule ──► roll-forward ──► variance-commentary ──► (audit-xls / xlsx-author)
應計表             結轉表(must foot)   差異說明
```
**Skill（共 5 支）**　`accrual-schedule` 應計表 · `roll-forward` 結轉表 · `variance-commentary` 差異說明 · `audit-xls` 檢查 Excel · `xlsx-author` 產出報告檔
**MCP（1 個）**　`internal-gl` 內部總帳（唯讀）

> 工具：讀／搜尋＋總帳MCP（唯讀）　⚠️ 不能寫檔·不能委派　|　模型：opus-4-7

**外掛 vs CMA（兩種安裝）**
```
 外掛版 (真人盯)         CMA版 (雲端·無頭)
 ┌───────────┐          ┌──────────────────────────┐
 │ 單一agent │          │ 主代理 (不寫)            │
 │ 工具收窄  │          │  ├ ledger-reader 讀帳    │
 └───────────┘          │  ├ rollforward   建結轉  │
                        │  └ poster        唯一可寫 │
                        └──────────────────────────┘
```
> 🎯 招牌設計：沒有獨立 critic——驗證直接內建在結轉的「期初＋變動－沖回＝期末」foot check 裡。因為結帳是「建一張平衡的表」、不是「抓誤報」，驗證設計跟著任務性質走

**改哪裡（快速 map）**

| 想改 | 動這個檔 |
|---|---|
| 流程／stop 點／守則 | `agents/month-end-closer.md` 的 Workflow／Guardrails |
| 用哪些 skill | 同檔的 Skills 行 |
| 重大性門檻（5%）／應計結轉規則 | `variance-commentary`／`accrual-schedule`／`roll-forward` 的 SKILL.md → sync |
| 幾個 sub-agent | `cookbooks/month-end-closer/agent.yaml` 的 callable_agents |
| ledger-reader 輸出限制 | `subagents/ledger-reader.yaml` 的 output_schema |

> 通用改法見 [Customizing.md](../Customizing.md);上線要補的見下方 §四。

**跨 agent**　fund-admin 三兄弟 ┄ 對帳（gl-reconciler）╳ 本 agent（月底結帳）╳ 報表稽核

## 四、上線前要補齊的（客製化）

```
 Anthropic 參考骨架    ＋    貴公司要補的    ＝    可實際上線
 (提示詞·技能·流程)          (資料·規則·範本)
```

- 🔌 **接真實總帳**：`internal-gl`（port 8001）已經接到本地 mock（`mock-mcp/`），跑 `python3 mock-mcp/run_all_http.py` 就能用假資料把 agent 端到端離線跑起來（零金鑰、零內部系統）
  - 外掛 → server 已定義在 `plugins/vertical-plugins/fund-admin/.mcp.json`，上線只要把該 server 的 `url` 從 `127.0.0.1:8001` 改指向你的真實系統（別改 server 名、也別動 agent frontmatter 的 `tools:` 名稱）
  - CMA → 設 env var `GL_MCP_URL`（或改 `managed-agent-cookbooks/month-end-closer/agent.yaml`）
  - 🛠️ `internal-gl` 要做到：①拉試算表（實體·期間）②查分錄（科目·日期區間·來源篩選）③查餘額（科目·日期）（規格見 `roll-forward`、`variance-commentary`）
- 🎚️ **重大性門檻**（預設 `5%`）＋「一定要說明」科目 → `plugins/vertical-plugins/fund-admin/skills/variance-commentary/SKILL.md`
- 📋 **應計／結轉規則** → `plugins/vertical-plugins/fund-admin/skills/accrual-schedule/SKILL.md`、`.../roll-forward/SKILL.md`
- 🧾 **分錄格式／會計科目表（chart of accounts）**＋✏️ **調整範圍** → `plugins/agent-plugins/month-end-closer/agents/month-end-closer.md`
- 📄 **Excel template** → `plugins/vertical-plugins/financial-analysis/skills/xlsx-author/`
- 👤 **人工覆核不變**：只草擬分錄，核准後才過帳

> ⚠️ skill 一律改 `vertical-plugins/` 的**source(真本)**，改完跑 `python3 scripts/sync-agent-skills.py` sync 到 agent。這個 agent 是刻意把公司專屬的東西留空，你填上去才算完整。

## 五、導入評估

| 面向 | 評估 |
|---|---|
| **導入風險** | 🔴 高 — 月結直接影響財報數字跟財務誠信，雖然 agent 只產結帳包、要等控制員（controller）核准後才過帳，但底層的應計／結轉／差異一旦失真，就會污染對外財報。覆核擋得住錯，但風險本質是合規跟財務誠信，不是單純的品質問題。 |
| **導入成本** | 🔴 高 — `internal-gl` 雖然已接好本地 mock（可離線端到端跑），但上線要把它從 mock repoint 到公司內部總帳（拉試算表／查分錄／查餘額）；還要客製應計排程、結轉規則、重大性門檻（預設 `5%`）跟「一定要說明」的科目清單，再加上分錄格式跟會計科目表（chart of accounts）。整合工程重、規則又多。 |
| **適用單位** | 基金行政（後台作業）、財務結帳／總帳部、控制（control）部門 |
| **單位中角色** | 控制員（下指令＋核准過帳，唯一可過帳者）· 結帳會計（產結帳包＋覆核應計結轉）· 財務主管（簽核結帳包＋核重大差異說明） |

**最有機會成功的場景**
1. **例行月結的應計與結轉打底** — 每月固定要估列應計、推算結轉、再驗「期初＋變動＝期末」對不對得上，agent 把這段重複的苦工自動化，控制員只要覆核就好，CP（成本效益）值最高。
2. **重大差異的初步說明草稿** — 超過重大性門檻的科目要寫差異說明（flux），agent 先從底層活動擬一版草稿，會計補上業務脈絡後定稿，省下大把撈資料的時間。
3. **結帳包的組裝與自我檢查** — 把試算表、應計表、結轉表、差異說明組裝成一份 structured 的結帳包，再跑內建 foot check，控制員拿到的就是已經自我驗算過的版本，簽核更快。

## 六、它補的是哪一段（與成熟系統／自建的分工）

它不取代結帳系統，而是坐在上面做「要判斷」的那一層。

| 環節 | 誰做 |
|---|---|
| 拉試算表、模板化常態分錄、結帳清單、超門檻標紅 | 🏦 成熟結帳系統（FloQast／SAP）或自建腳本 |
| 估列要判斷的應計、寫差異原因、反問資料合不合理 | 🤖 本 agent |
| 拍板、過帳 | 👤 控制員 |

**優勢來源**
- **對成熟系統**：它們強在結帳編排／多實體合併／清單管理，但「該估多少應計、為什麼變這麼多、這資料對不對」仍丟給人；agent 補這段知識工作，還會反過來質疑來源資料（例：有固定資產卻整季不提折舊＝疑似漏提）。
- **對自建腳本**：不用把「什麼叫不合理」一條條寫死，會計常識內建；自帶 foot check 與簽核護欄。

**和對帳那支的關鍵差別**：本 agent 沒有獨立 critic，靠結轉的 foot check 自我驗算。因為結帳的錯有等式可對（期初＋變動＝期末），公式自己抓得到；對帳的真假沒有公式可驗，才需要第二雙眼。代價是「判斷型錯誤」只有 foot check＋人兩道，比對帳更要靠人覆核。

**什麼時候用哪個**
- 固定金額的常態應計（租金、攤提）→ 模板化分錄／系統，別用 agent。
- 要判斷的應計、差異敘事、質疑資料 → agent。
- 多實體合併、結帳編排、認證 → 成熟系統（agent 永不過帳）。

## 七、Skill 白話

每支 skill 是一份「給 AI 看的作業手冊」。算術與驗證都導向 Excel 公式，skill 只負責判斷與接線。

- **`accrual-schedule` 估列應計**：把「該認列卻沒入帳」的費用，依全期金額×本期占比−已入帳算出來，附根據、草擬分錄（只擬不過帳）。
- **`roll-forward` 結轉驗算**：把科目從月初推到月底，每條都接得回 GL，並驗「期初＋變動＝期末」一定要 foot；對不上就攤開，不准硬湊（plug）。
- **`variance-commentary` 差異說明**：對超過重大性（預設 5%）的科目，從底層活動寫「為什麼變」而非「變多少」，查不到原因就標示、不掰。
- **`audit-xls` 檢查 Excel**：產出前健檢公式——抓 #REF!、藏在公式裡的死數字、漏行的 SUM、斷掉的連結，確保驗算是活公式。
- **`xlsx-author` 產出報告檔**：無頭模式下用 Python 把 .xlsx 寫成檔（藍＝輸入、黑＝公式、綠＝連結，計算格一律公式）；有開著的 Excel 時改用 office 工具直接操作。
