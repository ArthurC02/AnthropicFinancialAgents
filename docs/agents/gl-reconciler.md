# ⚖️ GL Reconciler（總帳對帳）

> **用途**：總帳對帳助理，幫你比對總帳跟子帳、把對不上的差異挑出來追根因，最後產一份例外報告給控制員簽。

`總帳 vs 子帳 → 找出對不上的差異 → 追根因 → 例外報告給控制員簽核`

| 家族 | 用戶 | 頻率 | 風險 |
|---|---|---|---|
| 後台作業（基金行政） | 控制員 | 每日／月底 | 🔴 高 |

## 一、Workflow

```
 GL總帳 + 子帳 (某交易日)
     │
     ▼
┌────────┐  ┌────────┐  ┌────────┐  ┌──────────┐  ┌────────┐
│①拉餘額 │─►│②找差異 │─►│③追根因 │─►│④獨立複核 │─►│⑤例外報告│
│GL/子帳 │  │每類資產│  │逐筆追到│  │critic    │  │給控制員│
│        │  │一reader│  │來源    │  │確認/駁回 │  └───┬────┘
└────────┘  └────────┘  └────────┘  └──────────┘      │
            (扇出並行)              (過濾誤報)          ▼
                                                  控制員簽核 ⚖️
```
> 差異＝break，總帳與子帳對不上的地方　|　刻意不做：過帳（那是月底結帳）

**步驟拆解**
1. **拉出兩邊的帳** — 把總帳和明細帳（子帳）在指定日期、指定資產上的餘額都拉出來。
   - 步驟說明：接 MCP 拉資料（兩邊都唯讀）——透過總帳 MCP（`internal-gl`）跟子帳 MCP（`subledger`），照交易日和資產類別把兩邊餘額拉出來當比對基準。
2. **比對找差異** — 逐類比對兩邊，把對不起來、超過容許範圍的差異挑出來。
   - 步驟說明：fan-out 並行比對——每個資產類別派一個 reader 同時跑，用 `gl-recon` 這個 skill 比對兩邊餘額，把超過容差門檻的差異（break）挑出來。
3. **追查原因** — 一筆筆往下追，搞清楚每個差異是時間差、系統落差、還是分類錯誤。
   - 步驟說明：一筆筆追根因——對每個 break 把底層分錄跟交易拉出來，用 `break-trace` 這個 skill 追到來源，再分類（時間差／系統落差／重分類／不明）。
4. **獨立複查** — 由另一個角色拿可信來源重查一遍，把其實沒問題的假差異濾掉。
   - 步驟說明：對抗式 review——critic 這個 sub-agent（唯讀）拿可信來源把每筆回報的差異再 review 一遍，用對抗式 review 把誤報（false positive）濾掉，只留真的往上送。
5. **產出例外報告** — 把確認過的差異整理成一份可簽核的例外清單。
   - 步驟說明：產報告——把確認後的差異集交給唯一可寫的 resolver，用 `audit-xls`／`xlsx-author` 這兩個 skill 格式化成一份可供控制員簽核的例外報告。

## 二、風險與把關

```
 agent ──建議──► 控制員 ⚖️ 決定        ✗ agent 永不過帳

 對帳單(外來) ──► reader(無MCP·無寫) ──► 結構化資料 ──► 流程
 (不可信)
```
> 守則：對不上就攤開講、不硬湊（plug）　|　最後防線：不 post（不過帳）

## 三、技術架構

**技能鏈**
```
gl-recon ──► break-trace ──► (audit-xls / xlsx-author)
比對找差異   逐筆追根因      檢查／產出報告
```
**Skill（共 4 支）**　`gl-recon` 比對找差異 · `break-trace` 追根因 · `audit-xls` 檢查 Excel · `xlsx-author` 產出報告檔
**MCP（2 個）**　`internal-gl` 內部總帳 · `subledger` 子帳明細（兩個都唯讀）

> 工具：讀／搜尋＋總帳MCP＋子帳MCP（都唯讀）　⚠️ 不能寫檔·不能委派　|　模型：opus-4-7

**外掛 vs CMA（兩種安裝）**
```
 外掛版 (真人盯)              CMA版 (雲端·無頭)
 ┌────────────┐             ┌──────────────────────────┐
 │ 單一 agent │             │ 主代理 (不寫·不碰髒)     │
 │ 工具收窄   │             │  ├ reader   讀對帳單·碰髒 │
 └────────────┘             │  ├ critic   獨立複核·唯讀 │ ◄ 對抗式驗證
  安全靠：真人＋收窄        │  └ resolver 唯一可寫     │
                            └──────────────────────────┘
                             安全靠：拆分＋分權
```
> 🎯 招牌設計：全 10 支裡唯一「髒 reader + 獨立 critic」的雙層（4 階段）。reader 的 output_schema 把差異原因 suspected_cause 鎖成固定 enum（`temporal_cutoff`／`system_drift`／`reclass`／`unknown`），連分類都不給自由發揮、注入塞不進來；reader 還是 per asset class fan-out 並行。critic 則拿可信 MCP 重算、做對抗式 review，把誤報濾掉只送真的——對帳容易誤報，所以才需要這層

**改哪裡（快速 map）**

| 想改 | 動這個檔 |
|---|---|
| 流程／stop 點／守則 | `agents/gl-reconciler.md` 的 Workflow／Guardrails |
| 用哪些 skill | 同檔的 Skills 行 |
| 容差門檻（0.01）／根因規則 | `gl-recon`／`break-trace` 的 SKILL.md → sync |
| 幾個 sub-agent | `cookbooks/gl-reconciler/agent.yaml` 的 callable_agents |
| reader 輸出限制 | `subagents/reader.yaml` 的 output_schema |

> 通用改法見 [Customizing.md](../Customizing.md);上線要補的見下方 §四。

**跨 agent**　fund-admin 三兄弟 ┄ 本 agent（日常對帳）╳ 月底結帳 ╳ 報表稽核，各自劃好邊界

## 四、上線前要補齊的（客製化）

```
 Anthropic 參考骨架    ＋    貴公司要補的    ＝    可實際上線
 (提示詞·技能·流程)          (資料·規則·範本)
```

- 🔌 **接真實帳務系統**：`internal-gl`／`subledger` 都還是 placeholder（佔位，repo 裡沒定義）
  - 外掛 → 新增 `plugins/vertical-plugins/fund-admin/.mcp.json`（目前不存在）
  - CMA → 設 env var `GL_MCP_URL`／`SUBLEDGER_MCP_URL`（或改 `managed-agent-cookbooks/gl-reconciler/agent.yaml`）
  - 🛠️ `internal-gl` 要做到：①查餘額（資產類別·交易日）②依 GL 明細查分錄 → 分錄號·過帳日·來源系統·批次號·製單人
  - 🛠️ `subledger` 要做到：①查持倉/餘額（資產類別·交易日）②依 key 查交易 → 交易號·交易日·交割日·對手·feed·FX率（規格見 `gl-recon`、`break-trace`）
- 🎚️ **容差門檻**（預設金額 `0.01`／數量 `0`）＋🗺️ **科目對應表** → `plugins/vertical-plugins/fund-admin/skills/gl-recon/SKILL.md`
- 🔎 **追根因規則** → `plugins/vertical-plugins/fund-admin/skills/break-trace/SKILL.md`
- 📦 **資產類別清單**（決定要 fan-out 幾個 reader）＋✏️ **調整範圍** → `plugins/agent-plugins/gl-reconciler/agents/gl-reconciler.md`
- 📄 **Excel template** → `plugins/vertical-plugins/financial-analysis/skills/xlsx-author/`
- 👤 **人工覆核不變**：只產例外報告，永遠不 post（不過帳）

> ⚠️ skill 一律改 `vertical-plugins/` 的**source(真本)**，改完跑 `python3 scripts/sync-agent-skills.py` sync 到 agent。這個 agent 是刻意把公司專屬的東西留空，你填上去才算完整。

## 五、導入評估

| 面向 | 評估 |
|---|---|
| **導入風險** | 🔴 高 — 對帳結果直接牽涉帳務正不正確跟財務誠信，差異沒抓到就會污染後面的結帳跟報表。雖然 agent 只產例外報告、永遠不過帳，最後一定由控制員簽核覆核，但只要把真差異漏掉、或是硬湊（plug），影響的就是財務真實性，這是合規等級的風險。 |
| **導入成本** | 🔴 高 — 要自建內部系統整合：`internal-gl` 跟 `subledger` 都還是 placeholder（佔位），得接內部總帳／子帳系統（查餘額、查分錄／交易明細），還要設容差門檻、科目對應表、追根因規則，再決定資產類別清單（決定要 fan-out 幾個 reader）。資料格式跟規則都是內部專屬的，整合工程不小。 |
| **適用單位** | 基金行政後台作業、財務／帳務控制、託管行對帳團隊 |
| **單位中角色** | 對帳控制員（下指令＋簽核例外報告）· 帳務主管（核定容差與科目對應）· 後台作業員（提供帳務／對帳單來源） |

**最有機會成功的場景**
1. **每日例行 GL vs 子帳對帳** — 資產類別固定、容差規則固定的日常比對，量大又重複，agent 用 fan-out 並行比對最省人工，CP 值最高。
2. **月底結帳前的差異清理** — 結帳前要把累積的 break 一筆筆追根因、濾掉誤報，agent 的 critic 對抗式 review 能擋掉假差異，讓控制員只看真的。
3. **新增資產類別／系統 feed 上線後的對帳驗證** — 換子帳系統或新加 feed 之後，臨時要密集核對兩邊一不一致，agent 可以很快一筆筆追到來源系統的落差。
