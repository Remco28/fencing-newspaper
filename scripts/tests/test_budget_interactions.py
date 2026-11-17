#!/usr/bin/env python3
"""Headless Chrome: Budget-page expand/shrink/clear, handles, and Wide/Tall, especially on page 2.

Builds a throwaway page from the frozen No. 7 fixtures (never touches live staging).
Skipped if Playwright or Chrome is missing.
  python3 scripts/tests/test_budget_interactions.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CHROME = Path("/usr/bin/google-chrome")
SNAP = json.loads((FIXTURES / "budget-no-7.json").read_text(encoding="utf-8"))
LINEUP = REPO / SNAP["lineup"]
WEEK = REPO / SNAP["week"]


def have_playwright() -> bool:
    if not CHROME.is_file() and not shutil.which("google-chrome"):
        return False
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return True
    except ImportError:
        return False


@unittest.skipUnless(have_playwright(), "playwright or chrome not installed")
class Interactions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.tmp = Path(tempfile.mkdtemp())
        wk = cls.tmp / "week"
        shutil.copytree(WEEK / "media", wk / "media")
        for f in ("items.json", "budget-versions.json"):
            shutil.copy(WEEK / f, wk / f)
        out = cls.tmp / "out"
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "build_budget_html.py"),
             "--lineup", str(LINEUP), "--staging-week", str(wk), "--out", str(out),
             "--preview", "--allow-pending"],
            capture_output=True, text=True,
        )
        if r.returncode:
            shutil.rmtree(cls.tmp, ignore_errors=True)
            raise AssertionError(r.stderr or r.stdout)
        pages = list(out.glob("*.html"))
        cls.html = pages[0]
        cls._pw = sync_playwright().start()
        cls.browser = cls._pw.chromium.launch(
            executable_path=str(CHROME) if CHROME.is_file() else shutil.which("google-chrome"),
            args=["--no-sandbox", "--disable-gpu"],
        )

    @classmethod
    def tearDownClass(cls):
        try:
            cls.browser.close()
        finally:
            cls._pw.stop()
            shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        self.ctx = self.browser.new_context(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
        self.page = self.ctx.new_page()
        self.errors = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.goto(self.html.resolve().as_uri())
        self.page.wait_for_selector(".page .blk")

    def tearDown(self):
        self.ctx.close()
        self.assertEqual(self.errors, [], "page errors: " + "; ".join(self.errors))

    def js(self, body, arg=None):
        return self.page.evaluate(body, arg) if arg is not None else self.page.evaluate(body)

    def test_slip_expand_shrink_clear_update_page2_table_and_the_slip(self):
        info = self.js("""() => {
          const C = BudgetPage.core;
          const s = C.slots.find(x => C.state.inc[x.key] && C.state.page[x.key] === 2
            && x.cost && (x.cost.type === 'table' || x.cost.type === 'table_rows'));
          return { key: s.key, cost: C.costOf(s), words: C.wordsOf(s) };
        }""")
        self.assertTrue(info["key"])
        self.js("key => BudgetPage.select('slot', key)", info["key"])
        self.page.wait_for_selector('.sheet [data-act="rz"][data-v="expand"]')
        t0 = self.js("() => performance.now()")
        self.page.click('.sheet [data-act="rz"][data-v="expand"]')
        after = self.js("""(before) => {
          const C = BudgetPage.core, s = C.slotBy[before.key];
          const t1 = performance.now();
          return {
            cost: C.costOf(s), words: C.wordsOf(s), rz: C.state.resize[before.key],
            expandOn: !!document.querySelector('.sheet [data-act="rz"][data-v="expand"].on'),
            clear: !!document.querySelector('.sheet [data-act="rz"][data-v="clear"]'),
            input: (document.querySelector('.sheet [data-rztarget]') || {}).value || '',
            slipCost: document.querySelector('.sheet .sh-row .dim') && document.querySelector('.sheet .sh-row .dim').textContent,
            fill: C.fill().used, ms: t1 - before.t0
          };
        }""", dict(info, t0=t0))
        self.assertGreater(after["cost"], info["cost"], "expanding a page-2 table must change its col-in")
        self.assertGreater(after["words"], info["words"])
        self.assertTrue(after["expandOn"], "the Expand button should light up after a click")
        self.assertTrue(after["clear"], "Clear should appear once a resize is set")
        self.assertTrue(after["input"], "the target field should show what was applied")
        self.assertIsNotNone(after["rz"])
        # a second Expand must keep growing (not stay stuck at 125% of the original)
        self.page.click('.sheet [data-act="rz"][data-v="expand"]')
        stepped = self.js("key => BudgetPage.core.wordsOf(BudgetPage.core.slotBy[key])", info["key"])
        self.assertGreater(stepped, after["words"])
        self.page.click('.sheet [data-act="rz"][data-v="shrink"]')
        shrunk = self.js("key => ({ words: BudgetPage.core.wordsOf(BudgetPage.core.slotBy[key]), dir: (BudgetPage.core.state.resize[key] || {}).direction })", info["key"])
        self.assertLess(shrunk["words"], stepped)
        # two Expands land above the original, so one Shrink still may be an expand vs the original
        self.page.click('.sheet [data-act="rz"][data-v="clear"]')
        self.page.click('.sheet [data-act="rz"][data-v="shrink"]')
        from_base = self.js("""key => ({
          words: BudgetPage.core.wordsOf(BudgetPage.core.slotBy[key]),
          shrinkOn: !!document.querySelector('.sheet [data-act="rz"][data-v="shrink"].on'),
          expandOn: !!document.querySelector('.sheet [data-act="rz"][data-v="expand"].on')
        })""", info["key"])
        self.assertLess(from_base["words"], info["words"])
        self.assertTrue(from_base["shrinkOn"])
        self.assertFalse(from_base["expandOn"])
        self.page.click('.sheet [data-act="rz"][data-v="clear"]')
        cleared = self.js("""key => {
          const C = BudgetPage.core, s = C.slotBy[key];
          return { cost: C.costOf(s), words: C.wordsOf(s), rz: C.state.resize[key] || null,
            clear: !!document.querySelector('.sheet [data-act="rz"][data-v="clear"]'),
            input: (document.querySelector('.sheet [data-rztarget]') || {}).value || '',
            doc: C.submission().resize[key] || null };
        }""", info["key"])
        self.assertIsNone(cleared["rz"])
        self.assertIsNone(cleared["doc"])
        self.assertAlmostEqual(cleared["cost"], info["cost"], delta=0.05)
        self.assertEqual(cleared["words"], info["words"])
        self.assertFalse(cleared["clear"])
        self.assertEqual(cleared["input"], "")
        self.assertLess(after["ms"], 250, "Expand click should stay snappy; was %s ms" % after["ms"])

    def test_page2_length_handle_is_not_covered_and_drags_update_cost(self):
        hits = self.js("""() => {
          const C = BudgetPage.core;
          const out = [];
          document.querySelectorAll('.page[data-page="2"] .handle.len').forEach(h => {
            const blk = h.closest('.blk'), r = h.getBoundingClientRect();
            const x = r.x + r.width / 2, y = r.y + r.height / 2;
            const top = document.elementFromPoint(x, y);
            const s = C.slotBy[blk.dataset.slot];
            out.push({
              key: blk.dataset.slot, type: (s.cost || {}).type, x, y,
              hitHandle: !!(top && top.closest && top.closest('[data-handle]')),
              hitToggle: !!(top && top.closest && top.closest('.lay-tog')),
              tag: top && top.className, words: C.wordsOf(s), cost: C.costOf(s)
            });
          });
          return out;
        }""")
        self.assertGreaterEqual(len(hits), 1, "page 2 should have length handles")
        covered = [h for h in hits if not h["hitHandle"] or h["hitToggle"]]
        self.assertEqual(covered, [], "length handle on a 1-col page-2 block was covered: " + repr(covered))
        # drag a table and a prose block (if both exist)
        kinds = {}
        for h in hits:
            if h["type"] in kinds:
                continue
            kinds[h["type"]] = h
            self.page.mouse.move(h["x"], h["y"])
            self.page.mouse.down()
            self.page.mouse.move(h["x"], h["y"] + 70, steps=8)
            self.page.mouse.up()
            after = self.js("""k => {
              const C = BudgetPage.core, s = C.slotBy[k];
              return { words: C.wordsOf(s), cost: +C.costOf(s).toFixed(3), rz: C.state.resize[k] || null };
            }""", h["key"])
            self.assertIsNotNone(after["rz"], "%s handle drag did not set resize" % h["key"])
            self.assertGreater(after["cost"], h["cost"], "%s cost should grow when the handle is dragged down" % h["key"])
            self.assertGreater(after["words"], h["words"], "%s words should grow when the handle is dragged down" % h["key"])
            # clear via slip so the next drag starts from the original
            self.js("k => BudgetPage.core.act.setResize(k, null)", h["key"])

    def test_page2_wide_tall_toggle_and_span(self):
        tog = self.js("""() => {
          const btn = document.querySelector('.page[data-page="2"] .lay-tog');
          if (!btn) return null;
          const blk = btn.closest('.blk'), r = btn.getBoundingClientRect(), C = BudgetPage.core;
          const key = blk.dataset.slot;
          return { key, before: C.currentLayout(C.slotBy[key]), span: C.spanOf(C.slotBy[key]),
            x: r.x + r.width / 2, y: r.y + r.height / 2 };
        }""")
        self.assertTrue(tog, "page 2 should have a Wide/Tall toggle")
        self.page.mouse.click(tog["x"], tog["y"])
        after = self.js("""d => {
          const C = BudgetPage.core, s = C.slotBy[d.key];
          return { layout: C.currentLayout(s), span: C.spanOf(s), field: C.submission().layout[d.key] };
        }""", tog)
        self.assertNotEqual(after["layout"], tog["before"])
        self.assertEqual(after["field"], after["layout"])
        self.assertEqual(after["span"], 1 if after["layout"] == "tall" else max(2, tog["span"]))

    def test_page1_prose_expand_updates_slip_and_fill(self):
        info = self.js("""() => {
          const C = BudgetPage.core;
          const s = C.slots.find(x => C.state.inc[x.key] && C.state.page[x.key] === 1 && !(x.cost && String(x.cost.type).startsWith('table')));
          return { key: s.key, words: C.wordsOf(s), cost: C.costOf(s), fill: C.fill().used };
        }""")
        self.js("key => BudgetPage.select('slot', key)", info["key"])
        self.page.wait_for_selector('.sheet [data-act="rz"][data-v="expand"]')
        self.page.click('.sheet [data-act="rz"][data-v="expand"]')
        after = self.js("""key => {
          const C = BudgetPage.core, s = C.slotBy[key];
          return { words: C.wordsOf(s), cost: C.costOf(s), fill: C.fill().used,
            expandOn: !!document.querySelector('.sheet [data-act="rz"][data-v="expand"].on'),
            clear: !!document.querySelector('.sheet [data-act="rz"][data-v="clear"]') };
        }""", info["key"])
        self.assertGreater(after["words"], info["words"])
        self.assertTrue(after["expandOn"])
        self.assertTrue(after["clear"])
        self.assertGreaterEqual(after["fill"], info["fill"])

    def test_handle_drag_is_throttled_and_stays_responsive(self):
        h = self.js("""() => {
          const hs = document.querySelectorAll('.page[data-page="2"] .handle.len');
          const el = hs[hs.length - 1] || document.querySelector('.handle.len');
          const r = el.getBoundingClientRect(), blk = el.closest('.blk');
          return { key: blk.dataset.slot, x: r.x + r.width / 2, y: r.y + r.height / 2 };
        }""")
        # 20 pointer-move samples along the handle; each frame should stay well under a frame budget once coalesced
        import time
        self.page.mouse.move(h["x"], h["y"])
        t0 = time.perf_counter()
        self.page.mouse.down()
        for i in range(16):
            self.page.mouse.move(h["x"], h["y"] + 6 * (i + 1), steps=1)
        self.page.mouse.up()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        after = self.js("k => BudgetPage.core.state.resize[k] || null", h["key"])
        self.assertIsNotNone(after, "throttled drag should still commit a resize on pointerup")
        # 16 moves + up should stay well under a second on this page once packing is rAF-coalesced
        self.assertLess(elapsed_ms, 1000, "page-2 handle drag felt slow: %s ms" % round(elapsed_ms, 1))


if __name__ == "__main__":
    unittest.main(verbosity=1)
