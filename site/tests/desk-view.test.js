// node site/tests/desk-view.test.js
const assert = require('assert');
const view = require('../js/desk-view.js');
const B = { x0: 36, y0: 33, x1: 1504, y1: 996 };
const near = (a, b, e) => Math.abs(a - b) <= e;
// wide screens: whole wood fitted exactly as before (10-unit margin, centred), play == bounds, all rims
for (const [W, H] of [[1440, 828], [1280, 728], [780, 314], [844, 344]]) {
  const v = view(W, H, B), fit = Math.min(W / 1488, H / 983);
  assert.strictEqual(v.s, fit, `fit scale ${W}x${H}`);
  assert(near(v.tx, (W - 1488 * fit) / 2 - 26 * fit, 1e-9) && near(v.ty, (H - 983 * fit) / 2 - 23 * fit, 1e-9), 'old fit translation');
  assert.deepStrictEqual([v.play.x0, v.play.y0, v.play.x1, v.play.y1], [B.x0, B.y0, B.x1, B.y1], 'play == bounds');
  assert.deepStrictEqual(v.play.edges, { left: 'rim', right: 'rim', top: 'rim', bottom: 'rim' });
  assert(!v.cropped);
  console.log(`ok  ${W}x${H}  fit s=${v.s.toFixed(3)}`);
}
// phones (portrait, desk area below the header): zoomed, sides cropped to walls, real top/bottom rims on screen
for (const [W, H] of [[360, 700], [393, 770], [412, 835], [360, 520]]) {
  const v = view(W, H, B), paper = 360 * v.s;
  assert(v.cropped && v.play.edges.left === 'wall' && v.play.edges.right === 'wall', 'sides are walls');
  assert(v.play.edges.top === 'rim' && v.play.edges.bottom === 'rim', 'top/bottom are rims');
  assert(v.ty + B.y0 * v.s >= 0 && v.ty + B.y1 * v.s <= H, 'rims on screen');
  // play is on screen and inside the wood
  assert(v.tx + v.play.x0 * v.s >= 0 && v.tx + v.play.x1 * v.s <= W && v.play.x0 > B.x0 && v.play.x1 < B.x1);
  assert(near((v.play.x0 + v.play.x1) / 2, (B.x0 + B.x1) / 2, 1e-6), 'centred');
  if (W === 360 && H === 700) assert(paper >= 150 && paper <= 170, 'paper ~150-170 px on a 360 px phone');
  console.log(`ok  ${W}x${H}  s=${v.s.toFixed(3)}  paper=${paper.toFixed(0)}px  play x ${v.play.x0.toFixed(0)}-${v.play.x1.toFixed(0)}`);
}
// a short portrait window: zoom capped so the rims stay on screen
const v = view(360, 380, B);
assert(v.ty + B.y0 * v.s >= -1e-9 && v.ty + B.y1 * v.s <= 380 + 1e-9, 'short: rims still visible');
console.log('all tests passed');
