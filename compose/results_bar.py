"""STYLE-GUIDE §0d — strong finishes only, in every printed place.

A club member's place prints only if it clears the inclusion bar (or is a medal,
a qualification, or a rating earned). Weak finishes are not printed in the Club
Results box, in captions, in leads or shorts, or on boards — no "also fenced"
line, nobody embarrassed (Frank 2026-10-12 / 2026-10-20 / 2026-10-26; reaffirmed
2026-11-24 when below-bar NAC places reached print in a short).

Vetting an item as factually correct is not permission to print a below-bar
place. Frank has to clear that place for print explicitly (a
`data-results-bar-ok` mark on the element, or a `print_below_bar` flag on the
claim).
"""
from __future__ import annotations

import re

PLACE_RE = re.compile(
    r"\b(?P<place>\d+)(?:st|nd|rd|th)\s+of\s+(?P<field>\d+)\b",
    re.I,
)
RATING_RE = re.compile(r"\bearned\s+[A-EU]\d{2}\b", re.I)
QUAL_RE = re.compile(r"\bqualif(?:y|ied|ication)s?\b", re.I)

NATIONAL_HINTS = (
    "nac", "syc", "sjcc", "snc", "championship", "nationals", "national",
    "fie", "world cup", "worlds", "grand prix", "satellite",
    "super youth", "youth circuit", "super junior", "cadet circuit",
    "challenger",  # NAC/SN Elite–Challenger split
)
REGIONAL_HINTS = ("ryc", "rcc", "rjcc", "regional", "region ", "region.")

# A short window of context around a place, used to guess the event tier.
WINDOW = 800


def event_tier(context: str, field: int | None = None) -> str:
    t = (context or "").lower()
    if any(h in t for h in NATIONAL_HINTS):
        return "national"
    if any(h in t for h in REGIONAL_HINTS):
        return "regional"
    # A 100+ field is not a local club event; default to the national bar so a
    # legal 15th of 136 is not flagged just because "NAC" sat a paragraph away.
    if field and field >= 100:
        return "national"
    return "local"


def bar_for(tier: str, field: int) -> int:
    """Highest place number that still prints (medals are always allowed)."""
    if field < 16:
        return 8
    if tier == "national":
        return 32
    if tier == "regional":
        return 16
    return 8


def clears_bar(place: int, field: int, tier: str, *, context: str = "") -> bool:
    """True if this place may print under §0d."""
    if place <= 0 or field <= 0:
        return False
    if place <= 3:
        return True
    ctx = context or ""
    if RATING_RE.search(ctx) or QUAL_RE.search(ctx):
        return True
    return place <= bar_for(tier, field)


def is_weak_finish(place: int, field: int, tier: str, *, context: str = "") -> bool:
    """Below the inclusion bar, or in the bottom half of the field (and not a medal).

    A medal, a qualification, or a rating earned always prints, even in the bottom half.
    """
    if place <= 3:
        return False
    ctx = context or ""
    if RATING_RE.search(ctx) or QUAL_RE.search(ctx):
        return False
    if not clears_bar(place, field, tier, context=ctx):
        return True
    if field and place > field / 2:
        return True
    return False


def _place_waived(html: str, place_text: str) -> bool:
    """True if this 'Nth of M' sits near an element marked data-results-bar-ok."""
    for hm in re.finditer(re.escape(place_text), html, re.I):
        window = html[max(0, hm.start() - 800):hm.end() + 80]
        if re.search(r"<[^>]*\bdata-results-bar-ok\b[^>]*>", window, re.I):
            return True
    return False


def find_weak_places(text: str, html: str | None = None) -> list[dict]:
    """Return weak 'Nth of M' mentions in plain text (HTML used only for waivers)."""
    scan = re.sub(r"<style>.*?</style>", " ", text, flags=re.S | re.I)
    scan = re.sub(r"<script>.*?</script>", " ", scan, flags=re.S | re.I)
    scan = re.sub(r"<[^>]+>", " ", scan)
    scan = re.sub(r"\s+", " ", scan)
    found = []
    seen = set()
    for m in PLACE_RE.finditer(scan):
        place, field = int(m.group("place")), int(m.group("field"))
        ctx = scan[max(0, m.start() - WINDOW):min(len(scan), m.end() + WINDOW)]
        tier = event_tier(ctx, field)
        if not is_weak_finish(place, field, tier, context=ctx):
            continue
        key = m.group(0)
        if key in seen:
            continue
        if html is not None and _place_waived(html, key):
            continue
        seen.add(key)
        found.append({
            "text": key,
            "place": place,
            "field": field,
            "tier": tier,
            "bar": bar_for(tier, field),
        })
    return found


def format_flags(weak: list[dict]) -> list[str]:
    msgs = []
    for w in weak:
        half = f", or bottom half of {w['field']}" if w["place"] > w["field"] / 2 else ""
        msgs.append(
            f"results bar (§0d): {w['text']} is below the {w['tier']} bar "
            f"(top {w['bar']}{half}) — do not print a weak finish unless Frank "
            f"clears it for print (data-results-bar-ok)"
        )
    return msgs
