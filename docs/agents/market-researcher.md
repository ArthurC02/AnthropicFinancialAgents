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
**MCP（2 個）**　`capiq` · `factset`（`capiq` 是 placeholder（佔位）— 可改接 repo 內建的 sp-global（S&P）connector;`factset` 是公開供應商）

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

**跨 agent**　研究與建模家族 ┄ 跟〔earnings-reviewer〕〔model-builder〕互補

## 四、上線前要補齊（客製化）

```
 Anthropic 參考骨架    ＋    貴公司要補的    ＝    可實際上線
```
- 🔌 **接資料訂閱**：`factset` 是公開供應商，**要訂閱／API key**;`capiq` 是 placeholder（佔位）— 可改接 repo 內建的 sp-global（S&P）connector
- 📐 **同業範圍／倍數定義**：comps 的指標定義跟同業圈選慣例 → `plugins/vertical-plugins/financial-analysis/skills/comps-analysis/SKILL.md`
- 🎨 **簡報 template**：用 `/ppt-template` 產貴公司的版型（底層是 `pptx-author`）
- ✏️ **調整範圍** → `plugins/agent-plugins/market-researcher/agents/market-researcher.md`
- 👤 **人工 review 不變**：只產草稿，分析師核准才發布

> ⚠️ skill 一律改 `vertical-plugins/` 的 source（真本），改完跑 `python3 scripts/sync-agent-skills.py` 做 sync。

## 五、導入評估

| 面向 | 評估 |
|---|---|
| **導入風險** | 🟢 低 — 產出只是內部研究草稿，不對外發布、不碰法規簽核或財務過帳;分析師 review 一下就能攔錯。真正的風險在研究品質跟出處正不正確（已經用 `[UNSOURCED]` 這個規矩控管），不是合規風險。 |
| **導入成本** | 🟡 中 — 要訂閱公開 source（CapIQ／FactSet，買訂閱＋API key）、客製 comps 指標定義跟品牌簡報 template;不用自己蓋內部系統，整合很輕。 |
| **適用單位** | 賣方／買方研究部、投資團隊、財富管理投資研究 |
| **單位中角色** | 研究分析師（下指令＋覆核草稿）· 投組經理（提需求＋消費研究）· 研究助理（草稿加工） |

**最有機會成功的場景**
1. **陌生產業/主題的初步掃描** — 分析師接到不熟的主題，想快速拿到一份結構化的概覽，省下一堆人工蒐集的時間，CP 值最高。
2. **既有覆蓋產業的定期更新** — 季度／年度例行刷新產業格局跟同業 comps。
3. **投資委員會前的主題背景包** — 投組經理要在會上談一個主題，臨時需要格局＋同業＋點子清單。
