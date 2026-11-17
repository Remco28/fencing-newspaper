#!/usr/bin/env python3
"""Section history: which registry section (sections.json) ran in which published issue.

Derived from data, every time, never typed in by hand:
  - which issues are PUBLISHED:  site/issues.json (written by scripts/publish_issue.py). An issue folder
    that is only a proof (e.g. next week's issues/<date>/) is not in that file and is never counted.
  - what PRINTED in each issue:  issues/<date>/issue.html (box titles, rail-title kickers, headlines,
    photos, figures; plus data-section="<registry id>" on any block, if the composer ever emits it)
  - what each block WAS:         scripts/section_history_rules.json (kicker / slot aliases per section),
    issues/<date>/budget-submission.json (included slot -> printed headline link), issue.json and
    sources.json (item ids, for The Vault and club photos), and sections.json (names, Vault entries).
  - manual corrections:          "overrides" in scripts/section-history.json (kept across regeneration).

Printed kickers that are NOT in sections.json (On the Road, Also on the Calendar, one-off info boxes)
are listed separately. sections.json `last_ran` is never read as truth; disagreements are reported.

Usage:
  python3 scripts/build_section_history.py            # print the table, write scripts/section-history.json
  python3 scripts/build_section_history.py --check    # exit 1 if section-history.json is out of date
  python3 scripts/build_section_history.py --issue 2026-11-11 --explain   # show the evidence for one issue
  python3 scripts/build_section_history.py --no-write # table only

scripts/publish_issue.py calls update_record() after it lists the issue on the site, and
scripts/build_budget_html.py calls budget_history() to inline the history into the budget page (it derives
fresh from the issues each build, so the page can't go stale even if the record file does).
"""
from __future__ import annotations

import argparse
import html as htmllib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RULES = Path(__file__).resolve().parent / "section_history_rules.json"
RECORD = "scripts/section-history.json"  # the record lives with the budget tooling
VOID = {"img", "br", "hr", "meta", "link", "input", "col", "wbr", "source"}
FIGURE_CLASSES = {"figure", "art", "comic-wide", "comicfig", "comic"}
GENERIC = ("lead-story", "secondary-articles")  # matched from slots and structure, never from a headline prefix
SMALL = {"on", "the", "a", "an", "of", "in", "for", "to", "and", "at"}


# ----------------------------------------------------------------- small helpers
def norm(text) -> str:
    """Case/punctuation-insensitive form: 'N.J. High-School' -> 'nj high school'."""
    t = htmllib.unescape(str(text or "")).replace("­", "").replace(".", "").replace("’", "").replace("'", "")
    return re.sub(r"[^a-z0-9&]+", " ", t.lower()).strip()


def starts(text_n: str, alias_n: str) -> bool:
    return bool(alias_n) and (text_n == alias_n or text_n.startswith(alias_n + " "))


def segments(name) -> list[str]:
    return [s.strip() for s in re.split(r"\s+[—–-]\s+|\s*→\s*|:\s+", str(name or "")) if s.strip()]


def smart_title(text: str) -> str:
    words = text.strip().rstrip(".:").split()
    return " ".join(w if (i and w.lower() in SMALL) else w[:1].upper() + w[1:] for i, w in enumerate(words))


def ranges(nums) -> str:
    """[1,2,3,5] -> '1–3, 5'."""
    nums, out, i = sorted(set(nums)), [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else f"{nums[i]}–{nums[j]}")
        i = j + 1
    return ", ".join(out)


def read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


# ----------------------------------------------------------------- rules + registry
class Rules:
    def __init__(self, repo: Path = REPO):
        doc = read_json(RULES, {}) or {}
        reg = read_json(repo / "sections.json", {}) or {}
        self.registry = [s for s in reg.get("sections", []) if isinstance(s, dict) and s.get("id")]
        self.club_re = re.compile(doc.get("club_regex") or r"$^", re.I)
        self.sec = {}
        for s in self.registry:
            r = dict((doc.get("sections") or {}).get(s["id"]) or {})
            names = [s.get("name", ""), re.sub(r"\s*\(.*", "", s.get("name", ""))] + list(r.get("aliases") or [])
            r["aliases_n"] = sorted({norm(a) for a in names if norm(a)}, key=len, reverse=True)
            r["keys"] = {s["id"], *(r.get("slot_keys") or [])}
            r["hints_n"] = {norm(h) for h in (r.get("slot_hints") or [])} | {norm(s["id"])}
            r["short"] = r.get("short") or re.sub(r"\s*\(.*", "", s.get("name", s["id"]))
            r["head_re"] = re.compile(r["headline_regex"], re.I) if r.get("headline_regex") else None
            r["alt_re"] = re.compile(r["figure_alt_regex"], re.I) if r.get("figure_alt_regex") else None
            self.sec[s["id"]] = r
        self.unknown_rule_ids = sorted(set(doc.get("sections") or {}) - set(self.sec))
        vault = next((s for s in self.registry if self.sec[s["id"]].get("vault_entries")), None)
        self.vault_id = vault["id"] if vault else None
        self.vault_entries = [e for e in (vault or {}).get("entries", []) if isinstance(e, dict)]
        self.photo_id = next((i for i, r in self.sec.items() if r.get("club_photo")), None)
        self.lead_id = next((i for i, r in self.sec.items() if r.get("lead_h1")), None)
        self.leftover_id = next((i for i, r in self.sec.items() if r.get("leftover_stories")), None)

    def by_alias(self, text, generic=False) -> str | None:
        """Section whose alias starts `text` (a printed kicker, a headline, one segment of a slot name)."""
        t = norm(text)
        best = None
        for sid, r in self.sec.items():
            if sid in GENERIC and not generic:
                continue
            for a in r["aliases_n"]:
                if starts(t, a) and (best is None or len(a) > best[0]):
                    best = (len(a), sid)
        return best[1] if best else None

    def classify_slot(self, slot: dict, item: dict | None = None) -> list[str]:
        """Registry section id(s) for a lineup / submission slot. Explicit `registry` wins; then the slot
        name ('Club events — Winter Camp'), then the key ('signup-2'), then the staging item's hint/kind."""
        explicit = slot.get("registry") or slot.get("registry_section")
        if explicit:
            return [e for e in ([explicit] if isinstance(explicit, str) else explicit) if e in self.sec]
        found = []
        for seg in segments(slot.get("name") or slot.get("slot")):
            sid = self.by_alias(seg, generic=True)
            if sid and sid not in found:
                found.append(sid)
        if not found:
            key = str(slot.get("key") if "key" in slot else slot.get("slot") if "name" in slot else "") or ""
            hits = [(len(k), sid) for sid, r in self.sec.items() for k in r["keys"] if key == k or key.startswith(k + "-")]
            if hits:
                found.append(max(hits)[1])
        if not found and item:
            for hint in (item.get("slot_hint"), item.get("suggested_slot"), item.get("kind")):
                sid = next((s for s, r in self.sec.items() if hint and norm(hint) in r["hints_n"]), None)
                if sid:
                    found.append(sid)
                    break
        specific = [s for s in found if s not in GENERIC]
        return specific + [s for s in found if s in GENERIC]


# ----------------------------------------------------------------- printed issue -> blocks
class Node:
    __slots__ = ("tag", "attrs", "cls", "kids", "parent", "kicker")

    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.kids, self.kicker = tag, dict(attrs), parent, [], None
        self.cls = set((self.attrs.get("class") or "").split())

    def text(self) -> str:
        out = []
        for k in self.kids:
            out.append(k if isinstance(k, str) else k.text())
        return re.sub(r"\s+", " ", "".join(out).replace("­", "")).strip()

    def walk(self):
        yield self
        for k in self.kids:
            if not isinstance(k, str):
                yield from k.walk()

    def find(self, cls):
        return [n for n in self.walk() if cls in n.cls]


class _Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root", {}, None)
        self.cur, self.skip = self.root, 0

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.skip += 1
            return
        n = Node(tag, attrs, self.cur)
        self.cur.kids.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.kids.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.skip = max(0, self.skip - 1)
            return
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, data):
        if not self.skip:
            self.cur.kids.append(data)


def printed_blocks(html_text: str) -> list[dict]:
    """Document-order blocks of a printed issue: lead, story, box, rail (kicker without a head), photo,
    figure, lead-in (a bold run-in opening a box note, e.g. 'Also on the calendar.')."""
    p = _Tree()
    p.feed(html_text)
    blocks, seen_fig = [], set()

    def anc_kicker(n):
        while n is not None:
            if n.kicker:
                return n
            n = n.parent
        return None

    for n in p.root.walk():
        if "rail-title" in n.cls and n.parent is not None:
            n.parent.kicker = n.text()
    used = set()
    for n in p.root.walk():
        ds = n.attrs.get("data-section")
        if "head" in n.cls and re.fullmatch(r"h[1-6]", n.tag):
            k = anc_kicker(n)
            if k is not None:
                used.add(id(k))
            sec_anc = n
            while sec_anc is not None and not sec_anc.attrs.get("data-section"):
                sec_anc = sec_anc.parent
            blocks.append({"kind": "lead" if n.tag == "h1" else "story", "title": n.text(), "kicker": k.kicker if k else None,
                           "data_section": sec_anc.attrs.get("data-section") if sec_anc else None})
        elif "boxtitle" in n.cls:
            box = n.parent
            blocks.append({"kind": "box", "title": n.text(), "kicker": None,
                           "data_section": ds or (box.attrs.get("data-section") if box else None)})
            for note in (box.find("boxnote") if box else []):
                first = next((k for k in note.kids if not (isinstance(k, str) and not k.strip())), None)
                if isinstance(first, Node) and first.tag in ("b", "strong") and 3 < len(first.text()) < 40:
                    blocks.append({"kind": "lead-in", "title": first.text(), "kicker": None, "within": n.text()})
        elif "photo" in n.cls and n.tag in ("div", "figure"):
            scope = n.parent if n.parent is not None else n
            img = next((x for x in n.walk() if x.tag == "img"), None)
            cap = " ".join(c.text() for c in scope.find("caption")) or n.text()
            credit = " ".join(c.text() for c in scope.find("credit"))
            k = anc_kicker(n)
            blocks.append({"kind": "photo", "title": cap, "credit": credit, "kicker": k.kicker if k else None,
                           "src": (img.attrs.get("src") if img else "") or "", "alt": (img.attrs.get("alt") if img else "") or ""})
        elif n.cls & FIGURE_CLASSES:
            a = n.parent
            while a is not None and id(a) not in seen_fig:
                a = a.parent
            seen_fig.add(id(n))
            if a is not None:
                continue  # comicfig inside comic-wide: one figure
            img = next((x for x in n.walk() if x.tag == "img"), None)
            caps = n.find("caption")
            blocks.append({"kind": "figure", "title": (caps[0].text() if caps else "") or (img.attrs.get("alt") if img else "") or "",
                           "classes": sorted(n.cls), "alt": (img.attrs.get("alt") if img else "") or "",
                           "src": (img.attrs.get("src") if img else "") or "", "kicker": None, "data_section": ds})
    # kickers that sit over no headline (Parent Q&A: rail-title + question)
    for n in p.root.walk():
        if n.kicker and id(n) not in used and not any("photo" in x.cls for x in n.walk()):
            blocks.append({"kind": "rail", "title": n.kicker, "kicker": n.kicker})
    return blocks


# ----------------------------------------------------------------- one issue
def issue_item_ids(folder: Path) -> tuple[set, dict]:
    """Every staging item id this issue names (issue.json pages, sources.json, included budget slots),
    and the sources.json entry text per id (provenance, to tell a club photo from other art)."""
    ids, prov = set(), {}

    def grab(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ("itemId", "id") and isinstance(v, str):
                    ids.add(v)
                elif k == "itemIds" and isinstance(v, list):
                    ids.update(i for i in v if isinstance(i, str))
                else:
                    grab(v)
        elif isinstance(x, list):
            for v in x:
                grab(v)

    grab((read_json(folder / "issue.json", {}) or {}).get("pages"))
    for it in (read_json(folder / "sources.json", {}) or {}).get("items", []) or []:
        iid = isinstance(it, dict) and (it.get("id") or it.get("itemId"))
        if iid:
            ids.add(iid)
            prov[iid] = json.dumps(it, ensure_ascii=False)
    sub = read_json(folder / "budget-submission.json", {}) or {}
    for e in sub.get("includedSlots") or []:
        if isinstance(e, dict) and e.get("itemId"):
            ids.add(e["itemId"])
    ids.update(i for i in sub.get("photoIncludes") or [] if isinstance(i, str))
    return ids, prov


def derive_issue(folder: Path, rules: Rules) -> dict:
    """{"sections": {id: [evidence]}, "unregistered": [{name, kind, evidence}], "notes": [...]} for one issue."""
    out = {"sections": {}, "unregistered": [], "notes": []}
    page = folder / "issue.html"
    if not page.is_file():
        out["notes"].append("no issue.html: nothing derived")
        return out
    blocks = printed_blocks(page.read_text(encoding="utf-8"))
    item_ids, prov = issue_item_ids(folder)
    sub = read_json(folder / "budget-submission.json", {}) or {}
    slots = [e for e in sub.get("includedSlots") or [] if isinstance(e, dict)]

    def hit(sid, why):
        ev = out["sections"].setdefault(sid, [])
        if why not in ev:
            ev.append(why)

    def unreg(name, kind, why):
        name = re.sub(r"\s+", " ", name).strip()
        if name and not any(norm(u["name"]) == norm(name) for u in out["unregistered"]):
            out["unregistered"].append({"name": name, "kind": kind, "evidence": why})

    def vault_match(b):
        t = norm(b.get("title"))
        for e in rules.vault_entries:
            et = norm(e.get("title"))
            if et and (t == et or (" ".join(t.split()[:2]) == " ".join(et.split()[:2]) and e.get("source_item") in item_ids)):
                return e
        return None

    def slot_link(b):
        """Included budget slot whose headline is this printed title -> that slot's (specific) section."""
        t = norm(b["title"])
        for e in slots:
            h = norm(e.get("headline"))
            if len(h) >= 12 and len(t) >= 12 and (h.startswith(t) or t.startswith(h)):
                sids = [s for s in rules.classify_slot(e) if s not in GENERIC]
                if sids:
                    return sids[0], e
        return None, None

    lead_done = False
    for b in blocks:
        kind, title = b["kind"], b.get("title") or ""
        q = f"“{title[:70]}”"
        if b.get("data_section") in rules.sec:
            hit(b["data_section"], f"data-section on {kind}: {q}")
        elif kind == "lead":
            if rules.lead_id and not lead_done:
                hit(rules.lead_id, f"page-1 headline: {q}")
                lead_done = True
        elif kind in ("story", "rail"):
            sid = rules.by_alias(b["kicker"]) if b.get("kicker") else None
            if sid:
                hit(sid, f"kicker “{b['kicker']}”" + (f": {q}" if kind == "story" else ""))
                continue
            if kind == "rail":
                unreg(b["kicker"], "kicker", "kicker with no headline")
                continue
            sid = rules.by_alias(title)
            if sid:
                hit(sid, f"headline: {q}")
                continue
            v = vault_match(b)
            if v and rules.vault_id:
                hit(rules.vault_id, f"Vault entry “{v.get('title')}”: {q}")
                continue
            sid, e = slot_link(b)
            if sid:
                hit(sid, f"budget slot “{e.get('name') or e.get('slot')}”: {q}")
                continue
            sid = next((s for s, r in rules.sec.items() if r["head_re"] and r["head_re"].search(title)), None)
            if sid:
                hit(sid, f"headline pattern: {q}")
                continue
            if b.get("kicker"):
                unreg(b["kicker"], "topical kicker", f"over {q}")
            if rules.leftover_id:
                hit(rules.leftover_id, f"story: {q}" + (f" (kicker “{b['kicker']}”)" if b.get("kicker") else ""))
        elif kind == "box":
            first = (segments(title) or [title])[0]
            sid = rules.by_alias(first) or rules.by_alias(title)
            if sid:
                hit(sid, f"box “{title}”")
                continue
            sid, e = slot_link(b)
            if sid:
                hit(sid, f"box “{title}” = budget slot “{e.get('name') or e.get('slot')}”")
                continue
            sid = next((s for s, r in rules.sec.items() if r["head_re"] and r["head_re"].search(title)), None)
            if sid:
                hit(sid, f"box title pattern: “{title}”")
            else:
                unreg(first, "box", f"box “{title}”")
        elif kind == "lead-in":
            sid = rules.by_alias(title)
            if sid:
                hit(sid, f"note lead-in “{title}”")
            else:
                unreg(smart_title(title), "note lead-in", f"in the “{b.get('within')}” box")
        elif kind == "photo":
            sid = rules.by_alias(b["kicker"]) if b.get("kicker") else None
            if sid:
                hit(sid, f"kicker “{b['kicker']}” (photo)")
                continue
            stem = re.sub(r"-crop$", "", Path(b.get("src") or "").stem)
            src_txt = " ".join(t for i, t in prov.items() if stem and (stem in i or i in stem))
            if rules.photo_id and (rules.club_re.search(title) or rules.club_re.search(b.get("credit") or "") or rules.club_re.search(src_txt)):
                hit(rules.photo_id, f"photo: “{title[:70]}”")
            else:
                out["notes"].append(f"photo not counted as a club photo: “{title[:70]}”")
        elif kind == "figure":
            comic = next((s for s, r in rules.sec.items() if (set(r.get("figure_classes") or []) & set(b.get("classes") or []))
                          or (r["alt_re"] and r["alt_re"].search(b.get("alt") or ""))), None)
            v = vault_match(b)
            if comic:
                hit(comic, "figure (" + (" ".join(b.get("classes") or []) or "art") + ")")
            elif v and rules.vault_id:
                hit(rules.vault_id, f"Vault entry “{v.get('title')}” (figure)")
            else:
                out["notes"].append(f"figure not matched to a section: “{title[:70]}”")
    return out


# ----------------------------------------------------------------- all published issues
def published_issues(repo: Path) -> list[dict]:
    """Published = listed in site/issues.json (publish_issue.py writes it). Oldest first."""
    rows = read_json(repo / "site" / "issues.json", []) or []
    out = [{"number": int(e["number"]), "date": e["date"], "headline": e.get("headline") or ""}
           for e in rows if isinstance(e, dict) and isinstance(e.get("number"), int) and e.get("date")]
    return sorted(out, key=lambda e: e["number"])


def build_history(repo: Path = REPO, rules: Rules | None = None) -> dict:
    rules = rules or Rules(repo)
    record = read_json(repo / RECORD, {}) or {}
    overrides = record.get("overrides") if isinstance(record.get("overrides"), dict) else {}
    issues, per = published_issues(repo), {}
    for iss in issues:
        d = derive_issue(repo / "issues" / iss["date"], rules)
        ov = overrides.get(str(iss["number"])) or {}
        for sid, why in (ov.get("add") or {}).items():
            if sid in rules.sec:
                d["sections"].setdefault(sid, []).append(f"manual override: {why}")
        for sid, why in (ov.get("remove") or {}).items():
            if d["sections"].pop(sid, None) is not None:
                d["notes"].append(f"manual override removed {sid}: {why}")
        drop = {norm(x) for x in ov.get("ignore_unregistered") or []}
        d["unregistered"] = [u for u in d["unregistered"] if norm(u["name"]) not in drop]
        per[iss["number"]] = d
    sections = []
    for s in rules.registry:
        ran = [n for n in sorted(per) if s["id"] in per[n]["sections"]]
        sections.append({
            "id": s["id"], "name": re.sub(r"\s*\(.*", "", s.get("name", s["id"])), "short": rules.sec[s["id"]]["short"],
            "frequency": s.get("frequency") or "", "frequency_detail": s.get("frequency_detail") or "",
            "priority": s.get("priority") or "", "ran": ran, "last": ran[-1] if ran else None,
            "evidence": {str(n): per[n]["sections"][s["id"]] for n in ran},
            "registry_last_ran": s.get("last_ran"),
        })
    unreg = {}
    for n in sorted(per):
        for u in per[n]["unregistered"]:
            row = unreg.setdefault(norm(u["name"]), {"name": u["name"], "kind": u["kind"], "ran": [], "evidence": {}})
            row["ran"].append(n)
            row["evidence"][str(n)] = [u["evidence"]]
    for row in unreg.values():
        row["last"] = row["ran"][-1]
    stale = [f"{s['short']}: sections.json last_ran={s['registry_last_ran']!r}, derived {s['last']!r}"
             for s in sections if s["registry_last_ran"] != s["last"]]
    return {
        "source": "derived by scripts/build_section_history.py from site/issues.json + issues/<date>/",
        "issues": issues, "sections": sections, "unregistered": list(unreg.values()),
        "notes": {str(n): per[n]["notes"] for n in sorted(per) if per[n]["notes"]},
        "registry_last_ran_stale": stale,
        "rules_for_unknown_sections": rules.unknown_rule_ids,
    }


def budget_history(repo: Path, lineup: dict, items: list, manifest: dict, rules: Rules | None = None) -> dict:
    """History for the budget page: build_history() + which lineup slots / photos belong to which section
    (the page works out 'in this budget' live from Frank's ticks)."""
    rules = rules or Rules(repo)
    h = build_history(repo, rules)
    by_id = {i.get("id"): i for i in items if isinstance(i, dict)}
    known_other = {norm(u["name"]): u["name"] for u in h["unregistered"]}
    slot_sections, slot_other, seen = {}, {}, {}
    for i, s in enumerate(x for x in (lineup.get("slots") or lineup.get("lineup") or []) if isinstance(x, dict)):
        key = s.get("key") or f"slot-{i}"
        while key in seen:  # same de-duplication as core.js buildSlots
            key += "-dup"
        seen[key] = 1
        segs = segments(s.get("slot"))
        other = next((known_other[norm(g)] for g in segs if norm(g) in known_other), None)
        sids = [] if (other and segs and norm(segs[0]) in known_other) else rules.classify_slot(s, by_id.get(s.get("item")))
        if sids:
            slot_sections[key] = sids
        if other or (not sids and segs):
            slot_other[key] = other or segs[0]
    item_slot = {s.get("item"): k for k, s in ((x.get("key"), x) for x in lineup.get("slots") or [] if isinstance(x, dict)) if s.get("item")}
    photo_sections = {}
    for m in manifest.get("items", []) if isinstance(manifest, dict) else []:
        if not isinstance(m, dict) or not m.get("id"):
            continue
        parent = item_slot.get(m.get("parent_item_id"))
        blob = " ".join(str(m.get(k) or "") for k in ("from", "source", "caption", "url"))
        if str(m.get("kind")) in ("comic", "cartoon") and "comic" in rules.sec:
            photo_sections[m["id"]] = "comic"
        elif "photo-from-history" in (slot_sections.get(parent) or []) or str(m.get("source")) == "history-photos":
            if "photo-from-history" in rules.sec:
                photo_sections[m["id"]] = "photo-from-history"
        elif m.get("kind") == "photo" and rules.photo_id and rules.club_re.search(blob):
            photo_sections[m["id"]] = rules.photo_id
    h.update({"slotSections": slot_sections, "slotOther": slot_other, "photoSections": photo_sections})
    for s in h["sections"]:
        s.pop("registry_last_ran", None)
    return h


# ----------------------------------------------------------------- record + CLI
def record_doc(history: dict, old: dict | None) -> dict:
    old = old if isinstance(old, dict) else {}
    return {
        "_about": "Section history record. GENERATED by scripts/build_section_history.py (publish_issue.py refreshes it "
                  "at publish time) from site/issues.json + issues/<date>/. Do not edit 'issues', 'sections' or "
                  "'unregistered' by hand; to correct a wrong call, add it under 'overrides' (kept across regeneration): "
                  "{\"<issue number>\": {\"add\": {\"<section id>\": \"why\"}, \"remove\": {\"<section id>\": \"why\"}, "
                  "\"ignore_unregistered\": [\"<kicker>\"]}}.",
        "overrides": old.get("overrides") if isinstance(old.get("overrides"), dict) else {},
        "issues": history["issues"],
        "sections": [{"id": s["id"], "name": s["name"], "frequency": s["frequency"], "ran": s["ran"], "last": s["last"],
                      "evidence": s["evidence"]} for s in history["sections"]],
        "unregistered": history["unregistered"],
        "notes": history["notes"],
    }


def update_record(repo: Path = REPO) -> tuple[bool, dict]:
    """Regenerate section-history.json. Returns (changed, history). Called by publish_issue.py."""
    history = build_history(repo)
    path = repo / RECORD
    new = json.dumps(record_doc(history, read_json(path)), indent=2, ensure_ascii=False) + "\n"
    old = path.read_text(encoding="utf-8") if path.is_file() else ""
    if new != old:
        path.write_text(new, encoding="utf-8")
    return new != old, history


def table(history: dict) -> str:
    nums = [i["number"] for i in history["issues"]]
    lines = [f"Section history · published issues Nos. {ranges(nums) or '—'} ({len(nums)})", ""]
    w = max([len(s["short"]) for s in history["sections"]] + [10])
    for s in history["sections"]:
        dots = "".join("●" if n in s["ran"] else "·" for n in nums)
        lines.append(f"  {s['short']:<{w}}  {s['frequency']:<14} {dots}  " +
                     (f"No{'s' if len(s['ran']) > 1 else ''}. {ranges(s['ran'])} · last No. {s['last']}" if s["ran"] else "never ran"))
    if history["unregistered"]:
        lines += ["", "Printed kickers not in sections.json:"]
        for u in history["unregistered"]:
            lines.append(f"  {u['name']:<{w}}  {u['kind']:<14} No{'s' if len(u['ran']) > 1 else ''}. {ranges(u['ran'])}")
    for msg in history["registry_last_ran_stale"]:
        lines.append(f"  note: sections.json is stale — {msg}")
    for rid in history["rules_for_unknown_sections"]:
        lines.append(f"  warning: section_history_rules.json has rules for unknown section id {rid!r}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Derive section history from published issues.")
    ap.add_argument("--repo", type=Path, default=REPO)
    ap.add_argument("--check", action="store_true", help="exit 1 if section-history.json is missing or out of date")
    ap.add_argument("--no-write", action="store_true", help="print only")
    ap.add_argument("--issue", help="issue folder date: print what was derived for that one issue")
    ap.add_argument("--explain", action="store_true", help="print the evidence behind every 'ran'")
    args = ap.parse_args()
    repo = args.repo.resolve()
    if args.issue:
        d = derive_issue(repo / "issues" / args.issue, Rules(repo))
        print(json.dumps(d, indent=2, ensure_ascii=False))
        return
    history = build_history(repo)
    print(table(history))
    if args.explain:
        for s in history["sections"]:
            for n, ev in s["evidence"].items():
                print(f"  {s['short']} · No. {n}: " + " | ".join(ev))
        for n, notes in history["notes"].items():
            for m in notes:
                print(f"  No. {n} note: {m}")
    path = repo / RECORD
    new = json.dumps(record_doc(history, read_json(path)), indent=2, ensure_ascii=False) + "\n"
    current = path.is_file() and path.read_text(encoding="utf-8") == new
    if args.check:
        print(f"\n{RECORD}: " + ("up to date" if current else "OUT OF DATE (run scripts/build_section_history.py)"))
        sys.exit(0 if current else 1)
    if not args.no_write and not current:
        path.write_text(new, encoding="utf-8")
        print(f"\nwrote {RECORD}")


if __name__ == "__main__":
    main()
