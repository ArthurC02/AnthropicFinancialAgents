# ⚖️ 總帳對帳（gl-reconciler）— 執行紀錄

## 1. 安裝外掛

```text
❯ /plugin install gl-reconciler@fsi-local
  ⎿  ✓ Installed gl-reconciler. Run /reload-plugins to apply.
```

## 2. GL ↔ 子帳對帳任務

> 使用者：這是 Aurora Growth Fund III 的總帳 (gl_balances_2026-04-30.md)、子帳 (subledger_holdings_2026-04-30.md)，和對帳參考 (recon_reference_2026-04-30.md)。幫我逐筆比對找差異、追根因、做獨立複核濾掉誤報，產出例外報告。

GL ↔ 子帳對帳。先讀三份來源檔。

```text
Read 3 files (ctrl+o to expand)
```

三份都讀齊（GL 交易日基礎、子帳交割日基礎、含容差/未交割/匯率/分類佐證）。我逐筆比對、追根因、用佐證做獨立複核濾掉誤報，產出例外報告並存到 ./out/。

```text
● Write(out\gl_recon_exceptions_2026-04-30.md)
  ⎿  Wrote 80 lines to out\gl_recon_exceptions_2026-04-30.md
      1 # GL ↔ 子帳 對帳例外報告 — Aurora Growth Fund III
      2
      3 **對帳日 2026-04-30 · USD**
      4 GL 基礎：**交易日 Trade-date** ｜ 子帳基礎：**交割日 Settlement-date**（custody，視為外來資料）
      5 來源：`gl_balances`、`subledger_holdings`、`recon_reference`。編製 2026-06-18。
      6
      7 ---
      8
      9 ## 0. 對帳總覽
     … +74 lines (ctrl+o to expand)
```

對帳完成，例外報告已存至 `./out/gl_recon_exceptions_2026-04-30.md`。

結果：9 筆 = 3 一致 / 3 誤報（濾除）/ 3 真實 break

### 🟡 濾掉的誤報（附佐證）

- **EQ-SPY** — 僅資產類別標籤不同（Equity vs Funds/ETF），數量/市值一致 → 重分類
- **FI-BUND** — MV 差 +$300，相對 0.003% < 0.05% FX 容差 → 匯率進位
- **FI-GB123** — −$500,000 = 未交割買單 TRD-9001（交易日 4/29、交割 5/2）；GL 交易日已計、子帳交割日未計 → 時間差，5/2 後自然消除

### 🔴 真實例外（升級，淨額 $1,350,000）

| 優先 | 項目 | 金額 | 根因 |
|------|------|------|------|
| 1 | CA-USD 現金 | $600,000 | 保管較 GL 少，查無佐證 → 立即對銀行流水 |
| 2 | FI-XYZ 公司債 | $1,000,000 | GL 多 1,000,000 面額，疑已處分/贖回 GL 未沖 |
| 3 | EQ-VRT | $250,000 | 子帳多 2,500 股，疑買單 GL 未入帳 |

### 關鍵判讀

- 總差異 $1,849,700 = 已解釋 $499,700（時間差+FX）+ 真實 $1,350,000 ✓ 對得上
- 真實 break 多指向 GL 側落後/漏記（XYZ、VRT），建議查 GL 過帳佇列
- 方向驗證：GB123 的交割日時間差會使保管現金「偏高」，與現金實際「偏低 $600k」相反 → 證明現金缺口是獨立真實 break，非該時間差所致
- 現金 $600k 列最高優先（金額大、無佐證）；原因不明只標示升級、不臆測

報告含逐筆比對表、誤報佐證、真實例外根因追蹤、根因分布與升級清單。

需要的話我可以把這份做成 Excel 對帳底稿（逐筆 match＋差異拆解＋誤報濾除＋升級清單，含活公式與 tie-out 檢查），或對這 7 個 FSI plugin 的整批產出做一份交付索引。

## 3. 執行：Excel 對帳底稿 + 交付索引

> 使用者：執行

「執行」= 做 Excel 對帳底稿，並對目前實存的 FSI 產出做交付索引。先建對帳底稿。

```text
● Write(build_gl_recon.py)
  ⎿  Wrote 129 lines to build_gl_recon.py
       1 # -*- coding: utf-8 -*-
       2 """Aurora Growth Fund III — GL↔Subledger reconciliation workpaper (live formulas)."""
       3 import os
       4 os.makedirs("./out", exist_ok=True)
       5 from openpyxl import Workbook
       6 from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
       7 from openpyxl.utils import get_column_letter
       8
       9 BLUEF="0000FF"; BLACKF="000000"; GREENF="008000"
      10 HDR="1F4E79"; SUB="D9E1F2"; OUT="BDD7EE"; INP="F2F2F2"; WHITE="FFFFFF"; WARN="FCE4D6"; OK="E2EFDA"; AMB="FFF2CC"
     … +119 lines (ctrl+o to expand)
```

```bash
cd "<repo>" && python build_gl_recon.py 2>&1 && python - <<'PY'
# validate tie-out…
PY
```

```text
SAVED ./out/GL_Recon_Workpaper_2026-04-30.xlsx  sheets: ['Break Analysis', 'Recon', 'Escalation']
total diff 1,849,700 | real 1,350,000 | explained 499,700 | real+expl 1,849,700 -> tie OK
```

對帳底稿完成，tie-out 通過 ✓。現在做交付索引——先確認 out/ 目前實存哪些檔案（避免索引到已被清掉的）。

```bash
cd "<repo>" && ls -la out/ | awk '{print $5, $9}' && echo "--- charts ---" && ls out/charts 2>/dev/null
```

```text
Error: Exit code 2

0 .
0 ..
4925 gl_recon_exceptions_2026-04-30.md
9697 GL_Recon_Workpaper_2026-04-30.xlsx
--- charts ---
```

out/ 又被清空了——只剩這回合剛建的 2 個 GL 對帳檔。先前各回合的產出（VRT、估值複核、LP 報告、結帳包等）再次消失。讓我確認腳本狀態：

```bash
cd "<repo>" && echo "=== build scripts ===" && ls build_*.py 2>/dev/null | awk '{print $NF}'; echo "=== git status (untracked…"
```

```text
=== build scripts ===
build_gl_recon.py
=== git status (untracked out) ===
… +5 lines (ctrl+o to expand)
```

out/ 在回合間被清空，只有當回合檔案留存——先前各任務的產出都已不在。因此「索引到實體檔案」會失真。我改做一份誠實的 session 交付索引：記錄全部任務與產出、並標明目前持久化狀態與重生路徑。

```text
● Write(out\DELIVERY_INDEX.md)
  ⎿  Wrote 55 lines to out\DELIVERY_INDEX.md
       1 # FSI 交付索引 Delivery Index（本 session）
       2
       3 > ⚠️  **重要：`out/` 在回合之間會被清空**，僅保留「當回合」產生的檔案。
       4 > 因此下表多數先前產出**目前已不在磁碟**，但**建構腳本邏輯與資料都在對話記錄中，可即時重生**。
       5 > 若要永久保存：請我**git add/commit** 這些檔案，或改寫到不被清理的位置（如 `outputs/`）。
       6 > 編製 2026-06-18。
       7
       8 ---
       9
      10 ## 目前實體存在於 `out/`（本回合）
     … +45 lines (ctrl+o to expand)
```

## 4. 完成

兩項都執行了。

① GL 對帳底稿 ✅ `out/GL_Recon_Workpaper_2026-04-30.xlsx`（tie-out 通過）

- **Recon** — 9 筆逐筆比對，Category 分類（藍字可改），真實 break/已解釋欄由公式自動拆解，含 2 個 tie-out 檢查
- **Break Analysis** — 總差異 $1,849,700 = 已解釋 $499,700 + 真實 $1,350,000，跨頁連結 + ✓ 檢查
- **Escalation** — 3 筆真實 break 升級清單 + GB123 監控
