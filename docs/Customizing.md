# 🔧 改 Agent 指南 — 想改什麼、動哪個檔、要注意什麼

> 給「**要動手改 agent**」的人看。先懂架構讀 [TechSummary.md](TechSummary.md);模型怎麼換讀 [Models.md](Models.md);單支 agent 全貌見 [agents/](agents/)。

---

## 一、想改 X → 動哪個檔(總表)

| 想改的東西 | 動這個檔 | 影響範圍 |
|---|---|---|
| 流程步驟 / 人工停點 / guardrail | `agents/<slug>.md` 的 `## Workflow`、`## Guardrails` | **plugin + CMA 同時** |
| agent 用哪些 skill / 模型 | `agents/<slug>.md` 的 Skills 行 + Workflow | **plugin + CMA 同時** |
| skill 內部怎麼做 / 業務門檻(容差・重大性・估值政策) | `vertical-plugins/<vertical>/skills/<name>/SKILL.md` 真本 → `sync` | **plugin + CMA 同時** |
| 幾個 sub-agent | `managed-agent-cookbooks/<slug>/agent.yaml` 的 `callable_agents` | 只 CMA |
| 給不給寫檔／工具(能力閘) | plugin:`tools:` 行;CMA:`agent.yaml` / `subagents/*.yaml` 的 `tools` | 視改哪邊 |
| 髒 reader 的輸出限制(schema 閘) | `subagents/<reader>.yaml` 的 `output_schema` | 只 CMA |
| 誰能交棒給誰(handoff) | `scripts/orchestrate.py` 的 `ALLOWED_TARGETS` | 只 CMA(reference) |

> 一句話記法:**「角色/流程/守則」改劇本(兩邊生效);「怎麼做一件事」改 SKILL.md(要 sync);「分工/權限/結構」改 CMA 的 yaml(只 CMA)。**

---

## 二、改之前必看的 5 個注意事項

1. **真本 vs copy** — skill 一律改 `vertical-plugins/` 的 source(真本),改完跑 `sync`;直接改 `agent-plugins/.../skills/` 的 copy(副本)→ check.py 抓到 drift 會擋你 commit。
2. **一份劇本兩邊用** — 改 `agents/<slug>.md` 會**同時**動到 plugin 和 CMA(CMA 的 agent.yaml 用 `system.file` 指回它)。別以為只改了一邊。
3. **最小權限別亂破壞** — 要加 `Write` / `bash` / MCP 給某個 sub-agent 前先想:**它會不會碰到髒資料?** 碰髒的 reader 多一個對外能力,就多一個 prompt injection 破口。後台 agent「reader 無 MCP、唯一 writer 不碰髒源」是刻意設計。
4. **業務門檻要 sign off** — 後台 agent 的容差(tolerance)、重大性(materiality)、估值政策藏在 SKILL.md;改它等於改稽核行為,要會計/法遵點頭,不是工程自己說了算。
5. **YAML 縮排、JSON 逗號** — 壞一個字整支 agent 載不起來。改完一定跑 `check.py`。

---

## 三、結構即防線:CMA 的三道安全閘

外掛(plugin)版安全靠「真人盯」;CMA 無人值守,安全只能靠**結構**。實際有三道閘,改 agent 時別把它們拆了:

```
① 能力閘 (tools)        每個 agent / sub-agent 只開它該有的工具。
                        碰髒的 reader 通常 read/grep only、mcp_servers: []、無 write。

② schema 閘 (output_schema)  髒 reader 的輸出被 JSON Schema 鎖死:
                        字元白名單(pattern)+ maxLength + maxItems + additionalProperties:false
                        ↳ 注意:CMA API 目前「不強制」schema。deploy 時會 del(.output_schema),
                          改由 harness 的 scripts/validate.py 在 reader→orchestrator 之間驗。
                          所以這道閘的執行者是 validate.py,不是 API。

③ 交棒閘 (handoff)       agent 之間不直接交棒;emit handoff_request,
                        由 scripts/orchestrate.py 的 ALLOWED_TARGETS allowlist + schema 驗證路由。
                        target 不在 allowlist 或 payload 不合規 → 直接擋掉。
```

> 改 `output_schema`(放寬字數/欄位)或 `ALLOWED_TARGETS`(開放新交棒對象)時要特別小心——這兩個直接決定「髒資料能塞多少進來」和「資料能流去哪」。

---

## 四、固定收尾(改完一定做)

```
改 skill  → python3 scripts/sync-agent-skills.py   把 copy 同步
任何改動  → python3 scripts/check.py               lint + 參照 + drift 檢查
動到 CMA  → bash scripts/deploy-managed-agent.sh <slug> --dry-run   驗結構(不上雲)
          → bash scripts/test-cookbooks.sh        全 10 支 dry-run 斷言
測行為    → /plugin install <slug>@fsi-local      本地真跑一次
```

> 少了 sync,check 會擋;直接改 copy,check 也會擋。這條紀律就是「一個來源」能成立的關鍵。

---

## 五、常見情境速查

| 我想… | 怎麼做 |
|---|---|
| 換 agent 用的模型 | 見 [Models.md](Models.md)(Layer 2:改 Skills 行 + bundle skill) |
| 加/減一個 sub-agent | 改 `agent.yaml` 的 `callable_agents`(加的話另寫一支 `subagents/<name>.yaml`) |
| 改某一步要不要停下給人審 | 改 `agents/<slug>.md` 的 `## Workflow`(那句 stop/surface) |
| 收回某 agent 的寫檔權 | plugin 刪 `tools:` 的 `Write, Edit`;CMA 改對應 yaml 的 `tools` |
| 加一支全新 agent | `plugin.json` + `agents/<slug>.md` +(技能放 vertical → sync)+ `marketplace.json` 加一筆 +(要 CMA 再加 cookbook) |

> 📎 新增 agent 的完整思考(部門/信任邊界/工具/驗證方式)可搭配 [AgentSummary.md](AgentSummary.md) 的設計原則一起看。
