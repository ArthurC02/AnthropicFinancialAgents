# 🔭 Market Researcher（市場研究）

> **用途**：產業研究助理，針對某投資主題研究產業概況、競品、同業比較，最終產出研究報告。

`產業/主題 → 產業概覽＋競爭格局＋同業 comps＋點子清單 → 研究報告（可選簡報）`

| 家族 | 用戶 | 頻率 | 風險 |
|---|---|---|---|
| 研究與建模 | 分析師／投組經理(PM) | 接到產業或主題研究需求 | 🟡 中 |

## 一、Workflow

```
 產業/主題 + 一句話切角
     │
     ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ ┌────────┐
│①界定   │►│②寫概覽 │►│③競爭格局 │►│④同業comps│►│⑤點子   │►│⑥組裝   │
│8-15名  │ │sector- │ │competit- │ │comps-    │ │idea-   │ │報告    │
│        │ │overview│ │ive-anal  │ │analysis  │ │generat │ └───┬────┘
└────────┘ └────────┘ └──────────┘ └─────┬────┘ └────────┘     │
                                          ▼(stop審)             ▼(stop審)
                                                          分析師審 👤
```
> 可比公司分析（comps），用交易倍數比同業　|　刻意不做：單一標的的追蹤更新（用 earnings-reviewer）

**步驟拆解**
1. **定義研究範圍** — 先把研究問題、市場範圍跟邊界講清楚，找出這個領域裡 8–15 家代表公司。
   - 步驟說明：先框定研究問題跟邊界，圈出 8–15 家標的公司，當作後面分析的範圍。
2. **市場全景分析** — 把這個產業的市場規模、產業結構、值得注意的點、主要成長動力跟風險整理出來。
   - 步驟說明：去外部 source 爬資料，產出一份產業總覽報告（用 `sector-overview` 這個 skill）。
3. **分析競爭格局** — 比較產業裡前幾大公司的營收、成長率跟市占率，看誰強誰弱。
   - 步驟說明：接 MCP 拉資料做動態分析——用 MCP（CapIQ／FactSet）接 source，抓競品的營收、成長、市占等數據來比，比較項目可以自己改（用 `competitive-analysis` 這個 skill）。
4. **做同業 comps** — 用交易倍數把同業攤開比一比，看大家估值落在哪。
   - 步驟說明：用一致的指標定義把同業 spread 出來,推估估值區間（用 `comps-analysis` 這個 skill）。
5. **篩選潛在關注標的** — 根據前面整理好的產業格局跟公司比較，挑出最值得關注的幾個名字。
   - 步驟說明：把多個 source 的資訊整合起來給投資建議——綜合前面幾步蒐集的東西，推薦值得關注的標的（用 `idea-generation` 這個 skill）。
6. **輸出研究報告** — 把研究成果整理成一份報告，需要的話再做成簡報。
   - 步驟說明：產報告——把所有研究成果整合起來，產出市場研究報告，需要時用 `pptx-author` 產簡報。

## 二、風險與把關

```
 agent ──草稿──► 分析師（內部）      ✗ 不對外發布

 第三方報告/發行人資料(外來) ──► 只當資料 ──► 流程
 (不可信)

 兩次停下來給人審：comps 後 · 報告草擬後
```
> guardrail：查不到就標 `[UNSOURCED]`、不要自己亂估　|　最後防線：不發布

## 三、技術架構

**技能鏈**
```
sector-overview ──► competitive-analysis ──► comps-analysis ──► idea-generation
產業概覽           競爭格局               同業倍數          點子清單
```
**Skill（共 5 支）**　`sector-overview` 產業概覽 · `competitive-analysis` 競爭格局 · `comps-analysis` 同業倍數 · `idea-generation` 點子清單 · `pptx-author` 做簡報檔
**MCP（2 個）**　`capiq` · `factset`（`capiq` 在 vertical `.mcp.json` 已定義，指向本機 mock（`mock-mcp/`，假 CSV），要上線把 url 改指你的 CapIQ／S&P feed;`factset` 是公開供應商）

> 工具：讀＋**寫檔**＋CapIQ/FactSet MCP　|　模型：opus-4-7

**外掛 vs CMA（兩種安裝）**
```
 外掛版 (真人盯)         CMA版 (雲端·無頭)
 ┌───────────┐          ┌──────────────────────────┐
 │ 單一agent │          │ 主代理 (不寫)            │
 │ 可直接寫檔│          │  ├ sector-reader   讀資料│
 └───────────┘          │  ├ comps-spreader  spread│
                        │  └ note-writer     唯一可寫│
                        └──────────────────────────┘
```
> plugin 版的主代理可以直接寫檔（研究草稿、風險中），CMA 版還是把寫檔權隔離給 note-writer

> 🎯 招牌設計：三層權限切得很乾淨——sector-reader 碰髒的第三方報告但無 MCP、comps-spreader 有 MCP 但不能寫檔、note-writer 是唯一能寫的且不碰髒源。最漂亮的是 sector-reader 的 output_schema 把每筆 fact 都設成「必須附 source」——「cite every number」不是靠提示拜託 Claude，而是用 schema 寫死：沒附來源的 fact 直接驗不過。

**改哪裡（快速 map）**

| 想改 | 動這個檔 |
|---|---|
| 流程／兩個 stop 點／守則 | `agents/market-researcher.md` 的 Workflow／Guardrails |
| 用哪些 skill | 同檔的 Skills 行 |
| comps 怎麼算（指標定義／圈同業） | `comps-analysis/SKILL.md` 真本 → sync |
| 幾個 sub-agent | `cookbooks/market-researcher/agent.yaml` 的 callable_agents |
| sector-reader 輸出限制 | `subagents/sector-reader.yaml` 的 output_schema |

> 通用改法見 [Customizing.md](../Customizing.md);上線要補的見下方 §四。

**跨 agent**　研究與建模家族 ┄ 跟〔earnings-reviewer〕〔model-builder〕互補

## 四、上線前要補齊（客製化）

```
 Anthropic 參考骨架    ＋    貴公司要補的    ＝    可實際上線
```
- 🔌 **接資料訂閱**：`factset` 是公開供應商，**要訂閱／API key**;`capiq` 在 vertical `.mcp.json` 已定義、指向本機 mock（`mock-mcp/`，假 CSV）——想離線 demo 跑 `python3 mock-mcp/run_all_http.py`，要上線把 url 改指你的 CapIQ／S&P feed（伺服器名跟 frontmatter `tools:` 都不要改）
- 📐 **同業範圍／倍數定義**：comps 的指標定義跟同業圈選慣例 → `plugins/vertical-plugins/financial-analysis/skills/comps-analysis/SKILL.md`
- 🎨 **簡報 template**：用 `/ppt-template` 產貴公司的版型（底層是 `pptx-author`）
- ✏️ **調整範圍** → `plugins/agent-plugins/market-researcher/agents/market-researcher.md`
- 👤 **人工 review 不變**：只產草稿，分析師核准才發布

> ⚠️ skill 一律改 `vertical-plugins/` 的 source（真本），改完跑 `python3 scripts/sync-agent-skills.py` 做 sync。

## 五、導入評估

| 面向 | 評估 |
|---|---|
| **導入風險** | 🟢 低 — 產出只是內部研究草稿，不對外發布、不碰法規簽核或財務過帳;分析師 review 一下就能攔錯。真正的風險在研究品質跟出處正不正確（已經用 `[UNSOURCED]` 這個規矩控管），不是合規風險。 |
| **導入成本** | 🟡 中 — `factset` 要訂閱公開 source（買訂閱＋API key）;`capiq` 已接本機 mock，要上線把 url 改指你的 CapIQ／S&P feed;另外要客製 comps 指標定義跟品牌簡報 template;不用自己蓋內部系統，整合很輕。 |
| **適用單位** | 賣方／買方研究部、投資團隊、財富管理投資研究 |
| **單位中角色** | 研究分析師（下指令＋覆核草稿）· 投組經理（提需求＋消費研究）· 研究助理（草稿加工） |

**最有機會成功的場景**
1. **陌生產業/主題的初步掃描** — 分析師接到不熟的主題，想快速拿到一份結構化的概覽，省下一堆人工蒐集的時間，CP 值最高。
2. **既有覆蓋產業的定期更新** — 季度／年度例行刷新產業格局跟同業 comps。
3. **投資委員會前的主題背景包** — 投組經理要在會上談一個主題，臨時需要格局＋同業＋點子清單。

## 六、它補的是哪一段（與成熟系統／自建的分工）

它不是資料庫、也不是外部研究報告，而是坐在那些資源「上面」做組織、判斷、草稿的那一層。把市場研究拆幾段就清楚：

| 環節 | 誰做 |
|---|---|
| 提供結構化財務資料、同業財務歷史、行業覆蓋報告 | 🏦 成熟系統（FactSet／CapIQ）或外部研究顧問——有訂閱才有資料 |
| 把資料拼成有觀點的產業格局、競爭分析、同業 comps、點子清單 | 🤖 本 agent——判斷框架、誠實標 [UNSOURCED]、不瞎掰 |
| 審核草稿、決定投資方向 | 👤 分析師／投組經理 |

**優勢來源**
- **對成熟系統**：FactSet／CapIQ 給資料就停了，從散落的數字到有結構的產業觀點——哪些公司值得關注、競爭格局誰輸誰贏——這段需要判斷，系統本來留給人手工整合的。
- **對分析師手動桌面研究**：不用自己一頁一頁查、手動整理表格；沒有訂閱資料源也能產出結構化草稿，誠實標出查不到的地方而非臆測填空。

**什麼時候用哪個**
- 查特定公司的精確財務數字、取完整的賣方研究 → 成熟系統（FactSet／CapIQ）。
- 產業全景掃描、競爭格局分析、同業估值比較、投資點子初篩 → agent。
- 需要審計級財務資料、法規備查用途 → 成熟系統（資料有完整 audit trail）。
- ❌ 沒有分析師覆核就對外發布別用 agent（只交草稿，分析師審核才發布）。

## 七、Skill 白話

每支 skill 是一份「給 AI 看的作業手冊」。這支 agent 的產出主要是文件與簡報，skill 負責判斷框架與接線，沒有訂閱資料源時誠實標 [UNSOURCED] 而非自行估填。

- **`sector-overview` 產業概覽**：從市場規模、產業結構、競爭態勢到主要成長動力與風險，整理成一份完整的產業全景報告（5–30 頁，深度可調）；每筆市場規模數字都要標來源，避免把 TAM 行銷說法當研究結論。
- **`competitive-analysis` 競爭格局**：圈定 8–15 家代表公司後，逐一做指標比較（營收、成長率、市占、護城河等）並視覺化排出格局——誰在拉開差距、誰在失守，出成投影片或 Word 報告。
- **`comps-analysis` 同業估值倍數**：用一致的指標定義把同業攤開、建統計區間（最大、四分位、中位、最小），推估估值合理區間；以 MCP 資料為優先，無訂閱時顯示 N/A 而非估值；輸出為 Excel，每格計算都是公式、來源有 cell comment。
- **`idea-generation` 投資點子篩選**：綜合前面的格局與 comps，按量化篩選條件（估值、成長、品質、空頭等）加主題掃描，產出 5–10 個值得深入研究的候選標的，附一句話論點與下一步建議。
- **`pptx-author` 產簡報檔**：無頭模式下用 Python 把 .pptx 寫成檔，每張投影片標題即觀點、每個數字可追回模型儲存格；有開著的 PowerPoint 時改用 office 工具直接操作。
