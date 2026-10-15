/* Landing page: random messy desk, draggable papers, mobile fallback */
(function () {
  'use strict';
  var stage = document.getElementById('stage');
  var props = document.getElementById('props');
  var mobileList = document.getElementById('m-list');
  var mobileCover = document.getElementById('m-cover');
  var issues = [];
  var zTop = 1000;
  var mq = window.matchMedia(EGG.MOBILE_QUERY);
  var built = false;

  function rnd(a, b) { return a + Math.random() * (b - a); }
  function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
  function shuffle(a) { for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }

  // Mitchell best-candidate: spreads points out but still lets them overlap.
  function spread(n, box, existing) {
    var pts = existing.slice(), out = [];
    for (var i = 0; i < n; i++) {
      var best = null, bd = -1;
      for (var k = 0; k < 14; k++) {
        var p = { x: rnd(box[0], box[2]), y: rnd(box[1], box[3]) };
        var d = pts.length ? Infinity : 1;
        pts.forEach(function (q) { d = Math.min(d, Math.hypot((p.x - q.x), (p.y - q.y) * 1.5)); });
        if (d > bd) { bd = d; best = p; }
      }
      pts.push(best); out.push(best);
    }
    return out;
  }

  function place(node, x, y, rot, z, delay) {
    node.style.left = x + '%';
    node.style.top = y + '%';
    node.style.zIndex = z;
    node.firstChild.style.setProperty('--r', rot + 'deg');
    node.firstChild.style.setProperty('--d', delay + 's');
  }

  function makeItem(cls, w, ar) {
    var item = document.createElement('div');
    item.className = 'item ' + cls;
    if (w) item.style.width = w + '%';
    if (ar) item.style.aspectRatio = ar;
    var sheet = document.createElement('div');
    sheet.className = 'sheet';
    item.appendChild(sheet);
    return item;
  }

  // 1200w + full-res srcset so thumbnails stay crisp on HiDPI screens
  function setSrc(im, iss, n, sizes) {
    var th = iss.thumbs && iss.thumbs[n];
    if (th) { im.sizes = sizes; im.srcset = th + ' 1200w, ' + iss.pages[n] + ' 1870w'; }
    im.src = iss.pages[n];
  }

  function makePaper(iss, cls) {
    var item = makeItem('paper ' + cls);
    item.setAttribute('role', 'button');
    item.tabIndex = 0;
    item.setAttribute('aria-label', 'Open En Garde Gazette No. ' + iss.number + ': ' + iss.headline);
    var im = new Image();
    setSrc(im, iss, 0, 'min(calc((100vw - 24px) * .24), calc((100vh - 84px) * .3605))');
    im.alt = '';
    im.draggable = false;
    im.decoding = 'async';
    item.firstChild.appendChild(im);
    item._issue = iss;
    return item;
  }

  function makeTin(src, w, ar) {
    var item = makeItem('tin', w, ar);
    item.setAttribute('aria-hidden', 'true');
    var im = new Image();
    im.src = src; im.alt = ''; im.draggable = false;
    item.firstChild.appendChild(im);
    return item;
  }

  /* ---------- rolling pencils ---------- */
  // Desk edge, as fractions of the stage (the wooden rim in desk.webp).
  var EDGE = { x0: 0.04, x1: 0.965, y0: 0.045, y1: 0.955 };
  var PR = 10, PVB = '0 0 540 20'; // body radius / viewBox in SVG units
  var NS = 'http://www.w3.org/2000/svg';
  var pencilSeq = 0;
  var pencils = window.__pencils = [];
  var raf = 0, lastTs = 0, pencilsSpawned = false;

  function makePencil() {
    var id = 'pc' + (++pencilSeq);
    var item = makeItem('pencil');
    item.setAttribute('aria-hidden', 'true');
    var facets = '';
    for (var i = 0; i < 6; i++) {
      facets += '<g class="f"><rect x="72" y="0" width="372" height="1"/>' +
        '<rect x="72" y=".44" width="372" height=".12" fill="#000" opacity=".16"/>' +
        (i === 0 ? '<g fill="#4a2f00" opacity=".72"><rect x="150" y=".36" width="46" height=".28"/><rect x="200" y=".36" width="14" height=".28"/>' +
          '<rect x="218" y=".36" width="30" height=".28"/><rect x="252" y=".36" width="22" height=".28"/><rect x="290" y=".36" width="40" height=".28"/></g>' : '') +
        (i === 3 ? '<rect x="96" y=".3" width="8" height=".4" fill="#7a1f1f" opacity=".7"/>' : '') +
        '</g>';
    }
    var ridges = '';
    for (var k = 0; k < 4; k++) ridges += '<rect x="' + (44 + k * 6) + '" y="0" width="1.6" height="20" fill="#5a3f10" opacity=".55"/>' +
      '<rect x="' + (45.6 + k * 6) + '" y="0" width="1" height="20" fill="#fff2b0" opacity=".35"/>';
    item.firstChild.innerHTML =
      '<svg viewBox="' + PVB + '" overflow="visible">' +
      '<defs>' +
      '<linearGradient id="' + id + 'cyl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".42"/><stop offset=".22" stop-color="#fff" stop-opacity=".05"/><stop offset=".34" stop-color="#fff" stop-opacity=".38"/><stop offset=".48" stop-color="#fff" stop-opacity=".04"/><stop offset=".8" stop-color="#000" stop-opacity=".22"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></linearGradient>' +
      '<linearGradient id="' + id + 'br" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7a5a1c"/><stop offset=".2" stop-color="#e9cf87"/><stop offset=".38" stop-color="#fff3c4"/><stop offset=".55" stop-color="#c4a04e"/><stop offset=".85" stop-color="#7c5c1e"/><stop offset="1" stop-color="#4c3510"/></linearGradient>' +
      '<linearGradient id="' + id + 'er" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a86a6c"/><stop offset=".3" stop-color="#f2a9ac"/><stop offset=".45" stop-color="#ffd0d1"/><stop offset=".8" stop-color="#d98a8e"/><stop offset="1" stop-color="#8d5456"/></linearGradient>' +
      '<linearGradient id="' + id + 'wd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3dcae"/><stop offset=".45" stop-color="#e2bd82"/><stop offset=".75" stop-color="#bf935a"/><stop offset="1" stop-color="#8e6538"/></linearGradient>' +
      '<linearGradient id="' + id + 'gr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7b7b82"/><stop offset=".35" stop-color="#3b3b42"/><stop offset="1" stop-color="#18181b"/></linearGradient>' +
      '<clipPath id="' + id + 'cp"><path d="M72 0H436 q-5 3.3 0 6.6 q-5 3.4 0 6.8 q-5 3.3 0 6.6 V20H72Z"/></clipPath>' +
      '</defs>' +
      // sharpened cone: bare wood, then graphite
      '<path d="M420 0 L506 7.2 Q508 10 506 12.8 L420 20Z" fill="url(#' + id + 'wd)"/>' +
      '<path d="M432 2 L470 5.6 M436 6 L480 8 M434 14 L478 12.4 M430 18 L466 14.6" stroke="#8a6030" stroke-width=".5" opacity=".35" fill="none"/>' +
      '<path d="M498 6.4 L538 9.1 Q540 10 538 10.9 L498 13.6Z" fill="url(#' + id + 'gr)"/>' +
      '<path d="M500 8.2 L530 9.4" stroke="#bbb" stroke-width=".6" opacity=".5"/>' +
      // painted hex body (facets are driven by the roll angle) with scalloped sharpening edge
      '<g clip-path="url(#' + id + 'cp)">' + facets + '<rect x="72" y="0" width="372" height="20" fill="url(#' + id + 'cyl)" opacity=".35"/></g>' +
      // brass ferrule
      '<rect x="34" y=".5" width="42" height="19" fill="url(#' + id + 'br)"/>' + ridges +
      '<rect x="72" y=".5" width="4" height="19" fill="#000" opacity=".25"/>' +
      // eraser
      '<path d="M4 3 Q0 3.5 0 10 Q0 16.5 4 17 H36 V3Z" fill="url(#' + id + 'er)"/>' +
      '<path d="M2 4 Q.6 6 .6 10" stroke="#fff" stroke-width=".8" opacity=".4" fill="none"/>' +
      '</svg>';
    item._facets = Array.prototype.slice.call(item.firstChild.querySelectorAll('g.f'));
    return item;
  }

  function pencilR(s) { // apothem in px, for rolling distance
    return PR * (stageW() * 0.27 / 540);
  }
  function stageW() { return stage.getBoundingClientRect().width; }

  function renderPencil(it) {
    var s = it._s, th = s.th * Math.PI / 180;
    // light from upper-left of the screen, expressed in the pencil's own (y, z) frame
    var ly = 0.35 * Math.sin(th) - 0.9 * Math.cos(th), lz = 0.55, ln = Math.hypot(ly, lz);
    ly /= ln; lz /= ln;
    it._facets.forEach(function (g, i) {
      var c = s.phase + i * 60;
      c = ((c + 180) % 360 + 360) % 360 - 180;
      var lo = Math.max(c - 30, -90), hi = Math.min(c + 30, 90);
      if (hi <= lo) { g.setAttribute('display', 'none'); return; }
      var y0 = 10 + PR * Math.sin(lo * Math.PI / 180), y1 = 10 + PR * Math.sin(hi * Math.PI / 180);
      var am = (lo + hi) / 2 * Math.PI / 180;
      var dot = Math.max(0, Math.sin(am) * ly + Math.cos(am) * lz);
      var light = 20 + 42 * (0.18 + 0.82 * dot) + (i === 0 ? 0 : 0);
      g.removeAttribute('display');
      g.setAttribute('transform', 'translate(0 ' + y0.toFixed(3) + ') scale(1 ' + Math.max(y1 - y0, 0.01).toFixed(3) + ')');
      g.firstChild.setAttribute('fill', 'hsl(' + (43 + dot * 3).toFixed(1) + ',' + (88 - (1 - dot) * 10).toFixed(1) + '%,' + light.toFixed(1) + '%)');
    });
    it.style.left = (s.x * 100) + '%';
    it.style.top = (s.y * 100) + '%';
    it.firstChild.style.setProperty('--r', s.th + 'deg');
  }

  function placePencil(it, x, y, th) {
    var s = it._s || (it._s = { vx: 0, vy: 0, phase: rnd(0, 360), drag: false, fall: false });
    s.x = x; s.y = y; s.th = th; s.vx = s.vy = 0; s.drag = false;
    renderPencil(it);
  }

  function dropPencil(it) {
    var s = it._s;
    if (s.fall) return;
    s.fall = true;
    var sp = Math.hypot(s.vx, s.vy) || 1, d = Math.min(Math.max(sp * 0.3, 30), 150);
    it.firstChild.style.setProperty('--fx', (s.vx / sp * d) + 'px');
    it.firstChild.style.setProperty('--fy', (s.vy / sp * d + 30) + 'px');
    it.classList.remove('dragging');
    it.classList.add('falling');
    it.style.zIndex = 150; // slips under the loose papers as it drops
    var i = pencils.indexOf(it);
    if (i >= 0) pencils.splice(i, 1);
    setTimeout(function () { it.remove(); }, 850);
  }

  function outside(s) { return s.x <= EDGE.x0 || s.x >= EDGE.x1 || s.y <= EDGE.y0 || s.y >= EDGE.y1; }

  function tick(ts) {
    raf = 0;
    var dt = Math.min((ts - lastTs) / 1000 || 0.016, 0.034);
    lastTs = ts;
    var active = false, r = stage.getBoundingClientRect();
    pencils.slice().forEach(function (it) {
      var s = it._s;
      if (s.fall || s.drag) return;
      var sp = Math.hypot(s.vx, s.vy);
      if (sp < 6) { s.vx = s.vy = 0; return; }
      var th = s.th * Math.PI / 180, c = Math.cos(th), sn = Math.sin(th);
      var va = s.vx * c + s.vy * sn, vp = -s.vx * sn + s.vy * c;
      va *= Math.exp(-7 * dt);                 // sliding along the axis: grips fast
      vp *= Math.exp(-1.25 * dt);              // rolling: keeps momentum
      var vpm = Math.max(Math.abs(vp) - 30 * dt, 0); vp = vp < 0 ? -vpm : vpm; // rolling resistance
      s.vx = va * c - vp * sn; s.vy = va * sn + vp * c;
      s.x += s.vx * dt / r.width; s.y += s.vy * dt / r.height;
      s.phase = (s.phase + vp * dt / pencilR(s) * 180 / Math.PI) % 360;
      renderPencil(it);
      if (outside(s)) dropPencil(it); else active = true;
    });
    if (active) { raf = requestAnimationFrame(tick); }
  }
  function kick() { if (!raf) { lastTs = performance.now(); raf = requestAnimationFrame(tick); } }

  function attachPencilDrag(it) {
    var st = null;
    it.addEventListener('pointerdown', function (e) {
      if (e.button !== 0 || it._s.fall) return;
      var s = it._s;
      s.vx = s.vy = 0; s.drag = true;
      st = { id: e.pointerId, px: e.clientX, py: e.clientY, moved: false, trail: [{ t: e.timeStamp, x: e.clientX, y: e.clientY }] };
      it.setPointerCapture(e.pointerId);
      it.style.zIndex = ++zTop;
    });
    it.addEventListener('pointermove', function (e) {
      if (!st || e.pointerId !== st.id) return;
      var s = it._s, r = stage.getBoundingClientRect();
      var dx = e.clientX - st.px, dy = e.clientY - st.py;
      if (!st.moved) { if (Math.hypot(dx, dy) < 4) return; st.moved = true; it.classList.add('dragging'); }
      st.px = e.clientX; st.py = e.clientY;
      var th = s.th * Math.PI / 180;
      s.phase = (s.phase + (-dx * Math.sin(th) + dy * Math.cos(th)) / pencilR(s) * 180 / Math.PI) % 360; // dragging sideways rolls it
      s.x = Math.min(Math.max(s.x + dx / r.width, EDGE.x0), EDGE.x1);
      s.y = Math.min(Math.max(s.y + dy / r.height, EDGE.y0), EDGE.y1);
      st.trail.push({ t: e.timeStamp, x: e.clientX, y: e.clientY });
      while (st.trail.length > 2 && e.timeStamp - st.trail[0].t > 90) st.trail.shift();
      renderPencil(it);
    });
    function end(e, cancelled) {
      if (!st || e.pointerId !== st.id) return;
      var s = it._s, moved = st.moved, tr = st.trail, r = stage.getBoundingClientRect();
      st = null; s.drag = false;
      it.classList.remove('dragging');
      if (!moved || cancelled) return;
      var a = tr[0], b = tr[tr.length - 1], span = (b.t - a.t) / 1000;
      if (span > 0.012 && e.timeStamp - b.t < 80) { s.vx = (b.x - a.x) / span; s.vy = (b.y - a.y) / span; }
      var sp = Math.hypot(s.vx, s.vy);
      if (sp > 2400) { s.vx *= 2400 / sp; s.vy *= 2400 / sp; }
      // a small nudge near the rim is enough to tip it over
      var tip = 0.03, nx = 0, ny = 0;
      if (s.x - EDGE.x0 < tip) nx = -1; else if (EDGE.x1 - s.x < tip) nx = 1;
      if (s.y - EDGE.y0 < tip * 1.5) ny = -1; else if (EDGE.y1 - s.y < tip * 1.5) ny = 1;
      if (nx || ny) {
        var n = Math.hypot(nx, ny); nx /= n; ny /= n;
        var out = s.vx * nx + s.vy * ny;
        if (out < 160) { s.vx += nx * (160 - out); s.vy += ny * (160 - out); }
      }
      if (outside(s)) dropPencil(it); else kick();
    }
    it.addEventListener('pointerup', function (e) { end(e, false); });
    it.addEventListener('pointercancel', function (e) { end(e, true); });
  }

  function buildDesk() {
    pencils.forEach(function (pc) { pc.remove(); if (pc._s) { pc._s.vx = pc._s.vy = 0; } });
    props.textContent = '';
    stage.querySelectorAll('.item, .stains').forEach(function (n) { n.remove(); });
    zTop = 1000;

    var stains = document.createElement('div');
    stains.className = 'stains';
    var coffee = document.createElement('div');
    coffee.className = 'coffee';
    coffee.style.cssText = 'width:' + rnd(5.5, 7) + '%;left:' + rnd(14, 80) + '%;top:' + rnd(14, 62) + '%';
    var blot = document.createElement('div');
    blot.className = 'inkblot';
    blot.style.cssText = 'left:' + rnd(12, 88) + '%;top:' + rnd(14, 86) + '%;transform:rotate(' + rnd(0, 360) + 'deg)';
    stains.appendChild(coffee); stains.appendChild(blot);
    stage.insertBefore(stains, props);

    var count = 7 + Math.floor(Math.random() * 3); // 7-9 copies
    var newest = issues[0];
    var pts = spread(count, [24, 30, 76, 70], []);
    var folds = ['', 'fold-h', 'fold-v', '', 'fold-h'];
    var order = [];
    // newest copy goes last (on top); the rest are random picks from the archive
    for (var i = 0; i < count - 1; i++) order.push(pick(issues));
    // make sure the newest issue shows up under itself too, for a fresh pile
    if (count > 2 && Math.random() < .6) order[Math.floor(Math.random() * order.length)] = newest;
    order.push(newest);

    var all = [];
    order.forEach(function (iss, i) {
      var top = i === order.length - 1;
      var p = makePaper(iss, pick(folds));
      var pt = top ? { x: rnd(40, 60), y: rnd(44, 56) } : pts[i];
      place(p, pt.x, pt.y, top ? rnd(-14, 14) : rnd(-38, 38), top ? zTop : 10 + i, i * 0.06);
      all.push(p);
    });

    // props: near the margins, above the loose papers but under the newest one
    var tinPts = shuffle([[12, 20], [88, 22], [11, 80], [89, 79], [50, 14], [50, 86]]);
    var tp = makeTin('assets/tin-paperclips.webp', 9.4, '1162 / 1214');
    place(tp, tinPts[0][0] + rnd(-4, 4), tinPts[0][1] + rnd(-4, 4), rnd(-180, 180), 200, 0.5);
    all.push(tp);
    all.forEach(function (n) { props.appendChild(n); attachDrag(n); });

    // pencils: two on the first build; re-mess only re-scatters the survivors (rolled-off ones never return)
    if (!pencilsSpawned) {
      pencilsSpawned = true;
      for (var q = 0; q < 2; q++) { var np = makePencil(); attachPencilDrag(np); pencils.push(np); }
    }
    pencils.forEach(function (pc, i) {
      var top = i % 2 === 0, flip = Math.random() < .5 ? 180 : 0;
      placePencil(pc, (top ? rnd(22, 45) : rnd(55, 78)) / 100, (top ? rnd(11, 16) : rnd(84, 89)) / 100, rnd(-20, 20) + flip);
      pc.style.zIndex = 201 + i;
      props.appendChild(pc);
    });
  }

  function attachDrag(item) {
    var isPaper = !!item._issue, st = null;

    item.addEventListener('pointerdown', function (e) {
      if (e.button !== 0) return;
      var r = stage.getBoundingClientRect();
      st = { id: e.pointerId, x: e.clientX, y: e.clientY, r: r, moved: false,
             l: parseFloat(item.style.left) / 100 * r.width, t: parseFloat(item.style.top) / 100 * r.height };
      item.setPointerCapture(e.pointerId);
      item.style.zIndex = ++zTop;
    });
    item.addEventListener('pointermove', function (e) {
      if (!st || e.pointerId !== st.id) return;
      var dx = e.clientX - st.x, dy = e.clientY - st.y;
      if (!st.moved) {
        if (Math.hypot(dx, dy) < 5) return;
        st.moved = true;
        item.classList.add('dragging');
      }
      var x = Math.min(Math.max(st.l + dx, st.r.width * 0.08), st.r.width * 0.92);
      var y = Math.min(Math.max(st.t + dy, st.r.height * 0.10), st.r.height * 0.90);
      item.style.left = (x / st.r.width * 100) + '%';
      item.style.top = (y / st.r.height * 100) + '%';
    });
    function end(e, cancelled) {
      if (!st || e.pointerId !== st.id) return;
      var moved = st.moved;
      st = null;
      item.classList.remove('dragging');
      if (isPaper && !moved && !cancelled) EGG.openReader(item._issue, 0, item);
    }
    item.addEventListener('pointerup', function (e) { end(e, false); });
    item.addEventListener('pointercancel', function (e) { end(e, true); });
    if (isPaper) {
      item.addEventListener('keydown', function (ev) {
        if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); EGG.openReader(item._issue, 0, item); }
      });
    }
  }

  function buildMobile() {
    var first = issues[0];
    mobileCover.textContent = '';
    var im = new Image();
    setSrc(im, first, 0, 'min(calc(100vw - 32px), 528px)');
    im.alt = 'Front page of En Garde Gazette No. ' + first.number;
    var cap = document.createElement('p');
    cap.className = 'cover-cap';
    cap.innerHTML = '<small></small><span></span>';
    cap.firstChild.textContent = 'No. ' + first.number + ' · ' + EGG.fmtDate(first.date);
    cap.lastChild.textContent = first.headline;
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'cover';
    b.setAttribute('aria-label', 'Read No. ' + first.number + ': ' + first.headline);
    b.appendChild(im); b.appendChild(cap);
    b.onclick = function () { EGG.openReader(first, 0, b); };
    mobileCover.appendChild(b);

    mobileList.textContent = '';
    issues.forEach(function (iss) {
      var li = document.createElement('li');
      var meta = EGG.el('div', { 'class': 'meta', text: 'No. ' + iss.number + ' · ' + EGG.fmtDate(iss.date) });
      var h = EGG.el('div', { text: iss.headline });
      var read = EGG.el('button', { type: 'button', 'class': 'btn', text: 'Read' });
      read.onclick = function () { EGG.openReader(iss, 0, read); };
      var pdf = EGG.el('a', { 'class': 'btn ghost', href: iss.pdf, text: 'PDF' });
      li.appendChild(meta); li.appendChild(h);
      li.appendChild(EGG.el('div', { 'class': 'row' }, [read, pdf]));
      mobileList.appendChild(li);
    });
  }

  function sync() {
    if (!issues.length) return;
    if (!mq.matches && !built) { buildDesk(); built = true; }
  }

  document.getElementById('shuffle').addEventListener('click', function () { if (issues.length) buildDesk(); });

  EGG.loadIssues().then(function (list) {
    issues = list.filter(function (i) { return i.pages && i.pages.length; });
    if (!issues.length) return;
    buildMobile();
    sync();
    mq.addEventListener ? mq.addEventListener('change', sync) : mq.addListener(sync);
    EGG.openFromQuery(issues);
  }).catch(function (err) {
    var m = document.getElementById('load-error');
    m.hidden = false;
    console.error(err);
  });
})();
