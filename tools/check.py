#!/usr/bin/env python3
"""檢查專案是否符合 AGENTS.md 的規則。用法：python3 tools/check.py

只使用 Python 標準函式庫，不需要安裝任何套件。
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_BLOCKS = ["summary", "rules", "examples", "pitfalls", "cheatsheet", "quiz"]
FILE_PATTERN = re.compile(r"^\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KANJI = re.compile(r"[一-鿿]")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")

errors = []


def fail(where, msg):
    errors.append(f"[{where}] {msg}")


class NoteParser(HTMLParser):
    """收集 data-block 順序、例句中沒有讀音的漢字、內嵌樣式等資訊。"""

    def __init__(self):
        super().__init__()
        self.body_id = None
        self.title = ""
        self.blocks = []
        self.inline_style = False
        self.in_title = False
        self.in_jp = 0          # 位於 <p class="jp"> 內
        self.in_ruby = 0        # 位於 <ruby> 內
        self.bare_kanji = []    # 例句中不在 <ruby> 裡的漢字

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "style" in a or tag == "style":
            self.inline_style = True
        if tag == "body":
            self.body_id = a.get("data-note-id")
        if tag == "title":
            self.in_title = True
        if tag == "section" and "block" in (a.get("class") or "").split():
            self.blocks.append(a.get("data-block"))
        if tag == "p" and "jp" in (a.get("class") or "").split():
            self.in_jp += 1
        if tag == "ruby":
            self.in_ruby += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "p" and self.in_jp:
            self.in_jp -= 1
        if tag == "ruby" and self.in_ruby:
            self.in_ruby -= 1

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_jp and not self.in_ruby:
            self.bare_kanji += KANJI.findall(data)


def load_index():
    path = ROOT / "assets" / "notes-index.js"
    text = path.read_text(encoding="utf-8")
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        fail("notes-index.js", "找不到 window.NOTES 陣列")
        return []
    try:
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError as exc:
        fail("notes-index.js", f"不是嚴格的 JSON（雙引號、不可有結尾逗號）：{exc}")
        return []
    return data


def check_index(notes):
    seen = set()
    prev_no = 0
    for i, n in enumerate(notes):
        where = f"notes-index.js #{i + 1}"
        for key in ["id", "title", "summary", "tags", "updated"]:
            if key not in n:
                fail(where, f"缺少欄位 {key}")
        nid = n.get("id", "")
        if not FILE_PATTERN.match(nid):
            fail(where, f"id「{nid}」不符合 NN-slug 格式（兩位數字、英文小寫、用 - 連接）")
            continue
        if nid in seen:
            fail(where, f"id「{nid}」重複")
        seen.add(nid)
        no = int(nid[:2])
        if no != prev_no + 1:
            fail(where, f"編號應為 {prev_no + 1:02d}，實際為 {no:02d}（不重複、不跳號、依課程順序）")
        prev_no = no
        if not (ROOT / "notes" / f"{nid}.html").exists():
            fail(where, f"找不到對應檔案 notes/{nid}.html")
        if not DATE_PATTERN.match(str(n.get("updated", ""))):
            fail(where, "updated 必須是 YYYY-MM-DD")
        if not isinstance(n.get("tags"), list) or not n.get("tags"):
            fail(where, "tags 必須是至少一個標籤的陣列")
    return seen


def check_note(path, entry):
    where = f"notes/{path.name}"
    html = path.read_text(encoding="utf-8")
    p = NoteParser()
    p.feed(html)

    if p.body_id != path.stem:
        fail(where, f"<body data-note-id> 應為「{path.stem}」，實際為「{p.body_id}」")
    if p.blocks != REQUIRED_BLOCKS:
        fail(where, f"區塊必須依序為 {REQUIRED_BLOCKS}，實際為 {p.blocks}")
    expected_title = f"第 {path.stem[:2]} 課｜{entry['title']}｜日文課筆記" if entry else None
    if expected_title and p.title.strip() != expected_title:
        fail(where, f"<title> 應為「{expected_title}」")
    if p.inline_style:
        fail(where, "不可使用 style 屬性或 <style>，樣式請寫在 assets/style.css")
    if p.bare_kanji:
        sample = "".join(sorted(set(p.bare_kanji)))[:20]
        fail(where, f"例句中有漢字沒有 <ruby> 讀音：{sample}")
    if EMOJI.search(html):
        fail(where, "不可使用 emoji")
    for needed in ['href="../assets/style.css"', 'src="../assets/notes-index.js"',
                   'src="../assets/main.js"', 'id="note-nav"']:
        if needed not in html:
            fail(where, f"缺少共用元素：{needed}")


def main():
    notes = load_index()
    ids = check_index(notes)
    by_id = {n.get("id"): n for n in notes}

    for path in sorted((ROOT / "notes").glob("*.html")):
        if path.stem not in ids:
            fail(f"notes/{path.name}", "這個檔案沒有登記在 assets/notes-index.js")
        check_note(path, by_id.get(path.stem))

    if errors:
        print(f"發現 {len(errors)} 個問題：")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print(f"全部通過：共 {len(notes)} 篇筆記，皆符合 AGENTS.md 規則。")


if __name__ == "__main__":
    main()
