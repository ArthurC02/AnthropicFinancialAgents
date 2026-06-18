# 💰 估值複核（valuation-reviewer）— 筆記

## 緣起

💰 估值複核（valuation-reviewer）——一樣只接 1 個唯讀來源、一樣可餵檔案試水溫，但多了「收益分配（waterfall/carry）」的計算，難度再上一階。

要我幫你產 valuation-reviewer 的樣本檔（GP 估值包 ＋ 投組部位 ＋ waterfall 條款），照同樣的「埋幾個點考它」方式做嗎？

## 產出樣本檔

好，我來產 valuation-reviewer 的樣本檔。這支多了「估值政策複核」和「收益分配 waterfall」兩層，所以我做兩份：一份是 GP 估值包（被複核對象，埋了違反政策的估值），一份是 基金條款與部位（NAV 組成＋waterfall 條款＋估值政策）。

### gp_valuation_package_2026-Q1.md

```text
Write c:\Users\a8022\Desktop\financial-services\samples\valuation-reviewer\gp_valuation_package_2026-Q1.md
32 lines
```

# GP 估值包 GP Valuation Package — Aurora Growth Fund III, L.P.

> **這是什麼**：基金管理團隊（GP）提交的各被投資公司季末估值，是 valuation-reviewer 要**複核的對象**。
> ⚠️ 在流程裡，這份被當成**不可信外來資料**——GP 報的估值（marks）要**對照估值政策**檢查，不照單全收。
> 本檔為**假資料**，且**刻意放了幾筆違反政策的估值**供測試。

- **基金 / Fund**：Aurora Growth Fund III, L.P.
- **估值日 / As-of**：2026-03-31（Q1 季末）
- **幣別 / Currency**：USD

#### 各被投資公司估值（GP 報的數字）

| #   | 被投資公司 Portfolio Co. |   投資成本 Cost | 上季 FV (2025-12) | 本季報告 FV (2026-03) | QoQ 變動 | 估值方法 Method                   | 最後更新    | 佐證 Support                          |
| --- | ------------------------ | --------------: | ----------------: | --------------------: | -------: | --------------------------------- | ----------- | ------------------------------------- |
| 1   | Helios Software          |      60,000,000 |        90,000,000 |           120,000,000 |     +33% | 可比公司倍數（public comps）      | 2026-03     | 附倍數表；2025-09 新一輪隱含估值支持  |
| 2   | Orion Logistics          |      50,000,000 |        55,000,000 |            55,000,000 |       0% | 近期交易（2025-06 募資輪）        | 2026-03     | 沿用最近一輪價格                      |
| 3   | Nova Biotech             |      40,000,000 |        40,000,000 |            65,000,000 | **+62%** | 管理層估計（management estimate） | 2026-03     | **無新一輪、無觸發事件、無方法佐證**  |
| 4   | Titan Manufacturing      |      70,000,000 |        60,000,000 |            60,000,000 |       0% | 現金流折現（DCF）                 | 2026-03     | 已減損至成本以下，附 DCF              |
| 5   | Zephyr Retail            |      30,000,000 |        30,000,000 |            30,000,000 |       0% | 成本法（cost）                    | **2025-03** | **連續 4 季未更新（自上次後無複核）** |
|     | **合計 Total**           | **250,000,000** |   **275,000,000** |       **330,000,000** |          |                                   |             |                                       |

#### GP 附註（GP 的說法，僅供參考，需自行查核）

- **Helios**：本季依公開同業倍數上調，倍數表與 2025-09 新一輪隱含估值一致。
- **Nova Biotech**：「我們內部認為臨床進展使估值上升至 65M。」（**未提供新一輪或第三方佐證**）
- **Zephyr Retail**：「業務穩定，沿用成本即可。」（**自 2025-03 起未再做公允價值複核**）
- **Titan**：終端需求轉弱，DCF 下修，續抱於成本以下（減損已反映）。

### fund_terms_and_positions_2026-Q1.md

```text
Write c:\Users\a8022\Desktop\financial-services\samples\valuation-reviewer\fund_terms_and_positions_2026-Q1.md
54 lines
```

# 基金條款與部位 Fund Terms & Positions — Aurora Growth Fund III, L.P.

> **這是什麼**：基金層級資料——NAV 組成、出資/分配歷史、**收益分配（waterfall）條款**、**估值政策**。
> valuation-reviewer 用這份算 NAV、報酬（IRR/MOIC）、carry 與各 LP 分配，並據估值政策複核 GP 估值包。本檔為**假資料**。

- **基金 / Fund**：Aurora Growth Fund III, L.P.
- **估值日 / As-of**：2026-03-31（Q1 季末）
- **幣別 / Currency**：USD

#### A. 基金層 NAV 組成（採 GP 報告 FV）

| 項目                                       |        金額 USD |
| ------------------------------------------ | --------------: |
| 投資組合公允價值（GP 報告）Portfolio at FV |     330,000,000 |
| 現金 Cash                                  |      20,000,000 |
| 其他資產 Other Assets                      |       5,000,000 |
| 應付費用 Accrued Liabilities               |     (5,000,000) |
| **基金淨值 NAV（as-reported）**            | **350,000,000** |

#### B. 出資與分配歷史（Capital Flows，供 IRR/MOIC）

| 日期       | 事件                    |      金額 USD |
| ---------- | ----------------------- | ------------: |
| 2022-06-30 | 出資 Contribution       | (100,000,000) |
| 2023-06-30 | 出資 Contribution       | (100,000,000) |
| 2024-06-30 | 出資 Contribution       | (100,000,000) |
| 2025-06-30 | 分配 Distribution       |    40,000,000 |
| 2026-03-31 | 期末 NAV（as-reported） |   350,000,000 |

- **承諾資本 Committed**：500,000,000　|　**累計出資 Contributed**：300,000,000（其中投資成本 250,000,000、費用 50,000,000）
- **累計分配 Distributions to date**：40,000,000

#### C. 收益分配條款（Waterfall Terms）

- **型態**：歐式（European / whole-fund，全基金結算）
- **優先報酬 Preferred Return（hurdle）**：8%／年，複利
- **GP 追補 Catch-up**：100%（追到 GP 取得超額報酬的 20% 為止）
- **附帶權益 Carry**：20%
- **分配順序**：① 返還 LP 出資 → ② 補 LP 優先報酬 → ③ GP 追補 → ④ 其餘 80/20（LP/GP）
- **已提供：優先報酬累計（8% 複利，至 2026-03）= 35,000,000**（供 waterfall 計算，免自行從頭推時間加權）

#### D. 估值政策（Valuation Policy，複核 GP 估值包的依據）

| 編號   | 政策                                                                                                                                   |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| **P1** | 每一部位**每季都要做公允價值複核**；同一估值連續 **>2 季未更新（stale）**，須重新複核，不得續抱舊值。                                  |
| **P2** | 任何**上調（mark-up）**須有**可佐證的方法**（可比公司／DCF／近期交易）**或觸發事件**（新一輪、重大事件）。**單憑「管理層估計」不足**。 |
| **P3** | 估值**高於最近一輪募資價格**者，須經**估值委員會／董事會核准**。                                                                       |
| **P4** | 複核後若 GP 報告值不符政策，**以政策調整後值計算 NAV 與分配**，差異列入給 IR/CCO 的複核意見。                                          |

> ⚠️ 人工覆核不變：valuation-reviewer **只備 LP 報告草稿**，須 **IR（投資人關係）＋ CCO（法遵長）簽核**才分送，agent 不對外發送。

兩份樣本檔已產好，放在 samples/valuation-reviewer/：

```text
samples/valuation-reviewer/
  ├─ gp_valuation_package_2026-Q1.md      ← GP 報的估值（埋了違反政策的 marks）
  └─ fund_terms_and_positions_2026-Q1.md  ← NAV組成＋waterfall條款＋估值政策
```

## 怎麼用

> 使用者：這是 Aurora Growth Fund III 的 GP 估值包 (gp_valuation_package_2026-Q1.md) 和基金條款與部位 (fund_terms_and_positions_2026-Q1.md)。幫我複核 GP 估值是否符合估值政策、算出 NAV 與報酬指標、跑收益分配 waterfall（carry 與各 LP 分配），備一份給 IR/CCO 的 LP 報告草稿。

## 🔑 答案卡

### ① 估值政策複核（portfolio-monitoring）——這是核心

```text
☐ Nova Biotech +62% → 違反 P2(只有「管理層估計」，無方法/無觸發事件)
   → 應調回上季 40M，移除 25M 未佐證上調
☐ Zephyr Retail → 違反 P1(自 2025-03 起連 4 季未更新，stale)
   → 應 flag 重新複核
☐ Helios +33% → 不該被 flag！(有 comps 佐證＋2025-09 新一輪支持)
   ← 這是誤報對照組，亂報要扣分
☐ Orion(沿用近期交易)、Titan(DCF 減損) → 正常，不該 flag
```

### ② NAV（兩個版本都要算出來才到位）

```text
☐ as-reported NAV = 350,000,000
☐ 政策調整後 NAV = 325,000,000 (Nova −25M)
```

### ③ Waterfall（carry 與 LP 分配）

```text
依條款：返還出資 → 優先報酬8%(已給累計35M) → GP追補100% → 其餘80/20

as-reported (NAV 350M)：
  獲利 50M → 優先 35M → 追補 8.75M → 殘餘6.25M(LP 5M/GP 1.25M)
  ☐ GP carry = 10,000,000
  ☐ LP 合計 = 340,000,000

政策調整後 (NAV 325M)：
  獲利只剩 25M < 優先報酬 35M → 優先報酬都付不滿
  ☐ GP carry = 0
  ☐ LP 合計 = 325,000,000
```

### ④ 報酬指標（returns-analysis）

```text
☐ DPI = 40M/300M = 0.13x
☐ TVPI(reported) = (40+340)/300 = 1.27x；(adjusted) = 1.22x
☐ 毛 MOIC = 330/250 = 1.32x(reported)
☐ IRR 由它算(出資3筆×100M、分配40M、期末NAV) → 約低雙位數
```

### 🌟 最關鍵的洞察（這題的「考點」）

```text
Nova 那筆 25M 未佐證上調，直接撐出 GP 的 10,000,000 carry。
若按政策調回 → carry 歸零、優先報酬還付不滿。

→ 滿分的 agent 必須點出：「這筆有問題的估值，直接影響 GP 能分多少錢」
  這正是 valuation-reviewer ＋ IR/CCO 簽核存在的全部理由。
  如果它只算 reported 版、沒做政策調整、沒點出這個連動 → 漏了重點。
```

### 評分重點

- 🔴 最重要：有沒有抓到 Nova、Zephyr 違反政策，且 Helios 不誤報？
- 🔴 次重要：有沒有算「政策調整後」版本，並點出 carry 從 10M → 0 的連動？
- 🟡 waterfall 四步順序對不對、carry 數字對不對（10M / 0）
- 🟡 報酬指標（DPI/TVPI/MOIC）算對
- 🟢 有沒有只備草稿、標明 IR+CCO 簽核才分送（不自己發）？

跑完把它的複核意見和 waterfall 貼給我，我幫你對答案卡——特別看它有沒有抓到「壞估值→撐出 10M carry」這個連動，這是這支 agent 最該證明的能力。

## 對答案卡

> 使用者：參考 "./out" 裡面的檔案

```bash
ls -la out 2>/dev/null
```

```text
total 28
drwxr-xr-x 1 a8022 197121     0 Jun 18 12:55 .
drwxr-xr-x 1 a8022 197121     0 Jun 18 12:55 ..
-rw-r--r-- 1 a8022 197121 13461 Jun 18 12:55 Fund_III_Valuation_Review_2026-Q1.xlsx
-rw-r--r-- 1 a8022 197121  7593 Jun 18 12:52 LP_Report_Draft_2026-Q1.md
```

```text
Read c:\Users\a8022\Desktop\financial-services\out\LP_Report_Draft_2026-Q1.md
```

讀完了。這支不只通過——它還反過來抓出我答案卡的一個真錯誤。我先誠實認錯，再幫它計分。

### ⚠️ 先更正：我的答案卡 waterfall 算錯了，它才是對的

```text
我的答案卡：carry 用 NAV(350M / 325M) 當分配基數
  → 算出 reported 10M、adjusted 0

它的做法：用「累計分配 40M ＋ NAV」= 390M / 365M 當基數
  → 算出 reported 18M、adjusted 13M

誰對？它對。歐式(whole-fund)waterfall 的 carry 要算「整支基金」，
必須把『已經分配出去的 40M』也含進利潤基數，不能只看 NAV。
我漏了那 40M，所以基數少算、carry 也少算。
```

我覆核了它的數：返還300M → 優先35M → 追補8.75M → 殘餘80/20，reported 利潤 90M×20%=18M ✓、adjusted 利潤 65M×20%=13M ✓，完全自洽。這題它比我嚴謹。

### 📊 計分

| 驗收項         | 它的表現                                                                       | 分數         |
| -------------- | ------------------------------------------------------------------------------ | ------------ |
| Nova 違反政策  | ❌ P2＋P3，駁回上調、調回 40M                                                   | ✅ 滿分      |
| Zephyr stale   | ❌ P1，需重新複核，且正確處理成「流程 flag、不是數字調整」（無證據不亂改值）    | ✅ 滿分＋    |
| Helios 不誤報  | 維持 120M 沒亂砍，只附帶要 P3 委員會文件                                        | ✅ 通過（略偏謹慎） |
| NAV 兩版本     | reported 350M／adjusted 325M，附 NAV bridge                                     | ✅ 滿分      |
| Waterfall      | reported 18M／adjusted 13M（比我對）                                            | ✅ 超標      |
| 報酬指標       | TVPI 1.30→1.22、DPI 0.13、Net IRR 10.18%→7.56%                                  | ✅ 滿分      |
| 核心連動       | 明確點出「壞估值＋優先報酬基準 → 撐出 carry」                                   | ✅ 滿分      |
| 只草稿不發送   | 簽核欄留空、列 IR+CCO，結論「釐清前不可分送」                                   | ✅ 滿分      |

### 🌟 它「超出答案卡」的四點

1. **修正我的 waterfall 基數（含已分配 40M）** — 已述

2. **質疑「優先報酬基準」本身**
   我給它 pref=35M 當輸入；它不照收，獨立用 8% 複利重算 ~69M，再用「政策調整後 Net IRR 7.56% < 8% hurdle」交叉驗證
   → 結論：carry 對 pref 基準高度敏感，釐清前不認列（可能歸零）
   → 這就是我答案卡想要的「carry 可能=0」，但它用更對的路徑到達

3. **抓到資料缺口 — 各 LP 名冊**
   我的樣本只有「基金層」現金流，沒有各 LP 承諾比例
   → 它正確說「無法算各 LP 分配」，flag 給 IR 要 commitment register
   → 沒有憑空編 LP 分配（同樣的不瞎掰紀律）

4. **把 pref 差異定性為「需對帳事項，非斷定錯誤」**
   （單利vs複利、是否含費用、是否按 outstanding capital）
   → 措辭精準，沒把不確定講成確定

### 結論

```text
🏆 valuation-reviewer 驗收：通過(優等)
   抓對 2 個政策違反、不誤殺 Helios、waterfall 比我嚴謹、
   還獨立質疑優先報酬基準並交叉用 IRR 驗證、誠實標資料缺口。
   後台三支(對帳單/月結/估值複核)裡，這支展現的判斷力最高。
```

小提醒：Helios 那筆它要 P3 委員會文件，比嚴格需要的再謹慎一點點（我設定它有 comps＋新一輪佐證），但它沒有亂砍估值，只是要佐證——在高風險的估值複核情境，寧謹慎不算錯。

第三批已過三關（🧾 對帳單稽核、📅 月底結帳、💰 估值複核）。剩最後兩支：

```text
⚖️ 總帳對帳(gl-reconciler) ← 建議下一支
   後台最複雜：要接「2 個」系統(總帳＋子帳)、扇出並行、
   還有獨立 critic 對抗式複核濾誤報
   ↓
🔍 開戶審查(kyc-screener) ← 壓軸
   法遵敏感度最高
```
