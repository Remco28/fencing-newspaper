/* Desk object kinds. Adding a prop = one EGG.Desk.register(...) call; see REPORT.md. */
(function () {
  'use strict';
  var Desk = EGG.Desk, G = Desk.G, TAU = Math.PI * 2;
  function rnd(a, b) { return a + Math.random() * (b - a); }
  function toward0(v, d) { return v > d ? v - d : v < -d ? v + d : 0; }

  /* ---------- newsletter copies ---------- */
  Desk.register('paper', {
    layer: 'paper', solid: false, edge: 'contain',
    slide: 2600, spin: 16, restitution: 0.05, tow: 0.85, lift: 1.025, focusable: true,
    shadow: { x: 1.5, y: 2.5, blur: 2.5, opacity: 0.55, radius: 1, liftX: 14, liftY: 22, liftBlur: 20, liftOpacity: 0.32 },
    build: function (b, o, desk) {
      var iss = o.issue;
      b.w = o.width || 300; b.h = b.w * 11 / 8.5;
      var im = new Image();
      im.alt = ''; im.draggable = false; im.decoding = 'async';
      // the 1200px thumb is plenty at desk size; full-size page only on very dense / zoomed screens
      var dense = (b.w * desk.scale * (window.devicePixelRatio || 1)) > 1150;
      im.src = (!dense && iss.thumbs && iss.thumbs[0]) || iss.pages[0];
      b.face.appendChild(im);
      b.face.appendChild(document.createElement('i'));
    },
    onTap: function (b) { EGG.openReader(b.data.issue, 0, b.face); }
  });

  /* ---------- the paperclip tin (photo) ---------- */
  Desk.register('tin', Desk.imageProp({
    src: 'assets/tin-paperclips.webp', imageWidth: 1162, imageHeight: 1214, box: [158, 7, 1094, 1156], width: 132,
    density: 3, slide: 650, spin: 3.2, restitution: 0.35, tow: 0.7, maxSpin: 30, lift: 1.03,
    shadow: { x: 3, y: 5, blur: 3, opacity: 0.6, radius: 9, inset: 2, liftX: 14, liftY: 22, liftBlur: 16, liftOpacity: 0.4 },
    // a tap sets it spinning
    onTap: function (b, desk) {
      b.va += (Math.random() < 0.5 ? -1 : 1) * rnd(10, 15);
      b.mode = 'move'; desk.wake();
    }
  }));

  /* ---------- pencils ----------
     Drawn on a canvas from a little lighting model of the barrel cross-section, so the faces of a hex
     pencil (and its stamp) visibly turn over as it rolls. Rolling is a real degree of freedom: pushed
     across its length a pencil rolls with little resistance; pushed along it, it slides and stops fast.
     A hex barrel clacks to rest on a flat face; the round copy-editor's pencil rolls on and on. */
  var STYLES = {
    yellow: { hex: true, paint: [226, 172, 38], ferrule: true, eraser: [214, 124, 118], stamp: 'EN GARDE GAZETTE  ·  No. 2 HB', stampColor: 'rgba(40,28,6,.85)', rollDrag: 320 },
    blue: { hex: false, paint: [34, 70, 150], ferrule: false, core: [40, 80, 190], stamp: 'COPY DESK  ·  BLUE', stampColor: 'rgba(235,215,150,.92)', rollDrag: 120 }
  };

  function shadeRGB(c, k, spec) {
    return 'rgb(' + Math.min(255, Math.round(c[0] * k + spec * 255)) + ',' + Math.min(255, Math.round(c[1] * k + spec * 255)) + ',' + Math.min(255, Math.round(c[2] * k + spec * 255)) + ')';
  }

  function drawPencil(b, desk) {
    var st = b.st, cv = b.cv, ctx = cv.getContext('2d');
    var k = desk.scale * Math.min(window.devicePixelRatio || 1, 2.5) * 1.25;
    var W = b.w, H = b.h, pw = Math.ceil(W * k), ph = Math.ceil(H * k);
    if (cv.width !== pw || cv.height !== ph) { cv.width = pw; cv.height = ph; }
    ctx.setTransform(pw / W, 0, 0, ph / H, 0, 0);
    ctx.clearRect(0, 0, W, H);

    // light in pencil coordinates: x along the pencil, y across, z up
    var Lw = desk.light, c = Math.cos(b.a), s = Math.sin(b.a);
    var L = { y: -Lw.x * s + Lw.y * c, z: Lw.z };
    var hy = L.y, hz = L.z + 1, hn = Math.hypot(hy, hz); hy /= hn; hz /= hn;
    function lit(ny, nz, base, gloss) {
      var d = Math.max(0, ny * L.y + nz * L.z), sp = Math.pow(Math.max(0, ny * hy + nz * hz), 36) * gloss;
      return shadeRGB(base, 0.38 + 0.66 * d, sp);
    }
    var R = H / 2, cy = H / 2, tipG = 9, cone = 36;
    var endLen = st.ferrule ? 34 : 3, x0 = cone, x1 = W - endLen;
    var roll = b.roll, faces = [], i;

    // round section shading across the width (used by the cone, ferrule, eraser and round barrels)
    function cylGrad(xa, xb, base, gloss, rad) {
      var g = ctx.createLinearGradient(0, cy - rad, 0, cy + rad);
      for (i = 0; i <= 10; i++) { var yy = i / 5 - 1, nz = Math.sqrt(Math.max(0, 1 - yy * yy)); g.addColorStop(i / 10, lit(yy, nz, base, gloss)); }
      return g;
    }

    // --- barrel ---
    if (st.hex) {
      for (i = 0; i < 6; i++) {
        var b0 = roll + i * Math.PI / 3, b1 = b0 + Math.PI / 3, bm = b0 + Math.PI / 6;
        if (Math.cos(bm) < 0.02) continue;
        var ya = cy + R * Math.sin(b0), yb = cy + R * Math.sin(b1);
        var f = { i: i, top: Math.min(ya, yb), bot: Math.max(ya, yb), ya: ya, yb: yb, bm: bm, col: lit(Math.sin(bm), Math.cos(bm), st.paint, 0.35) };
        faces.push(f);
        ctx.fillStyle = f.col;
        ctx.fillRect(x0 - 0.5, f.top, x1 - x0 + 1, f.bot - f.top + 0.15);
      }
      ctx.fillStyle = 'rgba(70,45,0,.35)'; // ridges
      faces.forEach(function (f) { ctx.fillRect(x0, f.top - 0.12, x1 - x0, 0.24); });
    } else {
      ctx.fillStyle = cylGrad(0, 0, st.paint, 0.55, R);
      ctx.fillRect(x0 - 0.5, 0, x1 - x0 + 1, H);
    }

    // --- stamp: rides on one face, foreshortened as that face turns away ---
    var sa = roll + (st.hex ? Math.PI / 6 : 0), sc = Math.cos(sa);
    if (sc > 0.25) {
      var sy = cy + R * Math.sin(sa), half = st.hex ? R * 0.5 : R * 0.45;
      ctx.save();
      ctx.beginPath(); ctx.rect(x0, sy - half * sc, x1 - x0, 2 * half * sc); ctx.clip();
      ctx.translate(x0 + 34, sy); ctx.scale(1, sc);
      ctx.fillStyle = st.stampColor; ctx.globalAlpha = Math.min(1, (sc - 0.25) * 3);
      ctx.font = '600 ' + (R * 0.82).toFixed(2) + 'px Georgia, serif'; ctx.textBaseline = 'middle';
      ctx.fillText(st.stamp, 0, 0.3);
      ctx.restore();
    }

    // --- sharpened end: shaved wood cone, scalloped paint edge, graphite ---
    var gh = 1.25, wood = [222, 172, 112];
    function coneHalf(x) { return gh + (R - gh) * (x - tipG) / (x0 - tipG); }
    ctx.fillStyle = cylGrad(0, 0, wood, 0.12, R);
    ctx.beginPath(); ctx.moveTo(x0 + 0.5, 0); ctx.lineTo(tipG, cy - gh); ctx.lineTo(tipG, cy + gh); ctx.lineTo(x0 + 0.5, H); ctx.closePath(); ctx.fill();
    ctx.fillStyle = 'rgba(120,70,20,.18)'; // shaving marks
    for (i = 0; i < 5; i++) { ctx.fillRect(tipG + 4 + i * 4.6, cy - coneHalf(tipG + 4 + i * 4.6) * 0.9, 0.5, coneHalf(tipG + 4 + i * 4.6) * 1.8); }
    var scal = 6, xr = x0 - scal, kr = coneHalf(xr) / R;
    if (st.hex) {
      faces.forEach(function (f) {
        var ya2 = cy + (f.ya - cy) * kr, yb2 = cy + (f.yb - cy) * kr;
        ctx.fillStyle = f.col;
        ctx.beginPath(); ctx.moveTo(x0 + 0.6, f.ya); ctx.lineTo(xr, ya2);
        ctx.quadraticCurveTo(x0 + 1.5, (ya2 + yb2) / 2, xr, yb2); ctx.lineTo(x0 + 0.6, f.yb); ctx.closePath(); ctx.fill();
      });
    } else {
      ctx.fillStyle = cylGrad(0, 0, st.paint, 0.55, R);
      ctx.beginPath(); ctx.moveTo(x0 + 0.6, 0); ctx.quadraticCurveTo(x0 - 4, cy, x0 + 0.6, H); ctx.closePath(); ctx.fill();
    }
    var lead = st.core || [52, 52, 58];
    ctx.fillStyle = cylGrad(0, 0, lead, st.core ? 0.25 : 0.9, gh);
    ctx.beginPath(); ctx.moveTo(0.2, cy); ctx.lineTo(tipG + 0.8, cy - gh - 0.15); ctx.quadraticCurveTo(tipG + 1.6, cy, tipG + 0.8, cy + gh + 0.15); ctx.closePath(); ctx.fill();

    // --- back end ---
    if (st.ferrule) {
      var fx = x1, fl = 17;
      ctx.fillStyle = cylGrad(0, 0, [196, 160, 88], 1.1, R);
      ctx.fillRect(fx, 0.15, fl, H - 0.3);
      ctx.fillStyle = 'rgba(60,40,5,.45)';
      [2, 4, 12.6, 14.6].forEach(function (d) { ctx.fillRect(fx + d, 0.15, 0.55, H - 0.3); });
      ctx.fillStyle = 'rgba(255,240,200,.35)';
      [2.7, 4.7, 13.3, 15.3].forEach(function (d) { ctx.fillRect(fx + d, 0.3, 0.4, H - 0.6); });
      ctx.fillStyle = cylGrad(0, 0, st.eraser, 0.15, R * 0.94);
      ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(fx + fl - 0.5, cy - R * 0.94, W - fx - fl, R * 1.88, [0, 3.2, 3.2, 0]);
      else ctx.rect(fx + fl - 0.5, cy - R * 0.94, W - fx - fl, R * 1.88);
      ctx.fill();
    } else {
      ctx.fillStyle = cylGrad(0, 0, [st.paint[0] * 0.55, st.paint[1] * 0.55, st.paint[2] * 0.55], 0.3, R);
      ctx.fillRect(W - endLen, 0, endLen, H);
    }
    b._drawn = { roll: b.roll, a: b.a, k: k };
  }

  Desk.register('pencil', {
    layer: 'prop', solid: true, edge: 'fall', rod: true, density: 0.55,
    spin: 26, restitution: 0.3, tow: 0.95, hitPad: 14, lift: 1.0, tipFriction: 0.12, maxSpin: 25,
    shadow: { x: 2.2, y: 3.6, blur: 1.6, opacity: 0.55, radius: 7, inset: 0.5, liftX: 10, liftY: 16, liftBlur: 6, liftOpacity: 0.32 },
    build: function (b, o) {
      b.st = STYLES[o.style] || STYLES.yellow;
      b.w = o.length || 280; b.h = o.diameter || 13;
      b.r = b.h / 2 * (b.st.hex ? 0.866 : 1); // rolling radius (hex: across flats)
      b.roll = b.st.hex ? Math.round(rnd(0, 6)) * Math.PI / 3 : rnd(0, TAU);
      b.cv = document.createElement('canvas');
      b.face.appendChild(b.cv);
    },
    onScale: function (b) { b._drawn = null; },
    draw: function (b, desk) {
      var d = b._drawn;
      if (b.mode === 'fall' || (d && Math.abs(d.roll - b.roll) < 0.015 && Math.abs(d.a - b.a) < 0.05 && b.mode !== 'tip')) return;
      if (d && b.mode === 'tip') return;
      drawPencil(b, desk);
    },
    onDrag: function (b, dx, dy) { b.roll += (-dx * Math.sin(b.a) + dy * Math.cos(b.a)) / b.r * 0.5; },
    onTap: function (b, desk) { // flick it across its length so it rolls
      var sgn = Math.random() < 0.5 ? -1 : 1, v = b.st.hex ? 420 : 300;
      b.vx += -Math.sin(b.a) * v * sgn; b.vy += Math.cos(b.a) * v * sgn;
      b.mode = 'move'; desk.wake();
    },
    // rolling across, sliding along, clacking from flat to flat if hexagonal
    friction: function (b, dt) {
      var c = Math.cos(b.a), s = Math.sin(b.a), st = b.st;
      var vax = b.vx * c + b.vy * s, vpe = -b.vx * s + b.vy * c;
      vax = toward0(vax, 2600 * dt);
      vpe = toward0(vpe, st.rollDrag * dt);
      var busy = Math.abs(vpe) > 0.5;
      if (st.hex) {
        var step = Math.PI / 3, off = b.roll - Math.round(b.roll / step) * step;
        vpe -= G * Math.tan(off) * 0.9 * dt;     // lifting the barrel over a corner, dropping onto the next flat
        vpe *= 1 - 3 * dt;
        var nroll = b.roll + vpe * dt / b.r, noff = nroll - Math.round(nroll / step) * step;
        if (Math.abs(off) > 0.4 && Math.abs(noff) > 0.4 && (off > 0) !== (noff > 0)) vpe *= 0.72; // clack
        if (Math.abs(off) < 0.004 && Math.abs(vpe) < 4) { vpe = 0; b.roll -= off; } else busy = true;
      }
      b.roll += vpe * dt / b.r;
      b.vx = vax * c - vpe * s; b.vy = vax * s + vpe * c;
      b.va = toward0(b.va, b.def.spin * dt);
      return busy;
    }
  });
})();
