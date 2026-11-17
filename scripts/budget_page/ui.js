/* En Garde Gazette — Budget page (the two-page spread): DOM. Logic is in core.js (BudgetCore).
   Interaction and look follow the approved mockup references/concept-a.html: two pages, blocks sized by the
   capacity model, a bank of what isn't running, drag on/off the pages (desktop), holes in column-inches and
   words, a slip per item, grease-pencil marks. On a phone the same moves are the slip's Page 1 / Page 2 /
   Bank buttons. Nothing leaves the file: Sign off downloads/copies the submission JSON. */
(function () {
  'use strict';
  const D = JSON.parse(document.getElementById('budget-data').textContent);
  const core = BudgetCore.make(D);

  /* ---- detail views: the per-item slip, the section-history table, the fill meter (from the mockup) ---- */
  const ui = (() => {
    const { esc, state, slotBy, items, media, fmt, r1 } = core;
    const shortName = s => s.slot.split(' — ')[0];
    function vetBlock(id, label) {
      const x = items[id] || media[id], session = id in state.vets, changed = items[id] && core.staleness(items[id]).changed;
      const note = `<input class="sh-in" data-vetnote="${esc(id)}" placeholder="Vet note (optional)" value="${esc(state.vets[id] || '')}">`;
      let body;
      if (session) body = `<div class="vet ok"><b>✔ Vetted here</b> — goes out in this submission. <button class="lnk" data-act="unvet" data-id="${esc(id)}">undo</button></div>${note}`;
      else if (x.vetted && changed) body = `<div class="vet warn"><b>Vetted ${fmt(x.vetted_at)}</b>, but the draft changed ${fmt(x.updated_at, false)} — after that vet.</div>${note}<button class="btn pri" data-act="vet" data-id="${esc(id)}">Vet the current draft</button>`;
      else if (x.vetted) body = `<div class="vet ok">✔ Vetted by ${esc(x.vetted_by || 'desk rule')}${x.vetted_at ? ' · ' + fmt(x.vetted_at) : ''}${x.vet_scope ? ` <span class="dim">· scope: ${esc(x.vet_scope.replace(/_/g, ' '))}</span>` : ''}${x.facts_status ? ` <span class="dim">· facts: ${esc(x.facts_status)}</span>` : ''}</div>`;
      else body = `<div class="vet bad"><b>UNVETTED</b> — not approved for print.</div>${note}<button class="btn pri" data-act="vet" data-id="${esc(id)}">Vet for print</button>`;
      return `<div class="sh-vet"><div class="sh-lbl">${esc(label)}</div>${body}</div>`;
    }
    function staleLine(it) {
      const st = core.staleness(it); if (!st) return '';
      const bits = [`Desk stale mark: <b>${st.desk ? 'STALE' : 'none'}</b>`, `last touched ${fmt(st.last)}${st.days ? ` (${st.days} day${st.days > 1 ? 's' : ''} before this build)` : ''}`];
      if (st.old) bits.push('<b class="warnc">may be out of date</b>');
      if (st.refreshed) bits.push('refreshed since your vet');
      if (st.carried) bits.push('carried from ' + esc(st.carried.split('/').pop()) + (st.carryNote ? ` — ${esc(st.carryNote)}` : ''));
      return `<div class="sh-stale ${st.old || st.desk ? 'old' : ''}">${bits.join(' · ')}</div>`;
    }
    const tableHTML = t => t && Array.isArray(t.rows) ? `<table class="sh-tbl"><tr>${(t.head || []).map(h => `<th>${esc(h)}</th>`).join('')}</tr>${t.rows.map(r => `<tr>${r.map(c => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</table>` : '';
    function sourcesHTML(it) {
      const src = core.sourcesOf(it);
      return `<div class="sh-src"><div class="sh-lbl">Sources — ${esc(it.headline || it.id)} <span class="dim">(${esc(it.source)}${it.from ? ', from ' + esc(it.from) : ''})</span></div>` +
        (src.length ? `<ol>${src.map(p => `<li><span class="tag">${esc(p.type)}</span> ${esc(p.what)}${p.where ? `<br><span class="dim mono">${esc(p.where)}</span>` : ''}${p.when ? `<br><span class="dim">${esc(p.when)}</span>` : ''}</li>`).join('')}</ol>` : '<p class="dim">No provenance entries recorded for this item.</p>') +
        (Array.isArray(it.facts) && it.facts.length ? `<details><summary>Fact checks (${it.facts.length})</summary><ul>${it.facts.map(f => `<li>${esc(f.claim)} <span class="dim">— ${esc(f.status)}</span></li>`).join('')}</ul></details>` : '') +
        (it.vet_notes ? `<details><summary>Desk &amp; vet log</summary><p class="pre">${esc(it.vet_notes)}</p></details>` : '') + '</div>';
    }
    function historyLine(key) {
      const rows = core.sectionsOfSlot(key), R = core.sectionRows(); if (!R || !rows.length) return '';
      return rows.map(r => `<div class="sh-hist"><div class="sh-lbl">Section history — ${esc(r.name)}${r.official ? '' : ' <span class="tag">not in official list</span>'}</div>
        <span class="dots">${R.issues.map(i => `<i class="${r.ran.includes(i.number) ? 'on' : ''}" title="No. ${i.number} (${esc(i.date)})${r.evidence[i.number] ? ': ' + esc(r.evidence[i.number].join('; ')) : ': did not run'}">${i.number}</i>`).join('')}<i class="now ${r.status}" title="This budget">${esc(core.issueNo)}</i></span>
        <span class="dim">${r.ran.length ? `last ran No. ${r.last}` : 'has never run'} · ${esc(String(r.frequency).replace(/_/g, ' '))}</span></div>`).join('');
    }
    function sheet(key) {
      const s = slotBy[key], it = core.itemOf(s), all = core.allItemsOf(s), m = core.mediaOfSlot(s), inc = state.inc[key];
      const qs = core.questionsOf(s), flags = core.flagsOf(s), c = s.cost;
      const costTxt = c ? `${r1(core.costOf(s))} col-in${c.type !== 'table' && c.type !== 'table_rows' && core.wordsOf(s) ? ` · ~${core.wordsOf(s)}w` : ''}${c.rows ? ` · ${c.rows} rows` : ''} · ${core.spanOf(s)} col wide` : '';
      return `<div class="sheet" data-slot="${esc(key)}">
        <div class="sh-k">${esc(s.slot)}</div>
        <h2 class="sh-h">${esc(s.title || (it && it.headline) || shortName(s))}</h2>
        ${s.item && !it ? `<div class="sh-now">The lineup names item <span class="mono">${esc(s.item)}</span>, which is not in staging. Nothing to vet or read yet.</div>` : ''}
        ${it && s.title && it.headline && it.headline !== s.title ? `<div class="sh-now">Draft headline now: <b>${esc(it.headline)}</b></div>` : ''}
        ${s.empty ? `<div class="sh-empty">EMPTY SLOT — nothing to run. ${esc(s.why || '')}</div>` :
          `<div class="sh-row"><div class="seg"><button data-act="inc" data-v="1" class="${inc ? 'on' : ''}">In the issue</button><button data-act="inc" data-v="0" class="${inc ? '' : 'on'}">Left out</button></div>
           <span class="dim">${costTxt} · desk ${s.proposed ? 'proposed it' : 'did not propose it'}${s.budget ? ' · budget: ' + esc(s.budget) : ''}</span></div>`}
        ${s.summary ? `<p class="sh-sum">${esc(s.summary)}</p>` : ''}
          ${qs.map(q => `<div class="sh-q ${q.answer.trim() ? 'done' : ''}"><div class="sh-lbl">The desk asks</div><p>${esc(q.q)}</p><textarea class="sh-in" data-q="${q.i}" rows="2" placeholder="Your answer…">${esc(q.answer)}</textarea></div>`).join('')}
        ${m ? `<img class="sh-img" src="${core.thumb(m.filename)}" alt="">` : ''}
        ${all.map(x => vetBlock(x.id, all.length > 1 ? 'Vet — ' + x.headline : 'Vet the facts')).join('')}
        ${m && m.id ? vetBlock(m.id, 'Vet the photo — ' + m.filename) + (m.note ? `<p class="dim sm">${esc(m.note)}${m.license ? ' · ' + esc(m.license) : ''}</p>` : '') : ''}
        ${flags.length ? `<ul class="sh-flags">${flags.map(f => `<li class="${f.level} ${f.cleared ? 'cleared' : ''}"><span>${esc(f.text)}</span>${f.cleared ? ' <em>cleared — vetted since the desk wrote this</em>' : ''}</li>`).join('')}</ul>` : ''}
        ${it ? staleLine(it) : ''}
        ${it && (it.body || s.table) ? `<details class="sh-body"><summary>${s.table ? 'The table as it would print' : `The draft${it.word_count ? ` (${it.word_count}w)` : ''}`}</summary>${tableHTML(s.table)}${it.body ? `<p>${esc(it.body)}</p>` : ''}${Array.isArray(it.held_rows) && it.held_rows.length ? `<p class="dim">Held rows: ${it.held_rows.map(r => esc([].concat(r).join(' · '))).join('; ')}</p>` : ''}</details>` : ''}
        ${all.map(sourcesHTML).join('')}
        <div class="sh-note"><div class="sh-lbl">Slot note to the desk</div><textarea class="sh-in" data-slotnote rows="3" placeholder="Anything about this slot: cuts, swaps, standing rules…">${esc(state.slotNotes[key] || '')}</textarea></div>
        ${historyLine(key)}</div>`;
    }
    function photoSheet(id) {
      const m = media[id], p = core.photoMeta[id] || {}, on = state.photos[id];
      return `<div class="sheet" data-photo="${esc(id)}"><div class="sh-k">Photo — ${esc(m.kind)}</div><h2 class="sh-h">${esc(m.filename)}</h2>
        <img class="sh-img" src="${core.thumb(m.filename)}" alt="">
        <div class="sh-row"><div class="seg"><button data-act="photo" data-v="1" class="${on ? 'on' : ''}">Run it</button><button data-act="photo" data-v="0" class="${on ? '' : 'on'}">Leave out</button></div>
        <span class="dim">${r1(core.photoCost(id))} col-in · ${p.span || 1} col wide · desk ${p.proposed ? 'proposed it' : 'did not propose it'}</span></div>
        <p class="sh-sum">${esc(p.note || '')}</p>${m.caption ? `<p><span class="sh-lbl">Caption on file</span> ${esc(m.caption)}</p>` : ''}
        ${vetBlock(id, 'Vet the photo')}
        <div class="sh-src"><div class="sh-lbl">Source</div><p>${esc(m.source)}${m.from ? ' · ' + esc(m.from) : ''}${m.retrieved_at ? ' · ' + fmt(m.retrieved_at) : ''}${m.url ? `<br><span class="dim mono">${esc(m.url)}</span>` : ''}</p><p class="dim sm">${esc(m.note || '')}</p></div></div>`;
    }
    // wire a container holding a sheet; text fields update state silently, buttons re-render
    function bind(el) {
      el.addEventListener('click', e => {
        const b = e.target.closest('[data-act]'); if (!b) return;
        const sh = b.closest('.sheet'), key = sh && sh.dataset.slot, a = b.dataset.act;
        if (a === 'inc') core.act.include(key, b.dataset.v === '1');
        else if (a === 'photo') core.act.photo(sh.dataset.photo, b.dataset.v === '1');
        else if (a === 'vet') { const n = sh.querySelector(`[data-vetnote="${CSS.escape(b.dataset.id)}"]`); core.act.vet(b.dataset.id, n ? n.value : ''); }
        else if (a === 'unvet') core.act.unvet(b.dataset.id);
      });
      el.addEventListener('input', e => {
        const t = e.target, sh = t.closest('.sheet'); if (!sh) return; const key = sh.dataset.slot;
        if (t.dataset.q != null) { core.act.answer(key, +t.dataset.q, t.value); t.closest('.sh-q').classList.toggle('done', !!t.value.trim()); }
        else if ('slotnote' in t.dataset) core.act.slotNote(key, t.value);
        else if (t.dataset.vetnote && t.dataset.vetnote in state.vets) { state.vets[t.dataset.vetnote] = t.value; core.emit('text'); }
      });
    }
    const TEXTY = ['answer', 'note', 'notes', 'text']; // emit reasons that must not rebuild a focused form
    function history(compact) {
      const R = core.sectionRows(), lab = { in: 'IN', out: 'left out', empty: 'empty', none: '—' };
      if (!R) return '<h3>Section history</h3><p class="dim">Section history was not derived for this build (see the builder’s warning).</p>';
      const nums = R.issues.map(i => i.number);
      const row = r => `<tr class="${r.status}${r.ran.length ? '' : ' never'}"><th>${esc(r.name)}<small>${esc(String(r.frequency).replace(/_/g, ' '))}</small></th>
        ${R.issues.map(i => `<td class="c ${r.ran.includes(i.number) ? 'on' : ''}" title="${r.evidence[i.number] ? esc(r.evidence[i.number].join('; ')) : 'did not run in No. ' + i.number}">${r.ran.includes(i.number) ? '●' : '·'}</td>`).join('')}
        <td class="last">${r.ran.length ? 'No. ' + r.last + (r.gap > 1 ? `<small>sat out ${r.gap - 1}</small>` : '') : '<b>never</b>'}</td><td class="st"><span class="chip ${r.status}">${lab[r.status]}</span></td>${compact ? '' : `<td class="nt">${esc(r.note)}</td>`}</tr>${compact && r.note ? `<tr class="ntr"><td class="nt" colspan="${R.issues.length + 3}">${esc(r.note)}</td></tr>` : ''}`;
      const head = `<tr><th></th>${R.issues.map(i => `<th class="c" title="${esc(i.date + ' — ' + i.headline)}">${i.number}</th>`).join('')}<th>Last ran</th><th>No. ${esc(core.issueNo)}</th>${compact ? '' : '<th>If absent, why</th>'}</tr>`;
      return `<h3>Section history, ${nums.length ? 'Nos. ' + nums[0] + '–' + nums[nums.length - 1] : 'no published issues yet'}</h3>
        <table class="hist">${head}${R.official.map(row).join('')}${R.unregistered.length ? `<tr class="sep"><td colspan="${R.issues.length + 4}">Printed kickers that are not in the official section list</td></tr>${R.unregistered.map(row).join('')}` : ''}</table>
        <p class="dim sm">Derived from the published issues when this page was built. Dots: hover for what actually printed. “Sat out” counts the published issues since it last ran. The No. ${esc(core.issueNo)} column follows what is on the pages right now.</p>
        ${Object.keys(R.notes).map(n => `<p class="dim sm">No. ${esc(n)}: ${esc(R.notes[n].join('; '))}</p>`).join('')}`;
    }
    function meter() {
      const f = core.fill(), max = 1.3, w = Math.min(f.pct, max) / max * 100;
      const msg = f.status === 'short' ? `short by ${r1(f.gap)} col-in ≈ ${f.words.toLocaleString()} words` : f.status === 'over' ? `over by ${r1(f.gap)} col-in ≈ ${f.words.toLocaleString()} words` : 'full, inside the oversupply cushion';
      return `<div class="meter ${f.status}" title="Estimate from the desk's capacity model (calibrated against the composed issues): prose words ÷ ${core.cap.wpi} per col-in (${core.cap.wpi_feature} for the lead), plus heads, table rows and art. Two pages hold ${r1(f.total)} col-in ≈ ${f.capWords.toLocaleString()} words; the desk aims to oversupply ×${core.cap.oversupply}.">
        <div class="m-bar"><i style="width:${w}%"></i><b style="left:${100 / max}%"></b><b class="os" style="left:${core.cap.oversupply / max * 100}%"></b></div>
        <div class="m-txt"><strong>${Math.round(f.pct * 100)}% full</strong> · ${r1(f.used)} of ${r1(f.total)} col-in · <span class="m-msg">${msg}</span></div></div>`;
    }
    return { sheet, photoSheet, bind, history, meter, shortName, TEXTY, vetBlock, tableHTML };
  })();

  /* ================= the spread ================= */
  const $ = q => document.querySelector(q), S = core.state, E = core.esc, cap = core.cap, dec = core.dec || {};
  const A = { sel: null, tab: 'needs' };
  const GUT = core.GUT, CW = cap.col_width_in, PW = 3 * CW + 2 * GUT;
  const colX = i => i * (CW + GUT), spanW = n => n * CW + (n - 1) * GUT;
  const FURN = { 1: [['mast', 0.98], ['dl', 0.5]], 2: [['dl', 0.5]] }; // drawn only; the page depths come from the capacity model
  const NO = core.issueNo;

  let NEEDS = [];
  const rowIn = c => ((c.span || 1) > 1 ? cap.row_full : cap.row_rail);
  function marks(key) {
    const n = NEEDS.filter(x => x.slot === key), s = core.slotBy[key], it = core.itemOf(s); let m = '';
    if (n.some(x => x.kind === 'vet' || x.kind === 'photo')) m += '<i class="mk vet" title="Needs your vet">VET</i>';
    if (n.some(x => x.kind === 'question')) m += '<i class="mk q" title="The desk asked you something here">?</i>';
    if (n.some(x => x.kind === 'changed')) m += '<i class="mk chg" title="Draft changed after your vet">Δ</i>';
    if ((S.slotNotes[key] || '').trim()) m += '<i class="mk note" title="You left a slot note">✎</i>';
    if (it && core.staleness(it).old) m += `<i class="mk age" title="Last touched ${core.staleness(it).days} days before this build — may be out of date">${core.staleness(it).days}d</i>`;
    if (!m && it && core.allItemsOf(s).every(i => core.isVetted(i.id))) m = '<i class="mk ok" title="Vetted">✓</i>';
    return `<span class="marks">${m}</span>`;
  }
  const isSel = (t, id) => (A.sel && A.sel.type === t && A.sel.id === id ? ' sel' : '');

  function blockHTML(b, ppi) {
    const pos = `left:${colX(b.col) * ppi}px;top:${b.y * ppi}px;width:${spanW(b.span) * ppi}px;height:${Math.max(6, b.h * ppi - 3)}px`;
    if (b.type === 'photo') {
      const m = core.media[b.id];
      return `<div class="blk t-photo${isSel('photo', b.id)}" draggable="true" tabindex="0" data-photo="${E(b.id)}" style="${pos}"><span class="marks">${core.isVetted(b.id) ? '<i class="mk ok">✓</i>' : '<i class="mk vet">VET</i>'}</span><img src="${core.thumb(m.filename)}" alt=""><div class="k">Photo · ${E(m.kind)}</div></div>`;
    }
    const s = core.slotBy[b.id], c = s.cost || {}, head = core.headlineOf(s), cont = b.part > 1;
    let inner = `<div class="k">${E(ui.shortName(s))}</div>`;
    if (cont) inner += `<div class="cont-l">continued</div><div class="greek"></div>`;
    else if (c.type === 'figure') inner += `<img src="${core.thumb(s.thumb)}" alt="">` + (c.head ? `<div class="h">${E(head)}</div><div class="greek" style="flex:1.3"></div>` : '');
    else if (s.table && Array.isArray(s.table.rows)) inner += (s.title ? `<div class="h">${E(head)}</div>` : '') + s.table.rows.map(r => `<div class="tr" style="height:${rowIn(c) * ppi}px;line-height:${rowIn(c) * ppi}px;font-size:${Math.min(9, rowIn(c) * ppi * .8)}px"><b>${E(r[0])}</b> · ${E(r.slice(1).join(' · '))}</div>`).join('');
    else inner += `<div class="h">${E(head)}</div><div class="greek"></div>`;
    return `<div class="blk t-${E(c.type || 'prose')}${c.feature ? ' lead' : ''}${b.span >= 2 ? ' wide' : ''}${cont ? ' cont' : ''}${isSel('slot', b.id)}" draggable="true" tabindex="0" data-slot="${E(b.id)}" style="${pos}">${cont ? '' : marks(b.id)}${inner}</div>`;
  }

  function renderPages() {
    const host = $('#pages');
    if (!host.children.length) host.innerHTML = [1, 2].map(p => `<div class="page" data-page="${p}">${FURN[p].map(([c]) => `<div class="furn ${c}" data-f="${c}"></div>`).join('')}<div class="cols" data-page="${p}"></div><div class="pfoot"></div><div class="overset"></div></div>`).join('');
    [1, 2].forEach(p => {
      const pg = host.querySelector(`.page[data-page="${p}"]`), cols = pg.querySelector('.cols'), ppi = cols.clientWidth / PW, r = core.pack(p);
      FURN[p].forEach(([c, inch]) => { const f = pg.querySelector(`[data-f="${c}"]`); f.style.height = inch * ppi + 'px';
        f.innerHTML = c === 'mast' ? 'En Garde Gazette' : `<span>${E((core.L.issue || {}).label || 'Issue No. ' + NO)}</span><span>${E(core.fmtDate(S.publishDate))}</span><span>Page ${p}</span>`; });
      cols.style.height = r.H * ppi + 'px';
      const holes = r.holes.filter(x => x.h > 0.3).map(x => `<div class="hole${x.trapped ? ' trap' : ''}" style="left:${colX(x.col) * ppi}px;width:${spanW(x.cols) * ppi}px;top:${x.y * ppi + 2}px;height:${x.h * ppi - 2}px">${
        x.h > 0.7 ? `OPEN<br>${core.r1(x.colIn)} col-in<br>≈ ${x.words}w` : x.h * ppi > 13 ? `${core.r1(x.colIn)} col-in` : ''}</div>`).join('');
      cols.innerHTML = r.placed.map(b => blockHTML(b, ppi)).join('') + holes;
      pg.querySelector('.pfoot').innerHTML = `<span>PAGE ${p} · ${core.r1(r.placedUsed)} of ${core.r1(r.cap)} col-in placed</span><span class="${r.open > 0.5 || r.over.length ? 'short' : ''}">${
        r.over.length ? `OVERSET by ${core.r1(r.overset)} col-in` : `open ${core.r1(r.open)} col-in ≈ ${Math.round(r.open * cap.wpi)} words`}</span>`;
      pg.querySelector('.overset').innerHTML = r.over.length ? 'OVERSET — does not fit on this page: ' + r.over.map(b => `<span data-${b.type}="${E(b.id)}">${E(b.type === 'slot' ? ui.shortName(core.slotBy[b.id]) : core.media[b.id].filename)} · ${core.r1(b.cost)}</span>`).join('') : '';
    });
  }

  function stripHTML(s) {
    const it = core.itemOf(s), k = s.key;
    if (s.empty) return `<div class="strip ghost${isSel('slot', k)}" tabindex="0" data-slot="${E(k)}">${marks(k)}<div class="k">Empty slot</div><div class="h">${E(s.slot)}</div><div class="w">${E(s.why || '')}</div></div>`;
    const who = (k in (dec.slotNotes || {})) || (dec.excluded || []).includes(k) ? 'You left it out' : s.auto ? 'Not slotted by the desk' : s.waiting ? 'Desk is waiting on it' : s.proposed ? 'Pulled' : 'Desk did not propose it';
    const unvet = core.allItemsOf(s).some(i => !core.isVetted(i.id));
    return `<div class="strip${s.item && !it ? ' missing' : ''}${isSel('slot', k)}" draggable="true" tabindex="0" data-slot="${E(k)}">${marks(k)}${s.thumb ? `<img src="${core.thumb(s.thumb)}" alt="">` : ''}<div class="k">${E(ui.shortName(s))}</div>
      <div class="h">${E(core.headlineOf(s) || s.slot)}</div><div class="w">${who} · ${core.r1(core.costOf(s))} col-in${unvet ? ' · <b style="color:var(--bad)">unvetted</b>' : ''}${s.item && !it ? ' · <b style="color:var(--bad)">not in staging</b>' : ''}</div>
      <div class="add">run on <button data-add="1">p.1</button><button data-add="2">p.2</button></div></div>`;
  }
  function renderBank() {
    const out = S.order.map(k => core.slotBy[k]).filter(s => s && !S.inc[s.key]);
    const photos = core.loosePhotos.filter(id => !S.photos[id]);
    const np = (core.L.not_proposed || []).concat((core.L.held || []).map(h => ({ item: h.id || h.item, why: h.why || h.note || 'Held.' })));
    const empties = core.slots.filter(s => s.empty);
    $('#bank').innerHTML = `<h3>The bank — not running (${out.length})</h3>${out.map(stripHTML).join('') || '<p class="np">Everything is on the pages.</p>'}
      ${core.loosePhotos.length ? `<h3>Loose art (${photos.length})</h3>${photos.map(id => { const m = core.media[id]; return `<div class="strip${isSel('photo', id)}" draggable="true" tabindex="0" data-photo="${E(id)}"><img src="${core.thumb(m.filename)}" alt=""><div class="k">${E(m.kind)}</div><div class="h">${E(String(m.filename).replace(/\.\w+$/, ''))}</div><div class="w">${core.r1(core.photoCost(id))} col-in · ${core.isVetted(id) ? 'vetted' : '<b style="color:var(--bad)">unvetted</b>'}</div><div class="add">run on <button data-add="1">p.1</button><button data-add="2">p.2</button></div></div>`; }).join('') || '<p class="np">All of it is on the pages.</p>'}` : ''}
      ${empties.length ? `<h3>Empty slots</h3>${empties.map(stripHTML).join('')}` : ''}
      ${np.length ? `<h3>Staged, not in the lineup</h3>${np.map(n => `<p class="np"><b>${E((core.items[n.item] || {}).headline || n.item)}</b>${E(n.why || '')}</p>`).join('')}` : ''}`;
  }

  function renderTop() {
    NEEDS = core.needs();
    const blk = NEEDS.filter(n => n.blocking).length, adv = NEEDS.length - blk, b = core.build;
    $('#iss').textContent = (core.L.issue || {}).label || 'Issue No. ' + NO;
    $('#stamp').innerHTML = `${b.budgetVersion ? 'BUDGET v' + E(b.budgetVersion) : 'PREVIEW'}<small>${E(String(b.versionLabel || '').split(' · ')[1] || '')}</small>`;
    $('#rd').textContent = core.fmtDate(S.publishDate); $('#ad').textContent = S.altDate ? 'alt ' + core.fmtDate(S.altDate) : 'no alternate';
    $('#meter').innerHTML = ui.meter();
    const nb = $('#needbtn'); nb.className = 'needbtn' + (blk ? '' : ' clear');
    nb.textContent = blk ? `${blk} need${blk > 1 ? '' : 's'} you` : adv ? `Nothing blocking · ${adv} to check` : 'All clear';
  }
  function renderDatePop() {
    const pub = core.L.publish || {};
    $('#rpop').innerHTML = `${pub.why ? `<div class="sh-lbl">The desk picked ${E(pub.label || core.fmtDate(pub.date))} because</div><p class="why">${E(pub.why)}</p>` : ''}
      <label for="dmain">Target publish date</label><input type="date" id="dmain" value="${E(S.publishDate)}">
      <label for="dalt">Alternate</label><input type="date" id="dalt" value="${E(S.altDate)}">
      <div class="acts"><button class="btn" id="dswap">⇄ Swap: run on the alternate</button></div>
      <p class="dim sm" style="margin:8px 0 0">The target goes out as <span class="mono">publishDate</span>, the alternate as <span class="mono">publishDateAlt</span> (blank = no alternate).</p>`;
  }

  function needsPane() {
    const lab = { vet: 'VET', photo: 'PHOTO', question: 'ASKED', changed: 'CHANGED', fill: 'FILL', date: 'DATE', missing: 'MISSING' };
    const li = n => `<div class="need${n.blocking ? '' : ' adv'}" ${n.slot ? `data-go="${E(n.slot)}"` : n.kind === 'photo' ? `data-gop="${E(n.id)}"` : n.kind === 'date' ? 'data-date' : ''}><span class="t">${lab[n.kind] || 'CHECK'}</span><span>${E(n.text)}${n.slot ? `<small>${E(core.slotBy[n.slot].slot)}${S.inc[n.slot] ? '' : ' · in the bank'}</small>` : ''}</span></div>`;
    const blk = NEEDS.filter(n => n.blocking), adv = NEEDS.filter(n => !n.blocking);
    const bench = core.slots.filter(s => !s.empty && !S.inc[s.key] && core.allItemsOf(s).some(i => !core.isVetted(i.id)));
    return `<h3>Before the budget can be signed off</h3>${blk.length ? blk.map(li).join('') : '<p class="allclear">✔ Nothing is blocking. Every block on the pages is vetted and every desk question has an answer.</p>'}
      <h3>Worth a look</h3>${adv.length ? adv.map(li).join('') : '<p class="dim">Nothing.</p>'}
      <h3>In the bank, unvetted</h3><p class="dim sm">Only matters if you run them.</p>${bench.map(s => `<div class="need adv" data-go="${E(s.key)}"><span class="t">BANK</span><span>${E(core.headlineOf(s) || s.slot)}<small>${core.allItemsOf(s).filter(i => !core.isVetted(i.id)).map(i => E(i.headline || i.id)).join(' · ')}</small></span></div>`).join('') || '<p class="dim">None.</p>'}`;
  }
  function readPane() {
    const ds = core.L.desk_summary || [], v = D.versions || [], log = D.decisionLog || [], last = log[log.length - 1], cal = core.build.calibration;
    const gen = core.L.generated_at || core.L.generated;
    return `<div class="read"><h3>Clark Kent’s read on the week</h3>${ds.length ? `<p class="lede">${E(ds[0])}</p>${ds.slice(1).map(p => `<p>${E(p)}</p>`).join('')}` : '<p class="dim">The lineup has no desk summary this week.</p>'}
      ${gen ? `<p class="dim sm">Written when the lineup was generated (${core.fmt(gen)}). Vet flags in it predate anything you vetted since.</p>` : ''}
      <h4>Since then</h4><ul class="vers">${v.map(x => `<li class="${x.v === core.build.budgetVersion ? 'cur' : ''}">v${E(x.v)} · built ${core.fmt(x.built_at, false)} · ${x.decisions_through ? 'decisions through ' + core.fmt(x.decisions_through, false) : 'no decisions yet'} · data ${E(x.data)}</li>`).join('') || '<li>This is a preview build; it is not numbered.</li>'}</ul>
      ${log.length ? `<h4>Your decisions on file (${log.length})</h4><ul class="vers">${log.map(d => `<li>#${d.n} · ${d.kind === 'chat' ? 'by chat' : 'budget page'} · ${core.fmt(d.through)} · ${d.included} on the pages${d.vets ? ' · ' + d.vets + ' vets' : ''}</li>`).join('')}</ul>` : '<p class="dim sm">No decisions from you are on file for this issue yet. The pages start from the desk’s proposal.</p>'}
      ${last && last.chat ? `<h4>Your last word (${core.fmt(last.through)}, by chat)</h4><p class="quote">${E(last.chat)}</p>` : ''}
      ${last && last.changes.length ? `<h4>What the desk changed because of it</h4><ul>${last.changes.map(c => `<li>${E(c)}</li>`).join('')}</ul>` : ''}
      <p class="cal">Block sizes and holes are estimates from the desk’s capacity model${core.build.calibrated ? `, calibrated against the composed issues${cal ? ` (typically within ${E(cal.page_mae)} col-in a page)` : ''}` : ' (not calibrated)'}. The composer balances columns and scales art, so the printed page will not match block for block.
      <br><button class="lnk" id="startover">Start over from the desk’s version</button> (clears what this browser saved for this issue)</p></div>`;
  }
  function deskPane() {
    const f = core.fill();
    const noted = Object.keys(S.slotNotes).filter(k => core.slotBy[k] && S.slotNotes[k].trim());
    return `<h3>To the desk</h3><h4>General notes — copy, cuts, swaps, things to skip</h4><textarea class="sh-in" id="gnotes" rows="5" placeholder="Anything that isn’t about one slot…">${E(S.notes)}</textarea>
      <h4>Filler request</h4><textarea class="sh-in" id="filler" rows="3" placeholder="Ask Clark for filler…">${E(S.filler)}</textarea>
      ${f.status === 'short' ? `<button class="btn" id="askfill">Ask for ≈${f.words.toLocaleString()} words to close the hole</button>` : ''}
      <h4>Slot notes on file (${noted.length})</h4>${noted.map(k => `<div class="need adv" data-go="${E(k)}"><span class="t" style="border-color:var(--accent);color:var(--accent)">NOTE</span><span>${E(core.slotBy[k].slot)}<small>${E(S.slotNotes[k].slice(0, 150))}${S.slotNotes[k].length > 150 ? '…' : ''}</small></span></div>`).join('') || '<p class="dim">None. Open any block to leave one.</p>'}
      <p class="dim sm" style="margin-top:14px">Both boxes are filed in the submission’s <span class="mono">notes</span> field. Slot notes go in <span class="mono">slotNotes</span>.</p>`;
  }
  function slipPane() {
    if (A.sel.type === 'photo') { const id = A.sel.id, on = S.photos[id];
      return `<div class="place"><span class="sh-lbl">On the budget</span><div class="seg" style="display:inline-flex">${[1, 2].map(p => `<button data-ppg="${p}" class="${on && S.photoPage[id] === p ? 'on' : ''}">Page ${p}</button>`).join('')}<button data-ppg="0" class="${on ? '' : 'on'}">Bank</button></div></div>${ui.photoSheet(id)}`; }
    const k = A.sel.id, s = core.slotBy[k], inc = S.inc[k], run = S.order.filter(x => S.inc[x]);
    const bar = s.empty ? '' : `<div class="place"><span class="sh-lbl">On the budget</span><div class="seg" style="display:inline-flex">${[1, 2].map(p => `<button data-pg="${p}" class="${inc && S.page[k] === p ? 'on' : ''}">Page ${p}</button>`).join('')}<button data-pg="0" class="${inc ? '' : 'on'}">Bank</button></div>
      ${inc ? `<button class="btn" data-mv="-1">↑ Earlier</button><button class="btn" data-mv="1">↓ Later</button><span class="dim sm">runs #${run.indexOf(k) + 1} of ${run.length}</span>` : ''}</div>`;
    return bar + ui.sheet(k);
  }
  function renderSide() {
    const blk = NEEDS.filter(n => n.blocking).length;
    const tabs = [['needs', `Needs you (${blk})`], ['read', 'Desk’s read'], ['hist', 'Sections'], ['desk', 'To the desk']];
    const body = A.sel ? slipPane() : A.tab === 'needs' ? needsPane() : A.tab === 'read' ? readPane() : A.tab === 'hist' ? ui.history(true) : deskPane();
    const pane = $('#side .pane'), top = pane ? pane.scrollTop : 0, same = pane && pane.dataset.v === (A.sel ? A.sel.id : A.tab);
    $('#side').innerHTML = `<nav class="tabs">${A.sel ? '<button class="on">Slip</button>' : ''}${tabs.map(([t, l]) => `<button data-tab="${t}" class="${!A.sel && A.tab === t ? 'on' : ''}">${l}</button>`).join('')}<button class="x" data-close aria-label="Close">×</button></nav><div class="pane" data-v="${E(A.sel ? A.sel.id : A.tab)}">${body}</div>`;
    if (same) $('#side .pane').scrollTop = top;
  }
  function render(side = true) { renderTop(); renderPages(); renderBank(); if (side) renderSide(); }
  function select(type, id) { if (type === 'slot' ? !core.slotBy[id] : !core.media[id]) return; A.sel = { type, id }; document.body.classList.add('side-open'); render(); }

  /* ---------- sign-off: where decisions become the submission document ---------- */
  function download(text, name) {
    try { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], { type: 'application/json' })); a.download = name; a.rel = 'noopener';
      document.body.appendChild(a); a.click(); a.remove(); return true; } catch (e) { return false; }
  }
  function execCopy(text) { const t = document.createElement('textarea'); t.value = text; t.style.position = 'fixed'; t.style.opacity = '0'; document.body.appendChild(t); t.select();
    let ok = false; try { ok = document.execCommand('copy'); } catch (e) { ok = false; } t.remove(); return ok; }
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText && window.isSecureContext) return navigator.clipboard.writeText(text).then(() => true, () => execCopy(text));
    return Promise.resolve(execCopy(text));
  }
  function openSign() {
    const doc = core.submission(), blk = NEEDS.filter(n => n.blocking), b = core.build, moved = core.placementNotes();
    $('#modal').innerHTML = `<div class="sheetbox"><div><div class="sh-lbl">Sign off the budget · ${E((core.L.issue || {}).label || 'Issue No. ' + NO)} · ${b.budgetVersion ? 'Budget v' + E(b.budgetVersion) : 'preview build'}</div><h2>${blk.length ? 'Not ready to sign' : 'Ready to sign'}</h2>
      ${blk.length ? `<p style="color:var(--bad)"><b>${blk.length} open item${blk.length > 1 ? 's' : ''}:</b></p>${blk.map(n => `<div class="need" ${n.slot ? `data-go="${E(n.slot)}"` : n.kind === 'photo' ? `data-gop="${E(n.id)}"` : ''}><span class="t">OPEN</span><span>${E(n.text)}</span></div>`).join('')}<p class="dim sm">You can still file; the desk will see these as unanswered.</p>` : '<p class="allclear">✔ Everything on the pages is vetted and answered.</p>'}
      <ul class="sum"><li><b>Runs</b> ${E(core.fmtDate(doc.publishDate))}${doc.publishDateAlt ? ` (alternate ${E(core.fmtDate(doc.publishDateAlt))})` : ' (no alternate)'}</li>
      <li><b>On the pages</b> ${doc.includedSlots.length} — ${doc.includedSlots.map(s => E(String(s.name).split(' — ')[0])).join(', ')}</li>
      <li><b>Left out</b> ${doc.excludedSlots.filter(s => !s.empty).length} + ${doc.excludedSlots.filter(s => s.empty).length} empty</li>
      <li><b>Photos</b> ${doc.photoIncludes.length || 'none'}</li><li><b>New vets</b> ${doc.vets.length || 'none this sitting'}</li>
      <li><b>Answers</b> ${doc.answers.length} · <b style="min-width:0">slot notes</b> ${Object.keys(doc.slotNotes).length}${moved.length ? ` · <b style="min-width:0">page moves</b> ${moved.length}` : ''}</li><li><b>Fill</b> ${E($('#meter .m-txt') ? $('#meter .m-txt').textContent : '')}</li></ul>
      <p class="dim sm">The page positions become <span class="mono">order</span>; a block you put on a page yourself becomes a line in <span class="mono">notes</span>. Nothing leaves this file until you download or copy the document and hand it to the desk.</p>
      <div class="acts"><button class="btn pri" id="dl">Download submission JSON</button><button class="btn" id="cp">Copy</button><button class="btn" data-closem>Back to the budget</button></div><p class="dim sm" id="signmsg" role="status"></p></div>
      <div><div class="sh-lbl">The submission document, exactly as it would be written</div><pre id="json">${E(JSON.stringify(doc, null, 2))}</pre></div></div>`;
    $('#modal').classList.add('open');
    const text = () => JSON.stringify(core.submission(), null, 2) + '\n';
    $('#dl').onclick = () => { const d = core.submission(); $('#signmsg').textContent = download(JSON.stringify(d, null, 2) + '\n', core.submissionName(d)) ? 'Download started: ' + core.submissionName(d) : 'Download blocked — use Copy, or select the text on the right.'; };
    $('#cp').onclick = () => copyText(text()).then(ok => { $('#signmsg').textContent = ok ? 'Copied. Paste it in chat to the desk.' : 'Could not copy automatically — select the text on the right and copy it.'; });
  }

  /* ---------- autosave in this browser (per issue); a newer ingested decision supersedes it ---------- */
  const STORE_KEY = 'gazette-budget-paper:' + NO + ':' + ((core.L.publish || {}).date || '');
  let store = null, saveT = 0;
  try { const k = '__gazette_probe__'; window.localStorage.setItem(k, '1'); window.localStorage.removeItem(k); store = window.localStorage; } catch (e) { store = null; }
  function save() { if (!store) return; clearTimeout(saveT); saveT = setTimeout(() => { try { store.setItem(STORE_KEY, JSON.stringify(core.serialize())); } catch (e) { /* full or blocked: the page still works */ } }, 250); }
  function notice(html) { const n = $('#notice'); n.hidden = !html; n.innerHTML = html || ''; }
  (function restoreSaved() {
    if (!store) return;
    let saved = null; try { saved = JSON.parse(store.getItem(STORE_KEY) || 'null'); } catch (e) { saved = null; }
    const r = core.restore(saved);
    if (r.superseded) notice('<span>Your earlier unsent work in this browser was replaced by the decisions the desk has since ingested.</span><button class="lnk" data-dismiss>OK</button>');
    else if (r.restored) notice(`<span>Picked up where you left off in this browser (saved ${E(core.fmt(saved.savedAt))})${r.dataChanged ? '. This is a newer build' + (r.dropped ? `; ${r.dropped} saved thing${r.dropped > 1 ? 's' : ''} no longer apply` : '') : ''}.</span><span><button class="lnk" id="startover2">Start over</button> · <button class="lnk" data-dismiss>OK</button></span>`);
  })();
  function startOver() { if (store) { try { store.removeItem(STORE_KEY); } catch (e) { /* ignore */ } } clearTimeout(saveT); core.on(() => clearTimeout(saveT)); location.reload(); }

  /* ---------- events ---------- */
  core.on(why => { render(!ui.TEXTY.includes(why)); save(); });
  ui.bind($('#side'));
  window.addEventListener('resize', renderPages);
  document.addEventListener('click', e => {
    const t = e.target, c = q => t.closest(q);
    if (c('[data-closem]') || t === $('#modal')) return $('#modal').classList.remove('open');
    if (c('[data-dismiss]')) return notice('');
    if (c('#startover') || c('#startover2')) return startOver();
    if (c('#sign')) return openSign();
    if (c('#needbtn')) { A.sel = null; A.tab = 'needs'; document.body.classList.add('side-open'); return render(); }
    if (c('[data-close]')) { if (A.sel && innerWidth > 900) A.sel = null; document.body.classList.remove('side-open'); return render(); }
    if (c('[data-tab]')) { A.sel = null; A.tab = c('[data-tab]').dataset.tab; document.body.classList.add('side-open'); return render(); }
    if (c('[data-add]')) { const st = c('.strip'), p = +c('[data-add]').dataset.add;
      return st.dataset.photo ? core.act.photo(st.dataset.photo, true, p) : core.act.place(st.dataset.slot, p); }
    if (c('[data-pg]')) { const p = +c('[data-pg]').dataset.pg, k = A.sel.id; return p ? core.act.place(k, p) : core.act.include(k, false); }
    if (c('[data-ppg]')) { const p = +c('[data-ppg]').dataset.ppg; return core.act.photo(A.sel.id, !!p, p); }
    if (c('[data-mv]')) return core.act.move(A.sel.id, +c('[data-mv]').dataset.mv);
    if (c('[data-date]')) { $('#modal').classList.remove('open'); $('#rund').open = true; return $('#rund').scrollIntoView({ block: 'nearest' }); }
    if (c('[data-go]') && c('[data-go]').dataset.go) { $('#modal').classList.remove('open'); return select('slot', c('[data-go]').dataset.go); }
    if (c('[data-gop]')) { $('#modal').classList.remove('open'); return select('photo', c('[data-gop]').dataset.gop); }
    if (c('#dswap')) { const a = S.altDate; if (!a) return; S.altDate = S.publishDate; core.act.date(a); return renderDatePop(); }
    if (c('#askfill')) { const f = core.fill(); core.act.filler(`Need about ${f.words} words of filler: ${core.r1(f.gap)} col-in are open under the current includes.`); return renderSide(); }
    const hit = c('.blk,.strip,.overset span');
    if (hit && !c('.sheet')) return hit.dataset.photo ? select('photo', hit.dataset.photo) : select('slot', hit.dataset.slot);
    if (c('.cols') && A.sel) { A.sel = null; render(); }
  });
  document.addEventListener('input', e => {
    const t = e.target;
    if (t.id === 'gnotes') core.act.notes(t.value); else if (t.id === 'filler') core.act.filler(t.value);
    else if (t.id === 'dmain') core.act.date(t.value); else if (t.id === 'dalt') core.act.alt(t.value);
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') { $('#modal').classList.remove('open'); if (A.sel) { A.sel = null; render(); } }
    if (e.key === 'Enter' && e.target.matches && e.target.matches('.blk,.strip')) e.target.click();
  });
  // drag (desktop): bank <-> pages, page <-> page, and a block onto another block to run ahead of it
  document.addEventListener('dragstart', e => { const b = e.target.closest && e.target.closest('[draggable]'); if (!b) return;
    e.dataTransfer.setData('text/plain', b.dataset.photo ? 'p:' + b.dataset.photo : 's:' + b.dataset.slot); e.dataTransfer.effectAllowed = 'move'; });
  document.addEventListener('dragover', e => { const z = e.target.closest && e.target.closest('.cols,.bank'); if (z) { e.preventDefault(); z.classList.add('drop'); } });
  document.addEventListener('dragleave', e => { const z = e.target.closest && e.target.closest('.cols,.bank'); if (z && !z.contains(e.relatedTarget)) z.classList.remove('drop'); });
  document.addEventListener('drop', e => {
    const z = e.target.closest && e.target.closest('.cols,.bank'); if (!z) return; e.preventDefault(); z.classList.remove('drop');
    const raw = e.dataTransfer.getData('text/plain'), type = raw.slice(0, 1), id = raw.slice(2); if (!id || (type !== 'p' && type !== 's')) return;
    const p = +z.dataset.page || 0;
    if (type === 'p') return core.act.photo(id, !!p, p);
    if (!p) return core.act.include(id, false);
    const over = e.target.closest('.blk[data-slot]');
    if (over && over.dataset.slot !== id) core.act.before(id, over.dataset.slot);
    core.act.place(id, p);
  });
  renderDatePop(); render();
  window.BudgetPage = { core, payload: () => core.submission(), storeKey: () => STORE_KEY, select };
})();
