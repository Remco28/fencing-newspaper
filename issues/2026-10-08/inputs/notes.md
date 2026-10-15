# Issue 2026-10-08 — compose notes (Gazette Desk)

- Publish: Thursday, October 8, 2026 (Frank slot note: "We are publishing this Thursday (tomorrow)"). Vol. I — No. 1, first real issue.
- Budget: budget-demo/submissions/budget-20261007-172024.json (copied to approvals.json).
- Page 1 = NJ HS feature package (primer + Morris Hills photo + Season at a Glance + flèche sidebar) with the SYC results box topping the rail so club names lead the front.
- Page 2 = club calendar page: Go Cheer board (Medeo + all Morris Cup entries), weekly classes, NAC (Desk fill) + epee-by-day box, podium photo + Remise, Song Se-ra (Desk fill), Casablanca (Desk fill), Parent Q&A.
- Built from /tmp parts: CSS = issues/2026-10-14 v3.14 verbatim + composition additions (see issue.json "template").
- Render: `python3 prototype/render.py issues/2026-10-08/issue.html issues/2026-10-08/en-garde-gazette-no-1-2026-10-08.pdf`; previews `pdftoppm -r 150`.
- Iterations: v1 3 pages (p1 overflow by ~0.3in; p2 1.25in short) → cropped Morris Hills tighter, trimmed glance labels, schedule to full-width split board, added Song + NAC box → v6 2 pages, all instruments OK.

## Proof v2 (2026-10-07 evening)

- Frank's chat answers (~17:53 ET): podium girls = Mila Siu + Penny Young; NAC registrants confirmed (Penny Young, Amina Gore, Maksim Milinkovic, Anayaa Sheth — Frank's ASCII spelling); photos fine; all Desk-fill kept.
- Go Cheer: added October NAC group (events/days from FencingTracker; no times). Layout: left = NAC + Morris Cup Sat, right = Medeo + Morris Cup Sun.
- Weekly Classes: Time column left-aligned (fixed 1.15in col, 8pt right pad). Rahi Shah Mirani no-wrap.
- Page-2 bottom row reflowed: col 1 NAC + by-day box; col 2 podium photo + Parent Q&A; col 3 Song + Casablanca + Remise.
- Trims (Desk-fill only): Casablanca 43 -> 23 words; Song 84 -> 63 words. No type shrunk.
- Instruments: 2 pages; p2 gap 0.12in; row-2 spread 0.19in.
