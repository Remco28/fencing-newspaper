#!/usr/bin/env python3
"""Headless Chrome: Budget-page expand/shrink/clear, handles, Wide/Tall (especially on page 2), and Manual
placement driven by real pointer events (move, bank, resize, overlap, overset, undo).

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


class _Browser(unittest.TestCase):
    """Shared: one throwaway No. 7 page per class, a fresh browser context per test."""
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


@unittest.skipUnless(have_playwright(), "playwright or chrome not installed")
class Interactions(_Browser):

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

    def test_manual_toggle_drag_to_page2_resize_overlap_undo_and_submission(self):
        # Auto is the default
        start = self.js("""() => {
          const C = BudgetPage.core;
          const lead = C.pack(1).placed.find(b => b.id === 'lead') || C.pack(1).placed[0];
          return { mode: C.submission().mode, pageVersion: C.PAGE_VERSION, lead: lead && { id: lead.id, page: 1, col: lead.col, y: lead.y, h: lead.h, span: lead.span } };
        }""")
        self.assertEqual(start["mode"], "auto")
        self.assertEqual(start["pageVersion"], "budget-paper-v2")
        self.page.wait_for_selector('#modebox [data-mode="manual"]')
        self.page.click('#modebox [data-mode="manual"]')
        snapped = self.js("""() => {
          const C = BudgetPage.core, doc = C.submission(), e = doc.manualLayout && doc.manualLayout.lead;
          return { mode: doc.mode, hasLayout: !!e, page: e && e.page, col: e && e.col, banner: !document.querySelector('.modebox [data-mode="manual"].on') ? false : true };
        }""")
        self.assertEqual(snapped["mode"], "manual")
        self.assertTrue(snapped["hasLayout"])
        self.assertTrue(snapped["banner"])

        # Drag lead down and onto page 2 (or keep page and move if already hard to cross)
        lead = self.js("""() => {
          const el = document.querySelector('.blk[data-slot="lead"]');
          const r = el.getBoundingClientRect();
          const p2 = document.querySelector('.cols[data-page="2"]').getBoundingClientRect();
          return { x: r.x + r.width/2, y: r.y + 12, p2x: p2.x + 40, p2y: p2.y + 80, startPage: +el.closest('.cols').dataset.page };
        }""")
        self.page.mouse.move(lead["x"], lead["y"])
        self.page.mouse.down()
        self.page.mouse.move(lead["p2x"], lead["p2y"], steps=12)
        self.page.mouse.up()
        after_drag = self.js("""() => {
          const e = BudgetPage.core.manualLayoutOf().lead, doc = BudgetPage.core.submission();
          return { page: e && e.page, col: e && e.col, topIn: e && e.topIn, mode: doc.mode, keys: Object.keys(doc.manualLayout || {}) };
        }""")
        self.assertEqual(after_drag["mode"], "manual")
        self.assertEqual(after_drag["page"], 2)
        self.assertIn("lead", after_drag["keys"])
        self.assertGreaterEqual(after_drag["topIn"], 0)

        # Height handle on a page-2 block (prefer a table or the lead now on page 2)
        handle = self.js("""() => {
          const blk = document.querySelector('.page[data-page="2"] .blk[data-slot="lead"]') || document.querySelector('.page[data-page="2"] .blk');
          const h = blk && blk.querySelector('.handle.len');
          if (!h) return null;
          const r = h.getBoundingClientRect(), C = BudgetPage.core, key = blk.dataset.slot;
          const e = C.manualLayoutOf()[key];
          return { key, x: r.x + r.width/2, y: r.y + r.height/2, heightIn: e.heightIn };
        }""")
        self.assertTrue(handle, "manual mode should show a length handle")
        self.page.mouse.move(handle["x"], handle["y"])
        self.page.mouse.down()
        self.page.mouse.move(handle["x"], handle["y"] + 50, steps=8)
        self.page.mouse.up()
        taller = self.js("k => BudgetPage.core.manualLayoutOf()[k].heightIn", handle["key"])
        self.assertGreater(taller, handle["heightIn"] - 0.001)

        # Overlap: drop another included block onto lead's box
        ov = self.js("""() => {
          const C = BudgetPage.core, lead = C.manualLayoutOf().lead;
          const other = Object.keys(C.manualLayoutOf()).find(k => k !== 'lead');
          C.act.placeAt(other, { page: lead.page, col: lead.col, span: Math.min(lead.span, C.manualLayoutOf()[other].span), topIn: lead.topIn, heightIn: C.manualLayoutOf()[other].heightIn });
          const pack = C.pack(lead.page);
          const banner = document.querySelector('#overlap');
          return { overlaps: pack.overlaps.length, banner: !!(banner && !banner.hidden && /overlap/i.test(banner.textContent || '')), other };
        }""")
        # placeAt emits and re-renders, so the banner should be visible
        ov = self.js("""() => {
          const C = BudgetPage.core, lead = C.manualLayoutOf().lead;
          const pack = C.pack(lead.page);
          const banner = document.querySelector('#overlap');
          return { overlaps: pack.overlaps.length, banner: !!(banner && !banner.hidden), text: banner && banner.textContent };
        }""")
        self.assertGreater(ov["overlaps"], 0)
        self.assertTrue(ov["banner"], "overlap banner should be visible: %s" % ov.get("text"))

        # Undo pops the overlap (and maybe the resize/drag); keep undoing until lead is not overlapping or positions change
        before_undo = self.js("() => BudgetPage.core.pack(BudgetPage.core.manualLayoutOf().lead.page).overlaps.length")
        self.page.click('#undoplace')
        after_undo = self.js("() => ({ overlaps: BudgetPage.core.pack(BudgetPage.core.manualLayoutOf().lead.page).overlaps.length, can: BudgetPage.core.canUndo() })")
        self.assertLessEqual(after_undo["overlaps"], before_undo)

        # Back to Auto with confirm
        self.page.once("dialog", lambda d: d.accept())
        self.page.click('#toauto')
        back = self.js('''() => ({ mode: BudgetPage.core.submission().mode, layout: BudgetPage.core.submission().manualLayout || null, autoOn: !!document.querySelector('#modebox [data-mode="auto"].on') })''')
        self.assertEqual(back["mode"], "auto")
        self.assertIsNone(back["layout"])
        self.assertTrue(back["autoOn"])

    def test_existing_auto_interactions_still_work_after_manual_and_back(self):
        self.page.click('#modebox [data-mode="manual"]')
        self.page.once("dialog", lambda d: d.accept())
        self.page.click('#toauto')
        info = self.js("""() => {
          const C = BudgetPage.core;
          const s = C.slots.find(x => C.state.inc[x.key] && C.state.page[x.key] === 2
            && x.cost && (x.cost.type === 'table' || x.cost.type === 'table_rows'));
          return { key: s.key, cost: C.costOf(s) };
        }""")
        self.js("key => BudgetPage.select('slot', key)", info["key"])
        self.page.wait_for_selector('.sheet [data-act="rz"][data-v="expand"]')
        self.page.click('.sheet [data-act="rz"][data-v="expand"]')
        after = self.js('''key => {
          const btn = document.querySelector('.sheet [data-act="rz"][data-v="expand"]');
          return { cost: BudgetPage.core.costOf(BudgetPage.core.slotBy[key]), on: !!(btn && btn.classList.contains("on")) };
        }''', info["key"])
        self.assertGreater(after["cost"], info["cost"])
        self.assertTrue(after["on"])


@unittest.skipUnless(have_playwright(), "playwright or chrome not installed")
class ManualPlacement(_Browser):
    """Manual placement with real pointer events (mouse down / move / up), the way Frank drags.

    Frank, 2026-11-17: placement "seems to work randomly", photos "not reliable at all", same-page moves
    "virtually impossible", dragging off to the left to pull a block "sometimes works". Causes this pins:
    a picture started the browser's own drag and cancelled the move; the overlap line appeared and vanished
    mid-drag and shifted the pages under the pointer; Manual had no drop on the bank; pointer capture on
    <html> ate the click that opens the slip."""

    def setUp(self):
        super().setUp()
        self.page.click('#modebox [data-mode="manual"]')
        self.page.wait_for_selector("body.manual")
        g = self.js("""() => { const c = document.querySelector('.cols[data-page="1"]'); return { ppi: +c.dataset.ppi }; }""")
        self.ppi = g["ppi"]
        self.colw = self.js("() => BudgetPage.core.cap.col_width_in + BudgetPage.core.GUT")

    # ---- helpers ----
    def frame(self, key):
        return self.js("""k => { const C = BudgetPage.core, e = C.state.manualLayout[k];
          return e ? Object.assign({}, e, { on: !!(C.photoMeta[k] ? C.state.photos[k] : C.state.inc[k]) }) : null; }""", key)

    def point(self, key, part=None):
        """Grab point on a block: its picture ('img'), its headline ('.h'), or its top-left area."""
        return self.js("""([k, part]) => {
          const el = document.querySelector('.cols .blk[data-photo="' + k + '"]') || document.querySelector('.cols .blk[data-slot="' + k + '"]');
          if (!el) return null;
          const t = (part && el.querySelector(part)) || el, r = t.getBoundingClientRect(), b = el.getBoundingClientRect();
          return { x: r.x + r.width / 2, y: r.y + Math.min(r.height / 2, 18), bx: b.x, by: b.y, tag: t.tagName };
        }""", [key, part])

    def cols_tops(self):
        return self.js("() => [1, 2].map(p => Math.round(document.querySelector('.cols[data-page=\"' + p + '\"]').getBoundingClientRect().top * 10) / 10)")

    def drag(self, x, y, tx, ty, steps=14):
        """Real pointer drag. Returns the page tops seen at every step (they must never move mid-drag)."""
        m = self.page.mouse
        m.move(x, y)
        m.down()
        tops = []
        for i in range(1, steps + 1):
            m.move(x + (tx - x) * i / steps, y + (ty - y) * i / steps)
            tops.append(tuple(self.cols_tops()))
        m.up()
        return tops

    def move_by(self, key, dx_in, dy_in, part=None):
        p = self.point(key, part)
        self.assertIsNotNone(p, "no block for " + key)
        tops = self.drag(p["x"], p["y"], p["x"] + dx_in * self.ppi, p["y"] + dy_in * self.ppi)
        self.assertEqual(len(set(tops)), 1, "the pages moved under the pointer mid-drag: %r" % sorted(set(tops)))
        return p

    def place_photo_by_button(self, page=1):
        pid = self.js("() => BudgetPage.core.loosePhotos.find(id => BudgetPage.core.canPlacePhoto(id) && BudgetPage.core.media[id].w)")
        self.assertTrue(pid, "fixture needs a vetted loose photo with a size")
        btn = '#bank .strip[data-photo="%s"] [data-add="%d"]' % (pid, page)
        self.page.locator(btn).scroll_into_view_if_needed()
        self.page.click(btn)
        self.assertTrue(self.frame(pid)["on"])
        return pid

    def bank_point(self):
        return self.js("() => { const b = document.querySelector('#bank').getBoundingClientRect(); return { x: b.x + b.width / 2, y: b.y + 260 }; }")

    # ---- tests ----
    def test_photo_moves_up_and_down_on_the_same_page_every_time_grabbed_by_the_picture(self):
        pid = self.place_photo_by_button(1)
        start = self.frame(pid)
        self.assertEqual(self.point(pid, "img")["tag"], "IMG")
        top = start["topIn"]
        # Five moves in a row, all grabbed on the picture itself (that used to start the browser's image drag).
        for dy in (-2.0, 1.5, -1.0, 2.2, -2.7):
            self.move_by(pid, 0, dy, "img")
            top = max(0.0, top + dy)
            got = self.frame(pid)
            self.assertAlmostEqual(got["topIn"], top, delta=0.051, msg="photo did not land where it was dropped (dy %s)" % dy)
            self.assertEqual((got["page"], got["col"], got["span"], got["heightIn"]), (1, start["col"], start["span"], start["heightIn"]))
            top = got["topIn"]

    def test_photo_from_a_lower_section_to_a_higher_section_and_back(self):
        pid = self.place_photo_by_button(1)
        low = self.frame(pid)
        self.assertGreater(low["topIn"], 3, "the photo should start low on page 1")
        # Free the top of the right-hand column by dragging its story off the page to the left.
        b = self.bank_point()
        p = self.point("for-the-parents", ".h")
        self.drag(p["x"], p["y"], b["x"], b["y"])
        self.assertFalse(self.frame("for-the-parents")["on"])
        # Lower section, column 1 -> top of column 3: two columns right, all the way up.
        self.move_by(pid, 2 * self.colw, -low["topIn"], "img")
        high = self.frame(pid)
        self.assertEqual((high["page"], high["col"]), (1, 2))
        self.assertAlmostEqual(high["topIn"], 0, delta=0.051)
        self.assertEqual((high["span"], high["heightIn"]), (low["span"], low["heightIn"]), "a move never resizes")
        # Its frame runs a little into the table below: reported, never resolved for Frank.
        ov = self.js("() => BudgetPage.core.pack(1).overlaps.map(o => [o.a.id, o.b.id].sort().join('+'))")
        self.assertTrue(all(pid in o for o in ov), ov)
        # ... and onto an occupied spot higher up the page: it stays where it is put, with a warning, not refused.
        self.move_by(pid, -2 * self.colw, 0.5, "img")
        over = self.frame(pid)
        self.assertEqual((over["col"], over["page"]), (0, 1))
        self.assertAlmostEqual(over["topIn"], 0.5, delta=0.051)
        banner = self.js("() => { const b = document.querySelector('#overlap'); return { hidden: b.hidden, calm: b.classList.contains('calm'), text: b.textContent }; }")
        self.assertFalse(banner["hidden"])
        self.assertFalse(banner["calm"])
        self.assertIn("Overlap", banner["text"])
        self.assertTrue(self.js("id => document.querySelector('.blk[data-photo=\"' + id + '\"]').classList.contains('overlap')", pid))
        self.assertTrue(self.js("id => document.querySelector('.blk[data-photo=\"' + id + '\"]').classList.contains('lifted')", pid),
                        "the block just dropped draws on top so an overlap never hides it")

    def test_articles_move_up_down_and_across_on_the_same_page(self):
        lead = self.frame("lead")
        self.move_by("lead", 0, 4.6, ".h")
        down = self.frame("lead")
        self.assertAlmostEqual(down["topIn"], lead["topIn"] + 4.6, delta=0.051)
        self.assertEqual((down["page"], down["col"], down["span"]), (lead["page"], lead["col"], lead["span"]))
        self.move_by("lead", 0, -4.6, ".h")
        self.assertAlmostEqual(self.frame("lead")["topIn"], lead["topIn"], delta=0.051)
        nac = self.frame("nac-preview")
        self.move_by("nac-preview", 2 * self.colw, 2.0, ".h")
        moved = self.frame("nac-preview")
        self.assertEqual((moved["page"], moved["col"]), (nac["page"], 2))
        self.assertAlmostEqual(moved["topIn"], nac["topIn"] + 2.0, delta=0.051)
        others = self.js("() => { const L = BudgetPage.core.state.manualLayout; return Object.keys(L).filter(k => k !== 'lead' && k !== 'nac-preview').map(k => [k, L[k].page, L[k].col, L[k].topIn]); }")
        self.assertTrue(others)

    def test_drag_off_the_page_to_the_left_returns_articles_and_photos_to_the_bank(self):
        pid = self.place_photo_by_button(1)
        b = self.bank_point()
        # An article onto the bank rail.
        p = self.point("lead", ".h")
        self.drag(p["x"], p["y"], b["x"], b["y"])
        self.assertFalse(self.frame("lead")["on"])
        self.assertTrue(self.js("() => !!document.querySelector('#bank .strip[data-slot=\"lead\"]')"))
        self.assertFalse(self.js("() => !!document.querySelector('.cols .blk[data-slot=\"lead\"]')"))
        # A photo, grabbed by its picture, released just off page 1's left edge (on the mat, not the rail).
        for attempt in range(3):  # every time, not sometimes
            if attempt:
                btn = '#bank .strip[data-photo="%s"] [data-add="1"]' % pid
                self.page.locator(btn).scroll_into_view_if_needed()
                self.page.click(btn)
                self.assertTrue(self.frame(pid)["on"])
            p = self.point(pid, "img")
            edge = self.js("() => document.querySelector('.page[data-page=\"1\"]').getBoundingClientRect().left")
            self.drag(p["x"], p["y"], edge - 6, p["y"])
            self.assertFalse(self.frame(pid)["on"], "attempt %d: photo stayed on the page" % attempt)
            self.assertTrue(self.js("id => !!document.querySelector('#bank .strip[data-photo=\"' + id + '\"]')", pid))
        doc = self.js("() => BudgetPage.core.submission()")
        self.assertNotIn("lead", [e["slot"] for e in doc["includedSlots"]])
        self.assertNotIn("lead", doc["manualLayout"])
        self.assertNotIn(pid, doc["photoIncludes"])
        self.assertNotIn(pid, doc["manualLayout"])

    def test_bank_strip_drops_on_the_outline_and_unvetted_strips_stay_in_the_bank(self):
        key = self.js("() => BudgetPage.core.slots.find(s => !s.empty && !BudgetPage.core.state.inc[s.key] && BudgetPage.core.canPlace(s)).key")
        s = self.js("""k => { const el = document.querySelector('#bank .strip[data-slot="' + k + '"]'); el.scrollIntoView({ block: 'center' });
          const r = el.getBoundingClientRect(), c = document.querySelector('.cols[data-page="2"]').getBoundingClientRect();
          return { x: r.x + 40, y: r.y + 14, tx: c.x + c.width * 0.5, ty: c.y + c.height * 0.75 }; }""", key)
        m = self.page.mouse
        m.move(s["x"], s["y"]); m.down()
        for i in range(1, 13):
            m.move(s["x"] + (s["tx"] - s["x"]) * i / 12, s["y"] + (s["ty"] - s["y"]) * i / 12)
        outline = self.js("""() => { const o = document.querySelector('.cols .drop-outline'); if (!o) return null;
          const c = o.closest('.cols'); return { page: +c.dataset.page, left: parseFloat(o.style.left), top: parseFloat(o.style.top), tag: o.textContent }; }""")
        m.up()
        self.assertIsNotNone(outline, "a dashed outline shows where the block will land")
        got = self.frame(key)
        self.assertTrue(got["on"])
        self.assertEqual(got["page"], outline["page"])
        self.assertAlmostEqual(got["topIn"] * self.ppi, outline["top"], delta=1.5)
        self.assertIn("Page 2", outline["tag"])
        self.assertFalse(self.js("() => !!document.querySelector('.drag-ghost, .drop-outline')"), "drag visuals are cleaned up")
        # Vetting gate: an unvetted strip does not leave the bank.
        locked = self.js("() => { const s = BudgetPage.core.slots.find(x => !x.empty && !BudgetPage.core.state.inc[x.key] && !BudgetPage.core.canPlace(x)); return s && s.key; }")
        self.assertTrue(locked, "fixture needs an unvetted slot")
        s = self.js("""k => { const el = document.querySelector('#bank .strip[data-slot="' + k + '"]'); el.scrollIntoView({ block: 'center' });
          const r = el.getBoundingClientRect(), c = document.querySelector('.cols[data-page="1"]').getBoundingClientRect();
          return { x: r.x + 40, y: r.y + 14, tx: c.x + c.width * 0.5, ty: c.y + c.height * 0.8 }; }""", locked)
        self.drag(s["x"], s["y"], s["tx"], s["ty"])
        self.assertFalse(self.js("k => !!BudgetPage.core.state.inc[k]", locked))
        self.assertFalse(self.js("k => k in BudgetPage.core.submission().manualLayout", locked))

    def test_page1_to_page2_by_drag_for_a_photo_and_an_article(self):
        pid = self.place_photo_by_button(1)
        for key, part in ((pid, "img"), ("nac-preview", ".h")):
            p = self.point(key, part)
            c2 = self.js("() => { const r = document.querySelector('.cols[data-page=\"2\"]').getBoundingClientRect(); return { x: r.x, y: r.y }; }")
            tx = c2["x"] + 2 * self.colw * self.ppi + (p["x"] - p["bx"])
            ty = c2["y"] + 5.0 * self.ppi + (p["y"] - p["by"])
            self.drag(p["x"], p["y"], tx, ty)
            got = self.frame(key)
            self.assertEqual((got["page"], got["col"]), (2, 2), key)
            self.assertAlmostEqual(got["topIn"], 5.0, delta=0.051, msg=key)
            self.assertTrue(self.js("k => !!document.querySelector('.cols[data-page=\"2\"] .blk[data-photo=\"' + k + '\"], .cols[data-page=\"2\"] .blk[data-slot=\"' + k + '\"]')", key))

    def test_photo_resize_handles_keep_its_shape_and_change_only_that_photo(self):
        pid = self.place_photo_by_button(1)
        before = self.js("() => JSON.parse(JSON.stringify(BudgetPage.core.state.manualLayout))")
        aspect = self.js("id => BudgetPage.core.media[id].h / BudgetPage.core.media[id].w", pid)

        def handle(kind, dx, dy):
            h = self.js("""([id, kind]) => { const r = document.querySelector('.blk[data-photo="' + id + '"] .handle.' + kind).getBoundingClientRect();
              return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; }""", [pid, kind])
            self.drag(h["x"], h["y"], h["x"] + dx, h["y"] + dy, steps=10)
            return self.js("id => ({ e: BudgetPage.core.state.manualLayout[id], size: BudgetPage.core.photoSize(id) })", pid)

        one = self.js("id => ({ e: BudgetPage.core.state.manualLayout[id], size: BudgetPage.core.photoSize(id) })", pid)
        wide = handle("wid", (self.colw + 0.1) * self.ppi, 0)  # one column wider
        self.assertEqual(wide["e"]["span"], one["e"]["span"] + 1)
        self.assertAlmostEqual(wide["size"]["heightIn"] / wide["size"]["widthIn"], aspect, delta=0.03, msg="never stretched or cropped")
        self.assertGreater(wide["size"]["widthIn"], one["size"]["widthIn"] * 1.8, "the picture grows with its frame")
        smaller = handle("len", 0, -1.2 * self.ppi)  # bottom edge up: the picture scales down, it does not jump back
        self.assertAlmostEqual(smaller["e"]["heightIn"], wide["e"]["heightIn"] - 1.2, delta=0.06)
        self.assertLess(smaller["size"]["heightIn"], wide["size"]["heightIn"])
        self.assertAlmostEqual(smaller["size"]["heightIn"] / smaller["size"]["widthIn"], aspect, delta=0.03)
        taller = handle("len", 0, 2.0 * self.ppi)  # past Clark's 2.2in guide: allowed
        self.assertGreater(taller["size"]["heightIn"], 2.2)
        self.assertAlmostEqual(taller["e"]["heightIn"], smaller["e"]["heightIn"] + 2.0, delta=0.06)
        img = self.js("""id => { const i = document.querySelector('.blk[data-photo="' + id + '"] img'); return { w: i.getBoundingClientRect().width, h: i.getBoundingClientRect().height, fit: getComputedStyle(i).objectFit }; }""", pid)
        self.assertNotEqual(img["fit"], "cover", "the preview never crops")
        self.assertAlmostEqual(img["h"] / self.ppi, taller["size"]["heightIn"], delta=0.08)
        # Only that photo changed.
        after = self.js("() => JSON.parse(JSON.stringify(BudgetPage.core.state.manualLayout))")
        self.assertEqual({k: v for k, v in after.items() if k != pid}, {k: v for k, v in before.items() if k != pid})
        # Slip controls: Smaller / Bigger / Natural size, Wide / Tall — all on that photo only.
        self.js("id => BudgetPage.select('photo', id)", pid)
        for v in ("smaller", "bigger", "natural"):
            self.page.click('#side .sheet [data-act="art"][data-v="%s"]' % v)
        nat = self.js("id => ({ e: BudgetPage.core.state.manualLayout[id], size: BudgetPage.core.photoSize(id), frameW: BudgetPage.core.frameW(BudgetPage.core.state.manualLayout[id].span) })", pid)
        self.assertAlmostEqual(nat["size"]["widthIn"], nat["frameW"], delta=0.02, msg="Natural size fills the frame width, uncropped")
        self.page.click('#side .sheet [data-act="lay"][data-v="tall"]')
        tall = self.js("id => ({ e: BudgetPage.core.state.manualLayout[id], size: BudgetPage.core.photoSize(id) })", pid)
        self.assertEqual(tall["e"]["span"], 1)
        self.assertAlmostEqual(tall["size"]["heightIn"] / tall["size"]["widthIn"], aspect, delta=0.03)
        final = self.js("() => JSON.parse(JSON.stringify(BudgetPage.core.state.manualLayout))")
        self.assertEqual({k: v for k, v in final.items() if k != pid}, {k: v for k, v in before.items() if k != pid})
        # The slip's Page 2 button keeps the size Frank gave it.
        self.page.click('#side [data-ppg="2"]')
        moved = self.js("id => BudgetPage.core.state.manualLayout[id]", pid)
        self.assertEqual((moved["page"], moved["span"], moved["heightIn"]), (2, tall["e"]["span"], tall["e"]["heightIn"]))

    def test_text_width_and_depth_handles_change_only_that_block(self):
        before = self.js("() => JSON.parse(JSON.stringify(BudgetPage.core.state.manualLayout))")
        h = self.js("""() => { const r = document.querySelector('.blk[data-slot="lead"] .handle.len').getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; }""")
        self.drag(h["x"], h["y"], h["x"], h["y"] + 1.0 * self.ppi, steps=10)
        got = self.js("() => { const C = BudgetPage.core, e = C.state.manualLayout.lead; return { e, cost: C.costOf(C.slotBy.lead), rz: C.state.resize.lead }; }")
        self.assertAlmostEqual(got["e"]["heightIn"], before["lead"]["heightIn"] + 1.0, delta=0.06)
        self.assertAlmostEqual(got["cost"], got["e"]["heightIn"] * got["e"]["span"], delta=0.1, msg="the words Clark is asked for fill the frame")
        self.assertEqual(got["rz"]["direction"], "expand")
        h = self.js("""() => { const r = document.querySelector('.blk[data-slot="lead"] .handle.wid').getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; }""")
        self.drag(h["x"], h["y"], h["x"] - (self.colw - 0.1) * self.ppi, h["y"], steps=10)
        narrow = self.js("() => { const C = BudgetPage.core; return { e: C.state.manualLayout.lead, cost: C.costOf(C.slotBy.lead) }; }")
        self.assertEqual(narrow["e"]["span"], 1)
        self.assertAlmostEqual(narrow["e"]["heightIn"], narrow["cost"], delta=0.06, msg="same words, re-flowed into one column")
        after = self.js("() => JSON.parse(JSON.stringify(BudgetPage.core.state.manualLayout))")
        self.assertEqual({k: v for k, v in after.items() if k != "lead"}, {k: v for k, v in before.items() if k != "lead"})
        # The comic is art: its bottom edge resizes the picture and asks Clark for no words.
        h = self.js("""() => { const r = document.querySelector('.blk[data-slot="comic"] .handle.len').getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; }""")
        self.drag(h["x"], h["y"], h["x"], h["y"] - 0.5 * self.ppi, steps=8)
        self.assertIsNone(self.js("() => BudgetPage.core.state.resize.comic || null"))

    def test_overlap_warns_without_moving_the_pages_and_overset_hangs_past_the_trim(self):
        tops0 = self.cols_tops()
        banner0 = self.js("() => { const b = document.querySelector('#overlap'); return { hidden: b.hidden, h: b.getBoundingClientRect().height, calm: b.classList.contains('calm') }; }")
        self.assertFalse(banner0["hidden"])
        self.assertTrue(banner0["calm"])
        cobra = self.frame("signup-cobra")
        nac = self.frame("nac-preview")
        self.move_by("nac-preview", self.colw, cobra["topIn"] - nac["topIn"] + 0.3, ".h")  # onto the Cobra table
        banner1 = self.js("() => { const b = document.querySelector('#overlap'); return { hidden: b.hidden, h: b.getBoundingClientRect().height, calm: b.classList.contains('calm'), text: b.textContent }; }")
        self.assertFalse(banner1["calm"])
        self.assertIn("Overlap", banner1["text"])
        self.assertEqual(banner1["h"], banner0["h"], "the overlap line keeps its height")
        self.assertEqual(self.cols_tops(), tops0, "showing the overlap warning did not push the pages")
        self.assertTrue(self.js("() => document.querySelector('.blk[data-slot=\"nac-preview\"]').classList.contains('overlap')"))
        self.assertTrue(any(n["kind"] == "overlap" for n in self.js("() => BudgetPage.core.needs()")))
        stays = self.frame("nac-preview")
        self.assertEqual(stays["col"], 1)
        # Overset: drag a block low on page 2 so it runs past the trim. It hangs; it is not moved for Frank.
        H = self.js("() => BudgetPage.core.pageH(2)")
        sec = self.frame("secondary-a")
        self.move_by("secondary-a", 0, H - 1.0 - sec["topIn"], ".h")
        hang = self.frame("secondary-a")
        self.assertAlmostEqual(hang["topIn"], H - 1.0, delta=0.06)
        self.assertGreater(hang["topIn"] + hang["heightIn"], H)
        vis = self.js("""() => { const b = document.querySelector('.cols[data-page="2"] .blk[data-slot="secondary-a"]');
          return { spill: b.classList.contains('spill'), hang: !!b.querySelector('.hang'), trim: !!document.querySelector('.cols[data-page="2"] .trim'),
                   foot: document.querySelector('.page[data-page="2"] .pfoot').textContent, well: !!document.querySelector('.cols[data-page="2"] .spillwell') }; }""")
        self.assertTrue(vis["spill"] and vis["hang"] and vis["trim"] and vis["well"], vis)
        self.assertIn("OVERSET", vis["foot"])

    def test_click_still_opens_the_slip_and_escape_cancels_a_drag(self):
        p = self.point("lead", ".h")
        self.page.mouse.click(p["x"], p["y"])
        self.assertTrue(self.js("() => !!document.querySelector('#side .sheet[data-slot=\"lead\"]')"), "a click on a block opens its slip in Manual")
        start = self.frame("lead")
        m = self.page.mouse
        m.move(p["x"], p["y"]); m.down()
        for i in range(1, 9):
            m.move(p["x"], p["y"] + i * 25)
        self.assertTrue(self.js("() => !!document.querySelector('.drag-ghost')"))
        self.page.keyboard.press("Escape")
        m.up()
        self.assertEqual(self.frame("lead"), start)
        self.assertFalse(self.js("() => !!document.querySelector('.drag-ghost, .drop-outline, .blk.lifting')"))

    def test_undo_steps_back_through_each_gesture(self):
        start = self.js("() => JSON.parse(JSON.stringify(BudgetPage.core.state.manualLayout))")
        self.move_by("lead", 0, 4.6, ".h")
        self.move_by("nac-preview", 2 * self.colw, 2.0, ".h")
        b = self.bank_point()
        p = self.point("camp", ".h")
        self.drag(p["x"], p["y"], b["x"], b["y"])
        self.assertFalse(self.frame("camp")["on"])
        for _ in range(3):
            self.page.click("#undoplace")
        back = self.js("() => ({ L: JSON.parse(JSON.stringify(BudgetPage.core.state.manualLayout)), camp: BudgetPage.core.state.inc.camp })")
        self.assertTrue(back["camp"])
        for k in ("lead", "nac-preview", "camp"):
            self.assertEqual(back["L"][k], start[k], k)
        # One more undo leaves Manual (the switch itself is a step); Auto takes over.
        self.page.click("#undoplace")
        self.assertEqual(self.js("() => BudgetPage.core.submission().mode"), "auto")

    def test_auto_mode_drags_still_work_and_off_the_left_edge_is_the_bank(self):
        self.page.once("dialog", lambda d: d.accept())
        self.page.click("#toauto")
        self.page.wait_for_selector("body:not(.manual)")
        self.assertEqual(self.js("() => BudgetPage.core.submission().mode"), "auto")
        self.assertTrue(self.js("() => document.querySelector('.cols .blk[data-slot=\"lead\"]').getAttribute('draggable') === 'true'"))
        p = self.point("camp", ".h")
        edge = self.js("() => document.querySelector('.page[data-page=\"1\"]').getBoundingClientRect().left")
        self.drag(p["x"], p["y"], edge - 6, p["y"] + 40)
        self.assertFalse(self.js("() => BudgetPage.core.state.inc.camp"), "Auto: off page 1's left edge is the bank too")
        s = self.js("""() => { const el = document.querySelector('#bank .strip[data-slot="camp"]'); el.scrollIntoView({ block: 'center' });
          const r = el.getBoundingClientRect(), c = document.querySelector('.cols[data-page="2"]').getBoundingClientRect();
          return { x: r.x + 40, y: r.y + 14, tx: c.x + 60, ty: c.y + 60 }; }""")
        self.drag(s["x"], s["y"], s["tx"], s["ty"])
        self.assertTrue(self.js("() => BudgetPage.core.state.inc.camp && BudgetPage.core.state.page.camp === 2"))


if __name__ == "__main__":
    unittest.main(verbosity=1)
