/* En Garde Gazette desk engine.
   One small rigid-body world for everything that lies on the desk: papers, the paperclip tin, pencils,
   and whatever props come later. Each kind of object is a registry entry (EGG.Desk.register) that only
   describes what is different about it: how it looks, how heavy and slippery it is, whether it collides,
   whether it is kept on the desk or can tip over the edge, and what a tap does. Dragging, flicking,
   one-finger "towing" rotation, two-finger twist, wheel rotation, collisions, edge bounces, tipping and
   falling are shared.
   World units are desk-photo pixels (desk.webp is 1520x1012); about 14 units = 1 cm. */
(function () {
  'use strict';
  var EGG = (window.EGG = window.EGG || {});

  var G = 14000;                  // gravity, units/s^2
  var SUB = 1 / 240;              // physics substep
  var TAP_PX = 7, TAP_MS = 550;   // a press that moves less than this (screen px) and is this short is a tap
  var KINDS = {};

  var BASE = {
    layer: 'prop',        // 'paper': flat sheets, always under props | 'prop': things that sit on top
    solid: false,         // collides with other solid bodies
    edge: 'contain',      // 'contain': bounces off the desk rim | 'fall': tips over the rim and drops
    density: 1,           // mass = density * w * h (only ratios matter)
    slide: 900,           // sliding friction, as a deceleration (units/s^2)
    spin: 8,              // spin friction, as an angular deceleration (rad/s^2)
    restitution: 0.3,     // bounce off the rim and other bodies
    tow: 0.8,             // 0..1: how much a one-finger drag off-centre swings the body round behind the finger
    maxSpeed: 4200,
    maxSpin: 40,
    hitPad: 0,            // extra grab margin, screen px (thin things)
    lift: 1.02,           // scale while held
    focusable: false,     // keyboard focus: Enter/Space = tap, arrows move, [ ] rotate
    shadow: { x: 3, y: 5, blur: 5, opacity: 0.45, radius: 2, inset: 0, liftX: 12, liftY: 18, liftBlur: 16, liftOpacity: 0.35 }
    /* optional hooks, all called with (body, desk):
         build(b, opts, desk)  create b.w, b.h and the content of b.face (required)
         friction(b, dt)       replace the default isotropic friction; return true while still settling
         draw(b, desk)         called before each render (custom-drawn faces, e.g. a canvas)
         onScale(b, desk)      the on-screen scale or view rotation changed
         onDrag(b, dx, dy)     the body was moved by the user by (dx, dy) world units
         onTap(b, desk)        tap / click / Enter
         onGone(b, desk)       it fell off the desk and was removed */
  };

  function merge(a, b) { var o = {}, k; for (k in a) o[k] = a[k]; for (k in b || {}) o[k] = b[k]; return o; }
  function el(tag, cls) { var n = document.createElement(tag); if (cls) n.className = cls; return n; }
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function toward0(v, d) { return v > d ? v - d : v < -d ? v + d : 0; }
  function angDiff(a, b) { var d = b - a; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return d; }

  /* ---------- 4x4 matrices, column-major (CSS matrix3d order) ---------- */
  function M4() { return [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]; }
  function mul(a, b) {
    var o = new Array(16), c, r, k, s;
    for (c = 0; c < 4; c++) for (r = 0; r < 4; r++) {
      for (s = 0, k = 0; k < 4; k++) s += a[k * 4 + r] * b[c * 4 + k];
      o[c * 4 + r] = s;
    }
    return o;
  }
  function tr(x, y, z) { var m = M4(); m[12] = x; m[13] = y; m[14] = z; return m; }
  function rotZ(a) { var c = Math.cos(a), s = Math.sin(a), m = M4(); m[0] = c; m[1] = s; m[4] = -s; m[5] = c; return m; }
  function rotAxis(x, y, z, t) {
    var c = Math.cos(t), s = Math.sin(t), C = 1 - c, m = M4();
    m[0] = c + x * x * C;     m[4] = x * y * C - z * s; m[8] = x * z * C + y * s;
    m[1] = y * x * C + z * s; m[5] = c + y * y * C;     m[9] = y * z * C - x * s;
    m[2] = z * x * C - y * s; m[6] = z * y * C + x * s; m[10] = c + z * z * C;
    return m;
  }
  function css3d(m) { return 'matrix3d(' + m.map(function (v) { return +v.toFixed(6); }).join(',') + ')'; }

  // Clip the w x h rectangle to the half-plane f(x, y) = ax + by + c < 0 (Sutherland-Hodgman, one edge).
  function clipRect(w, h, a, b, c, keepNeg) {
    var pts = [[0, 0], [w, 0], [w, h], [0, h]], out = [], i;
    function f(p) { var v = a * p[0] + b * p[1] + c; return keepNeg ? v : -v; }
    for (i = 0; i < 4; i++) {
      var p = pts[i], q = pts[(i + 1) % 4], fp = f(p), fq = f(q);
      if (fp <= 0) out.push(p);
      if ((fp <= 0) !== (fq <= 0)) { var t = fp / (fp - fq); out.push([p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t]); }
    }
    if (out.length < 3) return 'polygon(0 0, 0 0, 0 0)';
    return 'polygon(' + out.map(function (p) { return p[0].toFixed(1) + 'px ' + p[1].toFixed(1) + 'px'; }).join(',') + ')';
  }

  /* ---------- the desk ---------- */
  function Desk(viewport, o) {
    var self = this;
    this.vp = viewport;
    this.size = o.size;
    this.bounds = o.bounds;               // the wood surface, world units
    this.P = o.perspective || 2200;       // camera height above the desk (for things that fall)
    this.floor = o.floor || 1100;         // how far below the desk the floor is
    this.bodies = [];
    this.zc = { paper: 10, prop: 10 };
    this.ptrs = {};
    this.scale = 1; this.rot = 0; this.portrait = false;
    this.running = false;
    this.onLayout = o.onLayout || null;

    var b = this.bounds;
    this.ox = (b.x0 + b.x1) / 2; this.oy = (b.y0 + b.y1) / 2;
    this.proj = mul(tr(this.ox, this.oy, 0), mul((function (P) { var m = M4(); m[11] = -1 / P; return m; })(this.P), tr(-this.ox, -this.oy, 0)));

    var scene = (this.scene = el('div', 'scene'));
    scene.style.width = o.size.w + 'px'; scene.style.height = o.size.h + 'px';
    this.under = el('div', 'layer layer-under');
    var img = el('img', 'desk-img');
    img.src = o.image; img.alt = ''; img.draggable = false; img.width = o.size.w; img.height = o.size.h;
    this.layers = { paper: el('div', 'layer layer-paper'), prop: el('div', 'layer layer-prop') };
    var fx = el('div', 'desk-fx');
    fx.style.cssText = 'left:' + b.x0 + 'px;top:' + b.y0 + 'px;width:' + (b.x1 - b.x0) + 'px;height:' + (b.y1 - b.y0) + 'px';
    [this.under, img, this.layers.paper, this.layers.prop, fx].forEach(function (n) { scene.appendChild(n); });
    viewport.appendChild(scene);

    this.layout();
    window.addEventListener('resize', function () { self.layout(); });
    this._bindPointers();
    this._tick = this._tick.bind(this);
  }

  Desk.register = function (name, def) {
    def = merge(BASE, def);
    def.shadow = def.shadow === false ? false : merge(BASE.shadow, def.shadow);
    def.name = name;
    KINDS[name] = def;
    return def;
  };
  Desk.kinds = KINDS;
  Desk.G = G;

  /* A ready-made definition for a photographed prop: a transparent image, with `box` giving the
     part of the image that is the object itself (in image px) and `width` its size on the desk. */
  Desk.imageProp = function (o) {
    var box = o.box || [0, 0, o.imageWidth, o.imageHeight];
    var spec = merge({ layer: 'prop', solid: true }, o);
    spec.build = function (b) {
      var k = o.width / (box[2] - box[0]);
      b.w = o.width; b.h = (box[3] - box[1]) * k;
      var im = el('img');
      im.src = o.src; im.alt = ''; im.draggable = false; im.decoding = 'async';
      im.style.cssText = 'position:absolute;max-width:none;left:' + (-box[0] * k) + 'px;top:' + (-box[1] * k) + 'px;width:' + (o.imageWidth * k) + 'px;height:' + (o.imageHeight * k) + 'px';
      b.face.appendChild(im);
      if (o.build) o.build(b);
    };
    return spec;
  };

  var D = Desk.prototype;

  /* ---------- view: fit the wood to the viewport; tall screens turn the desk sideways ---------- */
  D.layout = function () {
    var W = this.vp.clientWidth, H = this.vp.clientHeight;
    if (!W || !H) return;
    var b = this.bounds, m = 10, bw = b.x1 - b.x0 + 2 * m, bh = b.y1 - b.y0 + 2 * m;
    var portrait = W / H < 0.95, s, tx, ty;
    if (portrait) {
      s = Math.min(W / bh, H / bw);
      tx = (W - bh * s) / 2 + (b.y1 + m) * s;
      ty = (H - bw * s) / 2 - (b.x0 - m) * s;
    } else {
      s = Math.min(W / bw, H / bh);
      tx = (W - bw * s) / 2 - (b.x0 - m) * s;
      ty = (H - bh * s) / 2 - (b.y0 - m) * s;
    }
    var changed = s !== this.scale || portrait !== this.portrait;
    this.scale = s; this.tx = tx; this.ty = ty; this.portrait = portrait; this.rot = portrait ? Math.PI / 2 : 0;
    this.scene.style.transform = 'translate(' + tx + 'px,' + ty + 'px)' + (portrait ? ' rotate(90deg)' : '') + ' scale(' + s + ')';
    // light comes from the screen's upper left whichever way the desk is turned
    var lx = -0.45, ly = -0.55, c = Math.cos(-this.rot), sn = Math.sin(-this.rot);
    this.light = { x: lx * c - ly * sn, y: lx * sn + ly * c, z: 0.85 };
    var n = Math.hypot(this.light.x, this.light.y, this.light.z);
    this.light.x /= n; this.light.y /= n; this.light.z /= n;
    var self = this;
    if (changed) this.bodies.forEach(function (bd) { if (bd.def.onScale) bd.def.onScale(bd, self); self._render(bd); });
    if (this.onLayout && changed) this.onLayout(this);
  };

  // screen-space offset (px) -> world vector; used for light and shadows
  D.screenVec = function (x, y) { var c = Math.cos(-this.rot), s = Math.sin(-this.rot); return { x: x * c - y * s, y: x * s + y * c }; };
  // angle (world) that looks upright on screen
  D.upright = function () { return -this.rot; };

  D.toWorld = function (cx, cy) {
    var r = this.vp.getBoundingClientRect(), lx = cx - r.left - this.tx, ly = cy - r.top - this.ty, s = this.scale;
    return this.portrait ? { x: ly / s, y: -lx / s } : { x: lx / s, y: ly / s };
  };

  /* ---------- bodies ---------- */
  D.add = function (kind, opts) {
    opts = opts || {};
    var def = KINDS[kind];
    if (!def) throw new Error('Unknown desk object kind: ' + kind);
    var b = {
      kind: kind, def: def, data: opts, desk: this,
      x: opts.x || 0, y: opts.y || 0, a: opts.a || 0, vx: 0, vy: 0, va: 0,
      w: 10, h: 10, mode: 'rest', held: null, lift: opts.drop != null ? 2.4 : 0, dropAt: 0, hist: []
    };
    b.el = el('div', 'obj obj-' + kind);
    if (def.shadow) { b.shadow = el('div', 'obj-shadow'); b.el.appendChild(b.shadow); }
    b.face = el('div', 'obj-face');
    b.el.appendChild(b.face);
    def.build(b, opts, this);
    b.face.style.width = b.w + 'px'; b.face.style.height = b.h + 'px';
    if (b.shadow) {
      var sh = def.shadow, ins = sh.inset || 0;
      b.shadow.style.width = (b.w - 2 * ins) + 'px'; b.shadow.style.height = (b.h - 2 * ins) + 'px';
      b.shadow.style.borderRadius = sh.radius + 'px';
    }
    b.m = def.density * b.w * b.h;
    b.I = b.m * (b.w * b.w + b.h * b.h) / 12;
    if (def.focusable) {
      b.face.tabIndex = 0;
      b.face.setAttribute('role', 'button');
      if (opts.label) b.face.setAttribute('aria-label', opts.label);
      this._bindKeys(b);
    } else b.el.setAttribute('aria-hidden', 'true');
    if (opts.drop != null) { b.dropAt = performance.now() + opts.drop * 1000; b.el.style.animationDelay = opts.drop + 's'; b.el.classList.add('dropping'); }
    this.bodies.push(b);
    this._front(b);
    this.layers[def.layer].appendChild(b.el);
    if (def.onScale) def.onScale(b, this);
    this.constrain(b);
    this._render(b);
    this.wake();
    return b;
  };

  D.remove = function (b) {
    b.mode = 'gone';
    if (b.el.parentNode) b.el.parentNode.removeChild(b.el);
    if (b.under && b.under.parentNode) b.under.parentNode.removeChild(b.under);
    var i = this.bodies.indexOf(b);
    if (i >= 0) this.bodies.splice(i, 1);
    for (var id in this.ptrs) if (this.ptrs[id].body === b) delete this.ptrs[id];
  };

  D.clear = function () { while (this.bodies.length) this.remove(this.bodies[0]); this.ptrs = {}; };

  D._front = function (b) { b.z = ++this.zc[b.def.layer]; b.el.style.zIndex = b.z; };

  function axes(b) { var c = Math.cos(b.a), s = Math.sin(b.a); return { ux: c, uy: s, vx: -s, vy: c }; }
  function cornersOf(b) {
    var A = axes(b), hw = b.w / 2, hh = b.h / 2, out = [], i, sx, sy;
    for (i = 0; i < 4; i++) {
      sx = i === 0 || i === 3 ? -1 : 1; sy = i < 2 ? -1 : 1;
      out.push({ x: b.x + A.ux * hw * sx + A.vx * hh * sy, y: b.y + A.uy * hw * sx + A.vy * hh * sy });
    }
    return out;
  }
  function inside(b, x, y, pad) {
    var c = Math.cos(b.a), s = Math.sin(b.a), dx = x - b.x, dy = y - b.y;
    return Math.abs(dx * c + dy * s) <= b.w / 2 + pad && Math.abs(-dx * s + dy * c) <= b.h / 2 + pad;
  }

  // Does b overlap any solid body (placement helper)?
  D.overlaps = function (b, pad) {
    var self = this;
    return this.bodies.some(function (o) { return o !== b && o.def.solid && b.def.solid && sat(b, o, pad || 0); });
  };

  // Keep the body on the wood: contained kinds keep their whole outline on it; falling kinds keep their centre on it.
  D.constrain = function (b) {
    var B = this.bounds;
    if (b.def.edge === 'fall') {
      var mg = Math.min(b.w, b.h) / 2 + 2;
      b.x = clamp(b.x, B.x0 + mg, B.x1 - mg); b.y = clamp(b.y, B.y0 + mg, B.y1 - mg);
      return;
    }
    var cs = cornersOf(b), minx = Infinity, maxx = -Infinity, miny = Infinity, maxy = -Infinity;
    cs.forEach(function (p) { minx = Math.min(minx, p.x); maxx = Math.max(maxx, p.x); miny = Math.min(miny, p.y); maxy = Math.max(maxy, p.y); });
    if (maxx - minx > B.x1 - B.x0) b.x += (B.x0 + B.x1) / 2 - (minx + maxx) / 2;
    else if (minx < B.x0) b.x += B.x0 - minx; else if (maxx > B.x1) b.x -= maxx - B.x1;
    if (maxy - miny > B.y1 - B.y0) b.y += (B.y0 + B.y1) / 2 - (miny + maxy) / 2;
    else if (miny < B.y0) b.y += B.y0 - miny; else if (maxy > B.y1) b.y -= maxy - B.y1;
  };

  D.hit = function (x, y, coarse) {
    var list = this.bodies.slice().sort(function (p, q) {
      var lp = p.def.layer === 'prop' ? 1 : 0, lq = q.def.layer === 'prop' ? 1 : 0;
      return lq - lp || q.z - p.z;
    });
    var self = this;
    // exact hits first; then the generous margin for thin things (pencils) so they stay easy to pick up
    for (var pass = 0; pass < 2; pass++) for (var i = 0; i < list.length; i++) {
      var b = list[i];
      if (b.mode === 'fall' || b.mode === 'gone') continue;
      var pad = pass ? (b.def.hitPad * (coarse ? 1.6 : 1)) / self.scale : 0;
      if (pass && !pad) continue;
      if (inside(b, x, y, pad)) return b;
    }
    return null;
  };

  /* ---------- pointer interaction ---------- */
  D._bindPointers = function () {
    var self = this, vp = this.vp;

    vp.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'mouse' && e.button !== 0) return;
      var p = self.toWorld(e.clientX, e.clientY), coarse = e.pointerType !== 'mouse';
      var b = self.hit(p.x, p.y, coarse);
      if (!b) { // a second finger on bare wood twists whatever the first finger holds
        var held = self.bodies.filter(function (q) { return q.held && q.held.ids.length === 1 && self.ptrs[q.held.ids[0]].type !== 'mouse'; });
        if (!held.length || e.pointerType === 'mouse') return;
        b = held[held.length - 1];
      }
      e.preventDefault();
      try { vp.setPointerCapture(e.pointerId); } catch (_) { /* synthetic pointers */ }
      self.ptrs[e.pointerId] = { body: b, x: p.x, y: p.y, sx: e.clientX, sy: e.clientY, t0: performance.now(), travel: 0, type: e.pointerType };
      self._grab(b, e.pointerId);
    });

    vp.addEventListener('pointermove', function (e) {
      var pt = self.ptrs[e.pointerId];
      if (!pt) {
        if (e.pointerType === 'mouse' && !e.buttons) {
          var q = self.toWorld(e.clientX, e.clientY), hb = self.hit(q.x, q.y, false);
          vp.style.cursor = hb ? 'grab' : '';
        }
        return;
      }
      var evs = e.getCoalescedEvents ? e.getCoalescedEvents() : [];
      var last = evs.length ? evs[evs.length - 1] : e;
      pt.travel = Math.max(pt.travel, Math.hypot(last.clientX - pt.sx, last.clientY - pt.sy));
      var p = self.toWorld(last.clientX, last.clientY);
      pt.x = p.x; pt.y = p.y;
      self._drag(pt.body);
    });

    function up(e, cancel) {
      var pt = self.ptrs[e.pointerId];
      if (!pt) return;
      delete self.ptrs[e.pointerId];
      var b = pt.body, h = b.held;
      if (!h) return;
      h.ids = h.ids.filter(function (id) { return id !== +e.pointerId; });
      var tap = !cancel && !h.multi && pt.travel < TAP_PX && performance.now() - pt.t0 < TAP_MS;
      if (h.ids.length) { self._regrip(b); return; }
      self._release(b, tap);
      if (tap && b.def.onTap) b.def.onTap(b, self);
    }
    vp.addEventListener('pointerup', function (e) { up(e, false); });
    vp.addEventListener('pointercancel', function (e) { up(e, true); });
    vp.addEventListener('lostpointercapture', function (e) { if (self.ptrs[e.pointerId]) up(e, true); });

    // wheel over an object turns it
    vp.addEventListener('wheel', function (e) {
      var p = self.toWorld(e.clientX, e.clientY), b = self.hit(p.x, p.y, false);
      if (!b) return;
      e.preventDefault();
      var d = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaY;
      if (b.held) return;
      b.a += clamp(d, -120, 120) * 0.0035;
      self._front(b);
      self.constrain(b);
      b.mode = b.mode === 'rest' ? 'move' : b.mode;
      self._render(b); self.wake();
    }, { passive: false });
  };

  D._grab = function (b, id) {
    if (b.mode === 'tip') { // caught it on the way over the edge
      var t = b.tip;
      b.mode = 'move'; b.tip = null;
      b.x = t.nx * (t.c - 2) + t.tx * t.s; b.y = t.ny * (t.c - 2) + t.ty * t.s;
      b.x -= t.nx * Math.min(b.w, b.h) / 2;
      this._dropUnder(b);
    }
    if (!b.held) b.held = { ids: [], multi: false };
    if (b.held.ids.indexOf(+id) < 0) b.held.ids.push(+id);
    if (b.held.ids.length > 1) b.held.multi = true;
    b.vx = b.vy = b.va = 0; b.mode = 'move';
    b.hist = [{ t: performance.now(), x: b.x, y: b.y, a: b.a }];
    b.kx = b.x; b.ky = b.y; b.ka = b.a;
    b.el.classList.add('held');
    this._front(b);
    this._regrip(b);
    this.wake();
  };

  D._regrip = function (b) {
    var h = b.held, ids = h.ids, ptrs = this.ptrs, c = Math.cos(-b.a), s = Math.sin(-b.a);
    function local(x, y) { var dx = x - b.x, dy = y - b.y; return { x: dx * c - dy * s, y: dx * s + dy * c }; }
    if (ids.length === 1) {
      var p = ptrs[ids[0]];
      h.local = local(p.x, p.y); h.two = null;
    } else {
      var p1 = ptrs[ids[0]], p2 = ptrs[ids[1]];
      h.two = { lm: local((p1.x + p2.x) / 2, (p1.y + p2.y) / 2), th0: Math.atan2(p2.y - p1.y, p2.x - p1.x), a0: b.a };
    }
  };

  D._drag = function (b) {
    var h = b.held;
    if (!h) return;
    var ox = b.x, oy = b.y, P, c, s, lm;
    if (h.two) {
      var p1 = this.ptrs[h.ids[0]], p2 = this.ptrs[h.ids[1]];
      var th = Math.atan2(p2.y - p1.y, p2.x - p1.x);
      b.a = h.two.a0 + angDiff(h.two.th0, th);
      P = { x: (p1.x + p2.x) / 2, y: (p1.y + p2.y) / 2 }; lm = h.two.lm;
    } else {
      P = this.ptrs[h.ids[0]]; lm = h.local;
      // towing: grabbed off-centre, the body swings round to trail behind the finger, like a sheet pushed by one fingertip
      c = Math.cos(b.a); s = Math.sin(b.a);
      var gx = b.x + lm.x * c - lm.y * s, gy = b.y + lm.x * s + lm.y * c;
      var rl = Math.hypot(lm.x, lm.y), R = Math.hypot(b.w, b.h) / 2;
      var f = clamp((rl / R - 0.12) / 0.45, 0, 1), wgt = b.def.tow * f * f * (3 - 2 * f);
      if (wgt > 0) {
        var ax = b.x - gx, ay = b.y - gy, bx = b.x - P.x, by = b.y - P.y;
        var dth = Math.atan2(ax * by - ay * bx, ax * bx + ay * by);
        b.a += clamp(dth, -0.5, 0.5) * wgt;
      }
    }
    c = Math.cos(b.a); s = Math.sin(b.a);
    b.x = P.x - (lm.x * c - lm.y * s);
    b.y = P.y - (lm.x * s + lm.y * c);
    this.constrain(b);
    var now = performance.now();
    b.hist.push({ t: now, x: b.x, y: b.y, a: b.a });
    while (b.hist.length > 2 && now - b.hist[0].t > 110) b.hist.shift();
    if (b.def.onDrag) b.def.onDrag(b, b.x - ox, b.y - oy);
    this._render(b);
    this.wake();
  };

  D._release = function (b, tap) {
    var now = performance.now(), hs = b.hist, last = hs[hs.length - 1], first = hs[0];
    b.held = null;
    b.el.classList.remove('held');
    b.vx = b.vy = b.va = 0;
    if (!tap && hs.length > 1 && now - last.t < 70) {
      var dt = Math.max((last.t - first.t) / 1000, 1 / 120);
      b.vx = (last.x - first.x) / dt; b.vy = (last.y - first.y) / dt; b.va = angDiff(first.a, last.a) / dt;
      var sp = Math.hypot(b.vx, b.vy), mx = b.def.maxSpeed;
      if (sp > mx) { b.vx *= mx / sp; b.vy *= mx / sp; }
      b.va = clamp(b.va, -b.def.maxSpin, b.def.maxSpin);
    }
    b.mode = 'move';
    this.wake();
  };

  D._bindKeys = function (b) {
    var self = this;
    b.face.addEventListener('keydown', function (e) {
      var k = e.key, step = e.shiftKey ? 60 : 18, u;
      if (k === 'Enter' || k === ' ') { e.preventDefault(); if (b.def.onTap) b.def.onTap(b, self); return; }
      var mv = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[k];
      if (mv) { u = self.screenVec(mv[0] * step, mv[1] * step); b.x += u.x; b.y += u.y; }
      else if (k === '[' || k === ']') b.a += (k === ']' ? 1 : -1) * (e.shiftKey ? 0.4 : 0.09);
      else return;
      e.preventDefault();
      self._front(b); self.constrain(b); self._render(b);
    });
  };

  /* ---------- physics ---------- */
  D.wake = function () {
    if (this.running) return;
    this.running = true; this.last = performance.now();
    requestAnimationFrame(this._tick);
  };

  D._tick = function (now) {
    var dt = Math.min((now - this.last) / 1000, 1 / 30), self = this;
    this.last = now;
    if (dt <= 0) { requestAnimationFrame(this._tick); return; }
    this.bodies.forEach(function (b) { // velocity of held bodies, so they can shove others
      if (!b.held) return;
      b.vx = (b.x - b.kx) / dt; b.vy = (b.y - b.ky) / dt; b.va = angDiff(b.ka, b.a) / dt;
      b.kx = b.x; b.ky = b.y; b.ka = b.a;
    });
    var n = Math.ceil(dt / SUB), h = dt / n, i;
    for (i = 0; i < n; i++) this._step(h);
    var active = false;
    this.bodies.slice().forEach(function (b) {
      if (b.mode === 'gone') return;
      var target = b.held ? 1 : 0, dl = 0;
      if (b.lift !== target && now >= b.dropAt) {
        var nl = b.lift + (target - b.lift) * Math.min(1, dt * (target ? 14 : 9));
        if (Math.abs(nl - target) < 0.004) nl = target;
        dl = nl - b.lift; b.lift = nl;
      }
      if (b.held || b.mode !== 'rest' || dl || b.lift !== target) active = true;
      if (b.mode !== 'rest' || b.held || dl) self._render(b);
    });
    if (active) requestAnimationFrame(this._tick); else this.running = false;
  };

  D._step = function (h) {
    var bs = this.bodies, i, j, b;
    for (i = 0; i < bs.length; i++) {
      b = bs[i];
      if (b.held || b.mode === 'rest' || b.mode === 'gone') continue;
      if (b.mode === 'tip') { this._stepTip(b, h); continue; }
      if (b.mode === 'fall') { this._stepFall(b, h); continue; }
      var busy;
      if (b.def.friction) busy = b.def.friction(b, h);
      else {
        var sp = Math.hypot(b.vx, b.vy);
        if (sp > 0) { var ns = Math.max(0, sp - b.def.slide * h); b.vx *= ns / sp; b.vy *= ns / sp; }
        b.va = toward0(b.va, b.def.spin * h);
      }
      b.x += b.vx * h; b.y += b.vy * h; b.a += b.va * h;
      if (b.def.edge === 'contain') this._rim(b); else this._checkTip(b);
      if (!busy && b.mode === 'move' && Math.abs(b.vx) + Math.abs(b.vy) < 1.5 && Math.abs(b.va) < 0.01) { b.vx = b.vy = b.va = 0; b.mode = 'rest'; }
    }
    for (i = 0; i < bs.length; i++) for (j = i + 1; j < bs.length; j++) {
      var A = bs[i], B = bs[j];
      if (!A.def.solid || !B.def.solid) continue;
      if ((A.mode === 'rest' && !A.held) && (B.mode === 'rest' && !B.held)) continue;
      if (A.mode === 'tip' || A.mode === 'fall' || B.mode === 'tip' || B.mode === 'fall') continue;
      this._collide(A, B);
    }
  };

  function impulse(b, px, py, nx, ny, e, mu) { // push body b at point p along inward normal n
    var rx = px - b.x, ry = py - b.y, vpx = b.vx - b.va * ry, vpy = b.vy + b.va * rx, vn = vpx * nx + vpy * ny;
    if (vn >= 0) return;
    var im = 1 / b.m, iI = 1 / b.I, rn = rx * ny - ry * nx;
    var j = -(1 + e) * vn / (im + rn * rn * iI);
    var tx = -ny, ty = nx, vt = vpx * tx + vpy * ty, rt = rx * ty - ry * tx;
    var jt = clamp(-vt / (im + rt * rt * iI), -mu * j, mu * j);
    b.vx += (j * nx + jt * tx) * im; b.vy += (j * ny + jt * ty) * im;
    b.va += (rn * j + rt * jt) * iI;
  }

  // bounce off the rim of the desk
  D._rim = function (b) {
    var B = this.bounds, cs = cornersOf(b), sides = [
      { nx: 1, ny: 0, d: function (p) { return B.x0 - p.x; } }, { nx: -1, ny: 0, d: function (p) { return p.x - B.x1; } },
      { nx: 0, ny: 1, d: function (p) { return B.y0 - p.y; } }, { nx: 0, ny: -1, d: function (p) { return p.y - B.y1; } }];
    var e = b.def.restitution;
    sides.forEach(function (sd) {
      var best = null, bd = 0;
      cs.forEach(function (p) { var d = sd.d(p); if (d > bd) { bd = d; best = p; } });
      if (!best) return;
      b.x += sd.nx * bd; b.y += sd.ny * bd;
      impulse(b, best.x + sd.nx * bd, best.y + sd.ny * bd, sd.nx, sd.ny, e, 0.25);
      cs = cornersOf(b);
    });
  };

  /* Tipping over the rim: once the centre of mass passes the edge, the body pivots about the rim
     line under gravity (rod about a pivot), keeps sliding outward, and leaves the rim when its inner
     end gets past it. Then it is in free fall, tumbling, until it hits the floor out of sight. */
  D._checkTip = function (b) {
    var B = this.bounds, over = [[b.x - B.x1, 1, 0, B.x1], [B.x0 - b.x, -1, 0, -B.x0], [b.y - B.y1, 0, 1, B.y1], [B.y0 - b.y, 0, -1, -B.y0]];
    var best = null;
    over.forEach(function (o) { if (o[0] > 0 && (!best || o[0] > best[0])) best = o; });
    if (!best) return;
    var nx = best[1], ny = best[2], tx = -ny, ty = nx;
    b.tip = { nx: nx, ny: ny, tx: tx, ty: ty, c: best[3], d: best[0], dd: b.vx * nx + b.vy * ny,
              s: b.x * tx + b.y * ty, vs: b.vx * tx + b.vy * ty, phi: 0, w: 0 };
    b.mode = 'tip';
    if (!b.under) {
      b.under = b.face.cloneNode(true);
      b.under.className = 'obj-face obj-under';
      b.under.removeAttribute('tabindex');
      var src = b.face.querySelectorAll('canvas'), dst = b.under.querySelectorAll('canvas');
      for (var i = 0; i < src.length; i++) { dst[i].width = src[i].width; dst[i].height = src[i].height; dst[i].getContext('2d').drawImage(src[i], 0, 0); }
      this.under.appendChild(b.under);
    }
  };

  D._dropUnder = function (b) {
    if (b.under && b.under.parentNode) b.under.parentNode.removeChild(b.under);
    b.under = null; b.face.style.clipPath = ''; b.face.style.visibility = ''; b._sl = null;
  };

  D._extentAlong = function (b, nx, ny) {
    var A = axes(b);
    return b.w / 2 * Math.abs(A.ux * nx + A.uy * ny) + b.h / 2 * Math.abs(A.vx * nx + A.vy * ny);
  };

  D._stepTip = function (b, h) {
    var t = b.tip, en = this._extentAlong(b, t.nx, t.ny), r = Math.min(b.w, b.h) / 2;
    var k2 = Math.max(en * en / 3, r * r), cp = Math.cos(t.phi), sp = Math.sin(t.phi);
    t.w += G * t.d * cp / (k2 + t.d * t.d) * h;
    t.phi += t.w * h;
    var acc = G * (sp - (b.def.tipFriction == null ? 0.3 : b.def.tipFriction) * cp);
    t.dd = acc > 0 || t.dd > 0 ? Math.max(0, t.dd + acc * h) : 0;
    t.d += t.dd * h;
    t.s += t.vs * h; t.vs *= 1 - 2 * h;
    b.a += b.va * h; b.va *= 1 - 4 * h;
    if (t.d > en + 1 || t.phi > 2) this._beginFall(b);
  };

  D._tipPose = function (b) {
    var t = b.tip, cp = Math.cos(t.phi), sp = Math.sin(t.phi);
    return { x: t.nx * (t.c + t.d * cp) + t.tx * t.s, y: t.ny * (t.c + t.d * cp) + t.ty * t.s, z: -t.d * sp };
  };

  D._beginFall = function (b) {
    var t = b.tip, P = this._tipPose(b), cp = Math.cos(t.phi), sp = Math.sin(t.phi);
    var vn = t.dd * cp - t.d * t.w * sp, vz = -t.dd * sp - t.d * t.w * cp;
    b.fall = { x: P.x, y: P.y, z: P.z, vx: t.nx * vn + t.tx * t.vs, vy: t.ny * vn + t.ty * t.vs, vz: vz };
    b.mode = 'fall';
  };

  D._stepFall = function (b, h) {
    var f = b.fall, t = b.tip;
    f.vz -= G * h;
    f.x += f.vx * h; f.y += f.vy * h; f.z += f.vz * h;
    t.phi += t.w * h; t.w *= 1 - 1.2 * h; b.a += b.va * h;
    if (f.z < -this.floor) {
      var def = b.def;
      this.remove(b);
      if (def.onGone) def.onGone(b, this);
    }
  };

  // separating-axis test between two rotated boxes; returns contact normal (A->B), depth and point
  function sat(A, B, pad) {
    var a1 = axes(A), b1 = axes(B), ax = [[a1.ux, a1.uy], [a1.vx, a1.vy], [b1.ux, b1.uy], [b1.vx, b1.vy]];
    var dx = B.x - A.x, dy = B.y - A.y, best = Infinity, nx = 0, ny = 0;
    for (var i = 0; i < 4; i++) {
      var x = ax[i][0], y = ax[i][1];
      var rA = A.w / 2 * Math.abs(a1.ux * x + a1.uy * y) + A.h / 2 * Math.abs(a1.vx * x + a1.vy * y);
      var rB = B.w / 2 * Math.abs(b1.ux * x + b1.uy * y) + B.h / 2 * Math.abs(b1.vx * x + b1.vy * y);
      var d = dx * x + dy * y, o = rA + rB + (pad || 0) - Math.abs(d);
      if (o <= 0) return null;
      if (o < best) { best = o; var sg = d < 0 ? -1 : 1; nx = x * sg; ny = y * sg; }
    }
    return { nx: nx, ny: ny, depth: best };
  }

  D._collide = function (A, B) {
    var c = sat(A, B, 0);
    if (!c) return;
    var pts = [];
    cornersOf(B).forEach(function (p) { if (inside(A, p.x, p.y, 0.5)) pts.push(p); });
    cornersOf(A).forEach(function (p) { if (inside(B, p.x, p.y, 0.5)) pts.push(p); });
    var px = 0, py = 0;
    if (pts.length) { pts.forEach(function (p) { px += p.x; py += p.y; }); px /= pts.length; py /= pts.length; }
    else { px = (A.x + B.x) / 2; py = (A.y + B.y) / 2; }
    var imA = A.held ? 0 : 1 / A.m, imB = B.held ? 0 : 1 / B.m, iIA = A.held ? 0 : 1 / A.I, iIB = B.held ? 0 : 1 / B.I;
    if (imA + imB === 0) return;
    var nx = c.nx, ny = c.ny, corr = Math.max(c.depth - 0.3, 0) * 0.8 / (imA + imB);
    A.x -= nx * corr * imA; A.y -= ny * corr * imA; B.x += nx * corr * imB; B.y += ny * corr * imB;
    var rax = px - A.x, ray = py - A.y, rbx = px - B.x, rby = py - B.y;
    var vrx = (B.vx - B.va * rby) - (A.vx - A.va * ray), vry = (B.vy + B.va * rbx) - (A.vy + A.va * rax);
    var vn = vrx * nx + vry * ny;
    if (!A.held) A.mode = 'move';
    if (!B.held) B.mode = 'move';
    if (vn >= 0) return;
    var ran = rax * ny - ray * nx, rbn = rbx * ny - rby * nx, e = Math.min(A.def.restitution, B.def.restitution);
    var j = -(1 + e) * vn / (imA + imB + ran * ran * iIA + rbn * rbn * iIB);
    A.vx -= j * nx * imA; A.vy -= j * ny * imA; A.va -= ran * j * iIA;
    B.vx += j * nx * imB; B.vy += j * ny * imB; B.va += rbn * j * iIB;
    var tx = -ny, ty = nx, vt = vrx * tx + vry * ty, rat = rax * ty - ray * tx, rbt = rbx * ty - rby * tx;
    var jt = clamp(-vt / (imA + imB + rat * rat * iIA + rbt * rbt * iIB), -0.3 * j, 0.3 * j);
    A.vx -= jt * tx * imA; A.vy -= jt * ty * imA; A.va -= rat * jt * iIA;
    B.vx += jt * tx * imB; B.vy += jt * ty * imB; B.va += rbt * jt * iIB;
    if (!A.held) this.constrain(A);
    if (!B.held) this.constrain(B);
  };

  /* ---------- rendering ---------- */
  D._render = function (b) {
    var def = b.def, sh = def.shadow, L = b.lift, w = b.w, h = b.h;
    if (def.draw) def.draw(b, this);
    if (b.mode === 'tip' || b.mode === 'fall') return this._render3d(b);
    var sc = 1 + (def.lift - 1) * L;
    b.face.style.transform = 'translate(' + b.x.toFixed(2) + 'px,' + b.y.toFixed(2) + 'px) rotate(' + b.a.toFixed(4) + 'rad) scale(' + sc.toFixed(4) + ') translate(' + (-w / 2) + 'px,' + (-h / 2) + 'px)';
    if (sh) {
      var o = this.screenVec(sh.x + (sh.liftX - sh.x) * L, sh.y + (sh.liftY - sh.y) * L), ins = sh.inset || 0;
      b.shadow.style.transform = 'translate(' + (b.x + o.x).toFixed(2) + 'px,' + (b.y + o.y).toFixed(2) + 'px) rotate(' + b.a.toFixed(4) + 'rad) scale(' + sc.toFixed(4) + ') translate(' + (-w / 2 + ins) + 'px,' + (-h / 2 + ins) + 'px)';
      if (b._sl !== L) {
        b._sl = L;
        b.shadow.style.opacity = Math.max(0, sh.opacity + (sh.liftOpacity - sh.opacity) * Math.min(L, 1.5));
        b.shadow.style.filter = 'blur(' + (sh.blur + (sh.liftBlur - sh.blur) * L).toFixed(1) + 'px)';
      }
    }
  };

  D._render3d = function (b) {
    var t = b.tip, P = b.mode === 'fall' ? b.fall : this._tipPose(b);
    var R = mul(rotAxis(-t.ny, t.nx, 0, t.phi), rotZ(b.a));
    if (b.def.rod) {
      // a rod looks the same from any side about its own axis, so only the axis tilts: keep the drawing facing the camera
      var ux = R[0], uy = R[1], uz = R[2], vx = -uy, vy = ux, vl = Math.hypot(vx, vy);
      if (vl > 0.05) {
        vx /= vl; vy /= vl;
        if (vx * R[4] + vy * R[5] < 0) { vx = -vx; vy = -vy; }
        R = [ux, uy, uz, 0, vx, vy, 0, 0, uy * 0 - uz * vy, uz * vx - ux * 0, ux * vy - uy * vx, 0, 0, 0, 0, 1];
      }
    }
    var M = mul(this.proj, mul(tr(P.x, P.y, P.z), mul(R, tr(-b.w / 2, -b.h / 2, 0))));
    var m3 = css3d(M);
    b.face.style.transform = m3;
    if (b.under) b.under.style.transform = m3;
    if (b.mode === 'tip') {
      // the part still over the wood is drawn above the desk, the overhang below it (so the desk hides it as it drops)
      var c = Math.cos(b.a), s = Math.sin(b.a), mx = t.nx * c + t.ny * s, my = -t.nx * s + t.ny * c;
      var k = t.d - mx * b.w / 2 - my * b.h / 2; // f(local px) = m.(q - centre) + d
      b.face.style.clipPath = clipRect(b.w, b.h, mx, my, k, true);
      if (b.under) b.under.style.clipPath = clipRect(b.w, b.h, mx, my, k, false);
    } else {
      b.face.style.visibility = 'hidden';
      if (b.under) b.under.style.clipPath = '';
    }
    if (b.under) b.under.style.filter = 'brightness(' + (1 - 0.55 * clamp(-P.z / 1000, 0, 1)).toFixed(3) + ')';
    if (b.shadow && b.mode === 'tip') {
      var sh = b.def.shadow, o = this.screenVec(sh.x, sh.y), ins = sh.inset || 0;
      b.shadow.style.transform = 'translate(' + (P.x + o.x).toFixed(2) + 'px,' + (P.y + o.y).toFixed(2) + 'px) rotate(' + b.a.toFixed(4) + 'rad) translate(' + (-b.w / 2 + ins) + 'px,' + (-b.h / 2 + ins) + 'px)';
    }
    if (b.shadow) b.shadow.style.opacity = b.mode === 'fall' ? 0 : (b.def.shadow.opacity * Math.pow(Math.max(0, Math.cos(t.phi)), 6)).toFixed(3);
  };

  EGG.Desk = Desk;
})();
