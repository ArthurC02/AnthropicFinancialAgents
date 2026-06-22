# 🔍 KYC Screener

> **用途**：開戶審查助理，幫你解析開戶文件、套反洗錢規則、比對黑名單，最後產一份給合規官的盡職調查報告。

`開戶文件 → 整理成「客戶是誰／風險多高／缺什麼」→ 給合規官簽核`

| 家族 | 用戶 | 頻率 | 風險 |
|---|---|---|---|
| 後台作業 | 合規官 | 開戶＋定期複審 | 🔴 高 |

## 一、Workflow

```
 開戶文件包
     │
     ▼
┌─────────┐   ┌─────────┐   ┌──────────────┐   ┌────────┐
│①讀文件  │──►│②套規則  │──►│③比對黑名單   │──►│④打包   │
│抽欄位   │   │風險評分 │   │制裁/PEP/負面 │   │升級報告│
│留空不猜 │   │引用規則 │   │新聞          │   └───┬────┘
└─────────┘   └─────────┘   └──────────────┘       │
                                                    ▼
                                             合規官簽核 ⚖️
```
> 政治公眾人物（PEP，洗錢風險較高）　|　刻意不做：交易監控

**步驟拆解**
1. **讀開戶文件** — 從開戶文件裡讀出公司名稱、實際出資人、地址、證件號等基本資料。
   - 步驟說明：隔離抽取——由 doc-reader 這個 sub-agent 抽欄位，它只有讀／搜尋權限、沒有 MCP，回傳有長度上限的 structured JSON，把不可信文件擋在流程外（`kyc-doc-parse` 這個 skill）。
2. **逐條套規則** — 拿這些資料對照開戶與防制洗錢的規則，標出哪裡通過、哪裡不通過，並附上證據。
   - 步驟說明：規則引擎評分——用 `kyc-rules` 規則引擎逐條跑抽出來的欄位，輸出每條規則的通過／不通過跟證據引用。
3. **比對黑名單** — 對每一個相關人，查制裁名單、政治人物名單與負面新聞有沒有命中。
   - 步驟說明：接篩查 MCP（唯讀）——透過 screening MCP 對每位相關人查制裁／PEP（政治公眾人物）／負面新聞，回傳命中跟比對信心。
4. **整理待簽報告** — 把查到的缺漏與命中整理成一份報告，送給法遵人員簽核。
   - 步驟說明：限制 structured output——把已驗證的缺漏跟命中交給唯一可寫的 escalator 這個 sub-agent 打包成合規報告（`xlsx-author` 這個 skill），主代理永遠不寫檔。

## 二、風險與把關

```
 agent ──建議──► 合規官 ⚖️ 決定        ✗ agent 永不核准

 不可信文件 ──►[格式防火牆]──► 乾淨資料 ──► 流程
 (怕藏惡意指令)  只當資料·嚴格格式
```
> 守則：查不到就留空、不捏造　|　最後防線：不核准

## 三、技術架構

**技能鏈**
```
kyc-doc-parse ──► kyc-rules ──► (screening MCP)
讀文件抽資料      套規則評分     查黑名單·唯讀
```
**Skill（共 3 支）**　`kyc-doc-parse` 讀文件抽資料 · `kyc-rules` 套規則評分 · `xlsx-author` 產出報告檔
**MCP（1 個）**　`screening` 黑名單篩查／制裁·PEP·負面新聞（唯讀）

> 工具：讀／搜尋＋黑名單 connector　⚠️ 不能寫檔·不能委派　|　模型：opus-4-7

**外掛 vs CMA（兩種安裝）**
```
 外掛版 (Claude Code·真人盯)      CMA版 (雲端·無頭自動)
 ┌────────────────┐              ┌─────────────────────────┐
 │ 單一 agent     │              │ 主代理 (不寫·不碰髒)    │
 │ 工具被收窄     │              │  ├ doc-reader  只讀·碰髒 │
 └────────────────┘              │  ├ rules-engine 套規則  │
  安全靠：真人＋收窄              │  └ escalator   唯一可寫 │
                                 └─────────────────────────┘
                                  安全靠：拆分＋分權
```
> 🎯 招牌設計：KYC 的輸入是全 10 支裡最髒的領域（護照、設立文件、UBO 股權圖），所以 doc-reader 的 output_schema 切得最細——country 限兩碼大寫（`^[A-Z]{2}$`）、每個 UBO 的 pct 限數字，硬把不可信文件壓成嚴格結構。配上「不下決定」守則：agent 只建議風險評等，真正放行是合規官

**改哪裡（快速 map）**

| 想改 | 動這個檔 |
|---|---|
| 流程／stop 點／守則 | `agents/kyc-screener.md` 的 Workflow／Guardrails |
| 用哪些 skill | 同檔的 Skills 行 |
| KYC 規則／風險評等門檻 | `kyc-rules/SKILL.md` 真本 → sync |
| 幾個 sub-agent | `cookbooks/kyc-screener/agent.yaml` 的 callable_agents |
| doc-reader 輸出限制 | `subagents/doc-reader.yaml` 的 output_schema |

> 通用改法見 [Customizing.md](../Customizing.md);上線要補的見下方 §四。

> Claude 託管代理（CMA, Claude Managed Agents），deploy 到 Anthropic 雲端、無頭自動跑

**跨 agent**　後台作業家族 ┄ 跟〔對帳〕〔結帳〕並列，各管一塊

## 四、上線前要補齊的（客製化）

```
 Anthropic 參考骨架    ＋    貴公司要補的    ＝    可實際上線
 (提示詞·技能·流程)          (資料·規則·範本)
```

- 🔌 **接真實篩查源**：`screening` MCP（port 8006）已經接到本地 mock（`mock-mcp/`），跑 `python3 mock-mcp/run_all_http.py` 就能用假資料把 agent 端到端離線跑起來（零金鑰、零內部系統）
  - 外掛 → server 已定義在 `plugins/vertical-plugins/operations/.mcp.json`，上線只要把該 server 的 `url` 從 `127.0.0.1:8006` 改指向你的真實系統（別改 server 名、也別動 agent frontmatter 的 `tools:` 名稱）
  - CMA → 設 env var `SCREENING_MCP_URL`（或改 `managed-agent-cookbooks/kyc-screener/agent.yaml`）
  - 🛠️ MCP 要做到：**依人名查** → 回傳制裁／PEP／負面新聞命中＋比對信心（規格見 `kyc-rules` 這個 skill）
- 📋 **規則表／門檻**：風險因子·高風險國家·風險評等邏輯 → `plugins/vertical-plugins/operations/skills/kyc-rules/SKILL.md`
- 📋 **必備文件清單** → `plugins/vertical-plugins/operations/skills/kyc-doc-parse/SKILL.md`
- 📄 **Excel template** → `plugins/vertical-plugins/financial-analysis/skills/xlsx-author/`
- ✏️ **調整 agent 範圍** → `plugins/agent-plugins/kyc-screener/agents/kyc-screener.md`
- 👤 **人工覆核不變**：只產建議評等，合規官決定，永遠不自動核准

> ⚠️ skill 一律改 `vertical-plugins/` 的 **source(真本)**，改完跑 `python3 scripts/sync-agent-skills.py` sync 到 agent。這個 agent 是刻意把公司專屬的東西留空，你填上去才算完整。

## 五、導入評估

| 面向 | 評估 |
|---|---|
| **導入風險** | 🔴 高 — 開戶審查跟防制洗錢（AML）是法遵把關，制裁／政治公眾人物（PEP）一旦錯放，後果直接牽涉監管裁罰跟聲譽風險；雖然 agent 只產建議評等、要合規官簽核，但這業務本身高度敏感，誤判的成本極高。 |
| **導入成本** | 🔴 高 — `screening` MCP 雖然已接好本地 mock（可離線端到端跑），但上線要把它從 mock repoint 到真實的制裁／PEP／負面新聞篩查源（內部或訂閱），還要客製規則表（風險因子·高風險國家·風險評等邏輯）、門檻跟必備文件清單；這是自建內部系統＋內部資料／規則表的重整合。 |
| **適用單位** | 法令遵循部、防制洗錢專責單位、開戶／客戶盡職調查（KYC）作業部門 |
| **單位中角色** | 合規官（下指令＋審查建議＋簽核決定）· 防制洗錢專責人員（維護規則表／門檻＋複審命中）· 開戶作業人員（備齊文件＋送件） |

**最有機會成功的場景**
1. **新客戶開戶的初步盡職調查** — 開戶文件一進來，agent 自動抽欄位、套規則、比對黑名單，把「缺什麼／命中什麼」整理成待簽報告，省下大把人工逐筆查核的時間，合規官只要覆核決策就好。
2. **既有客戶的定期複審（KYC Refresh）** — 例行週期性重跑風險評等跟名單比對，及早抓出新增的制裁／PEP／負面新聞命中，避免人工漏掉。
3. **高風險客群的批次預篩** — 對特定高風險國家或產業客群批次跑篩查，先把需要人工深入調查的案件過濾出來，讓合規人力集中在真正可疑的個案。
