# NAV Pack — 晨曦成長基金 (Aurora Growth Fund)

> **這是什麼**：基金的「官方淨值資料包」，是對帳單稽核的**核對基準（source of truth）**。
> 所有數字皆為**假資料**，僅供 statement-auditor agent 測試用。

- **基金 / Fund**：晨曦成長基金 (Aurora Growth Fund)
- **截止日 / As-of Date**：2026-03-31（Q1 季末）
- **幣別 / Currency**：USD
- **報表類型**：季度資本帳結算（Quarterly Capital Account Statement）

---

## Section A — 基金層淨值組成（Balance Sheet NAV Build）

| 項目 Item | 金額 USD |
|---|---:|
| 投資部位（按公允價值）Investments at Fair Value | 108,000,000 |
| 現金 Cash | 6,000,000 |
| 其他資產（應收）Other Assets (Receivables) | 1,500,000 |
| **總資產 Total Assets** | **115,500,000** |
| 應付管理費 Accrued Management Fee Payable | 562,500 |
| 應付費用（審計／行政）Accrued Expenses | 500,000 |
| 其他負債 Other Liabilities | 2,000,000 |
| **總負債 Total Liabilities** | **3,062,500** |
| **基金淨值 Net Assets (NAV)** | **112,437,500** |

> 驗算：115,500,000 − 3,062,500 = **112,437,500** ✓（NAV 與 Section B 各 LP 期末資本合計一致）

---

## Section B — 各出資人資本帳（Per-LP Capital Accounts）

| LP_ID | 出資人 LP Name | 期初資本 Beginning | 出資 Contributions | 分配 Distributions | 損益 Net Gain/Loss | 管理費 Mgmt Fee | 期末資本 Ending | 持份% Ownership |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LP-001 | University Endowment | 40,000,000 | 5,000,000 | 2,000,000 | 4,000,000 | 250,000 | 46,750,000 | 41.58 |
| LP-002 | State Pension Plan | 30,000,000 | 0 | 1,500,000 | 3,000,000 | 187,500 | 31,312,500 | 27.85 |
| LP-003 | Family Office LLC | 20,000,000 | 2,000,000 | 0 | 2,000,000 | 125,000 | 23,875,000 | 21.23 |
| LP-004 | GP Commitment | 10,000,000 | 0 | 500,000 | 1,000,000 | 0 | 10,500,000 | 9.34 |
| **TOTAL** | — | **100,000,000** | **7,000,000** | **4,000,000** | **10,000,000** | **562,500** | **112,437,500** | **100.00** |

> 每列驗算：期初 ＋ 出資 − 分配 ＋ 損益 − 管理費 = 期末（四列皆對得上）
> 合計驗算：100,000,000 ＋ 7,000,000 − 4,000,000 ＋ 10,000,000 − 562,500 = **112,437,500** ✓
