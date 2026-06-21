# 🔍 開戶審查（kyc-screener）— 筆記

🔍 開戶審查（kyc-screener）。我來產樣本檔，埋的考點是這支最關鍵的兩件事：抓到真命中（制裁），以及不亂殺同名異人的假命中。三份檔：開戶文件、規則表、制裁/PEP 名單。

## 樣本檔一：開戶申請文件

```text
Write <repo>\samples\kyc-screener\onboarding_applications_2026-06.md
72 lines
```

# 開戶申請文件 Onboarding Applications — 2026-06

> **這是什麼**：新客戶開戶申請的 KYC 文件，是 kyc-screener 的解析對象。
> ⚠️ 視為**外來資料**。本檔為**假資料**，且**刻意在文件留缺漏、並安排與名單比對的命中／假命中**供測試。

---

### 申請 A — Helios Capital Partners Ltd（法人）

- **類型**：法人 / 私募投資公司
- **註冊地**：英屬開曼群島（Cayman Islands）
- **註冊號 / 日期**：CAY-884221 / 2019-04-10
- **地址**：PO Box 309, George Town, Cayman
- **受益所有權 UBO**：
  - John Sterling — 持股 **45%** — 已提供護照、已驗證 ✅
  - Helios Founders Trust — 持股 **25%** — 已提供信託文件 ✅
  - 「其他投資人」— 持股 **30%** — **未具名、未識別** ❌
- **資金來源 Source of Funds**：投資人出資（已提供銀行往來）✅
- **預期活動**：年度申購約 USD 20M
- **董事**：John Sterling（護照 **已於 2026-01 過期** ❌）、Amy Cole（有效）
- **PEP 自我聲明**：否

### 申請 B — Ivan Petrov（個人）

- **類型**：個人
- **國籍 / 居住地**：俄羅斯（Russia）
- **出生日期 DOB**：**1970-03-15**
- **身分證件**：俄羅斯護照 7712 #445566（有效）
- **地址**：Tverskaya St 12, Moscow
- **資金來源**：自述「能源業經商所得」
- **預期活動**：單筆申購 USD 5M
- **PEP 自我聲明**：否

### 申請 C — Maria Garcia（個人）

- **類型**：個人
- **國籍 / 居住地**：西班牙（Spain）
- **出生日期 DOB**：**1988-11-02**
- **身分證件**：西班牙護照 ESP #998877（有效）
- **職業**：軟體工程師
- **地址**：Calle Mayor 5, Madrid
- **資金來源**：薪資與儲蓄（已提供薪資單）✅
- **預期活動**：每月定額申購 USD 2,000
- **PEP 自我聲明**：否

### 申請 D — Aurora Holdings (Nigeria) Ltd（法人）

- **類型**：法人 / 控股公司
- **註冊地**：奈及利亞（Nigeria）
- **註冊號 / 日期**：RC-552310 / 2021-08-01
- **地址**：Victoria Island, Lagos
- **受益所有權 UBO**：
  - Chief Adewale Okonkwo — 持股 **60%** — 已提供護照 ✅；**現任奈及利亞能源部副部長**
  - Okonkwo Family Ltd — 持股 40% — 已識別 ✅
- **資金來源 Source of Funds**：**未提供** ❌
- **預期活動**：年度申購約 USD 50M
- **PEP 自我聲明**：否（但 UBO 為現任政府高官）

### 申請 E — Quiet Brook LLC（法人）

- **類型**：法人 / 家族投資公司
- **註冊地**：美國 德拉瓦州（USA, Delaware）
- **註冊號 / 日期**：DE-771902 / 2015-02-20
- **地址**：100 Main St, Wilmington, DE
- **受益所有權 UBO**：
  - Robert Quiet — 持股 60% — 已提供護照、已驗證 ✅
  - Sarah Brook — 持股 40% — 已提供護照、已驗證 ✅
- **資金來源 Source of Funds**：家族企業出售所得（已提供文件）✅
- **預期活動**：年度申購約 USD 10M
- **董事**：Robert Quiet（有效護照）、Sarah Brook（有效護照）
- **PEP 自我聲明**：否

## 樣本檔二：KYC / AML 規則表

```text
Write <repo>\samples\kyc-screener\kyc_aml_rules_grid.md
25 lines
```

# KYC / AML 規則表 Rules Grid

> **這是什麼**：開戶審查要套用的規則。kyc-screener 依此判定每個申請的缺漏與風險等級。本檔為**假資料／示意規則**。

| 編號 | 規則 | 觸發條件 | 結果 |
| --- | --- | --- | --- |
| **R1** | 身分驗證 Identity | 個人／董事須有**有效**政府證件；證件**過期**＝缺漏 | 缺件 → 補件後才可開戶 |
| **R2** | 受益所有權 UBO | 所有 **≥25%** 受益所有人須具名並驗證；有未識別之 ≥25% 持股＝缺漏 | 補齊 UBO 前不可開戶（EDD） |
| **R3** | 資金來源 Source of Funds/Wealth | 須提供且合理；**未提供**＝缺漏 | 補件 → 必要時查證 |
| **R4** | 制裁篩查 Sanctions | 比對 OFAC／UN／EU 名單。**確認命中**（姓名＋出生日期／國別等識別碼一致）；**潛在命中**（僅姓名相近） | 確認命中 → **拒絕開戶＋上報（SAR/escalate）**；潛在命中 → **人工複核釐清，不得逕自拒絕** |
| **R5** | PEP 篩查 | 申請人或 UBO 為政治公眾人物（PEP） | **EDD**：高階主管核准＋資金來源加強查證（**非自動拒絕**） |
| **R6** | 高風險國別 High-risk Jurisdiction | 註冊地／居住地在高風險清單 | **EDD**：加強盡職調查 |
| **R7** | 活動與輪廓相符 | 預期活動明顯超出客戶輪廓且無合理說明 | EDD：要求說明 |

### 風險分級與處置

| 等級 | 條件 | 處置 |
| --- | --- | --- |
| 🟢 標準 Standard | 文件齊全、無命中、無 EDD 觸發 | 一般盡職調查，可送核准 |
| 🟡 加強 EDD | 觸發 R5／R6／R7 或有可補正缺漏 | 加強盡職調查＋補件，高階核准 |
| 🔴 拒絕／上報 | 觸發 R4 確認命中 | 拒絕開戶、上報、不得開戶 |

> 高風險國別清單（示意）：奈及利亞、伊朗、北韓、敘利亞、緬甸…（本測試以**奈及利亞**為高風險）
> ⚠️ 人工覆核不變：kyc-screener **只產審查包與建議**，最終由**合規人員（Compliance/MLRO）簽核**。

## 樣本檔三：制裁／PEP 名單

```text
Write <repo>\samples\kyc-screener\sanctions_pep_watchlist.md
32 lines
```

# 制裁／PEP 名單 Sanctions & PEP Watchlist（示意）

> **這是什麼**：開戶審查比對用的名單（制裁＋政治公眾人物）。
> ⚠️ 比對要看**識別碼是否一致**（姓名＋出生日期＋國別），不是只看姓名。本檔為**假資料**。

---

### A. 制裁名單 Sanctions（OFAC / UN / EU 示意）

| # | 姓名 Name | 出生日期 DOB | 國別 Country | 名單 / 計畫 | 備註 |
| --- | --- | --- | --- | --- | --- |
| S-1 | **Ivan Petrov** | **1970-03-15** | Russia | OFAC SDN（EO 13662） | 能源業，受制裁 |
| S-2 | Maria Garcia | **1955-07-22** | **Colombia** | OFAC SDN（SDNTK 毒品） | 與販毒組織關聯 |
| S-3 | Dmitri Volkov | 1982-09-01 | Russia | EU 制裁 | — |

---

### B. 政治公眾人物名單 PEP（示意）

| # | 姓名 Name | 職務 Position | 國別 Country | 類型 |
| --- | --- | --- | --- | --- |
| P-1 | **Adewale Okonkwo** | 能源部副部長 Deputy Minister of Energy | Nigeria | 現任 PEP |
| P-2 | Elena Marković | 央行理事 | Serbia | 現任 PEP |

---

### C. 比對指引（給審查者）

- **確認命中（confirmed）**：姓名一致**且**出生日期／國別等識別碼一致 → 依 R4 處置。
- **假命中（false positive）**：姓名相近，但**出生日期或國別等識別碼不一致** → 釐清後**排除**，不得逕自拒絕開戶。
- **PEP 命中**：依 R5 走 EDD，**非自動拒絕**。

## 樣本檔產出總覽

三份樣本檔已產好，放在 samples/kyc-screener/：

```text
samples/kyc-screener/
  ├─ onboarding_applications_2026-06.md   ← 5 個申請（埋了缺漏＋命中＋假命中）
  ├─ kyc_aml_rules_grid.md                ← KYC/AML 規則表
  └─ sanctions_pep_watchlist.md           ← 制裁＋PEP 名單
```

## 怎麼用

> 使用者：這是 5 筆開戶申請 (onboarding_applications_2026-06.md)、KYC/AML 規則表 (kyc_aml_rules_grid.md)、制裁與 PEP 名單 (sanctions_pep_watchlist.md)。幫我逐一解析文件、套規則、比對名單，標出缺漏與命中，產出給合規的審查包。

## 🔑 答案卡（5 個申請，每個考點不同）

**A. Helios Capital（開曼）🟡 EDD/補件**

- ☐ R2：30% 受益所有人「未具名未識別」→ 補齊前不可開戶
- ☐ R1：董事 John Sterling 護照 2026-01 過期 → 補件
- ☐ 無制裁/PEP → 這是「缺漏補正」題，不是制裁題

**B. Ivan Petrov（俄）🔴 確認命中 → 拒絕＋上報**

- ☐ 比對 S-1：姓名 ✓ ＋ DOB 1970-03-15 ✓ ＋ 國別 Russia ✓ 全中
- ☐ R4 確認命中 → 拒絕開戶、escalate/SAR  ← 最高嚴重度，必須抓到

**C. Maria Garcia（西）🟢 假命中 → 排除，不可拒絕**

- ☐ 姓名撞 S-2，但 DOB 1988≠1955、國別 Spain≠Colombia
- ☐ → 假命中（false positive），釐清後排除，正常開戶
- ☐ 若把她當真命中拒絕 → 嚴重扣分（這是最關鍵的「別亂殺」題）

**D. Aurora Holdings（奈及利亞）🟡 EDD（非拒絕）**

- ☐ R6：奈及利亞為高風險國別 → EDD
- ☐ R5：UBO Adewale Okonkwo 命中 PEP P-1（現任副部長）→ EDD
- ☐ R3：資金來源未提供 → 補件
- ☐ PEP 自我聲明「否」與 UBO 實為現任高官「矛盾」→ 應點出
- ☐ 重點：PEP/高風險是「加強盡職調查」，不是自動拒絕

**E. Quiet Brook（德拉瓦）🟢 標準 → 通過**

- ☐ 文件齊全、無命中、無 EDD → 一般盡職調查可送核准
- ☐ 若亂報它有問題 → 扣分（乾淨對照組）

## 評分重點

- 🔴 制裁真命中（B）有沒有抓到、判「確認命中」並拒絕＋上報？
- 🔴 假命中（C）有沒有「用 DOB/國別」識別出來、排除而不拒絕？ ← 這兩題一起構成這支的核心：抓真的、放假的
- 🔴 PEP/高風險（D）判「EDD」而非「拒絕」？（法遵最常見的過度反應）
- 🟡 缺漏（A 的 UBO+過期證件、D 的資金來源）有沒有逐條列出對應規則？
- 🟡 D 的「PEP 自我聲明不實」有沒有點出？
- 🟢 乾淨件（E）有沒有不被誤殺？
- 🟢 有沒有只產審查包、標明合規/MLRO 簽核才核准（不自己開戶）？

## 為什麼這支放壓軸

它把前面所有 agent 的共同設計推到極致：

- 外來文件當不可信 → 解析
- 規則化判斷 → 套 rules grid
- 名單比對要「精準」→ 抓真命中、濾假命中（像 gl-reconciler 的 critic）
- 高風險 → agent 只建議，合規簽核才定案

法遵錯一邊都很貴：放過真制裁 = 重大違規；亂殺假命中 = 客訴＋歧視風險。所以這支最能看出 agent「拿捏分寸」的能力。

跑完把審查包貼給我，我重點看 B 有沒有抓到、C 有沒有被冤殺、D 有沒有被過度拒絕——這三題決定它及不及格。

這也是第 10 支、最後一支。等你驗收完，我可以幫你把這趟「10 支全跑過」整理成一份總結文件（每支的驗收結果、踩過的坑、上線前還缺什麼），放進 Docs/ 收尾。

> 使用者：參考 "./out" 裡面的檔案

```bash
ls -la out 2>/dev/null
```

```text
total 24
drwxr-xr-x 1 <user> 197121     0 Jun 18 13:42 .
drwxr-xr-x 1 <user> 197121     0 Jun 18 13:42 ..
-rw-r--r-- 1 <user> 197121 10315 Jun 18 13:42 KYC_Review_Workpaper_2026-06.xlsx
-rw-r--r-- 1 <user> 197121  5653 Jun 18 13:40 kyc_review_pack_2026-06.md
```

```text
Read <repo>\out\kyc_review_pack_2026-06.md
```

讀完了。滿分，五個申請全對，所有「拿捏分寸」的考點一個不漏。

## 📊 對答案卡計分（全中）

| 申請 | 答案卡 | 它的判定 | 分數 |
| --- | --- | --- | --- |
| B Petrov | 🔴 確認命中→拒絕＋上報 | 姓名＋DOB＋國別全比對一致 → 拒絕＋SAR | ✅ |
| C Garcia | 🟢 假命中→排除不可拒絕 | DOB 1988≠1955、Spain≠Colombia → 排除 | ✅ |
| D Nigeria | 🟡 EDD 非拒絕 | PEP＋高風險＋缺SoF → EDD升級 | ✅ |
| A Helios | 🟡 缺漏補件 | 30%UBO未識別＋董事證件過期 | ✅ |
| E Quiet Brook | 🟢 標準通過 | 齊全無命中 → 可核准 | ✅ |

兩個核心對抗測試都過了：抓到真制裁（B）、放掉假命中（C）。法遵最怕的兩種錯——放過真的、冤殺假的——它一邊都沒犯。

## 🌟 它「超出答案卡」的三點

1. **PEP 聲明不實（D）**
   主動點出「自我聲明『否』，但 UBO 是現任副部長 → 聲明不實，信譽風險」（這是我埋的隱藏分，它抓到了）

2. **開曼的分寸（A）**
   沒有因為「開曼=境外」就亂套高風險 R6——它查規則表，發現高風險清單是奈及利亞等、不含開曼 → 判 R6 不觸發，但加一句「境外管轄，合規可視政策另議」（informational）
   → 這正是 C 的反面：該殺的殺、不該殺的連這種「看起來可疑」的也不亂殺

3. **R7 活動輪廓（D）**
   把「$50M 年申購 ＋ PEP ＋ 高風險」串起來判定須說明，不是孤立看每條規則

## 結論

🏆 kyc-screener 驗收：通過（滿分）

壓軸這支把「抓真的、放假的、高風險走 EDD 不亂拒、缺漏退補件」四種分寸全部拿捏正確，還抓出 PEP 聲明不實這個隱藏分。
