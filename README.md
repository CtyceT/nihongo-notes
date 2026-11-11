# 日文課筆記站（Nihongo Notes）

把日文課的內容整理成「一個主題一頁」的筆記網站，方便開卷考查閱與複習。
每頁都有固定的六個區塊：**一句話重點、規則、例句、易混淆、開卷速查、自我小測**。

- 網站：https://【你的 GitHub 帳號】.github.io/nihongo-notes/
- 專案規則：[AGENTS.md](AGENTS.md)（給 AI 讀的開發規則；CLAUDE.md 會引用它）

## 目前的筆記

| 編號 | 主題 |
|---|---|
| 01 | 五十音：平假名與片假名 |
| 02 | 基本助詞：は・が・を・に・で・へ・と・の・も |
| 03 | 動詞三分類與ます形 |

## 請 AI 新增一篇筆記

在專案資料夾中打開 Claude Code（或其他會讀 AGENTS.md 的 AI 工具），直接說：

> 依照 AGENTS.md，新增第 04 課「形容詞（い形・な形）」的筆記。內容如下：（貼上講義重點）

AI 會依規則複製樣板、填好六個區塊、登記到 `assets/notes-index.js`，並執行 `python3 tools/check.py` 驗證。首頁清單與上下頁導覽會自動更新。

## 本機預覽

```bash
python3 -m http.server 8000
```
或直接用瀏覽器打開 `index.html`。

## 檢查規則

```bash
python3 tools/check.py
```
會檢查：檔名與編號、筆記是否登記、六個區塊的順序、`<title>` 格式、例句漢字是否都有讀音、是否有內嵌樣式或 emoji。
