# ⚖️ 總帳對帳（gl-reconciler）— 筆記 / 答案卡（MCP 版）

> 這份對照「mock-mcp 埋了哪些雷」與「這次 MCP 跑下來有沒有正確處理」。資料全是 mock / dev。
> 跟 `fileBased/` 版的差別:那版的真假差異是寫在三份 `samples/*.md`;這版是**即時從 `internal-gl` + `subledger` 兩個 MCP server 拉回來**,埋雷的定義寫在 `mock-mcp/internal-gl/README.md` 和 `mock-mcp/subledger/README.md` 的「Planted for testing」。

## 這支的考點

`gl-reconciler` 的看家本領是它的 **critic(對抗式獨立複核)**:能不能**留住真差異、濾掉假差異**。
對帳最常見的毛病是誤報一堆淹沒真問題(over-report),但**漏報(under-report)更危險** —— 把真 break 放過會污染後面的結帳與報表。

## 資料來源(MCP 工具呼叫)

| # | server | tool | args | 用途 | 落地 |
|---|---|---|---|---|---|
| 1 | internal-gl | `list_entities` | — | 確認合法 fund / as_of | `mcp_pulls/01_gl_list_entities.json` |
| 2 | internal-gl | `get_gl_positions` | fund, as_of | GL 側部位(對帳一邊) | `mcp_pulls/02_gl_positions.json` |
| 3 | subledger | `get_subledger_holdings` | fund, as_of | custody 側部位(對帳另一邊,外來) | `mcp_pulls/03_subledger_holdings.json` |
| 4 | subledger | `get_pending_settlements` | fund, as_of | 未交割清單 → 判時間差 | `mcp_pulls/04_pending_settlements.json` |
| 5 | subledger | `get_fx_rates` | as_of | GL vs custody 匯率 → 判 FX 進位 | `mcp_pulls/05_fx_rates.json` |
| 6 | subledger | `get_tolerance_policy` | — | 容差門檻 | `mcp_pulls/06_tolerance_policy.json` |

> 6 個工具呼叫全 `ok=true`,**零失敗**。GL 總計 84,500,000 / 子帳總計 82,650,300,皆取自 server 回傳的 `total_mv_usd`,未重算。

## 🔑 答案卡（總差異 GL−Sub = 1,849,700,拆成 6 筆有差 + 3 筆一致）

critic 的考點:留住「真差異」3 筆、濾掉「假差異」3 筆。

### ✅ 真差異（critic 應「留」並升級）——合計 +1,350,000

| 項目 | 金額 | 說明 | MCP 佐證 |
|---|---|---|---|
| EQ-VRT 股票 | −250,000 | 子帳 52,500 股 > GL 50,000 股,差 2,500 股;`get_pending_settlements`「沒有」這筆 → 漏記/系統落差,真 | 不在未交割清單 |
| FI-XYZ 公司債 | +1,000,000 | GL 20M 面額 > 子帳 19M,差 100 萬;已交割賣出但 GL 未沖 → 系統落差,真 | 不在未交割清單 |
| CA-USD 現金 | +600,000 | GL 3.0M > 子帳 2.4M,查無佐證 → 不明(unknown),須升級調查,真 | 非 FX(USD)、不在未交割清單 |

### ❌ 假差異（critic 應「濾掉/標 benign」,不可當錯誤升級）——合計 +499,700

| 項目 | 金額 | 說明 | MCP 佐證 |
|---|---|---|---|
| FI-GB123 公債 | +500,000 | TRD-9001:4/29 買、5/2 交割 → 時間差(交易日 vs 交割日),會自然消除 | `get_pending_settlements` TRD-9001 |
| FI-BUND (EUR) | −300 | GL 1.08000 vs custody 1.08004,差 0.0037% → 在 FX 容差 0.05% 內,進位非差異 | `get_fx_rates` + `get_tolerance_policy` |
| EQ-SPY ETF | 0 | 同證券同數同市值,只是 Equity vs Funds/ETF → 重分類,淨額為 0,非差異 | `asset_class` 欄不同、qty/MV 一致 |

## 🎯 埋雷對照表（mock-mcp README 的 Planted vs 這次處理結果）

`mock-mcp` 在兩個 server 的 CSV 裡刻意埋了 6 筆 GL≠custody。逐筆驗收:

| 埋的雷(README) | GL | Custody | 正解 | 這次判定 | 對? |
|---|---:|---:|---|---|:--:|
| **EQ-VRT qty** | 50,000 | 52,500 | **真 break**(不在未交割) | 🔴 REAL,留+升級,根因=GL 漏記買單 | ✅ |
| **FI-XYZ face** | 20,000,000 | 19,000,000 | **真 break**(系統落差/未記賣出) | 🔴 REAL,留+升級,根因=GL 未沖處分 | ✅ |
| **CA-USD cash** | 3,000,000 | 2,400,000 | **真 break**(查無佐證) | 🔴 REAL,留+升級,根因=unknown,不臆測 | ✅ |
| **FI-GB123 face** | 15,500,000 | 15,000,000 | **時間差**(TRD-9001 5/2 交割) | 🟡 FP-Timing,濾除+監控 | ✅ |
| **FI-BUND MV** | 9,000,000 | 9,000,300 | **FX 進位**(0.05% 內) | 🟡 FP-FX,濾除 | ✅ |
| **EQ-SPY class** | Equity | Funds/ETF | **重分類**(同 qty/MV) | 🟡 FP-Reclass,濾除+建議對應主檔 | ✅ |

**結論:3 真 3 假,六筆全中。真差異一筆沒漏(無 under-report),假差異一筆沒誤升(無 over-report)。**

> 註:`internal-gl/README.md` 把 EQ-SPY 重分類也列在它那張表(共列 4 筆),`subledger/README.md` 列完整 6 筆。本任務題目定義為「3 真 + 3 假」,以 subledger 那張完整表為準,六筆全數對照通過。

## ⚠️ 這次跑出來的真實插曲(critic 的價值現場)

第一版自動分類器**把 CA-USD 誤判成 FX 進位** → 那會變成**漏報一筆真 break(under-report)**,是最嚴重的扣分項。
原因:CA-USD 現金兩邊 `qty_face` 都空白(0)、只有 MV 差,程式的「qty 相等且 MV 有差 → 查 FX 容差」分支,誤用了表上那個剛好在容差內的 EUR/USD pair。
critic 反查抓到兩個破綻:① CA-USD 是 **USD** 現金,根本沒有外幣換算;② 它**自身**相對差 600,000/3,000,000 = **20%**,遠超 0.05%。
修正規則:FX 進位只在「該部位**自身**相對差也在容差內」時成立。修正後 tie-out 從 (real 750k / explained 1,099.7k) 變回正確的 **(real 1,350k / explained 499.7k)**。

> 教訓正中這支 agent 的設計初衷:對帳容易誤報,但**漏報更致命**,所以非要一層獨立 critic 拿可信來源重算不可 —— 它擋下的正是「用一個容差規則打發掉一筆真 break」的陷阱。

## 評分重點(self-check)

```text
🔴 critic 兩邊都做對?
   ☑ 真差異 3 筆(VRT/XYZ/Cash)全留下、分類正確(漏記/系統落差/不明)
   ☑ 假差異 3 筆(GB123/Bund/SPY)全濾掉,沒當錯誤升級

🔴 過度升報(over-report)? ☑ 無 —— GB123/Bund/SPY 都濾掉了
🔴 漏報(under-report)?    ☑ 無 —— 一度誤判 CA-USD,critic 修正,最終一筆沒漏

🟡 追根因有沒有用佐證?     ☑ 逐筆引用 get_pending_settlements / get_fx_rates / get_tolerance_policy
🟡 例外報告可簽核 + 護欄?  ☑ 升級清單 + 明寫「agent 永不過帳、控制員簽核」
🟢 加分:SPY 雖淨額 0,仍建議建 GL↔custody 分類對應主檔 ☑
🟢 加分:方向性對抗檢查 —— GB123 時間差使子帳現金偏高,與現金實況偏低相反,
        故不能用來解釋現金缺口 ☑
```

## 數字勾稽

```text
✓ 總差異 1,849,700 = 84,500,000(GL) − 82,650,300(子帳)   [兩數皆取自 MCP total_mv_usd]
✓ 真實 1,350,000 = −250,000(VRT) + 1,000,000(XYZ) + 600,000(Cash)
✓ 已解釋 499,700 = 500,000(GB123) − 300(Bund) + 0(SPY)
✓ 1,350,000 + 499,700 = 1,849,700                         [xlsx tie-out: OK]
✓ VRT 純數量差:2,500 股 × $100 = $250,000(單價兩邊一致)
✓ Bund FX:|1.08004−1.08000|/1.08000 = 0.0037% < 0.05% 容差 → 正確濾除
✓ GB123:TRD-9001 買 500,000、5/2 交割 → 正確認定時間差
```

## 結論

```text
🏆 gl-reconciler(MCP 版)驗收:通過
   6 個 MCP 工具呼叫全成功、零失敗;埋的 3 真 3 假六筆全中,
   零誤報、零漏報(CA-USD 一度誤判,由 critic 反查修正)。
   守住護欄:只產例外報告、永不過帳、等控制員簽核。
   後台最複雜的一支(2 個 MCP + 扇出 + 獨立 critic),在真實 MCP 上完整重現。
```
