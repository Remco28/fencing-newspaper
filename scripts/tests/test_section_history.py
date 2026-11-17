#!/usr/bin/env python3
"""Section history: derived from the published issues, checked against the 2026-11-16 manual audit.
No Chrome, no network. Run: python3 scripts/tests/test_section_history.py"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "scripts"))
import build_section_history as bsh  # noqa: E402

AUDIT = json.loads((HERE / "fixtures" / "section-audit-2026-11-16.json").read_text(encoding="utf-8"))


def repo_copy(tmp: Path, extra_published=None) -> Path:
    """A throwaway repo with just what the deriver reads; optionally 'publish' more issues."""
    (tmp / "scripts").mkdir()
    for name in ("sections.json", bsh.RECORD):
        if (REPO / name).is_file():
            shutil.copy(REPO / name, tmp / name)
    (tmp / "site").mkdir()
    listed = json.loads((REPO / "site" / "issues.json").read_text(encoding="utf-8")) + list(extra_published or [])
    (tmp / "site" / "issues.json").write_text(json.dumps(listed), encoding="utf-8")
    for e in listed:
        dst = tmp / "issues" / e["date"]
        dst.mkdir(parents=True)
        for f in ("issue.html", "issue.json", "sources.json", "budget-submission.json"):
            if (REPO / "issues" / e["date"] / f).is_file():
                shutil.copy(REPO / "issues" / e["date"] / f, dst / f)
    return tmp


class Audit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h = bsh.build_history(REPO)
        cls.by_id = {s["id"]: s for s in cls.h["sections"]}

    def test_published_issues_only(self):
        nums = [i["number"] for i in self.h["issues"]]
        self.assertEqual(nums[:6], AUDIT["issues"])
        proof = json.loads((REPO / "issues" / "2026-11-17" / "issue.json").read_text(encoding="utf-8"))
        if "not approved" in proof.get("status", ""):  # No. 7 is a proof in this snapshot: must not count
            self.assertNotIn(7, nums)

    def test_every_registry_section_has_a_row_and_a_rule(self):
        reg = [s["id"] for s in json.loads((REPO / "sections.json").read_text(encoding="utf-8"))["sections"]]
        self.assertEqual([s["id"] for s in self.h["sections"]], reg)
        self.assertEqual(set(AUDIT["ran"]), set(reg), "audit fixture and sections.json list different sections")
        rules = json.loads(bsh.RULES.read_text(encoding="utf-8"))["sections"]
        self.assertEqual(set(rules), set(reg), "section_history_rules.json and sections.json list different sections")
        self.assertEqual(self.h["rules_for_unknown_sections"], [])

    def test_derived_history_matches_the_manual_audit(self):
        wrong = {}
        for sid, want in AUDIT["ran"].items():
            got = [n for n in self.by_id[sid]["ran"] if n in AUDIT["issues"]]
            if got != want:
                wrong[sid] = {"audit": want, "derived": got, "evidence": self.by_id[sid]["evidence"]}
        self.assertEqual(wrong, {}, "derived history disagrees with the audit:\n" + json.dumps(wrong, indent=1, ensure_ascii=False))

    def test_last_ran_and_evidence(self):
        for s in self.h["sections"]:
            self.assertEqual(s["last"], s["ran"][-1] if s["ran"] else None)
            self.assertEqual(sorted(s["evidence"]), sorted(str(n) for n in s["ran"]))
            self.assertTrue(all(s["evidence"][str(n)] for n in s["ran"]), s["id"])

    def test_unregistered_kickers(self):
        got = {u["name"]: u["ran"] for u in self.h["unregistered"]}
        for name, nums in AUDIT["unregistered_kickers_at_least"].items():
            self.assertEqual(got.get(name), nums, f"{name}: {got}")
        reg_names = {bsh.norm(s["name"]) for s in self.h["sections"]}
        self.assertFalse(reg_names & {bsh.norm(n) for n in got})

    def test_registry_last_ran_is_not_trusted(self):
        self.assertTrue(self.h["registry_last_ran_stale"], "sections.json last_ran matched everywhere? then drop this test")
        self.assertEqual(self.by_id["epee-on-screen"]["last"], 6)  # sections.json says 2

    def test_record_file_is_current(self):
        r = subprocess.run([sys.executable, str(REPO / "scripts" / "build_section_history.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout[-400:] + r.stderr[-400:])


class GoingForward(unittest.TestCase):
    """Nothing is keyed to issue numbers: publishing the next issue extends the history by itself."""

    def test_next_issue_counts_once_it_is_published(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = repo_copy(Path(t), [{"number": 7, "date": "2026-11-17", "headline": "x"}])
            h = bsh.build_history(tmp)
            self.assertEqual([i["number"] for i in h["issues"]], [1, 2, 3, 4, 5, 6, 7])
            ran7 = {s["id"] for s in h["sections"] if 7 in s["ran"]}
            # the No. 7 proof prints these kickers / boxes (new composer: rail-title kickers on every piece)
            for sid in ("lead-story", "by-the-book", "for-the-parents", "club-events", "nearby-tournaments", "deadlines", "comic", "secondary-articles"):
                self.assertIn(sid, ran7)
            self.assertNotIn("overheard-reddit", ran7)
            other = {u["name"]: u for u in h["unregistered"]}
            self.assertEqual(other["On the Road"]["ran"], [6, 7])
            self.assertIn("World Cup", other)  # topical kicker over a secondary story
            changed, _ = bsh.update_record(tmp)
            self.assertTrue(changed)
            rec = json.loads((tmp / bsh.RECORD).read_text(encoding="utf-8"))
            self.assertEqual(rec["issues"][-1]["number"], 7)
            self.assertFalse(bsh.update_record(tmp)[0], "second run must be a no-op")

    def test_overrides_survive_regeneration(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = repo_copy(Path(t))
            rec = json.loads((tmp / bsh.RECORD).read_text(encoding="utf-8"))
            rec["overrides"] = {"6": {"add": {"featured-bout": "test"}, "remove": {"comic": "test"}, "ignore_unregistered": ["On the Road"]}}
            (tmp / bsh.RECORD).write_text(json.dumps(rec), encoding="utf-8")
            _, h = bsh.update_record(tmp)
            by = {s["id"]: s for s in h["sections"]}
            self.assertEqual(by["featured-bout"]["ran"], [6])
            self.assertEqual(by["comic"]["ran"], [])
            self.assertNotIn("On the Road", [u["name"] for u in h["unregistered"]])
            self.assertEqual(json.loads((tmp / bsh.RECORD).read_text(encoding="utf-8"))["overrides"], rec["overrides"])

    def test_printed_blocks(self):
        html = """<div class="page"><h1 class="head">Big News</h1>
          <div class="rail-block"><div class="rail-title">By the Book</div><h2 class="head">One Minute</h2><p>x</p></div>
          <div class="rail-block"><h2 class="head">Plain Story</h2></div>
          <div class="box"><div class="boxtitle">On the Road — Elite FC Entries</div><p class="boxnote"><b>Also on the calendar.</b> More.</p></div>
          <div class="rail-block" data-section="featured-bout"><h2 class="head">Watch This</h2></div>
          <div class="rail-block qa"><div class="rail-title">Parent Q&amp;A</div><p class="q">Why?</p></div>
          <figure class="art"><img src="media/x.png" alt="A three-panel comic"></figure></div>"""
        got = [(b["kind"], b["title"], b.get("kicker")) for b in bsh.printed_blocks(html)]
        self.assertIn(("lead", "Big News", None), got)
        self.assertIn(("story", "One Minute", "By the Book"), got)
        self.assertIn(("story", "Plain Story", None), got)
        self.assertIn(("box", "On the Road — Elite FC Entries", None), got)
        self.assertIn(("lead-in", "Also on the calendar.", None), got)
        self.assertIn(("rail", "Parent Q&A", "Parent Q&A"), got)
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "issue.html").write_text(html, encoding="utf-8")
            d = bsh.derive_issue(Path(t), bsh.Rules(REPO))
        self.assertEqual(set(d["sections"]), {"lead-story", "by-the-book", "secondary-articles", "featured-bout", "parent-qa", "comic"})
        self.assertEqual([u["name"] for u in d["unregistered"]], ["On the Road", "Also on the Calendar"])


class Lineup(unittest.TestCase):
    def test_classify_slot(self):
        r = bsh.Rules(REPO)
        cases = [
            ({"key": "signup-cobra", "slot": "Nearby Tournaments — Cobra Challenge"}, ["nearby-tournaments"]),
            ({"key": "signup-2", "slot": "Go Cheer — Ultimate Cup who's entered"}, ["nearby-tournaments"]),
            ({"key": "overheard", "slot": "Page 2 feature — For the Parents: What a Rating Letter Means"}, ["for-the-parents"]),
            ({"key": "lead", "slot": "Lead story — Controversial Calls"}, ["controversial-calls", "lead-story"]),
            ({"key": "camp", "slot": "Club events — Winter Camp"}, ["club-events"]),
            ({"key": "tv", "slot": "TV / streaming"}, ["epee-on-screen"]),
            ({"key": "comic", "slot": "Page 2 visual — VR parent filter comic"}, ["comic"]),
            ({"key": "x", "slot": "Something new", "registry": "featured-bout"}, ["featured-bout"]),
            ({"key": "on-the-road", "slot": "On the Road — November NAC"}, []),
        ]
        for slot, want in cases:
            self.assertEqual(r.classify_slot(slot), want, slot)
        self.assertEqual(r.classify_slot({"key": "x1", "slot": "Mystery"}, {"slot_hint": "by_the_book"}), ["by-the-book"])

    def test_budget_history_for_the_current_lineup(self):
        lineup = json.loads((REPO / "budget-demo" / "practice-lineup.json").read_text(encoding="utf-8"))
        items = json.loads((REPO / "staging" / "weeks" / "next" / "items.json").read_text(encoding="utf-8"))["items"]
        manifest = json.loads((REPO / "staging" / "weeks" / "next" / "media" / "manifest.json").read_text(encoding="utf-8"))
        h = bsh.budget_history(REPO, lineup, items, manifest)
        keys = {s.get("key") for s in lineup["slots"]}
        self.assertTrue(set(h["slotSections"]) <= keys and set(h["slotOther"]) <= keys)
        for k in keys:  # every slot is accounted for: a registry section or a named non-registry kicker
            self.assertTrue(k in h["slotSections"] or k in h["slotOther"], k)
        for sids in h["slotSections"].values():
            self.assertTrue(all(s in {x["id"] for x in h["sections"]} for s in sids))
        json.dumps(h)  # inlinable


if __name__ == "__main__":
    unittest.main(verbosity=1)
