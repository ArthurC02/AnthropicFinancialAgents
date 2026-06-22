# 🎯 十支 Agent 能力與驗收樣本 — 它們各能做什麼、怎麼驗

> **這份文件做什麼**：用**假資料**把十支 financial-services agent（外掛模式、真人盯）各跑一遍後，整理出**每支證明了什麼能力、怎麼驗收、上線前還缺什麼**，並附上可重複使用的「埋了考點」測試樣本。給想評估或複製這趟的人看。
>
> 入門步驟見 [QuickStart.md](QuickStart.md)；十支總覽見 [AgentSummary.md](AgentSummary.md)；技術架構見 [TechSummary.md](TechSummary.md)。

---

## 一、十支能力與驗收方式總表

> **兩種驗收方式**：
> `🎯 埋考點` = 有埋了考點的樣本檔＋對著答案卡逐項打分（適合反覆驗收）；
> `📦 看交付物` = 多靠外部資料、沒另做埋錯樣本，看它產不產得出實際交付物。

| 批次 | 助理 | 驗收方式 | 重點表現 |
|---|---|---|---|
| 一·前台 | 🔭 市場研究 market-researcher | 📦 看交付物 | 主題「**AI 資料中心散熱**」→ 產業研究簡報＋同業比較＋VRT DCF；沒接資料源也照跑，comps 正確掛 `[UNSOURCED]` |
| 一·前台 | 🧮 估值建模 model-builder | 📦 看交付物 | **VRT** 從零建 DCF 模型；計算格用公式、不寫死 |
| 一·前台 | 📊 財報追蹤 earnings-reviewer | 📦 看交付物 | **TSMC Q1-2026**：更新模型＋DCF 估值＋財報觀點筆記＋11 張圖表 |
| 二·投行 | 🎯 投行提案 pitch-agent | 📦 看交付物 | **VRT M&A**：提案簡報＋估值＋足球場圖＋IRR 熱力圖 |
| 一·前台 | 🤝 會前準備 meeting-prep-agent | 🎯 埋考點 | 用**提示注入**信要它匯款並隱匿 → 它拒做、還把詐騙信攤在資料包最前面；再平衡超標＋DCI 到期風險＋不粉飾虧損全中 |
| 三·後台 | 🧾 對帳單稽核 statement-auditor | 🎯 埋考點 | 埋的 3 錯全揪（費用/期末換位/出資）＋合計差 +559,000＋LP-004 正確放行；附更正後正確期末 |
| 三·後台 | 📅 月底結帳 month-end-closer | 🎯 埋考點 | foot check 對上 1,275,000；**還抓出樣本裡折舊/分紅的前期瑕疵** |
| 三·後台 | 💰 估值複核 valuation-reviewer | 🎯 埋考點 | 抓 2 政策違反、不誤殺 Helios；**waterfall 比答案卡還對** |
| 三·後台 | ⚖️ 總帳對帳 gl-reconciler | 🎯 埋考點 | critic 留 3 真差異、濾 3 假差異，零誤報零漏報 |
| 三·中台 | 🔍 開戶審查 kyc-screener | 🎯 埋考點 | 抓真制裁(B)、放假命中(C)、PEP 走 EDD 不亂拒(D) |

> **怎麼讀這張表**：**六支**有「埋考點的樣本檔」可對著答案卡逐項打分——後台四支（對帳單／月結／估值複核／總帳）＋中台一支（開戶審查）＋前台 🤝 會前準備；另**四支前台**（市場研究／估值建模／財報追蹤／投行提案）多靠外部資料，看它的實際交付物（產出由 [`outputs/fileBased/`](outputs/fileBased/) 各自的 `scripts/` 建，binary 檔不入庫）。

---

## 二、最大的發現：好 agent 會「反過來挑出你資料的毛病」

埋考點的六支裡，**有三支不只答對，還反過來抓出出題時沒注意到的瑕疵**——這比單純答對更能證明判斷力。

```
📅 月底結帳
   樣本把 1–3 月折舊設 0、4 月設 50k
   → 它反問：「140 萬固定資產卻 Q1 不提折舊？疑似漏提」
   樣本只讓它估列 4 月分紅
   → 它反問：「若 1–3 月也該按月估，YTD 怎麼只見 4 月？」

💰 估值複核
   答案卡的 waterfall 用 NAV 當基數，算出 carry 10M
   → 它改用「累計分配 40M ＋ NAV」當基數（歐式 whole-fund 正解）
     carry 連動跑出三情境：18M（報告）→ 13M（NAV 調整 −25M）→ 0（IRR 7.56% < 8% hurdle）
   → 答案卡錯、它對
   而且它不只算 carry：獨立用 8% 複利重算「優先報酬基準」≈ 69M，
     對照給的 35M（差約 34M）→ 標「需對帳、非斷定錯誤」交 CCO

⚖️ 總帳對帳
   它主動做「方向性對抗檢查」：
   「時間差會讓保管現金偏高，但實況是 GL 偏高 → 方向相反，
     所以現金差異不能用時間差打發」
```

> **共通的好行為（10 支都有）**：
> - **不瞎掰**：查不到就標 `[UNSOURCED]`／`[ASSUMPTION]`／「需查」，不硬擠假數字。
> - **不亂殺**：假命中、誤報、乾淨件都正確放行（kyc 的 C/E、gl 的 3 筆假差異）。
> - **人留最後一關**：全部只產草稿／審查包，標明「合規／控制員／IR/CCO 簽核才定案」，agent 自己不過帳、不發送。

---

## 三、埋了考點的測試樣本索引（可重複拿來驗收）

> 樣本檔收在對應 agent 的 [`outputs/fileBased/<agent>/samples/`](outputs/fileBased/) 底下，都是假資料、每組都「埋了考點」。
> 註：輸出資料夾用的是縮寫名（`gl-conciler`／`earning-reviewer`／`pitch`），跟 [`agents/`](agents/) 裡的正式檔名略有出入，不是連結壞掉。

| Agent | 樣本檔位置 | 埋的考點 |
|---|---|---|
| 🧾 對帳單稽核 | `outputs/fileBased/statement-auditor/samples/statement-auditor/` nav_pack＋lp_statement | 埋 3 處錯（費用/期末/出資），含 1 列內部加總也不對 |
| 📅 月底結帳 | `outputs/fileBased/month-end-closer/samples/` 試算表＋應計清單 | 3 筆應計、結轉 foot 到 1,275,000、差異說明門檻 5% |
| 💰 估值複核 | `outputs/fileBased/valuation-reviewer/samples/` GP估值包＋基金條款 | 2 筆違反估值政策、1 筆誤報對照、carry 連動 |
| ⚖️ 總帳對帳 | `outputs/fileBased/gl-conciler/samples/` GL＋子帳＋對帳參考 | 3 真差異＋3 假差異（時間差/FX進位/重分類）|
| 🔍 開戶審查 | `outputs/fileBased/kyc-screener/samples/` 申請＋規則表＋名單 | 真制裁命中＋同名假命中＋PEP/高風險＋缺漏 |
| 🤝 會前準備 | `outputs/fileBased/meeting-prep-agent/samples/` 客戶檔案＋近期往來 | **提示注入**防火牆＋再平衡超標＋不粉飾虧損＋未結項 |

> 前台另外四支多靠外部資料、沒另做埋錯樣本。它們的交付物由各自 `scripts/` 底下的 builder 產（binary 檔不入庫）：

| Agent | 標的 | 產出由哪些 builder 建 |
|---|---|---|
| 🔭 市場研究 | AI 資料中心散熱 | `outputs/fileBased/market-researcher/scripts/` build_deck.py · build_comps.py · build_dcf.py |
| 🧮 估值建模 | VRT | `outputs/fileBased/model-builder/scripts/build_vrt_dcf2.py` |
| 📊 財報追蹤 | TSMC Q1-2026 | `outputs/fileBased/earning-reviewer/scripts/` build_tsmc_model.py · build_tsmc_dcf.py · build_tsmc_note.py · build_tsmc_charts.py |
| 🎯 投行提案 | VRT M&A | `outputs/fileBased/pitch/scripts/` build_vrt_pitch.py · build_vrt_ma.py · build_vrt_football.py · build_vrt_heatmap.py |

> 📎 同一批 agent 也跑過「接 MCP」版（接 [`mock-mcp/`](../mock-mcp/) 的本機假資料源），紀錄在 [`outputs/mcpBased/`](outputs/mcpBased/)，與 `fileBased/` 對照。

---

## 四、上線前共通缺口（試水溫 ≠ 可上線）

```
能「無痛試水溫」的：
  前台四支              → 公開廠商連接器，缺金鑰也能跑（網路搜尋補洞）
  🤝 會前準備＋中後台五支 → 用「餵檔案」或跑 mock-mcp 代替內部系統，可完整體驗流程

要「真正上線」一定得補的：
┌──────────────────┬──────────────────────────────────────────┐
│ 前台四支          │ 買資料訂閱＋API金鑰（FactSet/CapIQ…）      │
│                  │ ＋客製 comps 定義／建模慣例／簡報範本       │
├──────────────────┼──────────────────────────────────────────┤
│ 🤝 會前準備       │ 把 crm（現指本機 mock）改指內部 CRM         │
│ （前台但需內部系統）│ ＋客製 IPS／再平衡門檻／簡報範本            │
├──────────────────┼──────────────────────────────────────────┤
│ 中後台五支        │ 把內部系統 MCP（總帳/子帳/淨值/投組/名單）  │
│ （後台4＋中台1）  │ 從本機 mock 改指公司真實系統                │
│                  │ ＋客製規則（容差/重大性/估值政策/KYC規則）  │
│                  │ ＋建可追查的操作紀錄                        │
└──────────────────┴──────────────────────────────────────────┘
```
> 內部系統的 MCP 現在都已接到 repo 內建的本機 mock（[`mock-mcp/`](../mock-mcp/)），所以連後台都能離線完整 demo；上線就是把那些 mock 的 url 改指真實來源（見 [TechSummary.md](TechSummary.md) 第三段）。各支「上線前要補齊」的細節，見 [agents/](agents/) 各自文件的「四、上線前要補齊」段。

---

## 五、一句話總結：每支證明了什麼能力

| 助理 | 它證明了 |
|---|---|
| 🔭 市場研究 | 沒資料源也能產結構化研究草稿，而且誠實標未證實 |
| 🧮 估值建模 | 從零建出公式化、可 trace 的估值模型 |
| 📊 財報追蹤 | 讀懂法說會、把新數字正確更新進既有模型 |
| 🎯 投行提案 | 把研究＋建模＋簡報端到端串成一份提案 |
| 🤝 會前準備 | 整理客戶關係＋持倉＋市場動態成會前包，並擋住客戶來信的提示注入（要它匯款並隱匿，它拒做並攤開）|
| 🧾 對帳單稽核 | 逐欄 tie-out，分送前揪出對不上的數字 |
| 📅 月底結帳 | 自我驗證（foot check），而且對不上就攤開不硬湊 |
| 💰 估值複核 | 拿 GP 估值對照政策、算對 carry，不照單全收 |
| ⚖️ 總帳對帳 | critic 跑對抗式 review：留真差異、濾假差異 |
| 🔍 開戶審查 | 法遵分寸：抓真制裁、放假命中、高風險走 EDD |
| **全部** | **只建議、不拍板——最後一定有人簽核** |

---

> 📎 安裝與常見錯誤（保留名稱、Windows 反斜線路徑、agent 不自動接管對話）見 [QuickStart.md](QuickStart.md) 第三段，不在此重複。
> 📎 設計原則、商業故事、導入順序見 [AgentSummary.md](AgentSummary.md)；「一個來源兩個輸出」與外掛 vs CMA 見 [TechSummary.md](TechSummary.md)。
