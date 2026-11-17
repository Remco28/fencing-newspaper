/* En Garde Gazette — Budget page (the two-page spread): pure logic, no DOM.
   Everything the page decides lives here so it also runs under node for tests:
     node -e 'const C=require("./scripts/budget_page/core.js").make(DATA); console.log(C.submission())'
   - model: lineup slots (+ staged items the lineup doesn't slot), photos, section history
   - state: includes, running order, page placement, photo picks, vets, answers, notes, dates
     (seeded from Frank's latest ingested decision; restorable from this browser's autosave)
   - capacity model in column-inches (lineup.capacity with the fill calibration laid over it;
     same arithmetic as scripts/budget_model.py) and the packer that turns costs into blocks + holes
   - what still needs Frank, and the submission document (fixed contract, see buildDoc/submission). */
(function (root) {
  'use strict';
  const PAGE_VERSION = 'budget-paper-v1';
  const isObj = x => !!x && typeof x === 'object' && !Array.isArray(x);
  const words = t => { t = String(t || '').trim(); return t ? t.split(/\s+/).length : 0; };
  const itemWords = it => (it ? (Number(it.word_count) || words(it.body)) : 0);
  const fileOf = p => { const m = String(p || '').match(/([^/]+)$/); return m ? m[1] : ''; };
  const isDate = d => typeof d === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(d);
  const r1 = n => Math.round(n * 10) / 10;
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const GUT = 0.125;       // gutter between columns, inches
  const MIN_PIECE = 0.5;   // shortest piece of a block worth starting in a column, inches

  function make(D) {
    const L = D.lineup, build = D.build || {}, dec = isObj(D.decisions) ? D.decisions : null;
    const cap = Object.assign({ photo_ceiling_in: 2.2, full_width_in: 7.5, oversupply: 1.15 }, L.capacity, isObj(D.capacity) ? D.capacity : {});
    const itemList = (isObj(D.items) && Array.isArray(D.items.items) ? D.items.items : []).filter(i => isObj(i) && i.id);
    const mediaList = (isObj(D.media) && Array.isArray(D.media.items) ? D.media.items : []).filter(m => isObj(m) && m.id);
    mediaList.forEach(m => { if (!m.filename) m.filename = fileOf(m.media_path); });
    const items = Object.fromEntries(itemList.map(i => [i.id, i]));
    const media = Object.fromEntries(mediaList.map(m => [m.id, m]));
    const issueNo = (L.issue || {}).number;

    /* ---------- slots: the lineup, plus staged items it doesn't mention (so nothing is invisible) ---------- */
    const seen = {}, keys = {};
    const isSeed = it => !!it.pretend || (L.seed_ids || []).includes(it.id) || /invented|pretend/i.test(it.id) || /@example\.com$/i.test(it.from || '');
    const slots = (L.slots || L.lineup || []).filter(isObj).map((s, i) => {
      if (s.item) seen[s.item] = 1;
      (s.merged || []).forEach(m => { seen[m] = 1; });
      let key = s.key || 'slot-' + i;
      while (keys[key]) key += '-dup'; // duplicate keys would make the submission ambiguous
      keys[key] = 1;
      return Object.assign({}, s, { key, slot: s.slot || key });
    });
    (L.not_proposed || []).forEach(n => { seen[n.item] = 1; });
    (L.held || []).forEach(h => { seen[h.id || h.item] = 1; });
    itemList.forEach(it => {
      if (seen[it.id] || isSeed(it) || (it.kind === 'photo' && it.media_path)) return;
      const hint = it.slot_hint || it.suggested_slot || it.kind || '';
      if (/ops_note_not_print/.test(hint)) return;
      slots.push({ key: 'auto-' + it.id, slot: 'Not slotted yet (' + (hint || 'item') + ')', budget: itemWords(it) ? itemWords(it) + 'w' : '',
        item: it.id, proposed: false, auto: true, cost: { type: 'prose', span: 1 }, why: 'Staged, but Clark has not given it a slot.' });
    });
    const slotBy = Object.fromEntries(slots.map(s => [s.key, s]));
    const itemOf = s => (s.item && items[s.item]) || null;
    const allItemsOf = s => [s.item].concat(s.merged || []).filter(Boolean).map(id => items[id]).filter(Boolean);
    const headlineOf = s => s.title || (itemOf(s) || {}).headline || '';
    const shortName = s => String(s.slot).split(' — ')[0];
    const questionsFor = s => s.questions || ((itemOf(s) && Array.isArray(itemOf(s).need)) ? itemOf(s).need.map(n => 'Need: ' + n) : []);

    /* ---------- photos: the lineup's list + any staged photo Clark hasn't reviewed ---------- */
    const photoList = (L.photos || []).filter(p => isObj(p) && media[p.id]);
    mediaList.forEach(m => { if (m.kind === 'photo' && !photoList.some(p => p.id === m.id)) photoList.push({ id: m.id, proposed: false, span: 1, note: 'Not reviewed by Clark yet.' }); });
    const photoMeta = Object.fromEntries(photoList.map(p => [p.id, p]));
    const mediaOfSlot = s => (s.item && s.thumb && mediaList.find(m => m.parent_item_id === s.item && fileOf(s.thumb) === m.filename)) || null;
    const slotMediaIds = new Set(slots.map(mediaOfSlot).filter(Boolean).map(m => m.id));
    const loosePhotos = photoList.filter(p => !slotMediaIds.has(p.id)).map(p => p.id); // art not already riding inside a slot

    /* ---------- capacity model (column-inches; mirrors scripts/budget_model.py) ---------- */
    const total = cap.page1_col_in + cap.page2_col_in;
    const pageH = p => (p === 1 ? cap.page1_col_in : cap.page2_col_in) / 3;
    function figDepth(w, h, span) {
      const width = span <= 1 ? cap.col_width_in : span === 2 ? cap.span2_width_in : cap.full_width_in, nat = width * (h || 1) / (w || 1);
      return span <= 1 ? Math.min(nat, cap.photo_ceiling_in) : nat;
    }
    let state = null;
    /* Layout variants. Shared names with compose/: 'wide' | 'tall'. compose/ does not yet expose a
       registry, so the builder inlines scripts/budget_page/layouts.json as D.layouts. */
    const LAY = isObj(D.layouts) ? D.layouts : {};
    const LAY_SECTIONS = isObj(LAY.sections) ? LAY.sections : {};
    const LAY_BY_SLOT = isObj(LAY.bySlot) ? LAY.bySlot : {};
    const SNAP_WIDTHS = { 1: cap.col_width_in, 2: cap.span2_width_in, 3: cap.full_width_in };
    const hist = isObj(D.sectionHistory) ? D.sectionHistory : null;
    function naturalSpan(s) { return Math.max(1, Math.min(3, (s.cost && s.cost.span) || 1)); }
    function sectionIdOf(s) {
      if (!s) return '';
      if (LAY_BY_SLOT[s.key]) return LAY_BY_SLOT[s.key];
      const secs = (hist && (hist.slotSections || {})[s.key]) || [];
      return secs.find(id => LAY_SECTIONS[id]) || secs[0] || '';
    }
    function layoutSpec(s) {
      const id = sectionIdOf(s), spec = (id && LAY_SECTIONS[id]) || null;
      return (spec && Array.isArray(spec.variants) && spec.variants.length > 1) ? spec : null;
    }
    const canSwitchLayout = s => !!layoutSpec(s);
    function layoutSpan(s, lay) {
      const spec = layoutSpec(s);
      const n = (spec && spec[lay] && spec[lay].span) || (lay === 'tall' ? 1 : Math.max(2, naturalSpan(s)));
      return Math.max(1, Math.min(3, n));
    }
    function currentLayout(s) {
      const v = state && state.layout && state.layout[s.key];
      if (v === 'wide' || v === 'tall') return v;
      return spanOf(s) >= 2 ? 'wide' : 'tall';
    }
    function photoLayoutOf(id) {
      const v = state && state.layout && state.layout[id];
      if (v === 'wide' || v === 'tall') return v;
      return photoSpanOf(id) >= 2 ? 'wide' : 'tall';
    }
    const spanOf = s => {
      if (state && state.slotSpan && state.slotSpan[s.key]) return Math.max(1, Math.min(3, state.slotSpan[s.key]));
      if (state && state.layout && (state.layout[s.key] === 'wide' || state.layout[s.key] === 'tall')) return layoutSpan(s, state.layout[s.key]);
      return naturalSpan(s);
    };
    function photoSpanOf(id) {
      if (state && state.photoSpan && state.photoSpan[id]) return Math.max(1, Math.min(3, state.photoSpan[id]));
      if (state && state.layout && (state.layout[id] === 'wide' || state.layout[id] === 'tall')) return state.layout[id] === 'tall' ? 1 : Math.max(2, (photoMeta[id] || {}).span || 2);
      return Math.max(1, Math.min(3, (photoMeta[id] || {}).span || 1));
    }
    const baseWordsOf = s => (s.cost && typeof s.cost.words === 'number' ? s.cost.words : itemWords(itemOf(s)));
    const wordsOf = s => {
      const rz = state && state.resize && state.resize[s.key];
      return (rz && typeof rz.toWords === 'number') ? rz.toWords : baseWordsOf(s);
    };
    function costOf(s) {
      const c = s.cost; if (!c) return 0; const span = spanOf(s), t = c.type;
      if (t === 'prose' || t === 'qa') return wordsOf(s) / (c.feature ? cap.wpi_feature : cap.wpi) + ((c.feature ? cap.head_feature : cap.head_short) + cap.gap) * span;
      if (t === 'table' || t === 'table_rows') return (cap.table_head + (c.rows || 0) * (span > 1 ? cap.row_full : cap.row_rail) + cap.gap) * span + (c.words || 0) / cap.wpi;
      if (t === 'figure') return figDepth(c.w, c.h, span) * span + (c.head ? cap.caption_in : 0) * span + cap.gap * span + (c.words || 0) / cap.wpi + (c.head ? cap.head_short * span : 0);
      return 0;
    }
    function photoCost(id) {
      const m = media[id] || {}, span = photoSpanOf(id);
      return (figDepth(m.w, m.h, span) + cap.caption_in + cap.gap) * span;
    }
    function slotSize(s) {
      const span = spanOf(s);
      return { span, widthIn: SNAP_WIDTHS[span] || cap.col_width_in, heightIn: r1(costOf(s) / span) };
    }
    function photoSize(id) {
      const m = media[id] || {}, span = photoSpanOf(id);
      return { span, widthIn: SNAP_WIDTHS[span] || cap.col_width_in, heightIn: r1(figDepth(m.w, m.h, span)) };
    }
    function snapSpan(widthIn) {
      let best = 1, d = Infinity;
      [1, 2, 3].forEach(n => { const dd = Math.abs((SNAP_WIDTHS[n] || 0) - widthIn); if (dd < d) { d = dd; best = n; } });
      return best;
    }
    function applyResize(s, direction, target) {
      const fromWords = baseWordsOf(s), prev = state.resize[s.key];
      delete state.resize[s.key];
      const fromColIn = costOf(s);
      if (prev) state.resize[s.key] = prev;
      let toWords = fromWords, unit = 'words', pct = 100, raw = (target == null ? '' : String(target).trim());
      let m;
      if ((m = raw.match(/^([+-]?\d+(?:\.\d+)?)\s*%$/))) {
        pct = Math.max(10, Math.min(400, Number(m[1])));
        toWords = Math.max(0, Math.round(fromWords * pct / 100));
        unit = 'pct';
      } else if ((m = raw.match(/^([+-]?\d+(?:\.\d+)?)\s*(col-?in(?:ches)?|in|")$/i))) {
        const wpi = (s.cost && s.cost.feature) ? cap.wpi_feature : cap.wpi;
        toWords = Math.max(0, Math.round(Number(m[1]) * wpi));
        unit = 'col-in';
        pct = fromWords ? Math.round(toWords / fromWords * 100) : 100;
      } else if (raw && (m = raw.match(/^([+-]?\d+)\s*w?$/i))) {
        toWords = Math.max(0, Math.round(Number(m[1])));
        unit = 'words';
        pct = fromWords ? Math.round(toWords / fromWords * 100) : 100;
      } else if (typeof target === 'number' && isFinite(target)) {
        toWords = Math.max(0, Math.round(target));
        unit = 'words';
        raw = String(toWords);
        pct = fromWords ? Math.round(toWords / fromWords * 100) : 100;
      } else if (direction === 'expand') {
        toWords = Math.round(fromWords * 1.25); pct = 125; unit = 'pct'; raw = raw || '125%';
      } else if (direction === 'shrink') {
        toWords = Math.round(fromWords * 0.75); pct = 75; unit = 'pct'; raw = raw || '75%';
      } else {
        return null;
      }
      direction = toWords > fromWords ? 'expand' : toWords < fromWords ? 'shrink' : (direction === 'shrink' || direction === 'expand' ? direction : 'expand');
      state.resize[s.key] = { direction, target: raw, fromWords, toWords, fromColIn: r1(fromColIn), unit, pct };
      state.resize[s.key].toColIn = r1(costOf(s));
      return state.resize[s.key];
    }
    const pageNum = v => (v === 1 || v === 2) ? v : (isObj(v) && (v.page === 1 || v.page === 2) ? v.page : 0);
    const takeSpan = v => (isObj(v) && typeof v.span === 'number' && v.span >= 1 && v.span <= 3) ? Math.round(v.span) : 0;

    /* ---------- state ---------- */
    const qKey = (k, i) => k + '|' + i;
    const carried = []; // captured answers that don't belong to a desk question on a slot (e.g. answers given by chat)
    // On-file only. Session vets are not applied yet; unvetted work stays in the bank and is never auto-queued
    // from a proposal or from last sitting's includes / photoIncludes.
    const vettedOnFile = id => { const x = items[id] || media[id]; return !!(x && x.vetted); };
    function slotVettedOnFile(s) {
      if (!s || s.empty) return false;
      const its = allItemsOf(s);
      if (s.item && !its.length) return false;
      if (its.some(i => !vettedOnFile(i.id))) return false;
      const m = mediaOfSlot(s);
      return !m || vettedOnFile(m.id);
    }
    function freshState() {
      const st = { v: build.dataVersion || '', savedAt: null, publishDate: (L.publish || {}).date || '', altDate: (L.publish || {}).alt || '',
        inc: {}, order: [], photos: {}, slotNotes: {}, answers: {}, vets: {}, notes: '', filler: '', page: {}, photoPage: {}, moved: {}, resize: {}, layout: {}, slotSpan: {}, photoSpan: {} };
      slots.forEach(s => { st.inc[s.key] = !s.empty && !!s.proposed && !s.waiting && slotVettedOnFile(s); });
      photoList.forEach(p => { st.photos[p.id] = loosePhotos.includes(p.id) && !!p.proposed && vettedOnFile(p.id); });
      if (dec) {
        const inc = dec.included || [], known = new Set([].concat(dec.order || [], inc, dec.excluded || []));
        slots.forEach(s => { if (!s.empty && known.has(s.key)) st.inc[s.key] = inc.includes(s.key) && slotVettedOnFile(s); });
        (dec.order || []).forEach(k => { if (slotBy[k] && !slotBy[k].empty && !st.order.includes(k)) st.order.push(k); });
        if (Array.isArray(dec.photoIncludes)) photoList.forEach(p => { st.photos[p.id] = dec.photoIncludes.includes(p.id) && vettedOnFile(p.id); });
        if (isObj(dec.slotNotes)) Object.keys(dec.slotNotes).forEach(k => { if (slotBy[k] && typeof dec.slotNotes[k] === 'string') st.slotNotes[k] = dec.slotNotes[k]; });
        if (typeof dec.notes === 'string') st.notes = dec.notes;
        if (isDate(dec.publishDate)) st.publishDate = dec.publishDate;
        if ('publishDateAlt' in dec) st.altDate = isDate(dec.publishDateAlt) ? dec.publishDateAlt : '';
        carried.length = 0;
        (dec.answers || []).filter(isObj).forEach(a => {
          const s = slotBy[a.slot], i = s ? questionsFor(s).indexOf(a.question) : -1;
          if (i >= 0) { if (String(a.answer || '').trim()) st.answers[qKey(s.key, i)] = String(a.answer); } else carried.push(a);
        });
      }
      slots.forEach(s => { if (!s.empty && !st.order.includes(s.key)) st.order.push(s.key); });
      // Starting pages: the lineup's own `page` (1|2) when the desk gives one, or a page named in the slot; otherwise the running order is
      // poured so both pages are about equally full. Frozen here: adding a block later never reshuffles the rest.
      const run = st.order.map(k => slotBy[k]), used = run.filter(s => st.inc[s.key]).reduce((a, s) => a + costOf(s), 0);
      const target = Math.min(cap.page1_col_in, Math.max(used, 1) * cap.page1_col_in / total);
      let cum = 0;
      run.forEach((s, i) => {
        const named = /\b(page|p\.?)\s*2\b|back[- ]page/i.test(s.slot) ? 2 : /\b(page|p\.?)\s*1\b|front[- ]page/i.test(s.slot) ? 1 : 0; // "Page 2 visual — …"
        if (s.page === 1 || s.page === 2) st.page[s.key] = s.page;
        else if (named) st.page[s.key] = named;
        else if (!st.inc[s.key]) st.page[s.key] = 2;
        else st.page[s.key] = (i === 0 || cum + costOf(s) / 2 <= target) ? 1 : 2;
        if (st.inc[s.key] && st.page[s.key] === 1) cum += costOf(s);
      });
      loosePhotos.forEach(id => { st.photoPage[id] = 1; });
      // Optional pages field: {slots:{key:1|2}, photos:{id:1|2}}, or a flat slot map. Older submissions omit it.
      if (dec && isObj(dec.pages)) {
        const raw = dec.pages, slotMap = (isObj(raw.slots) || isObj(raw.photos)) ? (raw.slots || {}) : raw, photoMap = isObj(raw.photos) ? raw.photos : {};
        Object.keys(slotMap).forEach(k => {
          const n = pageNum(slotMap[k]), sp = takeSpan(slotMap[k]);
          if (slotBy[k] && n) { st.page[k] = n; if (st.inc[k]) st.moved[k] = n; }
          if (slotBy[k] && sp) { st.slotSpan[k] = sp; st.layout[k] = sp >= 2 ? 'wide' : 'tall'; }
        });
        Object.keys(photoMap).forEach(id => {
          const n = pageNum(photoMap[id]), sp = takeSpan(photoMap[id]);
          if (photoMeta[id] && n) st.photoPage[id] = n;
          if (photoMeta[id] && sp) { st.photoSpan[id] = sp; st.layout[id] = sp >= 2 ? 'wide' : 'tall'; }
        });
      }
      if (dec && isObj(dec.layout)) Object.keys(dec.layout).forEach(k => {
        if (dec.layout[k] === 'wide' || dec.layout[k] === 'tall') st.layout[k] = dec.layout[k];
      });
      if (dec && isObj(dec.resize)) Object.keys(dec.resize).forEach(k => {
        if (isObj(dec.resize[k])) st.resize[k] = Object.assign({}, dec.resize[k]);
      });
      return st;
    }
    state = freshState();
    const listeners = [];
    const on = f => listeners.push(f), emit = why => listeners.forEach(f => f(why));

    /* Autosave round trip. A save made before Frank's latest ingested decision is superseded by it; a save made
       against other data keeps whatever still matches (slots by key, answers by question text). */
    function serialize(now) { return Object.assign({}, state, { savedAt: (now || new Date()).toISOString(), answerQs: answersForSave() }); }
    function restore(saved) {
      const res = { restored: false, dataChanged: false, dropped: 0, superseded: false };
      if (!isObj(saved)) return res;
      const thr = dec && Date.parse(dec.client_submitted_at || dec.at || ''), sv = Date.parse(saved.savedAt || '');
      if (thr && (!sv || sv < thr)) { res.superseded = true; return res; }
      res.restored = true; res.dataChanged = saved.v !== state.v;
      const each = (o, f) => { if (isObj(o)) Object.keys(o).forEach(k => f(k, o[k])); };
      const card = k => slotBy[k] && !slotBy[k].empty;
      if (isDate(saved.publishDate)) state.publishDate = saved.publishDate;
      if (saved.altDate === '' || isDate(saved.altDate)) state.altDate = saved.altDate;
      ['notes', 'filler'].forEach(k => { if (typeof saved[k] === 'string') state[k] = saved[k]; });
      each(saved.vets, (id, v) => { if (!(items[id] || media[id])) { res.dropped++; return; } if (!vettedOnFile(id)) state.vets[id] = typeof v === 'string' ? v : ''; });
      each(saved.inc, (k, v) => { if (card(k)) state.inc[k] = !!v && canPlace(slotBy[k]); else res.dropped++; });
      each(saved.photos, (k, v) => { if (photoMeta[k]) state.photos[k] = !!v && canPlacePhoto(k); else res.dropped++; });
      each(saved.page, (k, v) => { const n = pageNum(v); if (card(k) && n) state.page[k] = n; });
      each(saved.moved, (k, v) => { const n = pageNum(v); if (card(k) && n) state.moved[k] = n; });
      each(saved.photoPage, (k, v) => { const n = pageNum(v); if (photoMeta[k] && n) state.photoPage[k] = n; });
      each(saved.slotSpan, (k, v) => { if (card(k) && typeof v === 'number' && v >= 1 && v <= 3) state.slotSpan[k] = Math.round(v); });
      each(saved.photoSpan, (k, v) => { if (photoMeta[k] && typeof v === 'number' && v >= 1 && v <= 3) state.photoSpan[k] = Math.round(v); });
      each(saved.layout, (k, v) => { if ((card(k) || photoMeta[k]) && (v === 'wide' || v === 'tall')) state.layout[k] = v; });
      each(saved.resize, (k, v) => { if (card(k) && isObj(v)) state.resize[k] = Object.assign({}, v); });
      each(saved.slotNotes, (k, v) => { if (typeof v !== 'string') return; if (slotBy[k]) state.slotNotes[k] = v; else if (v.trim()) res.dropped++; });
      each(saved.answers, (k, v) => {
        if (typeof v !== 'string') return;
        const s = slotBy[k.split('|')[0]], i = Number(k.split('|')[1]);
        const q = (saved.answerQs || {})[k], qs = s ? questionsFor(s) : [], at = q != null ? qs.indexOf(q) : (res.dataChanged ? -1 : i);
        if (at >= 0 && qs[at] != null) state.answers[qKey(s.key, at)] = v; else if (v.trim()) res.dropped++;
      });
      if (Array.isArray(saved.order)) {
        const ok = saved.order.filter((k, i, a) => card(k) && a.indexOf(k) === i);
        state.order = ok.concat(state.order.filter(k => !ok.includes(k)));
      }
      return res;
    }

    /* ---------- per-item truth ---------- */
    const isVetted = id => vettedOnFile(id) || id in state.vets;
    function canPlace(s) {
      if (!s || s.empty) return false;
      const its = allItemsOf(s);
      if (s.item && !its.length) return false;
      if (its.some(i => !isVetted(i.id))) return false;
      const m = mediaOfSlot(s);
      return !m || isVetted(m.id);
    }
    const canPlacePhoto = id => !!(photoMeta[id] && isVetted(id));
    const ms = t => (t ? new Date(t).getTime() : 0);
    const fmt = (t, withDay = true) => { if (!t) return '—'; const d = new Date(t); if (isNaN(d)) return String(t);
      return d.toLocaleString('en-US', Object.assign({ timeZone: 'America/New_York', hour: 'numeric', minute: '2-digit' }, withDay ? { weekday: 'short', month: 'short', day: 'numeric' } : {})) + ' ET'; };
    const fmtDate = iso => { if (!isDate(iso)) return '—'; const [y, m, d] = iso.split('-').map(Number);
      return new Date(Date.UTC(y, m - 1, d, 12)).toLocaleDateString('en-US', { timeZone: 'UTC', weekday: 'short', month: 'short', day: 'numeric' }); };
    // draft changed more than 10 minutes after Frank's vet, and not re-vetted here. Only vets given during this
    // budget cycle count; older vets on refreshed boards show as age, not as a to-do.
    function changedSinceVet(it) { return !!(it && it.vetted && it.vetted_at && it.updated_at && ms(it.vetted_at) >= ms(L.generated_at || L.generated)
      && ms(it.updated_at) - ms(it.vetted_at) > 6e5 && !(it.id in state.vets)); }
    function staleness(it) {
      if (!it) return null;
      const last = it.updated_at || it.created_at, days = last ? Math.max(0, Math.floor((ms(build.generatedAt) - ms(last)) / 864e5)) : 0;
      const refreshed = !!(it.vetted && it.vetted_at && it.updated_at && ms(it.updated_at) - ms(it.vetted_at) > 864e5);
      return { desk: !!it.stale, last, days, old: days >= 3, carried: it.carried_from || null, carryNote: it.carry_note || null, changed: changedSinceVet(it), refreshed };
    }
    function sourcesOf(it) {
      return (it.provenance || []).filter(isObj).map(p => {
        const when = p.fetched_at_et || p.posted_at_et || fmt(p.retrieved_at || p.fetched_at || p.received_at || p.at);
        const what = p.type === 'derived' ? 'Derived from: ' + [].concat(p.from || []).map(id => (items[id] || {}).headline || id).join(' · ')
          : (p.subject || p.note || p.text || p.endpoint || p.url || p.path || p.source || '');
        const where = p.url || p.endpoint || p.path || (typeof p.from === 'string' ? p.from : '') || '';
        return { type: (p.source && p.type !== 'fencingapi' ? p.type + '/' + p.source : p.type), when: when === '—' ? '' : when, what: String(what), where: String(where) === String(what) ? '' : String(where) };
      });
    }
    const flagsOf = s => (s.flags || []).filter(isObj).map(f => {
      const un = /UNVETTED/.test(f.text || ''), cleared = un && allItemsOf(s).length > 0 && allItemsOf(s).every(i => isVetted(i.id));
      return Object.assign({}, f, { un, cleared });
    });
    const questionsOf = s => questionsFor(s).map((q, i) => ({ q, i, key: qKey(s.key, i), answer: state.answers[qKey(s.key, i)] || '' }));

    /* ---------- fill ---------- */
    function fill() {
      let used = 0;
      slots.forEach(s => { if (state.inc[s.key]) used += costOf(s); });
      loosePhotos.forEach(id => { if (state.photos[id]) used += photoCost(id); });
      const pct = used / total, target = total * cap.oversupply;
      const status = pct < 1 ? 'short' : pct > cap.oversupply ? 'over' : 'ok';
      const gap = status === 'short' ? total - used : status === 'over' ? used - target : 0;
      return { used, total, pct, target, status, gap, words: Math.round(gap * cap.wpi), capWords: Math.round(total * cap.wpi) };
    }

    /* ---------- the packer: costs -> blocks on a three-column page, and the holes left over ----------
       Top-down, running order, each block into the shallowest column(s) that take it. A one-column text or
       table block that doesn't fit in one piece jumps columns the way type does. Whatever is not covered is a
       hole, including space trapped under a wide block, so holes + blocks always add up to the page. It is an
       estimate of how much fits, not a layout: the composer balances, splits and scales art its own way. */
    function pageBlocks(p) {
      return state.order.filter(k => state.inc[k] && state.page[k] === p).map(k => ({ type: 'slot', id: k, span: spanOf(slotBy[k]), cost: costOf(slotBy[k]), kind: (slotBy[k].cost || {}).type }))
        .concat(loosePhotos.filter(id => state.photos[id] && state.photoPage[id] === p).map(id => ({ type: 'photo', id, span: photoSpanOf(id), cost: photoCost(id), kind: 'figure' })));
    }
    function pack(p) {
      const H = pageH(p), h = [0, 0, 0], placed = [], over = [], holes = [], blocks = pageBlocks(p);
      blocks.forEach(b => {
        b.h = b.cost / b.span;
        const cands = b.span >= 3 ? [[0, 1, 2]] : b.span === 2 ? [[0, 1], [1, 2]] : [[0], [1], [2]];
        let best = null, bestSpill = null;
        cands.forEach(c => {
          const y = Math.max.apply(null, c.map(i => h[i])), waste = c.reduce((a, i) => a + y - h[i], 0);
          const cand = { c, y, waste };
          if (y + b.h <= H + 0.05) {
            if (!best || y < best.y - 1e-6 || (Math.abs(y - best.y) < 1e-6 && waste < best.waste)) best = cand;
          } else if (!bestSpill || y < bestSpill.y - 1e-6 || (Math.abs(y - bestSpill.y) < 1e-6 && waste < bestSpill.waste)) {
            bestSpill = cand;
          }
        });
        if (best) {
          best.c.forEach(i => { if (best.y - h[i] > 0.02) holes.push({ col: i, cols: 1, y: h[i], h: best.y - h[i], trapped: true }); h[i] = best.y + b.h; });
          placed.push(Object.assign({}, b, { col: best.c[0], y: best.y, hang: 0, spill: false, onPage: b.h }));
          return;
        }
        // One-column text/tables may still continue across on-page column remnants.
        const open = [0, 1, 2].filter(i => H - h[i] >= MIN_PIECE), room = open.reduce((a, i) => a + Math.max(0, H - h[i]), 0);
        if (b.span === 1 && b.kind !== 'figure' && room >= b.h - 0.05) {
          let left = b.h, part = 0; const parts = [];
          open.forEach(i => { if (left <= 0.01) return; const take = Math.min(left, H - h[i]); parts.push({ col: i, y: h[i], h: take }); h[i] += take; left -= take; });
          parts.forEach(x => placed.push(Object.assign({}, b, x, { part: ++part, parts: parts.length, hang: 0, spill: false, onPage: x.h })));
          return;
        }
        // Place it anyway, hanging past the trim (or stacked in the spill well if every column is already full).
        const minCol = Math.min(h[0], h[1], h[2]);
        let c, y;
        if (minCol >= H - 0.01) {
          c = (bestSpill && bestSpill.c) || [0];
          y = Math.max(H, Math.max.apply(null, c.map(i => h[i])));
        } else {
          c = bestSpill.c; y = bestSpill.y;
        }
        c.forEach(i => {
          const top = Math.min(y, H);
          if (top - h[i] > 0.02 && h[i] < H - 0.01) holes.push({ col: i, cols: 1, y: h[i], h: top - h[i], trapped: true });
          h[i] = y + b.h;
        });
        const onPage = y >= H ? 0 : Math.max(0, Math.min(b.h, H - y));
        const hang = Math.max(0, b.h - onPage);
        const rec = Object.assign({}, b, { col: c[0], y, hang, spill: hang > 0.02, onPage });
        placed.push(rec);
        over.push(rec);
      });
      for (let i = 0; i < 3; i++) { // open space at the foot of each column (on the page only); neighbours of the same depth merge
        const usedH = Math.min(h[i], H), free = H - usedH; if (free <= 0.02) continue;
        const last = holes[holes.length - 1];
        if (last && !last.trapped && last.col + last.cols === i && Math.abs(last.y - usedH) < 0.05) last.cols++;
        else holes.push({ col: i, cols: 1, y: usedH, h: free, trapped: false });
      }
      holes.forEach(x => { x.colIn = x.h * x.cols; x.words = Math.round(x.colIn * cap.wpi); });
      const onPageCol = b => (typeof b.onPage === 'number' ? b.onPage : (b.parts ? b.h : b.cost / (b.span || 1))) * (b.parts ? 1 : (b.span || 1));
      const usedPlaced = placed.reduce((a, b) => a + onPageCol(b), 0);
      const overset = placed.reduce((a, b) => a + (b.hang || 0) * (b.parts ? 1 : (b.span || 1)), 0);
      const spillIn = Math.max(0, Math.max(h[0], h[1], h[2]) - H);
      return { H, h, placed, over, holes, cap: H * 3, used: blocks.reduce((a, b) => a + b.cost, 0), placedUsed: usedPlaced,
        open: holes.reduce((a, x) => a + x.colIn, 0), overset, spillIn, oversetWords: Math.round(overset * cap.wpi) };
    }

    /* ---------- what still needs Frank ---------- */
    function needs() {
      const out = [];
      slots.forEach(s => {
        if (state.inc[s.key]) {
          allItemsOf(s).forEach(it => { if (!isVetted(it.id)) out.push({ kind: 'vet', slot: s.key, id: it.id, blocking: true, text: 'Vet facts: ' + (it.headline || s.slot) }); });
          const m = mediaOfSlot(s); if (m && !isVetted(m.id)) out.push({ kind: 'photo', slot: s.key, id: m.id, blocking: true, text: 'Vet photo: ' + m.filename });
          const it = itemOf(s); if (changedSinceVet(it)) out.push({ kind: 'changed', slot: s.key, id: it.id, blocking: false, text: 'Draft changed after your vet: ' + (it.headline || s.slot) });
          if (s.item && !it) out.push({ kind: 'missing', slot: s.key, blocking: false, text: 'Lineup names an item that is not in staging: ' + s.item });
        }
        questionsOf(s).forEach(q => { if (!q.answer.trim()) out.push({ kind: 'question', slot: s.key, qi: q.i, blocking: true, text: q.q }); });
      });
      loosePhotos.forEach(id => { if (state.photos[id] && !isVetted(id)) out.push({ kind: 'photo', id, blocking: true, text: 'Vet photo: ' + media[id].filename }); });
      if (!isDate(state.publishDate)) out.push({ kind: 'date', blocking: true, text: 'Publish date is not set' });
      if (!state.altDate) out.push({ kind: 'date', blocking: false, text: 'No alternate publish date' });
      const f = fill();
      if (f.status === 'short') out.push({ kind: 'fill', blocking: false, text: 'Issue is short: ' + r1(f.gap) + ' col-in open (≈' + f.words + ' words)' });
      if (f.status === 'over') out.push({ kind: 'fill', blocking: false, text: 'Over Clark’s oversupply line by ' + r1(f.gap) + ' col-in (≈' + f.words + ' words)' });
      return out;
    }

    /* ---------- section history (derived by scripts/build_section_history.py at build time) ----------
       "In this budget" is worked out here, live, from Frank's current includes. */
    const H = hist;
    function sectionRows() {
      if (!H) return null;
      const n = (H.issues || []).length, secOf = H.slotSections || {}, otherOf = H.slotOther || {}, photoOf = H.photoSections || {};
      const norm = t => String(t || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
      const excludedBefore = dec ? (dec.excluded || []) : [];
      const row = (id, base, ks, photos) => {
        const inK = ks.filter(s => state.inc[s.key]), inP = photos.filter(pid => state.photos[pid]);
        const status = inK.length || inP.length ? 'in' : ks.some(s => !s.empty) || photos.length ? 'out' : ks.length ? 'empty' : 'none';
        let note = '';
        if (status !== 'in') {
          const s = ks.find(x => (state.slotNotes[x.key] || '').trim()) || ks.find(x => !x.empty) || ks[0];
          note = !s ? (photos.length ? 'A photo is staged but not on the pages.' : 'No slot in this week’s lineup.')
            : (state.slotNotes[s.key] || '').trim() ? 'You left it out. Your note: ' + state.slotNotes[s.key]
            : s.empty ? 'Empty slot. ' + (s.why || '')
            : excludedBefore.includes(s.key) ? 'You left it out in your ' + fmt(dec.client_submitted_at || dec.at) + ' decision.'
            : s.proposed === false ? 'Clark did not propose it' + (s.why || s.summary ? ': ' + (s.why || s.summary) : '.')
            : 'You pulled it this sitting.';
        }
        if (!base.ran.length) note = ('Has never run. ' + note).trim();
        const gap = base.last ? n + 1 - (H.issues.findIndex(i => i.number === base.last) + 1) : null; // 1 = ran in the latest published issue
        return Object.assign({}, base, { id, slots: ks.map(s => s.key), photos, status, note: note.trim(), gap });
      };
      const official = (H.sections || []).map(s => row(s.id, { name: s.name, frequency: s.frequency || '', ran: s.ran || [], last: s.last, evidence: s.evidence || {}, official: true },
        slots.filter(x => (secOf[x.key] || []).includes(s.id)), loosePhotos.filter(pid => photoOf[pid] === s.id)));
      const names = (H.unregistered || []).map(u => u.name);
      Object.keys(otherOf).forEach(k => { if (slotBy[k] && !names.some(nm => norm(nm) === norm(otherOf[k]))) names.push(otherOf[k]); });
      const unregistered = names.map(name => {
        const u = (H.unregistered || []).find(x => x.name === name) || { name, kind: 'new in this budget', ran: [], evidence: {}, last: null };
        return row('u:' + name, { name, frequency: u.kind || '', ran: u.ran || [], last: u.last, evidence: u.evidence || {}, official: false },
          slots.filter(x => norm(otherOf[x.key]) === norm(name)), []);
      });
      return { issues: H.issues || [], official, unregistered, notes: H.notes || {} };
    }
    function sectionsOfSlot(key) {
      const r = sectionRows(); if (!r) return [];
      return r.official.concat(r.unregistered).filter(x => x.slots.includes(key));
    }

    /* ---------- the submission document (the contract scripts/ingest_budget_submission.py reads) ---------- */
    function isoLocal(d) {
      const p = n => String(n).padStart(2, '0'), o = -d.getTimezoneOffset(), a = Math.abs(o);
      return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + 'T' + p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds()) + (o < 0 ? '-' : '+') + p(a / 60 | 0) + ':' + p(a % 60);
    }
    // pages is the placement contract (slot/photo → 1|2). Placement is not written into notes.
    function placementVal(page, sized, size) { return sized ? { page, span: size.span, widthIn: size.widthIn, heightIn: size.heightIn } : page; }
    const placementOf = () => ({
      slots: Object.fromEntries(slots.filter(s => state.inc[s.key] && (state.page[s.key] === 1 || state.page[s.key] === 2)).map(s => [s.key, placementVal(state.page[s.key], !!state.slotSpan[s.key], slotSize(s))])),
      photos: Object.fromEntries(loosePhotos.filter(id => state.photos[id] && (state.photoPage[id] === 1 || state.photoPage[id] === 2)).map(id => [id, placementVal(state.photoPage[id], !!state.photoSpan[id], photoSize(id))])),
    });
    function resizeOf() {
      const out = {};
      Object.keys(state.resize).forEach(k => {
        const r = state.resize[k];
        if (r && (r.direction === 'expand' || r.direction === 'shrink')) out[k] = Object.assign({}, r);
      });
      return out;
    }
    function layoutOf() {
      const out = {};
      Object.keys(state.layout).forEach(k => { if (state.layout[k] === 'wide' || state.layout[k] === 'tall') out[k] = state.layout[k]; });
      return out;
    }
    const placementNotes = () => { const p = placementOf(), n = Object.keys(p.slots).length + Object.keys(p.photos).length;
      return n ? [n + ' block' + (n === 1 ? '' : 's') + ' placed'] : []; }; // used only as a count label on sign-off, never as notes text
    function submission(now) {
      const entry = s => {
        const it = itemOf(s), e = { slot: s.key, name: s.slot, headline: s.empty ? '' : headlineOf(s), itemId: s.item || null,
          vetted: it ? isVetted(it.id) : true, stale: !!(s.stale || s.waiting || (it && it.stale)) };
        if (s.empty) e.empty = true;
        return e;
      };
      const ordered = state.order.map(k => slotBy[k]).filter(Boolean), empties = slots.filter(s => s.empty);
      const answers = [];
      slots.forEach(s => questionsOf(s).forEach(q => { if (q.answer.trim()) answers.push({ slot: s.key, itemId: s.item || null, question: q.q, answer: q.answer.trim() }); }));
      const prior = dec ? (dec.answers || []) : [];
      const capOrder = a => { const i = prior.findIndex(x => x.slot === a.slot && x.question === a.question); return i < 0 ? 1e6 : i; };
      answers.sort((a, b) => capOrder(a) - capOrder(b)); // captured answers keep their order, new ones follow
      carried.forEach(a => answers.splice(Math.min(capOrder(a), answers.length), 0, Object.assign({}, a, { itemId: a.itemId || (slotBy[a.slot] || {}).item || null })));
      const stripPlacement = t => String(t || '').split(/\n+/).filter(line => !/^Budget placement:/i.test(line.trim())).join('\n\n').trim();
      const lines = [stripPlacement(state.notes), state.filler.trim() && 'FILLER REQUEST: ' + state.filler.trim()];
      const slotNotes = {};
      Object.keys(state.slotNotes).forEach(k => { if (slotBy[k] && String(state.slotNotes[k]).trim()) slotNotes[k] = String(state.slotNotes[k]).trim(); });
      return {
        publishDate: state.publishDate, practice: L.mode !== 'real', pretend: false, targetWeek: L.target_week || 'next', issue: L.issue || null,
        includedSlots: ordered.filter(s => state.inc[s.key]).map(entry),
        excludedSlots: ordered.filter(s => !state.inc[s.key]).concat(empties).map(entry), // empty slots listed as excluded, as before
        photoIncludes: photoList.map(p => p.id).filter(id => state.photos[id] && isVetted(id)), // never queue an unvetted photo
        notes: lines.filter(Boolean).join('\n\n'), slotNotes, answers, order: state.order.slice(),
        pageVersion: PAGE_VERSION, submittedAt: isoLocal(now || new Date()),
        vets: Object.keys(state.vets).filter(id => (items[id] || media[id]) && !vettedOnFile(id)).map(id => ({ id, vet_notes: String(state.vets[id] || '').trim() })),
        publishDateAlt: isDate(state.altDate) ? state.altDate : null, // optional: alternate run date, or null for "no alternate"
        budgetVersion: build.budgetVersion == null ? null : build.budgetVersion, dataVersion: build.dataVersion || null,
        pages: placementOf(),
        resize: resizeOf(),
        layout: layoutOf(),
      };
    }
    const submissionName = doc => 'budget-submission-no-' + issueNo + '-' + doc.publishDate + (build.budgetVersion ? '-v' + build.budgetVersion : '') + '-'
      + doc.submittedAt.replace(/[-:]/g, '').replace('T', '-').slice(0, 15) + '.json';

    /* ---------- mutations ---------- */
    const act = {
      include(k, v) {
        const s = slotBy[k]; if (!s || s.empty) return;
        if (v && !canPlace(s)) return; // unvetted items cannot run; vet on the slip first
        state.inc[k] = !!v;
        const m = mediaOfSlot(s);
        if (m && s.cost && s.cost.type === 'figure' && s.cost.head) {
          if (v && isVetted(m.id)) state.photos[m.id] = true;
          else if (!v) state.photos[m.id] = false;
        }
        emit('include');
      },
      place(k, p) { if (!slotBy[k] || slotBy[k].empty) return; if (!canPlace(slotBy[k])) return; if (state.page[k] !== p || !state.inc[k]) state.moved[k] = p; state.page[k] = p; act.include(k, true); },
      photo(id, v, p) { if (!photoMeta[id]) return; if (v && !canPlacePhoto(id)) return; if (p) state.photoPage[id] = p; state.photos[id] = !!v; emit('photo'); },
      vet(id, note) { state.vets[id] = note || ''; emit('vet'); },
      unvet(id) {
        delete state.vets[id];
        slots.forEach(s => { if (state.inc[s.key] && !canPlace(s)) state.inc[s.key] = false; });
        if (state.photos[id] && !canPlacePhoto(id)) state.photos[id] = false;
        emit('vet');
      },
      answer(k, i, text) { state.answers[qKey(k, i)] = text; emit('answer'); },
      slotNote(k, text) { state.slotNotes[k] = text; emit('note'); },
      notes(text) { state.notes = text; emit('notes'); },
      filler(text) { state.filler = text; emit('notes'); },
      date(d) { state.publishDate = d; emit('date'); },
      alt(d) { state.altDate = d; emit('date'); },
      move(k, dir) { const o = state.order, i = o.indexOf(k); let j = i + dir;
        while (j >= 0 && j < o.length && !state.inc[o[j]] && state.inc[k]) j += dir; // skip past slots in the bank
        if (i < 0 || j < 0 || j >= o.length) return; o.splice(i, 1); o.splice(j, 0, k); emit('order'); },
      before(k, other) { const o = state.order; if (k === other || !o.includes(k) || !o.includes(other)) return; o.splice(o.indexOf(k), 1); o.splice(o.indexOf(other), 0, k); },
      setLayout(k, v) {
        if (v !== 'wide' && v !== 'tall') return;
        if (photoMeta[k]) {
          state.layout[k] = v;
          state.photoSpan[k] = v === 'tall' ? 1 : Math.max(2, (photoMeta[k] || {}).span || 2);
          emit('layout'); return;
        }
        const s = slotBy[k]; if (!s || s.empty) return;
        state.layout[k] = v;
        state.slotSpan[k] = layoutSpan(s, v);
        emit('layout');
      },
      setSpan(k, span) {
        span = Math.max(1, Math.min(3, Math.round(Number(span) || 1)));
        if (photoMeta[k]) {
          state.photoSpan[k] = span;
          state.layout[k] = span >= 2 ? 'wide' : 'tall';
          emit('resize'); return;
        }
        const s = slotBy[k]; if (!s || s.empty) return;
        state.slotSpan[k] = span;
        state.layout[k] = span >= 2 ? 'wide' : 'tall';
        emit('resize');
      },
      setResize(k, direction, target) {
        const s = slotBy[k]; if (!s || s.empty) return;
        if (!direction) { delete state.resize[k]; emit('resize'); return; }
        applyResize(s, direction, target);
        emit('resize');
      },
    };
    const thumb = name => (((D.thumbs || {})[fileOf(name)]) || {}).src || '';
    function answersForSave() { const m = {}; slots.forEach(s => questionsOf(s).forEach(q => { m[q.key] = q.q; })); return m; }

    return { PAGE_VERSION, D, L, cap, dec, build, items, media, slots, slotBy, state, on, emit, act, costOf, photoCost, spanOf, wordsOf, fill, pack, pageH, needs, itemOf, allItemsOf,
      headlineOf, shortName, isVetted, vettedOnFile, canPlace, canPlacePhoto, staleness, sourcesOf, flagsOf, questionsOf, mediaOfSlot, loosePhotos, photoMeta, sectionRows, sectionsOfSlot, submission, submissionName,
      placementNotes, placementOf, resizeOf, layoutOf, serialize, restore, answersForSave, fmt, fmtDate, r1, esc, thumb, total, issueNo, GUT,
      layoutSpec, canSwitchLayout, currentLayout, layoutSpan, photoSpanOf, photoLayoutOf, photoSize, slotSize, snapSpan, baseWordsOf, naturalSpan, SNAP_WIDTHS };
  }

  const Core = { PAGE_VERSION, make };
  if (typeof module === 'object' && module.exports) module.exports = Core;
  else root.BudgetCore = Core;
})(this);
