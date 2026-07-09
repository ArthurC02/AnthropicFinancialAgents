# Anthropic Financial Agents 完整開發指南（電子書）

寫給要把這套 Financial Agents 以 **CMA（Claude Managed Agents）模式**落地到銀行 AWS 環境的團隊——從零基礎的概念導讀（第 0 章），到認識架構、客製與新開發 agent、整合行內系統（MCP）、部署、編排、安全合規、治理、維運與測試。**初級與非工程背景讀者（PM／法遵）也讀得完主線**：進階細節收在可摺疊的進階區塊，術語點擊即看白話解釋。

## 怎麼開始讀

直接用瀏覽器開 [`index.html`](./index.html)（總目錄，含三條角色導向學習路徑）。全書純靜態 HTML/CSS/JS、離線可讀。

閱讀輔助（頁面右上角）：

- **🌱 初學者模式**（預設開啟）：進階段落自動收合，主線更好讀；切到完整模式即全部展開。
- **🔍 全文搜尋**（快捷鍵 `/`）：離線可用，索引預先建好。
- **🌓 深淺色主題**切換。
- 內文**虛線術語**點一下即彈出白話解釋，並可連到附錄詞彙表詳解。
- 每章標示**難度**（入門／中階／進階）與**預估閱讀時間**。

```
Guidbook/
├── index.html               # 總目錄（從這裡開始；含角色學習路徑）
├── assets/
│   ├── book.css             # 全書共用樣式
│   ├── book.js              # 導覽/主題/互動元件/術語表 GLOSSARY/初學者模式/搜尋 UI
│   ├── search-index.js      # 全文搜尋索引（自動產生，勿手改）
│   ├── build-search-index.py# 重建搜尋索引的腳本
│   └── CHAPTER-SPEC.md      # 章節撰寫規格（新增/改章前必讀）
├── ch00-basics/             # 第 0 章：零基礎概念導讀（每章一個資料夾，內含 index.html）
├── ch01-introduction/
├── …
├── ch12-testing-evals/
└── appendix/                # 詞彙表（tooltip 連結落點）、速查、疑難排解、檢核
```

## 維護規則

- 新增或改名章節：先改 `assets/book.js` 的 `CHAPTERS` 陣列，再照 `assets/CHAPTER-SPEC.md` 的骨架寫章節頁（header/footer/主題/搜尋由 book.js 自動注入，章節頁不要自帶）。
- **改完任何章節內容，必跑** `python3 Guidbook/assets/build-search-index.py` 重建搜尋索引，否則新內容搜不到。
- 新增術語：在 `assets/book.js` 的 `GLOSSARY` 加一筆（key 用小寫連字號），並在 `appendix/index.html` 詞彙表加對應列（`<tr id="g-<key>">`）——tooltip 的「查看附錄詞彙表 →」連結指向這個錨點。
- 內容正確性以 repo 實際檔案為準（`managed-agent-cookbooks/`、`scripts/`、`docs/`、`mock-mcp/`）；repo 行為變更時，優先更新對應章節的程式碼引用段落。
- 白話化寫作鐵則（術語三件套、先比喻再精確、進階內容進 `.adv` 區塊等）見 `assets/CHAPTER-SPEC.md`。
- 不引入外部 CDN / 字型 / 圖片，保持離線可讀。
