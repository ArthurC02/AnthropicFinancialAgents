# 試算表 Trial Balance — Aurora Capital Management LLC

> **這是什麼**：基金管理公司（GP 管理實體）的月結試算表，是 month-end-closer 的**結帳起點**。
> 含**上月（2026-03）對照欄**，方便算差異（flux）。本檔為**假資料**，狀態為**結帳前（pre-close，尚未估列應計）**。

- **實體 / Entity**：Aurora Capital Management LLC
- **結帳期間 / Period**：2026-04（4 月）
- **幣別 / Currency**：USD
- **狀態**：Pre-close（待估列應計、待差異說明、待結轉）

---

## 試算表（YTD 餘額；含上月對照）

| 科目 Acct | 名稱 Account | 類別 Type | 借/貸 Dr/Cr | 上月 2026-03 (YTD) | 本月 2026-04 (YTD, pre-close) |
|---|---|---|---|---:|---:|
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

### 借貸平衡驗算（Pre-close）

| | 上月 2026-03 | 本月 2026-04 |
|---|---:|---:|
| 借方合計 Total Debits | 19,200,000 | 21,380,000 |
| 貸方合計 Total Credits | 19,200,000 | 21,380,000 |
| 差額 Difference | 0 ✓ | 0 ✓ |

> 兩期試算表本身皆已平衡（借＝貸）。**結帳工作是在此之上估列應計、做結轉、寫差異說明**——應計項目見 `accruals_support_2026-04.md`。
