// node site/tests/pick-issues.test.js
const assert = require('assert');
const pick = require('../js/pick-issues.js');
const mk = n => Array.from({ length: n }, (_, i) => ({ number: n - i, id: 'n' + (n - i) })); // newest first
const RUNS = 5000;
for (const n of [1, 3, 7, 20]) for (const [count, recent] of [[7, 2], [5, 1]]) {
  const L = mk(n), seen = new Set();
  for (let r = 0; r < RUNS; r++) {
    const o = pick(L, count, recent);
    assert.strictEqual(o.length, count, 'count');
    assert.strictEqual(o[o.length - 1], L[0], 'newest on top');
    for (let k = 1; k <= Math.min(recent, n - 1); k++) assert(o.includes(L[k]), 'recent present');
    if (n >= count) assert.strictEqual(new Set(o).size, count, 'no dupes when enough issues');
    if (n > 1) assert(!o.slice(0, -1).includes(L[0]), 'no second newest when older exist');
    o.forEach(x => seen.add(x));
  }
  assert.strictEqual(seen.size, n, 'every issue eventually appears');
  console.log(`ok  n=${n} count=${count} recent=${recent}  (${RUNS} runs, ${seen.size}/${n} seen)`);
}
// uniformity sanity for the back catalogue with 20 issues
const L = mk(20), hits = new Map();
for (let r = 0; r < 20000; r++) pick(L, 7, 2).slice(0, -1).forEach(x => hits.set(x, (hits.get(x) || 0) + 1));
const old = L.slice(3).map(x => hits.get(x) / 20000);
console.log('older-issue appearance rate min/max:', Math.min(...old).toFixed(3), Math.max(...old).toFixed(3), '(expected 4/17 = 0.235)');
assert(Math.max(...old) - Math.min(...old) < 0.03);
console.log('all tests passed');
