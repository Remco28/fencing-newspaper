/* Shared helpers + reader overlay for En Garde Gazette */
(function () {
  'use strict';

  var EGG = (window.EGG = {});

  EGG.MOBILE_QUERY = '(max-width: 720px), (max-height: 460px)';

  EGG.loadIssues = function () {
    return fetch('issues.json', { cache: 'no-cache' })
      .then(function (r) { if (!r.ok) throw new Error('issues.json ' + r.status); return r.json(); })
      .then(function (list) {
        return list.slice().sort(function (a, b) {
          return a.date < b.date ? 1 : a.date > b.date ? -1 : b.number - a.number;
        });
      });
  };

  EGG.fmtDate = function (iso, long) {
    var d = new Date(iso + 'T12:00:00');
    return d.toLocaleDateString('en-US', long
      ? { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
      : { year: 'numeric', month: 'short', day: 'numeric' });
  };

  EGG.el = function (tag, attrs, children) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'text') n.textContent = attrs[k];
      else n.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { n.appendChild(c); });
    return n;
  };

  /* ---------- reader ---------- */
  var ZOOMS = [1, 1.5, 2, 3, 4], ZMAX = 5;
  var root, view, pageBox, img, title, sub, readout, prevBtn, nextBtn, zoomIn, zoomOut, dl, curl;
  var issue = null, page = 0, zoom = 1, opener = null, onClose = null, anim = null;
  var imgCache = {};

  function build() {
    if (root) return;
    var el = EGG.el;
    function btn(label, text, cls) { return el('button', { type: 'button', 'class': 'btn ' + (cls || 'ghost'), 'aria-label': label, text: text }); }
    title = el('strong', { id: 'reader-title' });
    sub = el('span');
    prevBtn = btn('Previous page', '‹ Prev');
    nextBtn = btn('Next page', 'Next ›');
    readout = el('span', { 'class': 'readout', 'aria-live': 'polite' });
    zoomOut = btn('Zoom out', '−');
    zoomIn = btn('Zoom in', '+');
    var fit = btn('Fit page to window', 'Fit');
    dl = el('a', { 'class': 'btn', text: 'Download PDF', download: '' });
    var close = btn('Close reader', 'Close ✕');
    var controls = el('div', { 'class': 'reader-controls', role: 'group', 'aria-label': 'Reader controls' },
      [prevBtn, readout, nextBtn, el('span', { 'class': 'sep' }), zoomOut, zoomIn, fit, el('span', { 'class': 'sep' }), dl, close]);
    var bar = el('div', { 'class': 'reader-bar' }, [el('div', { 'class': 'reader-heading' }, [title, sub]), controls]);
    img = el('img', { alt: '', draggable: 'false' });
    curl = el('canvas', { 'class': 'reader-curl', 'aria-hidden': 'true' });
    pageBox = el('div', { 'class': 'reader-page' }, [img, curl]);
    view = el('div', { 'class': 'reader-view', tabindex: '0', role: 'region', 'aria-label': 'Newsletter page. Arrow keys turn pages; plus and minus, or the scroll wheel, zoom.' }, [pageBox]);
    root = el('div', { 'class': 'reader', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'reader-title', hidden: '' }, [bar, view]);
    document.body.appendChild(root);

    prevBtn.onclick = function () { turn(-1); };
    nextBtn.onclick = function () { turn(1); };
    zoomIn.onclick = function () { stepZoom(1); };
    zoomOut.onclick = function () { stepZoom(-1); };
    fit.onclick = function () { setZoom(1); };
    close.onclick = EGG.closeReader;
    img.addEventListener('dblclick', function (e) { setZoom(zoom > 1.01 ? 1 : 2, e.clientX, e.clientY); });
    img.addEventListener('load', layout);
    window.addEventListener('resize', function () { if (root && !root.hidden) layout(); });
    root.addEventListener('keydown', key);
    root.addEventListener('mousedown', function (e) { if (e.target === root) EGG.closeReader(); });

    // wheel / trackpad-pinch zoom, centred on the cursor
    view.addEventListener('wheel', function (e) {
      e.preventDefault();
      var d = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaMode === 2 ? e.deltaY * 400 : e.deltaY;
      setZoom(zoom * Math.exp(-d * (e.ctrlKey ? 0.01 : 0.0018)), e.clientX, e.clientY);
    }, { passive: false });

    // pointer pan (mouse, touch, pen) when zoomed; two touches pinch-zoom around their midpoint
    var ptrs = {}, pan = null, pinch = null;
    function pts() { return Object.keys(ptrs).map(function (k) { return ptrs[k]; }); }
    function startPan(p) { pan = { x: p.x, y: p.y, l: view.scrollLeft, t: view.scrollTop }; }
    view.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'mouse' && e.button !== 0) return;
      ptrs[e.pointerId] = { x: e.clientX, y: e.clientY };
      view.setPointerCapture(e.pointerId);
      var p = pts();
      if (p.length === 2) {
        var mx = (p[0].x + p[1].x) / 2, my = (p[0].y + p[1].y) / 2, ir = img.getBoundingClientRect();
        pinch = { d: Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y) || 1, z: zoom, fx: (mx - ir.left) / ir.width, fy: (my - ir.top) / ir.height };
        pan = null;
      } else if (zoom > 1.01) { startPan(ptrs[e.pointerId]); view.classList.add('panning'); }
    });
    view.addEventListener('pointermove', function (e) {
      if (!ptrs[e.pointerId]) return;
      ptrs[e.pointerId] = { x: e.clientX, y: e.clientY };
      var p = pts();
      if (pinch && p.length >= 2) {
        var mx = (p[0].x + p[1].x) / 2, my = (p[0].y + p[1].y) / 2;
        zoom = clampZoom(pinch.z * Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y) / pinch.d);
        layout();
        var ir = img.getBoundingClientRect();
        view.scrollLeft += ir.left + pinch.fx * ir.width - mx;
        view.scrollTop += ir.top + pinch.fy * ir.height - my;
      } else if (pan) {
        view.scrollLeft = pan.l - (e.clientX - pan.x);
        view.scrollTop = pan.t - (e.clientY - pan.y);
      }
    });
    function endPtr(e) {
      delete ptrs[e.pointerId];
      var p = pts();
      pinch = null;
      if (p.length === 1 && zoom > 1.01) startPan(p[0]); else { pan = null; view.classList.remove('panning'); }
    }
    view.addEventListener('pointerup', endPtr);
    view.addEventListener('pointercancel', endPtr);
  }

  function key(e) {
    if (e.key === 'Escape') { EGG.closeReader(); e.preventDefault(); }
    else if (e.key === 'Tab') { // keep focus inside the dialog
      var f = Array.prototype.filter.call(root.querySelectorAll('button, a[href], [tabindex="0"]'), function (n) { return !n.disabled; });
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { last.focus(); e.preventDefault(); }
      else if (!e.shiftKey && document.activeElement === last) { first.focus(); e.preventDefault(); }
    } else if (document.activeElement === view || document.activeElement === document.body) {
      if (e.key === 'ArrowRight' && zoom < 1.01) turn(1);
      else if (e.key === 'ArrowLeft' && zoom < 1.01) turn(-1);
      else if (e.key === 'PageDown') turn(1);
      else if (e.key === 'PageUp') turn(-1);
      else if (e.key === '+' || e.key === '=') stepZoom(1);
      else if (e.key === '-' || e.key === '_') stepZoom(-1);
      else if (e.key === '0') setZoom(1);
    }
  }

  /* ---------- page turn: soft paper curl ----------
     The outgoing (or, going back, incoming) sheet is drawn on a canvas as vertical strips wrapped
     around a small cylinder that rolls across the page: the free edge lifts toward the viewer,
     curls over, and its paper-coloured underside lies back across the page, with shading and a
     cast shadow on the page below. Same renderer runs forwards (next) and in reverse (prev). */
  var REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)');
  function loadImg(src) {
    return imgCache[src] || (imgCache[src] = new Promise(function (res) {
      var im = new Image();
      im.onload = function () { res(im); };
      im.onerror = function () { res(null); };
      im.src = src;
    }));
  }
  function ease(t) { return t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }

  function drawCurl(top, p, w, h, dpr) {
    var pad = w, g = curl.getContext('2d');
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, w * 2, h);
    g.save(); g.translate(pad, 0);
    var R = w * (0.035 + 0.07 * Math.sin(Math.min(p, 1) * Math.PI * .5)), c = w - p * (w + R * 1.1);
    var sw = 2, i, s, th, x, nx;
    var iw = top.naturalWidth, k = iw / w; // source px per css px
    // cast shadow on the page underneath, just beyond the curl
    var tipX = c + R;
    var sh = g.createLinearGradient(tipX, 0, tipX + w * 0.11, 0);
    sh.addColorStop(0, 'rgba(0,0,0,.34)'); sh.addColorStop(1, 'rgba(0,0,0,0)');
    g.save(); g.beginPath(); g.rect(0, 0, w, h); g.clip(); g.fillStyle = sh; g.fillRect(Math.max(tipX - R * .3, 0), 0, w * 0.2 + R, h); g.restore();
    // flat part
    if (c > 0) g.drawImage(top, 0, 0, Math.min(c, w) * k, top.naturalHeight, 0, 0, Math.min(c, w), h);
    // shadow of the returning flap on the flat part
    var fl = 2 * c + Math.PI * R - w;
    if (c < w && fl < c) {
      var fs = g.createLinearGradient(fl, 0, fl - w * 0.07, 0);
      fs.addColorStop(0, 'rgba(0,0,0,.3)'); fs.addColorStop(1, 'rgba(0,0,0,0)');
      g.save(); g.beginPath(); g.rect(0, 0, Math.max(c, 0), h); g.clip(); g.fillStyle = fs; g.fillRect(fl - w * 0.07, 0, w * 0.07, h); g.restore();
    }
    // curled strips, painter's order = increasing height above the page
    for (s = Math.max(c, 0); s < w; s += sw) {
      var s1 = Math.min(s + sw, w), d0 = (s - c) / R, d1 = (s1 - c) / R, a, b, shade, back;
      if (d0 < 0) continue;
      var pr = Math.PI;
      if (d0 < pr) {
        a = c + R * Math.sin(d0); b = c + R * Math.sin(Math.min(d1, pr));
        back = d0 >= Math.PI / 2;
        var mid = (d0 + Math.min(d1, pr)) / 2;
        shade = back ? 0.95 - 0.38 * Math.sin(mid) : 1 - 0.42 * Math.sin(mid);
      } else {
        a = c - (s - c - R * pr); b = c - (s1 - c - R * pr);
        back = true; shade = 0.96;
      }
      var x0 = Math.min(a, b), ww = Math.max(Math.abs(b - a), 0.6);
      if (back) {
        g.fillStyle = 'rgb(' + Math.round(236 * shade) + ',' + Math.round(228 * shade) + ',' + Math.round(207 * shade) + ')';
        g.fillRect(x0, 0, ww + 0.5, h);
        g.globalAlpha = .07; g.drawImage(top, s * k, 0, (s1 - s) * k, top.naturalHeight, x0, 0, ww + 0.5, h); g.globalAlpha = 1;
      } else {
        g.drawImage(top, s * k, 0, (s1 - s) * k, top.naturalHeight, x0, 0, ww + 0.5, h);
        g.fillStyle = 'rgba(20,10,0,' + (1 - shade).toFixed(3) + ')'; g.fillRect(x0, 0, ww + 0.5, h);
      }
    }
    // edge of the lifted sheet
    if (c < w) {
      var ex = c < w - R * pr ? fl : c + R * Math.sin(Math.min((w - c) / R, pr));
      g.fillStyle = 'rgba(70,50,20,.35)'; g.fillRect(ex - 0.5, 0, 1, h);
    }
    g.restore();
    curl.style.opacity = p > 0.9 ? Math.max(0, (1 - p) / 0.1).toFixed(3) : '1';
  }

  function finishAnim() {
    if (!anim) return;
    var a = anim; anim = null;
    cancelAnimationFrame(a.raf);
    curl.style.display = 'none';
    img.style.visibility = '';
    if (a.done) a.done();
  }

  function turn(d) {
    var n = page + d;
    if (n < 0 || n >= issue.pages.length) return;
    finishAnim();
    var from = page, ok = zoom < 1.01 && !REDUCED.matches && img.naturalWidth && img.complete;
    page = n;
    if (!ok) { show(); return; }
    var token = {}; anim = token;
    // d>0: the old page curls away over the new one; d<0: the new page uncurls back over the old one
    Promise.all([loadImg(issue.pages[from]), loadImg(issue.pages[n])]).then(function (r) {
      if (anim !== token) return;
      var top = d > 0 ? r[0] : r[1];
      if (!top) { anim = null; show(); return; }
      var w = img.clientWidth, h = img.clientHeight, dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      curl.width = Math.round(w * 2 * dpr); curl.height = Math.round(h * dpr);
      curl.style.cssText = 'display:block;width:' + (w * 2) + 'px;height:' + h + 'px;left:' + (-w) + 'px;top:' + img.offsetTop + 'px';
      readout.textContent = 'Page ' + (page + 1) + ' of ' + issue.pages.length;
      prevBtn.disabled = page === 0; nextBtn.disabled = page === issue.pages.length - 1;
      img.alt = issue.title + ', page ' + (page + 1) + ' of ' + issue.pages.length;
      var t0 = performance.now(), dur = 720;
      if (d > 0) { img.src = issue.pages[n]; } // new page sits underneath while the old one peels
      token.done = function () { if (d < 0) img.src = issue.pages[n]; };
      (function step(now) {
        var t = Math.min((now - t0) / dur, 1), e = ease(t), p = d > 0 ? e : 1 - e;
        drawCurl(top, p, w, h, dpr);
        if (t < 1) token.raf = requestAnimationFrame(step); else finishAnim();
      })(t0);
    });
  }

  function show() {
    finishAnim();
    img.alt = issue.title + ', page ' + (page + 1) + ' of ' + issue.pages.length;
    img.src = issue.pages[page];
    readout.textContent = 'Page ' + (page + 1) + ' of ' + issue.pages.length;
    prevBtn.disabled = page === 0;
    nextBtn.disabled = page === issue.pages.length - 1;
    view.scrollTop = view.scrollLeft = 0;
    layout();
  }

  function clampZoom(z) { return Math.max(1, Math.min(ZMAX, z)); }

  function layout() {
    if (!img.naturalWidth) return;
    var cs = getComputedStyle(view);
    var availW = view.clientWidth - parseFloat(cs.paddingLeft) * 2;
    var availH = view.clientHeight - parseFloat(cs.paddingTop) * 2;
    var ratio = img.naturalWidth / img.naturalHeight;
    var fitW = Math.min(availW, availH * ratio);
    img.style.width = Math.round(fitW * zoom) + 'px';
    img.style.height = 'auto';
    view.classList.toggle('pan', zoom > 1.01);
    zoomOut.disabled = zoom <= 1.01;
    zoomIn.disabled = zoom >= ZMAX - 0.01;
  }

  // Set the zoom; keep the page point under (cx, cy) in client px fixed (defaults to the view centre).
  function setZoom(z, cx, cy) {
    z = clampZoom(z);
    if (Math.abs(z - zoom) < 1e-4) return;
    finishAnim();
    var vr = view.getBoundingClientRect();
    if (cx == null) { cx = vr.left + vr.width / 2; cy = vr.top + vr.height / 2; }
    var ir = img.getBoundingClientRect();
    var fx = (cx - ir.left) / (ir.width || 1), fy = (cy - ir.top) / (ir.height || 1);
    zoom = z;
    layout();
    ir = img.getBoundingClientRect();
    view.scrollLeft += ir.left + fx * ir.width - cx;
    view.scrollTop += ir.top + fy * ir.height - cy;
  }

  function stepZoom(dir) {
    var z = zoom, i;
    if (dir > 0) { for (i = 0; i < ZOOMS.length; i++) if (ZOOMS[i] > z * 1.02) return setZoom(ZOOMS[i]); }
    else { for (i = ZOOMS.length - 1; i >= 0; i--) if (ZOOMS[i] < z / 1.02) return setZoom(ZOOMS[i]); }
  }

  EGG.openReader = function (iss, startPage, trigger, closeCb) {
    build();
    finishAnim(); issue = iss; page = startPage || 0; zoom = 1; opener = trigger || document.activeElement; onClose = closeCb || null;
    title.textContent = 'En Garde Gazette No. ' + iss.number + (iss.headline ? ' — ' + iss.headline : '');
    sub.textContent = EGG.fmtDate(iss.date, true) + (iss.edition ? ' · ' + iss.edition : '');
    dl.href = iss.pdf;
    dl.setAttribute('download', iss.pdf.split('/').pop());
    root.hidden = false;
    document.body.classList.add('reading');
    show();
    view.focus();
  };

  EGG.closeReader = function () {
    if (!root || root.hidden) return;
    root.hidden = true;
    document.body.classList.remove('reading');
    if (/[?&]read=/.test(location.search)) history.replaceState(null, '', location.pathname);
    if (opener && opener.focus) opener.focus();
    if (onClose) onClose();
  };

  // ?read=N opens issue N directly (also the no-JS-link target from the archive)
  EGG.openFromQuery = function (issues) {
    var m = /[?&]read=(\d+)/.exec(location.search);
    if (!m) return;
    var n = +m[1];
    var iss = issues.filter(function (i) { return i.number === n; })[0];
    if (iss) EGG.openReader(iss, 0, null);
  };
})();
