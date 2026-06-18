# 📅 月底結帳（month-end-closer）— 執行紀錄

## 安裝外掛

```text
❯ /plugin install month-end-closer@fsi-local
  ⎿  ✓ Installed month-end-closer. Run /reload-plugins to apply.
```

## 使用者請求

> 使用者：這是 Aurora Capital Management LLC 的 2026-04 試算表 (trial_balance_2026-04.md) 和待估列應計清單 (accruals_support_2026-04.md)。幫我跑月結：估列應計、做應付費用結轉、對變動大的科目寫差異說明，組裝成結帳包。(i.e. 參考 ./samples/month-end-closer 裡面的檔案)

## 讀取來源檔

月結任務。先讀這兩份來源檔。

```bash
cd "C:/Users/a8022/Desktop/financial-services" && ls samples/month-end-closer/ 2>&1
```

```text
accruals_support_2026-04.md
trial_balance_2026-04.md
```

```text
Read 2 files (ctrl+o to expand)
```

三份來源齊全。這是月結：估列應計、做 2100 結轉、寫差異說明、組裝結帳包。載入應計排程 skill 對齊分錄格式。

```text
Skill(month-end-closer:accrual-schedule)
  ⎿  Successfully loaded skill
```

## 組裝結帳包（Markdown）

全部讀齊。我已完成估列、結轉與差異分析，組裝成結帳包，輸出到 ./out/。先寫檔。

```text
Write(out\close_package_2026-04.md)
  ⎿  Wrote 119 lines to out\close_package_2026-04.md
      1 # 月結結帳包 Month-End Close Package
      2
      3 **Aurora Capital Management LLC** · 期間 2026-04 · 幣別 USD
      4 來源：`samples/month-end-closer/trial_balance_2026-04.md`、`accruals_support_2026-04.md`
      5 狀態：**草稿，待 controller 核准**（分錄為 draft，尚未過帳）· 編製 2026-06-18
      6
      7 ---
      8
      9 ## 0. 結帳摘要 Close Summary
     … +109 lines (ctrl+o to expand)
```

月結完成，結帳包已輸出至 ./out/close_package_2026-04.md。

### 重點

**① 估列應計（3 筆，共 +$275,000，草稿待核准）**

- A1 IT 服務 $75k（自動沖回）、A2 分紅 $100k、A3 審計 $100k — 皆 Dr 費用 / Cr 2100 應付費用

**② 應付費用 (2100) 結轉** — 1,200,000 −200,000 +275,000 = 1,275,000，foot check ✓

**③ 平衡與損益**

- Post-close 試算表 Dr=Cr=21,655,000 ✓
- 應計後 YTD 淨利 +200,000 → −75,000（翻為小額虧損）

需要的話我可以把整包輸出成 Excel 結帳工作底稿（TB＋分錄＋結轉＋flux 分頁，含活公式與 foot check），方便 controller 覆核。要嗎？

## 執行：產出 Excel 工作底稿

> 使用者：執行

「執行」= 把結帳包做成 Excel 工作底稿（活公式 + foot check）。

```text
Write(build_close_pack.py)
  ⎿  Wrote 170 lines to build_close_pack.py
       1 # -*- coding: utf-8 -*-
       2 """Aurora Capital Management LLC — 2026-04 month-end close workbook (live formulas)."""
       3 import os
       4 os.makedirs("./out", exist_ok=True)
       5 from openpyxl import Workbook
       6 from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
       7 from openpyxl.utils import get_column_letter
       8
       9 BLUEF="0000FF"; BLACKF="000000"; GREENF="008000"
      10 HDR="1F4E79"; SUB="D9E1F2"; OUT="BDD7EE"; INP="F2F2F2"; WHITE="FFFFFF"; WARN="FCE4D6"; OK="E2EFDA"
     … +160 lines (ctrl+o to expand)
```

```bash
cd "C:/Users/a8022/Desktop/financial-services" && python build_close_pack.py 2>&1 && python - <<'PY'
# validate key foot checks…
```

```text
SAVED ./out/Close_Package_2026-04.xlsx  sheets: ['Accruals & JEs', 'Trial Balance', 'Roll-forward 2100', 'Variance']
Post-close Dr=Cr = 21,655,000 (expect 21,655,000)
YTD net income post = -75,000 (expect -75,000)
… +4 lines (ctrl+o to expand)
```

結帳工作底稿已輸出至 ./out/Close_Package_2026-04.xlsx，所有 foot check 驗算通過 ✓

### 4 個分頁（活公式）

| 分頁 | 內容 |
| --- | --- |
| Accruals & JEs | 應計排程 3 筆 + 草稿分錄，含 Dr=Cr 檢查（合計 275,000） |
| Trial Balance | 上月/本月 pre/應計調整/結帳後（=公式），Dr/Cr 拆分平衡檢查、YTD 淨利（pre vs post） |
| Roll-forward 2100 | 1,200,000 −200,000 +275,000 = 1,275,000，內建 IF foot check + 與 TB 一致性連結 |
| Variance | 連結 TB 計算「當月 vs 月跑率」，>5% 異常自動標示，⚠ 三項紅底 |

### 驗算結果（與底稿公式一致）

- 結帳後試算表 Dr = Cr = 21,655,000 ✓
- 應付費用 2100 期末 = 1,275,000 ✓
- YTD 淨利（post）= −75,000 ✓
- 異常：專業服務費 +237%、差旅 +300%、折舊新增（跑率 0）→ 皆已標示需查

底稿是活公式 + 跨頁連結（綠字），controller 改任一輸入（應計金額、期初餘額等）會自動重算並重跑 foot check。本機無 LibreOffice，故以獨立 Python 重算驗證公式邏輯；分錄維持草稿未過帳狀態。

這份月結到此完成 ✅ — 需要我把 markdown 結帳包與這份 xlsx 一起整理一個交付索引，還是有其他實體要結？
