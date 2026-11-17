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
WEEK = "staging/weeks/next"

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

# Split so each results photo can sit ahead of the graf it belongs with and
# float beside that prose (art-fit; one portrait is too tall to stack at
# column width under the 2.2in photo ceiling).
LEAD_PENNY = (
    "Elite FC brought home two youth bronzes this weekend, one in New Haven and one "
    "in Glen Allen, Va. Penny Young won bronze in Youth 12 Women at the Pizza RYC/RJCC "
    "in New Haven, Conn., on Sunday, Nov. 15, finishing third in a field of 52. A day "
    "earlier she placed 13th of 67 in Youth 14 Women."
)
LEAD_MILA = (
    "At the Kiefer Meinhardt Cup, a Super Youth Circuit event, Mila Siu took bronze "
    "in Youth 14 Women on Saturday, Nov. 14, finishing third in a field of 62 and "
    "earning a C26. On Sunday she placed 10th of 54 in Youth 12 Women."
)
LEAD_ALSO = (
    "Clubmate Amina Gore made the top 16 twice at the New Haven regional: 16th of 54 in "
    "Junior Women on Saturday and 13th of 54 in Cadet Women on Sunday. Closer to home, "
    "Nico Ng finished fifth of 30 in Division IA Mixed at Freehold Fencing's November "
    "Open on Sunday."
)

PARENTS_BODY = body_of("desk-for-the-parents-cobra-2026-11-16")
NAC_BODY = body_of("desk-nac-preview-2026-11-16")
CAMP_BODY = body_of("chat-winter-camp-reminder")
PARTY_BODY = body_of("email-holiday-party-2026-12-11")
WORLD_BODY = body_of("x-fie-epee-world-cups-bern-wuxi-2026-11-15")
BOOK_BODY = body_of("desk-by-the-book-three-calls-2026-11-16")
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


def main():
    assets = load_art_manifest(ISSUE + "/recipe/art.json")
    by_id = {a["id"]: a for a in assets}
    comic = by_id["vr-parent-filter"]
    photo_penny = by_id["penny-young-pizza-ryc"]
    photo_mila = by_id["mila-siu-stella-kuo-kiefer"]
    for a in (photo_penny, photo_mila):
        if a.get("caption"):
            a["caption"] = ty(a["caption"])

    # Penny floats beside the lead (the one flex slot on page 1). Mila's
    # portrait is too tall to stack at span2 or even one column under the 2.2in
    # ceiling, so it sits in a 1/3 split next to Ratings Earned, where a stack
    # lands at ~1.65in wide / 2.2in tall — no second flex slot, no crop.
    lead = piece(
        LEAD_HEAD,
        f'<p class="dek">{ty(LEAD_DEK)}</p>\n'
        + art(photo_penny, credit=PHOTO_CREDIT)
        + "\n"
        + paras(LEAD_PENNY)
        + "\n"
        + paras(LEAD_MILA)
        + "\n"
        + paras(LEAD_ALSO),
        level=1,
        cls="lead",
    )
    ratings = box(
        "Ratings Earned",
        table(
            ["Fencer", "Rating", "Where"],
            [[ty("Mila Siu"), ty("C26"), ty("Kiefer Meinhardt Cup, Glen Allen, Va.")]],
            ["0.85in", "0.55in", None],
            numcol=1,
        ),
    )
    mila_and_ratings = split(
        art(photo_mila, credit=PHOTO_CREDIT),
        ratings,
        widths=[1, 2],
    )
    nac = piece(
        "Three Head to Columbus",
        paras(NAC_BODY),
        kicker="November NAC",
        cls="slot-a",
    )
    world = piece(
        "Hungary Rules World Cup Weekend",
        paras(WORLD_BODY),
        kicker="World Cup",
        cls="slot-a",
    )
    parents = piece(
        "A National Youth Event Next Door",
        paras(PARENTS_BODY),
        kicker="For the Parents",
    )
    book = piece(
        "Three Calls, Two Minutes",
        paras(BOOK_BODY),
        kicker="By the Book",
    )
    camp = piece(
        "Winter Camp: Sign Up Now",
        paras(CAMP_BODY),
        kicker="Club Events",
    )
    party = piece(
        "Holiday Party: Friday, Dec. 11",
        paras(PARTY_BODY),
        kicker="Club Events",
    )

    page1 = page(
        masthead()
        + "\n"
        + dateline("Tuesday Edition", "Vol. I — No. 7 · Chatham, N.J. · November 17, 2026")
        + "\n"
        + cols3(
            stack(lead, mila_and_ratings),
            stack(nac, book),
        )
        + "\n"
        + split(render_piece(parents), render_piece(camp), widths=[1, 1])
        + "\n"
        + footer(7)
    )

    nearby = box(
        "Nearby Tournaments — Elite FC Entries",
        str(cobra_block),
        note=cobra_note,
        cls="w3",
    )
    road = box("On the Road — November NAC", road_block, note=road_note)
    deadlines = box("Deadlines", dead_table, note=dead_note)

    page2 = page(
        dateline("Page Two", "Club Calendar &amp; Notes &nbsp;·&nbsp; Vol. I — No. 7", first=False)
        + "\n"
        + split(render_piece(world), render_piece(party), widths=[1, 1])
        + "\n"
        + nearby
        + "\n"
        + box_pair(road, deadlines)
        + "\n"
        + art(comic)
        + "\n"
        + footer(7),
        cls="fit",
    )

    title = "En Garde Gazette — Vol. I No. 7 — November 17, 2026"
    doc = document(title, [page1, page2])
    write_issue(ISSUE, doc)


if __name__ == "__main__":
    main()
