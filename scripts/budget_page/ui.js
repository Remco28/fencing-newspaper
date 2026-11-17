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
      else if (x.vetted) body = `<div class="vet ok">✔ Vetted by ${esc(x.vetted_by || 'a standing rule')}${x.vetted_at ? ' · ' + fmt(x.vetted_at) : ''}${x.vet_scope ? ` <span class="dim">· scope: ${esc(x.vet_scope.replace(/_/g, ' '))}</span>` : ''}${x.facts_status ? ` <span class="dim">· facts: ${esc(x.facts_status)}</span>` : ''}</div>`;
      else body = `<div class="vet bad"><b>UNVETTED</b> — not approved for print.</div>${note}<button class="btn pri" data-act="vet" data-id="${esc(id)}">Vet for print</button>`;
      return `<div class="sh-vet"><div class="sh-lbl">${esc(label)}</div>${body}</div>`;
    }
    function staleLine(it) {
      const st = core.staleness(it); if (!st) return '';
      const bits = [`Clark’s stale mark: <b>${st.desk ? 'STALE' : 'none'}</b>`, `last touched ${fmt(st.last)}${st.days ? ` (${st.days} day${st.days > 1 ? 's' : ''} before this build)` : ''}`];
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
        (it.vet_notes ? `<details><summary>Clark’s vet log</summary><p class="pre">${esc(it.vet_notes)}</p></details>` : '') + '</div>';
    }
    function historyLine(key) {
      const rows = core.sectionsOfSlot(key), R = core.sectionRows(); if (!R || !rows.length) return '';
      return rows.map(r => `<div class="sh-hist"><div class="sh-lbl">Section history — ${esc(r.name)}${r.official ? '' : ' <span class="tag">not in official list</span>'}</div>
        <span class="dots">${R.issues.map(i => `<i class="${r.ran.includes(i.number) ? 'on' : ''}" title="No. ${i.number} (${esc(i.date)})${r.evidence[i.number] ? ': ' + esc(r.evidence[i.number].join('; ')) : ': did not run'}">${i.number}</i>`).join('')}<i class="now ${r.status}" title="This budget">${esc(core.issueNo)}</i></span>
        <span class="dim">${r.ran.length ? `last ran No. ${r.last}` : 'has never run'} · ${esc(String(r.frequency).replace(/_/g, ' '))}</span></div>`).join('');
    }

    // Manual art: the picture keeps its shape inside its frame. Notes, never refusals.
    function manualArtHTML(id) {
      const e = core.isManual() && state.manualLayout[id]; if (!e) return '';
      const f = core.artFit(id, e.span, e.heightIn), notes = [];
      if (f.scaled) notes.push(`scaled to fit the frame (${r1(f.w)} of ${r1(f.frameW)} in wide); Clark sets text or a gutter beside it`);
      if (f.slack > 0.05) notes.push(`${r1(f.slack)} in spare below the picture`);
      if (f.h > 4.5) notes.push('taller than the 4.5 in cap compose uses; Clark will raise it with you');
      else if (f.h > 2.2 && isLoosePhoto(id)) notes.push('taller than the 2.2 in photo guide; fine, Clark notes it');
      return `<div class="sh-fit"><div class="sh-lbl">Size in Manual</div>
        <div class="seg"><button data-act="art" data-v="smaller">Smaller</button><button data-act="art" data-v="bigger">Bigger</button><button data-act="art" data-v="natural">Natural size</button></div>
        <span class="dim">Picture ${r1(f.w)} × ${r1(f.h)} in, in a ${e.span}-column frame ${r1(e.heightIn)} in deep (${r1(e.heightIn * e.span)} col-in). Never cropped.${notes.length ? ' ' + esc(notes.join('; ')) + '.' : ''} Drag the block’s right edge for columns, its bottom edge for size.</span></div>`;
    }
    const isLoosePhoto = id => !!core.photoMeta[id];
    function layoutResizeHTML(s, photoId) {
      const bits = [];
      if (photoId) {
        const sp = core.photoSpanOf(photoId), sz = core.photoSize(photoId), lay = core.photoLayoutOf(photoId);
        bits.push(`<div class="sh-fit"><div class="sh-lbl">Size on the page</div>
          <div class="seg">${[1,2,3].map(n => `<button data-act="span" data-v="${n}" class="${sp === n ? 'on' : ''}">${n} col</button>`).join('')}</div>
          <div class="seg"><button data-act="lay" data-v="wide" class="${lay === 'wide' ? 'on' : ''}">Wide</button><button data-act="lay" data-v="tall" class="${lay === 'tall' ? 'on' : ''}">Tall</button></div>
          <span class="dim">${r1(sz.widthIn)} × ${r1(sz.heightIn)} in · ${r1(core.liveCostOfPhoto(photoId))} col-in</span></div>`);
        bits.push(manualArtHTML(photoId));
        return bits.join('');
      }
      const kind = (s.cost || {}).type, fig = kind === 'figure';
      if (core.canSwitchLayout(s) || fig) {
        const lay = core.currentLayout(s), sp = core.spanOf(s), sz = core.slotSize(s);
        bits.push(`<div class="sh-fit"><div class="sh-lbl">${fig ? 'Size and layout' : 'Layout'}</div>
          ${fig || core.canSwitchLayout(s) ? `<div class="seg"><button data-act="lay" data-v="wide" class="${lay === 'wide' ? 'on' : ''}">Wide</button><button data-act="lay" data-v="tall" class="${lay === 'tall' ? 'on' : ''}">Tall</button></div>` : ''}
          ${fig ? `<div class="seg">${[1,2,3].map(n => `<button data-act="span" data-v="${n}" class="${sp === n ? 'on' : ''}">${n} col</button>`).join('')}</div>
            <span class="dim">${r1(sz.widthIn)} × ${r1(sz.heightIn)} in</span>` : `<span class="dim">${sp} col wide · ${r1(sz.heightIn)} in deep</span>`}</div>`);
      }
      if (fig) bits.push(manualArtHTML(s.key));
      if (kind === 'prose' || kind === 'qa' || kind === 'table' || kind === 'table_rows') {
        const rz = state.resize[s.key], cur = rz && rz.target ? rz.target : '';
        bits.push(`<div class="sh-fit"><div class="sh-lbl">Ask Clark to grow or shrink this</div>
          <div class="seg"><button data-act="rz" data-v="expand" class="${rz && rz.direction === 'expand' ? 'on' : ''}">Expand</button><button data-act="rz" data-v="shrink" class="${rz && rz.direction === 'shrink' ? 'on' : ''}">Shrink</button>${rz ? '<button data-act="rz" data-v="clear">Clear</button>' : ''}</div>
          <input class="sh-in" data-rztarget placeholder="e.g. 800, 80%, 3.5 col-in" value="${esc(cur)}">
          ${rz ? `<span class="dim">${rz.direction} to ${rz.toWords != null ? rz.toWords + 'w' : esc(rz.target)}${rz.toColIn != null ? ' · ' + r1(rz.toColIn) + ' col-in' : ''} (from ${rz.fromWords}w). This goes out in the submission as resize, for Clark to rewrite to length.</span>` : '<span class="dim">A target in words, a percent, or column-inches. Live fill and overset follow the estimate; Clark rewrites after checking the proof by eye.</span>'}</div>`);
      }
      return bits.join('');
    }
    function sheet(key) {
      const s = slotBy[key], it = core.itemOf(s), all = core.allItemsOf(s), m = core.mediaOfSlot(s), inc = state.inc[key];
      const qs = core.questionsOf(s), flags = core.flagsOf(s), c = s.cost;
      const costTxt = c ? `${r1(core.liveCostOfSlot(s))} col-in${c.type !== 'table' && c.type !== 'table_rows' && core.wordsOf(s) ? ` · ~${core.wordsOf(s)}w` : ''}${c.rows ? ` · ${c.rows} rows` : ''} · ${core.spanOf(s)} col wide` : '';
      return `<div class="sheet" data-slot="${esc(key)}">
        <div class="sh-k">${esc(s.slot)}</div>
        <h2 class="sh-h">${esc(s.title || (it && it.headline) || shortName(s))}</h2>
        ${s.item && !it ? `<div class="sh-now">The lineup names item <span class="mono">${esc(s.item)}</span>, which is not in staging. Nothing to vet or read yet.</div>` : ''}
        ${it && s.title && it.headline && it.headline !== s.title ? `<div class="sh-now">Draft headline now: <b>${esc(it.headline)}</b></div>` : ''}
        ${s.empty ? `<div class="sh-empty">EMPTY SLOT — nothing to run. ${esc(s.why || '')}</div>` :
          `<div class="sh-row"><div class="seg"><button data-act="inc" data-v="1" class="${inc ? 'on' : ''}" ${core.canPlace(s) ? '' : 'disabled title="Vet this on the slip first"'}>In the issue</button><button data-act="inc" data-v="0" class="${inc ? '' : 'on'}">Left out</button></div>
           <span class="dim">${costTxt} · Clark ${s.proposed ? 'proposed it' : 'did not propose it'}${s.budget ? ' · budget: ' + esc(s.budget) : ''}${core.canPlace(s) ? '' : ' · <b style="color:var(--bad)">vet it before it can run</b>'}</span></div>`}
        ${s.summary ? `<p class="sh-sum">${esc(s.summary)}</p>` : ''}
          ${qs.map(q => `<div class="sh-q ${q.answer.trim() ? 'done' : ''}"><div class="sh-lbl">Clark’s question</div><p>${esc(q.q)}</p><textarea class="sh-in" data-q="${q.i}" rows="2" placeholder="Your answer…">${esc(q.answer)}</textarea></div>`).join('')}
        ${m ? `<img class="sh-img" src="${core.thumb(m.filename)}" alt="">` : ''}
        ${all.map(x => vetBlock(x.id, all.length > 1 ? 'Vet — ' + x.headline : 'Vet the facts')).join('')}
        ${m && m.id ? vetBlock(m.id, 'Vet the photo — ' + m.filename) + (m.note ? `<p class="dim sm">${esc(m.note)}${m.license ? ' · ' + esc(m.license) : ''}</p>` : '') : ''}
        ${flags.length ? `<ul class="sh-flags">${flags.map(f => `<li class="${f.level} ${f.cleared ? 'cleared' : ''}"><span>${esc(f.text)}</span>${f.cleared ? ' <em>cleared — vetted since Clark wrote this</em>' : ''}</li>`).join('')}</ul>` : ''}
        ${it ? staleLine(it) : ''}
        ${it && (it.body || s.table) ? `<details class="sh-body"><summary>${s.table ? 'The table as it would print' : `The draft${it.word_count ? ` (${it.word_count}w)` : ''}`}</summary>${tableHTML(s.table)}${it.body ? `<p>${esc(it.body)}</p>` : ''}${Array.isArray(it.held_rows) && it.held_rows.length ? `<p class="dim">Held rows: ${it.held_rows.map(r => esc([].concat(r).join(' · '))).join('; ')}</p>` : ''}</details>` : ''}
        ${all.map(sourcesHTML).join('')}
        <div class="sh-note"><div class="sh-lbl">Slot note to Clark</div><textarea class="sh-in" data-slotnote rows="3" placeholder="Anything about this slot: cuts, swaps, standing rules…">${esc(state.slotNotes[key] || '')}</textarea></div>
        ${!s.empty ? layoutResizeHTML(s, null) : ''}
        ${historyLine(key)}</div>`;
    }
    function photoSheet(id) {
      const m = media[id], p = core.photoMeta[id] || {}, on = state.photos[id];
      return `<div class="sheet" data-photo="${esc(id)}"><div class="sh-k">Photo — ${esc(m.kind)}</div><h2 class="sh-h">${esc(m.filename)}</h2>
        <img class="sh-img" src="${core.thumb(m.filename)}" alt="">
        <div class="sh-row"><div class="seg"><button data-act="photo" data-v="1" class="${on ? 'on' : ''}" ${core.canPlacePhoto(id) ? '' : 'disabled title="Vet this photo on the slip first"'}>Run it</button><button data-act="photo" data-v="0" class="${on ? '' : 'on'}">Leave out</button></div>
        <span class="dim">${r1(core.liveCostOfPhoto(id))} col-in · ${core.photoSpanOf(id)} col wide · Clark ${p.proposed ? 'proposed it' : 'did not propose it'}${core.canPlacePhoto(id) ? '' : ' · <b style="color:var(--bad)">vet it before it can run</b>'}</span></div>
        <p class="sh-sum">${esc(p.note || '')}</p>${m.caption ? `<p><span class="sh-lbl">Caption on file</span> ${esc(m.caption)}</p>` : ''}
        ${vetBlock(id, 'Vet the photo')}
        ${layoutResizeHTML(null, id)}
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
        else if (a === 'lay') core.act.setLayout(key || sh.dataset.photo, b.dataset.v);
        else if (a === 'span') core.act.setSpan(key || sh.dataset.photo, +b.dataset.v);
        else if (a === 'art') core.act.artSize(key || sh.dataset.photo, b.dataset.v);
        else if (a === 'rz') {
          // Buttons step or clear on their own. A leftover value in the target field must not
          // hijack Expand / Shrink (that made a second click, or Clear then Expand, feel like a no-op).
          if (b.dataset.v === 'clear') core.act.setResize(key, null);
          else core.act.setResize(key, b.dataset.v, '');
        }
      });
      el.addEventListener('input', e => {
        const t = e.target, sh = t.closest('.sheet'); if (!sh) return; const key = sh.dataset.slot;
        if (t.dataset.q != null) { core.act.answer(key, +t.dataset.q, t.value); t.closest('.sh-q').classList.toggle('done', !!t.value.trim()); }
        else if ('slotnote' in t.dataset) core.act.slotNote(key, t.value);
        else if (t.dataset.vetnote && t.dataset.vetnote in state.vets) { state.vets[t.dataset.vetnote] = t.value; core.emit('text'); }
        else if ('rztarget' in t.dataset && key) {
          const dir = (state.resize[key] && state.resize[key].direction) || (t.value.trim() ? 'expand' : null);
          if (!t.value.trim()) core.act.setResize(key, null, null, 'resize-text');
          else core.act.setResize(key, dir, t.value, 'resize-text');
        }
      });
    }
    const TEXTY = ['answer', 'note', 'notes', 'text', 'resize-text']; // typing a target must not rebuild the focused form; Expand/Shrink/Clear do re-render the slip
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
      return `<div class="meter ${f.status}" title="Estimate from Clark’s capacity model (calibrated against the composed issues): prose words ÷ ${core.cap.wpi} per col-in (${core.cap.wpi_feature} for the lead), plus heads, table rows and art. Two pages hold ${r1(f.total)} col-in ≈ ${f.capWords.toLocaleString()} words; Clark aims to oversupply ×${core.cap.oversupply}.">
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
    if (n.some(x => x.kind === 'question')) m += '<i class="mk q" title="Clark asked you something here">?</i>';
    if (n.some(x => x.kind === 'changed')) m += '<i class="mk chg" title="Draft changed after your vet">Δ</i>';
    if ((S.slotNotes[key] || '').trim()) m += '<i class="mk note" title="You left a slot note">✎</i>';
    if (it && core.staleness(it).old) m += `<i class="mk age" title="Last touched ${core.staleness(it).days} days before this build — may be out of date">${core.staleness(it).days}d</i>`;
    if (!m && it && core.allItemsOf(s).every(i => core.isVetted(i.id))) m = '<i class="mk ok" title="Vetted">✓</i>';
    return `<span class="marks">${m}</span>`;
  }
  const isSel = (t, id) => (A.sel && A.sel.type === t && A.sel.id === id ? ' sel' : '');

  function hangHTML(b, ppi, pageH) {
    if (!b.spill && !(b.hang > 0.02)) return '';
    if (b.y >= pageH - 0.01) return ''; // whole block is in the well (styled .spill)
    const top = Math.max(0, (pageH - b.y) * ppi);
    return `<i class="hang" style="top:${top}px"></i>`;
  }
  function handlesHTML(b) {
    if (b.part > 1) return '';
    const fig = b.type === 'photo' || b.kind === 'figure' || (b.type === 'slot' && ((core.slotBy[b.id] || {}).cost || {}).type === 'figure');
    const s = b.type === 'slot' ? core.slotBy[b.id] : null;
    let h = '';
    if (core.isManual()) {
      h += `<i class="handle wid" data-handle="width" title="${fig ? 'Drag for columns (1, 2 or 3); the picture keeps its shape' : 'Drag for columns (1, 2 or 3); the same words re-flow'}"></i>`;
      h += `<i class="handle len" data-handle="length" title="${fig ? 'Drag to size the picture (0.05 in steps); never cropped' : 'Drag to set the depth; Clark is asked for the length that fills it'}"></i>`;
    } else if (fig) h += '<i class="handle se" data-handle="scale" title="Drag to size (keeps aspect, snaps to 1 / 2 / 3 columns)"></i>';
    else if (s && s.cost && (s.cost.type === 'prose' || s.cost.type === 'qa' || s.cost.type === 'table' || s.cost.type === 'table_rows'))
      h += '<i class="handle len" data-handle="length" title="Drag to grow or shrink the estimated length"></i>';
    if (s && core.canSwitchLayout(s)) {
      const lay = core.currentLayout(s);
      h += `<button type="button" class="lay-tog" data-lay="${lay === 'wide' ? 'tall' : 'wide'}" title="Switch to ${lay === 'wide' ? 'tall (1 column)' : 'wide'}">${lay === 'wide' ? 'Wide' : 'Tall'}</button>`;
    } else if (b.type === 'photo') {
      const lay = core.photoLayoutOf(b.id);
      h += `<button type="button" class="lay-tog" data-play="${lay === 'wide' ? 'tall' : 'wide'}" title="Switch to ${lay === 'wide' ? 'tall (1 column)' : 'wide'}">${lay === 'wide' ? 'Wide' : 'Tall'}</button>`;
    }
    if (fig) {
      const sz = b.type === 'photo' ? core.photoSize(b.id) : core.slotSize(core.slotBy[b.id]);
      h += `<span class="size-lab">${core.r1(sz.widthIn)} × ${core.r1(sz.heightIn)} in</span>`;
    } else if (s && S.resize[s.key]) {
      const rz = S.resize[s.key];
      h += `<span class="size-lab">${rz.direction} ${rz.toWords != null ? rz.toWords + 'w' : ''}</span>`;
    }
    return h;
  }
  // A picture never starts the browser's own drag (that used to cancel a Manual move a few pixels in).
  // In Manual it is drawn at the size it prints inside its frame: scaled to fit, never cropped.
  function picHTML(id, src, b, ppi) {
    const f = core.isManual() && core.isArtId(id) ? core.artFit(id, b.span, b.h) : null;
    return `<img draggable="false" src="${src}" alt=""${f ? ` class="fit" style="width:${f.w * ppi}px;height:${f.h * ppi}px"` : ''}>`;
  }
  function blockHTML(b, ppi, pageH) {
    const pos = `left:${colX(b.col) * ppi}px;top:${b.y * ppi}px;width:${spanW(b.span) * ppi}px;height:${Math.max(6, b.h * ppi - 3)}px`;
    const spillC = (b.spill || b.hang > 0.02) ? ' spill' : '';
    const overC = (b.overlap ? ' overlap' : '') + (core.isManual() && A.lift === b.id ? ' lifted' : '');
    const dragAttr = (!core.isManual() && ((b.type === 'photo' && core.canPlacePhoto(b.id)) || (b.type !== 'photo' && core.canPlace(core.slotBy[b.id])))) ? 'draggable="true"' : '';
    if (b.type === 'photo') {
      const m = core.media[b.id];
      return `<div class="blk t-photo${isSel('photo', b.id)}${core.canPlacePhoto(b.id) ? '' : ' locked'}${spillC}${overC}" ${dragAttr} tabindex="0" data-photo="${E(b.id)}" style="${pos}"><span class="marks">${core.isVetted(b.id) ? '<i class="mk ok">✓</i>' : '<i class="mk vet">VET</i>'}</span>${picHTML(b.id, core.thumb(m.filename), b, ppi)}<div class="k">Photo · ${E(m.kind)}</div>${hangHTML(b, ppi, pageH)}${handlesHTML(b)}</div>`;
    }
    const s = core.slotBy[b.id], c = s.cost || {}, head = core.headlineOf(s), cont = b.part > 1;
    let inner = `<div class="k">${E(ui.shortName(s))}</div>`;
    if (cont) inner += `<div class="cont-l">continued</div><div class="greek"></div>`;
    else if (c.type === 'figure') inner += picHTML(b.id, core.thumb(s.thumb), b, ppi) + (c.head ? `<div class="h">${E(head)}</div><div class="greek" style="flex:1.3"></div>` : '');
    else if (s.table && Array.isArray(s.table.rows)) inner += (s.title ? `<div class="h">${E(head)}</div>` : '') + s.table.rows.map(r => `<div class="tr" style="height:${rowIn(c) * ppi}px;line-height:${rowIn(c) * ppi}px;font-size:${Math.min(9, rowIn(c) * ppi * .8)}px"><b>${E(r[0])}</b> · ${E(r.slice(1).join(' · '))}</div>`).join('');
    else inner += `<div class="h">${E(head)}</div><div class="greek"></div>`;
    return `<div class="blk t-${E(c.type || 'prose')}${c.feature ? ' lead' : ''}${b.span >= 2 ? ' wide' : ''}${cont ? ' cont' : ''}${isSel('slot', b.id)}${core.canPlace(s) ? '' : ' locked'}${spillC}${overC}" ${dragAttr} tabindex="0" data-slot="${E(b.id)}" style="${pos}">${cont ? '' : marks(b.id)}${inner}${hangHTML(b, ppi, pageH)}${handlesHTML(b)}</div>`;
  }

  function renderPages() {
    const host = $('#pages');
    if (!host.children.length) host.innerHTML = [1, 2].map(p => `<div class="page" data-page="${p}">${FURN[p].map(([c]) => `<div class="furn ${c}" data-f="${c}"></div>`).join('')}<div class="cols" data-page="${p}"></div><div class="pfoot"></div><div class="overset"></div></div>`).join('');
    [1, 2].forEach(p => {
      const pg = host.querySelector(`.page[data-page="${p}"]`), cols = pg.querySelector('.cols'), ppi = cols.clientWidth / PW, r = core.pack(p);
      FURN[p].forEach(([c, inch]) => { const f = pg.querySelector(`[data-f="${c}"]`); f.style.height = inch * ppi + 'px';
        f.innerHTML = c === 'mast' ? 'En Garde Gazette' : `<span>${E((core.L.issue || {}).label || 'Issue No. ' + NO)}</span><span>${E(core.fmtDate(S.publishDate))}</span><span>Page ${p}</span>`; });
      const spill = r.spillIn || 0;
      cols.dataset.ppi = ppi;
      cols.style.height = (r.H + spill) * ppi + 'px';
      pg.classList.toggle('overseting', spill > 0.02);
      const holes = r.holes.filter(x => x.h > 0.3).map(x => `<div class="hole${x.trapped ? ' trap' : ''}" style="left:${colX(x.col) * ppi}px;width:${spanW(x.cols) * ppi}px;top:${x.y * ppi + 2}px;height:${x.h * ppi - 2}px">${
        x.h > 0.7 ? `OPEN<br>${core.r1(x.colIn)} col-in<br>≈ ${x.words}w` : x.h * ppi > 13 ? `${core.r1(x.colIn)} col-in` : ''}</div>`).join('');
      const trim = `<div class="trim" style="top:${r.H * ppi}px"><span>trim</span></div>`;
      const well = spill > 0.02 ? `<div class="spillwell" style="top:${r.H * ppi}px;height:${spill * ppi}px"></div>` : '';
      cols.innerHTML = well + r.placed.map(b => blockHTML(b, ppi, r.H)).join('') + holes + trim;
      const overTxt = r.overset > 0.02
        ? `OVERSET by ${core.r1(r.overset)} col-in ≈ ${r.oversetWords || Math.round(r.overset * cap.wpi)} words · hangs ${core.r1(spill)} in below the trim`
        : `open ${core.r1(r.open)} col-in ≈ ${Math.round(r.open * cap.wpi)} words`;
      pg.querySelector('.pfoot').innerHTML = `<span>PAGE ${p} · ${core.r1(r.placedUsed)} of ${core.r1(r.cap)} col-in on the page</span><span class="${r.open > 0.5 || r.overset > 0.02 ? 'short' : ''}">${overTxt}</span>`;
      const overlapTxt = (r.overlaps && r.overlaps.length) ? ` · ${r.overlaps.length} overlap${r.overlaps.length > 1 ? 's' : ''}` : '';
      pg.querySelector('.pfoot').innerHTML = `<span>PAGE ${p} · ${core.r1(r.placedUsed)} of ${core.r1(r.cap)} col-in on the page</span><span class="${r.open > 0.5 || r.overset > 0.02 || (r.overlaps && r.overlaps.length) ? 'short' : ''}">${overTxt}${overlapTxt}</span>`;
      pg.querySelector('.overset').innerHTML = r.over.length ? 'Hanging below the trim: ' + r.over.map(b => `<span data-${b.type}="${E(b.id)}">${E(b.type === 'slot' ? ui.shortName(core.slotBy[b.id]) : core.media[b.id].filename)} · ${core.r1(b.hang || 0)} in hang · ${core.r1(b.cost)} col-in</span>`).join('') : '';
    });
    renderOverlap();
  }
  // In Manual this line always keeps its one-line slot, overlaps or not: if it came and went it would push the
  // pages up and down under the pointer (that made same-page drags land in the wrong place).
  function renderOverlap() {
    const el = $('#overlap'); if (!el) return;
    if (!core.isManual()) { el.hidden = true; el.textContent = ''; el.title = ''; return; }
    const ov = core.allOverlaps();
    const name = rec => rec.type === 'photo' ? ((core.media[rec.id] || {}).filename || rec.id) : ui.shortName(core.slotBy[rec.id] || { slot: rec.id });
    el.hidden = false;
    el.classList.toggle('calm', !ov.length);
    el.textContent = ov.length
      ? 'Overlap: ' + ov.map(o => name(o.a) + ' and ' + name(o.b)).join('; ') + '. Move a block so they do not sit on top of each other.'
      : 'Manual placement: blocks stay where you put them. No overlaps.';
    el.title = el.textContent;
  }

  function stripHTML(s) {
    const it = core.itemOf(s), k = s.key;
    if (s.empty) return `<div class="strip ghost${isSel('slot', k)}" tabindex="0" data-slot="${E(k)}">${marks(k)}<div class="k">Empty slot</div><div class="h">${E(s.slot)}</div><div class="w">${E(s.why || '')}</div></div>`;
    const who = (k in (dec.slotNotes || {})) || (dec.excluded || []).includes(k) ? 'You left it out' : s.auto ? 'Not slotted by Clark' : s.waiting ? 'Clark is waiting on it' : s.proposed ? 'Pulled' : 'Clark did not propose it';
    const unvet = !core.canPlace(s), drag = !unvet && !core.isManual(); // Manual drags strips with the pointer, not the browser
    return `<div class="strip${s.item && !it ? ' missing' : ''}${isSel('slot', k)}${unvet ? ' locked' : ''}" ${drag ? 'draggable="true"' : ''} tabindex="0" data-slot="${E(k)}">${marks(k)}${s.thumb ? `<img draggable="false" src="${core.thumb(s.thumb)}" alt="">` : ''}<div class="k">${E(ui.shortName(s))}</div>
      <div class="h">${E(core.headlineOf(s) || s.slot)}</div><div class="w">${who} · ${core.r1(core.costOf(s))} col-in${unvet ? ' · <b style="color:var(--bad)">unvetted — vet on the slip to run it</b>' : ''}${s.item && !it ? ' · <b style="color:var(--bad)">not in staging</b>' : ''}</div>
      <div class="add">run on <button data-add="1" ${unvet ? 'disabled title="Vet this on the slip first"' : ''}>p.1</button><button data-add="2" ${unvet ? 'disabled title="Vet this on the slip first"' : ''}>p.2</button></div></div>`;
  }
  function renderBank() {
    const out = S.order.map(k => core.slotBy[k]).filter(s => s && !S.inc[s.key]);
    const photos = core.loosePhotos.filter(id => !S.photos[id]);
    const np = (core.L.not_proposed || []).concat((core.L.held || []).map(h => ({ item: h.id || h.item, why: h.why || h.note || 'Held.' })));
    const empties = core.slots.filter(s => s.empty);
    $('#bank').innerHTML = `<h3>The bank — not running (${out.length})</h3>${out.map(stripHTML).join('') || '<p class="np">Everything is on the pages.</p>'}
      ${core.loosePhotos.length ? `<h3>Loose art (${photos.length})</h3>${photos.map(id => { const m = core.media[id], ok = core.canPlacePhoto(id); return `<div class="strip${isSel('photo', id)}${ok ? '' : ' locked'}" ${ok && !core.isManual() ? 'draggable="true"' : ''} tabindex="0" data-photo="${E(id)}"><img draggable="false" src="${core.thumb(m.filename)}" alt=""><div class="k">${E(m.kind)}</div><div class="h">${E(String(m.filename).replace(/\.\w+$/, ''))}</div><div class="w">${core.r1(core.photoCost(id))} col-in · ${ok ? 'vetted' : '<b style="color:var(--bad)">unvetted — vet on the slip to run it</b>'}</div><div class="add">run on <button data-add="1" ${ok ? '' : 'disabled title="Vet this photo on the slip first"'}>p.1</button><button data-add="2" ${ok ? '' : 'disabled title="Vet this photo on the slip first"'}>p.2</button></div></div>`; }).join('') || '<p class="np">All of it is on the pages.</p>'}` : ''}
      ${empties.length ? `<h3>Empty slots</h3>${empties.map(stripHTML).join('')}` : ''}
      ${np.length ? `<h3>Staged, not in the lineup</h3>${np.map(n => `<p class="np"><b>${E((core.items[n.item] || {}).headline || n.item)}</b>${E(n.why || '')}</p>`).join('')}` : ''}`;
  }

  function renderTop() {
    NEEDS = core.needs();
    const blk = NEEDS.filter(n => n.blocking).length, adv = NEEDS.length - blk, b = core.build;
    $('#iss').textContent = (core.L.issue || {}).label || 'Issue No. ' + NO;
    $('#stamp').innerHTML = `BUDGET VERSION 2<small>${E(String(b.versionLabel || '').split(' · ').slice(1).join(' · ') || '')}</small>`;
    document.body.classList.toggle('manual', core.isManual());
    const mb = $('#modebox');
    if (mb) mb.innerHTML = `<span class="mlab">Placement</span><div class="seg"><button type="button" data-mode="auto" class="${core.isManual() ? '' : 'on'}">Auto</button><button type="button" data-mode="manual" class="${core.isManual() ? 'on' : ''}">Manual</button></div><button type="button" class="aux" id="undoplace" ${core.canUndo() ? '' : 'disabled'}>Undo</button>${core.isManual() ? '<button type="button" class="aux warn" id="toauto">Back to Auto</button>' : ''}`;
    $('#rd').textContent = core.fmtDate(S.publishDate); $('#ad').textContent = S.altDate ? 'alt ' + core.fmtDate(S.altDate) : 'no alternate';
    $('#meter').innerHTML = ui.meter();
    const nb = $('#needbtn'); nb.className = 'needbtn' + (blk ? '' : ' clear');
    nb.textContent = blk ? `${blk} need${blk > 1 ? '' : 's'} you` : adv ? `Nothing blocking · ${adv} to check` : 'All clear';
  }
  function renderDatePop() {
    const pub = core.L.publish || {};
    $('#rpop').innerHTML = `${pub.why ? `<div class="sh-lbl">Clark picked ${E(pub.label || core.fmtDate(pub.date))} because</div><p class="why">${E(pub.why)}</p>` : ''}
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
    return `<h3>Before the budget can be signed off</h3>${blk.length ? blk.map(li).join('') : '<p class="allclear">✔ Nothing is blocking. Every block on the pages is vetted and every question from Clark has an answer.</p>'}
      <h3>Worth a look</h3>${adv.length ? adv.map(li).join('') : '<p class="dim">Nothing.</p>'}
      <h3>In the bank, unvetted</h3><p class="dim sm">Vet them on the slip before they can run. They cannot be dropped onto the pages until then.</p>${bench.map(s => `<div class="need adv" data-go="${E(s.key)}"><span class="t">BANK</span><span>${E(core.headlineOf(s) || s.slot)}<small>${core.allItemsOf(s).filter(i => !core.isVetted(i.id)).map(i => E(i.headline || i.id)).join(' · ')}</small></span></div>`).join('') || '<p class="dim">None.</p>'}`;
  }
  function readPane() {
    const ds = core.L.desk_summary || [], v = D.versions || [], log = D.decisionLog || [], last = log[log.length - 1], cal = core.build.calibration;
    const gen = core.L.generated_at || core.L.generated;
    return `<div class="read"><h3>Clark Kent’s read on the week</h3>${ds.length ? `<p class="lede">${E(ds[0])}</p>${ds.slice(1).map(p => `<p>${E(p)}</p>`).join('')}` : '<p class="dim">Clark has no summary this week.</p>'}
      ${gen ? `<p class="dim sm">Written when the lineup was generated (${core.fmt(gen)}). Vet flags in it predate anything you vetted since.</p>` : ''}
      <h4>Since then</h4><ul class="vers">${v.map(x => `<li class="${x.v === core.build.budgetVersion ? 'cur' : ''}">v${E(x.v)} · built ${core.fmt(x.built_at, false)} · ${x.decisions_through ? 'decisions through ' + core.fmt(x.decisions_through, false) : 'no decisions yet'} · data ${E(x.data)}</li>`).join('') || '<li>This is a preview build; it is not numbered.</li>'}</ul>
      ${log.length ? `<h4>Your decisions on file (${log.length})</h4><ul class="vers">${log.map(d => `<li>#${d.n} · ${d.kind === 'chat' ? 'by chat' : 'budget page'} · ${core.fmt(d.through)} · ${d.included} on the pages${d.vets ? ' · ' + d.vets + ' vets' : ''}</li>`).join('')}</ul>` : '<p class="dim sm">No decisions from you are on file for this issue yet. The pages start from Clark’s proposal.</p>'}
      ${last && last.chat ? `<h4>Your last word (${core.fmt(last.through)}, by chat)</h4><p class="quote">${E(last.chat)}</p>` : ''}
      ${last && last.changes.length ? `<h4>What Clark changed because of it</h4><ul>${last.changes.map(c => `<li>${E(c)}</li>`).join('')}</ul>` : ''}
      <p class="cal">Block sizes and holes are estimates from Clark’s capacity model${core.build.calibrated ? `, calibrated against the composed issues${cal ? ` (typically within ${E(cal.page_mae)} col-in a page)` : ''}` : ' (not calibrated)'}. The composer balances columns and scales art, so the printed page will not match block for block.
      <br><button class="lnk" id="startover">Start over from Clark’s version</button> (clears what this browser saved for this issue)</p></div>`;
  }
  function deskPane() {
    const f = core.fill();
    const noted = Object.keys(S.slotNotes).filter(k => core.slotBy[k] && S.slotNotes[k].trim());
    return `<h3>To Clark</h3><h4>General notes — copy, cuts, swaps, things to skip</h4><textarea class="sh-in" id="gnotes" rows="5" placeholder="Anything that isn’t about one slot…">${E(S.notes)}</textarea>
      <h4>Filler request</h4><textarea class="sh-in" id="filler" rows="3" placeholder="Ask Clark for filler…">${E(S.filler)}</textarea>
      ${f.status === 'short' ? `<button class="btn" id="askfill">Ask for ≈${f.words.toLocaleString()} words to close the hole</button>` : ''}
      <h4>Slot notes on file (${noted.length})</h4>${noted.map(k => `<div class="need adv" data-go="${E(k)}"><span class="t" style="border-color:var(--accent);color:var(--accent)">NOTE</span><span>${E(core.slotBy[k].slot)}<small>${E(S.slotNotes[k].slice(0, 150))}${S.slotNotes[k].length > 150 ? '…' : ''}</small></span></div>`).join('') || '<p class="dim">None. Open any block to leave one.</p>'}
      <p class="dim sm" style="margin-top:14px">Both boxes are filed in the submission’s <span class="mono">notes</span> field. Slot notes go in <span class="mono">slotNotes</span>.</p>`;
  }
  function slipPane() {
    if (A.sel.type === 'photo') { const id = A.sel.id, on = S.photos[id];
      const okp = core.canPlacePhoto(id);
      return `<div class="place"><span class="sh-lbl">On the budget</span><div class="seg" style="display:inline-flex">${[1, 2].map(p => `<button data-ppg="${p}" class="${on && S.photoPage[id] === p ? 'on' : ''}" ${okp ? '' : 'disabled title="Vet this photo first"'}>Page ${p}</button>`).join('')}<button data-ppg="0" class="${on ? '' : 'on'}">Bank</button></div>${okp ? '' : '<span class="dim sm">Vet the photo on the slip, then place it.</span>'}</div>${ui.photoSheet(id)}`; }
    const k = A.sel.id, s = core.slotBy[k], inc = S.inc[k], run = S.order.filter(x => S.inc[x]);
    const ok = core.canPlace(s);
    const bar = s.empty ? '' : `<div class="place"><span class="sh-lbl">On the budget</span><div class="seg" style="display:inline-flex">${[1, 2].map(p => `<button data-pg="${p}" class="${inc && S.page[k] === p ? 'on' : ''}" ${ok ? '' : 'disabled title="Vet this on the slip first"'}>Page ${p}</button>`).join('')}<button data-pg="0" class="${inc ? '' : 'on'}">Bank</button></div>
      ${ok ? '' : '<span class="dim sm">Vet it on the slip, then place it.</span>'}
      ${inc ? `<button class="btn" data-mv="-1">↑ Earlier</button><button class="btn" data-mv="1">↓ Later</button><span class="dim sm">runs #${run.indexOf(k) + 1} of ${run.length}</span>` : ''}</div>`;
    return bar + ui.sheet(k);
  }
  function renderSide() {
    const blk = NEEDS.filter(n => n.blocking).length;
    const tabs = [['needs', `Needs you (${blk})`], ['read', 'Clark’s read'], ['hist', 'Sections'], ['desk', 'To Clark']];
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
      ${blk.length ? `<p style="color:var(--bad)"><b>${blk.length} open item${blk.length > 1 ? 's' : ''}:</b></p>${blk.map(n => `<div class="need" ${n.slot ? `data-go="${E(n.slot)}"` : n.kind === 'photo' ? `data-gop="${E(n.id)}"` : ''}><span class="t">OPEN</span><span>${E(n.text)}</span></div>`).join('')}<p class="dim sm">You can still file; Clark will see these as unanswered.</p>` : '<p class="allclear">✔ Everything on the pages is vetted and answered.</p>'}
      <ul class="sum"><li><b>Runs</b> ${E(core.fmtDate(doc.publishDate))}${doc.publishDateAlt ? ` (alternate ${E(core.fmtDate(doc.publishDateAlt))})` : ' (no alternate)'}</li>
      <li><b>On the pages</b> ${doc.includedSlots.length} — ${doc.includedSlots.map(s => E(String(s.name).split(' — ')[0])).join(', ')}</li>
      <li><b>Left out</b> ${doc.excludedSlots.filter(s => !s.empty).length} + ${doc.excludedSlots.filter(s => s.empty).length} empty</li>
      <li><b>Photos</b> ${doc.photoIncludes.length || 'none'}</li><li><b>New vets</b> ${doc.vets.length || 'none this sitting'}</li>
      <li><b>Answers</b> ${doc.answers.length} · <b style="min-width:0">slot notes</b> ${Object.keys(doc.slotNotes).length}${doc.pages && (Object.keys(doc.pages.slots || {}).length + Object.keys(doc.pages.photos || {}).length) ? ` · <b style="min-width:0">pages</b> ${Object.keys(doc.pages.slots || {}).length + Object.keys(doc.pages.photos || {}).length} placed` : ''}</li><li><b>Fill</b> ${E($('#meter .m-txt') ? $('#meter .m-txt').textContent : '')}</li></ul>
      <p class="dim sm">Running order is <span class="mono">order</span>; which page each block sits on is <span class="mono">pages</span>. Nothing leaves this file until you download or copy the document and hand it to Clark.</p>
      <div class="acts"><button class="btn pri" id="dl">Download submission JSON</button><button class="btn" id="cp">Copy</button><button class="btn" data-closem>Back to the budget</button></div><p class="dim sm" id="signmsg" role="status"></p></div>
      <div><div class="sh-lbl">The submission document, exactly as it would be written</div><pre id="json">${E(JSON.stringify(doc, null, 2))}</pre></div></div>`;
    $('#modal').classList.add('open');
    const text = () => JSON.stringify(core.submission(), null, 2) + '\n';
    $('#dl').onclick = () => { const d = core.submission(); $('#signmsg').textContent = download(JSON.stringify(d, null, 2) + '\n', core.submissionName(d)) ? 'Download started: ' + core.submissionName(d) : 'Download blocked — use Copy, or select the text on the right.'; };
    $('#cp').onclick = () => copyText(text()).then(ok => { $('#signmsg').textContent = ok ? 'Copied. Paste it in chat to Clark.' : 'Could not copy automatically — select the text on the right and copy it.'; });
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
    if (r.superseded) notice('<span>Your earlier unsent work in this browser was replaced by the decisions Clark has since ingested.</span><button class="lnk" data-dismiss>OK</button>');
    else if (r.restored) notice(`<span>Picked up where you left off in this browser (saved ${E(core.fmt(saved.savedAt))})${r.dataChanged ? '. This is a newer build' + (r.dropped ? `; ${r.dropped} saved thing${r.dropped > 1 ? 's' : ''} no longer apply` : '') : ''}.</span><span><button class="lnk" id="startover2">Start over</button> · <button class="lnk" data-dismiss>OK</button></span>`);
  })();
  function startOver() { if (store) { try { store.removeItem(STORE_KEY); } catch (e) { /* ignore */ } } clearTimeout(saveT); core.on(() => clearTimeout(saveT)); location.reload(); }

  /* ---------- events ---------- */
  core.on(why => {
    if (why === 'resize-drag' || why === 'move-drag') { // mid-drag: the pointer path previews; skip a full rebuild
      save();
      return;
    }
    render(!ui.TEXTY.includes(why));
    save();
  });
  ui.bind($('#side'));
  window.addEventListener('resize', renderPages);
  document.addEventListener('click', e => {
    const t = e.target, c = q => t.closest(q);
    if (c('[data-closem]') || t === $('#modal')) return $('#modal').classList.remove('open');
    if (c('[data-dismiss]')) return notice('');
    if (c('#startover') || c('#startover2')) return startOver();
    if (c('#sign')) return openSign();
    if (c('[data-mode]')) {
      const mode = c('[data-mode]').dataset.mode;
      if (mode === 'manual' && !core.isManual()) core.act.toManual();
      else if (mode === 'auto' && core.isManual()) {
        if (confirm('Return to Auto placement? Your manual positions will be cleared. Switching back to Manual later snapshots Auto again.')) core.act.toAuto();
      }
      return;
    }
    if (c('#undoplace')) { core.act.undo(); return; }
    if (c('#toauto')) {
      if (confirm('Return to Auto placement? Your manual positions will be cleared. Switching back to Manual later snapshots Auto again.')) core.act.toAuto();
      return;
    }
    if (c('#needbtn')) { A.sel = null; A.tab = 'needs'; document.body.classList.add('side-open'); return render(); }
    if (c('[data-close]')) { if (A.sel && innerWidth > 900) A.sel = null; document.body.classList.remove('side-open'); return render(); }
    if (c('[data-tab]')) { A.sel = null; A.tab = c('[data-tab]').dataset.tab; document.body.classList.add('side-open'); return render(); }
    if (c('[data-add]')) { if (c('[data-add]').disabled) return; const st = c('.strip'), p = +c('[data-add]').dataset.add;
      return st.dataset.photo ? core.act.photo(st.dataset.photo, true, p) : core.act.place(st.dataset.slot, p); }
    if (c('[data-pg]')) { const p = +c('[data-pg]').dataset.pg, k = A.sel.id; return p ? core.act.place(k, p) : core.act.include(k, false); }
    if (c('[data-ppg]')) { const p = +c('[data-ppg]').dataset.ppg; return core.act.photo(A.sel.id, !!p, p); }
    if (c('[data-mv]')) return core.act.move(A.sel.id, +c('[data-mv]').dataset.mv);
    if (c('[data-date]')) { $('#modal').classList.remove('open'); $('#rund').open = true; return $('#rund').scrollIntoView({ block: 'nearest' }); }
    if (c('[data-go]') && c('[data-go]').dataset.go) { $('#modal').classList.remove('open'); return select('slot', c('[data-go]').dataset.go); }
    if (c('[data-gop]')) { $('#modal').classList.remove('open'); return select('photo', c('[data-gop]').dataset.gop); }
    if (c('#dswap')) { const a = S.altDate; if (!a) return; S.altDate = S.publishDate; core.act.date(a); return renderDatePop(); }
    if (c('#askfill')) { const f = core.fill(); core.act.filler(`Need about ${f.words} words of filler: ${core.r1(f.gap)} col-in are open under the current includes.`); return renderSide(); }
    if (c('[data-lay]') && c('.blk')) { e.preventDefault(); e.stopPropagation(); return core.act.setLayout(c('.blk').dataset.slot, c('[data-lay]').dataset.lay); }
    if (c('[data-play]') && c('.blk')) { e.preventDefault(); e.stopPropagation(); return core.act.setLayout(c('.blk').dataset.photo, c('[data-play]').dataset.play); }
    if (c('[data-handle]')) return;
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
    if ((e.ctrlKey || e.metaKey) && (e.key === 'z' || e.key === 'Z') && !e.shiftKey) {
      const tag = (e.target && e.target.tagName) || '';
      if (tag !== 'INPUT' && tag !== 'TEXTAREA') { e.preventDefault(); core.act.undo(); return; }
    }
    if (e.key === 'Escape' && escapeDrag()) { e.preventDefault(); return; }
    if (e.key === 'Escape') { $('#modal').classList.remove('open'); if (A.sel) { A.sel = null; render(); } }
    if (e.key === 'Enter' && e.target.matches && e.target.matches('.blk,.strip')) e.target.click();
  });
  /* ---------- where a drop lands ---------- */
  const rectOf = el => el.getBoundingClientRect();
  const inRect = (r, x, y) => x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
  const pageEl = p => document.querySelector(`.page[data-page="${p}"]`);
  const colsOf = p => document.querySelector(`.cols[data-page="${p}"]`);
  const ppiOf = cols => Number(cols && cols.dataset.ppi) || (cols ? cols.clientWidth / PW : 48);
  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  // Off the page to the left is the bank: the bank rail itself, or (side-by-side layout) anywhere left of page 1's paper.
  function inBankZone(x, y) {
    const bank = $('#bank'), p1 = pageEl(1);
    if (bank && inRect(rectOf(bank), x, y)) return true;
    return innerWidth > 900 && !!p1 && x < rectOf(p1).left;
  }
  const clearDropMarks = () => document.querySelectorAll('.drop').forEach(z => z.classList.remove('drop'));
  let dragEndedAt = 0, swallowClick = false; // the click that follows a drag or a handle drag is not a "select" click
  const markDragEnd = () => { dragEndedAt = performance.now(); swallowClick = true; };
  window.addEventListener('pointerdown', () => { swallowClick = false; }, true);
  window.addEventListener('keydown', () => { swallowClick = false; }, true);
  window.addEventListener('click', e => {
    if (!swallowClick) return;
    swallowClick = false;
    if (performance.now() - dragEndedAt < 600) { e.preventDefault(); e.stopPropagation(); }
  }, true);

  /* ---------- drag, Auto: the browser's drag-and-drop between the bank and the pages, and onto a block to run ahead of it ---------- */
  document.addEventListener('dragstart', e => {
    if (core.isManual()) { e.preventDefault(); return; } // Manual has its own pointer drag (below) and no browser drag at all
    if (e.target.closest && e.target.closest('[data-handle],.lay-tog,.handle')) { e.preventDefault(); return; }
    const b = e.target.closest && e.target.closest('[draggable="true"]'); if (!b) return;
    const ok = b.dataset.photo ? core.canPlacePhoto(b.dataset.photo) : core.canPlace(core.slotBy[b.dataset.slot]);
    if (!ok) { e.preventDefault(); return; }
    e.dataTransfer.setData('text/plain', b.dataset.photo ? 'p:' + b.dataset.photo : 's:' + b.dataset.slot); e.dataTransfer.effectAllowed = 'move'; });
  const autoZone = e => (e.target.closest && e.target.closest('.cols,.bank')) || (inBankZone(e.clientX, e.clientY) ? $('#bank') : null);
  document.addEventListener('dragover', e => {
    if (core.isManual()) return;
    const z = autoZone(e); if (!z) return;
    e.preventDefault();
    if (!z.classList.contains('drop')) { clearDropMarks(); z.classList.add('drop'); }
  });
  document.addEventListener('dragleave', e => { if (!e.relatedTarget) clearDropMarks(); });
  document.addEventListener('dragend', clearDropMarks);
  document.addEventListener('drop', e => {
    if (core.isManual()) { e.preventDefault(); return; }
    const z = autoZone(e); if (!z) return; e.preventDefault(); clearDropMarks();
    const raw = e.dataTransfer.getData('text/plain'), type = raw.slice(0, 1), id = raw.slice(2); if (!id || (type !== 'p' && type !== 's')) return;
    const p = z.classList.contains('cols') ? (+z.dataset.page || 0) : 0;
    if (type === 'p') return core.act.photo(id, !!p, p);
    if (!p) return core.act.include(id, false);
    const over = e.target.closest('.blk[data-slot]');
    if (over && over.dataset.slot !== id) core.act.before(id, over.dataset.slot);
    core.act.place(id, p);
  });

  /* ---------- drag, Manual: one pointer drag for page blocks and bank strips ----------
     A picture is draggable by default, so the browser's drag used to start on a photo a few pixels in and cancel
     the move ("photos are not reliable at all"). In Manual the browser's drag is off everywhere and this is the
     only drag: grab a block anywhere (picture included) and it lands on the dashed outline, snapped to the columns
     and the 0.05in grid. Nothing in the layout moves while a block is in the air, so the outline is where it lands.
     Release left of page 1 (over the bank) to pull a block off the pages. Esc cancels. */
  const DRAG_PX = 4;
  let mv = null, mvRaf = 0;
  function moveTarget(d) {
    if (inBankZone(d.x, d.y)) return { bank: true };
    let best = null;
    [1, 2].forEach(p => {
      const pg = pageEl(p); if (!pg) return;
      const r = rectOf(pg);
      const dist = Math.hypot(d.x < r.left ? r.left - d.x : d.x > r.right ? d.x - r.right : 0, d.y < r.top ? r.top - d.y : d.y > r.bottom ? d.y - r.bottom : 0);
      if (!best || dist < best.dist) best = { p, dist };
    });
    if (!best) return null;
    const cols = colsOf(best.p), cr = rectOf(cols), ppi = ppiOf(cols), H = core.pageH(best.p);
    const col = clamp(Math.round((d.x - d.grabX - cr.left) / ppi / (CW + GUT)), 0, 3 - d.span);
    const topIn = clamp(core.snapY((d.y - d.grabY - cr.top) / ppi), 0, core.snapY(Math.max(0, H - 0.25)));
    return { page: best.p, col, span: d.span, topIn, heightIn: d.heightIn, cols, ppi };
  }
  function startMove(d) {
    d.started = true;
    const ppi = ppiOf(colsOf(1)), w = spanW(d.span) * ppi, h = Math.max(6, d.heightIn * ppi - 3);
    let g;
    if (d.onPage) {
      g = d.el.cloneNode(true);
      g.querySelectorAll('.handle,.lay-tog,.hang,.marks').forEach(n => n.remove());
      ['sel', 'overlap', 'spill', 'lifted', 'lifting'].forEach(c => g.classList.remove(c));
    } else { // a strip from the bank flies as the block it will become
      const s = d.slot ? core.slotBy[d.slot] : null;
      g = document.createElement('div');
      g.className = 'blk ' + (d.photo ? 't-photo' : 't-' + (((s && s.cost) || {}).type || 'prose'));
      g.innerHTML = d.photo ? `<img draggable="false" src="${core.thumb(core.media[d.photo].filename)}" alt=""><div class="k">Photo · ${E(core.media[d.photo].kind)}</div>`
        : `<div class="k">${E(ui.shortName(s))}</div>${s.thumb ? `<img draggable="false" src="${core.thumb(s.thumb)}" alt="">` : ''}<div class="h">${E(core.headlineOf(s) || s.slot)}</div><div class="greek"></div>`;
      d.grabX = Math.min(14, w / 3); d.grabY = Math.min(12, h / 3);
    }
    ['data-slot', 'data-photo', 'tabindex', 'draggable'].forEach(a => g.removeAttribute(a));
    g.classList.add('drag-ghost');
    g.setAttribute('aria-hidden', 'true');
    Object.assign(g.style, { position: 'fixed', left: '0px', top: '0px', width: w + 'px', height: h + 'px', margin: '0', transform: 'none' });
    const tag = document.createElement('span'); tag.className = 'ghost-tag'; g.appendChild(tag);
    document.body.appendChild(g);
    d.ghost = g; d.tag = tag;
    d.outline = document.createElement('div'); d.outline.className = 'drop-outline';
    d.where = document.createElement('span'); d.where.className = 'drop-tag'; d.outline.appendChild(d.where);
    d.el.classList.add('lifting');
    document.body.classList.add('moving');
    try { d.el.setPointerCapture(d.pointerId); } catch (err) { /* best-effort: window listeners still see the pointer */ }
  }
  function paintMove(d) {
    const t = moveTarget(d), bank = !!(t && t.bank);
    d.ghost.style.transform = `translate(${d.x - d.grabX}px,${d.y - d.grabY}px)`;
    d.ghost.classList.toggle('to-bank', bank);
    const bk = $('#bank'); if (bk) bk.classList.toggle('drop', bank);
    d.tag.textContent = bank ? (d.onPage ? 'To the bank' : 'Stays in the bank') : '';
    if (!t || bank) { d.outline.remove(); return; }
    if (d.outline.parentNode !== t.cols) t.cols.appendChild(d.outline);
    Object.assign(d.outline.style, { left: colX(t.col) * t.ppi + 'px', top: t.topIn * t.ppi + 'px', width: spanW(t.span) * t.ppi + 'px', height: Math.max(6, t.heightIn * t.ppi - 3) + 'px' });
    d.where.textContent = `Page ${t.page} · col ${t.col + 1}${t.span > 1 ? '–' + (t.col + t.span) : ''} · ${t.topIn.toFixed(2)} in down`;
  }
  function endMoveVisuals(d) {
    if (d.ghost) d.ghost.remove();
    if (d.outline) d.outline.remove();
    if (d.el) d.el.classList.remove('lifting');
    document.body.classList.remove('moving');
    clearDropMarks();
    try { if (d.el && d.el.hasPointerCapture && d.el.hasPointerCapture(d.pointerId)) d.el.releasePointerCapture(d.pointerId); } catch (err) { /* ignore */ }
  }
  function dropMove(d) {
    const t = moveTarget(d);
    endMoveVisuals(d);
    markDragEnd();
    if (!t) return;
    if (t.bank) { if (d.onPage) core.act.toBank(d.id); return; }
    const cur = S.manualLayout[d.id], on = d.photo ? S.photos[d.id] : S.inc[d.id];
    if (on && cur && cur.page === t.page && cur.col === t.col && Math.abs(cur.topIn - t.topIn) < 0.001) return; // dropped where it was
    A.lift = d.id; // the block just placed draws on top, so an overlap never hides it
    const pos = { page: t.page, col: t.col, span: t.span, topIn: t.topIn, heightIn: t.heightIn };
    if (d.photo) core.act.placePhotoAt(d.photo, pos); else core.act.placeAt(d.slot, pos);
  }
  function cancelMove() {
    if (!mv) return;
    const d = mv; mv = null;
    if (mvRaf) { cancelAnimationFrame(mvRaf); mvRaf = 0; }
    if (d.started) { endMoveVisuals(d); markDragEnd(); }
  }
  document.addEventListener('pointerdown', e => {
    if (!core.isManual() || mv || hd || e.button !== 0) return;
    const t = e.target;
    if (!t.closest || t.closest('[data-handle],.lay-tog,button,input,textarea,select,a,label,.marks')) return;
    const el = t.closest('.cols .blk, #bank .strip'); if (!el || el.classList.contains('ghost')) return;
    const photo = el.dataset.photo, slot = el.dataset.slot, id = photo || slot; if (!id) return;
    if (photo ? !core.canPlacePhoto(photo) : !(core.slotBy[slot] && core.canPlace(core.slotBy[slot]))) return; // vet first; a click still opens the slip
    const onPage = el.classList.contains('blk'), sz = S.manualLayout[id] || core.defaultSize(id), r = rectOf(el);
    if (e.pointerType === 'mouse') e.preventDefault(); // no text selection or picture drag under the pointer
    mv = { id, photo, slot, el, onPage, span: sz.span, heightIn: sz.heightIn, x0: e.clientX, y0: e.clientY, x: e.clientX, y: e.clientY,
      grabX: e.clientX - r.left, grabY: e.clientY - r.top, started: false, pointerId: e.pointerId };
  });
  window.addEventListener('pointermove', e => {
    if (!mv || e.pointerId !== mv.pointerId) return;
    mv.x = e.clientX; mv.y = e.clientY;
    if (!mv.started) { if (Math.abs(mv.x - mv.x0) + Math.abs(mv.y - mv.y0) < DRAG_PX) return; startMove(mv); }
    if (!mvRaf) mvRaf = requestAnimationFrame(() => { mvRaf = 0; if (mv && mv.started) paintMove(mv); });
  });
  window.addEventListener('pointerup', e => {
    if (!mv || e.pointerId !== mv.pointerId) return;
    const d = mv; mv = null;
    if (mvRaf) { cancelAnimationFrame(mvRaf); mvRaf = 0; }
    if (!d.started) return; // a click: the click handler opens the slip
    d.x = e.clientX; d.y = e.clientY;
    dropMove(d);
  });
  window.addEventListener('pointercancel', e => { if (mv && e.pointerId === mv.pointerId) cancelMove(); });
  window.addEventListener('blur', () => { cancelMove(); });

  /* ---------- handles ----------
     Manual: right edge = width (snaps to 1, 2 or 3 columns), bottom edge = depth (0.05in grid). Only that block
     changes. Art keeps its shape (a wider frame scales the picture with it; a deeper or shallower frame scales the
     picture to fit, never cropped). Text re-flows on a new width; the bottom edge asks Clark for the length that fills it.
     Auto: the corner scales art (aspect locked, snaps 1/2/3 columns); the bottom edge grows or shrinks a story.
     Mid-drag only this block and the page footers are redrawn; the full rebuild waits for the release so the handle
     under the pointer is never destroyed mid-gesture, and nothing above the pages changes size. */
  let hd = null, hdRaf = 0;
  function handleApply(d) {
    const dx = (d.x - d.x0) / d.ppi, dy = (d.y - d.y0) / d.ppi;
    if (core.isManual() && d.from) {
      const cur = S.manualLayout[d.id] || d.from;
      if (d.kind === 'width') {
        const span = core.snapSpan(core.frameW(d.from.span) + dx);
        if (span !== cur.span) core.act.frame(d.id, { span }, 'resize-drag', d.from);
      } else if (d.kind === 'length') {
        const h = core.snapY(Math.max(0.4, d.from.heightIn + dy));
        if (Math.abs(h - cur.heightIn) > 0.001) core.act.frame(d.id, { heightIn: h }, 'resize-drag', d.from);
      }
    } else if (d.kind === 'scale' || d.kind === 'width') {
      const span = core.snapSpan((core.SNAP_WIDTHS[d.startSpan] || cap.col_width_in) + dx);
      if (d.photo) { if (core.photoSpanOf(d.photo) !== span) core.act.setSpan(d.photo, span, 'resize-drag'); }
      else if (d.slot && core.spanOf(core.slotBy[d.slot]) !== span) core.act.setSpan(d.slot, span, 'resize-drag');
    } else if (d.kind === 'length' && d.slot) {
      const s = core.slotBy[d.slot]; if (!s) return;
      const span = core.spanOf(s), newH = Math.max(0.4, d.startH + dy);
      const toWords = core.wordsForColIn(s, newH * span); // the block's new depth follows the pointer exactly
      if (d.lastWords != null && Math.abs(toWords - d.lastWords) < 5) return;
      d.lastWords = toWords;
      core.act.setResize(d.slot, toWords >= core.baseWordsOf(s) ? 'expand' : 'shrink', toWords + 'w', 'resize-drag');
    }
    previewBlock(d);
  }
  function previewBlock(d) {
    const blk = d.el && d.el.isConnected ? d.el : document.querySelector(d.photo ? `.blk[data-photo="${CSS.escape(d.photo)}"]` : `.blk[data-slot="${CSS.escape(d.slot)}"]`);
    if (blk) {
      const ppi = d.ppi, s = d.slot ? core.slotBy[d.slot] : null, man = core.isManual() && S.manualLayout[d.id];
      const span = man ? man.span : d.photo ? core.photoSpanOf(d.photo) : core.spanOf(s);
      const hIn = man ? man.heightIn : (d.photo ? core.photoCost(d.photo) : core.costOf(s)) / span;
      blk.style.width = spanW(span) * ppi + 'px';
      blk.style.height = Math.max(6, hIn * ppi - 3) + 'px';
      if (man) blk.style.left = colX(man.col) * ppi + 'px';
      const img = blk.querySelector('img.fit');
      if (man && img && core.isArtId(d.id)) { const f = core.artFit(d.id, man.span, man.heightIn); img.style.width = f.w * ppi + 'px'; img.style.height = f.h * ppi + 'px'; }
      const lab = blk.querySelector('.size-lab');
      if (lab) {
        if (d.photo || (s && (s.cost || {}).type === 'figure')) {
          const sz = d.photo ? core.photoSize(d.photo) : core.slotSize(s);
          lab.textContent = core.r1(sz.widthIn) + ' × ' + core.r1(sz.heightIn) + ' in';
        } else if (s && S.resize[s.key]) {
          const rz = S.resize[s.key];
          lab.textContent = (rz.direction || '') + (rz.toWords != null ? ' ' + rz.toWords + 'w' : '');
        }
      }
    }
    [1, 2].forEach(p => {
      const r = core.pack(p), pg = pageEl(p), foot = pg && pg.querySelector('.pfoot');
      if (!foot) return;
      const overTxt = r.overset > 0.02
        ? `OVERSET by ${core.r1(r.overset)} col-in ≈ ${r.oversetWords || Math.round(r.overset * cap.wpi)} words · hangs ${core.r1(r.spillIn || 0)} in below the trim`
        : `open ${core.r1(r.open)} col-in ≈ ${Math.round(r.open * cap.wpi)} words`;
      foot.innerHTML = `<span>PAGE ${p} · ${core.r1(r.placedUsed)} of ${core.r1(r.cap)} col-in on the page</span><span class="${r.open > 0.5 || r.overset > 0.02 ? 'short' : ''}">${overTxt}</span>`;
    });
  }
  document.addEventListener('pointerdown', e => {
    const h = e.target.closest && e.target.closest('[data-handle]'); if (!h || e.button !== 0 || mv || hd) return;
    const blk = h.closest('.blk'); if (!blk) return;
    e.preventDefault(); e.stopPropagation();
    const cols = blk.closest('.cols'), ppi = ppiOf(cols);
    const photo = blk.dataset.photo, slot = blk.dataset.slot, id = photo || slot, s = slot ? core.slotBy[slot] : null;
    const man = core.isManual() && S.manualLayout[id], span = photo ? core.photoSpanOf(photo) : core.spanOf(s);
    hd = { kind: h.dataset.handle, id, photo, slot, el: blk, ppi, x0: e.clientX, y0: e.clientY, x: e.clientX, y: e.clientY,
      from: man ? Object.assign({}, man) : null, startSpan: span,
      startH: man ? man.heightIn : (photo ? core.photoCost(photo) : core.costOf(s)) / span, moved: false, pointerId: e.pointerId };
    document.body.classList.add('resizing');
    try { h.setPointerCapture(e.pointerId); } catch (err) { /* best-effort */ }
  });
  window.addEventListener('pointermove', e => {
    if (!hd || e.pointerId !== hd.pointerId) return;
    hd.x = e.clientX; hd.y = e.clientY;
    if (!hd.moved) {
      if (Math.abs(hd.x - hd.x0) + Math.abs(hd.y - hd.y0) <= 2) return;
      hd.moved = true;
      if (core.isManual()) core.act.checkpoint(); // one undo step per handle drag
    }
    if (hdRaf) return;
    const d = hd;
    hdRaf = requestAnimationFrame(() => { hdRaf = 0; if (hd === d) handleApply(d); });
  });
  function endHandle(e, cancelled) {
    if (!hd || (e && e.pointerId !== hd.pointerId)) return;
    if (hdRaf) { cancelAnimationFrame(hdRaf); hdRaf = 0; }
    const d = hd; hd = null;
    document.body.classList.remove('resizing');
    if (!d.moved) return;
    if (!cancelled && e) { d.x = e.clientX; d.y = e.clientY; handleApply(d); } // flush the last point
    markDragEnd();
    if (core.isManual()) A.lift = d.id;
    render(); save(); // full pack + slip, now that the gesture is done
  }
  window.addEventListener('pointerup', e => endHandle(e, false));
  window.addEventListener('pointercancel', e => endHandle(e, true));
  function escapeDrag() { // Esc: a block in the air goes back; a handle drag is undone
    if (mv) { cancelMove(); return true; }
    if (hd) { const moved = hd.moved; endHandle(null, true); if (moved && core.isManual()) core.act.undo(); return true; }
    return false;
  }

  renderDatePop(); render();
  window.BudgetPage = { core, payload: () => core.submission(), storeKey: () => STORE_KEY, select };
})();
