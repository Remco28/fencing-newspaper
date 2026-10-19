/* Landing page: lay out a fresh mess on the desk every visit. */
(function () {
  'use strict';
  var vp = document.getElementById('desk');
  if (!vp) return;
  var Desk = EGG.Desk;
  var desk = new Desk(vp, {
    image: 'assets/desk.webp',
    size: { w: 1520, h: 1012 },
    bounds: { x0: 36, y0: 33, x1: 1504, y1: 996 }, // the whole wooden top, frame included (measured from desk.webp); desk.play is the visible part
    perspective: 2300,
    floor: 1150
  });
  window.__desk = desk; // handy for poking at it from the console
  var issues = [];

  function rnd(a, b) { return a + Math.random() * (b - a); }

  // best-candidate sampling: spread out, but still overlapping like a real pile
  function spot(box, taken, tries) {
    var best = null, bd = -1;
    for (var k = 0; k < (tries || 16); k++) {
      var p = { x: rnd(box[0], box[2]), y: rnd(box[1], box[3]) }, d = Infinity;
      taken.forEach(function (q) { d = Math.min(d, Math.hypot(p.x - q.x, p.y - q.y)); });
      if (d > bd) { bd = d; best = p; }
    }
    return best;
  }

  function mess() {
    desk.clear();
    if (!issues.length) return;
    // place inside the visible part of the wood (desk.play), not desk.bounds: phones crop the sides
    var B = desk.play, small = Math.min(vp.clientWidth, vp.clientHeight) < 560;
    var up = desk.upright(), W = B.x1 - B.x0, H = B.y1 - B.y0;
    var count = small ? 5 : 7, pw = small ? 360 : 300;
    // newest on top; next 2 (1 small) always in; rest random from the back catalogue — see js/pick-issues.js
    var order = EGG.pickDeskIssues(issues, count, small ? 1 : 2);

    // the top sheet's spot is chosen first so the rest spread out around it (on a narrow phone desk
    // they would otherwise end up hidden underneath it)
    var top = { x: B.x0 + W * rnd(0.36, 0.64), y: B.y0 + H * rnd(0.36, 0.64) }, taken = [top], delay = 0;
    var ins = small ? pw * 0.45 : 90;
    order.forEach(function (iss, i) {
      var p, a;
      if (i === order.length - 1) { p = top; a = up + rnd(-0.3, 0.3); }
      else {
        p = spot([B.x0 + ins, B.y0 + ins, B.x1 - ins, B.y1 - ins], taken, 24);
        a = Math.random() < 0.55 ? up + rnd(-0.7, 0.7) : rnd(0, Math.PI * 2);
        taken.push(p);
      }
      desk.add('paper', {
        issue: iss, width: pw, x: p.x, y: p.y, a: a, drop: delay,
        label: 'En Garde Gazette No. ' + iss.number + ': ' + iss.headline + '. Open to read.'
      });
      delay += 0.07;
    });

    // nothing buried: a sheet with almost nothing showing is moved to the best of a few other spots
    var sheets = desk.bodies.slice(0, order.length);
    function shown(b) {
      var c = Math.cos(b.a), s = Math.sin(b.a), n = 0, i, j, lx, ly;
      for (i = 1; i < 8; i++) for (j = 1; j < 8; j++) {
        lx = (i / 8 - 0.5) * b.w; ly = (j / 8 - 0.5) * b.h;
        if (desk.hit(b.x + c * lx - s * ly, b.y + s * lx + c * ly) === b) n++;
      }
      return n / 49;
    }
    for (var k = sheets.length - 2; k >= 0; k--) {
      var sh = sheets[k], best = { x: sh.x, y: sh.y, a: sh.a, f: shown(sh) };
      for (var t = 0; t < 14 && best.f < 0.15; t++) {
        var q = spot([B.x0 + ins, B.y0 + ins, B.x1 - ins, B.y1 - ins], taken, 6);
        sh.x = q.x; sh.y = q.y; sh.a = Math.random() < 0.55 ? up + rnd(-0.7, 0.7) : rnd(0, Math.PI * 2);
        desk.constrain(sh);
        var f = shown(sh);
        if (f > best.f) best = { x: sh.x, y: sh.y, a: sh.a, f: f };
      }
      sh.x = best.x; sh.y = best.y; sh.a = best.a;
    }

    // the tin: somewhere off the newest copy
    var tin;
    for (t = 0; t < 40; t++) {
      var tp = spot([B.x0 + 110, B.y0 + 110, B.x1 - 110, B.y1 - 110], [top], 8);
      if (Math.hypot(tp.x - top.x, tp.y - top.y) > 300 || t === 39) { tin = desk.add('tin', { x: tp.x, y: tp.y, a: rnd(0, Math.PI * 2), drop: delay }); break; }
    }
    delay += 0.1;

    // two pencils, not on top of each other or the tin
    ['yellow', 'blue'].forEach(function (style) {
      var pc = desk.add('pencil', { style: style, x: 0, y: 0, a: 0, drop: delay });
      for (t = 0; t < 60; t++) {
        pc.x = rnd(B.x0 + 160, B.x1 - 160); pc.y = rnd(B.y0 + 80, B.y1 - 80); pc.a = rnd(0, Math.PI * 2);
        if (!desk.overlaps(pc, 10)) break;
      }
      desk.constrain(pc);
      delay += 0.08;
    });
    desk.bodies.forEach(function (b) { desk._render(b); });
    desk.wake();
  }

  document.getElementById('shuffle').addEventListener('click', mess);
  var hint = document.getElementById('hint');
  if (hint && window.matchMedia('(pointer: coarse)').matches) hint.textContent = 'Drag things about · twist with two fingers · tap a paper to read it';

  EGG.loadIssues().then(function (list) {
    issues = list;
    mess();
    EGG.openFromQuery(issues);
  }).catch(function () {
    document.getElementById('load-error').hidden = false;
  });
})();
