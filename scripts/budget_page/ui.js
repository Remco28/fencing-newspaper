/* En Garde Gazette — standalone budget page: rendering + interactions.
   All data is inlined (#budget-data); logic lives in BudgetCore (core.js). No network: Vet is local,
   Submit downloads + copies a JSON file, progress autosaves to localStorage. */
(function () {
  "use strict";
  var Core = window.BudgetCore;
  var $ = function (id) { return document.getElementById(id); };
  var DATA, M, S, STORE_KEY, storage = null, ui = { open: {}, jumpIdx: {}, last: null };
  var saveTimer = 0, totalsTimer = 0;

  function esc(s) {
    return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function attrSel(v) { return String(v).replace(/["\\]/g, "\\$&"); }
  function fmtTime(iso) {
    var d = iso ? new Date(iso) : null;
    return d && !isNaN(d) ? d.toLocaleString("en-US", { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }) : "";
  }
  function fmtDay(v) {
    var d = v ? new Date(v + "T12:00:00") : null;
    return d && !isNaN(d) ? d.toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" }) : "";
  }
  function thumbHtml(file, cls) {
    var t = file && M.thumbs[file];
    if (!t) return file ? '<div class="nothumb">No thumbnail</div>' : "";
    return '<img class="' + (cls || "thumb") + '" alt="" decoding="async" src="' + t.src + '" width="' + t.w + '" height="' + t.h + '" />';
  }

  /* ---------- storage ---------- */
  function probeStorage() {
    try { var k = "__gazette_probe__"; window.localStorage.setItem(k, "1"); window.localStorage.removeItem(k); return window.localStorage; }
    catch (e) { return null; }
  }
  function saveNow() {
    clearTimeout(saveTimer); saveTimer = 0;
    if (!storage) return;
    S.savedAt = new Date().toISOString();
    try { storage.setItem(STORE_KEY, JSON.stringify(S)); }
    catch (e) { storage = null; notice("warn", "Couldn't save progress on this device (storage full or blocked). Finish in one sitting, or Submit early."); }
  }
  function changed(opts) {
    clearTimeout(saveTimer); saveTimer = setTimeout(saveNow, 400);
    if (!opts || !opts.noTotals) { clearTimeout(totalsTimer); totalsTimer = setTimeout(updateTotals, 120); }
    else { clearTimeout(totalsTimer); totalsTimer = setTimeout(updateDirty, 300); }
  }

  /* ---------- notices / status ---------- */
  function notice(kind, html) {
    var d = document.createElement("div");
    d.className = "notice" + (kind === "warn" ? " warn" : "");
    d.innerHTML = "<span>" + html + '</span><button type="button" aria-label="Dismiss" data-act="dismiss">✕</button>';
    $("notices").appendChild(d);
  }
  function status(cls, html) { var s = $("status"); s.className = cls || ""; s.innerHTML = html; }
  function toast(html) { $("toastMsg").innerHTML = html; $("toast").classList.add("show"); }

  /* ---------- cards ---------- */
  function hostAttrs(s) { return ' data-key="' + esc(s.key) + '" data-item-id="' + esc(s.item || "") + '"'; }

  function statusHtml(s, it) {
    var missing = Core.isMissing(M, s), onFile = Core.vettedOnFile(M, s.item), local = !onFile && !!(s.item && S.vets[s.item]);
    var nq = Core.openQuestions(M, S, s), nqAll = Core.questionsFor(s, it).length, info = [], pill;
    if (missing) pill = '<span class="pill missing">Not in staging</span>';
    else if (s.waiting) pill = '<span class="pill wait">Waiting on results</span>';
    else if (!onFile && !local) pill = '<span class="pill vet">Needs your vet</span>';
    else if (nq) pill = '<span class="pill q">Question for you</span>';
    else if (local) pill = '<span class="pill mine">✓ Vetted by you · not sent yet</span>';
    else pill = '<span class="pill ok">✓ Vetted' + (it && it.vet_scope === "angle_tone_only" ? " (angle &amp; tone)" : "") + "</span>";
    if (!missing && s.waiting) info.push(onFile || local ? "vetted" : "unvetted");
    if (nq && (missing || s.waiting || (!onFile && !local))) info.push(nq + (nq === 1 ? " question" : " questions") + " for you");
    else if (nqAll && !nq) info.push("questions answered");
    if (it && it.facts_status === "pending") info.push("facts pending");
    if (s.proposed && !missing && !onFile && !local) info.push("Desk proposes — goes in once vetted");
    else if (s.proposed && !missing) info.push("Desk proposes");
    if (s.auto) info.push("auto-placed from staging");
    return pill + (info.length ? '<span class="sec-info">' + esc(info.join(" · ")) + "</span>" : "");
  }

  function qsHtml(s, qs) {
    return '<div class="qs"><div class="qs-h">Questions for Frank</div>' + qs.map(function (q, i) {
      var a = S.answers[s.key + "|" + i], v = a ? a.a : "", id = "q-" + s.key + "-" + i;
      return '<div class="q' + (String(v).trim() ? " done" : "") + '"><label for="' + esc(id) + '"><span>' + esc(q) + "</span></label>" +
        '<textarea rows="1" id="' + esc(id) + '" data-q="' + esc(s.key + "|" + i) + '" placeholder="Type your answer">' + esc(v) + "</textarea></div>";
    }).join("") + "</div>";
  }

  function draftLabel(s, it) {
    var w = Core.itemWords(it);
    if (s.panels) return "See the board (" + s.panels.panels.reduce(function (n, p) { return n + p.rows.length; }, 0) + " events)";
    if (s.table && !it) return "See the table";
    if (it && it.schedule_rows) return "See the class table";
    if (s.cost && s.cost.type === "figure") return "Read Desk's description of the figure";
    if (it && /graf|qa|comic/.test(it.kind || "")) return "Read the draft · " + w + " words";
    if (s.table) return "See the table";
    return "Read the staging text";
  }
  function tableHtml(head, rows) {
    return '<div class="tscroll"><table class="t"><thead><tr>' + (head || []).map(function (h) { return "<th>" + esc(h) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      (rows || []).map(function (r) { return "<tr>" + (Array.isArray(r) ? r : [r]).map(function (c) { return "<td>" + esc(c) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table></div>";
  }
  function draftBody(s, it) {
    if (s.panels) {
      return s.panels.panels.map(function (p) { return '<div class="panel-h">' + esc(p.title) + "</div>" + tableHtml(s.panels.head, p.rows); }).join("");
    }
    if (s.table || (it && it.schedule_rows)) {
      var t = s.table || { head: ["Day", "Time", "Class"], rows: it.schedule_rows };
      return tableHtml(t.head, t.rows);
    }
    var body = String((it && it.body) || "");
    return '<div class="draft-body">' + body.split(/\n\s*\n/).map(function (p) {
      return "<p>" + esc(p.trim()).replace(/\n/g, "<br>").replace(/\[NEED:[^\]]*\]/g, function (m) { return "<mark>" + m + "</mark>"; }) + "</p>";
    }).join("") + "</div>" + (it && it.draft_path ? '<div class="hint">Draft file: <code>' + esc(it.draft_path) + "</code></div>" : "");
  }
  function provLine(p) {
    var bits = [];
    if (p.type) bits.push('<span class="lbl">' + esc(p.type) + "</span>");
    if (p.url) {
      var label = p.url;
      try { var u = new URL(p.url); label = u.hostname.replace(/^www\./, "") + u.pathname.replace(/\/$/, "").slice(0, 60); } catch (e) {}
      bits.push(/^https?:\/\//i.test(p.url) ? '<a href="' + esc(p.url) + '" target="_blank" rel="noopener noreferrer">' + esc(label) + "</a>" : esc(label));
    }
    if (p.source) bits.push(esc(p.source));
    if (p.author) bits.push(esc(p.author));
    if (p.from) bits.push(esc(p.from));
    if (p.subject) bits.push("“" + esc(p.subject) + "”");
    if (p.note) bits.push(esc(p.note));
    ["id", "path", "endpoint", "underlying", "method"].forEach(function (k) { if (p[k] && typeof p[k] !== "object") bits.push("<code>" + esc(p[k]) + "</code>"); });
    if (p.local_copy) bits.push("copy: <code>" + esc(p.local_copy) + "</code>");
    if (p.message_id) bits.push("<code>" + esc(p.message_id) + "</code>");
    var when = p.retrieved_at || p.fetched_at || p.posted_at || p.received_at;
    if (when) bits.push('<span class="lbl">' + esc(String(when).slice(0, 16).replace("T", " ")) + "</span>");
    return bits.join(" · ");
  }
  function provBody(s, it) {
    var prov = Array.isArray(it.provenance) ? it.provenance : [];
    var h = '<div class="prov-body">';
    h += '<div><span class="lbl">Item</span> <code>' + esc(it.id) + "</code> · " + esc(it.kind || "") + " · source " + esc(it.source || "—") + (it.from ? " · from " + esc(it.from) : "") + "</div>";
    if (it.vetted) h += '<div><span class="lbl">Vetted</span> by ' + esc(it.vetted_by || "?") + " · " + esc(String(it.vetted_at || "").slice(0, 16).replace("T", " ")) + "</div>";
    else if (S.vets[it.id]) h += '<div><span class="lbl">Vetted by you</span> on this page · not sent yet</div>';
    if (prov.length) h += "<ol>" + prov.filter(function (p) { return p && typeof p === "object"; }).map(function (p) { return "<li>" + provLine(p) + "</li>"; }).join("") + "</ol>";
    else if (it.message_id) h += "<div><code>" + esc(it.message_id) + "</code></div>";
    if (Array.isArray(it.facts) && it.facts.length) h += '<div class="lbl">Facts on file</div><ol>' + it.facts.map(function (f) { return "<li>" + esc(f && f.claim) + (f && f.status ? " — " + esc(f.status) : "") + "</li>"; }).join("") + "</ol>";
    if (it.claims_path) h += '<div><span class="lbl">Claim check</span> <code>' + esc(it.claims_path) + "</code></div>";
    if (it.vet_notes) h += '<div style="margin-top:6px"><span class="lbl">Desk / vet notes</span> ' + esc(it.vet_notes) + "</div>";
    if ((s.merged || []).length) h += '<div><span class="lbl">Merged</span> ' + s.merged.map(function (m) { return "<code>" + esc(m) + "</code>" + (M.byId[m] ? "" : " (not in staging)"); }).join(", ") + "</div>";
    return h + "</div>";
  }
  function detailsHtml(key, kind, label, bodyFn) {
    var open = !!ui.open[key + "|" + kind];
    return '<details class="x" data-lazy="' + kind + '"' + (open ? " open data-filled=\"1\"" : "") + "><summary>" + esc(label) + "</summary>" +
      (open ? '<div class="xb">' + bodyFn() + "</div>" : "") + "</details>";
  }
  function vetBoxHtml(id, what) {
    var v = S.vets[id];
    return '<div class="mine-box"><b>✓ Vetted by you — goes with your submission</b>' +
      '<label class="sr" for="vn-' + esc(id) + '">Vet note</label><input type="text" id="vn-' + esc(id) + '" data-vnote="' + esc(id) + '" value="' + esc(v.notes || "") + '" placeholder="Vet note for the bot (optional)" />' +
      '<button type="button" class="unvet" data-unvet="' + esc(id) + '">Un-vet ' + what + "</button></div>";
  }
  function moveHtml(s) {
    return '<div class="move"><button type="button" data-move="-1" aria-label="Move up: ' + esc(s.slot) + '">↑ Up</button><button type="button" data-move="1" aria-label="Move down: ' + esc(s.slot) + '">↓ Down</button></div>';
  }

  function cardHtml(s) {
    var it = s.item ? M.byId[s.item] || null : null;
    var qs = Core.questionsFor(s, it);
    if (s.empty) {
      return '<div class="empty-wrap" id="c-' + esc(s.key) + '"' + hostAttrs(s) + ' data-empty="1">' +
        '<div class="empty"><span class="slot">' + esc(s.slot) + "</span><span>Empty · " + esc(s.why || "") + "</span></div>" +
        (qs.length ? qsHtml(s, qs) : "") + "</div>";
    }
    var missing = Core.isMissing(M, s), onFile = Core.vettedOnFile(M, s.item), local = !onFile && !!(s.item && S.vets[s.item]);
    var vetted = onFile || local, on = Core.isIncluded(M, S, s);
    var cls = ["card"];
    if (missing) cls.push("missing"); else if (!vetted) cls.push("needs-vet"); else if (on) cls.push("is-in"); else cls.push("is-out");
    var summary = s.summary || (it && it.summary) || Core.firstSentence(it && it.body);
    var w = Core.itemWords(it), meta = [];
    if (s.cost && /table/.test(s.cost.type || "")) meta.push((s.cost.rows || "?") + " rows");
    else if (s.cost && s.cost.type === "figure") meta.push("figure, " + s.cost.span + " columns");
    else if (w && !(it && /signup_row|fact/.test(it.kind || ""))) meta.push(w + " words");
    if (s.budget) meta.push("budget " + s.budget);
    var thumbFile = s.thumb || (it && it.media_path && !/\.svg$/i.test(it.media_path) ? Core.fileOf(it.media_path) : "");
    var hasDraft = it || s.table || s.panels;
    var incLabel = on ? "In the issue" : missing ? "Include (not in staging)" : vetted ? "Include" : "Include (Vet first)";
    var locked = missing || !vetted;
    return '<article class="' + cls.join(" ") + '" id="c-' + esc(s.key) + '"' + hostAttrs(s) + ' data-vetted="' + vetted + '"' +
      (!missing && !vetted ? ' data-needs-vet="1"' : "") + (on ? ' data-in="1"' : "") + ">" +
      '<div class="c-main">' +
        '<div class="slotline"><span class="slot">' + esc(s.slot) + "</span><span>" + esc(meta.join(" · ")) + "</span></div>" +
        "<h3>" + esc(Core.headlineOf(s, it)) + "</h3>" +
        '<div class="status">' + statusHtml(s, it) + "</div>" +
        (missing ? '<p class="missing-note">' + (s.item ? "Item <code>" + esc(s.item) + "</code> is not in this week's staging (rolled out of <code>next</code>?). Can't be vetted or included from here." : "No staging item for this slot.") + "</p>" : "") +
        (summary ? '<p class="sum">' + esc(summary) + "</p>" : "") +
        (qs.length ? qsHtml(s, qs) : "") +
        ((s.flags || []).length ? '<ul class="flags">' + s.flags.map(function (f) { return '<li class="' + esc(f.level || "") + '">' + esc(f.text) + "</li>"; }).join("") + "</ul>" : "") +
        (hasDraft ? detailsHtml(s.key, "draft", draftLabel(s, it), function () { return draftBody(s, it); }) : "") +
        (it ? detailsHtml(s.key, "prov", "Source & provenance", function () { return provBody(s, it); }) : "") +
      "</div>" +
      '<div class="ctl">' +
        thumbHtml(thumbFile) +
        '<label class="inc' + (on ? " on" : "") + (locked ? " locked" : "") + '"><input type="checkbox" data-inc' + (on ? " checked" : "") + (locked ? " disabled" : "") + " /><span>" + esc(incLabel) + "</span></label>" +
        (!missing && !vetted ? '<button type="button" class="vet" data-vet="' + esc(s.item) + '">Vet this item</button>' : "") +
        (local ? vetBoxHtml(s.item, "item") : "") +
        '<label class="sr" for="n-' + esc(s.key) + '">Note to Desk</label><textarea class="note" rows="2" id="n-' + esc(s.key) + '" data-note="' + esc(s.key) + '" placeholder="Note to Desk (optional)">' + esc(S.slotNotes[s.key] || "") + "</textarea>" +
        moveHtml(s) +
      "</div></article>";
  }

  function photoHtml(p) {
    var m = M.mediaById[p.id] || {}, item = M.byId[p.id], present = Core.photoPresent(M, p);
    var onFile = Core.vettedOnFile(M, p.id), local = !onFile && !!S.vets[p.id], vetted = onFile || local;
    var on = Core.photoIncluded(M, S, p), file = m.filename || Core.fileOf(m.media_path), d = Core.photoDims(M, p);
    var pill = !present ? '<span class="pill missing">Not in staging</span>' : local ? '<span class="pill mine">✓ Vetted by you · not sent yet</span>' :
      vetted ? '<span class="pill ok">✓ Vetted</span>' : '<span class="pill vet">Needs your vet</span>';
    var info = [];
    if (p.proposed) info.push(present && !vetted ? "Desk proposes — goes in once vetted" : "Desk proposes");
    var cls = "ph" + (on ? " is-in" : present && !vetted ? " needs-vet" : "");
    return '<div class="' + cls + '" id="p-' + esc(p.id) + '" data-photo="' + esc(p.id) + '" data-item-id="' + esc(p.id) + '"' +
      (present && !vetted ? ' data-needs-vet="1"' : "") + (on ? ' data-in="1"' : "") + ">" +
      (file ? thumbHtml(file) : '<div class="nothumb">' + (present ? "No file" : "Not in this week's media") + "</div>") +
      '<div class="cap">' + esc(m.caption || (item && item.caption) || p.id) + "</div>" +
      '<div class="status">' + pill + (info.length ? '<span class="sec-info">' + esc(info.join(" · ")) + "</span>" : "") + "</div>" +
      (p.note ? '<div class="meta">' + esc(p.note) + "</div>" : "") +
      '<div class="meta">' + esc(file || p.id) + (m.w || (d[0] > 1) ? " · " + d[0] + "×" + d[1] : "") + (m.source ? " · " + esc(m.source) : "") + (m.license ? " · " + esc(m.license) : "") +
        (m.parent_item_id ? " · for <code>" + esc(m.parent_item_id) + "</code>" : "") + "</div>" +
      '<label class="inc' + (on ? " on" : "") + (vetted && present ? "" : " locked") + '"><input type="checkbox" data-pinc="' + esc(p.id) + '"' + (on ? " checked" : "") + (vetted && present ? "" : " disabled") + " /><span>" +
        (on ? "In the issue" : !present ? "Not in staging" : vetted ? "Include photo" : "Include (Vet first)") + "</span></label>" +
      (present && !vetted ? '<button type="button" class="vet" data-vet="' + esc(p.id) + '">Vet this photo</button>' : "") +
      (local ? vetBoxHtml(p.id, "photo") + (item ? "" : '<div class="hint">Media id — Desk records this vet from your submission.</div>') : "") +
      "</div>";
  }

  function heldHtml() {
    var cfg = M.cfg, rows = [];
    (cfg.held || []).forEach(function (h) { rows.push("<b>Held: " + esc(h.label || h.id || h.item) + "</b><span>" + esc(h.note || "") + "</span>"); });
    (cfg.not_proposed || []).forEach(function (n) {
      var it = M.byId[n.item];
      rows.push("<b>" + esc((it && it.headline) || n.item) + "</b><span>" + esc(n.why) + " · <code>" + esc(n.item) + "</code>" +
        (!it ? " · not in staging" : it.vetted === false ? " · unvetted" : "") + "</span>");
    });
    var seeds = M.items.filter(function (i) { return Core.isSeed(cfg, i); });
    if (seeds.length) rows.push("<b>Seed / pretend items excluded (" + seeds.length + ")</b><span>" + seeds.map(function (s) { return "<code>" + esc(s.id) + "</code>"; }).join(", ") + "</span>");
    if (!rows.length) rows.push("<span>Nothing held.</span>");
    return '<div class="held-list">' + rows.map(function (r) { return '<div class="held-row">' + r + "</div>"; }).join("") + "</div>";
  }

  function render() {
    var html = "";
    M.sections.forEach(function (sec) {
      html += '<section class="sec" id="sec-' + esc(sec.key) + '"><h2>' + esc(sec.title) + ' <span class="sc" data-sc="' + esc(sec.key) + '"></span></h2>' +
        (sec.hint ? '<p class="sec-hint">' + esc(sec.hint) + "</p>" : "");
      if (sec.type === "photos") html += M.photos.length ? '<div class="photos">' + M.photos.map(photoHtml).join("") + "</div>" : '<p class="sec-hint">No photos in staging.</p>';
      else if (sec.type === "held") html += heldHtml();
      else {
        var list = Core.sectionList(M, S, sec.key);
        html += list.length ? '<div class="cards" data-cards="' + esc(sec.key) + '">' + list.map(cardHtml).join("") + "</div>" : '<p class="sec-hint">Nothing slotted here.</p>';
      }
      html += "</section>";
    });
    $("sections").innerHTML = html;
    var links = M.sections.map(function (sec) {
      return '<a href="#sec-' + esc(sec.key) + '">' + esc(sec.title) + ' <span data-jc="' + esc(sec.key) + '"></span></a>';
    }).join("") + '<a href="#sec-notes">Notes &amp; submit <span></span></a>';
    $("jumpSide").innerHTML = links;
    $("jumpChips").innerHTML = links;
    document.querySelectorAll("[data-cards]").forEach(fixMoveButtons);
    updateTotals();
  }

  function rerenderHosts(id) {
    document.querySelectorAll('[data-item-id="' + attrSel(id) + '"]').forEach(function (el) {
      var key = el.getAttribute("data-key"), fresh = null;
      if (key) { var s = M.slotByKey[key]; if (s) fresh = cardHtml(s); }
      else if (el.hasAttribute("data-photo")) { var p = M.photos.filter(function (x) { return x.id === id; })[0]; if (p) fresh = photoHtml(p); }
      if (fresh) replaceNode(el, fresh);
    });
  }
  function rerenderKey(key) { var el = $("c-" + key), s = M.slotByKey[key]; if (el && s) replaceNode(el, cardHtml(s)); }
  function replaceNode(el, html) {
    var tmp = document.createElement("div"); tmp.innerHTML = html;
    var node = tmp.firstElementChild; el.replaceWith(node);
    var cards = node.closest("[data-cards]"); if (cards) fixMoveButtons(cards);
    return node;
  }
  function fixMoveButtons(container) {
    var cards = container.querySelectorAll("article.card");
    cards.forEach(function (c, i) {
      var up = c.querySelector('[data-move="-1"]'), dn = c.querySelector('[data-move="1"]');
      if (up) up.disabled = i === 0;
      if (dn) dn.disabled = i === cards.length - 1;
    });
  }

  /* ---------- totals (debounced; reads state, never the DOM) ---------- */
  function updateTotals() {
    clearTimeout(totalsTimer); totalsTimer = 0;
    var T = Core.computeTotals(M, S);
    $("mFill").style.width = T.fillPct + "%";
    $("mPend").style.width = T.pendPct + "%";
    $("mTick").style.left = T.tickPct + "%";
    $("meter").classList.toggle("over", T.over);
    var room = Math.abs(T.room).toLocaleString();
    $("fitLine").innerHTML = "<b>" + T.pct + "%</b>" +
      '<span class="long"> of two pages · ' + (T.room >= 0 ? "room for ≈ " + room + " words" : '<span class="over">over by ≈ ' + room + " words — cut from the bottom</span>") + "</span>" +
      '<span class="short"> full · ' + (T.room >= 0 ? "≈" + room + "w room" : '<span class="over">≈' + room + "w over</span>") +
      (T.pend ? ' <span class="proj">· ' + T.pctP + "% if vetted</span>" : "") + "</span>";
    $("fitProj").textContent = (T.pend ? T.pctP + "% if you Vet what Desk proposes · " : "") + "rough estimate · red tick = full";
    [["nIn", T.nIn], ["nVet", T.nVet], ["nQ", T.nQ]].forEach(function (x) { $(x[0]).textContent = x[1]; $(x[0]).parentNode.classList.toggle("zero", !x[1] && !(x[0] === "nVet" && T.nVetPh)); });
    $("nVetPh").textContent = T.nVetPh; $("nVetPhWrap").hidden = !T.nVetPh; $("nVetPhWrap").parentNode.classList.toggle("has-ph", !!T.nVetPh);
    Object.keys(T.labels).forEach(function (k) {
      var sc = document.querySelector('[data-sc="' + attrSel(k) + '"]'); if (sc) sc.textContent = T.labels[k];
      document.querySelectorAll('[data-jc="' + attrSel(k) + '"]').forEach(function (b) { b.textContent = T.labels[k]; });
    });
    updateDirty();
  }
  function updateDirty() {
    var d = $("dirty"), dirty = false;
    if (S.lastSubmit && S.lastSubmit.sig) {
      dirty = Core.payloadSig(Core.buildPayload(M, S, null)) !== S.lastSubmit.sig;
      d.textContent = dirty ? "Changed since your last submit (" + fmtTime(S.lastSubmit.at) + ") — Submit again to send the changes." : "";
    }
    d.classList.toggle("show", dirty);
    $("submitTop").classList.toggle("dirty", dirty);
    $("submitTop").textContent = dirty ? "Submit again" : "Submit";
  }

  /* ---------- header ---------- */
  function showDay() {
    var v = $("publishDate").value, pub = M.cfg.publish || {};
    $("publishDay").textContent = fmtDay(v) + (v && v === pub.date ? " · Desk's pick" : v && v === pub.alt ? " · Desk's alternate" : "");
    document.querySelectorAll("[data-pick]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-pick") === v)); });
    $("fileName").textContent = fileName(v);
  }
  function fileName(date) { return "budget-submission-no-" + ((M.cfg.issue || {}).number || "x") + "-" + (date || (M.cfg.publish || {}).date || "undated") + ".json"; }
  function renderHeader() {
    var cfg = M.cfg, iss = cfg.issue || {}, pub = cfg.publish || {}, real = cfg.mode === "real", b = M.build || {};
    $("issueLabel").textContent = iss.label || "Next issue";
    $("weekLabel").textContent = iss.week || "";
    $("barId").innerHTML = esc(iss.label || "Budget") + "<small>" + esc(iss.week || "") + "</small>";
    document.title = "Budget — " + (iss.label || "next issue") + (real ? "" : " (practice)");
    $("modeTag").textContent = real ? "Real budget · your submission goes to the Desk" : "Practice — not a real submission";
    $("modeTag").className = "mode" + (real ? "" : " practice");
    var picks = [];
    if (pub.date) picks.push('<button type="button" data-pick="' + esc(pub.date) + '">Desk\'s pick: ' + esc(fmtDay(pub.date)) + "</button>");
    if (pub.alt) picks.push('<button type="button" data-pick="' + esc(pub.alt) + '">Alternate: ' + esc(fmtDay(pub.alt)) + "</button>");
    $("datePicks").innerHTML = picks.join("");
    $("publishWhy").innerHTML = (pub.note ? esc(pub.note) : "") + (pub.why ? (pub.note ? "<br>" : "") + "<b>Why:</b> " + esc(pub.why) : "");
    $("deskList").innerHTML = (cfg.desk_summary || []).map(function (l) { return "<li>" + esc(l) + "</li>"; }).join("") || "<li>No summary from Desk.</li>";
    $("publishDate").value = S.publishDate || pub.date || "";
    $("globalNotes").value = S.notes || "";
    var miss = (b.missing && b.missing.items) || [];
    $("foot").innerHTML = "Locked footer (prints on every issue): “For fun only — facts aren't guaranteed accurate.”<br>" +
      "Built " + esc(fmtTime(b.generatedAt)) + " from <code>" + esc(b.stagingWeek || "?") + "</code> · lineup <code>" + esc(b.lineupPath || "?") + "</code> · data " + esc(b.dataVersion || "?") +
      (miss.length ? " · " + miss.length + " lineup item" + (miss.length === 1 ? "" : "s") + " not in staging" : "") + " · " + esc(Core.PAGE_VERSION);
    if (window.matchMedia && window.matchMedia("(max-width: 640px)").matches && (cfg.desk_summary || []).length > 4) $("desk").open = false;
    showDay();
  }

  /* ---------- interactions (event delegation) ---------- */
  document.addEventListener("change", function (e) {
    var t = e.target, host;
    if (t.matches("[data-inc]")) {
      host = t.closest("[data-key]"); S.inc[host.getAttribute("data-key")] = t.checked;
      var n = replaceNode(host, cardHtml(M.slotByKey[host.getAttribute("data-key")])); var box = n.querySelector("[data-inc]"); if (box) box.focus();
      changed();
    } else if (t.matches("[data-pinc]")) {
      var id = t.getAttribute("data-pinc"); S.pinc[id] = t.checked;
      rerenderHosts(id); var pb = document.querySelector('[data-pinc="' + attrSel(id) + '"]'); if (pb) pb.focus();
      changed();
    } else if (t.id === "publishDate") { S.publishDate = t.value; showDay(); changed(); }
  });
  document.addEventListener("input", function (e) {
    var t = e.target;
    if (t.matches("[data-q]")) {
      var k = t.getAttribute("data-q"), parts = k.split("|"), s = M.slotByKey[parts[0]];
      S.answers[k] = { q: Core.questionsFor(s, M.byId[s.item])[Number(parts[1])], a: t.value };
      t.closest(".q").classList.toggle("done", !!t.value.trim());
      var st = t.closest("[data-key]").querySelector(".status"); if (st) st.innerHTML = statusHtml(s, M.byId[s.item]);
      autoGrow(t); changed();
    } else if (t.matches("[data-note]")) { S.slotNotes[t.getAttribute("data-note")] = t.value; changed({ noTotals: true }); }
    else if (t.matches("[data-vnote]")) { var v = S.vets[t.getAttribute("data-vnote")]; if (v) v.notes = t.value; changed({ noTotals: true }); }
    else if (t.id === "globalNotes") { S.notes = t.value; changed({ noTotals: true }); }
  });
  function autoGrow(t) { t.style.height = "auto"; t.style.height = Math.min(240, t.scrollHeight + 2) + "px"; }
  document.addEventListener("toggle", function (e) {
    var d = e.target;
    if (!d.matches || !d.matches("details[data-lazy]")) return;
    var host = d.closest("[data-key]"); if (!host) return;
    var key = host.getAttribute("data-key"), kind = d.getAttribute("data-lazy");
    ui.open[key + "|" + kind] = d.open;
    if (!d.open || d.getAttribute("data-filled")) return;
    var s = M.slotByKey[key], it = M.byId[s.item];
    d.insertAdjacentHTML("beforeend", '<div class="xb">' + (kind === "draft" ? draftBody(s, it) : provBody(s, it)) + "</div>");
    d.setAttribute("data-filled", "1");
  }, true);
  document.addEventListener("click", function (e) {
    var t = e.target.closest("button,a[href^='#']"); if (!t) return;
    if (t.tagName === "A") { if (t.closest("#chips")) toggleChips(false); return; }
    var act = t.getAttribute("data-act");
    if (t.hasAttribute("data-vet")) return vet(t.getAttribute("data-vet"));
    if (t.hasAttribute("data-unvet")) return unvet(t.getAttribute("data-unvet"));
    if (t.hasAttribute("data-move")) return move(t, Number(t.getAttribute("data-move")));
    if (t.hasAttribute("data-jump")) return jumpNext(t.getAttribute("data-jump"));
    if (t.hasAttribute("data-pick")) { $("publishDate").value = t.getAttribute("data-pick"); S.publishDate = $("publishDate").value; showDay(); changed(); return; }
    if (t.id === "submitTop" || t.id === "submitBottom") return submit();
    if (t.id === "secsBtn") return toggleChips();
    if (act === "dismiss") return t.closest(".notice").remove();
    if (act === "show-json") return openJson("");
    if (act === "close-json") return closeJson();
    if (act === "select-json") { var ta = $("jsonText"); ta.focus(); ta.select(); ta.setSelectionRange(0, ta.value.length); return; }
    if (act === "copy-json") return copyText($("jsonText").value).then(function (ok) { $("jpMsg").textContent = ok ? "Copied. Paste it in chat, or send the file to the Gazette inbox." : "Couldn't copy automatically — tap Select all, then copy."; });
    if (act === "download-json") { var c = current(); $("jpMsg").textContent = download(c.text, c.name) ? "Download started: " + c.name : "Download blocked — use Copy instead."; return; }
    if (act === "share-json") return share();
    if (act === "close-toast") return $("toast").classList.remove("show");
    if (act === "reset") return reset();
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && $("jsonPanel").classList.contains("open")) closeJson(); });
  function toggleChips(force) {
    var open = force == null ? !$("chips").classList.contains("open") : force;
    $("chips").classList.toggle("open", open); $("secsBtn").setAttribute("aria-expanded", String(open));
    measureBar();
  }

  function vet(id) {
    if (!Core.vettable(M, id) || Core.vettedOnFile(M, id)) return;
    S.vets[id] = { notes: "", at: Core.isoLocal(new Date()) };
    rerenderHosts(id);
    var inp = document.querySelector('[data-vnote="' + attrSel(id) + '"]'); if (inp) inp.focus({ preventScroll: true });
    status("", "Vetted <code>" + esc(id) + "</code> on this page. It goes to the Desk with your submission.");
    changed();
  }
  function unvet(id) {
    delete S.vets[id];
    M.slots.forEach(function (s) { if (s.item === id) delete S.inc[s.key]; });
    delete S.pinc[id];
    rerenderHosts(id);
    var b = document.querySelector('[data-vet="' + attrSel(id) + '"]'); if (b) b.focus({ preventScroll: true });
    status("", "Un-vetted <code>" + esc(id) + "</code>. Include is locked again.");
    changed();
  }
  function move(btn, dir) {
    var card = btn.closest("article.card"), list = card.parentNode;
    var sib = dir < 0 ? card.previousElementSibling : card.nextElementSibling;
    while (sib && !sib.matches("article.card")) sib = dir < 0 ? sib.previousElementSibling : sib.nextElementSibling;
    if (!sib) return;
    // swap positions so empty slots keep their places (same as Core.sectionList)
    var mark = document.createComment("");
    list.replaceChild(mark, sib); list.replaceChild(sib, card); list.replaceChild(card, mark);
    S.order[list.getAttribute("data-cards")] = Array.from(list.querySelectorAll("article.card")).map(function (c) { return c.getAttribute("data-key"); });
    fixMoveButtons(list);
    if (btn.disabled) { var other = card.querySelector('[data-move="' + (-dir) + '"]'); if (other) other.focus(); } else btn.focus();
    if (card.getBoundingClientRect().top < barH()) card.scrollIntoView({ block: "start" });
    changed();
  }
  function barH() { return $("bar").getBoundingClientRect().height; }
  function measureBar() { document.documentElement.style.setProperty("--barh", Math.ceil(barH()) + "px"); }
  function jumpNext(which) {
    var els = [];
    if (which === "q") document.querySelectorAll("[data-q]").forEach(function (i) { if (!i.value.trim()) els.push(i); });
    else document.querySelectorAll(which === "in" ? "[data-in]" : "[data-needs-vet]").forEach(function (el) { els.push(el); });
    if (!els.length) { status("", which === "q" ? "No open questions." : which === "in" ? "Nothing included yet." : "Nothing left to vet."); return; }
    var top = barH() + 12, target = null;
    for (var i = 0; i < els.length; i++) { if (els[i].getBoundingClientRect().top > top + 4) { target = els[i]; break; } }
    if (!target) target = els[0]; // wrap around
    var scrollEl = which === "q" ? target.closest("[data-key]") || target : target;
    scrollEl.scrollIntoView({ block: "start" });
    if (which === "q" && !(window.matchMedia && window.matchMedia("(pointer: coarse)").matches)) target.focus({ preventScroll: true });
  }

  /* ---------- submit: download + clipboard, JSON box fallback ---------- */
  function current() {
    var p = Core.buildPayload(M, S, new Date());
    return { payload: p, text: JSON.stringify(p, null, 2) + "\n", name: fileName(p.publishDate) };
  }
  function download(text, name) {
    try {
      var url = URL.createObjectURL(new Blob([text], { type: "application/json" }));
      var a = document.createElement("a"); a.href = url; a.download = name; a.rel = "noopener"; a.style.display = "none";
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 60000);
      return true;
    } catch (e) { return false; }
  }
  function execCopy(text) {
    var ta = document.createElement("textarea"), ok = false, active = document.activeElement;
    ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.top = "0"; ta.style.left = "-9999px"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select(); ta.setSelectionRange(0, text.length);
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    ta.remove(); if (active && active.focus) active.focus({ preventScroll: true });
    return ok;
  }
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText && window.isSecureContext) {
      return navigator.clipboard.writeText(text).then(function () { return true; }, function () { return execCopy(text); });
    }
    return Promise.resolve(execCopy(text));
  }
  function submit() {
    var c = current(); ui.last = c;
    var dl = download(c.text, c.name);
    copyText(c.text).then(function (copied) {
      S.lastSubmit = { at: c.payload.submittedAt, sig: Core.payloadSig(c.payload) };
      saveNow(); updateDirty();
      var p = c.payload, summary = p.includedSlots.length + " included · " + p.vets.length + " vetted by you · " + p.answers.length + " answers · " + p.photoIncludes.length + " photos";
      var msg = dl && copied ? "<b>Downloaded + copied.</b> Send <code>" + esc(c.name) + "</code> to the Gazette inbox or paste it in chat." :
        copied ? "<b>Copied.</b> Paste it in chat (the download may not have started)." :
        dl ? "<b>Downloaded</b> <code>" + esc(c.name) + "</code> — send it to the Gazette inbox. (Couldn't copy; use Show JSON to copy by hand.)" :
        "<b>Couldn't download or copy.</b> Select the text below and copy it.";
      status("ok", msg + "<br>" + esc(summary) + " · " + esc(fmtTime(p.submittedAt)));
      toast(msg);
      if (!copied) openJson(dl ? "Couldn't copy automatically. If the file didn't download either, tap Select all, copy, and paste it in chat." : "Tap Select all, copy, and paste it in chat — or Share/Download.");
    });
  }
  function openJson(msg) {
    var c = current(); ui.last = c;
    $("jsonText").value = c.text;
    $("jpMsg").textContent = msg || "Copy this and paste it in chat, or save it (" + c.name + ") and send it to the Gazette inbox.";
    $("shareBtn").hidden = !canShareFile(c);
    $("jsonPanel").classList.add("open");
    $("jsonText").scrollTop = 0;
    $("jsonText").focus({ preventScroll: true }); // readonly: no phone keyboard
  }
  function closeJson() { $("jsonPanel").classList.remove("open"); }
  function shareFile(c) { try { return new File([c.text], c.name, { type: "application/json" }); } catch (e) { return null; } }
  function canShareFile(c) { var f = navigator.canShare && shareFile(c); return !!(f && navigator.canShare({ files: [f] })); }
  function share() {
    var c = current(), f = shareFile(c);
    navigator.share({ files: [f], title: c.name }).then(function () { $("jpMsg").textContent = "Shared " + c.name + "."; }, function () {});
  }

  function reset() {
    if (!window.confirm("Reset everything you've done on this issue (includes, vets, notes, answers, order)? This can't be undone.")) return;
    if (storage) { try { storage.removeItem(STORE_KEY); } catch (e) {} }
    S = Core.defaultState(M); ui.open = {};
    renderHeader(); render();
    status("", "Reset. Back to Desk's proposed budget.");
  }

  /* ---------- boot ---------- */
  function boot() {
    DATA = JSON.parse($("budget-data").textContent);
    M = Core.makeModel(DATA);
    var iss = M.cfg.issue || {};
    STORE_KEY = "gazette-budget:" + (iss.number != null ? iss.number : "x") + ":" + (iss.week || (M.cfg.publish || {}).date || "");
    storage = probeStorage();
    var saved = null;
    if (storage) { try { saved = JSON.parse(storage.getItem(STORE_KEY) || "null"); } catch (e) { saved = null; } }
    var r = Core.restoreState(M, saved);
    S = r.state;
    renderHeader();
    render();
    measureBar();
    if (window.ResizeObserver) new ResizeObserver(measureBar).observe($("bar")); else window.addEventListener("resize", measureBar);
    if (!storage) notice("warn", "This browser won't save your progress here (private mode or file:// limits). The page still works — finish in one sitting, or Submit early.");
    else if (r.restored) {
      notice("", "Restored your progress from " + esc(fmtTime(S.savedAt) || "earlier") + "." +
        (r.dataChanged ? " The Desk has updated this page since; your notes, answers, includes, order and vets were kept where they still match" +
          (r.dropped ? " (" + r.dropped + " saved entr" + (r.dropped === 1 ? "y" : "ies") + " no longer match and were dropped)" : "") + "." : ""));
    }
    if (r.restored) saveNow();
    document.querySelectorAll("[data-q]").forEach(function (t) { if (t.value) autoGrow(t); });
    window.addEventListener("pagehide", function () { if (saveTimer) saveNow(); });
    document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden" && saveTimer) saveNow(); });
  }
  window.BudgetPage = { model: function () { return M; }, state: function () { return S; }, payload: function () { return Core.buildPayload(M, S, new Date()); }, storeKey: function () { return STORE_KEY; } };
  try { boot(); }
  catch (err) {
    document.body.insertAdjacentHTML("afterbegin", '<div class="notice warn" style="margin:12px"><span>Page failed to load: ' + esc(err && err.message || err) + "</span></div>");
    throw err;
  }
})();
