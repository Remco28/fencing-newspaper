# Eye check: PASS

PDF `issues/2026-11-24/en-garde-gazette-no-8-2026-11-24.pdf` (sha256 9d73281a7a92), checked 2026-11-24T16:01:07-05:00.

## Vision critique (claude-sonnet-5-5): PASS

Both pages are well filled. The largest hole is about 1.0 sq in, the gaps are even, there are no stranded widows, and the photos are large and legible. Only minor polish remains: uneven column bottoms and box bottoms, and a few short last lines.

- blank_space: pass - The largest blank is about 1.0 sq in, under the 1.5 sq in limit. It sits under the middle column on page 1 (x≈2.9in, y≈10.0in). Page 1 footer gaps are 0.16 and 0.24in, and page 2 gaps are 0.24 and 0.19in. All are within the approved reference's ~0.4in. The page 2 pixel-map candidates are ragged-right headline or short-line space, not holes.
- even_gaps: pass - The measured gaps of 6–8pt are consistent on both pages. Nothing touches. On page 2 the gap under the right-hand 'On the Road' box looks a little larger than the others, because that box ends higher than the left-hand Nearby Tournaments box. It is not a major problem.
- no_widows: pass - No stranded word is at the top of a column or box. Table cells wrap to 2–3 lines at most, with no tall sliver: 'Cadet Challenger', 'Y12 Women', the Deadlines text and 'Amina Gore, Anayaa Sheth'. A few paragraphs end on short lines, which is minor.
- photo_sizing: pass - Both page 1 photos are large and clearly legible, and the second is at least as big as the first. There are no lettered cartoons, and nothing looks like an afterthought.
- focal_point: pass - The page 1 lead headline and its long text block anchor the page. The big photos in the right column are secondary but strong. The reference also runs a text-only lead.
- alignment: pass - The page 1 column bottoms are slightly uneven (left ≈ 10.2in, middle ≈ 9.9in, right ≈ 10.2in). On page 2 the side-by-side box bottoms differ by about 0.1in (left box ≈ 3.9in, right box ≈ 3.8in). Rules and borders are consistent, and nothing looks accidental enough to count as major.
- [minor] p1 Middle column bottom (Holiday Party story): The column ends about 0.3in higher than the left and right columns, leaving a ~1.0 sq in pocket above the footer. -> Add about 15–20 words to the Holiday Party blurb, for example the time or location, or trim about 10 words from the left column so the bottoms match.
- [minor] p1 Left column, 'Club Closed Wednesday Through Friday' and the mid-column NAC story: Each paragraph ends in a short last line ('Saturday, Nov. 28.' and 'entry list.'). -> Trim or add about 3–5 words in each to fill the last line.
- [minor] p1 Club Results table: The 'Cadet Challenger' and 'Y12 Women' event cells wrap to two lines, which makes the rows tall. -> Shorten them to 'Cadet Chall.' and 'Y12 W', or widen the Event column.
- [minor] p2 Top row: Nearby Tournaments box next to the On the Road box: The box bottoms don't line up (left ≈ 773px, right ≈ 752px). This leaves the gap above Deadlines visibly larger on the right than on the left. -> Add about 8–10 words to the On the Road footnote, or trim one line from the Nearby Tournaments footnote, so both boxes end together.
- [minor] p2 On the Road box header: The title wraps to two lines ('ON THE ROAD — DECEMBER / SJCC'), and the sub-header 'Dec. 4–6' also wraps. -> Shorten the title to 'ON THE ROAD — DEC. SJCC' and tighten the sub-header.

## Pixel blank map

- Page 1: 2.56x0.4in @(2.94,10.0); 0.74x0.54in @(4.64,5.5)
- Page 2: 1.38x0.66in @(4.0,3.92); 1.66x0.42in @(6.34,8.62); 1.12x0.44in @(6.88,6.74)

Send only after `python3 compose/eyecheck.py --verify <pdf>` passes and Clark has looked at the previews.
