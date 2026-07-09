#!/usr/bin/env python3
"""建立全書離線搜尋索引 → Guidbook/assets/search-index.js

用法（在 repo 根目錄或任何位置皆可）：
    python3 Guidbook/assets/build-search-index.py

原理：讀 book.js 的 CHAPTERS 陣列取得章節清單，逐章把 index.html
按 <h2 id="..."> 切成小節、抽純文字，輸出成 window.BOOK_SEARCH_INDEX。
純標準函式庫，無外部依賴。改完任何章節內容都要重跑一次。
"""
import html
import json
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parent
GUIDBOOK = ASSETS.parent


def load_chapters():
    """從 book.js 讀 CHAPTERS（單一事實來源，避免兩處清單漂移）。"""
    src = (ASSETS / "book.js").read_text(encoding="utf-8")
    m = re.search(r"const CHAPTERS = \[(.*?)\];", src, re.S)
    chapters = []
    for item in re.finditer(
        r'\{\s*id:\s*"([^"]+)",\s*title:\s*"([^"]+)",\s*path:\s*"([^"]+)"', m.group(1)
    ):
        chapters.append({"id": item.group(1), "title": item.group(2), "path": item.group(3)})
    return chapters


def strip_tags(fragment: str) -> str:
    fragment = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", fragment, flags=re.S | re.I)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def index_chapter(path: Path):
    doc = path.read_text(encoding="utf-8")
    body = re.search(r"<main[^>]*>(.*?)</main>", doc, re.S)
    body = body.group(1) if body else doc
    sections = []
    # 依 <h2 id="..."> 切段；第一段（h2 之前的導言）錨點留空
    parts = re.split(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', body, flags=re.S)
    lead = strip_tags(parts[0])
    if lead:
        sections.append({"a": "", "h": "", "x": lead[:1500]})
    for i in range(1, len(parts), 3):
        anchor, heading, content = parts[i], strip_tags(parts[i + 1]), strip_tags(parts[i + 2])
        if content:
            sections.append({"a": anchor, "h": heading, "x": content[:4000]})
    return sections


def main():
    out = []
    for ch in load_chapters():
        if ch["id"] == "index":
            continue
        page = GUIDBOOK / ch["path"]
        if not page.exists():
            print(f"WARN: {page} 不存在，跳過")
            continue
        out.append({"c": ch["id"], "t": ch["title"], "p": ch["path"], "s": index_chapter(page)})
    js = "/* 自動產生，勿手改 — python3 Guidbook/assets/build-search-index.py */\n" \
         "window.BOOK_SEARCH_INDEX = " + json.dumps(out, ensure_ascii=False) + ";\n"
    (ASSETS / "search-index.js").write_text(js, encoding="utf-8")
    total = sum(len(c["s"]) for c in out)
    print(f"OK: {len(out)} 章、{total} 小節 → assets/search-index.js")


if __name__ == "__main__":
    main()
