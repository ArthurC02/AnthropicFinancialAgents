/* ===== Anthropic Financial Agents 開發指南 — 共用腳本 =====
 * 每個章節頁 <body data-chapter="ch03"> 即可自動獲得：
 * 頁首導覽、主題切換、進度條、上一章/下一章、頁籤、複製按鈕、流程動畫、測驗、檢核清單
 */

const CHAPTERS = [
  { id: "index", title: "總目錄", path: "index.html" },
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

  /* 上一章 / 下一章 */
  if (!isIndex && idx > 0) {
    const main = document.querySelector("main");
    if (main) {
      const nav = document.createElement("nav");
      nav.className = "chapter-nav";
      const prev = CHAPTERS[idx - 1], next = CHAPTERS[idx + 1];
      let html = "";
      if (prev) html += `<a href="${root}${prev.path}"><span class="dir">← 上一章</span>${prev.title}</a>`;
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
      li.addEventListener("click", () => {
        li.classList.toggle("done");
        const done = [...list.querySelectorAll("li")]
          .map((x, j) => (x.classList.contains("done") ? j : -1)).filter(j => j >= 0);
        localStorage.setItem(key, JSON.stringify(done));
      });
    });
  });
})();
