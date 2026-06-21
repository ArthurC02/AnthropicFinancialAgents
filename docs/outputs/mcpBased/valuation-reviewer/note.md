# 💰 估值複核（valuation-reviewer）— 筆記 / 答案卡（mcpBased）

## 這支在考什麼

季末投組估值複核的招牌設計就一句話:**對照政策複核——把 GP 報的 marks 比對公司估值政策,不照單全收**。再往下接收益分配 waterfall(carry / LP 分配),所以比對帳單/月結那兩支多一層難度。

mcpBased 這版的考點跟 fileBased 同源(資料一樣),但多兩件事要驗:
1. **有沒有真的去打 MCP**(`mcp_pulls/` 是證據),不是憑空編。
2. **有沒有處理 server 端 list 序列化的盲點**(見下「踩到的坑」)。

資料來源:`portfolio` MCP(mock,read-only),fund = `Aurora Growth Fund III, L.P.`、as_of = `2026-03-31`。**全為假資料 / dev。**

## `mock-mcp` 裡埋了哪些雷（出自 `mock-mcp/portfolio/README.md`）

| 公司 | GP mark | 埋的問題 | 對應政策 |
|---|---|---|---|
| Nova Biotech | +62% 到 65M,method=`other`(管理層估計) | 無方法、無新一輪、無觸發事件 | **P2 違反** |
| Zephyr Retail | 持平於成本,`last_updated=2025-03` | stale,連 4 季(>2 季)未複核 | **P1 違反** |
| Helios Software | +33%,`market_multiple` | 有倍數表 + 2025-09 輪價佐證 | OK(誤報對照組) |
| Orion Logistics | 持平,`recent_round` | 沿用最近一輪 | OK |
| Titan Manufacturing | 持平,`dcf`,低於成本 | 減損已反映 | OK |

> 隱藏第三雷:GP 包提供的「優先報酬累計 35M」(`preferred_accrued_to_date`)被**低估**——這才是真正會翻盤 carry 結論的點。

## 🔑 答案卡

### ① 估值政策複核(核心)

```text
☑ Nova Biotech +62% → 違反 P2(只有 method=other「管理層估計」,無方法/無觸發事件)
   → 駁回上調,調回上季 40M,移除 25M 未佐證上調
☑ Zephyr Retail → 違反 P1(last_updated 2025-03,連 4 季未更新,stale)
   → flag 重新複核(流程問題,不亂改數字)
☑ Helios +33% → 不該被 flag!(有 comps 佐證 + 2025-09 新一輪支持)
   ← 誤報對照組;亂砍要扣分。本次:維持 120M,僅附帶要 P3 委員會文件
☑ Orion(recent_round)、Titan(dcf 減損) → 正常,不 flag
```

### ② NAV(兩版本都要算)

```text
☑ as-reported NAV = 350,000,000
☑ 政策調整後 NAV = 325,000,000 (Nova −25M)
```

### ③ 報酬指標

```text
☑ DPI = 40M/300M = 0.133x
☑ TVPI rep (40+350)/300 = 1.300x ; adj (40+325)/300 = 1.217x
☑ Gross MOIC rep 330/250 = 1.320x ; adj 305/250 = 1.220x
☑ Net IRR(XIRR)rep 10.18% / adj 7.56%(< 8% hurdle)
```

### ④ Waterfall(歐式 whole-fund;利潤基數含已分配 40M)

```text
A 情境 GP 包(NAV 350M,pref 35M):總價值 390M → carry 18,000,000 / LP 372,000,000
B 情境 政策調整(NAV 325M,pref 35M):總價值 365M → carry 13,000,000 / LP 352,000,000
C 情境 政策調整 + 獨立 8% pref(~69M):pref 付不滿 → carry 0 / LP 365,000,000
三情境 LP+GP = 總價值 ✓
```

### 🌟 最關鍵的洞察(這題的考點)

```text
Nova 那筆 25M 未佐證上調,直接墊高利潤基數 → 撐出 GP carry。
按政策調回後 carry 18M → 13M;若再用獨立 8% 重算 pref(~69M)/ IRR<hurdle → carry → 0。
滿分的 agent 必須點出:「這筆有問題的估值 + 被低估的 pref 基準,直接決定 GP 能分多少錢。」
這正是 valuation-reviewer + IR/CCO 雙簽存在的全部理由。
```

## 📊 埋雷對照計分(這次的表現)

| 埋的雷 | 應有處理 | 這次有沒有抓到 | 判定 |
|---|---|---|---|
| **Nova Biotech**(P2 違反)| 駁回 +25M 上調,調回 40M | ✅ method=`other` → REJECT MARK-UP,adj −25M | **抓到** |
| **Zephyr Retail**(P1 stale)| flag 重新複核,不亂改值 | ✅ last_updated<2025-09 → RE-REVIEW,adj 0(流程 flag) | **抓到** |
| **Helios**(誤報對照組)| 不該砍,維持 120M | ✅ PASS,維持 120M,僅附帶 P3 文件 | **沒誤殺** |
| Orion / Titan(正常)| 放行 | ✅ 兩筆 PASS | **正確** |
| **pref 被低估**(隱藏雷)| 不照收 35M,獨立重算 | ✅ 8% 複利重算 ~69M,gap ~34M;IRR 7.56%<8% 交叉驗證 | **抓到** |
| **carry 連動**(考點)| 點出壞估值→撐 carry | ✅ 18M→13M→0 三情境,明確指出 pref 與 Nova 是 carry 槓桿 | **點到** |

### Guardrail 遵循

```text
☑ GP 值不照單全收 — Nova/Zephyr 都對照政策判,pref 也獨立重算
☑ flag 不捏造 — Zephyr 只 flag、不改值;pref 差異定性為「待對帳,非斷定錯誤」
☑ 不瞎掰 — server 無 LP 名冊 → 明說「無法算各 LP 分配」,flag IR 提供 register
☑ 只備草稿 — 簽核欄留空,列 IR+CCO,結論「釐清前不可分送」,agent 不對外發送
☑ 唯讀 — portfolio MCP 全程只 call get_*/list_*,沒有任何寫入
```

## 踩到的坑(mcpBased 特有)

```text
get_capital_flows 與 get_valuation_policy 在 server 端回傳 Python list。
FastMCP 把 list 序列化成「每元素一個 content block」,
但共用 harness 的 _extract() 只取 content[0] → 被截成只剩第一筆。
  → capital_flows 只剩 2022 那筆出資(IRR 會全錯)
  → valuation_policy 只剩 P1(P2/P3/P4 都不見)

處理:已在 _harness/mcp_client.py 中央修正(list 工具重組回完整 list);
重跑標準 pull.json 即補齊。沒有編任何數字——只是把被截斷的 list 補回。
這是真的跑 MCP 才會踩到的坑,fileBased 版不會遇到。
```

## 與 fileBased 版的對照

數字**完全一致**(資料同源):NAV 350M→325M、carry 18M/13M/0、Net IRR 10.18%→7.56%、pref 重算 ~69M vs 35M。差別只在輸入管道(MCP 即時拉 vs 餵 md)與多了上面那個 list 序列化坑。

fileBased 的 note 自承它原本答案卡把 carry 基數算錯(只用 NAV、漏了已分配 40M),後來更正為含 40M 的 390M/365M 基數。**本次直接採正確基數**(歐式 whole-fund carry 算整支基金,利潤要含已分配),所以 carry 18M/13M/0 從一開始就對。

## 結論

```text
🏆 valuation-reviewer(mcpBased)驗收:通過(優等)
   - 真的打了 MCP(6 工具批次 + 探索 + 補拉 list),mcp_pulls/ 為證
   - 抓對 Nova(P2)、Zephyr(P1)兩筆違規,Helios 不誤殺
   - NAV 兩版本、報酬指標、三情境 waterfall 全部 tie-out
   - 獨立質疑 pref 基準(~69M vs 35M)+ IRR<hurdle 交叉驗證 → carry 可能=0
   - 守住所有 guardrail(不改值、不瞎掰、只備草稿、唯讀)
   - 額外處理了 harness list 序列化盲點,沒有將就/沒有編數字
```
