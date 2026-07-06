# Anthropic Financial Agents 完整開發指南（電子書）

寫給要把這套 Financial Agents 以 **CMA（Claude Managed Agents）模式**落地到銀行 AWS 環境的工程師：從認識架構、客製與新開發 agent、整合行內系統（MCP）、部署、編排，到安全合規、治理、維運與測試。

## 怎麼開始讀

直接用瀏覽器開 [`index.html`](./index.html)（總目錄）。全書純靜態 HTML/CSS/JS、離線可讀、支援深淺色主題（右上角切換）。

```
Guidbook/
├── index.html               # 總目錄（從這裡開始）
├── assets/
│   ├── book.css             # 全書共用樣式
│   ├── book.js              # 導覽/主題/互動元件（章節清單定義於此）
│   └── CHAPTER-SPEC.md      # 章節撰寫規格（新增/改章前必讀）
├── ch01-introduction/       # 每章一個資料夾，內含 index.html
├── ch02-architecture/
├── …
├── ch12-testing-evals/
└── appendix/
```

## 維護規則

- 新增或改名章節：先改 `assets/book.js` 的 `CHAPTERS` 陣列，再照 `assets/CHAPTER-SPEC.md` 的骨架寫章節頁（header/footer/導覽由 book.js 自動注入，章節頁不要自帶）。
- 內容正確性以 repo 實際檔案為準（`managed-agent-cookbooks/`、`scripts/`、`docs/`、`mock-mcp/`）；repo 行為變更時，優先更新對應章節的程式碼引用段落。
- 不引入外部 CDN / 字型 / 圖片，保持離線可讀。
