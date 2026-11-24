#!/usr/bin/env python3
"""Issue No. 8 recipe — Tuesday, November 24, 2026.

Matches Frank's Manual budget submission (2026-11-24 3:38 PM ET, budget v2,
data ebead6e13faa) by hand. Compose does not pack from manualLayout.
"""
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

ISSUE = "issues/2026-11-24"
LINEUP = "budget-demo/archive/practice-lineup-issue8-2026-11-24.json"
WEEK = "staging/weeks/2026-11-24"

items = {i["id"]: i for i in load(WEEK + "/items.json")["items"]}
PHOTO_CREDIT = "Photo: Elite Fencers Club"

# ---------------------------------------------------------------------------
# Copy lengths (Frank's resize targets). Every variant is from vetted sources
# only; college is not padded with later, unverified meets.
# ---------------------------------------------------------------------------

LEAD = {
    "short": (
        "The Cobra Challenge SYC/RCC is Friday through Sunday, Nov. 27–29, at the "
        "Meadowlands Expo Center in Secaucus, a short trip from the club. Sixteen "
        "Elite FC fencers have 26 approved entries in Youth 10, Youth 12, Youth 14 "
        "and Cadet epee. Several fields are already full: Youth 14 Men has 140 "
        "official competitors, Youth 14 Women 133, Cadet Men 126, Youth 12 Women 106 "
        "and Cadet Women 105.\n\n"
        "For parents still learning the youth-tournament alphabet, Cobra is an SYC — "
        "a Super Youth Circuit, not simply a larger Regional Youth Circuit event. The "
        "two circuits award different points, feed different standings and open "
        "different paths to national tournaments.\n\n"
        "A Regional Youth Circuit tournament, or RYC, awards only regional points, "
        "and only to fencers competing in their home region. Everyone in the event "
        "earns some. The formula is ((number of entries minus place plus 1) divided "
        "by the number of entries) times 100, so the winner always receives 100 "
        "points, whatever the field size. A fencer's best three RYC results in that "
        "region count toward the Regional Youth Point Standings. Those points do not "
        "appear on the national point lists.\n\n"
        "A Super Youth Circuit tournament awards national youth points, and a fencer "
        "from any region can earn them by placing high enough. Points go to the top "
        "40 percent of the competitive field — current competitive members in the "
        "starting field — rounded up, to a maximum of 64th place. At least three "
        "fencers must compete. Only a fencer's single best SYC result in each age "
        "category counts. USA Fencing then builds the Youth Point Standings from the "
        "four highest results among that SYC, North American Cups and National "
        "Championships in the eligible age groups.\n\n"
        "That is why an SYC carries more weight for younger fencers. To enter Youth "
        "10 or Youth 12 at the March NAC in Atlantic City, a fencer must have competed "
        "in one RYC or one SYC this season in the same age group and weapon (Youth 12 "
        "fencers on the national point standings also qualify). Youth 14 has no such "
        "qualifying path for the March NAC; age is enough. For the USA Fencing "
        "National Championships in the summer, the national point standings — which "
        "an SYC result can help build — are one qualifying path in Youth 10, Youth 12 "
        "and Youth 14.\n\n"
        "Cobra is a local SYC, which is unusual. Super Youth Circuit tournaments are "
        "held throughout the country, and many families travel to them. This one is "
        "in Secaucus. There are no rating requirements for an SYC or an RYC, only a "
        "current competitive membership and the right age group.\n\n"
        "The SYC format is one round of pools, with every fencer advancing to direct "
        "elimination. Youth 10 direct-elimination bouts are to 10 touches, in two "
        "three-minute periods. Youth 12 and Youth 14 are to 15. There is no fence-off "
        "for third place. Cobra also runs Cadet events as a Regional Cadet Circuit, "
        "not as an SYC, and those results do not earn youth national points."
    ),
    "standard": (
        "The Cobra Challenge SYC/RCC is Friday through Sunday, Nov. 27–29, at the "
        "Meadowlands Expo Center in Secaucus, a short trip from the club. Sixteen "
        "Elite FC fencers have 26 approved entries in Youth 10, Youth 12, Youth 14 "
        "and Cadet epee. Several fields are already full: Youth 14 Men has 140 "
        "official competitors, Youth 14 Women 133, Cadet Men 126, Youth 12 Women 106 "
        "and Cadet Women 105.\n\n"
        "For parents still learning the youth-tournament alphabet, Cobra is an SYC — "
        "a Super Youth Circuit, not simply a larger Regional Youth Circuit event. The "
        "two circuits award different points, feed different standings and open "
        "different paths to national tournaments.\n\n"
        "A Regional Youth Circuit tournament, or RYC, awards only regional points, "
        "and only to fencers competing in their home region. Everyone in the event "
        "earns some. The formula is ((number of entries minus place plus 1) divided "
        "by the number of entries) times 100, so the winner always receives 100 "
        "points, whatever the field size. A fencer's best three RYC results in that "
        "region count toward the Regional Youth Point Standings. Those points do not "
        "appear on the national point lists.\n\n"
        "A Super Youth Circuit tournament awards national youth points, and a fencer "
        "from any region can earn them by placing high enough. Points go to the top "
        "40 percent of the competitive field — current competitive members in the "
        "starting field — rounded up, to a maximum of 64th place. At least three "
        "fencers must compete. Only a fencer's single best SYC result in each age "
        "category counts. USA Fencing then builds the Youth Point Standings from the "
        "four highest results among that SYC, North American Cups and National "
        "Championships in the eligible age groups.\n\n"
        "That is why an SYC carries more weight for younger fencers. To enter Youth "
        "10 or Youth 12 at the March NAC in Atlantic City, a fencer must have competed "
        "in one RYC or one SYC this season in the same age group and weapon (Youth 12 "
        "fencers on the national point standings also qualify). Youth 14 has no such "
        "qualifying path for the March NAC; age is enough. For the USA Fencing "
        "National Championships in the summer, the national point standings — which "
        "an SYC result can help build — are one qualifying path in Youth 10, Youth 12 "
        "and Youth 14. Regional RYC points are another: 60 Youth 12 regional points "
        "can qualify a Youth 10 fencer, 70 Youth 12 or 160 Youth 14 regional points a "
        "Youth 12 fencer, and 160 Youth 14 regional points a Youth 14 fencer, each "
        "from the fencer's best three regional results.\n\n"
        "Cobra is a local SYC, which is unusual. Super Youth Circuit tournaments are "
        "held throughout the country, and many families travel to them. This one is "
        "in Secaucus. There are no rating requirements for an SYC or an RYC, only a "
        "current competitive membership and the right age group.\n\n"
        "The SYC format is one round of pools, with every fencer advancing to direct "
        "elimination. Youth 10 direct-elimination bouts are to 10 touches, in two "
        "three-minute periods. Youth 12 and Youth 14 are to 15.\n\n"
        "Cobra also runs Cadet events as a Regional Cadet Circuit, not as an SYC, "
        "and those results do not earn youth national points."
    ),
    "long": (
        "The Cobra Challenge SYC/RCC is Friday through Sunday, Nov. 27–29, at the "
        "Meadowlands Expo Center in Secaucus, a short trip from the club. Sixteen "
        "Elite FC fencers have 26 approved entries in Youth 10, Youth 12, Youth 14 "
        "and Cadet epee. Several fields are already full: Youth 14 Men has 140 "
        "official competitors, Youth 14 Women 133, Cadet Men 126, Youth 12 Women 106 "
        "and Cadet Women 105.\n\n"
        "For parents still learning the youth-tournament alphabet, Cobra is an SYC — "
        "a Super Youth Circuit, not simply a larger Regional Youth Circuit event. The "
        "two circuits award different points, feed different standings and open "
        "different paths to national tournaments, and those differences matter most "
        "for the younger age groups.\n\n"
        "A Regional Youth Circuit tournament, or RYC, awards only regional points, "
        "and only to fencers competing in their home region. Everyone in the event "
        "earns some. The formula is ((number of entries minus place plus 1) divided "
        "by the number of entries) times 100, so the winner always receives 100 "
        "points, whatever the field size. A fencer's best three RYC results in that "
        "region count toward the Regional Youth Point Standings. Those points do not "
        "appear on the national point lists. An RYC must have at least two competitors "
        "for regional points to be awarded.\n\n"
        "A Super Youth Circuit tournament awards national youth points, and a fencer "
        "from any region can earn them by placing high enough. Points go to the top "
        "40 percent of the competitive field — current competitive members in the "
        "starting field — rounded up, to a maximum of 64th place. At least three "
        "fencers must compete. Only a fencer's single best SYC result in each age "
        "category counts. USA Fencing then builds the Youth Point Standings from the "
        "four highest results among that SYC, North American Cups and National "
        "Championships in the eligible age groups.\n\n"
        "That is why an SYC carries more weight for younger fencers. To enter Youth "
        "10 or Youth 12 at the March NAC in Atlantic City, a fencer must have competed "
        "in one RYC or one SYC this season in the same age group and weapon (Youth 12 "
        "fencers on the national point standings also qualify). Youth 14 has no such "
        "qualifying path for the March NAC; age is enough. For the USA Fencing "
        "National Championships in the summer, the national point standings — which "
        "an SYC result can help build — are one qualifying path in Youth 10, Youth 12 "
        "and Youth 14. Regional RYC points are another: 60 Youth 12 regional points "
        "can qualify a Youth 10 fencer, 70 Youth 12 or 160 Youth 14 regional points a "
        "Youth 12 fencer, and 160 Youth 14 regional points a Youth 14 fencer, each "
        "from the fencer's best three regional results.\n\n"
        "Cobra is a local SYC, which is unusual. Super Youth Circuit tournaments are "
        "held throughout the country, and many families travel to them. This one is "
        "in Secaucus. There are no rating requirements for an SYC or an RYC, only a "
        "current competitive membership and the right age group. Youth 8 events, when "
        "they appear, are not part of either circuit for points.\n\n"
        "The SYC format is one round of pools, with every fencer advancing to direct "
        "elimination. Youth 10 direct-elimination bouts are to 10 touches, in two "
        "three-minute periods. Youth 12 and Youth 14 are to 15. There is no fence-off "
        "for third place.\n\n"
        "Cobra also runs Cadet events as a Regional Cadet Circuit, not as an SYC, "
        "and those results do not earn youth national points.\n\n"
        "The club is closed Friday for Thanksgiving. Regular classes resume Saturday, "
        "Nov. 28."
    ),
}

MARCH = {
    "standard": items["desk-march-nac-feature-2026-11-23"]["body"],
}

NAC_BODY = items["ft-november-nac-results-2026-11-24"]["body"]

FAIR = {
    "short": items["desk-secondary-fair-play-schembri-2026-11-23"]["body"],
    "standard": (
        "The FIE named Kruz Schembri, the world's No. 1 junior men's epee fencer, a "
        "co-winner of its 2026 Fair Play Trophy at its annual awards gala in Budapest "
        "on Sunday, Nov. 22. The award recognized a moment at this year's Senior World "
        "Championships in Hong Kong: Schembri was tied 13–13 in a round-of-32 bout "
        "with Italy's Davide Di Veroli when he was awarded a touch that would have "
        "put him one away from winning. He told the referee he had hit himself and "
        "refused the touch. Di Veroli won the bout 15–13 and went on to take silver "
        "at the championships. Schembri shared the trophy with Gilles Martinage, the "
        "French team's armorer, who had fixed Schembri's weapons in Hong Kong after "
        "three of his four blades failed inspection. Schembri, 20, represents the "
        "U.S. Virgin Islands. The same gala honored the season's other epee No. 1s: "
        "Alberta Santuccio of Italy and Mohamed Elsayed of Egypt among the seniors, "
        "and Sofija Prošina of Latvia among junior women."
    ),
}

BOOK = {
    "short": items["desk-by-the-book-two-of-everything-2026-11-23"]["body"],
    "standard": (
        "Packing for Cobra this weekend? Rule t.117 says a fencer must come to the "
        "strip with two weapons, two body cords and two mask cords, one of each as a "
        "spare, all in perfect working order. Arriving without the second weapon or "
        "body cord, or with equipment that doesn't work or doesn't conform, is a "
        "first-group offense on the penalty chart (t.71–t.73, t.117): a Yellow Card "
        "the first time, then a Red Card, which gives the opponent a touch. Check "
        "tips and cords at home, not in line at the strip."
    ),
    "long": (
        "Packing for Cobra this weekend? Rule t.117 says a fencer must come to the "
        "strip with two weapons, two body cords and two mask cords, one of each as a "
        "spare, all in perfect working order. Arriving without the second weapon or "
        "body cord, or with equipment that doesn't work or doesn't conform, is a "
        "first-group offense on the penalty chart (t.71–t.73, t.117): a Yellow Card "
        "the first time, then a Red Card, which gives the opponent a touch. Both "
        "sets have to be complete and working before the fencer steps on the strip. "
        "Check tips and cords at home, not in line at the strip."
    ),
}

PARTY = {
    "short": (
        "This year's Elite FC holiday party will be Friday, Dec. 11. There will be "
        "food, drinks and snacks, and everyone is welcome."
    ),
    "standard": (
        "This year's Elite FC holiday party will be Friday, Dec. 11. There will be "
        "food, drinks and snacks, and everyone is welcome. The club hopes you can "
        "join to celebrate the year."
    ),
    "long": items["email-holiday-party-2026-12-11"]["body"],
}

THANKS = {
    "short": (
        "Elite FC will be closed Wednesday, Nov. 25, through Friday, Nov. 27, for "
        "Thanksgiving. Regular classes resume Saturday, Nov. 28."
    ),
    "standard": (
        "Elite FC will be closed Wednesday, Nov. 25, through Friday, Nov. 27, for "
        "the Thanksgiving holiday, including Friday, when the Cobra Challenge begins. "
        "Regular classes resume Saturday, Nov. 28."
    ),
}

COLLEGE = {
    "short": (
        "NCAA fencing season opened the first weekends of November. NJIT hosted its "
        "first home meet since 2019 on Nov. 1 (men 2–0, women 1–1), then fenced the "
        "Drew Invitational in Madison, N.J., on Nov. 7 and the Columbia Invitational "
        "in New York on Nov. 8. Duke beat North Carolina in their opener."
    ),
    "standard": (
        "NCAA fencing season opened the first weekends of November. NJIT hosted its "
        "first home meet since 2019 on Nov. 1, the men going 2–0 and the women 1–1, "
        "then fenced the Drew Invitational in Madison, N.J., on Nov. 7 — a short trip "
        "from Chatham — and the Columbia Invitational in New York on Nov. 8. Duke beat "
        "North Carolina in their opener."
    ),
}

# Club results: table only (Frank shrink 27→3: drop the Jiang prose graf).
# Format must be "Tournament, Event (Date)" so results_table() can group sub-rows.
CLUB_ROWS = [
    ["Nico Ng", "November NAC, Cadet Challenger (Nov. 21)", "15th of 136"],
    ["Christina Jiang", "Freehold Youth, Y12 Women (Nov. 22)", "1st of 4"],
]

# Cobra board: official close-of-registration times, Nov. 24 official page.
COBRA = items["fencingapi-cobra-efc-entries-2026-10-19"]
_cobra_days = []
_close = COBRA.get("close_of_registration_2026_11_24") or {}
for day, event, names, _n in COBRA["panels_rows"]:
    cell_event, cell_names = ty(event), ty(names)
    if _cobra_days and _cobra_days[-1][0] == day:
        _cobra_days[-1][1].append([cell_event, cell_names])
    else:
        _cobra_days.append([day, [[cell_event, cell_names]]])
cobra_days = [(ty(day), rows) for day, rows in _cobra_days]
cobra_block = tourney(
    "Cobra Challenge SYC/RCC",
    "Secaucus, N.J.",
    "Nov.&nbsp;27–29",
    ["Event", "Elite FC"],
    ["1.05in", None],
    cobra_days,
)
# Close-of-registration times, official page Nov. 24. Kept in the note so the board stays compact.
_close_bits = []
for day, event, names, _n in COBRA["panels_rows"]:
    tm = _close.get(event)
    if tm:
        _close_bits.append(f"{event} {tm}")
cobra_note = ty(
    "Sixteen Elite FC fencers, 26 entries, all approved. Close of registration is on the "
    "official USA Fencing page (Nov. 24). Youth 14 Men is at 140 and capped."
)

ROAD = items["ft-efc-on-the-road-dec-sjcc-2026-11-23"]
_road_days = []
for day, event, names in ROAD["rows"]:
    cell_event, cell_names = ty(event), ty(names)
    if _road_days and _road_days[-1][0] == day:
        _road_days[-1][1].append([cell_event, cell_names])
    else:
        _road_days.append([day, [[cell_event, cell_names]]])
road_days = [(ty(day), rows) for day, rows in _road_days]
road_block = tourney(
    "December SJCC",
    "Milwaukee, Wis.",
    "Dec.&nbsp;4–6",
    ["Event", "Elite FC"],
    ["1.05in", None],
    road_days,
    layout="rows",
)
road_note = ty(
    "Baird Center. Three Elite FC fencers, five approved entries, as of Nov. 23."
)

# Tight rail wording, same vetted deadlines (full phrasing is in the item body/note).
dead_rows = [
    [ty("Nov. 30"), ty("Fairfax Challenge: last day of regular fees; triple from Dec. 1")],
    [ty("Dec. 10"), ty("Z1 RYC/RJCC: late registration closes")],
    [ty("Jan. 6"), ty("March NAC: last day of regular fees; late fees triple")],
    [ty("Jan. 7"), ty("Junior Olympics: late registration ends")],
    [ty("Jan. 8"), ty("N.J. high school: independent fencers' entries close")],
]
dead_table = table(["Date", "What's due"], dead_rows, ["0.72in", None], numcol=0)
dead_note = ty(
    "USA Fencing fee deadlines are 11:59 p.m. Pacific. Z1 regular fees ended Nov. 23."
)

# Frank's manual layout is the only legal candidate this week: page/column
# assignments stay put. arrange.py is still run so the ranking is on record.
ARRANGEMENTS = {
    "manual": {"map": "frank-2026-11-24"},
}
DEFAULT_ARRANGEMENT = "manual"


def build(arrangement=DEFAULT_ARRANGEMENT, picks=None):
    """Return the issue HTML for one arrangement and one set of length picks."""
    if arrangement not in ARRANGEMENTS:
        raise SystemExit(f"unknown arrangement {arrangement!r}")
    picks = lengths_for(ISSUE) if picks is None else picks
    assets = load_art_manifest(ISSUE + "/recipe/art.json")
    by_id = {a["id"]: a for a in assets}
    photo_jiang = by_id["christina-jiang-freehold-youth"]
    photo_nac = by_id["efc-november-nac-photo"]
    for a in (photo_jiang, photo_nac):
        if a.get("caption"):
            a["caption"] = ty(a["caption"])

    march = piece(
        "March NAC Comes to Atlantic City",
        paras(copy_length("march-nac", MARCH, picks)),
        kicker="A National Tournament Next Door",
        cls="slot-a",
    )
    fair = piece(
        "The Touch He Gave Back",
        paras(copy_length("fair-play", FAIR, picks)),
        kicker="Fair Play",
    )
    nac = piece(
        "Nico Ng 15th of 136 in Cadet Challenger",
        paras(NAC_BODY),
        kicker="November NAC",
        cls="slot-a",
    )
    party = piece(
        "Holiday Party: Friday, Dec. 11",
        paras(copy_length("party", PARTY, picks)),
        kicker="Club Events",
    )
    thanks = piece(
        "Club Closed Wednesday Through Friday",
        paras(copy_length("thanksgiving", THANKS, picks)),
        kicker="Club Events",
    )
    lead = piece(
        "This Weekend at Cobra: What an SYC Is, and Why It Matters",
        paras(copy_length("lead", LEAD, picks)),
        level=1,
        cls="lead",
    )
    book = piece(
        "Two of Everything",
        paras(copy_length("by-the-book", BOOK, picks)),
        kicker="By the Book",
    )
    college = piece(
        "College Season Opens Next Door",
        paras(copy_length("college", COLLEGE, picks)),
        kicker="College",
    )

    club = box(
        "Club Results",
        results_table(
            CLUB_ROWS,
            cols=["0.88in", None, "0.70in"],
            head=("Fencer", "Event", "Finish"),
        ),
        note=ty("Cadet place is in the Challenger field, not the combined entry list."),
    )

    # Page 1 matches Frank's page/column map, as one span2 + rail so the
    # shorter March piece does not leave a hole above Fair Play / the NAC short:
    #   span 2: March NAC, then Fair Play | NAC short + party
    #   rail:   club results, Jiang photo, NAC photo, Thanksgiving
    # Tasteful departure from the inch grid, same page/column map: Thanksgiving
    # sits under Fair Play so the span 2 fills, and the portrait NAC photo
    # stacks at rail width (soft-ceiling WARN, still in Frank's rail) in place
    # of that box. Party and the NAC short stay in column 1.
    left = stack(
        march,
        split(stack(fair, thanks), stack(nac, party), widths=[1, 1]),
    )
    right = stack(
        club,
        art(photo_jiang, credit=PHOTO_CREDIT),
        art(photo_nac, credit=PHOTO_CREDIT),
    )
    page1 = page(
        masthead()
        + "\n"
        + dateline("Tuesday Edition", "Vol. I — No. 8 · Chatham, N.J. · November 24, 2026")
        + "\n"
        + cols3(left, right)
        + "\n"
        + footer(8),
        cls="fit",
    )

    # Page 2: Cobra board span 2 | On the Road; then lead span 2 | deadlines, book, college.
    nearby = box("Nearby Tournaments — Elite FC Entries", str(cobra_block), note=cobra_note, cls="w3")
    road = box("On the Road — December SJCC", road_block, note=road_note)
    deadlines = box("Deadlines", dead_table, note=dead_note)
    row3 = cols3(nearby, road)
    row4 = cols3(render_piece(lead), stack(deadlines, book, college))
    page2 = page(
        dateline("Page Two", "Club Calendar &amp; Notes &nbsp;·&nbsp; Vol. I — No. 8", first=False)
        + "\n"
        + row3
        + "\n"
        + row4
        + "\n"
        + footer(8),
        cls="fit",
    )

    # Clean title: proof labels stay on the proof file / issue.json, not in the PDF <title>.
    title = "En Garde Gazette — Vol. I No. 8 — November 24, 2026"
    extra = (
        "    /* Same column rhythm as .c, inside a .split (Fair Play / NAC short "
        "stacks). Uses the --gap-block token, not a one-off margin. */\n"
        "    .split > * > * + :not(p),\n"
        "    .split > * > :not(p) + p { margin-top: var(--gap-block); }\n"
    )
    return document(title, [page1, page2], extra_css=extra)


def main():
    name = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--arrangement=")), None)
    f = REPO / ISSUE / "recipe" / "arrangement.json"
    if name is None and f.is_file():
        import json as _json
        name = _json.loads(f.read_text(encoding="utf-8")).get("arrangement")
    name = name or DEFAULT_ARRANGEMENT
    print(f"arrangement: {name}; lengths: {lengths_for(ISSUE) or 'all standard'}")
    for key, variants in (
        ("lead", LEAD),
        ("fair-play", FAIR),
        ("college", COLLEGE),
        ("party", PARTY),
        ("thanksgiving", THANKS),
        ("by-the-book", BOOK),
        ("march-nac", MARCH),
    ):
        text = copy_length(key, variants, lengths_for(ISSUE))
        print(f"  {key}: {LENGTH_CHOICES.get(key)} {words(text)}w")
    write_issue(ISSUE, build(name))
    print(f"length choices: {LENGTH_CHOICES}")


if __name__ == "__main__":
    main()
