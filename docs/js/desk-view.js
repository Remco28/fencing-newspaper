/* Desk view math (pure; tested by tests/desk-view.test.js).
   The desk is always landscape: world units (desk-photo px) map to the screen by one uniform scale `s`
   and a translation (tx, ty); there is no rotation.
   - Wide screens: fit the whole wood (plus a 10-unit margin), exactly as before.
   - Narrow / portrait screens: zoom in until about VIEW_W world units span the screen width (a 360-unit
     small-screen paper is ~160 px on a 360 px phone, ~175 px on 393, ~180 px on 412). The desk is centred
     and the left/right of the wood are cropped. The zoom never pushes the top/bottom rims off screen: it is
     capped so the full wood height plus ROOM units above and below still fits.
     Between aspect 1.0 and 0.75 the zoom blends in (log-scale smoothstep), so tablets get part of it and a
     resize across square doesn't jump.
   - play: the visible part of the wood, in world units. A side cut off by the screen is a 'wall' (inset by
     WALL_PX screen px), a side where the real rim is on screen is a 'rim' (exactly the wood edge).
     With the whole wood visible, play equals bounds and every edge is 'rim'. */
(function (root) {
  'use strict';
  var MARGIN = 10, VIEW_W = 820, ROOM = 40, WALL_PX = 6;

  function deskView(W, H, b) {
    var bw = b.x1 - b.x0 + 2 * MARGIN, bh = b.y1 - b.y0 + 2 * MARGIN;
    var fit = Math.min(W / bw, H / bh), s = fit;
    var aspect = W / H, t = Math.max(0, Math.min(1, (1 - aspect) / 0.25));
    t = t * t * (3 - 2 * t);
    if (t > 0) {
      var zoom = Math.min(W / VIEW_W, H / (b.y1 - b.y0 + 2 * ROOM));
      if (zoom > fit) s = fit * Math.pow(zoom / fit, t);
    }
    // centred on the wood both ways (identical to the old fit layout when nothing is cropped)
    var tx = W / 2 - (b.x0 + b.x1) / 2 * s, ty = H / 2 - (b.y0 + b.y1) / 2 * s;
    var vx0 = -tx / s, vx1 = (W - tx) / s, vy0 = -ty / s, vy1 = (H - ty) / s, ins = WALL_PX / s, eps = 0.5;
    var edges = {
      left: vx0 > b.x0 + eps ? 'wall' : 'rim', right: vx1 < b.x1 - eps ? 'wall' : 'rim',
      top: vy0 > b.y0 + eps ? 'wall' : 'rim', bottom: vy1 < b.y1 - eps ? 'wall' : 'rim'
    };
    var play = {
      x0: edges.left === 'wall' ? vx0 + ins : b.x0, x1: edges.right === 'wall' ? vx1 - ins : b.x1,
      y0: edges.top === 'wall' ? vy0 + ins : b.y0, y1: edges.bottom === 'wall' ? vy1 - ins : b.y1,
      edges: edges
    };
    return { s: s, tx: tx, ty: ty, play: play, cropped: edges.left === 'wall' || edges.right === 'wall' };
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = deskView;
  else (root.EGG = root.EGG || {}).deskView = deskView;
})(this);
