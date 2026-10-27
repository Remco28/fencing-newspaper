/* En Garde Gazette — standalone budget page: pure logic (no DOM).
   Ported from budget-demo/practice.html (buildSlots, questionsFor, photoList, costOf, updateTotals,
   buildPayload) so the lineup + items + media are read exactly the same way. State (includes,
   local vets, notes, answers, order) is a plain object; everything here is a function of
   (model, state), so it runs in the page and under node for tests:
     node -e 'var C=require("./scripts/budget_page/core.js"); ...' */
(function (root) {
  "use strict";
  var PAGE_VERSION = "budget-standalone-v1";
  var SECTION_GUESS = [
    [/lead|feature|back_page|overheard|secondary_a/i, "lead"],
    [/club|signup|whos|result|rating|deadline|class|schedule|event|go_cheer/i, "club"],
    [/./, "shorts"]
  ];
  var DEFAULT_SECTIONS = [
    { key: "lead", title: "Lead & features" }, { key: "club", title: "Club" }, { key: "shorts", title: "Shorts & fill" },
    { key: "photos", title: "Photos" }, { key: "held", title: "Held, merged & next week" }
  ];

  function isObj(x) { return !!x && typeof x === "object" && !Array.isArray(x); }
  function words(t) { t = String(t || "").trim(); return t ? t.split(/\s+/).length : 0; }
  function itemWords(it) { return it ? (Number(it.word_count) || words(it.body)) : 0; }
  function firstSentence(t) {
    t = String(t || "").replace(/\s+/g, " ").trim();
    var m = t.match(/^(.{20,200}?[.!?])(\s|$)/);
    return m ? m[1] : (t.length > 180 ? t.slice(0, 177) + "…" : t);
  }
  function fileOf(path) { var m = String(path || "").match(/([^/]+)$/); return m ? m[1] : ""; }
  function guessSection(s) {
    for (var i = 0; i < SECTION_GUESS.length; i++) if (SECTION_GUESS[i][0].test(s || "")) return SECTION_GUESS[i][1];
    return "shorts";
  }
  function isSeed(cfg, it) {
    if (!it) return false;
    if (it.pretend) return true;
    if ((cfg.seed_ids || []).indexOf(it.id) >= 0) return true;
    return /invented|pretend/i.test(it.id || "") || /@example\.com$/i.test(it.from || "");
  }

  /* ---------- model: inlined data -> lookups, slots, photos, sections ---------- */
  function makeModel(data) {
    var cfg = data.lineup, itemsDoc = isObj(data.items) ? data.items : {}, mediaDoc = isObj(data.media) ? data.media : {};
    var M = { cfg: cfg, build: data.build || {}, thumbs: data.thumbs || {}, byId: {}, mediaById: {}, mediaByFile: {}, sizeByFile: {} };
    M.items = (Array.isArray(itemsDoc.items) ? itemsDoc.items : []).filter(function (i) { return isObj(i) && i.id; });
    M.items.forEach(function (i) { M.byId[i.id] = i; });
    M.media = (Array.isArray(mediaDoc.items) ? mediaDoc.items : []).filter(function (m) { return isObj(m) && m.id; });
    M.media.forEach(function (m) {
      M.mediaById[m.id] = m;
      var f = m.filename || fileOf(m.media_path);
      if (f) { M.mediaByFile[f] = m; if (m.w) M.sizeByFile[f] = [m.w, m.h]; }
    });
    Object.keys(cfg.media_sizes || {}).forEach(function (f) { M.sizeByFile[f] = cfg.media_sizes[f]; });
    M.slots = buildSlots(M);
    M.photos = photoList(M);
    M.sections = sectionsFor(M);
    M.slotByKey = {};
    M.slots.forEach(function (s) { M.slotByKey[s.key] = s; });
    return M;
  }

  /* slots: config + auto-placed staging items (practice.html buildSlots) */
  function buildSlots(M) {
    var cfg = M.cfg, raw = cfg.slots || cfg.lineup || []; // `lineup` = schema-1 files still render
    var seen = {}, keys = {};
    var out = raw.filter(isObj).map(function (s, i) {
      var it = s.item ? M.byId[s.item] : null;
      var sec = s.section || guessSection([s.key, s.slot, it && (it.slot_hint || it.suggested_slot)].join(" "));
      if (s.item) seen[s.item] = 1;
      (s.merged || []).forEach(function (m) { seen[m] = 1; });
      var key = s.key || ("slot-" + i);
      while (keys[key]) key += "-dup"; // duplicate keys would make the payload ambiguous
      keys[key] = 1;
      return Object.assign({}, s, { section: sec, key: key });
    });
    (cfg.not_proposed || []).forEach(function (n) { seen[n.item] = 1; });
    (cfg.held || []).forEach(function (h) { seen[h.id || h.item] = 1; });
    M.items.forEach(function (it) {
      if (seen[it.id] || isSeed(cfg, it)) return;
      if (it.kind === "photo" && it.media_path) return; // photo desk
      var hint = it.slot_hint || it.suggested_slot || it.kind || "";
      if (/ops_note_not_print/.test(hint)) return;
      out.push({
        key: "auto-" + it.id, section: guessSection(hint), slot: "Not slotted yet (" + (hint || it.kind || "item") + ")",
        budget: itemWords(it) ? itemWords(it) + "w" : "", item: it.id, proposed: false, auto: true,
        cost: { type: "prose", span: 1 }
      });
    });
    return out;
  }

  function photoList(M) {
    var listed = {};
    var out = (M.cfg.photos || []).filter(isObj).map(function (p) { listed[p.id] = 1; return p; });
    M.media.forEach(function (m) {
      if (listed[m.id] || m.kind !== "photo") return;
      out.push({ id: m.id, proposed: false, span: 1, note: "Not reviewed by Desk yet." });
    });
    return out;
  }

  /* Sections from the lineup; slots whose section isn't listed go to an "Other" section instead of vanishing. */
  function sectionsFor(M) {
    var secs = (Array.isArray(M.cfg.sections) && M.cfg.sections.length ? M.cfg.sections : DEFAULT_SECTIONS).filter(isObj);
    var known = {};
    secs.forEach(function (s) { known[s.key] = 1; });
    var out = secs.map(function (s) {
      return Object.assign({}, s, { type: s.key === "photos" ? "photos" : s.key === "held" ? "held" : "cards" });
    });
    if (M.slots.some(function (s) { return !known[s.section] || s.section === "photos" || s.section === "held"; })) {
      M.slots.forEach(function (s) { if (!known[s.section] || s.section === "photos" || s.section === "held") s.section = "other"; });
      var at = out.findIndex(function (s) { return s.type !== "cards"; });
      out.splice(at < 0 ? out.length : at, 0, { key: "other", title: "Other", hint: "Slots with a section the lineup doesn't list", type: "cards" });
    }
    return out;
  }

  function questionsFor(s, it) {
    if (s.questions) return s.questions;
    if (it && Array.isArray(it.need)) return it.need.map(function (n) { return "Need: " + n; });
    return [];
  }

  /* ---------- per-slot status ---------- */
  function isMissing(M, s) { return !s.empty && (!s.item || !M.byId[s.item]); }
  function vettedOnFile(M, id) {
    if (!id) return false;
    if (M.byId[id]) return !!M.byId[id].vetted;
    return !!(M.mediaById[id] && M.mediaById[id].vetted);
  }
  function isVetted(M, st, id) { return vettedOnFile(M, id) || !!(id && st.vets[id]); }
  function photoPresent(M, p) { return !!(M.mediaById[p.id] || M.byId[p.id]); }
  function isIncluded(M, st, s) {
    if (s.empty || isMissing(M, s) || !isVetted(M, st, s.item)) return false;
    if (Object.prototype.hasOwnProperty.call(st.inc, s.key)) return !!st.inc[s.key];
    return !!s.proposed && !s.waiting;
  }
  function photoIncluded(M, st, p) {
    if (!photoPresent(M, p) || !isVetted(M, st, p.id)) return false;
    if (Object.prototype.hasOwnProperty.call(st.pinc, p.id)) return !!st.pinc[p.id];
    return !!p.proposed;
  }
  function headlineOf(s, it) { return s.title || (it && it.headline) || s.slot || ""; }
  function openQuestions(M, st, s) {
    var qs = questionsFor(s, M.byId[s.item]), n = 0;
    qs.forEach(function (q, i) { if (!answerOf(st, s.key, i)) n++; });
    return n;
  }
  function answerOf(st, key, i) { var a = st.answers[key + "|" + i]; return a && String(a.a || "").trim() ? String(a.a).trim() : ""; }

  /* Display order of a card section: empties keep their lineup position, cards follow st.order. */
  function sectionList(M, st, secKey) {
    var list = M.slots.filter(function (s) { return s.section === secKey; });
    var cards = list.filter(function (s) { return !s.empty; });
    var saved = st.order[secKey];
    if (Array.isArray(saved) && saved.length) {
      var rank = {};
      saved.forEach(function (k, i) { rank[k] = i; });
      cards = cards.map(function (s, i) { return { s: s, r: rank.hasOwnProperty(s.key) ? rank[s.key] : saved.length + i, i: i }; })
        .sort(function (a, b) { return a.r - b.r || a.i - b.i; }).map(function (x) { return x.s; });
    }
    var ci = 0;
    return list.map(function (s) { return s.empty ? s : cards[ci++]; });
  }
  function cardSections(M) { return M.sections.filter(function (s) { return s.type === "cards"; }); }
  function orderedSlots(M, st) {
    var out = [];
    cardSections(M).forEach(function (sec) { out = out.concat(sectionList(M, st, sec.key)); });
    return out;
  }

  /* ---------- fit estimate (practice.html costOf / updateTotals) ---------- */
  function costOf(M, s) {
    var C = M.cfg.capacity, c = s.cost || {}, it = M.byId[s.item], span = c.span || 1;
    if (c.type === "prose") { var f = c.feature; return itemWords(it) / (f ? C.wpi_feature : C.wpi) + (f ? C.head_feature : C.head_short) * span + C.gap * span; }
    if (c.type === "table") return (C.table_head + (c.rows || 0) * (span >= 3 ? C.row_full : C.row_rail) + C.gap) * span;
    if (c.type === "table_rows") return (c.rows || 0) * C.row_rail;
    if (c.type === "qa") return C.head_short + (itemWords(it) || 40) / C.wpi + C.gap;
    if (c.type === "figure") { var wIn = span >= 2 ? C.span2_width_in : C.col_width_in; return (wIn * (c.h / c.w) + C.caption_in + C.gap) * span + (c.words ? c.words / C.wpi : 0) + (c.head ? C.head_short : 0); }
    return 0;
  }
  function photoDims(M, p) {
    var m = M.mediaById[p.id] || {}, f = m.filename || fileOf(m.media_path), d = M.sizeByFile[f];
    return d ? [Number(d[0]) || 1, Number(d[1]) || 1] : [m.w || 1, m.h || 1];
  }
  function photoCost(M, p) {
    var C = M.cfg.capacity, span = Number(p.span) || 1, wIn = span >= 2 ? C.span2_width_in : C.col_width_in, d = photoDims(M, p);
    return (wIn * d[1] / d[0] + C.caption_in) * span;
  }
  function computeTotals(M, st) {
    var C = M.cfg.capacity, cap = C.page1_col_in + C.page2_col_in, used = 0, pend = 0, nIn = 0, nVet = 0, nQ = 0, perSec = {};
    orderedSlots(M, st).forEach(function (s) {
      nQ += openQuestions(M, st, s);
      if (s.empty) return;
      var sec = perSec[s.section] = perSec[s.section] || { n: 0, inc: 0 };
      sec.n++;
      if (isIncluded(M, st, s)) { used += costOf(M, s); nIn++; sec.inc++; }
      if (!isMissing(M, s) && !isVetted(M, st, s.item)) { nVet++; if (s.proposed) pend += costOf(M, s); }
    });
    var ps = perSec.photos = { n: 0, inc: 0 };
    M.photos.forEach(function (p) {
      ps.n++;
      if (photoIncluded(M, st, p)) { used += photoCost(M, p); nIn++; ps.inc++; }
      if (photoPresent(M, p) && !isVetted(M, st, p.id)) nVet++;
    });
    var labels = {};
    M.sections.forEach(function (sec) {
      var d = perSec[sec.key], t = "";
      if (sec.key === "held") { var n = (M.cfg.held || []).length + (M.cfg.not_proposed || []).length; t = n + (n === 1 ? " item" : " items"); }
      else if (d) t = d.inc + " of " + d.n + " in";
      else if (sec.key !== "photos") t = "empty";
      labels[sec.key] = t;
    });
    return {
      cap: cap, used: used, pend: pend, nIn: nIn, nVet: nVet, nQ: nQ, perSec: perSec, labels: labels,
      pct: Math.round(used / cap * 100), pctP: Math.round((used + pend) / cap * 100),
      room: Math.round((cap - used) * C.wpi / 10) * 10, over: used > cap * 1.08,
      fillPct: Math.min(100, used / (cap * 1.25) * 100), pendPct: Math.min(100, (used + pend) / (cap * 1.25) * 100), tickPct: 100 / 1.25
    };
  }

  /* ---------- payload: the server's /submit shape + vets ---------- */
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function isoLocal(d) {
    var off = -d.getTimezoneOffset(), sign = off >= 0 ? "+" : "-", a = Math.abs(off);
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) + "T" + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds()) +
      sign + pad(Math.floor(a / 60)) + ":" + pad(a % 60);
  }
  function buildPayload(M, st, now) {
    var cfg = M.cfg, included = [], excluded = [], empties = [], order = [], slotNotes = {}, answers = [];
    orderedSlots(M, st).forEach(function (s) {
      var it = M.byId[s.item];
      questionsFor(s, it).forEach(function (q, i) {
        var a = answerOf(st, s.key, i);
        if (a) answers.push({ slot: s.key, itemId: s.item || null, question: q, answer: a });
      });
      if (s.empty) { empties.push({ slot: s.key, name: s.slot, headline: "", itemId: null, vetted: true, stale: false, empty: true }); return; }
      var entry = { slot: s.key, name: s.slot, headline: headlineOf(s, it), itemId: s.item || null,
        vetted: isVetted(M, st, s.item), stale: !!(s.stale || s.waiting) };
      order.push(s.key);
      (isIncluded(M, st, s) ? included : excluded).push(entry);
      var n = String(st.slotNotes[s.key] || "").trim(); if (n) slotNotes[s.key] = n;
    });
    var real = cfg.mode === "real";
    return {
      publishDate: st.publishDate || (cfg.publish && cfg.publish.date) || "",
      practice: !real, pretend: false, targetWeek: cfg.target_week || "next",
      issue: cfg.issue || null,
      includedSlots: included, excludedSlots: excluded.concat(empties), // empty slots listed as excluded, like v1
      photoIncludes: M.photos.filter(function (p) { return photoIncluded(M, st, p); }).map(function (p) { return p.id; }),
      notes: String(st.notes || "").trim(), slotNotes: slotNotes, answers: answers, order: order,
      pageVersion: PAGE_VERSION, submittedAt: now ? isoLocal(now) : null,
      vets: Object.keys(st.vets).filter(function (id) { return vettable(M, id) && !vettedOnFile(M, id); })
        .map(function (id) { return { id: id, vet_notes: String(st.vets[id].notes || "").trim() }; })
    };
  }
  /* Signature for "changed since last submit": the payload minus its timestamp. */
  function payloadSig(p) { var c = Object.assign({}, p); delete c.submittedAt; return JSON.stringify(c); }

  /* ---------- state: defaults + restore (keeps what still matches when data changed) ---------- */
  function vettable(M, id) {
    if (!id) return false;
    if (M.byId[id]) return true;
    return M.photos.some(function (p) { return p.id === id && photoPresent(M, p); });
  }
  function defaultState(M) {
    return { v: M.build.dataVersion || "", savedAt: null, publishDate: (M.cfg.publish && M.cfg.publish.date) || "",
      inc: {}, pinc: {}, notes: "", slotNotes: {}, answers: {}, order: {}, vets: {}, lastSubmit: null };
  }
  function restoreState(M, saved) {
    var st = defaultState(M), res = { state: st, restored: false, dataChanged: false, dropped: 0 };
    if (!isObj(saved)) return res;
    res.restored = true;
    res.dataChanged = saved.v !== st.v;
    var cardKeys = {}, photoIds = {};
    M.slots.forEach(function (s) { if (!s.empty) cardKeys[s.key] = s; });
    M.photos.forEach(function (p) { photoIds[p.id] = p; });
    if (typeof saved.publishDate === "string" && /^\d{4}-\d{2}-\d{2}$/.test(saved.publishDate)) st.publishDate = saved.publishDate;
    if (typeof saved.notes === "string") st.notes = saved.notes;
    st.savedAt = saved.savedAt || null;
    if (isObj(saved.lastSubmit)) st.lastSubmit = saved.lastSubmit;
    function each(obj, fn) { if (isObj(obj)) Object.keys(obj).forEach(function (k) { fn(k, obj[k]); }); }
    each(saved.inc, function (k, v) { if (cardKeys[k]) st.inc[k] = !!v; else res.dropped++; });
    each(saved.pinc, function (k, v) { if (photoIds[k]) st.pinc[k] = !!v; else res.dropped++; });
    each(saved.slotNotes, function (k, v) { if (typeof v !== "string") return; if (cardKeys[k]) st.slotNotes[k] = v; else if (v.trim()) res.dropped++; });
    each(saved.answers, function (k, v) {
      if (!isObj(v) || !String(v.a || "").trim()) return;
      var parts = k.split("|"), s = M.slotByKey[parts[0]];
      var qs = s ? questionsFor(s, M.byId[s.item]) : [], idx = qs.indexOf(v.q);
      if (idx < 0 && !res.dataChanged && qs[Number(parts[1])] != null) idx = Number(parts[1]);
      if (idx >= 0) st.answers[parts[0] + "|" + idx] = { q: qs[idx], a: v.a }; else res.dropped++;
    });
    each(saved.order, function (sec, keys) {
      if (!Array.isArray(keys)) return;
      var ok = keys.filter(function (k) { return cardKeys[k] && cardKeys[k].section === sec; });
      if (ok.length) st.order[sec] = ok;
    });
    each(saved.vets, function (id, v) {
      if (!vettable(M, id)) { res.dropped++; return; }
      if (vettedOnFile(M, id)) return; // Desk already applied it
      st.vets[id] = { notes: isObj(v) && typeof v.notes === "string" ? v.notes : "", at: isObj(v) ? v.at || null : null };
    });
    return res;
  }

  var Core = {
    PAGE_VERSION: PAGE_VERSION, words: words, itemWords: itemWords, firstSentence: firstSentence, fileOf: fileOf,
    guessSection: guessSection, isSeed: isSeed, makeModel: makeModel, questionsFor: questionsFor,
    isMissing: isMissing, vettedOnFile: vettedOnFile, isVetted: isVetted, photoPresent: photoPresent, vettable: vettable,
    isIncluded: isIncluded, photoIncluded: photoIncluded, headlineOf: headlineOf, openQuestions: openQuestions, answerOf: answerOf,
    sectionList: sectionList, orderedSlots: orderedSlots, costOf: costOf, photoCost: photoCost, photoDims: photoDims,
    computeTotals: computeTotals, isoLocal: isoLocal, buildPayload: buildPayload, payloadSig: payloadSig,
    defaultState: defaultState, restoreState: restoreState
  };
  if (typeof module === "object" && module.exports) module.exports = Core;
  else root.BudgetCore = Core;
})(this);
