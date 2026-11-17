#!/usr/bin/env python3
"""OPTIONAL Chrome smoke test for the Budget page (not part of the unit tests; needs playwright + google-chrome).

Opens a built page from file://, checks it renders with no script errors and no network requests, clicks through
the phone path (slip -> Page 1 / Page 2 / Bank), signs off, and writes screenshots.
  python3 scripts/tests/smoke_budget_chrome.py PAGE.html [SCREENSHOT_DIR]
"""
import json
import sys
from pathlib import Path


def main() -> int:
    from playwright.sync_api import sync_playwright
    page_file = Path(sys.argv[1]).resolve()
    shots = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None
    errors, requests = [], []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--disable-gpu"])
        for name, vp in (("desktop", {"width": 1440, "height": 900}), ("phone", {"width": 390, "height": 844})):
            ctx = br.new_context(viewport=vp, device_scale_factor=1 if name == "desktop" else 2, has_touch=name == "phone")
            pg = ctx.new_page()
            pg.on("pageerror", lambda e: errors.append(f"{name}: {e}"))
            pg.on("console", lambda m: errors.append(f"{name} console: {m.text}") if m.type == "error" else None)
            pg.on("request", lambda r: requests.append(r.url) if not r.url.startswith(("file:", "data:", "blob:")) else None)
            pg.goto(page_file.as_uri())
            pg.wait_for_selector(".page .blk")
            stats = pg.evaluate("""() => { const c = BudgetPage.core, p = [1, 2].map(n => c.pack(n)), d = BudgetPage.payload();
              return { title: document.title, blocks: document.querySelectorAll('.blk').length, holes: document.querySelectorAll('.hole').length,
                strips: document.querySelectorAll('.bank .strip').length, fill: Math.round(c.fill().pct * 100),
                pages: p.map(x => ({ placed: x.placed.length, over: x.over.length, used: +x.placedUsed.toFixed(1), open: +x.open.toFixed(1), cap: +x.cap.toFixed(1) })),
                needs: c.needs().filter(n => n.blocking).length, included: d.includedSlots.length, keys: Object.keys(d),
                overflowX: document.documentElement.scrollWidth > innerWidth + 1 }; }""")
            print(name, json.dumps(stats))
            assert stats["blocks"] and stats["holes"] is not None and not stats["overflowX"], stats
            for x in stats["pages"]:  # blocks + holes account for the whole page
                assert abs(x["used"] + x["open"] - x["cap"]) < 0.3 or x["over"], x
            if shots:
                shots.mkdir(parents=True, exist_ok=True)
                pg.screenshot(path=str(shots / f"budget-{name}.png"), full_page=name == "phone")
            # the tap path: open a bank strip's slip, run it on page 2, send it back to the bank
            pg.locator(".bank .strip[draggable] .h").first.click()
            pg.wait_for_selector("#side .place [data-pg]")
            key = pg.evaluate("document.querySelector('#side .sheet').dataset.slot")
            pg.locator('#side .place [data-pg="2"]').click()
            assert pg.evaluate("k => BudgetPage.core.state.inc[k] && BudgetPage.core.state.page[k] === 2", key)
            assert pg.locator(f'.page[data-page="2"] .blk[data-slot="{key}"]').count() >= 1 or pg.locator(f'.overset [data-slot="{key}"]').count() == 1
            if shots:
                pg.screenshot(path=str(shots / f"budget-{name}-slip.png"))
            pg.locator('#side .place [data-pg="0"]').click()
            assert pg.evaluate("k => !BudgetPage.core.state.inc[k]", key)
            if name == "desktop":  # drag (HTML5 drag events): bank -> page 1, onto another block, then back to the bank
                drag = """([from, to]) => { const src = document.querySelector(from), dst = document.querySelector(to), dt = new DataTransfer();
                  src.dispatchEvent(new DragEvent('dragstart', { bubbles: true, dataTransfer: dt }));
                  dst.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: dt }));
                  dst.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt })); }"""
                pg.evaluate(drag, [f'.bank .strip[data-slot="{key}"]', '.cols[data-page="1"]'])
                assert pg.evaluate("k => BudgetPage.core.state.inc[k] && BudgetPage.core.state.page[k] === 1", key), "drag onto page 1"
                first = pg.evaluate("BudgetPage.core.state.order.find(k => BudgetPage.core.state.inc[k])")
                pg.evaluate(drag, [f'.blk[data-slot="{key}"]', f'.blk[data-slot="{first}"]'])
                assert pg.evaluate("k => BudgetPage.core.state.order.filter(x => BudgetPage.core.state.inc[x])[0] === k", key), "drop on a block runs ahead of it"
                pg.evaluate(drag, [f'.blk[data-slot="{key}"]', "#bank"])
                assert pg.evaluate("k => !BudgetPage.core.state.inc[k]", key), "drag back to the bank"
                pg.wait_for_timeout(400)
                assert pg.evaluate("localStorage.getItem(BudgetPage.storeKey()) !== null"), "autosave"
            # history tab follows the includes; sign-off shows the document
            pg.locator('#side [data-tab="hist"]').click()
            assert pg.locator("#side table.hist tr").count() > 20
            if shots and name == "desktop":
                pg.screenshot(path=str(shots / "budget-desktop-sections.png"))
            if name == "phone":
                pg.locator("#side [data-close]").click()
            pg.locator("#sign").click()
            doc = json.loads(pg.locator("#json").inner_text())
            assert doc["pageVersion"] == "budget-paper-v2" and "publishDateAlt" in doc and "budgetVersion" in doc and "dataVersion" in doc
            if shots and name == "desktop":
                pg.screenshot(path=str(shots / "budget-desktop-signoff.png"))
            ctx.close()
        br.close()
    print("script errors:", errors or "none", "| network requests:", requests or "none")
    return 1 if errors or requests else 0


if __name__ == "__main__":
    sys.exit(main())
