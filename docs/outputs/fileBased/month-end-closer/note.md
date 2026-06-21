# 📅 月底結帳（month-end-closer）— 筆記

月底結帳（month-end-closer）——後台第二站，整合一樣輕（只接 1 個唯讀總帳來源），而且跟對帳單稽核一樣可以「餵檔案」試水溫，不必真的接系統。

我直接幫你把配套樣本檔也產好（這支需要的是「試算表」，我做一份含當月＋上月對照的試算表，外加一份待估列項目（應計）清單，讓它有東西可結）。

## 樣本檔一：試算表

```text
Write <repo>\samples\month-end-closer\trial_balance_2026-04.md
45 lines
```

### 試算表 Trial Balance — Aurora Capital Management LLC

> **這是什麼**：基金管理公司（GP 管理實體）的月結試算表，是 month-end-closer 的**結帳起點**。
> 含**上月（2026-03）對照欄**，方便算差異（flux）。本檔為**假資料**，狀態為**結帳前（pre-close，尚未估列應計）**。

- **實體 / Entity**：Aurora Capital Management LLC
- **結帳期間 / Period**：2026-04（4 月）
- **幣別 / Currency**：USD
- **狀態**：Pre-close（待估列應計、待差異說明、待結轉）

#### 試算表（YTD 餘額；含上月對照）

| 科目 Acct | 名稱 Account | 類別 Type | 借/貸 Dr/Cr | 上月 2026-03 (YTD) | 本月 2026-04 (YTD, pre-close) |
| --- | --- | --- | --- | ---: | ---: |
| 1000 | 現金 Cash | 資產 Asset | Dr | 8,000,000 | 7,550,000 |
| 1100 | 應收管理費 Mgmt Fees Receivable | 資產 Asset | Dr | 3,000,000 | 3,200,000 |
| 1200 | 預付費用 Prepaid Expenses | 資產 Asset | Dr | 600,000 | 600,000 |
| 1500 | 固定資產（淨）Fixed Assets, net | 資產 Asset | Dr | 1,400,000 | 1,350,000 |
| 2000 | 應付帳款 Accounts Payable | 負債 Liability | Cr | 900,000 | 1,100,000 |
| 2100 | 應付費用 Accrued Expenses | 負債 Liability | Cr | 1,200,000 | 1,000,000 |
| 2200 | 遞延收入 Deferred Revenue | 負債 Liability | Cr | 500,000 | 400,000 |
| 3000 | 成員資本 Members' Capital | 權益 Equity | Cr | 8,000,000 | 8,000,000 |
| 3100 | 期初保留盈餘 Retained Earnings (BOY) | 權益 Equity | Cr | 2,000,000 | 2,000,000 |
| 4000 | 管理費收入 Management Fee Income | 收入 Revenue | Cr | 6,300,000 | 8,500,000 |
| 4100 | 其他收入 Other Income | 收入 Revenue | Cr | 300,000 | 380,000 |
| 6000 | 薪酬 Compensation | 費用 Expense | Dr | 4,500,000 | 6,000,000 |
| 6100 | 租金 Rent | 費用 Expense | Dr | 600,000 | 800,000 |
| 6200 | 專業服務費 Professional Fees | 費用 Expense | Dr | 400,000 | 750,000 |
| 6300 | 資訊技術 Technology | 費用 Expense | Dr | 300,000 | 400,000 |
| 6400 | 差旅 Travel | 費用 Expense | Dr | 150,000 | 350,000 |
| 6500 | 其他營運費用 Other Opex | 費用 Expense | Dr | 250,000 | 330,000 |
| 6600 | 折舊 Depreciation | 費用 Expense | Dr | 0 | 50,000 |

#### 借貸平衡驗算（Pre-close）

| | 上月 2026-03 | 本月 2026-04 |
| --- | ---: | ---: |
| 借方合計 Total Debits | 19,200,000 | 21,380,000 |
| 貸方合計 Total Credits | 19,200,000 | 21,380,000 |
| 差額 Difference | 0 ✓ | 0 ✓ |

> 兩期試算表本身皆已平衡（借＝貸）。**結帳工作是在此之上估列應計、做結轉、寫差異說明**——應計項目見 `accruals_support_2026-04.md`。

## 樣本檔二：待估列應計清單

```text
Write <repo>\samples\month-end-closer\accruals_support_2026-04.md
42 lines
```

### 待估列應計項目清單 Accruals Support — 2026-04

> **這是什麼**：4 月底結帳時，**應該估列但尚未入帳**的費用，以及應付費用科目的結轉（roll-forward）起算資料。
> month-end-closer 應據此**提出應計分錄草稿**並驗證結轉「對得上」。本檔為**假資料**。

- **實體 / Entity**：Aurora Capital Management LLC
- **結帳期間 / Period**：2026-04
- **幣別 / Currency**：USD

#### A. 待估列應計項目（尚未入帳，需在 4 月估列）

| # | 項目 Item | 說明 | 借（費用）Dr | 貸（應付費用）Cr | 金額 USD |
| --- | --- | --- | --- | --- | ---: |
| A1 | IT 服務商 4 月帳單 | 發票 5/3 才開（月結後才到），屬 4 月服務 → 應估列 | 6300 資訊技術 Technology | 2100 應付費用 | 75,000 |
| A2 | 4 月分紅估列 | 年度獎金池估 1,200,000，按月攤 100,000／月 → 4 月估列 | 6000 薪酬 Compensation | 2100 應付費用 | 100,000 |
| A3 | FY2026 外部審計費 | 全年估 300,000，至 4 月完成約 1/3 → 累計估列 100,000，已入帳 0 | 6200 專業服務費 Professional Fees | 2100 應付費用 | 100,000 |
| | **合計** | | | | **275,000** |

#### B. 應付費用（2100）結轉資料（Roll-forward seed）

| 項目 | 金額 USD |
| --- | ---: |
| 期初餘額（2026-03 月底）Beginning | 1,200,000 |
| 減：4 月已支付／沖回 Payments & Reversals | (200,000) |
| ＝ 結帳前餘額（pre-close，與試算表一致） | 1,000,000 |
| 加：本月新估列應計（A1+A2+A3）New Accruals | 275,000 |
| **＝ 期末餘額（post-close）Ending** | **應自行算出並驗證對得上** |

> ✅ **結轉 foot check**：期初 1,200,000 − 支付 200,000 ＋ 新估列 275,000 = **期末**。
> 正確的 agent 應該算出期末 = 1,275,000，並驗證「期初 ＋ 變動 = 期末」對得上（這是它的內建自我驗證）。

#### C. 重大性門檻（Materiality）

- **預設門檻**：費用科目較上月變動 **> 5%** 者，需寫差異說明（variance commentary）。
- 結帳前已知幾個費用科目跳動較大（專業服務費、差旅、資訊技術），請從**底層實際活動**解釋，原因不明就標示、不瞎掰。

## 怎麼用

兩份樣本檔已產好，放在 `samples/month-end-closer/`：

```text
samples/month-end-closer/
  ├─ trial_balance_2026-04.md     ← 試算表（含本月＋上月對照，已平衡）
  └─ accruals_support_2026-04.md  ← 待估列應計清單 ＋ 結轉起算資料
```

把這句丟給你裝好的 month-end-closer：

```text
這是 Aurora Capital Management LLC 的 2026-04 試算表 (trial_balance_2026-04.md)
和待估列應計清單 (accruals_support_2026-04.md)。幫我跑月結：估列應計、
做應付費用結轉、對變動大的科目寫差異說明，組裝成結帳包。
```

## 🔑 答案卡（對照它跑出來的結帳包打分）

這支跟對帳單稽核不同——它不是「找錯」，是「建構」。所以看它有沒有正確做出三件事：

```text
① 應計分錄(該估列 3 筆，合計 275,000)
   ☐ A1 IT 帳單 75,000   (Dr 資訊技術 / Cr 應付費用)
   ☐ A2 分紅估列 100,000 (Dr 薪酬 / Cr 應付費用)
   ☐ A3 審計費 100,000   (Dr 專業服務費 / Cr 應付費用)

② 應付費用(2100)結轉，foot check 要對得上
   ☐ 期初 1,200,000 − 支付 200,000 ＋ 新估列 275,000 = 期末 1,275,000
   ☐ 它有沒有「驗證期初＋變動=期末對得上」？(這是它的內建自我驗證，最關鍵)

③ 差異說明(>5% 門檻；估列後 vs 上月)
   ☐ 專業服務費 400,000→850,000 (+112%)  → 審計季＋審計費估列
   ☐ 差旅       150,000→350,000 (+133%)  → 需從實際活動解釋
   ☐ 資訊技術   300,000→475,000 (+58%)   → 新增＋4月帳單估列
   ☐ 薪酬       4,500,000→6,100,000(+36%) → 月薪酬常態＋分紅估列
   ☐ 它有沒有「原因不明就標示、不瞎掰」？(誠信測試)
```

### 評分重點（三個 vs 統一）

```text
🔴 最重要：結轉 foot check 有沒有對得上 (期末=1,275,000)
   → 對得上＝它的內建驗證在運作；對不上或硬湊(plug)＝危險信號

🟡 應計：3 筆有沒有都估列、方向(借費用/貸應付)對不對

🟡 差異說明：有沒有「從底層實際活動」解釋，而不是空話帶過
   → 加分：明確指出哪些是「常態 run-rate」(租金 200k/月)、
     哪些是「真的異常」(差旅暴增)
```

### 這支「新增要注意」的地方（跟對帳單稽核的差別）

```text
① 它是「自我驗證」型——沒有獨立 critic，驗證內建在「結轉必須對得上」
   (因為結帳是「建平衡表」，不是「挑誤報」，驗證設計隨任務性質不同)
② 它「永不過帳」——只組裝結帳包草稿，控制員(controller)核准後才過帳
③ 它要「不硬湊」——對不上就攤開、原因不明就標示，不擠一個假數字進去
```

跑完把它的結帳包（尤其是結轉那段和差異說明）貼給我，我幫你對答案卡看它幾分，特別是 foot check 到底有沒有對上 1,275,000。

下一支（第三批還剩 💰 估值複核 → ⚖️ 總帳對帳 → 🔍 開戶審查）等你這支驗收完再繼續。

## 驗收：讀結帳包、對答案卡打分

> 使用者：參考 "./out" 裡面的檔案

```bash
echo "=== ./out ===" && ls -la out 2>/dev/null; echo "=== outputs/ ===" && ls -R outputs 2>/dev/null | head -80
```

```text
=== ./out ===
total 24
drwxr-xr-x 1 <user> 197121     0 Jun 18 12:39 .
drwxr-xr-x 1 <user> 197121     0 Jun 18 12:38 ..
-rw-r--r-- 1 <user> 197121 11672 Jun 18 12:39 Close_Package_2026-04.xlsx
-rw-r--r-- 1 <user> 197121  6488 Jun 18 12:36 close_package_2026-04.md
=== outputs/ ===
outputs:
earning-reviewer
market-researcher
model-builder
pitch
statement-auditor

outputs/earning-reviewer:
execution_history.md
note.md
out
scripts

outputs/earning-reviewer/out:
TSMC_DCF_Valuation.xlsx
TSMC_Q1-2026_Model.xlsx
TSMC_Q1_2026_Earnings_Note.docx
TSMC_Q1_2026_Earnings_Update.docx
charts

outputs/earning-reviewer/out/charts:
01_revenue.png
02_grossmargin.png
03_eps.png
04_platform.png
05_node.png
06_beatmiss.png
07_q2guide.png
08_fyrevenue.png
09_capex.png
10_gmwalk.png
11_football.png

outputs/earning-reviewer/scripts:
build_tsmc_charts.py
build_tsmc_dcf.py
build_tsmc_model.py
build_tsmc_note.py
build_tsmc_report.py
build_tsmc_valchart.py

outputs/market-researcher:
execution_history.md
note.md
out
scripts

outputs/market-researcher/out:
AI資料中心散熱_Comps.xlsx
AI資料中心散熱_產業研究.pptx
Vertiv_VRT_DCF.xlsx

outputs/market-researcher/scripts:
build_comps.py
build_dcf.py
build_deck.py

outputs/model-builder:
execution_history.md
note.md
out
scripts

outputs/model-builder/out:
VRT_DCF_Model_2026-06-18.xlsx

outputs/model-builder/scripts:
build_vrt_dcf2.py

outputs/pitch:
execution_history.md
note.md
out
scripts

outputs/pitch/out:
VRT_M&A_Proposal_Draft.pptx
VRT_MA_Valuation.xlsx
charts
```

月結跑出來了，輸出在 out/。我來讀它的結帳包，對照答案卡打分。

```text
Read <repo>\out\close_package_2026-04.md
```

讀完了。這支跑得非常好——甚至比我的答案卡還嚴格，而且反過來抓出我樣本資料裡的兩個破綻。逐項對分：

### 📊 對答案卡計分

| 驗收項 | 答案卡要求 | 它的表現 | 分數 |
| --- | --- | --- | --- |
| ① 應計 3 筆 | A1 IT 75k／A2 分紅 100k／A3 審計 100k，方向 Dr費用 Cr應付 | 全中，方向正確，還多標了沖回邏輯（A1 自動沖回、A2 年底發放不沖回） | ✅ 滿分＋ |
| ② 結轉 foot check | 期初1,200k −支付200k ＋估列275k = 期末1,275k | 算出 1,275,000，並明寫「期初＋變動=期末對得上」 | ✅ 滿分 |
| ③ 差異說明 | 對 >5% 科目從實際活動解釋 | 用了比我更對的方法（見下） | ✅ 超標 |
| 誠信（不瞎掰） | 原因不明就標示 | 來源不明的明確標「需查 GL」，不編理由 | ✅ 滿分 |
| 永不過帳 | 只草稿、待簽核 | 分錄全標 draft、簽核欄留空 | ✅ 滿分 |
| 誤報控制 | 不該亂報 | 租金、其他營運正確判為「正常 run-rate」 | ✅ 滿分 |

### 🌟 它「超出答案卡」的三點（這才是亮點）

```text
1. 差異分析方法比我對
   我的答案卡：拿 YTD(4個月) 比 YTD(3個月) → 其實會放大每條費用
   它的做法：改用「4月當月 vs 前3個月平均月跑率」→ 這才是正確的 flux 分析
   → 它沒照我給的爛基準走，反而用了會計上更正確的口徑

2. 抓到我沒埋的破綻① — 折舊時點
   我隨手把 1–3月折舊設 0、4月設 50k(沒多想)
   它抓到：「有 140萬固定資產卻 Q1 不提折舊、4月才提」→ 疑似 1–3月漏提
   → 這是我樣本資料的真實瑕疵，它合理揪了出來

3. 抓到我沒埋的破綻② — 分紅估列前期
   我只讓它估列「4月」那筆 100k
   它反問：若 1–3月也該按月估列，YTD 應有 300k，怎麼只見 4月？
   → 又一個我資料的隱含控制問題，它主動 flag 給 controller
```

💡 重點：第 2、3 點不是它出錯，是它把我樣本裡的不一致挑出來了——這正是月結 agent 最該有的行為（寧可多問，不硬湊）。它甚至把這些放進 §5「待 controller 處理」清單，沒自己擅自補帳。

### 數字我也覆核過

```text
✓ post-close 借貸平衡 21,655,000 = 21,655,000
✓ YTD 淨利 +200,000 →(估列 −275,000)→ −75,000
✓ 專業服務費當月 450k：審計估列 100k 已解釋，殘差 350k vs 跑率 133k → 合理判為異常
✓ 差旅當月 200k = 跑率 4 倍 → 合理 flag
```

全部算對。

### 結論

```text
🏆 month-end-closer 驗收：通過(近滿分)
   它不只把 3 件事做對，還用更正確的方法、外加抓出測試資料本身的兩個瑕疵。
   這支的「自我驗證(foot check)＋不瞎掰」設計，在這次跑測裡完整展現了。
```
