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
NEW_OPTIONAL = ["publishDateAlt", "budgetVersion", "dataVersion"]


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
        for a in ("page.html", "page.css", "core.js", "ui.js"):
            self.assertTrue((SCRIPTS / "budget_page" / a).is_file())

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
        self.assertEqual([e["slot"] for e in doc["includedSlots"]], [k for k in dec["order"] if k in dec["included"]])
        self.assertEqual(doc["publishDate"], dec["publishDate"])
        self.assertEqual(doc["slotNotes"], {k: v.strip() for k, v in dec["slotNotes"].items()})
        for a in dec["answers"]:  # nothing Frank already answered is dropped, including answers given by chat
            self.assertIn((a["slot"], a["answer"]), [(x["slot"], x["answer"]) for x in doc["answers"]])

    def test_alternate_date_vets_and_page_moves_reach_the_document(self):
        doc = node(self.data, """
          const bank = C.slots.find(s => !s.empty && !C.state.inc[s.key]), photo = Object.keys(C.media).find(id => !C.vettedOnFile(id)), loose = C.loosePhotos[0];
          C.act.alt('2026-11-19'); C.act.place(bank.key, 2); C.act.vet(photo, 'crop ok'); C.act.photo(loose, true, 1);
          const a = C.submission(); C.act.alt(''); const b = C.submission();
          out = { a, b, bank: bank.key, photo, loose };""")
        a = doc["a"]
        self.assertEqual(a["publishDateAlt"], "2026-11-19")
        self.assertIsNone(doc["b"]["publishDateAlt"])
        self.assertIn(doc["bank"], [e["slot"] for e in a["includedSlots"]])
        self.assertIn(f"({doc['bank']}) on page 2", a["notes"])  # page placement rides in notes: the contract has no page field
        self.assertIn({"id": doc["photo"], "vet_notes": "crop ok"}, a["vets"])  # photo vets are collected (media id + note)
        self.assertIn(doc["loose"], a["photoIncludes"])

    def test_no_decisions_yet_starts_from_the_desks_proposal(self):
        data = dict(self.data, decisions=None)
        doc = node(data, "out = { d: C.submission(), needs: C.needs().length };")
        proposed = [s["key"] for s in self.data["lineup"]["slots"] if s.get("proposed") and not s.get("waiting") and not s.get("empty")]
        self.assertEqual(sorted(e["slot"] for e in doc["d"]["includedSlots"]), sorted(proposed))
        self.assertEqual(doc["d"]["publishDateAlt"], self.data["lineup"]["publish"].get("alt"))

    def test_blocks_and_holes_account_for_each_page(self):
        res = node(self.data, """
          const snap = () => [1, 2].map(p => { const r = C.pack(p); return { cap: r.cap, placed: r.placedUsed, open: r.open, over: r.overset, used: r.used }; });
          const a = snap(); C.slots.filter(s => !s.empty).forEach(s => C.act.place(s.key, 2)); const b = snap();
          out = { a, b, fill: C.fill() };""")
        for pg in res["a"] + res["b"]:
            self.assertAlmostEqual(pg["placed"] + pg["open"], pg["cap"], delta=0.15)       # holes + blocks = the page
            self.assertAlmostEqual(pg["placed"] + pg["over"], pg["used"], delta=0.15)      # what doesn't fit is overset, not lost
        self.assertGreater(res["b"][1]["over"], 0)  # everything on page 2 cannot fit

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
          const k = C.slots.find(s => !s.empty && !C.state.inc[s.key]).key;
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

    def test_photo_vets_are_collected_but_never_written_to_the_manifest(self):
        manifest = json.loads(self.manifest_before)
        pid = next(m["id"] for m in manifest["items"] if not m.get("vetted"))
        r = self.ingest(dict(self.base(), vets=[{"id": pid, "vet_notes": "fine to run"}]))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.week / "media" / "manifest.json").read_bytes(), self.manifest_before)
        self.assertIn(pid, self.last_decision()["vets"])  # on the decision log and in the stored submission only
        self.assertIn(pid, [v["id"] for v in json.loads((self.subs / "approvals.json").read_text(encoding="utf-8"))["vets"]])

    @unittest.skipUnless(NODE, "node not installed")
    def test_page_document_round_trips_through_ingest_and_the_next_build(self):
        _, _, data = build(self.tmp, "--preview")
        doc = node(data, "C.act.alt('2026-11-19'); const k = C.slots.find(s => !s.empty && !C.state.inc[s.key]).key; C.act.place(k, 1); out = C.submission();")
        r = self.ingest(doc)
        self.assertEqual(r.returncode, 0, r.stderr)
        d = self.last_decision()
        self.assertEqual(d["included"], [e["slot"] for e in doc["includedSlots"]])
        self.assertEqual(d["publishDateAlt"], "2026-11-19")
        r2, _, data2 = build(self.tmp)  # the next numbered budget starts from it, alternate date included
        self.assertEqual(r2.returncode, 0, r2.stderr)
        again = node(data2, "out = C.submission();")
        self.assertEqual(again["publishDateAlt"], "2026-11-19")
        self.assertEqual([e["slot"] for e in again["includedSlots"]], d["included"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
