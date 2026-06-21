# 🎯 投行提案(pitch-agent)— 執行紀錄(mcpBased)

> 這版跟 fileBased 的差別:輸入不是人工餵的 `samples/*.md`,而是**真的去打 mock MCP**(capiq + daloopa,stdio,經 `_harness/mcp_client.py`),把回傳存進 `mcp_pulls/` 當證據,再用 pulled 數字建估值與提案。全部為 mock / dev 資料。

## 安裝與初始指令

```text
❯ /plugin install pitch-agent@fsi-local
  ⎿  ✓ Installed pitch-agent. Run /reload-plugins to apply.
```

> 使用者:對 Vertiv(VRT)做一份併購提案初稿。這次用 **mcpBased 跑法** — 從 capiq + daloopa 兩支 mock MCP 即時拉資料,建估值三角驗證(comps / DCF / LBO+IRR)+ 足球場 + 提案 narrative,所有數字必須來自 pulled JSON。

我裝了 pitch-agent。框架假設(初稿):以「潛在收購方評估收購 VRT」視角;Comps/DCF 為策略買方、LBO 為財務買方(PE);示意控制報價 $400(對現價 +25%)。先去打 MCP 拿到合法 ticker/欄位,再建模。

## 一、探索與拉資料(真的打 MCP)

先用 harness 批次模式叫起 capiq server(stdio),打 4 個工具:

```bash
cd ".../mcpBased/_harness" && PYTHONUTF8=1 python mcp_client.py \
  --spec ".../mcpBased/pitch/scripts/pull_capiq.json" 2>/dev/null
```

```text
server: capiq  tools: [get_comps, get_quote, get_market_events, get_estimates]
  get_comps              ok  -> 01_capiq_get_comps.json
  get_quote (VRT)        ok  -> 02_capiq_get_quote_VRT.json
  get_estimates (VRT)    ok  -> 03_capiq_get_estimates_VRT.json
  get_market_events(VRT) ok  -> 04_capiq_get_market_events_VRT.json
```

接著叫起 daloopa server,先 `list_coverage` 確認合法參數,再逐個 statement 拉 VRT 線項:

```bash
cd ".../mcpBased/_harness" && PYTHONUTF8=1 python mcp_client.py \
  --spec ".../mcpBased/pitch/scripts/pull_daloopa.json" 2>/dev/null
```

```text
server: daloopa  tools: [list_coverage, get_line_items]
  list_coverage                          ok  -> 05_daloopa_list_coverage.json
  get_line_items (VRT, all)              ok  -> 06_daloopa_get_line_items_VRT_all.json
  get_line_items (VRT/FY2025/segment)    ok  -> 07_daloopa_VRT_segment_revenue.json
  get_line_items (VRT/FY2025/product)    ok  -> 08_daloopa_VRT_product_revenue.json
  get_line_items (VRT/FY2025/income)     ok  -> 09_daloopa_VRT_income_statement.json
  get_line_items (VRT/FY2025/balance)    ok  -> 10_daloopa_VRT_balance_sheet.json
```

> 兩支 server 各保留一份工具清單:`_tools_capiq.json`、`_tools_daloopa.json`(harness 預設只寫 `_tools.json`,會被後跑的 server 蓋掉,故各自另存一份)。**10 次呼叫全部成功,0 失敗。**

### 拿回來的關鍵數字(pulled)

```text
capiq get_quote(VRT)     : price $320 | mktcap $122bn | 52wk $80–$340  → 隱含股數 0.381bn
capiq get_comps(...)     : VRT EV/EBITDA 51x(全組最高);同業中位 ~20x;EV/Rev caveat(不跨模式比)
capiq get_estimates(VRT) : FY26E 營收 $10.9bn / EBITDA 利潤率 22% / EPS $3.6 ; FY27E 營收 $13.5bn / 23%
capiq get_market_events  : 2026-06-17「估值升至 ~51x;backlog>$15B;NVIDIA 參考設計」
daloopa VRT FY2025       : 營收 $8.0bn / 營業利益 $1.5bn ; backlog $15bn
   segment  : Americas 4.6 / APAC 1.8 / EMEA 1.6   (= 8.0 ✓)
   product  : Power 3.0 / Thermal 2.5 / Rack 1.5 / Services 1.0  (= 8.0 ✓)
   balance  : 只有 Backlog,**沒有任何負債科目**
```

## 二、判讀(agent 怎麼想)

兩個一拉就跳出來的點:

1. **基準 EBITDA 要用 pulled,不能沿用 fileBased 舊假設。** fileBased deck 當時用 FY26E 營收 $13.75bn,但 capiq `get_estimates` 實際只回 $10.9bn(利潤率 22%)→ FY26E EBITDA = **$2.40bn**(FY27E 才 $3.11bn)。基準變小,所有區間整體下移。
2. **淨負債 server 沒給。** daloopa balance_sheet 只回 Backlog,沒有負債。→ 淨負債只能標成**假設**($2.0bn),附 comment、列入待校正風險。**不編。**

先用 Python 把所有估值法區間一次算準(單一真實來源),確保 xlsx / 圖 / proposal 三者一致:

```bash
cd ".../mcpBased/pitch" && PYTHONUTF8=1 python - <<'PY'
# 全部 inputs 來自 mcp_pulls/*.json
price=320; mktcap=122; shares=mktcap/price        # 0.381bn(quote 推算)
EBITDA26=10.9*0.22                                # 2.398(capiq estimates)
net_debt=2.0                                      # 假設(daloopa 未給負債)
...
PY
```

```text
Current EV $124  | EV/EBITDA on FY26E 51.7x  (≈ capiq comps 51x ✓) | on FY27E 39.9x
COMPS 25–40x FY26E:  $152 – $246   (VRT 自身 51x ≈ $316 ≈ 現價)
DCF  永續 $97 / 出場22x $191       區間 $97 – $191
LBO ability-to-pay: 25% $133 | 20% $156 | 15% $185
示意 $400 報價: 進場 EV $155 = 64x EBITDA
```

LBO ability-to-pay($133–$156)遠低於現價 $320 —— 這就是提案核心張力。再精算寫進工作簿的完整活公式 LBO(含掃債)+ 5×5 IRR 敏感度 + 綜效 ability-to-pay:

```text
LBO @ $400: 發起人股權 ~$144bn | MOIC 0.81x | IRR ~−4%(不可行)
5×5 IRR 中心($400/22x) = −4.1%;即便 $320/26x 也只 ~4%
綜效 ATP @20% IRR: $0→$156 / $1bn→$179 / $2bn→$202(仍 < 現價 $320)
```

> 結論已浮現:DCF / 合理倍數 Comps / LBO ability-to-pay 三法一致落在 $97–$246,全部 < 現價 $320。收購 VRT = 對已偏貴的價格再付控制溢價。

## 三、建立估值工作簿(活公式)

```text
● Write(scripts/build_vrt_ma.py)   # 讀 mcp_pulls/*.json → openpyxl,藍輸入/黑公式/紫連結,輸入格附來源 comment
```

```bash
cd ".../mcpBased/pitch" && PYTHONUTF8=1 python scripts/build_vrt_ma.py
```

```text
SAVED .../out/VRT_MA_Valuation.xlsx  sheets:
  ['Football Field', 'LBO', 'Comps', 'DCF Summary', 'Synergies & Sensitivity']
```

工作簿 5 分頁:Football Field(彙總)、LBO(活公式 + 掃債 + ability-to-pay)、Comps(14 家 pulled)、DCF Summary、Synergies & Sensitivity(綜效 ATP + 5×5 IRR,公式連結 LBO 分頁)。每個輸入格的 comment 指回 pulled 來源,或明標「假設」。

## 四、足球場圖 + IRR 熱力圖

```text
● Write(scripts/build_vrt_football.py)   # 各法區間疊橫條,標現價 $320 / 報價 $400
● Write(scripts/build_vrt_heatmap.py)    # 報價 × 出場倍數 5×5 IRR,框出基準 $400/22x
```

```bash
cd ".../mcpBased/pitch" && PYTHONUTF8=1 python scripts/build_vrt_football.py && \
                           PYTHONUTF8=1 python scripts/build_vrt_heatmap.py
```

```text
saved out/charts/vrt_football.png
saved out/charts/vrt_irr_heatmap.png
```

熱力圖中心格($400/22x)= −4%,與 Python 精算的 −4.1% 一致 ✓;足球場所有內在/交易法區間皆在現價 $320 紅線之左。

## 五、提案 narrative

```text
● Write(out/VRT_MA_Proposal_Draft.md)
```

含:框架/聲明 → 標的快照(pulled facts)→ 策略理由 → 估值三角驗證(Comps/DCF/LBO/綜效)→ 足球場彙總 → IRR 敏感度 → 建議與後續 → 風險與待校正。溢價/綜效/WACC/終值/FY28+ 路徑全標假設;先例交易與淨負債明標「server 未提供」。

## 交付清單(out\\ 與 mcp_pulls\\)

| 交付物 | 檔案 | 內容 |
|---|---|---|
| 提案 narrative | `out/VRT_MA_Proposal_Draft.md` | 估值三角驗證 + 值區間 + 建議,全程標 pulled vs 假設 |
| 估值工作簿 | `out/VRT_MA_Valuation.xlsx` | 5 分頁,LBO/Synergies 活公式 |
| 足球場圖 | `out/charts/vrt_football.png` | 5 法區間 vs 現價/報價 |
| IRR 熱力圖 | `out/charts/vrt_irr_heatmap.png` | 報價 × 出場倍數 5×5 |
| MCP 證據 | `mcp_pulls/*.json` + `_tools_*.json` | 10 次呼叫原始回傳 |
| pull spec / build script | `scripts/pull_capiq.json`, `pull_daloopa.json`, `build_vrt_*.py` | 可重跑 |

### 核心結論(誠實、未粉飾)

VRT 是最優質的 AI 散熱 pure-play,**但以現價 $320 收購的經濟學不成立**。以 pulled FY26E EBITDA $2.40bn 為基準:

- 足球場區間(每股):Comps $152–$246 | DCF $97–$191 | LBO ability-to-pay $133–$156 | 綜效 ATP @20% IRR $156–$202 —— 全部 < 現價 $320。
- 示意 $400 報價:進場 ~64x EBITDA、發起人寫 ~$144bn 股權、MOIC 0.81x / IRR ~−4%(不可行)。要達 20–25% IRR 進場價需 $133–$156(現價的 4–5 折)。
- 即便給 $2bn 綜效(≈ 進場 EBITDA 83%),@20% IRR 進場價仍只 ~$202。

建議:① 暫不推進全額現金收購;② 改採少數股權/合資/可轉換結構;③ 列入觀察、設估值修正觸發;④ 平行評估較便宜的純標的(Auras 3324、AVC 3017、私有液冷資產)。

### 兩個提醒

- **這次的數字比 fileBased 更低、結論更強** —— 因為改用 pulled FY26E EBITDA $2.40bn(舊版自行假設 $13.75bn 營收 → 高估 ~25% 基準)。先拉再算很重要。
- **待校正**:現價/股數/淨負債/EBITDA/倍數均為 mock 合成值;淨負債為假設(daloopa 未給負債);先例交易 server 未提供。全須以 FactSet/Bloomberg 與申報文件核實。模型後 / 簡報後各須 banker 簽核;agent 無對外通訊。

✅ 已完成
