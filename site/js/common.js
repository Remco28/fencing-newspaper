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
  var ZOOMS = [1, 1.5, 2, 3, 4];
  var root, view, pageBox, img, title, sub, readout, prevBtn, nextBtn, zoomIn, zoomOut, dl;
  var issue = null, page = 0, zi = 0, opener = null, onClose = null;

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
    pageBox = el('div', { 'class': 'reader-page' }, [img]);
    view = el('div', { 'class': 'reader-view', tabindex: '0', role: 'region', 'aria-label': 'Newsletter page. Arrow keys turn pages; plus and minus zoom.' }, [pageBox]);
    root = el('div', { 'class': 'reader', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'reader-title', hidden: '' }, [bar, view]);
    document.body.appendChild(root);

    prevBtn.onclick = function () { turn(-1); };
    nextBtn.onclick = function () { turn(1); };
    zoomIn.onclick = function () { setZoom(zi + 1); };
    zoomOut.onclick = function () { setZoom(zi - 1); };
    fit.onclick = function () { setZoom(0); };
    close.onclick = EGG.closeReader;
    img.addEventListener('dblclick', function () { setZoom(zi ? 0 : 2); });
    img.addEventListener('load', layout);
    window.addEventListener('resize', function () { if (root && !root.hidden) layout(); });
    root.addEventListener('keydown', key);
    root.addEventListener('mousedown', function (e) { if (e.target === root) EGG.closeReader(); });

    // drag-to-pan when zoomed (mouse; touch scrolls natively)
    var pan = null;
    view.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse' || e.button !== 0 || !zi) return;
      pan = { x: e.clientX, y: e.clientY, l: view.scrollLeft, t: view.scrollTop };
      view.setPointerCapture(e.pointerId);
      view.classList.add('panning');
    });
    view.addEventListener('pointermove', function (e) {
      if (!pan) return;
      view.scrollLeft = pan.l - (e.clientX - pan.x);
      view.scrollTop = pan.t - (e.clientY - pan.y);
    });
    function endPan() { pan = null; view.classList.remove('panning'); }
    view.addEventListener('pointerup', endPan);
    view.addEventListener('pointercancel', endPan);
  }

  function key(e) {
    if (e.key === 'Escape') { EGG.closeReader(); e.preventDefault(); }
    else if (e.key === 'Tab') { // keep focus inside the dialog
      var f = Array.prototype.filter.call(root.querySelectorAll('button, a[href], [tabindex="0"]'), function (n) { return !n.disabled; });
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { last.focus(); e.preventDefault(); }
      else if (!e.shiftKey && document.activeElement === last) { first.focus(); e.preventDefault(); }
    } else if (document.activeElement === view || document.activeElement === document.body) {
      if (e.key === 'ArrowRight' && !zi) turn(1);
      else if (e.key === 'ArrowLeft' && !zi) turn(-1);
      else if (e.key === 'PageDown') turn(1);
      else if (e.key === 'PageUp') turn(-1);
      else if (e.key === '+' || e.key === '=') setZoom(zi + 1);
      else if (e.key === '-' || e.key === '_') setZoom(zi - 1);
      else if (e.key === '0') setZoom(0);
    }
  }

  function turn(d) {
    var n = page + d;
    if (n < 0 || n >= issue.pages.length) return;
    page = n;
    show(d > 0 ? 'turn-next' : 'turn-prev');
  }

  function show(anim) {
    img.className = '';
    img.alt = issue.title + ', page ' + (page + 1) + ' of ' + issue.pages.length;
    img.src = issue.pages[page];
    if (anim && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      void img.offsetWidth;
      img.classList.add(anim);
    }
    readout.textContent = 'Page ' + (page + 1) + ' of ' + issue.pages.length;
    prevBtn.disabled = page === 0;
    nextBtn.disabled = page === issue.pages.length - 1;
    view.scrollTop = view.scrollLeft = 0;
    layout();
  }

  function layout() {
    if (!img.naturalWidth) return;
    var availW = view.clientWidth - parseFloat(getComputedStyle(view).paddingLeft) * 2;
    var availH = view.clientHeight - parseFloat(getComputedStyle(view).paddingTop) * 2;
    var ratio = img.naturalWidth / img.naturalHeight;
    var fitW = Math.min(availW, availH * ratio);
    img.style.width = Math.round(fitW * ZOOMS[zi]) + 'px';
    img.style.height = 'auto';
    view.classList.toggle('pan', zi > 0);
    zoomOut.disabled = zi === 0;
    zoomIn.disabled = zi === ZOOMS.length - 1;
  }

  function setZoom(n) {
    n = Math.max(0, Math.min(ZOOMS.length - 1, n));
    if (n === zi) return;
    var cx = (view.scrollLeft + view.clientWidth / 2) / (view.scrollWidth || 1);
    var cy = (view.scrollTop + view.clientHeight / 2) / (view.scrollHeight || 1);
    zi = n;
    layout();
    view.scrollLeft = cx * view.scrollWidth - view.clientWidth / 2;
    view.scrollTop = cy * view.scrollHeight - view.clientHeight / 2;
  }

  EGG.openReader = function (iss, startPage, trigger, closeCb) {
    build();
    issue = iss; page = startPage || 0; zi = 0; opener = trigger || document.activeElement; onClose = closeCb || null;
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
