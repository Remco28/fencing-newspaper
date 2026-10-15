/* Shared helpers + reader overlay for En Garde Gazette */
(function () {
  'use strict';

  var EGG = (window.EGG = {});

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

  /* ---------- reader ----------
     The page image fills the view at "fit"; zoom (wheel, pinch, +/-, double-click) scales it inside a
     scrolling view, and dragging pans. Once zoomed past the image's own resolution, the visible part
     of the page is re-rendered from the PDF (pdf.js, loaded only then) so the type stays sharp.
     Page changes are instant: the next image is decoded first, then swapped in. */
  var ZOOMS = [1, 1.5, 2, 3, 4, 6], ZMAX = 8;
  var root, view, pageBox, img, hi, title, sub, readout, prevBtn, nextBtn, zoomIn, zoomOut, dl;
  var issue = null, page = 0, zoom = 1, opener = null, onClose = null, showToken = 0;
  var imgCache = {};

  function loadImg(src) {
    return imgCache[src] || (imgCache[src] = new Promise(function (res) {
      var im = new Image();
      im.onload = function () { (im.decode ? im.decode() : Promise.resolve()).catch(function () {}).then(function () { res(im); }); };
      im.onerror = function () { delete imgCache[src]; res(null); };
      im.src = src;
    }));
  }

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
    hi = el('canvas', { 'aria-hidden': 'true' });
    hi.hidden = true;
    pageBox = el('div', { 'class': 'reader-page' }, [img, hi]);
    view = el('div', { 'class': 'reader-view', tabindex: '0', role: 'region', 'aria-label': 'Newsletter page. Arrow keys turn pages; plus and minus, or the scroll wheel, zoom.' }, [pageBox]);
    root = el('div', { 'class': 'reader', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'reader-title', hidden: '' }, [bar, view]);
    document.body.appendChild(root);

    prevBtn.onclick = function () { turn(-1); };
    nextBtn.onclick = function () { turn(1); };
    zoomIn.onclick = function () { stepZoom(1); };
    zoomOut.onclick = function () { stepZoom(-1); };
    fit.onclick = function () { setZoom(1); };
    close.onclick = EGG.closeReader;
    view.addEventListener('dblclick', function (e) { setZoom(zoom > 1.01 ? 1 : 2.5, e.clientX, e.clientY); });
    window.addEventListener('resize', function () { if (root && !root.hidden) layout(); });
    root.addEventListener('keydown', key);
    view.addEventListener('mousedown', function (e) { if (e.target === view && zoom <= 1.01) EGG.closeReader(); });
    view.addEventListener('scroll', sharpenSoon, { passive: true });

    // wheel / trackpad-pinch zoom, centred on the cursor
    view.addEventListener('wheel', function (e) {
      if (e.shiftKey) return; // shift+wheel scrolls sideways as usual
      e.preventDefault();
      var d = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaMode === 2 ? e.deltaY * 400 : e.deltaY;
      setZoom(zoom * Math.exp(-d * (e.ctrlKey ? 0.01 : 0.0018)), e.clientX, e.clientY);
    }, { passive: false });

    // pointer pan (mouse, touch, pen) when zoomed; two touches pinch around their midpoint; a swipe at fit turns the page
    var ptrs = {}, pan = null, pinch = null, swipe = null;
    function pts() { return Object.keys(ptrs).map(function (k) { return ptrs[k]; }); }
    function startPan(p) { pan = { x: p.x, y: p.y, l: view.scrollLeft, t: view.scrollTop }; }
    view.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'mouse' && e.button !== 0) return;
      ptrs[e.pointerId] = { x: e.clientX, y: e.clientY };
      try { view.setPointerCapture(e.pointerId); } catch (_) { /* synthetic */ }
      var p = pts();
      swipe = null;
      if (p.length === 2) {
        var mx = (p[0].x + p[1].x) / 2, my = (p[0].y + p[1].y) / 2, ir = pageBox.getBoundingClientRect();
        pinch = { d: Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y) || 1, z: zoom, fx: (mx - ir.left) / ir.width, fy: (my - ir.top) / ir.height };
        pan = null;
      } else if (zoom > 1.01) { startPan(ptrs[e.pointerId]); view.classList.add('panning'); }
      else if (p.length === 1) swipe = { x: e.clientX, y: e.clientY, t: performance.now() };
    });
    view.addEventListener('pointermove', function (e) {
      if (!ptrs[e.pointerId]) return;
      ptrs[e.pointerId] = { x: e.clientX, y: e.clientY };
      var p = pts();
      if (pinch && p.length >= 2) {
        var mx = (p[0].x + p[1].x) / 2, my = (p[0].y + p[1].y) / 2;
        zoom = clampZoom(pinch.z * Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y) / pinch.d);
        layout();
        var ir = pageBox.getBoundingClientRect();
        view.scrollLeft += ir.left + pinch.fx * ir.width - mx;
        view.scrollTop += ir.top + pinch.fy * ir.height - my;
      } else if (pan) {
        view.scrollLeft = pan.l - (e.clientX - pan.x);
        view.scrollTop = pan.t - (e.clientY - pan.y);
      }
    });
    function endPtr(e) {
      if (!ptrs[e.pointerId]) return;
      delete ptrs[e.pointerId];
      var p = pts();
      if (swipe && !p.length && zoom <= 1.01) {
        var dx = e.clientX - swipe.x, dy = e.clientY - swipe.y;
        if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.4 && performance.now() - swipe.t < 700) turn(dx < 0 ? 1 : -1);
      }
      swipe = null; pinch = null;
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
      else return;
      e.preventDefault();
    }
  }

  function turn(d) {
    var n = page + d;
    if (!issue || n < 0 || n >= issue.pages.length) return;
    page = n;
    show();
  }

  function show() {
    var tok = ++showToken, src = issue.pages[page];
    readout.textContent = (page + 1) + ' / ' + issue.pages.length;
    readout.setAttribute('aria-label', 'Page ' + (page + 1) + ' of ' + issue.pages.length);
    prevBtn.disabled = page === 0;
    nextBtn.disabled = page === issue.pages.length - 1;
    if (issue.pages[page + 1]) loadImg(issue.pages[page + 1]);
    loadImg(src).then(function () {
      if (tok !== showToken) return;
      hi.hidden = true;
      img.src = src;
      img.alt = issue.title + ', page ' + (page + 1) + ' of ' + issue.pages.length;
      zoom = 1;
      layout();
      view.scrollTop = view.scrollLeft = 0;
    });
  }

  function clampZoom(z) { return Math.max(1, Math.min(ZMAX, z)); }

  function layout() {
    if (!img.naturalWidth) return;
    var cs = getComputedStyle(view);
    var availW = view.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    var availH = view.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
    var ratio = img.naturalWidth / img.naturalHeight;
    var fitW = Math.min(availW, availH * ratio);
    var w = Math.round(fitW * zoom);
    pageBox.style.width = w + 'px';
    pageBox.style.height = Math.round(w / ratio) + 'px';
    view.classList.toggle('pan', zoom > 1.01);
    zoomOut.disabled = zoom <= 1.01;
    zoomIn.disabled = zoom >= ZMAX - 0.01;
    sharpenSoon();
  }

  // Set the zoom; keep the page point under (cx, cy) in client px fixed (defaults to the view centre).
  function setZoom(z, cx, cy) {
    z = clampZoom(z);
    if (Math.abs(z - zoom) < 1e-4) return;
    var vr = view.getBoundingClientRect();
    if (cx == null) { cx = vr.left + vr.width / 2; cy = vr.top + vr.height / 2; }
    var ir = pageBox.getBoundingClientRect();
    var fx = (cx - ir.left) / (ir.width || 1), fy = (cy - ir.top) / (ir.height || 1);
    zoom = z;
    layout();
    ir = pageBox.getBoundingClientRect();
    view.scrollLeft += ir.left + fx * ir.width - cx;
    view.scrollTop += ir.top + fy * ir.height - cy;
  }

  function stepZoom(dir) {
    var z = zoom, i;
    if (dir > 0) { for (i = 0; i < ZOOMS.length; i++) if (ZOOMS[i] > z * 1.02) return setZoom(ZOOMS[i]); setZoom(ZMAX); }
    else { for (i = ZOOMS.length - 1; i >= 0; i--) if (ZOOMS[i] < z / 1.02) return setZoom(ZOOMS[i]); }
  }

  /* ---------- sharp zoom from the PDF ---------- */
  var pdfjs = null, docs = {}, sharpT = 0, task = null;
  function sharpenSoon() { clearTimeout(sharpT); sharpT = setTimeout(sharpen, 160); }
  function lib() {
    if (!pdfjs) {
      pdfjs = import(new URL('vendor/pdfjs/pdf.min.js', document.baseURI).href).then(function (m) {
        m.GlobalWorkerOptions.workerSrc = new URL('vendor/pdfjs/pdf.worker.min.js', document.baseURI).href;
        return m;
      });
      pdfjs.catch(function () { pdfjs = null; });
    }
    return pdfjs;
  }
  function sharpen() {
    if (!root || root.hidden || !issue || !img.naturalWidth) return;
    var dpr = window.devicePixelRatio || 1, bw = pageBox.clientWidth, bh = pageBox.clientHeight;
    if (bw * dpr <= img.naturalWidth * 1.05) { hi.hidden = true; return; }
    var pr = pageBox.getBoundingClientRect(), vr = view.getBoundingClientRect();
    var x0 = Math.max(0, vr.left - pr.left), y0 = Math.max(0, vr.top - pr.top);
    var x1 = Math.min(bw, vr.right - pr.left), y1 = Math.min(bh, vr.bottom - pr.top);
    if (x1 <= x0 || y1 <= y0) return;
    var want = { iss: issue, page: page, bw: bw };
    lib().then(function (m) {
      var d = docs[want.iss.pdf] || (docs[want.iss.pdf] = m.getDocument(want.iss.pdf).promise);
      return d.then(function (doc) { return doc.getPage(want.page + 1); });
    }).then(function (pg) {
      if (issue !== want.iss || page !== want.page || pageBox.clientWidth !== want.bw) return;
      if (task) { task.cancel(); task = null; }
      var vp = pg.getViewport({ scale: bw * dpr / pg.view[2] });
      var cv = document.createElement('canvas');
      cv.width = Math.ceil((x1 - x0) * dpr); cv.height = Math.ceil((y1 - y0) * dpr);
      task = pg.render({ canvasContext: cv.getContext('2d'), viewport: vp, transform: [1, 0, 0, 1, -x0 * dpr, -y0 * dpr] });
      return task.promise.then(function () {
        task = null;
        if (issue !== want.iss || page !== want.page || pageBox.clientWidth !== want.bw) return;
        hi.width = cv.width; hi.height = cv.height;
        hi.getContext('2d').drawImage(cv, 0, 0);
        hi.style.cssText = 'left:' + x0 + 'px;top:' + y0 + 'px;width:' + (x1 - x0) + 'px;height:' + (y1 - y0) + 'px';
        hi.hidden = false;
      });
    }).catch(function () { /* cancelled, offline, or no module support: the image is still there */ });
  }

  EGG.openReader = function (iss, startPage, trigger, closeCb) {
    build();
    issue = iss; page = startPage || 0; zoom = 1; opener = trigger || document.activeElement; onClose = closeCb || null;
    title.textContent = 'En Garde Gazette No. ' + iss.number + (iss.headline ? ' — ' + iss.headline : '');
    sub.textContent = EGG.fmtDate(iss.date, true) + (iss.edition ? ' · ' + iss.edition : '');
    dl.href = iss.pdf;
    dl.setAttribute('download', iss.pdf.split('/').pop().replace(/^paper/, 'en-garde-gazette-' + iss.number));
    img.removeAttribute('src'); hi.hidden = true;
    root.hidden = false;
    document.body.classList.add('reading');
    show();
    view.focus();
  };

  EGG.closeReader = function () {
    if (!root || root.hidden) return;
    root.hidden = true;
    showToken++;
    document.body.classList.remove('reading');
    if (/[?&]read=/.test(location.search)) history.replaceState(null, '', location.pathname);
    if (opener && opener.focus) opener.focus({ preventScroll: true });
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
