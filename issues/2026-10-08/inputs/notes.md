# Issue 2026-10-08 — compose notes (Gazette Desk)

- Publish: Thursday, October 8, 2026 (Frank slot note: "We are publishing this Thursday (tomorrow)"). Vol. I — No. 1, first real issue.
- Budget: budget-demo/submissions/budget-20261007-172024.json (copied to approvals.json).
- Page 1 = NJ HS feature package (primer + Morris Hills photo + Season at a Glance + flèche sidebar) with the SYC results box topping the rail so club names lead the front.
- Page 2 = club calendar page: Go Cheer board (Medeo + all Morris Cup entries), weekly classes, NAC (Desk fill) + epee-by-day box, podium photo + Remise, Song Se-ra (Desk fill), Casablanca (Desk fill), Parent Q&A.
- Built from /tmp parts: CSS = issues/2026-10-14 v3.14 verbatim + composition additions (see issue.json "template").
- Render: `python3 prototype/render.py issues/2026-10-08/issue.html issues/2026-10-08/paper.pdf`; previews `pdftoppm -r 150`.
- Iterations: v1 3 pages (p1 overflow by ~0.3in; p2 1.25in short) → cropped Morris Hills tighter, trimmed glance labels, schedule to full-width split board, added Song + NAC box → v6 2 pages, all instruments OK.
