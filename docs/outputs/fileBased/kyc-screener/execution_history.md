# 🔍 開戶審查（kyc-screener）— 執行紀錄

## 1. 安裝外掛

```text
❯ /plugin install kyc-screener@fsi-local
  ⎿  ✓ Installed kyc-screener. Run /reload-plugins to apply.
```

## 2. 使用者請求

> 使用者：這是 5 筆開戶申請 (onboarding_applications_2026-06.md)、KYC/AML 規則表 (kyc_aml_rules_grid.md)、制裁與 PEP 名單 (sanctions_pep_watchlist.md)。幫我逐一解析文件、套規則、比對名單，標出缺漏與命中，產出給合規的審查包。

KYC/AML 開戶審查。先讀三份來源檔。

```text
● KYC/AML 開戶審查。先讀三份來源檔。

  Read 3 files (ctrl+o to expand)
```

三份都讀齊。逐一解析、套 R1–R7、依「姓名＋DOB＋國別」做名單比對（分確認命中／假命中），產出合規審查包並存到 ./out/。

## 3. 產出審查包

```text
● Write(out\kyc_review_pack_2026-06.md)
  ⎿  Wrote 110 lines to out\kyc_review_pack_2026-06.md
      1 # KYC/AML 開戶審查包 — 2026-06
      2
      3 **對象：5 筆開戶申請 · 基準：KYC/AML 規則表 R1–R7 ＋ 制裁/PEP 名單**
      4 > ⚠️  本審查包**只評分與路由,不作最終決定**;須**合規 / MLRO 簽核**。申請文件視為外來資料。
      5 > 名單比對採「**姓名＋出生日期＋國別**」識別碼一致才算確認命中。編製 2026-06-18。
      6
      7 ---
      8
      9 ## 0. 審查總覽 Dashboard
     … +101 lines (ctrl+o to expand)
```

KYC/AML 審查完成，審查包已存至 ./out/kyc_review_pack_2026-06.md。

5 筆結果：1 拒絕上報 · 2 EDD 待補 · 2 標準可核准

| 申請 | 客戶 | 等級 | 處置 | 關鍵 |
| --- | --- | --- | --- | --- |
| B | Ivan Petrov | 🔴 | 拒絕＋SAR | R4 制裁確認命中：S-1 姓名＋DOB(1970-03-15)＋國別(Russia)全部一致，OFAC SDN |
| D | Aurora (Nigeria) | 🟡高 | 升級 MLRO，補件前不可開戶 | R5 PEP（現任副部長）＋R6 高風險國＋R3 缺 SoF＋PEP 聲明不實 |
| A | Helios Capital | 🟡 | 補件前不可開戶 | R2 30% UBO 未識別＋R1 董事護照過期(2026-01) |
| C | Maria Garcia | 🟢 | 記錄後可核准 | R4 假命中：同名但 DOB(1988 vs 1955)＋國別(Spain vs Colombia)不符 → 排除 |
| E | Quiet Brook | 🟢 | 可核准 | 文件齊全、無命中 |

### 關鍵判讀（依規則精神，避免誤殺／漏網）

- B 真命中 → 拒絕＋上報：三項識別碼全中，OFAC SDN，依 R4 不得開戶。
- C 假命中 → 不得逕自拒絕：僅姓名相同，DOB 與國別都不符 → 依比對指引排除，記錄後正常核准。避免把無辜同名者誤拒。
- D PEP → EDD 非拒絕：R5 明定 PEP 走加強盡調＋高階核准，不是自動拒絕；但 PEP 自我聲明「否」與事實（現任副部長）矛盾已標為信譽風險，且 SoF 未提供 + 奈及利亞高風險 + $50M，綜合最高關注。
- A：30% 受益所有權未識別（R2）是硬缺漏，補齊 UBO＋更新董事證件前不可開戶；開曼非本規則表高風險清單，僅附 informational 備註。

維持「只評分與路由、不作最終決定」，最終由合規／MLRO 簽核。

提醒：out/ 在回合間會被清空，此 kyc_review_pack_2026-06.md 為本回合產物。需要的話我可以把它做成 Excel 審查底稿（逐申請×R1–R7 矩陣＋名單命中表＋路由），或把這份與前述各任務一起 git commit 永久保存。

## 4. 產出 Excel 底稿

> 使用者：執行 Excel

「執行 Excel」= 把 KYC 審查包做成 Excel 底稿（逐申請 × R1–R7 矩陣＋名單命中表＋路由）。

```text
● Write(build_kyc_pack.py)
  ⎿  Wrote 131 lines to build_kyc_pack.py
       1 # -*- coding: utf-8 -*-
       2 """KYC/AML onboarding review workpaper — 2026-06 (rules matrix + screening + routing)."""
       3 import os
       4 os.makedirs("./out", exist_ok=True)
       5 from openpyxl import Workbook
       6 from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
       7 from openpyxl.utils import get_column_letter
       8
       9 BLUEF="0000FF"; BLACKF="000000"
      10 HDR="1F4E79"; SUB="D9E1F2"; OUT="BDD7EE"; INP="F2F2F2"; WHITE="FFFFFF"
     … +121 lines (ctrl+o to expand)
```

```bash
cd "<repo>" && python build_kyc_pack.py 2>&1
```

```text
SAVED ./out/KYC_Review_Workpaper_2026-06.xlsx  sheets: ['Rules Matrix', 'Dashboard', 'Sanctions-PEP Screening', 'Routing']
```

KYC 審查底稿已產出 → ./out/KYC_Review_Workpaper_2026-06.xlsx（4 分頁）

| 分頁 | 內容 |
| --- | --- |
| Rules Matrix | 5 申請 × R1–R7 矩陣；✗缺漏／🔴確認命中／🟡EDD／🟢假命中 顏色標示，含圖例 |
| Dashboard | 風險等級總覽 + 處置建議 + 關鍵觸發，依 🔴/🟡/🟢 上色 |
| Sanctions-PEP Screening | 逐對象「姓名/DOB/國別」三欄比對 → 確認命中 vs 假命中 vs PEP 命中 |
| Routing | 優先序 1–5 的合規/MLRO 動作 + 缺漏命中 |

### 結果（與審查包一致）

- 🔴 B Ivan Petrov — OFAC SDN 三識別碼全中 → 拒絕＋SAR
- 🟡 D Nigeria — PEP＋高風險國＋缺 SoF＋PEP 聲明不實 → 升級 MLRO、補件前不可開戶
- 🟡 A Helios — 30% UBO 未識別＋董事證件過期 → 退補件
- 🟢 C Maria Garcia — 假命中（DOB 1988≠1955、Spain≠Colombia）→ 排除後可核准
- 🟢 E Quiet Brook — 乾淨，可核准

底稿把「確認命中才拒絕、假命中須排除、PEP 走 EDD」的判定邏輯結構化呈現，維持只評分與路由、由合規／MLRO 簽核。
