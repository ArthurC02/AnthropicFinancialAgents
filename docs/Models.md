# 🧮 模型清單與替換指南 — repo 裡有哪些模型、能怎麼換

> 這頁回答三件事:**①** repo 裡到底有哪些「模型」skill?**②** 哪支 agent 在用?**③** 我想改／換模型,要動哪裡?
>
> 單支 agent 的完整內容見 [agents/](agents/);整體架構見 [TechSummary.md](TechSummary.md);改 agent 的通用 SOP 見 [Customizing.md](Customizing.md)。

---

## 一、全 repo 模型清單

這裡的「模型」指**會產出財務試算/估值結果**的 skill(不含純排版、純檢查那種)。

| 模型 skill | 住哪 vertical | 算什麼 | 目前哪支 agent 在用 | 狀態 |
|---|---|---|---|---|
| `dcf-model` | financial-analysis | DCF 現金流折現估值 | model-builder · pitch-agent | ✅ 已掛 |
| `lbo-model` | financial-analysis | LBO 槓桿收購報酬 | model-builder · pitch-agent | ✅ 已掛 |
| `3-statement-model` | financial-analysis | 三表整合(P&L／BS／CF) | model-builder · pitch-agent | ✅ 已掛 |
| `comps-analysis` | financial-analysis | 可比公司倍數(comps) | model-builder · market-researcher · pitch-agent | ✅ 已掛 |
| `model-update` | equity-research | 更新既有模型(財報後 plug 新數字) | earnings-reviewer | ✅ 已掛 |
| `returns-analysis` | private-equity | IRR／MOIC 報酬 | valuation-reviewer | ✅ 已掛 |
| `portfolio-monitoring` | private-equity | 投組監控:變異對預算/槓桿覆蓋率/KPI | valuation-reviewer | ⚠️ plugin 掛、CMA 未掛 |
| `merger-model` | investment-banking | 併購 accretion／dilution(增稀釋) | **沒有 agent 預設掛** | ⚠️ 未掛 |
| `unit-economics` | private-equity | 單位經濟分析(SaaS／訂閱型) | **沒有 agent 預設掛** | ⚠️ 未掛 |

> ⚠️ **兩支「現成但沒被任何 agent 掛」的**:`merger-model`(併購模型)、`unit-economics`(單位經濟)。它們的 source 已經在 repo 裡,要用就照[第三段](#三實作把一個新模型掛進-agent)掛進去,不用從零寫。
>
> 📌 **plugin 掛了、CMA 沒掛的兩個眉角**（雲端版要補才會跑）：
> - **pitch-agent**:`comps-analysis`／`3-statement-model` 寫在 plugin 劇本(兩個 surface 共用的 canonical prompt),plugin 版會用;但 CMA 的 `subagents/modeler.yaml` 只掛 `dcf-model`／`lbo-model`。要雲端版也跑這兩支,得補進 `modeler.yaml`。
> - **valuation-reviewer**:`portfolio-monitoring` 寫在 plugin 劇本,plugin 版會用;但 CMA 的 `subagents/valuation-runner.yaml` 只掛 `returns-analysis`。要雲端版也跑,得補進 `valuation-runner.yaml`。

---

## 二、模型能改嗎?能,分三層(別搞混)

```
Layer 1  改「怎麼算」      → SKILL.md 真本                     ← 改 WACC 組成、藍/黑/綠色碼、
         (邏輯/慣例)         vertical-plugins/.../<model>/SKILL.md   計算慣例、循環參照規則 → 跑 sync
            │
Layer 2  改「agent 會建哪幾種」→ agents/<slug>.md 的 Skills 行 + Workflow ← 例:讓 model-builder
         (掛哪些模型)                                                  也會建 merger-model
            │
Layer 3  改「數字/假設」    → 執行時的 input,不是改 source       ← WACC 用幾 %、成長率多少、
         (跑的時候給)                                              退場倍數 → 在 prompt 給它
```

| 你想改 | 動哪裡 | 影響範圍 | 例子 |
|---|---|---|---|
| 模型內部邏輯/慣例 | `vertical-plugins/.../<model>/SKILL.md` 真本 → `sync` | plugin + CMA 同時 | DCF 的 WACC 組成、色碼規則 |
| agent 會建哪幾種模型 | `agents/<slug>.md` 的 Skills 行 + Workflow | plugin + CMA 同時 | model-builder 加掛 merger-model |
| 單次的數字/假設 | 執行時的 prompt(不改檔) | 只這一次 | 「WACC 用 9%、永續成長 2.5%」 |

> 💡 大多數人想要的其實是 **Layer 3**(換假設)——那個直接在 prompt 講就好,不用碰原始碼。要改「模型長相/慣例」才是 Layer 1,要「換一種模型」才是 Layer 2。

---

## 三、實作:把一個新模型掛進 agent

以**「讓 `model-builder` 也會建併購模型(merger-model)」**為例,走一遍 Layer 2。

```
1. 確認 source 在哪      merger-model 的真本在 investment-banking vertical(已存在,不用自己寫)

2. 先 bundle 進 agent     ⚠️ 關鍵眉角:sync-agent-skills.py 只會「更新已存在」的 bundle 夾,
                          不會自己新增 skill。所以第一次要手動把 source 複製進:
                          plugins/agent-plugins/model-builder/skills/merger-model/
                          (之後 sync 會自動維護這份 copy)

3. 在劇本掛上去          agents/model-builder.md → Skills 行加 `merger-model`,Workflow 補一步
                          ↳ check.py 4b2 會強制:劇本裡用 backtick 提到的 skill,
                            一定要 bundle 在該 agent 的 skills/ 夾 — 第 2 步就是為了滿足這條

4. (CMA 才要)掛給工人    在會用到它的 subagent yaml(model-builder 的 builder.yaml)加一行:
                          - { path: ../../../plugins/agent-plugins/model-builder/skills/merger-model }

5. 收尾驗證              python3 scripts/sync-agent-skills.py → python3 scripts/check.py
                          → 本地 /plugin install model-builder@fsi-local 測一次
```

> ⚠️ **drift 檢查**:check.py 會比對 bundle 與 vertical source **是否一致**(檔案有出入就擋下 commit)。所以 bundle 進去後**別手改那份 copy**,要改一律去 investment-banking 真本再 `sync`。

---

## 四、哪支 agent 適合掛哪些模型(建議)

| Agent | 現在有的模型 | 可考慮加掛 | 什麼情況加 |
|---|---|---|---|
| 🧮 model-builder | dcf · lbo · 3-statement · comps | `merger-model` · `unit-economics` | 要建併購案模型、或標的是 SaaS/訂閱型 |
| 🎯 pitch-agent | dcf · lbo · 3-statement · comps | `merger-model` | 提案本身就是併購案,要算 accretion/dilution |
| 💰 valuation-reviewer | returns-analysis · portfolio-monitoring | `unit-economics` | 想連被投組合的單位經濟一起複核 |
| 📊 earnings-reviewer | model-update(只更新、不建新) | —(本來就不建模型) | — |

> 📎 改 agent 的通用注意事項(真本 vs copy、一份劇本兩邊用、最小權限…)見 [Customizing.md](Customizing.md);各模型內部慣例見對應的 `vertical-plugins/.../skills/<model>/SKILL.md`。
