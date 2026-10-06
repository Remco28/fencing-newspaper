# Gazette Vocabulary — words for talking about this project
For Frank: publishing terms, HTML-to-PDF terms, and our project workflow terms,
each with what it means *here*. New terms get added at the bottom with dates.

## Newspaper craft
- **Masthead / nameplate** — the paper's title logo at the top of page 1. Ours is `masthead001.png`.
- **Flanks** — the small info blocks left and right of the masthead (Vol/No, date, price).
- **Dateline bar** — the ruled strip under the masthead: edition, date, issue number.
- **Lead story** — the main article, top of page 1. Biggest news, biggest headline.
- **Dek** — the italic summary line under a headline. One or two lines, never more.
- **Byline** — "who wrote it" line. We don't use them for Frank; guests get credited.
- **Rail** — a narrow side column of stacked boxes (ratings, scoreboard).
- **Box** — bordered content block. Tabular data always; utility boxes may; articles never.
- **Boxtitle / kicker** — the small caps title on a box. Plain text only, no symbols.
- **Rule** — a printed line. Thin (1pt) dividers, thick (2.5pt) for dateline/footer.
- **Column rule** — the vertical line between text columns. Classic newspaper divider.
- **Folio / footer** — the bottom strip: paper name, issue number, archive note.
- **Above / below the fold** — top / bottom half of the page (from papers folded for sale).
  Front-page top should always carry the best item.
- **Cut / trim** — shortening copy to fit. We cut bottom-up per CONTENT-HIERARCHY.md.
- **Kill** — dropping an item entirely. ("Kill the ice-cream piece.")
- **Budget (meeting)** — the pre-layout decision of what goes in. Our checkbox page *is* this.
- **Makeup** — arranging approved content onto pages. What the template does.
- **Flatplan** — a thumbnail map of all pages and what's on each. (We have 2 pages; still useful.)
- **Proof** — the rendered PDF you check before anything prints. Nothing prints unproofed.
- **Corrections box** — printed fixes to past errors. Builds trust; folded into About until needed.
- **Widow / orphan** — a stranded line: paragraph-ending word alone atop a column (widow),
  or a headline alone at a column bottom with its text elsewhere (orphan). Both banned.
- **Tombstoning** — two headlines sitting side by side at the same height in adjacent columns,
  so the eye can't tell which text belongs to which. Stagger headlines to avoid it.
- **Pull-quote** — an enlarged excerpt repeated mid-article to fill space and catch the eye.
  Our approved filler for column-bottom voids.
- **Halftone / dither** — how photos survive B&W laser: rendered as dot patterns, not gray.
  Preview photos dithered or you're guessing.

## Layout & type
- **Grid** — the invisible column structure everything aligns to. Ours: 3 columns, 9pt gutters.
- **Gutter** — the gap between columns.
- **Measure** — a column's text width (~2.3in here). Shorter measures read faster.
- **Leading** — line spacing (~1.26× type size here). Never stretched to fake fullness.
- **Point (pt)** — type size unit. Body 8.5pt; nothing below the 7pt floor, ever.
- **Sans / serif** — headlines Arial Black (sans), body Times (serif).
- **Small caps / caps** — box titles and dateline style. Hierarchy without decoration.
- **Tabular numerals** — digits that all share one width, so stacked numbers align.
- **Hanging indent** — wrapped lines align under the text, not the label (scoreboard rows).
- **Widow control for tables** — row rules 0.5pt, header rule 1.5pt, consistent padding.

## HTML → PDF (how the paper gets made)
- **Template** — the HTML+CSS file with empty slots. Frozen once locked; content flows in.
- **Issue file (`issue.json`, future)** — one issue's content in strict schema with word budgets.
- **Render** — converting HTML to PDF. Always via `prototype/render.py` (never bare Chrome flags).
- **CDP** — Chrome Debug Protocol: how `render.py` drives Chrome (no headers, measure layout).
- **CSS `@page`** — the print rule declaring Letter size + margins. Margins live here only.
- **Viewport vs. page** — screen preview vs. printed sheet. They mostly match; trust the PDF.
- **Chrome headers/chrome (browser chrome)** — the date/URL/title stamps browsers add when
  printing. Banned; `render.py` suppresses them. (Unrelated to everyday "chrome" the metal.)
- **Flexbox** — the CSS layout used for rows/columns. Note: flex *stretches* children equal,
  so box heights lie — measure content depth, not box height.
- **Colgroup** — declared table column widths. Meta columns (dates/ratings) get fixed narrow
  widths so values sit snug, never floating.
- **Specificity** — which CSS rule wins when two collide. (Once cost us right-aligned headers.
  More specific = wins: `table.board th.r` beats `table.board th`.)
- **Void element** — tags with no close (`<hr>`, `<img>`, `<col>`). Validators must skip them
  or div-counting lies.
- **Div nesting / stray close** — every `<div>` needs its match. A stray `</div>` silently
  re-parents content and poisons all measurements. Validate mechanically (see README).

## Project workflow
- **Pattern** — a pre-designed arrangement (FRONT-A, BACK-A…). Selected per issue, never invented.
- **Slot / budget** — a pattern position plus its word/row allowance (~40 words/column-inch).
- **Oversupply (115%)** — always generate more than fits, then cut bottom-up. Mandatory.
- **Cut hierarchy / stretch hierarchy** — the order for trimming (shorts first) or growing
  (Fencing 101 first) content. In CONTENT-HIERARCHY.md and STYLE-GUIDE.md §11.
- **Fill-or-flag** — every page filled or Frank gets told what's missing, in inches and words.
- **Gap instrument** — `render.py`'s measured daylight above each footer. FLAG above 0.75in.
- **Region balance** — columns within a row ending within 0.5in of each other.
- **Zoomed QA** — checking each board at 150dpi+. Thumbnails are for taste; numbers are for fill.
- **Provenance** — every printed fact carries its source (URL+date or email ID). No provenance,
  no render. (Future gate; the rule already stands.)
- **Two gates** — (1) approve the budget, (2) approve the proof. Nothing prints otherwise.
- **Budget sheet** — the local approval web page (checkboxes for stories + photos). Writes
  `approvals.json`. Chat is doorbell-only.
- **Makeup output** — the final `paper.pdf` for the issue folder.
- **Dry run** — a full issue built for red-pen review, never printed for the club.

## Added later
- *(append new terms here with date)*
