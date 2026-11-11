// 渲染首頁清單、搜尋、標籤篩選，以及筆記頁的上一篇／下一篇。
// 資料來源只有 assets/notes-index.js 的 window.NOTES。
(function () {
  "use strict";
  var notes = Array.isArray(window.NOTES) ? window.NOTES : [];

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function lessonNo(id) {
    return id.split("-")[0];
  }

  // ---------- 首頁 ----------
  var list = document.getElementById("note-list");
  if (list) {
    var base = list.getAttribute("data-base") || "notes/";
    var search = document.getElementById("note-search");
    var filterBox = document.getElementById("tag-filter");
    var activeTag = "";

    var tags = [];
    notes.forEach(function (n) {
      (n.tags || []).forEach(function (t) { if (tags.indexOf(t) === -1) tags.push(t); });
    });

    function makeTagButton(label, value) {
      var b = el("button", "", label);
      b.type = "button";
      b.setAttribute("aria-pressed", value === activeTag ? "true" : "false");
      b.addEventListener("click", function () { activeTag = value; render(); });
      return b;
    }

    function render() {
      var q = (search && search.value || "").trim().toLowerCase();
      if (filterBox) {
        filterBox.replaceChildren(makeTagButton("全部", ""));
        tags.forEach(function (t) { filterBox.appendChild(makeTagButton(t, t)); });
      }
      list.replaceChildren();
      var shown = notes.filter(function (n) {
        var text = (n.title + " " + n.summary + " " + (n.tags || []).join(" ")).toLowerCase();
        var okTag = !activeTag || (n.tags || []).indexOf(activeTag) !== -1;
        return okTag && (!q || text.indexOf(q) !== -1);
      });
      shown.forEach(function (n) {
        var li = el("li", "note-card");
        var a = el("a");
        a.href = base + n.id + ".html";
        a.appendChild(el("span", "num", lessonNo(n.id)));
        a.appendChild(el("span", "title", n.title));
        a.appendChild(el("span", "summary", n.summary));
        var meta = el("span", "meta");
        (n.tags || []).forEach(function (t) { meta.appendChild(el("span", "tag", t)); });
        meta.appendChild(document.createTextNode("更新：" + n.updated));
        a.appendChild(meta);
        li.appendChild(a);
        list.appendChild(li);
      });
      if (!shown.length) list.appendChild(el("li", "empty", "找不到符合的筆記。"));
    }

    if (search) search.addEventListener("input", render);
    render();
  }

  // ---------- 筆記頁 ----------
  var noteId = document.body.getAttribute("data-note-id");
  if (noteId) {
    var i = -1;
    notes.forEach(function (n, idx) { if (n.id === noteId) i = idx; });
    var me = notes[i];

    var metaBox = document.getElementById("note-meta");
    if (metaBox && me) {
      metaBox.textContent = "更新：" + me.updated + "　標籤：" + (me.tags || []).join("、");
    }

    var nav = document.getElementById("note-nav");
    if (nav && i !== -1) {
      [[i - 1, "prev", "上一篇"], [i + 1, "next", "下一篇"]].forEach(function (item) {
        var n = notes[item[0]];
        if (!n) { nav.appendChild(el("span")); return; }
        var a = el("a", item[1]);
        a.href = n.id + ".html";
        a.appendChild(el("small", "", item[2]));
        a.appendChild(document.createTextNode(lessonNo(n.id) + "｜" + n.title));
        nav.appendChild(a);
      });
    }
  }
})();
