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

  /* ---------- desk bounds ---------- */
  // Desk silhouette (pencils roll off past this) and the inner wood panel (papers/tin stay inside it),
  // as fractions of the stage, measured from desk.webp (1520x1012).
  var EDGE = { x0: 0.034, x1: 0.978, y0: 0.042, y1: 0.972 };
  var PANEL = { x0: 0.084, x1: 0.934, y0: 0.108, y1: 0.886 };
  var pencils = null; // created on the first desk build, so phones never download the 3D library

  // Clamp an item's centre (stage fractions) so its rotated bounding box stays inside the panel.
  function clampToPanel(item, x, y) {
    var r = stage.getBoundingClientRect(), w = item.offsetWidth, h = item.offsetHeight;
    var rot = (parseFloat(item.firstChild.style.getPropertyValue('--r')) || 0) * Math.PI / 180;
    var c = Math.abs(Math.cos(rot)), s = Math.abs(Math.sin(rot));
    var hw = (w * c + h * s) / 2 / r.width, hh = (w * s + h * c) / 2 / r.height;
    function fit(v, lo, hi, half) { return lo + half > hi - half ? (lo + hi) / 2 : Math.min(Math.max(v, lo + half), hi - half); }
    return { x: fit(x, PANEL.x0, PANEL.x1, hw), y: fit(y, PANEL.y0, PANEL.y1, hh) };
  }

  function buildDesk() {
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

    // 3D pencils: two on the first build; re-mess only re-scatters the survivors (fallen ones never return)
    (pencils = pencils || EGG.Pencils3D(stage, EDGE)).scatter();

    // keep everything inside the wood panel (items are in the DOM now, so sizes are measurable)
    all.forEach(function (n) {
      var c = clampToPanel(n, parseFloat(n.style.left) / 100, parseFloat(n.style.top) / 100);
      n.style.left = (c.x * 100) + '%'; n.style.top = (c.y * 100) + '%';
    });
  }

  function attachDrag(item) {
    var isPaper = !!item._issue, isTin = item.classList.contains('tin'), st = null;

    item.addEventListener('pointerdown', function (e) {
      if (e.button !== 0) return;
      var r = stage.getBoundingClientRect();
      st = { id: e.pointerId, x: e.clientX, y: e.clientY, r: r, moved: false,
             lx: e.clientX, rot: parseFloat(item.firstChild.style.getPropertyValue('--r')) || 0,
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
      var c = clampToPanel(item, (st.l + dx) / st.r.width, (st.t + dy) / st.r.height);
      item.style.left = (c.x * 100) + '%';
      item.style.top = (c.y * 100) + '%';
      if (isTin) { // pushing the tin sideways turns it a little
        st.rot += (e.clientX - st.lx) * 0.35;
        item.firstChild.style.setProperty('--r', st.rot + 'deg');
      }
      st.lx = e.clientX;
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
