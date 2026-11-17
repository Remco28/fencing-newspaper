#!/usr/bin/env python3
"""Budget page (the two-page spread): builder, submission contract, ingest, capacity model.
No Chrome, no network. The JS logic (scripts/budget_page/core.js) runs under node; those tests skip without it.
Everything is written to temp dirs: the real staging week, submissions and version log are never touched.
Run: python3 scripts/tests/test_budget_page.py      (optional Chrome check: scripts/tests/smoke_budget_chrome.py)"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))
import budget_model  # noqa: E402

NODE = shutil.which("node")
LINEUP = REPO / "budget-demo" / "practice-lineup.json"
WEEK = REPO / "staging" / "weeks" / "next"
OLD_FIELDS = ["publishDate", "practice", "pretend", "targetWeek", "issue", "includedSlots", "excludedSlots", "photoIncludes",
              "notes", "slotNotes", "answers", "order", "pageVersion", "submittedAt", "vets"]
NEW_OPTIONAL = ["publishDateAlt", "budgetVersion", "dataVersion", "pages", "resize", "layout"]


def run(*args, **kw):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, **kw)


def week_copy(tmp: Path) -> Path:
    """A throwaway staging week: items, media + manifest, version log."""
    wk = tmp / "week"
    shutil.copytree(WEEK / "media", wk / "media")
    for f in ("items.json", "budget-versions.json"):
        shutil.copy(WEEK / f, wk / f)
    return wk


def build(tmp: Path, *extra) -> tuple[subprocess.CompletedProcess, Path, dict]:
    wk = week_copy(tmp) if not (tmp / "week").is_dir() else tmp / "week"
    out = tmp / "out"
    r = run(SCRIPTS / "build_budget_html.py", "--staging-week", wk, "--out", out, "--allow-pending", *extra)
    pages = sorted(out.glob("*.html"), key=lambda p: p.stat().st_mtime) if out.is_dir() else []
    data = {}
    if pages:
        m = re.search(r'<script type="application/json" id="budget-data">(.*?)</script>', pages[-1].read_text(encoding="utf-8"), re.S)
        data = json.loads(m.group(1))
    return r, (pages[-1] if pages else out), data


def node(data: dict, body: str):
    """Run `body` (JS; `C` is the page core, `out` the result) against a build's inlined data."""
    with tempfile.TemporaryDirectory() as t:
        f = Path(t) / "data.json"
        f.write_text(json.dumps(data), encoding="utf-8")
        js = ("const C = require(%s).make(JSON.parse(require('fs').readFileSync(%s, 'utf8'))); let out;\n%s\nconsole.log(JSON.stringify(out));"
              % (json.dumps(str(SCRIPTS / "budget_page" / "core.js")), json.dumps(str(f)), body))
        r = subprocess.run([NODE, "-e", js], capture_output=True, text=True)
        if r.returncode:
            raise AssertionError(r.stderr[-1500:])
        return json.loads(r.stdout)


class Builder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.before = (WEEK / "budget-versions.json").read_text(encoding="utf-8")
        cls.r, cls.page, cls.data = build(cls.tmp)
        cls.html = cls.page.read_text(encoding="utf-8") if cls.page.is_file() else ""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_builds_one_file_named_and_versioned_as_before(self):
        self.assertEqual(self.r.returncode, 0, self.r.stderr)
        self.assertRegex(self.page.name, r"^budget-no-\d+-\d{4}-\d{2}-\d{2}-v\d+\.html$")
        log = json.loads((self.tmp / "week" / "budget-versions.json").read_text(encoding="utf-8"))
        self.assertEqual(log["versions"][-1]["v"], self.data["build"]["budgetVersion"])
        self.assertEqual(log["versions"][-1]["data"], self.data["build"]["dataVersion"])
        self.assertEqual((WEEK / "budget-versions.json").read_text(encoding="utf-8"), self.before, "the real version log was touched")
        self.assertIn("self-check: ok", self.r.stdout)

    def test_rebuild_with_same_inputs_keeps_its_number(self):
        r2, page2, data2 = build(self.tmp)
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertEqual(data2["build"]["budgetVersion"], self.data["build"]["budgetVersion"])

    def test_preview_is_not_numbered_or_logged(self):
        with tempfile.TemporaryDirectory() as t:
            r, page, data = build(Path(t), "--preview")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(page.name.endswith("-preview.html"))
            self.assertIsNone(data["build"]["budgetVersion"])
            self.assertEqual((Path(t) / "week" / "budget-versions.json").read_text(encoding="utf-8"), self.before)

    def test_page_is_the_budget_spread_offline(self):
        self.assertIn("default-src 'none'", self.html)
        self.assertIn("<title>Budget — ", self.html)
        self.assertIn("Sign off the budget", self.html)
        code = re.sub(r'<script type="application/json" id="budget-data">.*?</script>', "", self.html, flags=re.S)
        self.assertNotRegex(code, r"(?i)dummy")  # the mockup's working name is gone from everything Frank sees
        self.assertNotRegex(code, r"\bfetch\(|XMLHttpRequest|<link\b|src=[\"']https?:")
        self.assertEqual(self.data["build"]["pageVersion"], "budget-paper-v1")
        for a in ("page.html", "page.css", "core.js", "ui.js", "layouts.json"):
            self.assertTrue((SCRIPTS / "budget_page" / a).is_file())
        self.assertIn("layouts", self.data)
        self.assertEqual(self.data["layouts"]["variants"], ["wide", "tall"])

    def test_history_is_derived_fresh_and_inlined(self):
        h = self.data["sectionHistory"]
        published = sorted(e["number"] for e in json.loads((REPO / "site" / "issues.json").read_text(encoding="utf-8")))
        self.assertEqual([i["number"] for i in h["issues"]], published)  # a proof (No. 7) is not history until it is published
        self.assertTrue(h["slotSections"] and "evidence" in h["sections"][0])
        self.assertIn("On the Road", [u["name"] for u in h["unregistered"]])

    def test_calibrated_capacity_is_inlined_over_the_lineup(self):
        cal = budget_model.load_calibration()
        self.assertIsNotNone(cal, "scripts/budget_page/calibration.json missing")
        lineup = json.loads(LINEUP.read_text(encoding="utf-8"))
        self.assertEqual(self.data["capacity"], budget_model.merged_capacity(lineup["capacity"], cal))
        self.assertEqual(self.data["lineup"]["capacity"], lineup["capacity"])  # the lineup itself is inlined untouched
        for k in ("wpi", "gap", "row_rail", "page1_col_in"):
            self.assertEqual(self.data["capacity"][k], cal["capacity"][k])

    def test_refuses_pending_submission_flag_still_exists(self):
        r = run(SCRIPTS / "build_budget_html.py", "--help")
        for flag in ("--lineup", "--staging-week", "--out", "--thumb-width", "--quality", "--preview", "--allow-pending"):
            self.assertIn(flag, r.stdout)


@unittest.skipUnless(NODE, "node not installed: page-logic tests skipped")
class PageLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        _, _, cls.data = build(cls.tmp, "--preview")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_submission_has_every_existing_field_plus_the_optional_ones(self):
        doc = node(self.data, "out = C.submission(new Date(2026, 10, 16, 22, 0, 0));")
        self.assertEqual(list(doc)[:len(OLD_FIELDS)], OLD_FIELDS)
        self.assertEqual(sorted(set(doc) - set(OLD_FIELDS)), sorted(NEW_OPTIONAL))
        self.assertEqual(doc["pageVersion"], "budget-paper-v1")
        self.assertRegex(doc["publishDate"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(doc["dataVersion"], self.data["build"]["dataVersion"])
        self.assertIn("budgetVersion", doc)
        for e in doc["includedSlots"] + doc["excludedSlots"]:
            self.assertEqual([k for k in e if k != "empty"], ["slot", "name", "headline", "itemId", "vetted", "stale"])
        keys = {s["key"] for s in self.data["lineup"]["slots"]}
        self.assertTrue(keys <= {e["slot"] for e in doc["includedSlots"] + doc["excludedSlots"]})
        self.assertTrue(set(doc["order"]) <= {e["slot"] for e in doc["includedSlots"] + doc["excludedSlots"]})
        self.assertIsInstance(doc["slotNotes"], dict)
        self.assertRegex(doc["submittedAt"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$")

    def test_starts_from_the_latest_decision(self):
        dec = self.data["decisions"]
        doc = node(self.data, "out = C.submission();")
        known = {s["key"] for s in self.data["lineup"]["slots"]}
        self.assertEqual([e["slot"] for e in doc["includedSlots"]], [k for k in dec["order"] if k in dec["included"] and k in known])
        self.assertEqual(doc["publishDate"], dec["publishDate"])
        self.assertEqual(doc["slotNotes"], {k: v.strip() for k, v in dec["slotNotes"].items()})
        for a in dec["answers"]:  # nothing Frank already answered is dropped, including answers given by chat
            self.assertIn((a["slot"], a["answer"]), [(x["slot"], x["answer"]) for x in doc["answers"]])

    def test_alternate_date_vets_and_page_moves_reach_the_document(self):
        doc = node(self.data, """
          const bank = C.slots.find(s => !s.empty && !C.state.inc[s.key] && C.canPlace(s))
                    || C.slots.find(s => !s.empty && !C.state.inc[s.key]);
          const photo = Object.keys(C.media).find(id => !C.vettedOnFile(id));
          const loose = C.loosePhotos.find(id => C.canPlacePhoto(id)) || C.loosePhotos[0];
          C.act.alt('2026-11-19');
          if (!C.canPlace(bank)) C.act.vet(bank.item, 'ok to run');
          C.act.place(bank.key, 2);
          C.act.vet(photo, 'crop ok');
          if (!C.canPlacePhoto(loose)) C.act.vet(loose, 'ok');
          C.act.photo(loose, true, 1);
          const a = C.submission(); C.act.alt(''); const b = C.submission();
          out = { a, b, bank: bank.key, photo, loose, notes: a.notes };""")
        a = doc["a"]
        self.assertEqual(a["publishDateAlt"], "2026-11-19")
        self.assertIsNone(doc["b"]["publishDateAlt"])
        self.assertIn(doc["bank"], [e["slot"] for e in a["includedSlots"]])
        self.assertNotIn("Budget placement", a["notes"] or "")
        self.assertEqual(a["pages"]["slots"][doc["bank"]], 2)
        self.assertIn({"id": doc["photo"], "vet_notes": "crop ok"}, a["vets"])
        self.assertIn(doc["loose"], a["photoIncludes"])
        self.assertEqual(a["pages"]["photos"].get(doc["loose"]), 1)

    def test_unvetted_items_cannot_be_placed_until_vetted(self):
        res = node(self.data, """
          const s = C.slots.find(x => !x.empty && !C.canPlace(x));
          const photo = C.loosePhotos.find(id => !C.canPlacePhoto(id));
          const before = { inc: !!(s && C.state.inc[s.key]), photo: !!(photo && C.state.photos[photo]) };
          if (s) C.act.place(s.key, 1);
          if (photo) C.act.photo(photo, true, 1);
          const refused = { inc: !!(s && C.state.inc[s.key]), photo: !!(photo && C.state.photos[photo]),
                            docInc: !!(s && C.submission().includedSlots.some(e => e.slot === s.key)),
                            docPhoto: !!(photo && C.submission().photoIncludes.includes(photo)) };
          if (s) { (C.allItemsOf(s).filter(i => !C.isVetted(i.id))).forEach(i => C.act.vet(i.id, 'ok')); const m = C.mediaOfSlot(s); if (m && !C.isVetted(m.id)) C.act.vet(m.id, 'ok'); C.act.place(s.key, 1); }
          if (photo) { C.act.vet(photo, 'ok'); C.act.photo(photo, true, 2); }
          const placed = { inc: !!(s && C.state.inc[s.key]), page: s ? C.submission().pages.slots[s.key] : null,
                           photo: !!(photo && C.submission().photoIncludes.includes(photo)), photoPage: photo ? C.submission().pages.photos[photo] : null };
          if (s) { C.allItemsOf(s).forEach(i => { if (i.id in C.state.vets) C.act.unvet(i.id); }); }
          if (photo) C.act.unvet(photo);
          const after = { inc: !!(s && C.state.inc[s.key]), photo: !!(photo && C.state.photos[photo]) };
          out = { hasSlot: !!s, hasPhoto: !!photo, slot: s && s.key, photo, before, refused, placed, after };
        """)
        self.assertTrue(res["hasSlot"] or res["hasPhoto"], "fixture has no unvetted slot or photo to exercise")
        self.assertFalse(res["refused"]["inc"])
        self.assertFalse(res["refused"]["photo"])
        self.assertFalse(res["refused"]["docInc"])
        self.assertFalse(res["refused"]["docPhoto"])
        if res["hasSlot"]:
            self.assertTrue(res["placed"]["inc"])
            self.assertEqual(res["placed"]["page"], 1)
            self.assertFalse(res["after"]["inc"])  # unvet returns it to the bank
        if res["hasPhoto"]:
            self.assertTrue(res["placed"]["photo"])
            self.assertEqual(res["placed"]["photoPage"], 2)
            self.assertFalse(res["after"]["photo"])

    def test_unvetted_photos_are_never_auto_queued(self):
        # A proposed unvetted photo, or one left in last sitting's photoIncludes, stays off the pages.
        res = node(self.data, """
          const pid = C.loosePhotos.find(id => !C.vettedOnFile(id)) || Object.keys(C.media).find(id => !C.vettedOnFile(id));
          out = { pid, defaultOn: pid && C.state.photos[pid] };
        """)
        if not res["pid"]:
            self.skipTest("no unvetted photo in the fixture")
        self.assertFalse(res["defaultOn"])
        data = dict(self.data)
        data = json.loads(json.dumps(self.data))
        data["decisions"] = dict(data.get("decisions") or {}, photoIncludes=[res["pid"]], included=list((data.get("decisions") or {}).get("included") or []))
        # also mark it proposed on the lineup photo list
        photos = data["lineup"].setdefault("photos", [])
        entry = next((p for p in photos if p.get("id") == res["pid"]), None)
        if entry: entry["proposed"] = True
        else: photos.append({"id": res["pid"], "proposed": True, "span": 1})
        again = node(data, "const pid = %s; out = { on: !!C.state.photos[pid], inc: C.submission().photoIncludes };" % json.dumps(res["pid"]))
        self.assertFalse(again["on"])
        self.assertNotIn(res["pid"], again["inc"])

    def test_no_decisions_yet_starts_from_the_desks_proposal(self):
        data = dict(self.data, decisions=None)
        doc = node(data, "out = { d: C.submission(), needs: C.needs().length };")
        proposed = node(data, """
          out = C.slots.filter(s => s.proposed && !s.waiting && !s.empty && C.canPlace(s)).map(s => s.key);
        """)
        self.assertEqual(sorted(e["slot"] for e in doc["d"]["includedSlots"]), sorted(proposed))
        self.assertEqual(doc["d"]["publishDateAlt"], self.data["lineup"]["publish"].get("alt"))

    def test_blocks_and_holes_account_for_each_page(self):
        res = node(self.data, """
          const snap = () => [1, 2].map(p => { const r = C.pack(p); return { cap: r.cap, placed: r.placedUsed, open: r.open, over: r.overset, used: r.used }; });
          const a = snap(); C.slots.filter(s => !s.empty && C.canPlace(s)).forEach(s => C.act.place(s.key, 2)); const b = snap();
          out = { a, b, fill: C.fill() };""")
        for pg in res["a"] + res["b"]:
            self.assertAlmostEqual(pg["placed"] + pg["open"], pg["cap"], delta=0.15)       # holes + blocks = the page
            self.assertAlmostEqual(pg["placed"] + pg["over"], pg["used"], delta=0.15)      # what doesn't fit is overset, not lost
        self.assertGreater(res["b"][1]["over"], 0)  # everything on page 2 cannot fit
        # Overflow is also placed, hanging past the trim (not dropped from the packing).
        hang = node(self.data, """
          C.slots.filter(s => !s.empty && C.canPlace(s)).forEach(s => C.act.place(s.key, 2));
          const r = C.pack(2);
          out = { spillIn: r.spillIn, hanging: r.placed.filter(b => b.spill || b.hang > 0.02).length, over: r.over.length, H: r.H,
                  anyBelow: r.placed.some(b => b.y + b.h > r.H + 0.05) };
        """)
        self.assertGreater(hang["spillIn"], 0)
        self.assertGreater(hang["hanging"], 0)
        self.assertTrue(hang["anyBelow"])
        self.assertEqual(hang["hanging"], hang["over"])

    def test_resize_layout_and_art_span_reach_the_document(self):
        res = node(self.data, """
          const lead = C.slotBy.lead;
          const before = { cost: C.costOf(lead), words: C.wordsOf(lead), span: C.spanOf(lead) };
          C.act.setResize('lead', 'shrink', '80%');
          const mid = { cost: C.costOf(lead), words: C.wordsOf(lead), resize: C.submission().resize.lead };
          C.act.setLayout('lead', 'tall');
          const after = { span: C.spanOf(lead), layout: C.submission().layout.lead, cost: C.costOf(lead) };
          const photo = C.loosePhotos.find(id => C.canPlacePhoto(id)) || C.loosePhotos[0];
          if (photo && !C.canPlacePhoto(photo)) C.act.vet(photo, 'ok');
          C.act.photo(photo, true, 1);
          C.act.setSpan(photo, 3);
          const doc = C.submission();
          out = { before, mid, after, photo, pagesPhoto: doc.pages.photos[photo], layoutPhoto: doc.layout[photo],
                  canLead: C.canSwitchLayout(lead), layoutsInlined: !!(C.D.layouts && C.D.layouts.sections) };
        """)
        self.assertTrue(res["canLead"])
        self.assertTrue(res["layoutsInlined"])
        self.assertLess(res["mid"]["words"], res["before"]["words"])
        self.assertLess(res["mid"]["cost"], res["before"]["cost"])
        self.assertEqual(res["mid"]["resize"]["direction"], "shrink")
        self.assertEqual(res["mid"]["resize"]["toWords"], res["mid"]["words"])
        self.assertEqual(res["after"]["span"], 1)
        self.assertEqual(res["after"]["layout"], "tall")
        self.assertEqual(res["pagesPhoto"]["page"], 1)
        self.assertEqual(res["pagesPhoto"]["span"], 3)
        self.assertIn("widthIn", res["pagesPhoto"])
        self.assertIn("heightIn", res["pagesPhoto"])
        self.assertEqual(res["layoutPhoto"], "wide")

    def test_resize_and_layout_seed_from_a_previous_decision(self):
        data = dict(self.data, decisions=dict(self.data["decisions"] or {}, 
            resize={"lead": {"direction": "expand", "target": "125%", "toWords": 2000}},
            layout={"lead": "tall", "comic": "wide"},
            pages={"slots": {"lead": {"page": 2, "span": 1, "widthIn": 2.42, "heightIn": 6.0}}, "photos": {}}))
        # keep other decision fields; lead may not be included if decisions say otherwise — force include via node after seed
        res = node(data, """
          out = {
            layout: C.state.layout.lead,
            span: C.spanOf(C.slotBy.lead),
            page: C.state.page.lead,
            slotSpan: C.state.slotSpan.lead,
            resize: C.state.resize.lead,
            pages: C.submission().pages.slots.lead,
            layoutOut: C.submission().layout
          };
        """)
        self.assertEqual(res["layout"], "tall")
        self.assertEqual(res["span"], 1)
        self.assertEqual(res["page"], 2)
        self.assertEqual(res["slotSpan"], 1)
        self.assertEqual(res["resize"]["direction"], "expand")
        self.assertEqual(res["pages"]["page"], 2)
        self.assertEqual(res["pages"]["span"], 1)
        self.assertEqual(res["layoutOut"]["lead"], "tall")
        self.assertEqual(res["layoutOut"]["comic"], "wide")

    def test_no_user_facing_desk_copy(self):
        """User-facing copy says Clark, not desk. Internal ids, classes, and property names may stay."""
        hits = []
        for name in ("core.js", "ui.js"):
            text = (SCRIPTS / "budget_page" / name).read_text(encoding="utf-8")
            text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
            text = re.sub(r"//.*?$", "", text, flags=re.M)
            for m in re.finditer(r"desk", text, flags=re.I):
                ctx = text[max(0, m.start() - 24):m.end() + 24]
                if re.search(r"desktop", ctx, re.I):
                    continue
                # internal: tab id, CSS class, deskPane, desk_summary, st.desk
                if re.search(r"st\.desk|desk_summary|deskPane|data-tab=[\"']desk[\"']|\.desk\b|[\"']desk[\"']|\{ desk:", ctx):
                    continue
                hits.append((name, " ".join(ctx.split())))
        self.assertEqual(hits, [], "user-facing string still says desk: " + repr(hits[:8]))

    def test_cost_model_matches_python(self):
        cap = self.data["capacity"]
        items = {i["id"]: i for i in self.data["items"]["items"]}
        got = node(self.data, "out = Object.fromEntries(C.slots.filter(s => s.cost).map(s => [s.key, C.costOf(s)]));")
        n = 0
        for s in self.data["lineup"]["slots"]:
            if not s.get("cost"):
                continue
            it = items.get(s.get("item")) or {}
            words = it.get("word_count") or len(str(it.get("body") or "").split())
            self.assertAlmostEqual(got[s["key"]], budget_model.cost_of(s["cost"], cap, words), places=6, msg=s["key"])
            n += 1
        self.assertGreater(n, 5)

    def test_in_this_budget_follows_the_includes(self):
        res = node(self.data, """
          const pick = () => { const R = C.sectionRows(); return Object.fromEntries(R.official.concat(R.unregistered).map(r => [r.id, { status: r.status, note: r.note, slots: r.slots, last: r.last, ran: r.ran, frequency: r.frequency }])); };
          const before = pick(), inKey = C.slots.find(s => C.state.inc[s.key] && C.sectionsOfSlot(s.key).length === 1).key, sec = C.sectionsOfSlot(inKey)[0].id;
          const others = C.slots.filter(s => C.state.inc[s.key] && C.sectionsOfSlot(s.key).some(r => r.id === sec)).map(s => s.key);
          others.forEach(k => C.act.include(k, false)); const after = pick();
          out = { before, after, sec };""")
        sec = res["sec"]
        self.assertEqual(res["before"][sec]["status"], "in")
        self.assertEqual(res["after"][sec]["status"], "out")
        self.assertTrue(res["after"][sec]["note"])  # absence note
        self.assertIn("u:On the Road", res["before"])  # unregistered kicker row, matched to this week's slot
        self.assertIn("on-the-road", res["before"]["u:On the Road"]["slots"])
        self.assertTrue(res["before"]["featured-bout"]["note"].startswith("Has never run."))
        self.assertEqual(res["before"]["lead-story"]["frequency"], "every_issue")

    def test_autosave_round_trip_and_supersede(self):
        res = node(self.data, """
          const s = C.slots.find(s => !s.empty && !C.state.inc[s.key] && C.canPlace(s)) || C.slots.find(s => !s.empty && !C.state.inc[s.key]);
          if (!C.canPlace(s)) { C.allItemsOf(s).forEach(i => C.act.vet(i.id, 'ok')); const m = C.mediaOfSlot(s); if (m) C.act.vet(m.id, 'ok'); }
          const k = s.key;
          C.act.place(k, 1); C.act.notes('hold the comic'); const saved = JSON.parse(JSON.stringify(C.serialize(new Date('2030-01-01T00:00:00Z'))));
          out = { k, saved };""")
        fresh = node(self.data, "const r = C.restore(%s); out = { r, inc: C.state.inc[%s], notes: C.state.notes, page: C.state.page[%s] };"
                     % (json.dumps(res["saved"]), json.dumps(res["k"]), json.dumps(res["k"])))
        self.assertTrue(fresh["r"]["restored"] and fresh["inc"] and fresh["page"] == 1)
        self.assertEqual(fresh["notes"], "hold the comic")
        old = dict(res["saved"], savedAt="2020-01-01T00:00:00Z")  # saved before the latest ingested decision: superseded
        stale = node(self.data, "const r = C.restore(%s); out = { r, inc: C.state.inc[%s] };" % (json.dumps(old), json.dumps(res["k"])))
        self.assertTrue(stale["r"]["superseded"])
        self.assertFalse(stale["inc"])


class Ingest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.week = week_copy(self.tmp)
        self.subs = self.tmp / "subs"
        self.manifest_before = (self.week / "media" / "manifest.json").read_bytes()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ingest(self, payload, *extra):
        f = self.tmp / "budget-submission-test.json"
        f.write_text(json.dumps(payload) if not isinstance(payload, str) else payload, encoding="utf-8")
        return run(SCRIPTS / "ingest_budget_submission.py", f, "--staging-week", self.week, "--submissions", self.subs,
                   "--lineup", LINEUP, "--now", "2026-11-16T23:00:00-05:00", *extra)

    def last_decision(self):
        return json.loads((self.week / "budget-versions.json").read_text(encoding="utf-8"))["decisions"][-1]

    def base(self):
        return json.loads((REPO / "issues" / "2026-11-17" / "budget-submission.json").read_text(encoding="utf-8"))

    def test_published_submissions_still_ingest(self):
        files = sorted((REPO / "issues").glob("*/budget-submission.json"))
        self.assertGreaterEqual(len(files), 6)
        for f in files:  # Nos. 1-6 and the No. 7 file: older schemas, no budgetVersion / dataVersion / alt date
            r = run(SCRIPTS / "ingest_budget_submission.py", f, "--staging-week", self.week, "--submissions", self.subs,
                    "--lineup", LINEUP, "--now", "2026-11-16T23:00:00-05:00", "--force")
            self.assertEqual(r.returncode, 0, f"{f}: {r.stderr}")
            d = self.last_decision()
            self.assertEqual(d["publishDate"], json.loads(f.read_text(encoding="utf-8"))["publishDate"])
            self.assertNotIn("publishDateAlt", d)
            self.assertNotIn("budgetVersion", d)
        self.assertEqual((self.week / "media" / "manifest.json").read_bytes(), self.manifest_before)

    def test_current_issue_file_ingests_without_force(self):
        r = self.ingest(self.base())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.subs / "approvals.json").is_file())

    def test_alternate_date_and_versions_are_stored_when_present(self):
        p = dict(self.base(), pageVersion="budget-paper-v1", publishDateAlt="2026-11-18", budgetVersion=5, dataVersion="abc123def456")
        r = self.ingest(p)
        self.assertEqual(r.returncode, 0, r.stderr)
        d = self.last_decision()
        self.assertEqual((d["publishDateAlt"], d["budgetVersion"], d["dataVersion"], d["pageVersion"]), ("2026-11-18", 5, "abc123def456", "budget-paper-v1"))
        self.assertIn("alternate 2026-11-18", r.stdout)
        stored = json.loads((self.subs / "approvals.json").read_text(encoding="utf-8"))
        self.assertEqual(stored["publishDateAlt"], "2026-11-18")

    def test_null_alternate_means_no_alternate_and_bad_one_is_rejected(self):
        self.assertEqual(self.ingest(dict(self.base(), publishDateAlt=None)).returncode, 0)
        self.assertIsNone(self.last_decision()["publishDateAlt"])
        n = len(json.loads((self.week / "budget-versions.json").read_text(encoding="utf-8"))["decisions"])
        r = self.ingest(dict(self.base(), publishDateAlt="next Wednesday"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("publishDateAlt", r.stderr)
        self.assertEqual(len(json.loads((self.week / "budget-versions.json").read_text(encoding="utf-8"))["decisions"]), n)

    def test_missing_or_older_budget_version_never_blocks(self):
        for extra in ({}, {"budgetVersion": 1}, {"budgetVersion": None, "dataVersion": None}, {"budgetVersion": 999, "dataVersion": "not-the-current-build"}):
            r = self.ingest(dict(self.base(), **extra))
            self.assertEqual(r.returncode, 0, f"{extra}: {r.stderr}")
        self.assertNotIn("--allow-stale", run(SCRIPTS / "ingest_budget_submission.py", "--help").stdout)

    def test_photo_vets_are_written_to_the_manifest(self):
        manifest = json.loads(self.manifest_before)
        pid = next(m["id"] for m in manifest["items"] if not m.get("vetted"))
        r = self.ingest(dict(self.base(), vets=[{"id": pid, "vet_notes": "fine to run"}]))
        self.assertEqual(r.returncode, 0, r.stderr)
        after = json.loads((self.week / "media" / "manifest.json").read_text(encoding="utf-8"))
        entry = next(m for m in after["items"] if m["id"] == pid)
        self.assertTrue(entry["vetted"])
        self.assertEqual(entry["vetted_by"], "frank")
        self.assertEqual(entry["vetted_at"], "2026-11-16T23:00:00-05:00")
        self.assertIn("Frank: fine to run", entry["vet_notes"])
        self.assertIn(pid, self.last_decision()["vets"])
        self.assertIn(pid, [v["id"] for v in json.loads((self.subs / "approvals.json").read_text(encoding="utf-8"))["vets"]])
        # re-ingest does not drop the note
        r2 = self.ingest(dict(self.base(), vets=[{"id": pid, "vet_notes": "fine to run"}]))
        self.assertEqual(r2.returncode, 0, r2.stderr)
        again = json.loads((self.week / "media" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(next(m for m in again["items"] if m["id"] == pid)["vet_notes"].count("Frank: fine to run"), 1)

    def test_ingest_rejects_unvetted_included_items_and_photos(self):
        # pick a real unvetted item and photo in the copied week
        items = {i["id"]: i for i in json.loads((self.week / "items.json").read_text(encoding="utf-8"))["items"]}
        iid = next(i for i, it in items.items() if not it.get("vetted"))
        pid = next(m["id"] for m in json.loads((self.week / "media" / "manifest.json").read_text(encoding="utf-8"))["items"] if not m.get("vetted"))
        n = len(json.loads((self.week / "budget-versions.json").read_text(encoding="utf-8"))["decisions"])
        payload = dict(self.base(), includedSlots=list(self.base()["includedSlots"]) + [
            {"slot": "college", "name": "College", "headline": "x", "itemId": iid, "vetted": False, "stale": False}
        ])
        r = self.ingest(payload)
        self.assertEqual(r.returncode, 4, r.stderr + r.stdout)
        self.assertIn(iid, r.stderr)
        self.assertIn("Nothing written", r.stderr)
        self.assertEqual(len(json.loads((self.week / "budget-versions.json").read_text(encoding="utf-8"))["decisions"]), n)
        r2 = self.ingest(dict(self.base(), photoIncludes=[pid]))
        self.assertEqual(r2.returncode, 4, r2.stderr + r2.stdout)
        self.assertIn(pid, r2.stderr)
        self.assertEqual((self.week / "media" / "manifest.json").read_bytes(), self.manifest_before)
        # same sitting: a vet in the payload allows the include
        r3 = self.ingest(dict(payload, vets=[{"id": iid, "vet_notes": "ok"}]))
        self.assertEqual(r3.returncode, 0, r3.stderr)
        self.assertIn("college", self.last_decision()["included"])
        self.assertTrue(next(i for i in json.loads((self.week / "items.json").read_text(encoding="utf-8"))["items"] if i["id"] == iid)["vetted"])
        r4 = self.ingest(dict(self.base(), photoIncludes=[pid], vets=[{"id": pid, "vet_notes": "ok"}]))
        self.assertEqual(r4.returncode, 0, r4.stderr)
        self.assertIn(pid, self.last_decision()["photoIncludes"])
        self.assertTrue(next(m for m in json.loads((self.week / "media" / "manifest.json").read_text(encoding="utf-8"))["items"] if m["id"] == pid)["vetted"])

    def test_pages_are_stored_and_old_submissions_without_them_still_ingest(self):
        pages = {"slots": {"lead": 1, "comic": 2}, "photos": {}}
        r = self.ingest(dict(self.base(), pages=pages, pageVersion="budget-paper-v1"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.last_decision()["pages"], pages)
        r2 = self.ingest(self.base())  # no pages field
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertNotIn("pages", self.last_decision())
        r3 = self.ingest(dict(self.base(), pages={"slots": {"lead": 3}}))
        self.assertEqual(r3.returncode, 1)
        self.assertIn("pages.slots.lead", r3.stderr)
        sized = {"slots": {"lead": {"page": 1, "span": 2, "widthIn": 4.96, "heightIn": 4.0}}, "photos": {}}
        r4 = self.ingest(dict(self.base(), pages=sized, resize={"lead": {"direction": "shrink", "target": "80%"}}, layout={"lead": "tall"}))
        self.assertEqual(r4.returncode, 0, r4.stderr)
        d = self.last_decision()
        self.assertEqual(d["pages"], sized)
        self.assertEqual(d["resize"]["lead"]["direction"], "shrink")
        self.assertEqual(d["layout"]["lead"], "tall")
        r5 = self.ingest(dict(self.base(), layout={"lead": "sideways"}))
        self.assertEqual(r5.returncode, 1)
        self.assertIn("layout.lead", r5.stderr)
        r6 = self.ingest(self.base())  # no resize/layout
        self.assertEqual(r6.returncode, 0, r6.stderr)
        self.assertNotIn("resize", self.last_decision())
        self.assertNotIn("layout", self.last_decision())

    @unittest.skipUnless(NODE, "node not installed")
    def test_page_document_round_trips_through_ingest_and_the_next_build(self):
        _, _, data = build(self.tmp, "--preview")
        doc = node(data, """
          C.act.alt('2026-11-19');
          const s = C.slots.find(s => !s.empty && !C.state.inc[s.key] && C.canPlace(s)) || C.slots.find(s => !s.empty && !C.state.inc[s.key]);
          if (!C.canPlace(s)) { C.allItemsOf(s).forEach(i => C.act.vet(i.id, 'ok')); const m = C.mediaOfSlot(s); if (m) C.act.vet(m.id, 'ok'); }
          C.act.place(s.key, 1);
          out = C.submission();
        """)
        r = self.ingest(doc)
        self.assertEqual(r.returncode, 0, r.stderr)
        d = self.last_decision()
        self.assertEqual(d["included"], [e["slot"] for e in doc["includedSlots"]])
        self.assertEqual(d["publishDateAlt"], "2026-11-19")
        self.assertEqual(d["pages"], doc["pages"])
        r2, _, data2 = build(self.tmp)  # the next numbered budget starts from it, alternate date and pages included
        self.assertEqual(r2.returncode, 0, r2.stderr)
        again = node(data2, "out = C.submission();")
        self.assertEqual(again["publishDateAlt"], "2026-11-19")
        self.assertEqual([e["slot"] for e in again["includedSlots"]], d["included"])
        self.assertEqual(again["pages"]["slots"], d["pages"]["slots"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
