# 🚀 快速上手：第一支 Agent（Market Researcher 市場研究）

> **這份文件做什麼**：手把手帶你把第一支 agent（🔭 市場研究）用**外掛模式**跑起來。全程**不用任何 API key、不用自建任何系統**，照著做就能看到產出。
>
> **為什麼從這支開始**：它風險最低（產出只是內部研究草稿），而且就算沒接資料源，靠 Claude 內建的網路搜尋也能跑出有結構的報告——是最「無痛」的入門。其他 agent 的選擇邏輯見 [AgentSummary.md](AgentSummary.md)。

---

## 〇、開始前你需要什麼

```
✅ 安裝好 Claude Code（CLI）
✅ 這個倉庫已經下載到本機，例如：
   <repo>
❌ 不需要：FactSet／CapIQ 訂閱、API 金鑰、任何內部系統
```

---

## 一、階段 A：零金鑰把它跑起來

整個過程四步。**第 0 步是關鍵**——不先做會卡住（我們實際踩過這個坑）。

### A0　先改一個名字（不改會失敗）

倉庫裡 `.claude-plugin/marketplace.json` 的 `name` 原本叫 `claude-for-financial-services`。

> ⛔ **這是 Anthropic 官方的保留名稱**，只允許從 GitHub 的 `anthropics` 組織來源使用。
> 你從**本機資料夾**加，名稱撞到保留字，會直接報錯：
> ```
> Error: The name 'claude-for-financial-services' is reserved for official
> Anthropic marketplaces and can only be used with GitHub sources from the
> 'anthropics' organization.
> ```

**解法**：把本機這份 `marketplace.json` 的 `name` 改成任何非保留名稱，例如 `fsi-local`：

```jsonc
{
  "name": "fsi-local",          ← 原本是 "claude-for-financial-services"
  "owner": { ... },
  "plugins": [ ... ]
}
```

> ⚠️ **這是「本機專用」的改動，不要 commit**。它只是讓你能從本地安裝；commit 上去會跟官方倉庫的保留名稱衝突。哪天不要了，改回原名就好。

### A1　把倉庫加成 marketplace

```
/plugin marketplace add <repo>
```

> 💡 **用正斜線 `/`**。Windows 的反斜線 `\` 有時候會出問題；官方範例一律用正斜線。

### A2　安裝兩個外掛

```
/plugin install financial-analysis@fsi-local
/plugin install market-researcher@fsi-local
```

| 外掛 | 角色 |
|---|---|
| `financial-analysis` | **技能與連接器來源**——市場研究會用到的 `comps-analysis`（同業比較）等 skill 放在這 |
| `market-researcher` | **主角 agent**——你要跑的就是這支 |

> ⚠️ `@` 後面要用你在 A0 改的新名字（這裡是 `fsi-local`）。

### A3　丟一個主題給它

挑一個你不熟、但網路上查得到的主題。例如：

```
研究 AI 資料中心散熱這個主題，給我產業概覽、主要玩家競爭格局、
同業比較和值得關注的標的清單
```

### A4　看它跑

正常情況下，它會照**五步流程**走，產出一份研究報告草稿：

```
①界定範圍(8–15家) → ②產業概覽 → ③競爭格局 → ④同業比較
→ ⑤值得關注的標的清單 →（必要時做成簡報）
```

---

## 二、怎麼判斷「它跑得對不對」（驗收檢查表）

跑完之後，拿它的輸出對照這張表逐項打勾：

```
☐ 有沒有照五步流程走？（範圍 → 概覽 → 格局 → 比較 → 點子）
☐ 第①步有沒有圈出 8–15 家代表公司？
☐ 第④步「同業比較」的數字——沒接金鑰時，應該掛 [UNSOURCED]
   或老實說「查不到」，而不是憑空編一個漂亮數字
☐ 產業規模有沒有附來源？（它應該引用，不該瞎掰）
☐ 最後是不是只給「草稿」，沒有自己對外發布？
☐ 整份是不是內部用、需要分析師核准才發布？
```

> ✅ **全部對得起來 → 這支 agent 行為正常，你成功跑通第一支了。**
> ❌ **第④步如果它編了具體數字卻沒來源 → 這是它在唬爛，要警覺。**

### 沒金鑰時，輸出長什麼樣（重點看第④步）

```
④ 同業比較(comps)　← 這就是「沒金鑰」的破口
  公司            市值        EV/EBITDA     營收成長
  Vertiv (VRT)    [UNSOURCED]  [UNSOURCED]   [UNSOURCED]
  nVent (NVT)     [UNSOURCED]  [UNSOURCED]   [UNSOURCED]
```
> 🔴 web-only 模式拿不到精準財報倍數，所以整欄掛 `[UNSOURCED]`——這是**正常且正確**的行為（它遵守「查不到就標、不瞎掰」的規矩）。
> 這一欄，就是你之後接金鑰要補實的唯一缺口。

---

## 三、常見錯誤與解法

| 症狀 | 原因 | 解法 |
|---|---|---|
| `name ... is reserved` | marketplace 名稱撞到官方保留字 | 見 **A0**，把 `name` 改成 `fsi-local` 之類 |
| `marketplace add` 一直失敗 | Windows 反斜線路徑 | 改用正斜線：`c:/Users/.../financial-services` |
| 路徑還是不行 | 指令對路徑格式很挑 | 改用互動式：直接打 `/plugin` → 進 **Marketplaces** 分頁用介面加，比較寬容 |
| `install ...@claude-for-financial-services` 找不到 | `@` 後面用了舊名字 | 改用 A0 設的新名字（`@fsi-local`） |
| agent 沒有自動回應我的提問 | 裝好的 agent 不會自動接管對話 | 在乾淨 session 裡讓它被指派，或明確點名要用 market-researcher |

---

## 四、階段 B：升級精準度（之後選做）

階段 A 跑順、建立信任後，再來把第④步那欄 `[UNSOURCED]` 換成官方數字。

```
┌─ 升級步驟 ────────────────────────────────────────────────┐
│ ①（JSON bug 已修復，可略過）之前 egnyte/box 缺逗號跟收尾大括號，  │
│    plugins/vertical-plugins/financial-analysis/.mcp.json 現已修好     │
│                                                            │
│ ② factset 已定義好 → 去 FactSet 申請 API 金鑰填進去        │
│ ③ capiq 是 placeholder（佔位）→ 改接倉庫內建的 sp-global（S&P）連接器 │
│ ④ 客製同業比較的指標定義／同業圈選慣例                    │
│    → financial-analysis/skills/comps-analysis/SKILL.md     │
│ ⑤ 要簡報就用 /ppt-template 產你公司的版型                 │
└────────────────────────────────────────────────────────────┘
```

> 📌 接上金鑰後：第④步的市值、EV/EBITDA、成長率、毛利率，會從「網路估算」變成「官方資料」，`[UNSOURCED]` 就消失了。

---

## 五、之後可以往哪走

跑通市場研究後，照 [AgentSummary.md](AgentSummary.md) 的三批導入順序往下：

```
第一批（都跟這支一樣不必碰內部系統）
  🔭 市場研究 ← 你在這
  🧮 估值建模（model-builder）
  📊 財報追蹤（earnings-reviewer）

第二批　🎯 投行提案（pitch-agent）— 要重度客製簡報範本

第三批　中後台五支（後台四支＋中台開戶審查）— 要接內部系統，門檻最高，最後再上
```

---

> 📎 單一助理的完整內容（工作流程／風險把關／技術架構／導入評估）見 [Docs/agents/market-researcher.md](agents/market-researcher.md)。
> 整體技術架構（一個來源兩個輸出、外掛 vs CMA、MCP 對照）見 [TechSummary.md](TechSummary.md)。
