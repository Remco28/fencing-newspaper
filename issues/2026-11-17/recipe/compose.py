#!/usr/bin/env python3
"""Compose En Garde Gazette No. 7 (Tuesday, Nov. 17, 2026) from the approved budget."""
import re
import sys
from pathlib import Path


def _repo():
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "compose" / "gazette.py").is_file():
            return parent
    raise SystemExit("compose/gazette.py not found above " + str(here))


REPO = _repo()
sys.path.insert(0, str(REPO / "compose"))
from gazette import *  # noqa: E402

ISSUE = "issues/2026-11-17"
LINEUP = "budget-demo/archive/practice-lineup-issue7-2026-11-17.json"
WEEK = "staging/weeks/2026-11-17"

items = {i["id"]: i for i in load(WEEK + "/items.json")["items"]}


def _strip_draft(text):
    return re.sub(r"^DRAFT\s*\([^)]*\)\.\s*", "", text.strip())


def body_of(item_id):
    return _strip_draft(items[item_id]["body"])


LEAD_ID = "pitch-weekend-roundup-2026-11-16"
# Frank (chat t223u, 2026-11-16 3:38 PM ET): share the lead between Penny Young
# and Mila Siu; print Mila's Kiefer Meinhardt Y14 bronze, C26, and Y12 10th;
# Stella Kuo stays out (below the regional top-16 bar). Official results only.
LEAD_HEAD = "Penny Young and Mila Siu Take Bronze"
LEAD_BODY = (
    "Elite FC brought home two youth bronzes this weekend, one in New Haven and one "
    "in Glen Allen, Va. Penny Young won bronze in Youth 12 Women at the Pizza RYC/RJCC "
    "in New Haven, Conn., on Sunday, Nov. 15, finishing third in a field of 52. A day "
    "earlier she placed 13th of 67 in Youth 14 Women. At the Kiefer Meinhardt Cup, a "
    "Super Youth Circuit event, Mila Siu took bronze in Youth 14 Women on Saturday, "
    "Nov. 14, finishing third in a field of 62 and earning a C26. On Sunday she placed "
    "10th of 54 in Youth 12 Women. Clubmate Amina Gore made the top 16 twice at the "
    "New Haven regional: 16th of 54 in Junior Women on Saturday and 13th of 54 in "
    "Cadet Women on Sunday. Closer to home, Nico Ng finished fifth of 30 in "
    "Division IA Mixed at Freehold Fencing's November Open on Sunday."
)
LEAD_DEK = (
    "Penny Young medals in New Haven; Mila Siu medals in Glen Allen, Va., "
    "and earns a C26."
)

# Lead copy in two lengths (gazette.copy_length; Frank t229u: grow/shrink is a judgement call
# after the eye check). Every sentence comes from vetted sources only:
#   standard - pitch-weekend-roundup-2026-11-16 (official USA Fencing results, final)
#   long     - adds: venue (fencingapi-pizza-ryc-results-2026-11-15); two bronzes per event
#              (official Kiefer Y14W result list shows two fencers tied 3rd,
#              fencingapi-kiefer-meinhardt-results-2026-11-16); what C26 means (No. 6's
#              For the Parents rating explainer, as published Nov. 11); Cobra entries
#              (fencingapi-cobra-efc-entries-2026-10-19, official entrant list).
LEAD_PENNY = {
    "standard": (
        "Elite FC brought home two youth bronzes this weekend, one in New Haven and one "
        "in Glen Allen, Va. Penny Young won bronze in Youth 12 Women at the Pizza RYC/RJCC "
        "in New Haven, Conn., on Sunday, Nov. 15, finishing third in a field of 52. A day "
        "earlier she placed 13th of 67 in Youth 14 Women."
    ),
    "long": (
        "Elite FC brought home two youth bronzes this weekend, one in New Haven and one "
        "in Glen Allen, Va. Penny Young won bronze in Youth 12 Women at the Pizza RYC/RJCC, "
        "a regional tournament at the Floyd Little Athletic Center in New Haven, Conn., on "
        "Sunday, Nov. 15, finishing third in a field of 52. A day earlier she fenced up an "
        "age group and placed 13th of 67 in Youth 14 Women."
    ),
}
LEAD_MILA = {
    "standard": (
        "At the Kiefer Meinhardt Cup, a Super Youth Circuit event, Mila Siu took bronze "
        "in Youth 14 Women on Saturday, Nov. 14, finishing third in a field of 62 and "
        "earning a C26. On Sunday she placed 10th of 54 in Youth 12 Women."
    ),
    "long": (
        "At the Kiefer Meinhardt Cup, a Super Youth Circuit event, Mila Siu took bronze "
        "in Youth 14 Women on Saturday, Nov. 14, finishing third in a field of 62 and "
        "earning a C26. Fencing awards two bronze medals in each event, one to each "
        "losing semifinalist, so Mila shared the third-place step. A C26 is a C rating "
        "earned in 2026; a rating lasts four seasons before it has to be renewed. On "
        "Sunday she placed 10th of 54 in Youth 12 Women."
    ),
}
LEAD_ALSO = {
    "standard": (
        "Clubmate Amina Gore made the top 16 twice at the New Haven regional: 16th of 54 in "
        "Junior Women on Saturday and 13th of 54 in Cadet Women on Sunday. Closer to home, "
        "Nico Ng finished fifth of 30 in Division IA Mixed at Freehold Fencing's November "
        "Open on Sunday."
    ),
    "long": (
        "Clubmate Amina Gore made the top 16 twice at the New Haven regional: 16th of 54 in "
        "Junior Women on Saturday and 13th of 54 in Cadet Women on Sunday. Closer to home, "
        "Nico Ng finished fifth of 30 in Division IA Mixed at Freehold Fencing's November "
        "Open on Sunday.\n\n"
        "Next up for both medalists is the Cobra Challenge in Secaucus, Nov. 27–29, where "
        "Penny and Mila are each entered in Cadet, Youth 12 and Youth 14 Women. Amina Gore "
        "fences Cadet Women there too."
    ),
}

PARENTS_BODY = body_of("desk-for-the-parents-cobra-2026-11-16")
NAC_BODY = body_of("desk-nac-preview-2026-11-16")
CAMP_BODY = body_of("chat-winter-camp-reminder")
# Long: adds a pointer to Winter Camp (chat-winter-camp-reminder, printed on page 1). The
# club email gives no time, place, cost or RSVP for the party; none is added.
PARTY_BODY = {
    "standard": body_of("email-holiday-party-2026-12-11"),
    "long": body_of("email-holiday-party-2026-12-11")
    + " After the party comes Winter Camp, Dec. 27–31; the details are on page 1.",
}
WORLD_BODY = body_of("x-fie-epee-world-cups-bern-wuxi-2026-11-15")
# March NAC (Frank t231u, 2026-11-16 11:43 PM ET): short this week, a large feature in No. 8.
# Both lengths only from the official event page, usafencing.org/2027-march-nac.
MARCH_BODY = {
    "standard": body_of("usaf-march-nac-atlantic-city-2027"),
    "long": body_of("usaf-march-nac-atlantic-city-2027").replace(
        " More on the March NAC next week.",
        " A fencer who misses an event without giving notice by 5 p.m. local time the day"
        " before faces a $250 fine per event. More on the March NAC next week."),
}
assert MARCH_BODY["long"] != MARCH_BODY["standard"], "March NAC long variant did not apply"
_BOOK = body_of("desk-by-the-book-three-calls-2026-11-16")
# Long: adds t.117's "perfect working order", checked against
# reference/usa-fencing/usaf-rules-for-competition-2026-10.pdf.
BOOK_BODY = {
    "standard": _BOOK,
    "long": _BOOK.replace(
        "Bring a spare weapon, body cord and mask cord to the strip, too (t.117).",
        "Bring a spare weapon, a spare body cord and a spare mask cord to the strip, too, all "
        "in perfect working order (t.117)."),
}
assert BOOK_BODY["long"] != BOOK_BODY["standard"], "By the Book long variant did not apply"
PHOTO_CREDIT = "Photo: Elite Fencers Club"

COBRA = items["fencingapi-cobra-efc-entries-2026-10-19"]
# panels_rows: day, event, names, count — group by day for tourney()
_cobra_days = []
for day, event, names, _n in COBRA["panels_rows"]:
    cell_event, cell_names = ty(event), ty(names)
    if _cobra_days and _cobra_days[-1][0] == day:
        _cobra_days[-1][1].append([cell_event, cell_names])
    else:
        _cobra_days.append([day, [[cell_event, cell_names]]])
# typographic day labels (Nov. 27 -> Nov.&nbsp;27)
cobra_days = [(ty(day), rows) for day, rows in _cobra_days]
cobra_block = tourney(
    "Cobra Challenge SYC/RCC",
    "Secaucus, N.J.",
    "Nov.&nbsp;27–29",
    ["Event", "Elite FC"],
    ["1.15in", None],
    cobra_days,
)
cobra_note = ty(
    "Sixteen Elite FC fencers, 26 entries, all approved. Meadowlands Expo Center. "
    "Event times were not posted on the official entrant list."
)

ROAD = items["ft-efc-travel-registrations-nov-dec-2026-10-28"]
road_days = [(ty(row[0]), [[ty(row[1]), ty(row[2])]]) for row in ROAD["rows"]]
road_block = tourney(
    "November NAC",
    "Columbus, Ohio",
    "Nov.&nbsp;20–23",
    ["Event", "Elite FC"],
    ["1.2in", None],
    road_days,
)
road_note = ty(
    "Greater Columbus Convention Center. Official USA Fencing entries as of "
    "Nov. 16, 8:55 a.m. ET; all approved."
)

DEAD = items["desk-deadlines-2026-10-18"]
dead_rows = [[ty(r[0]), ty(r[1])] for r in DEAD["rows"]]
dead_table = table(["Date", "What's due"], dead_rows, ["0.85in", None], numcol=0)
dead_note = ty("USA Fencing fee deadlines are 11:59 p.m. Pacific.")


# Candidate arrangements (Frank t229u: sections get tall and wide layouts; the composer tries
# a few and the eye check picks). compose/arrange.py renders each one and ranks them.
#   page 1: "pair-rail"  lead with the two medal photos side by side; Ratings Earned (tall,
#                        two columns + note) at the foot of the rail
#           "pair-under" same lead; Ratings Earned (wide, three columns) under the lead
#   page 2: "stacked"    Holiday Party, then World Cup, both full width
#           "split"      World Cup | Holiday Party side by side
ARRANGEMENTS = {
    "pair-rail+stacked": {"p1": "pair-rail", "p2": "stacked"},
    "pair-rail+split": {"p1": "pair-rail", "p2": "split"},
    "pair-under+stacked": {"p1": "pair-under", "p2": "stacked"},
    "pair-under+split": {"p1": "pair-under", "p2": "split"},
}
DEFAULT_ARRANGEMENT = "pair-rail+stacked"
PROOF_LABEL = "proof v3"


def build(arrangement=DEFAULT_ARRANGEMENT, picks=None):
    """Return the issue HTML for one arrangement and one set of length picks."""
    arr = ARRANGEMENTS[arrangement]
    picks = lengths_for(ISSUE) if picks is None else picks
    assets = load_art_manifest(ISSUE + "/recipe/art.json")
    by_id = {a["id"]: a for a in assets}
    comic = by_id["vr-parent-filter"]
    photo_penny = by_id["penny-young-pizza-ryc"]
    photo_mila = by_id["mila-siu-stella-kuo-kiefer"]
    for a in (photo_penny, photo_mila):
        if a.get("caption"):
            a["caption"] = ty(a["caption"])

    lead_text = "\n\n".join(
        copy_length(k, v, picks) for k, v in (("lead-penny", LEAD_PENNY), ("lead-mila", LEAD_MILA), ("lead-also", LEAD_ALSO))
    )
    pair = photo_pair(art(photo_penny, credit=PHOTO_CREDIT), art(photo_mila, credit=PHOTO_CREDIT))
    lead = piece(
        LEAD_HEAD,
        f'<p class="dek">{ty(LEAD_DEK)}</p>\n' + pair + "\n" + paras(lead_text),
        level=1,
        cls="lead",
    )
    if arr["p1"] == "pair-rail":
        # Tall shape for a 2.4in rail: no wrapping 'Where' column; the event goes in the note.
        ratings = box(
            "Ratings Earned",
            table(["Fencer", "Rating"], [[ty("Mila Siu"), ty("C26")]], [None, "0.6in"], numcol=None),
            note=ty("Earned at the Kiefer Meinhardt Cup, Glen Allen, Va., Nov. 14."),
        )
    else:
        ratings = box(
            "Ratings Earned",
            table(
                ["Fencer", "Rating", "Where"],
                [[ty("Mila Siu"), ty("C26"), ty("Kiefer Meinhardt Cup, Glen Allen, Va., Nov. 14")]],
                ["1.1in", "0.7in", None],
                numcol=None,
            ),
        )
    nac = piece("Three Head to Columbus", paras(NAC_BODY), kicker="November NAC", cls="slot-a")
    world = piece("Hungary Rules World Cup Weekend", paras(WORLD_BODY), kicker="World Cup", cls="slot-a")
    parents = piece("A National Youth Event Next Door", paras(PARENTS_BODY), kicker="For the Parents")
    book = piece("Three Calls, Two Minutes", paras(copy_length("by-the-book", BOOK_BODY, picks)),
                 kicker="By the Book")
    march = piece("March NAC Comes to Atlantic City", paras(copy_length("march-nac", MARCH_BODY, picks)),
                  kicker="March NAC")
    camp = piece("Winter Camp: Sign Up Now", paras(CAMP_BODY), kicker="Club Events")
    party = piece("Holiday Party: Friday, Dec. 11", paras(copy_length("party", PARTY_BODY, picks)),
                  kicker="Club Events")

    if arr["p1"] == "pair-rail":
        left, right = stack(lead), stack(nac, march, book) + "\n" + ratings
    else:
        left, right = stack(lead) + "\n" + ratings, stack(nac, march, book)
    page1 = page(
        masthead()
        + "\n"
        + dateline("Tuesday Edition", "Vol. I — No. 7 · Chatham, N.J. · November 17, 2026")
        + "\n"
        + cols3(left, right)
        + "\n"
        + split(render_piece(parents), render_piece(camp), widths=[1, 1])
        + "\n"
        + footer(7)
    )

    nearby = box("Nearby Tournaments — Elite FC Entries", str(cobra_block), note=cobra_note, cls="w3")
    road = box("On the Road — November NAC", road_block, note=road_note)
    deadlines = box("Deadlines", dead_table, note=dead_note)
    if arr["p2"] == "stacked":
        top = render_piece(party) + "\n" + render_piece(world)
    else:
        top = split(render_piece(world), render_piece(party), widths=[1, 1])
    page2 = page(
        dateline("Page Two", "Club Calendar &amp; Notes &nbsp;·&nbsp; Vol. I — No. 7", first=False)
        + "\n" + top
        + "\n" + nearby
        + "\n" + box_pair(road, deadlines)
        + "\n" + art(comic)
        + "\n" + footer(7),
        cls="fit",
    )
    title = f"En Garde Gazette — Vol. I No. 7 — November 17, 2026 ({PROOF_LABEL})"
    return document(title, [page1, page2])


def main():
    name = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--arrangement=")), None)
    f = REPO / ISSUE / "recipe" / "arrangement.json"
    if name is None and f.is_file():
        import json as _json
        name = _json.loads(f.read_text(encoding="utf-8")).get("arrangement")
    name = name or DEFAULT_ARRANGEMENT
    print(f"arrangement: {name}; lengths: {lengths_for(ISSUE) or 'all standard'}")
    write_issue(ISSUE, build(name))
    print(f"length choices: {LENGTH_CHOICES}")


if __name__ == "__main__":
    main()
