# 章節撰寫規格（給撰稿 SubAgent — 必讀，嚴格遵守）

## 讀者設定（v2 改版核心）

本書讀者涵蓋**三種人**，每一章都必須讓前兩種人讀得完主線：

1. **非工程背景**（PM、業務、法遵）：看得懂概念主線、比喻與圖解；程式碼區塊可跳過。
2. **初級工程師**：懂一般程式概念，但 AI agent / MCP / 雲端部署是新的。
3. **中高級工程師**：要動手改、部署——深度內容放進「進階區塊」，不刪不淡化。

## 檔案位置與骨架

每章寫成 `Guidbook/<chXX-slug>/index.html`，**必須**用以下骨架（勿自帶 header/footer/theme，book.js 會自動注入）：

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>第 N 章 — 章名 | Financial Agents 開發指南</title>
<link rel="stylesheet" href="../assets/book.css">
</head>
<body data-chapter="chXX" data-level="入門">   <!-- data-level：入門｜中階｜進階 -->
<main>
  <h1><span class="ch-no">Chapter N</span>章名</h1>
  <p class="lead">一段導言，說明本章解決什麼問題、讀完能做什麼。</p>

  <!-- 先備知識框：主線需要的前置概念，連回對應章節 -->
  <div class="callout info prereq"><span class="co-title">🔑 開始前，你需要先懂</span>
    <ul>
      <li><a href="../ch00-basics/index.html#s3">agent 的四塊積木</a>（第 0 章第 3 節）</li>
    </ul>
  </div>

  <div class="toc"><div class="toc-title">本章內容</div>
    <ol>
      <li><a href="#s1">…</a></li>
    </ol>
  </div>

  <h2 id="s1">…</h2>
  <!-- 內容 -->
</main>
<script src="../assets/book.js"></script>
</body>
</html>
```

`data-chapter` 的合法值與對應資料夾（與 book.js 的 CHAPTERS 一致，不得改動）：
ch00-basics, ch01-introduction, ch02-architecture, ch03-getting-started, ch04-customizing,
ch05-new-agent, ch06-bank-integration, ch07-aws-deployment, ch08-orchestration,
ch09-security-compliance, ch10-governance, ch11-operations, ch12-testing-evals, appendix

`data-level` 全書配置（不得改動）：ch00/ch01/ch03＝入門，ch02/ch09/ch10/ch11/ch12/appendix＝中階，ch04 中階，ch05/ch06/ch07/ch08＝進階。

## 可用互動元件（由 book.css/book.js 提供，直接用 class）

1. **提示框**：`<div class="callout info|tip|warn|danger"><span class="co-title">標題</span>內容</div>`
2. **先備知識框**：`<div class="callout info prereq">`（見骨架；每章 h1/lead 之後、toc 之前，恰好一個；ch00 免）
3. **術語標記**：`<span class="term" data-term="mcp">MCP</span>` — 點擊彈出白話解釋。
   - key 必須存在於 `assets/book.js` 的 `GLOSSARY`（合法 key 清單見該檔）。
   - **每個術語在每章「第一次出現」標記一次即可**，之後不再標（避免整頁虛線）。
   - 不要標在 `<code>`、`<pre>`、標題（h1–h3）、`.code-title` 內。
4. **進階區塊**：`<div class="adv" data-note="一句話說明這段是什麼、跳過會錯過什麼">…</div>`
   - book.js 會轉成可收合面板；「初學者模式」下預設收合。
   - 放：逐欄 yaml 解剖、腳本原始碼走讀、邊角案例、效能/相容性細節。
   - **不放**：安全警告、必要步驟——這些必須留在主線。
   - 每章至少 1 個；`.adv` 內不可再巢狀 `.adv`，也不要把整個 h2 節包進去（連同標題）。
5. **頁籤**：
   ```html
   <div class="tabs">
     <div class="tab-bar"><button>頁籤A</button><button>頁籤B</button></div>
     <div class="tab-panel">A 內容</div>
     <div class="tab-panel">B 內容</div>
   </div>
   ```
6. **摺疊**：`<details><summary>標題</summary><p>內容</p></details>`
7. **動畫流程圖**（自動加「▶ 播放流程」按鈕、逐步點亮）：
   ```html
   <div class="flow" data-animate>
     <div class="step"><span class="n">1</span><strong>步驟名</strong><br>說明</div>
     <div class="arrow">→</div>
     <div class="step"><span class="n">2</span>…</div>
   </div>
   ```
8. **測驗**（`data-answer` 為正解 label 的 0-based 索引）：
   ```html
   <div class="quiz" data-answer="1">
     <div class="q">Q：問題？</div>
     <label>選項A</label><label>選項B</label><label>選項C</label>
     <div class="explain">解析…</div>
   </div>
   ```
9. **檢核清單**（可點擊打勾、自動記憶）：`<ul class="checklist"><li>項目</li></ul>`
10. **程式碼**：`<div class="code-title">檔名或指令情境</div><pre><code>…</code></pre>`（自動有複製按鈕）。HTML 特殊字元務必轉義（`<` → `&lt;`）。
11. **ASCII 架構圖**：`<pre class="diagram">…</pre>`（無複製按鈕、虛線框）
12. **表格**：包在 `<div class="table-wrap"><table>…</table></div>`
13. **卡片**：`<div class="cards"><div class="card"><h4>…</h4><p>…</p></div>…</div>`
14. **標籤**：`<span class="badge green|amber|red|blue">文字</span>`（用於 🟢🟡🔴 安全分層）

## 白話化寫作鐵則（v2 新增）

- **術語首次出現三件套**：中文稱呼＋（英文原文）＋一句白話說明或比喻，並加 `data-term` 標記。範例：
  「<span class="term" data-term="mcp">MCP</span>（Model Context Protocol）——你可以把它想成 agent 接外部系統的標準插座」。
- **先比喻、再精確**：新概念先給一個銀行日常可對應的比喻（新進員工、職位說明書、代辦章、簽核關卡…），下一句再給技術上精確的定義。比喻只是引路，不能取代正確定義。
- **句子拆短**：一句話只講一件事；超過 40 個中文字的句子拆成兩句。少用「的的不休」的多層修飾。
- **段落開頭先講結論**，再講理由與細節（讓跳讀的人不迷路）。
- **程式碼區塊前後都要有白話**：前面一句「這段在做什麼」，後面一句「你該注意哪一行、為什麼」。非工程讀者跳過程式碼也要能接得上文。
- **每個 h2 節結尾加一行「小結」**：`<p class="callout tip" style="...">` 不必，直接一段以「**一句話總結：**」開頭的段落即可。

## 內容鐵則

- **語言**：台灣繁體中文（zh-TW），技術名詞第一次出現附英文。文風：親切但精確，不打高空、不裝可愛。
- **正確性高於一切**：所有 repo 相關敘述（檔案路徑、yaml 欄位、腳本行為、agent 名單、MCP 名稱）必須來自你實際 `Read` 過的 repo 檔案，不得憑印象編造。引用檔案時給出 repo 相對路徑。
- **銀行視角**：每章都要回答「這對銀行的你意味著什麼」，用銀行業務舉例（授信、KYC/AML、對帳、月結、財富管理客戶會議等）。
- **關鍵事實（不得寫錯）**：
  - CMA（Claude Managed Agents）跑在 **Anthropic 雲端**（`POST /v1/agents`，beta header `managed-agents-2026-04-01`）。「部署在 AWS」指的是**周邊系統**：呼叫端後端、MCP servers、編排器（orchestrate.py）、資料源都在銀行的 AWS 帳號裡。
  - `callable_agents` 只支援**一層**委派（orchestrator → leaf workers，worker 不能再叫 worker）。
  - 每個 agent 只有**一個** leaf worker 有 Write 權限（README 表格粗體者）。
  - Skill 真本在 `plugins/vertical-plugins/<vertical>/skills/`，改完跑 `python3 scripts/sync-agent-skills.py`，再跑 `python3 scripts/check.py`；直接改 agent 包副本會被 check.py 擋。
  - MCP 以「名字」解析；上線是把同名 server 的 URL 從 mock（`127.0.0.1:800x`）改指真實系統，**不改 agent 裡的 server 名稱**。CMA 用 `${..._MCP_URL}` 環境變數佔位。
  - 跨 agent 協作：named agents 不互叫，靠輸出 `handoff_request` → `scripts/orchestrate.py`（或銀行的事件匯流排）路由成新 steering event。
- **份量**：每章正文 2000–4500 中文字 + 至少 3 個互動元件（流程圖/頁籤/測驗/檢核清單擇用）+ 至少 2 段真實程式碼/設定引用 + 至少 1 個進階區塊 + 先備知識框。章末放一個「本章重點」callout(tip) 與一題測驗。
- **不要**外部 CDN、外部圖片、外部字型；全部離線可開。不要行內 `<style>` 大改版面（小微調可）。

## 改完章節之後（必做）

重建全文搜尋索引，否則新內容搜不到：

```
python3 Guidbook/assets/build-search-index.py
```

（產出 `Guidbook/assets/search-index.js`，離線搜尋用。）
