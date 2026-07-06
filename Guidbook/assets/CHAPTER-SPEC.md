# 章節撰寫規格（給撰稿 SubAgent — 必讀，嚴格遵守）

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
<body data-chapter="chXX">   <!-- 例如 data-chapter="ch03"；附錄用 "appendix" -->
<main>
  <h1><span class="ch-no">Chapter N</span>章名</h1>
  <p class="lead">一段導言，說明本章解決什麼問題、讀完能做什麼。</p>

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
ch01-introduction, ch02-architecture, ch03-getting-started, ch04-customizing,
ch05-new-agent, ch06-bank-integration, ch07-aws-deployment, ch08-orchestration,
ch09-security-compliance, ch10-governance, ch11-operations, ch12-testing-evals, appendix

## 可用互動元件（由 book.css/book.js 提供，直接用 class）

1. **提示框**：`<div class="callout info|tip|warn|danger"><span class="co-title">標題</span>內容</div>`
2. **頁籤**：
   ```html
   <div class="tabs">
     <div class="tab-bar"><button>頁籤A</button><button>頁籤B</button></div>
     <div class="tab-panel">A 內容</div>
     <div class="tab-panel">B 內容</div>
   </div>
   ```
3. **摺疊**：`<details><summary>標題</summary><p>內容</p></details>`
4. **動畫流程圖**（自動加「▶ 播放流程」按鈕、逐步點亮）：
   ```html
   <div class="flow" data-animate>
     <div class="step"><span class="n">1</span><strong>步驟名</strong><br>說明</div>
     <div class="arrow">→</div>
     <div class="step"><span class="n">2</span>…</div>
   </div>
   ```
5. **測驗**（`data-answer` 為正解 label 的 0-based 索引）：
   ```html
   <div class="quiz" data-answer="1">
     <div class="q">Q：問題？</div>
     <label>選項A</label><label>選項B</label><label>選項C</label>
     <div class="explain">解析…</div>
   </div>
   ```
6. **檢核清單**（可點擊打勾、自動記憶）：`<ul class="checklist"><li>項目</li></ul>`
7. **程式碼**：`<div class="code-title">檔名或指令情境</div><pre><code>…</code></pre>`（自動有複製按鈕）。HTML 特殊字元務必轉義（`<` → `&lt;`）。
8. **ASCII 架構圖**：`<pre class="diagram">…</pre>`（無複製按鈕、虛線框）
9. **表格**：包在 `<div class="table-wrap"><table>…</table></div>`
10. **卡片**：`<div class="cards"><div class="card"><h4>…</h4><p>…</p></div>…</div>`
11. **標籤**：`<span class="badge green|amber|red|blue">文字</span>`（用於 🟢🟡🔴 安全分層）

## 內容鐵則

- **語言**：台灣繁體中文（zh-TW），技術名詞第一次出現附英文。文風：對工程師說話、精確、不打高空。
- **正確性高於一切**：所有 repo 相關敘述（檔案路徑、yaml 欄位、腳本行為、agent 名單、MCP 名稱）必須來自你實際 `Read` 過的 repo 檔案，不得憑印象編造。引用檔案時給出 repo 相對路徑。
- **銀行視角**:每章都要回答「這對銀行工程師意味著什麼」,用銀行業務舉例(授信、KYC/AML、對帳、月結、財富管理客戶會議等)。
- **關鍵事實（不得寫錯）**：
  - CMA（Claude Managed Agents）跑在 **Anthropic 雲端**（`POST /v1/agents`，beta header `managed-agents-2026-04-01`）。「部署在 AWS」指的是**周邊系統**：呼叫端後端、MCP servers、編排器（orchestrate.py）、資料源都在銀行的 AWS 帳號裡。
  - `callable_agents` 只支援**一層**委派（orchestrator → leaf workers，worker 不能再叫 worker）。
  - 每個 agent 只有**一個** leaf worker 有 Write 權限（README 表格粗體者）。
  - Skill 真本在 `plugins/vertical-plugins/<vertical>/skills/`，改完跑 `python3 scripts/sync-agent-skills.py`，再跑 `python3 scripts/check.py`；直接改 agent 包副本會被 check.py 擋。
  - MCP 以「名字」解析；上線是把同名 server 的 URL 從 mock（`127.0.0.1:800x`）改指真實系統，**不改 agent 裡的 server 名稱**。CMA 用 `${..._MCP_URL}` 環境變數佔位。
  - 跨 agent 協作：named agents 不互叫，靠輸出 `handoff_request` → `scripts/orchestrate.py`（或銀行的事件匯流排）路由成新 steering event。
- **份量**：每章正文 2000–4000 中文字 + 至少 3 個互動元件（流程圖/頁籤/測驗/檢核清單擇用）+ 至少 2 段真實程式碼/設定引用。章末放一個「本章重點」callout(tip) 與一題測驗。
- **不要**外部 CDN、外部圖片、外部字型；全部離線可開。不要行內 `<style>` 大改版面（小微調可）。
