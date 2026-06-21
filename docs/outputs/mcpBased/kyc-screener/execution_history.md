# 🔍 開戶審查（kyc-screener）— 執行紀錄（MCP 版）

> 這份是 **mcpBased** 版本:篩查名單不再從 `samples/*.md` 餵,而是**真的去打 `screening` MCP server** 即時拉。
> 申請人名單(誰要被篩)是**任務輸入**——沿用 fileBased 的 `onboarding_applications_2026-06.md` 那 5 筆。
> 全部是 **mock / dev 假資料**,別當真。編製 2026-06-21。

---

## 1. 安裝外掛

```text
❯ /plugin install kyc-screener@fsi-local
  ⎿  ✓ Installed kyc-screener. Run /reload-plugins to apply.
```

## 2. 使用者請求

> 使用者:這是 5 筆開戶申請(沿用 onboarding_applications_2026-06.md)、KYC/AML 規則表(R1–R7)、以及 `screening` 篩查 MCP。請逐一對每位相關人打 MCP 比對制裁/PEP 名單,標出確認命中/假命中/PEP,套規則產出給合規的審查包。

這支的招牌考點:**抓到真制裁命中、但不亂殺同名異人的假命中、PEP 走 EDD 不自動拒**。
MCP 版的差別:名單比對改成「逐筆相關人 → `screen_name(name, dob, country)`」由 server 做識別碼比對,我只判讀它回的 classification + 套規則。

## 3. 任務輸入(申請人名單,非來自 MCP)

`screening` MCP 只存 **watchlist**,不存申請人。申請人是任務輸入,5 筆如下(名字 / DOB / 國別取自 `onboarding_applications_2026-06.md`):

| 申請 | 相關人(被篩對象) | DOB | 國別 |
|---|---|---|---|
| A Helios Capital(法人) | John Sterling(UBO 45%)、Amy Cole(董事) | — | Cayman Islands |
| B Ivan Petrov(個人) | Ivan Petrov | 1970-03-15 | Russia |
| C Maria Garcia(個人) | Maria Garcia | 1988-11-02 | Spain |
| D Aurora Holdings(法人) | Adewale Okonkwo(UBO 60%) | —(申請文件未列 DOB) | Nigeria |
| E Quiet Brook(法人) | Robert Quiet(UBO 60%)、Sarah Brook(UBO 40%) | — | USA |

> 註:D 的 UBO DOB 申請文件沒給,如實留空打 MCP——這也順帶測「identifiers 不全時 server 怎麼分類 PEP」。

## 4. 打 MCP(批次模式,真的有跑)

寫了 `scripts/pull.json`(`out_dir` 用絕對 Windows 路徑),跑 harness:

```bash
cd ".../docs/outputs/mcpBased/_harness" && PYTHONUTF8=1 \
  python mcp_client.py --spec ".../kyc-screener/scripts/pull.json" 2>/dev/null
```

server:`mock-mcp/screening/server.py`(stdio)。一共 **11 個 MCP 工具呼叫**,全部 `ok=true`:

| # | tool | args | 回傳重點 | 存檔 |
|---|---|---|---|---|
| 1 | `get_sanctions_list` | `{}` | 制裁名單(S-1…) | `01_get_sanctions_list.json` |
| 2 | `get_pep_list` | `{}` | PEP 名單(P-1…) | `02_get_pep_list.json` |
| 3 | `screen_name` | `John Sterling / — / Cayman Islands` | **CLEAR**(0 命中) | `03_screen_A_john_sterling.json` |
| 4 | `screen_name` | `Amy Cole / — / Cayman Islands` | **CLEAR**(0 命中) | `03_screen_A_amy_cole.json` |
| 5 | `screen_name` | `Ivan Petrov / 1970-03-15 / Russia` | **HIT_SANCTIONS** → `confirmed_sanctions_match`(S-1) | `03_screen_B_ivan_petrov.json` |
| 6 | `screen_name` | `Maria Garcia / 1988-11-02 / Spain` | **REVIEW** → `likely_false_positive`(S-2) | `03_screen_C_maria_garcia.json` |
| 7 | `screen_name` | `Adewale Okonkwo / — / Nigeria` | **HIT_PEP** → `pep_match`(P-1) | `03_screen_D_adewale_okonkwo.json` |
| 8 | `screen_name` | `Robert Quiet / — / USA` | **CLEAR**(0 命中) | `03_screen_E_robert_quiet.json` |
| 9 | `screen_name` | `Sarah Brook / — / USA` | **CLEAR**(0 命中) | `03_screen_E_sarah_brook.json` |

外加 harness 自動寫的 `_tools.json`(列出 server 三個工具)。原始 JSON 全部留在 `mcp_pulls/`。

### 4.1 server 回的關鍵欄位(逐筆,直接引用 JSON)

- **B Ivan Petrov**(`03_screen_B_ivan_petrov.json`):
  `overall=HIT_SANCTIONS`、`match_count=1`、`classification=confirmed_sanctions_match`、
  `reason="name + DOB + country all match"`、`action="R4: reject / escalate to MLRO"`、命中 `S-1 / OFAC SDN (EO 13662)`。
  → 姓名＋DOB＋國別三項全中,**真命中**。

- **C Maria Garcia**(`03_screen_C_maria_garcia.json`):
  `overall=REVIEW`、`match_count=1`、`classification=likely_false_positive`、
  `reason="name matches but identifiers differ: DOB 1988-11-02 vs 1955-07-22; country Spain vs Colombia"`、
  `action="clear after review; do NOT auto-reject"`、撞名 `S-2 / OFAC SDN (SDNTK)`。
  → 只有姓名撞,DOB 與國別都不符,**假命中**,server 明白要求「不得自動拒絕」。

- **D Adewale Okonkwo**(`03_screen_D_adewale_okonkwo.json`):
  `overall=HIT_PEP`、`match_count=1`、`classification=pep_match`、
  `position="Deputy Minister of Energy 能源部副部長"`、`type="current PEP"`、
  `action="R5: enhanced due diligence (EDD); not an auto-reject"`、命中 `P-1`。
  → PEP,走 EDD,**非自動拒絕**。即使 DOB 留空,PEP 比對只看姓名+名單,照樣命中。

- **A John Sterling / Amy Cole、E Robert Quiet / Sarah Brook**:四筆全 `overall=CLEAR`、`match_count=0`。乾淨。

## 5. agent 怎麼判讀(從 PULLED data,不是憑空)

照 server 回的 classification 直接對應規則表處置,**守 guardrail**:

| server classification | overall | 對應規則處置 |
|---|---|---|
| `confirmed_sanctions_match` | HIT_SANCTIONS | R4 → 拒絕＋上報 MLRO(SAR) |
| `likely_false_positive` | REVIEW | R4 假命中 → **釐清後排除,不得自動拒絕** |
| `pep_match` | HIT_PEP | R5 → EDD＋高階核准,**非自動拒絕** |
| (無命中) | CLEAR | 無 R4/R5 觸發,續看其他規則 |

接著把 MCP 比對結果跟申請文件本身的缺漏(R1 證件、R2 UBO、R3 SoF、R6 高風險國、R7 活動輪廓)合起來評等。文件層面的缺漏(如 A 的 30% UBO 未識別、董事護照過期;D 的 SoF 未提供、PEP 自我聲明不實;D 註冊地奈及利亞屬高風險)沿用 fileBased 的解析結果——這些不在 screening MCP 範圍內,是規則引擎依申請文件判的。

## 6. 寫出產物

```text
● Write(out/kyc_review_pack_2026-06.md)          ← 主審查包(逐申請處置＋理由)
● Write(scripts/build_kyc_pack.py)               ← openpyxl 產 xlsx 底稿
● python scripts/build_kyc_pack.py               ← 產 KYC_Review_Workpaper_2026-06.xlsx
```

```text
SAVED out/KYC_Review_Workpaper_2026-06.xlsx  sheets: ['Rules Matrix', 'Dashboard', 'Sanctions-PEP Screening', 'Routing']
```

## 7. 本回合結果(5 申請)

> 1 拒絕上報 · 2 EDD 待補 · 2 標準可核准。所有判定都對齊 MCP 回的 classification。

| 申請 | 客戶 | 等級 | 處置 | MCP 依據 |
|---|---|---|---|---|
| B | Ivan Petrov | 🔴 | 拒絕＋SAR、升級 MLRO | `confirmed_sanctions_match` S-1(姓名＋DOB＋國別全中) |
| D | Aurora (Nigeria) | 🟡 高 | 升級 MLRO,EDD,補件前不可開戶 | `pep_match` P-1 ＋ 文件層:R6 高風險國＋R3 缺 SoF＋PEP 聲明不實 |
| A | Helios Capital | 🟡 | 補件前不可開戶 | MCP 全 CLEAR;文件層:R2 30% UBO 未識別＋R1 董事護照過期 |
| C | Maria Garcia | 🟢 | 記錄假命中排除依據後可核准 | `likely_false_positive` S-2(DOB 1988≠1955、Spain≠Colombia)→ 排除,不拒絕 |
| E | Quiet Brook | 🟢 | 可核准 | MCP 全 CLEAR、文件齊全 |

維持「只評分與路由、不作最終決定」,最終由合規／MLRO 簽核。本代理不寫核准、不自動拒絕假命中與 PEP。

## 8. 失敗的呼叫 / 已知限制(誠實交代)

- **失敗呼叫:無。** 11 個 MCP call 全 `ok=true`。
- **harness 序列化限制**:`get_sanctions_list` / `get_pep_list` 回的是 **list**,但 harness 的 `_extract` 只取 `content[0]`,所以 `01_*.json` / `02_*.json` 快照只看得到第一筆(S-1 / P-1)。完整名單(S-1/S-2/S-3、P-1/P-2)在 server 端 CSV 是齊的。**這不影響篩查結論**——真正的比對證據是 9 筆 `screen_name`(回單一 dict,完整無損),已逐筆驗證命中/假命中/PEP/CLEAR 全部正確。
