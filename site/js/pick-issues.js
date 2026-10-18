/* Which issues go on the desk (Frank, 2026-10-18).
   `issues` is sorted newest first. Returns `count` issues in stacking order, bottom to top:
   - the newest issue is always last (the top sheet, placed centred and near-upright by desk.js);
   - the next `recent` issues (2 on desktop, 1 on small screens) are always in the pile, if they exist;
   - remaining slots are filled by uniform random sampling WITHOUT replacement from all older issues,
     so the whole back catalogue turns up over visits;
   - only when there are fewer distinct issues than slots are copies repeated, older ones first;
     a second copy of the newest is used only as a last resort and never ends up on top;
   - everything below the top sheet is shuffled. */
(function (root) {
  'use strict';
  function shuffle(a, rand) {
    for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(rand() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  function pickDeskIssues(issues, count, recent, rand) {
    rand = rand || Math.random;
    if (!issues.length || count < 1) return [];
    var newest = issues[0];
    var below = issues.slice(1, 1 + recent);                       // always-present recent issues
    var older = shuffle(issues.slice(1 + recent), rand);           // random back catalogue, no repeats
    var slots = count - 1;
    below = below.slice(0, slots);
    while (below.length < slots && older.length) below.push(older.pop());
    // not enough distinct issues: repeat older ones (oldest-first pool cycled), newest copy last resort
    var pool = issues.slice(1);
    for (var k = 0; below.length < slots; k++) below.push(pool.length ? pool[k % pool.length] : newest);
    shuffle(below, rand).push(newest);
    return below;
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = pickDeskIssues;
  else (root.EGG = root.EGG || {}).pickDeskIssues = pickDeskIssues;
})(this);
