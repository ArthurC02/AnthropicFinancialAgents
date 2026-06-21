# 💰 估值複核（valuation-reviewer）— 執行紀錄

## 安裝外掛

```text
❯ /plugin install valuation-reviewer@fsi-local
  ⎿  ✓ Installed valuation-reviewer. Run /reload-plugins to apply.
```

## 任務指派

> 使用者：這是 Aurora Growth Fund III 的 GP 估值包 (gp_valuation_package_2026-Q1.md) 和基金條款與部位 (fund_terms_and_positions_2026-Q1.md)。幫我複核 GP 估值是否符合估值政策、算出 NAV 與報酬指標、跑收益分配 waterfall（carry 與各 LP 分配），備一份給 IR/CCO 的 LP 報告草稿。
> (i.e. 參考 ./samples/valuation-reviewer)

新任務：複核 GP 估值、算 NAV/報酬指標、跑 waterfall、備 LP 報告草稿。先讀來源檔。

## 讀取來源檔

```bash
cd "<repo>" && ls samples/valuation-reviewer/ 2>&1
```

```text
fund_terms_and_positions_2026-Q1.md
gp_valuation_package_2026-Q1.md
```

```text
Read 2 files (ctrl+o to expand)
```

四份 policy（P1–P4）、條款、部位都讀到了。先用 Python 算 NAV、IRR/MOIC 與 waterfall（reported vs 政策調整後），確保數字精確。

## 計算 NAV 與 Waterfall

```bash
cd "<repo>" && python - <<'PY'
from datetime import date…
PY
```

```text
NAV reported 350,000,000 | NAV policy-adjusted 325,000,000 (portfolio 305,000,000)

[REPORTED] NAV 350,000,000
… +20 lines (ctrl+o to expand)
```

Waterfall 對得上（carry = 利潤 20%）。但有個關鍵矛盾要查：政策調整後 Net IRR 7.56% < 8% hurdle，卻仍算出 carry——這暗示提供的「優先報酬 35M」可能被低估。我驗算真實 8% 複利門檻。

## 驗算優先報酬門檻

```bash
cd "<repo>" && python - <<'PY'
from datetime import date…
PY
```

```text
FV of contributions @8% to 2026-03: 371,518,001
FV of distribution @8%:            42,379,000
Hurdle balance (cap+pref, net dist): 329,139,002
… +4 lines (ctrl+o to expand)
```

驗算揭露一個重大治理問題：獨立以 8% 複利重算，真實優先報酬約 $69M，而 GP 包提供的是 $35M——這個差異會讓 carry 結論翻盤。政策調整後 Net IRR 7.56% < 8% hurdle，意味 carry 可能根本尚未賺得。我把完整複核寫成 LP 報告草稿。

## 產出 LP 報告草稿

```text
Write(out\LP_Report_Draft_2026-Q1.md)
  ⎿  Wrote 136 lines to out\LP_Report_Draft_2026-Q1.md
      1 # LP 季度報告草稿 — Aurora Growth Fund III, L.P.
      2
      3 **估值日 As-of 2026-03-31（Q1）· USD · 草稿 DRAFT**
      4 > ⚠️  **分送前須 IR ＋ CCO 簽核**；本草稿由估值複核流程產出，含**對 GP 估值包的複核意見**，agent 不對外發送。
      5 來源：`gp_valuation_package_2026-Q1.md`（受複核對象）、`fund_terms_and_positions_2026-Q1.md`（基準）。編製 2026-06-18。
      6
      7 ---
      8
      9 ## 1. 執行摘要 Executive Summary
     … +126 lines (ctrl+o to expand)
```

估值複核完成，LP 報告草稿已輸出至 ./out/LP_Report_Draft_2026-Q1.md。

### 核心發現

**① 估值政策複核（P1–P4）— 2 筆明確違規**

- ❌ Nova Biotech +62%（$25M）：僅憑「管理層估計」、無方法/無觸發事件 → 違反 P2/P3，駁回上調（held 40M）
- ❌ Zephyr Retail：最後更新 2025-03、連續 4 季未複核 → 違反 P1，須立即重新複核
- ✅ Titan（DCF 減損）、Orion（近期輪價）放行；Helios（可比公司）有條件放行（P3 待委員會核准文件）

**② NAV：** GP 報告 350M → 政策調整後 325M（Nova −25M）

**③ 報酬：** TVPI 1.30x→1.22x、Net IRR 10.18%→7.56%、DPI 0.13x

**④ Waterfall（歐式）— carry 三情境**

|          | GP 包 | 政策調整 | 調整＋獨立 8% pref |
| -------- | ----- | -------- | ------------------ |
| GP Carry | $18M  | $13M     | $0                 |

**⑤ 最重大發現（給 CCO）：** GP 包的優先報酬用 $35M，但我獨立以 8% 複利重算約 $69M；且調整後 Net IRR 7.56% < 8% hurdle——意味 carry 可能根本尚未賺得。Nova 違規 + pref 疑被低估，合計把 GP carry 從合理的 ~$0 推高到聲稱的 $13–18M。建議釐清前不認列 carry。

**⑥ 資料缺口：** Fund III 無 LP 名冊，無法算各 LP 分配 → 已 flag IR 提供 commitment register，並附 pro-rata 計算方法。

---

整份草稿含複核表、NAV 橋接、報酬指標、三情境 waterfall、pref 對帳意見、IR/CCO 例外清單與簽核欄。維持「GP 報告值不照單全收、原因不明只標示不斷定」，並註明須 IR＋CCO 簽核才可分送。

需要的話我可以把這份做成 Excel 複核底稿（估值表＋NAV 橋接＋waterfall 三情境＋pref 重算，活公式），或等你提供 LP 名冊後補各 LP 分配表。

## 產出 Excel 覆核底稿

> 使用者：做成覆核底稿

做成 Excel 覆核底稿（活公式 + 跨頁連結）。

```text
Write(build_val_review.py)
  ⎿  Wrote 192 lines to build_val_review.py
      1 # -*- coding: utf-8 -*-
      2 """Aurora Growth Fund III — Q1 2026 valuation review workpaper (live formulas)."""
      3 import os
      4 os.makedirs("./out", exist_ok=True)
      5 from openpyxl import Workbook
      6 from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
      7 from openpyxl.comments import Comment
      8 from openpyxl.utils import get_column_letter
      9 import datetime
     … +182 lines (ctrl+o to expand)
```

```bash
cd "<repo>" && python build_val_review.py 2>&1 && python - <<'PY'
# validate waterfall formulas mirror (3 scenarios)…
PY
```

```text
SAVED ./out/Fund_III_Valuation_Review_2026-Q1.xlsx  sheets: ['NAV Bridge', 'Valuation Review', 'Returns', 'Pref Recompute', 'Waterfall']
A: carry 18,000,000 | LP 372,000,000 | check 390,000,000 vs 390,000,000
B: carry 13,000,000 | LP 352,000,000 | check 365,000,000 vs 365,000,000
C: carry 0 | LP 365,000,000 | check 365,000,000 vs 365,000,000
```

覆核底稿已輸出至 ./out/Fund_III_Valuation_Review_2026-Q1.xlsx，waterfall 三情境驗算全部 tie-out ✓

### 5 個分頁（活公式 + 跨頁連結）

| 分頁             | 內容                                                                                                |
| ---------------- | --------------------------------------------------------------------------------------------------- |
| NAV Bridge       | GP 報告 350M →（Nova −25M，連結估值表）→ 政策調整 325M，含組成檢查                                   |
| Valuation Review | 5 家逐筆：成本/上季/GP報告/方法/P1–P4 檢核/判定/調整，違規紅底；調整後 FV=公式                        |
| Returns          | TVPI/DPI/RVPI 公式；現金流表 + XIRR() 算 Reported/Adjusted Net IRR；自動標 <8% hurdle                |
| Pref Recompute   | 用 YEARFRAC + 8% 複利獨立重算優先報酬 ~$69M，對照 GP 提供 $35M，差異紅底                             |
| Waterfall        | A/B/C 三情境，逐層 MIN/MAX/IF（自動處理部分 pref、無 catch-up），carry 與 LP+GP=總價值檢查           |

底稿驗算結果（與公式一致）：

- GP Carry：情境 A $18M / B $13M / C $0
- 三情境 LP+GP 皆 = 總價值 ✓
- 調整後 Net IRR < 8% → Returns 分頁自動標示「❌ 低於 hurdle」

底稿全是活公式：CCO 改任一輸入（例如 Pref Recompute 的利率、估值表的 Nova 調整、或某部位 FV），NAV、報酬、三情境 carry 會連動重算。本機無 LibreOffice，故以獨立 Python 重算驗證公式邏輯（XIRR/YEARFRAC 由 Excel 開啟時計算）。

這份估值複核到此完成 ✅ — 維持「GP 值不照單全收、pref 差異標示為待 CCO 對帳、carry 釐清前不認列」。需要我等你提供 LP 名冊後補各 LP 分配表，或把 markdown 報告與這份 xlsx 整成一個交付索引嗎？
