/* Landing page: lay out a fresh mess on the desk every visit. */
(function () {
  'use strict';
  var vp = document.getElementById('desk');
  if (!vp) return;
  var Desk = EGG.Desk;
  var desk = new Desk(vp, {
    image: 'assets/desk.webp',
    size: { w: 1520, h: 1012 },
    bounds: { x0: 36, y0: 33, x1: 1504, y1: 996 }, // the whole wooden top, frame included (measured from desk.webp)
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
    var B = desk.bounds, small = Math.min(vp.clientWidth, vp.clientHeight) < 560;
    var up = desk.upright(), W = B.x1 - B.x0, H = B.y1 - B.y0;
    var count = small ? 5 : 7, pw = small ? 360 : 300;
    // newest on top; next 2 (1 small) always in; rest random from the back catalogue — see js/pick-issues.js
    var order = EGG.pickDeskIssues(issues, count, small ? 1 : 2);

    var taken = [], delay = 0;
    order.forEach(function (iss, i) {
      var top = i === order.length - 1, p, a;
      if (top) { p = { x: B.x0 + W * rnd(0.36, 0.64), y: B.y0 + H * rnd(0.36, 0.64) }; a = up + rnd(-0.3, 0.3); }
      else {
        p = spot([B.x0 + 90, B.y0 + 90, B.x1 - 90, B.y1 - 90], taken);
        a = Math.random() < 0.55 ? up + rnd(-0.7, 0.7) : rnd(0, Math.PI * 2);
      }
      taken.push(p);
      desk.add('paper', {
        issue: iss, width: pw, x: p.x, y: p.y, a: a, drop: delay,
        label: 'En Garde Gazette No. ' + iss.number + ': ' + iss.headline + '. Open to read.'
      });
      delay += 0.07;
    });
    var top = taken[taken.length - 1];

    // the tin: somewhere off the newest copy
    var tin, t;
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
