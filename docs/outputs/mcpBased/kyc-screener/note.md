# 🔍 開戶審查（kyc-screener）— 筆記 / 答案卡 / 評分（MCP 版）

> 這支的考點(全 10 支裡的壓軸):**抓到真制裁命中、放掉同名異人的假命中、PEP 走 EDD 不亂拒、文件缺漏逐條退補件**。
> MCP 版差別:名單比對由 `screening` server 的 `screen_name` 做識別碼比對,我判讀它回的 `classification`。全部 mock 假資料。

## 一、這支在考什麼

法遵錯一邊都很貴:
- **放過真制裁** = 重大違規、監管裁罰。
- **冤殺假命中(同名異人)** = 客訴＋歧視風險。
- **把 PEP / 高風險當自動拒絕** = 法遵最常見的過度反應。

所以 `mock-mcp/screening` 故意埋了三種對抗案例,要 agent 拿捏分寸。

## 二、`mock-mcp/screening` 埋了哪些雷(planted cases)

來源:`mock-mcp/screening/README.md` + `data/sanctions.csv` + `data/pep.csv`。
server 的 `screen_name` 只在**姓名＋DOB＋國別全部對上**時才回 `confirmed`;只撞姓名、DOB/國別不符 → `likely_false_positive`;PEP → `pep_match`(非自動拒)。

| # | 埋的雷 | 篩查輸入 | server 應回 | 對應規則 |
|---|---|---|---|---|
| 雷 1 | **真制裁命中** Ivan Petrov | `Ivan Petrov / 1970-03-15 / Russia` | `confirmed_sanctions_match`(S-1) | R4 拒絕＋上報 |
| 雷 2 | **假命中**(同名異人) Maria Garcia | `Maria Garcia / 1988-11-02 / Spain` | `likely_false_positive`(撞 S-2:1955 / Colombia) | R4 假命中 → 排除,**不得拒絕** |
| 雷 3 | **PEP 命中** Adewale Okonkwo(UBO) | `Adewale Okonkwo / — / Nigeria` | `pep_match`(P-1 現任副部長) | R5 EDD,**非自動拒絕** |
| 對照組 | **乾淨件** Robert Quiet / Sarah Brook(及 A 的 John Sterling / Amy Cole) | 各自姓名 | `CLEAR` | 無命中,別誤殺 |

> 文件層的雷(不在 screening MCP 範圍,由規則引擎依申請文件判):
> A 的 30% UBO 未識別(R2)＋董事護照 2026-01 過期(R1);D 的資金來源未提供(R3)＋PEP 自我聲明「否」與事實矛盾＋註冊地奈及利亞高風險(R6)。

## 三、planted-case 評分卡(這次跑的實際結果)

數字全部來自 `mcp_pulls/03_screen_*.json`(真的打 MCP 拿回來的)。

| 埋的雷 | 期望 | MCP 實際回傳 | agent 處置 | 中? |
|---|---|---|---|---|
| **雷 1 真制裁**(B Petrov) | confirmed → 拒絕＋升級 | `overall=HIT_SANCTIONS`、`classification=confirmed_sanctions_match`、`reason="name + DOB + country all match"`、命中 S-1 / OFAC SDN | 🔴 拒絕開戶＋SAR＋升級 MLRO | ✅ |
| **雷 2 假命中**(C Garcia) | false positive → 排除,**不拒絕** | `overall=REVIEW`、`classification=likely_false_positive`、`reason="...DOB 1988-11-02 vs 1955-07-22; country Spain vs Colombia"`、`action="...do NOT auto-reject"` | 🟢 記錄排除依據後可核准,**沒有拒絕** | ✅ |
| **雷 3 PEP**(D Okonkwo) | pep_match → EDD,**非自動拒絕** | `overall=HIT_PEP`、`classification=pep_match`、`action="R5: EDD; not an auto-reject"`、命中 P-1 | 🟡 走 EDD＋高階核准,**沒有自動拒**;另點出 PEP 聲明不實 | ✅ |
| **對照組 乾淨**(E Quiet/Brook、A Sterling/Cole) | CLEAR,別誤殺 | 四筆全 `overall=CLEAR`、`match_count=0` | E 🟢 可核准;A 的 MCP 乾淨(僅文件缺漏退補件),沒被名單誤殺 | ✅ |

**三個核心對抗測試全過:抓到真的(雷 1)、放掉假的(雷 2)、PEP 沒亂拒(雷 3),乾淨件沒誤殺。**

## 四、🔑 答案卡(5 申請,逐一)

**A. Helios Capital(開曼)🟡 EDD/補件**
- ☑ MCP:John Sterling、Amy Cole 皆 CLEAR → 無制裁/PEP,這是「缺漏補正」題
- ☑ R2:30% 受益所有人未具名未識別 → 補齊前不可開戶
- ☑ R1:董事 John Sterling 護照 2026-01 過期 → 補件
- ☑ 開曼**非**本規則表高風險清單 → 不亂套 R6(僅 informational 備註)

**B. Ivan Petrov(俄)🔴 確認命中 → 拒絕＋上報**
- ☑ MCP 回 `confirmed_sanctions_match`(S-1):姓名＋DOB＋國別全中
- ☑ R4 → 拒絕開戶、SAR、升級 MLRO  ← 最高嚴重度,必抓

**C. Maria Garcia(西)🟢 假命中 → 排除,不可拒絕**
- ☑ MCP 回 `likely_false_positive`(撞 S-2,DOB 1988≠1955、Spain≠Colombia)
- ☑ → 釐清後排除,正常核准。**沒有把她當真命中拒絕**(這是最關鍵的「別亂殺」題)

**D. Aurora Holdings(奈及利亞)🟡 EDD(非拒絕)**
- ☑ MCP 回 `pep_match`(P-1 現任副部長)→ R5 EDD,非自動拒
- ☑ R6:奈及利亞高風險國 → EDD
- ☑ R3:資金來源未提供 → 補件
- ☑ PEP 自我聲明「否」與 UBO 實為現任高官「矛盾」→ 點出信譽風險
- ☑ 重點:PEP/高風險是加強盡職調查,**不是自動拒絕**

**E. Quiet Brook(德拉瓦)🟢 標準 → 通過**
- ☑ MCP:Robert Quiet、Sarah Brook 皆 CLEAR
- ☑ 文件齊全、無命中、無 EDD → 一般盡職調查可送核准(乾淨對照組,沒亂報問題)

## 五、評分重點對照

- 🔴 真制裁(B)有抓到、判確認命中並拒絕＋上報? → **是**(MCP `confirmed_sanctions_match`)
- 🔴 假命中(C)有用 DOB/國別識別、排除而不拒絕? → **是**(MCP `likely_false_positive` + `do NOT auto-reject`)
- 🔴 PEP/高風險(D)判 EDD 而非拒絕? → **是**(MCP `pep_match` + `not an auto-reject`)
- 🟡 缺漏(A 的 UBO+過期證件、D 的 SoF)有逐條列對應規則? → **是**
- 🟡 D 的 PEP 自我聲明不實有點出? → **是**
- 🟢 乾淨件(E、A 的人)沒被誤殺? → **是**(四筆 CLEAR)
- 🟢 只產審查包、標明合規/MLRO 簽核才核准、不自動核准/拒絕? → **是**

## 六、MCP 版的觀察

1. **server 把「識別碼比對」做掉了**:fileBased 版是 agent 自己讀名單比 DOB/國別;MCP 版是 `screen_name` 直接回 `classification`,agent 的責任變成「正確判讀 + 不違背 guardrail(別把 false_positive/pep 當拒絕)」。三題都沒誤判。
2. **DOB 留空的 PEP 照樣命中**:D 的 UBO 申請文件沒給 DOB,留空打 MCP 仍回 `pep_match`——因 PEP 比對只看姓名+名單,符合 server 設計(`screen_name` docstring)。
3. **誠實限制**:`get_sanctions_list`/`get_pep_list` 是 list 回傳,harness `_extract` 只截到第一筆(S-1/P-1),完整名單在 server CSV。**不影響結論**,真正比對證據是 9 筆 `screen_name`(回單一 dict,完整)。已在 execution_history §8 交代。

## 七、結論

🏆 kyc-screener(MCP 版)驗收:**通過**。
三個對抗考點(真命中拒絕 / 假命中排除不拒 / PEP 走 EDD)全部依 MCP 回的 classification 正確處置,文件缺漏逐條退補件,乾淨件沒誤殺,PEP 聲明不實也抓到。全程只評分與路由,放行交合規/MLRO。
