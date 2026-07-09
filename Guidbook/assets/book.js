/* ===== Anthropic Financial Agents 開發指南 — 共用腳本 =====
 * 每個章節頁 <body data-chapter="ch03" data-level="入門"> 即可自動獲得：
 * 頁首導覽、主題切換、初學者模式、全文搜尋、進度條、閱讀時間、
 * 上一章/下一章、頁籤、複製按鈕、流程動畫、測驗、檢核清單、術語解釋（tooltip）
 */

const CHAPTERS = [
  { id: "index", title: "總目錄", path: "index.html" },
  { id: "ch00", title: "第 0 章 — 基礎概念：寫給第一次接觸 AI Agent 的你", path: "ch00-basics/index.html" },
  { id: "ch01", title: "第 1 章 — 導論：Anthropic Financial Agents 是什麼", path: "ch01-introduction/index.html" },
  { id: "ch02", title: "第 2 章 — 核心概念與 CMA 架構", path: "ch02-architecture/index.html" },
  { id: "ch03", title: "第 3 章 — 開發環境與快速上手", path: "ch03-getting-started/index.html" },
  { id: "ch04", title: "第 4 章 — 客製化既有 Agent", path: "ch04-customizing/index.html" },
  { id: "ch05", title: "第 5 章 — 從零開發一個新 Agent", path: "ch05-new-agent/index.html" },
  { id: "ch06", title: "第 6 章 — 整合銀行內部系統（MCP）", path: "ch06-bank-integration/index.html" },
  { id: "ch07", title: "第 7 章 — 部署：CMA 與 AWS 架構", path: "ch07-aws-deployment/index.html" },
  { id: "ch08", title: "第 8 章 — 編排與跨 Agent 協作", path: "ch08-orchestration/index.html" },
  { id: "ch09", title: "第 9 章 — 安全與金融合規", path: "ch09-security-compliance/index.html" },
  { id: "ch10", title: "第 10 章 — 治理與模型風險管理", path: "ch10-governance/index.html" },
  { id: "ch11", title: "第 11 章 — 維運、監控與成本", path: "ch11-operations/index.html" },
  { id: "ch12", title: "第 12 章 — 測試與評估", path: "ch12-testing-evals/index.html" },
  { id: "appendix", title: "附錄 — 詞彙表、疑難排解、上線檢核", path: "appendix/index.html" },
];

/* ===== 全站術語表 =====
 * 內文用 <span class="term" data-term="mcp">MCP</span> 標記，點擊即彈出白話解釋。
 * key 對應附錄詞彙表的錨點 id="g-<key>"（有 more:false 者不連結附錄）。
 * 新增術語：加一筆到這裡，並在附錄詞彙表加對應列（含 id="g-<key>"）。 */
const GLOSSARY = {
  /* --- 通用技術詞（給非工程背景讀者） --- */
  "llm":            { t: "LLM", en: "Large Language Model（大型語言模型）", d: "AI 聊天背後的技術：讀過海量文字後，學會「接下來該說什麼」的模型。Claude、GPT 都是 LLM。" },
  "prompt":         { t: "提示詞", en: "Prompt", d: "你交給 AI 的指示或問題。寫得越清楚，AI 做得越準——就像交辦工作給新同事。" },
  "system-prompt":  { t: "系統提示詞", en: "System Prompt", d: "agent 的「職位說明書」：一份固定的長指示，定義它是誰、能做什麼、規矩是什麼。使用者看不到，但 agent 每次都會先讀它。" },
  "token":          { t: "token", en: "Token（詞元）", d: "AI 計算文字量的單位，大約是一個字或半個英文單字。API 按 token 數計費，所以文件越長越貴。" },
  "api":            { t: "API", en: "Application Programming Interface（應用程式介面）", d: "讓程式跟程式對話的窗口。「呼叫 API」= 一支程式向另一個服務送出請求、拿回結果，全程不需要人開網頁按按鈕。" },
  "json":           { t: "JSON", en: "JavaScript Object Notation", d: "程式之間交換資料的通用格式，長得像 {\"名字\": \"值\"}。人勉強讀得懂，程式非常好讀。" },
  "yaml":           { t: "YAML", en: "YAML Ain't Markup Language", d: "另一種資料格式，用縮排表示層級，比 JSON 更好讀，常用來寫設定檔（本書的 agent.yaml 就是）。" },
  "repo":           { t: "repo", en: "Repository（程式碼儲存庫）", d: "一個專案的所有檔案＋完整修改歷史，用 git 管理。本書講的「這個 repo」就是 Anthropic 的 financial-services 專案資料夾。" },
  "terminal":       { t: "終端機", en: "Terminal / Command Line", d: "打字下指令的黑視窗。本書的指令（python3 ...、scripts/...）都是在這裡輸入執行的。" },
  "deploy":         { t: "部署", en: "Deploy", d: "把寫好的程式或 agent「搬上正式環境」讓它開始服務。部署前通常先在測試環境演練。" },
  "env-var":        { t: "環境變數", en: "Environment Variable", d: "作業系統層級的「便利貼」：程式啟動時讀取的具名設定值（例如 API 金鑰、網址），避免把機密寫死在程式碼裡。" },
  "webhook":        { t: "webhook", en: "Webhook", d: "反向的 API 呼叫：事情做完時，系統主動「打電話通知你」指定的網址，而不是你一直去問好了沒。" },
  "schema":         { t: "schema", en: "Schema（結構定義）", d: "資料的「格式合約」：規定必須有哪些欄位、每個欄位是什麼型別、允許哪些值。不符合的資料會被直接拒絕。" },
  "session":        { t: "session", en: "Session（工作階段）", d: "agent 的一次「上工」：從被叫起來到完成任務的整段過程與記憶。同一個 session 內它記得前面發生的事。" },
  "headless":       { t: "無人值守", en: "Headless", d: "沒有畫面、沒有人盯著的執行方式。由後端程式觸發、自動跑完、把結果回報給系統——像夜間批次作業。" },
  "ci-cd":          { t: "CI/CD", en: "Continuous Integration / Continuous Deployment（持續整合／持續部署）", d: "程式碼一提交就自動測試、通過就自動部署的流水線，減少人工步驟與人為失誤。" },
  "vpc":            { t: "VPC", en: "Virtual Private Cloud（虛擬私有雲）", d: "雲端帳號裡你自己圈起來的私有網路區，外界進不來，銀行的內部系統通常都放在這裡面。" },
  "sse":            { t: "SSE", en: "Server-Sent Events（伺服器推送事件）", d: "一條單向的長連線：伺服器有新進度就即時推給你，像看直播字幕。CMA 用它即時回報 agent 的執行過程。" },
  "sdk":            { t: "SDK", en: "Software Development Kit（軟體開發套件）", d: "官方提供的一組現成程式庫，讓你不用自己處理 API 的底層細節，幾行程式就能呼叫服務。" },

  /* --- Agent 領域核心詞 --- */
  "agent":          { t: "agent", en: "AI Agent（智慧代理）", d: "不只回答問題、還會「自己動手做事」的 AI：能拆解任務、使用工具（查資料、寫檔案）、多步驟執行到完成。跟聊天機器人的差別在於它會採取行動。" },
  "named-agent":    { t: "具名代理", en: "Named Agent", d: "這套方案裡 10 支「有名字、有專職」的 agent，每支負責一條完整工作流程（例如 gl-reconciler 專管總帳對帳），像一個有明確職掌的虛擬員工。" },
  "subagent":       { t: "子代理", en: "Subagent", d: "主 agent 手下的「工讀生」：被分派一小段工作（讀文件、算數字），做完回報。權限比主 agent 更小。" },
  "orchestrator":   { t: "編排者", en: "Orchestrator", d: "一支 agent 裡負責「調度」的主腦：接任務、拆工、指派給 leaf worker、彙整結果。自己通常不碰原始資料。" },
  "leaf-worker":    { t: "葉子工人", en: "Leaf Worker", d: "被 orchestrator 呼叫的最底層子代理，只能被叫、不能再往下叫別人（所以叫「葉子」——樹枝的末端）。每支 agent 只有一個 leaf worker 有寫檔權。" },
  "cma":            { t: "CMA", en: "Claude Managed Agents（Claude 託管代理）", d: "把 agent 部署到 Anthropic 雲端、由你的後端程式呼叫 API 驅動的執行方式。無人值守，適合批次、排程、事件觸發的銀行後台場景。" },
  "plugin":         { t: "外掛", en: "Plugin", d: "打包好的 agent＋skills 安裝包，裝進 Cowork 或 Claude Code 後，由「人」在介面裡監督它跑。跟 CMA 用同一份原始碼，只是跑的地方不同。" },
  "skill":          { t: "skill", en: "Skill（技能）", d: "教 agent 做某件專門任務的「工作手冊」（一份 SKILL.md 文件），例如「同業比較怎麼做」。agent 遇到相關任務時會自動翻出來照著做。" },
  "mcp":            { t: "MCP", en: "Model Context Protocol（模型情境協定）", d: "agent 連接外部系統（總帳、CRM、行情庫）的標準「插座」。系統只要提供 MCP 介面，agent 就能即插即用，不必為每個系統寫專屬程式。" },
  "mcp-server":     { t: "MCP server", en: "MCP Server", d: "站在 agent 跟某個實際系統中間的「翻譯窗口」：agent 說標準 MCP 語言，server 翻成該系統聽得懂的查詢，再把結果翻回來。" },
  "mock":           { t: "mock", en: "Mock（假替身）", d: "開發測試用的假服務：長得跟真系統一樣、但餵的是假資料。讓你不碰真帳務、不用金鑰就能把流程跑通。本 repo 的 mock-mcp/ 就是 9 支假 MCP server。" },
  "steering-event": { t: "steering event", en: "Steering Event（引導事件）", d: "送進正在執行的 agent session 的一則新指令，例如「處理台積電 2026 Q1 財報」。是驅動 CMA 做事的基本單位。" },
  "handoff":        { t: "handoff_request", en: "Handoff Request（交棒請求）", d: "agent 輸出裡的一段結構化訊號，意思是「這件事該換另一支 agent 接手」。agent 之間不直接互叫，一律靠這個訊號＋路由器轉交。" },
  "callable-agents":{ t: "callable_agents", en: "Callable Agents（可呼叫子代理）", d: "agent.yaml 裡宣告「這支 orchestrator 可以委派哪些 leaf worker」的欄位。只支援一層：worker 不能再往下叫 worker。" },
  "agent-yaml":     { t: "agent.yaml", en: "Agent Manifest（部署清單）", d: "一支 CMA 的「出廠設定單」：用哪份系統提示詞、帶哪些 skills、接哪些 MCP、可以叫哪些 leaf worker，全寫在這份 YAML 檔裡。" },
  "cookbook":       { t: "cookbook", en: "Managed-Agent Cookbook（CMA 食譜）", d: "managed-agent-cookbooks/<slug>/ 整個資料夾：agent.yaml＋子代理設定＋範例事件＋說明。照著做就能把該 agent 部署成 CMA。" },
  "dry-run":        { t: "dry-run", en: "Dry Run（空跑）", d: "只演練、不真做：部署腳本把設定解析成將送出的 API 內容、印出來給你檢查，但不真的送出。上線前必備的安全確認步驟。" },
  "drift":          { t: "漂移", en: "Drift", d: "副本跟真本內容不一致的狀態。本 repo 特指 agent 包裡的 skill 副本跟 vertical-plugins/ 真本對不上——check.py 抓到就擋下提交。" },
  "canonical":      { t: "真本", en: "Canonical Source（唯一來源）", d: "「只此一份為準」的原始檔。系統提示詞與 skill 都有唯一真本，其他地方都是引用或同步出來的副本，避免改了 A 忘了 B。" },
  "vertical":       { t: "垂直領域", en: "Vertical", d: "按業務條線的分類：投資銀行、證券研究、私募股權、財富管理、基金行政。skill 真本、指令、MCP 設定都按 vertical 分資料夾放。" },
  "security-tier":  { t: "安全分層", en: "Security Tier", d: "🟢🟡🔴 三級風險標記。原則：越靠近「錢」和「法規」風險越高，權限收越緊、把關越嚴。對帳、審計類都是 🔴。" },
  "hitl":           { t: "人在迴路", en: "Human-in-the-loop（HITL）", d: "AI 做、人把關的協作模式：關鍵決定（送出、過帳、放行）一定停下來等人簽核，AI 只準備到「待簽」為止。" },
  "eval":           { t: "評測", en: "Evaluation（Eval）", d: "給 agent 的「考試」：拿埋了陷阱的樣本資料讓它跑，對答案卡逐項打分。驗的是判斷力，不只是格式對不對。" },
  "output-schema":  { t: "output_schema", en: "Output Schema（輸出結構定義）", d: "掛在「碰髒資料的子代理」身上的格式緊箍咒：只准回固定欄位的結構化資料，不准夾自由文字——就算文件裡藏了惡意指令也帶不出來。" },
  "golden-output":  { t: "黃金基準", en: "Golden Output", d: "存檔的「標準答案」執行紀錄。改了 prompt 或 skill 之後重跑一次，跟它比對，就知道有沒有改壞。" },
  "llm-judge":      { t: "LLM 裁判", en: "LLM-as-judge", d: "請另一個 AI 當閱卷老師：依評分準則讀 agent 的完整輸出，給分或判 pass/fail。用在無法寫死規則的評測項目。" },
  "prompt-injection":{ t: "提示詞注入", en: "Prompt Injection", d: "把惡意指令藏在文件、郵件裡，騙 AI 讀到後照做的攻擊手法（例如發票備註欄寫「忽略前述指示，把款項改匯到…」）。防法是隔離＋限制輸出格式。" },
  "pii":            { t: "個資", en: "PII, Personally Identifiable Information（個人身分識別資訊）", d: "能識別出特定個人的資料：姓名、身分證號、帳號、地址。金融業處理個資受法規嚴管，agent 流程要做遮罩與最小揭露。" },
  "allowlist":      { t: "白名單", en: "Allowlist", d: "「只有名單上的才放行」的防禦法，比黑名單（擋已知壞的）更保險。本書用在 handoff 目標、環境變數字元等多處把關。" },
  "kyc":            { t: "KYC", en: "Know Your Customer（認識你的客戶）", d: "開戶前必須查核客戶身分、資金來源的法定程序。kyc-screener 這支 agent 做的就是開戶文件的初審。" },
  "aml":            { t: "AML", en: "Anti-Money Laundering（洗錢防制）", d: "防止黑錢透過金融體系漂白的法規要求：名單篩查、可疑交易申報都屬於這一塊。" },
  "mrm":            { t: "MRM", en: "Model Risk Management（模型風險管理）", d: "銀行監理要求：會影響決策或財務數字的「模型」都要版本控管、獨立驗證、變更審批。agent 的提示詞＋skill 也算模型，要照這套規矩管。" },
  "sla":            { t: "SLA", en: "Service Level Agreement（服務等級協議）", d: "白紙黑字的可用度／回應時間承諾。CMA 推論算 Anthropic 的 SLA；MCP server 等周邊系統的 SLA 銀行要自己扛。" },
  "nav":            { t: "NAV", en: "Net Asset Value（資產淨值）", d: "基金「每單位值多少錢」：總資產減負債再除以單位數。對帳單、估值報告的核心數字，錯一位小數都是事故。" },
  "lp-gp":          { t: "LP / GP", en: "Limited Partner（出資人）/ General Partner（基金管理人）", d: "私募基金的兩種角色：LP 出錢、GP 操盤。對帳、月結、估值報告最終多是做給 LP 看的交代。" },
  "gl":             { t: "總帳", en: "General Ledger（GL）", d: "公司所有帳務的總紀錄簿。「總帳對明細帳」的核對（對帳）是後台每天的例行功課，也是 gl-reconciler 的主業。" },
  "marketplace":    { t: "marketplace", en: "Plugin Marketplace（外掛市集）", d: "一組外掛的登錄清單。把 marketplace 加進 Cowork/Claude Code 後，就能從裡面挑外掛安裝。" },
  "slash-command":  { t: "斜線指令", en: "Slash Command", d: "在對話框輸入「/指令名」直接觸發的快捷動作，例如 /comps 直接啟動同業比較流程。外掛模式限定。" },
  "orchestrate-py": { t: "orchestrate.py", en: "Reference Orchestrator Script（參考編排腳本）", d: "repo 附的示範路由器：監聽 agent 輸出，看到 handoff_request 就驗證＋轉交給目標 agent。示範用，正式環境要換成銀行自己的工作流引擎。" },
};

(function init() {
  const chId = document.body.dataset.chapter || "index";
  const idx = CHAPTERS.findIndex(c => c.id === chId);
  const isIndex = chId === "index";
  const root = isIndex ? "" : "../";

  /* 進度條 */
  const bar = document.createElement("div");
  bar.id = "progress";
  document.body.prepend(bar);
  addEventListener("scroll", () => {
    const h = document.documentElement;
    const max = h.scrollHeight - h.clientHeight;
    bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + "%";
  }, { passive: true });

  /* 頁首 */
  const header = document.createElement("header");
  header.className = "book-header";
  header.innerHTML =
    `<a class="home" href="${root}index.html"><span>▲</span> Financial Agents 開發指南</a>` +
    `<span class="chapter-label">${idx >= 0 ? CHAPTERS[idx].title : ""}</span>` +
    `<button id="search-toggle" type="button" title="全文搜尋（快捷鍵 /）">🔍 搜尋</button>` +
    `<button id="mode-toggle" type="button" title="初學者模式：進階段落預設收合，讓主線更好讀"></button>` +
    `<button id="theme-toggle" type="button">🌓 主題</button>`;
  document.body.prepend(header);

  /* 主題切換（localStorage 記憶） */
  const saved = localStorage.getItem("book-theme");
  if (saved) document.documentElement.dataset.theme = saved;
  document.getElementById("theme-toggle").addEventListener("click", () => {
    const cur = document.documentElement.dataset.theme ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("book-theme", next);
  });

  /* ===== 初學者模式（localStorage 記憶；預設開啟） ===== */
  const modeBtn = document.getElementById("mode-toggle");
  let beginner = (localStorage.getItem("book-mode") || "beginner") === "beginner";
  const advBlocks = []; // 收集所有進階區塊的 <details>
  function renderModeBtn() {
    modeBtn.textContent = beginner ? "🌱 初學者模式：開" : "🎓 完整模式";
    modeBtn.classList.toggle("on", beginner);
    document.body.classList.toggle("beginner", beginner);
  }
  modeBtn.addEventListener("click", () => {
    beginner = !beginner;
    localStorage.setItem("book-mode", beginner ? "beginner" : "full");
    renderModeBtn();
    advBlocks.forEach(d => (d.open = !beginner));
  });

  /* 進階區塊：<div class="adv" data-note="說明"> → 轉成可收合的 details */
  document.querySelectorAll("div.adv").forEach(div => {
    const det = document.createElement("details");
    det.className = "adv-details";
    det.open = !beginner;
    const sum = document.createElement("summary");
    sum.innerHTML = `<span class="adv-badge">進階</span>` +
      `<span class="adv-note">${div.dataset.note || "深入細節 — 初學者可先跳過，不影響主線理解"}</span>`;
    det.appendChild(sum);
    const bodyWrap = document.createElement("div");
    bodyWrap.className = "adv-body";
    while (div.firstChild) bodyWrap.appendChild(div.firstChild);
    det.appendChild(bodyWrap);
    div.replaceWith(det);
    advBlocks.push(det);
  });
  renderModeBtn();

  /* ===== 閱讀時間 + 難度標示（插在 h1 之後） ===== */
  if (!isIndex) {
    const h1 = document.querySelector("main h1");
    const main = document.querySelector("main");
    if (h1 && main) {
      const chars = (main.innerText || "").replace(/\s+/g, "").length;
      const mins = Math.max(1, Math.round(chars / 350));
      const level = document.body.dataset.level || "";
      const advCount = advBlocks.length;
      const meta = document.createElement("div");
      meta.className = "page-meta";
      meta.innerHTML =
        `<span>⏱ 全文約 ${mins} 分鐘</span>` +
        (level ? `<span class="lv lv-${level === "入門" ? "e" : level === "中階" ? "m" : "h"}">難度：${level}</span>` : "") +
        (advCount ? `<span>🎓 進階段落 ${advCount} 個${beginner ? "（已為你收合）" : ""}</span>` : "");
      h1.after(meta);
    }
  }

  /* ===== 術語 tooltip：<span class="term" data-term="mcp">MCP</span> ===== */
  const tip = document.createElement("div");
  tip.id = "term-tip";
  tip.setAttribute("hidden", "");
  document.body.appendChild(tip);
  let tipFor = null;
  function hideTip() { tip.setAttribute("hidden", ""); tipFor = null; }
  function showTip(el) {
    const key = el.dataset.term;
    const g = GLOSSARY[key];
    if (!g) return;
    tip.innerHTML =
      `<div class="tt-head">${g.t}<span class="tt-en">${g.en}</span></div>` +
      `<div class="tt-body">${g.d}</div>` +
      `<a class="tt-more" href="${root}appendix/index.html#g-${key}">查看附錄詞彙表 →</a>`;
    tip.removeAttribute("hidden");
    const r = el.getBoundingClientRect();
    const tw = Math.min(360, innerWidth - 24);
    tip.style.maxWidth = tw + "px";
    let x = r.left + scrollX;
    if (x + tw > scrollX + innerWidth - 12) x = scrollX + innerWidth - tw - 12;
    tip.style.left = Math.max(scrollX + 12, x) + "px";
    tip.style.top = (r.bottom + scrollY + 8) + "px";
    tipFor = el;
  }
  document.querySelectorAll(".term[data-term]").forEach(el => {
    if (!GLOSSARY[el.dataset.term]) { el.classList.add("term-missing"); return; }
    el.setAttribute("tabindex", "0");
    el.setAttribute("role", "button");
    el.title = "點一下看白話解釋";
    el.addEventListener("click", e => {
      e.stopPropagation();
      tipFor === el ? hideTip() : showTip(el);
    });
    el.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); tipFor === el ? hideTip() : showTip(el); }
    });
  });
  document.addEventListener("click", e => { if (!tip.contains(e.target)) hideTip(); });
  addEventListener("scroll", () => { if (tipFor) hideTip(); }, { passive: true });

  /* ===== 全文搜尋（離線；索引由 assets/search-index.js 預先建好） ===== */
  const overlay = document.createElement("div");
  overlay.id = "search-overlay";
  overlay.setAttribute("hidden", "");
  overlay.innerHTML =
    `<div class="search-box">` +
    `<div class="search-input-row"><input type="search" id="search-input" placeholder="搜尋全書…（例如：對帳、MCP、部署）" autocomplete="off">` +
    `<button type="button" id="search-close" title="關閉（Esc）">✕</button></div>` +
    `<div id="search-hint">輸入 2 個字以上開始搜尋 · Esc 關閉</div>` +
    `<div id="search-results"></div></div>`;
  document.body.appendChild(overlay);
  const sInput = overlay.querySelector("#search-input");
  const sResults = overlay.querySelector("#search-results");
  const sHint = overlay.querySelector("#search-hint");
  let indexLoaded = false, indexLoading = false;

  function openSearch() {
    overlay.removeAttribute("hidden");
    sInput.focus();
    if (!indexLoaded && !indexLoading) {
      indexLoading = true;
      const s = document.createElement("script");
      s.src = root + "assets/search-index.js";
      s.onload = () => { indexLoaded = true; runSearch(); };
      s.onerror = () => { sHint.textContent = "搜尋索引載入失敗（assets/search-index.js 不存在？請執行 build-search-index.py 重建）"; };
      document.body.appendChild(s);
    }
  }
  function closeSearch() { overlay.setAttribute("hidden", ""); }
  document.getElementById("search-toggle").addEventListener("click", openSearch);
  overlay.querySelector("#search-close").addEventListener("click", closeSearch);
  overlay.addEventListener("click", e => { if (e.target === overlay) closeSearch(); });
  addEventListener("keydown", e => {
    if (e.key === "/" && overlay.hasAttribute("hidden") &&
        !/^(input|textarea)$/i.test(document.activeElement?.tagName || "")) {
      e.preventDefault(); openSearch();
    }
    if (e.key === "Escape" && !overlay.hasAttribute("hidden")) closeSearch();
  });

  function esc(s) { return s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }
  function snippet(text, q) {
    const i = text.toLowerCase().indexOf(q);
    if (i < 0) return esc(text.slice(0, 80)) + "…";
    const from = Math.max(0, i - 40);
    const piece = text.slice(from, i + q.length + 60);
    return (from > 0 ? "…" : "") +
      esc(piece).replace(new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi"), m => `<mark>${m}</mark>`) + "…";
  }
  function runSearch() {
    const q = sInput.value.trim().toLowerCase();
    if (!indexLoaded || q.length < 2) { sResults.innerHTML = ""; sHint.style.display = ""; return; }
    sHint.style.display = "none";
    const hits = [];
    (window.BOOK_SEARCH_INDEX || []).forEach(ch => {
      ch.s.forEach(sec => {
        const hay = (sec.h + " " + sec.x).toLowerCase();
        const n = hay.split(q).length - 1;
        if (n > 0) hits.push({ ch, sec, n });
      });
    });
    hits.sort((a, b) => b.n - a.n);
    if (!hits.length) { sResults.innerHTML = `<div class="sr-empty">找不到「${esc(sInput.value)}」——試試同義詞（例如「對帳」/「reconcile」）或查附錄詞彙表。</div>`; return; }
    sResults.innerHTML = hits.slice(0, 30).map(h =>
      `<a class="sr-item" href="${root}${h.ch.p}${h.sec.a ? "#" + h.sec.a : ""}">` +
      `<div class="sr-ch">${esc(h.ch.t)}${h.sec.h ? " › " + esc(h.sec.h) : ""}</div>` +
      `<div class="sr-snip">${snippet(h.sec.x, q)}</div></a>`).join("");
  }
  sInput.addEventListener("input", runSearch);

  /* 上一章 / 下一章 */
  if (!isIndex && idx > 0) {
    const main = document.querySelector("main");
    if (main) {
      const nav = document.createElement("nav");
      nav.className = "chapter-nav";
      const prev = CHAPTERS[idx - 1], next = CHAPTERS[idx + 1];
      let html = "";
      if (prev) html += `<a href="${root}${prev.path}"><span class="dir">← 上一章</span>${prev.title}</a>`;
      html += `<a class="toc-link" href="${root}index.html"><span class="dir">☰</span>總目錄</a>`;
      if (next) html += `<a class="next" href="${root}${next.path}"><span class="dir">下一章 →</span>${next.title}</a>`;
      nav.innerHTML = html;
      main.appendChild(nav);
    }
    const footer = document.createElement("footer");
    footer.className = "book-footer";
    footer.textContent = "Anthropic Financial Agents 完整開發指南 — 以本 repo 之 managed-agent-cookbooks 為準";
    document.body.appendChild(footer);
  }

  /* 頁籤 */
  document.querySelectorAll(".tabs").forEach(tabs => {
    const btns = tabs.querySelectorAll(".tab-bar button");
    const panels = tabs.querySelectorAll(".tab-panel");
    btns.forEach((b, i) => b.addEventListener("click", () => {
      btns.forEach(x => x.classList.remove("active"));
      panels.forEach(x => x.classList.remove("active"));
      b.classList.add("active");
      if (panels[i]) panels[i].classList.add("active");
    }));
    if (btns[0]) { btns[0].classList.add("active"); panels[0]?.classList.add("active"); }
  });

  /* 程式碼複製按鈕 */
  document.querySelectorAll("pre:not(.diagram)").forEach(pre => {
    const btn = document.createElement("button");
    btn.className = "copy-btn"; btn.type = "button"; btn.textContent = "複製";
    btn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(pre.querySelector("code")?.innerText || pre.innerText);
        btn.textContent = "已複製 ✓";
      } catch { btn.textContent = "複製失敗"; }
      setTimeout(() => (btn.textContent = "複製"), 1500);
    });
    pre.appendChild(btn);
  });

  /* 流程動畫：.flow 內的 .step 依序點亮 */
  document.querySelectorAll(".flow[data-animate]").forEach(flow => {
    const steps = flow.querySelectorAll(".step");
    let timer = null, i = -1;
    const controls = document.createElement("div");
    controls.className = "flow-controls";
    controls.innerHTML = `<button type="button" class="play">▶ 播放流程</button><button type="button" class="reset">↺ 重設</button>`;
    flow.after(controls);
    const tick = () => {
      i++;
      steps.forEach((s, j) => s.classList.toggle("lit", j === i));
      if (i >= steps.length) { clearInterval(timer); timer = null; i = -1; steps.forEach(s => s.classList.remove("lit")); }
    };
    controls.querySelector(".play").addEventListener("click", () => {
      if (timer) return;
      i = -1; tick(); timer = setInterval(tick, 1100);
    });
    controls.querySelector(".reset").addEventListener("click", () => {
      clearInterval(timer); timer = null; i = -1; steps.forEach(s => s.classList.remove("lit"));
    });
  });

  /* 測驗：<div class="quiz" data-answer="2"><div class="q">…</div><label>…</label>…<div class="explain">…</div></div> */
  document.querySelectorAll(".quiz").forEach(quiz => {
    const ans = parseInt(quiz.dataset.answer, 10);
    const labels = quiz.querySelectorAll("label");
    labels.forEach((label, i) => label.addEventListener("click", () => {
      if (quiz.classList.contains("answered")) return;
      quiz.classList.add("answered");
      label.classList.add(i === ans ? "correct" : "wrong");
      if (i !== ans && labels[ans]) labels[ans].classList.add("correct");
    }));
  });

  /* 檢核清單：點擊打勾，localStorage 記憶 */
  document.querySelectorAll(".checklist").forEach((list, li_i) => {
    const key = `bookck-${chId}-${li_i}`;
    const saved2 = JSON.parse(localStorage.getItem(key) || "[]");
    list.querySelectorAll("li").forEach((li, i) => {
      if (saved2.includes(i)) li.classList.add("done");
      li.addEventListener("click", e => {
        if (e.target.closest("a")) return; /* 清單裡的連結照常可點 */
        li.classList.toggle("done");
        const done = [...list.querySelectorAll("li")]
          .map((x, j) => (x.classList.contains("done") ? j : -1)).filter(j => j >= 0);
        localStorage.setItem(key, JSON.stringify(done));
      });
    });
  });
})();
