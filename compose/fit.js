/* Art-fit helpers, evaluated once per Chrome session. Dumb apply/reset/measure; Python owns policy. */
(() => {
  const inch = (px) => px / 96;
  const orig = new WeakMap();

  const remember = (el) => {
    if (!orig.has(el)) {
      orig.set(el, {
        cls: el.className,
        style: el.getAttribute("style") || "",
        parentDisplay: el.parentElement ? el.parentElement.style.display : "",
      });
    }
  };

  const reset = (el) => {
    const o = orig.get(el);
    if (!o) return;
    el.className = o.cls;
    if (o.style) el.setAttribute("style", o.style);
    else el.removeAttribute("style");
    if (el.parentElement) el.parentElement.style.display = o.parentDisplay;
  };

  const wrapOk = (el) => {
    let n = el.nextElementSibling;
    while (n) {
      if (n.matches && n.matches("p")) return true;
      if (n.matches && n.matches("table, .box, .textcols, .board-split, .tourney")) return false;
      if (n.querySelector) {
        const p = n.querySelector("p");
        if (p && !n.querySelector("table, .box, .board")) return true;
      }
      n = n.nextElementSibling;
    }
    return false;
  };

  const regionWidthIn = (el) => {
    const parent = el.parentElement;
    const r = parent.getBoundingClientRect();
    const cs = getComputedStyle(parent);
    const pl = parseFloat(cs.paddingLeft) || 0;
    const pr = parseFloat(cs.paddingRight) || 0;
    return inch(r.width - pl - pr);
  };

  const lastWrappedBottom = (slot) => {
    const fr = slot.getBoundingClientRect();
    let last = -Infinity;
    const range = document.createRange();
    let n = slot.nextElementSibling;
    while (n) {
      const ps = n.matches && n.matches("p") ? [n] : (n.querySelectorAll ? [...n.querySelectorAll("p")] : []);
      for (const p of ps) {
        const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
        for (let t = w.nextNode(); t; t = w.nextNode()) {
          if (!t.nodeValue.trim()) continue;
          range.selectNodeContents(t);
          for (const r of range.getClientRects()) {
            if (r.width > 0 && r.top < fr.bottom - 1) last = Math.max(last, r.bottom);
          }
        }
      }
      n = n.nextElementSibling;
    }
    return last;
  };

  const interiorGapPx = (slot) => {
    const top = slot.getBoundingClientRect().top;
    const parent = slot.parentElement;
    const cs = getComputedStyle(parent);
    const pt = parseFloat(cs.paddingTop) || 0;
    const prev = slot.previousElementSibling;
    const start = prev ? prev.getBoundingClientRect().bottom : (parent.getBoundingClientRect().top + pt);
    return top - start;
  };


  const SEL = '[data-balance], .cols3, .page2-lower, .split, .board-split, .box-pair';
  const inkBottom = (el) => {
    let b = -Infinity;
    const take = (r) => { if (r.width > 0 && r.height > 0 && r.bottom > b) b = r.bottom; };
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const range = document.createRange();
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      if (!n.nodeValue.trim()) continue;
      range.selectNodeContents(n);
      for (const r of range.getClientRects()) take(r);
    }
    el.querySelectorAll('img, svg, hr, td, th').forEach(e => take(e.getBoundingClientRect()));
    if (el.matches && el.matches('img, svg')) take(el.getBoundingClientRect());
    return b;
  };
  const colBottoms = (row) => {
    if (getComputedStyle(row).columnCount !== 'auto') {
      // CSS multi-column: approximate from line rects, same idea as the instrument.
      const cs = getComputedStyle(row), n = parseInt(cs.columnCount, 10) || 1;
      const box = row.getBoundingClientRect(), gap = parseFloat(cs.columnGap) || 0;
      const colW = (box.width - gap * (n - 1)) / n;
      const cols = new Array(n).fill(-Infinity);
      const w = document.createTreeWalker(row, NodeFilter.SHOW_TEXT);
      const range = document.createRange();
      for (let t = w.nextNode(); t; t = w.nextNode()) {
        if (!t.nodeValue.trim()) continue;
        range.selectNodeContents(t);
        for (const r of range.getClientRects()) {
          if (!(r.width > 0 && r.height > 0)) continue;
          const k = Math.max(0, Math.min(n - 1, Math.floor((r.left - box.left + gap / 2) / (colW + gap))));
          if (r.bottom > cols[k]) cols[k] = r.bottom;
        }
      }
      row.querySelectorAll('img, svg').forEach(e => {
        const r = e.getBoundingClientRect();
        if (!(r.width > 0 && r.height > 0)) return;
        const k = Math.max(0, Math.min(n - 1, Math.floor((r.left - box.left + gap / 2) / (colW + gap))));
        if (r.bottom > cols[k]) cols[k] = r.bottom;
      });
      return cols.filter(v => v > -Infinity);
    }
    return [...row.children].map(inkBottom).filter(v => v > -Infinity);
  };

  window.__gzFit = {
    listSlots() {
      return [...document.querySelectorAll("[data-art]")].map((el, i) => {
        remember(el);
        const page = el.closest(".page");
        const pages = [...document.querySelectorAll(".page")];
        const img = el.querySelector("img");
        return {
          id: el.getAttribute("data-art") || ("slot-" + i),
          kind: el.getAttribute("data-kind"),
          region: el.getAttribute("data-region"),
          flex: el.getAttribute("data-flex") !== "false",
          modes: el.getAttribute("data-modes") || "",
          src: el.getAttribute("data-src") || (img && img.getAttribute("src")) || "",
          wrap_ok: wrapOk(el),
          region_w_in: +regionWidthIn(el).toFixed(4),
          page: page ? pages.indexOf(page) + 1 : 0,
          px_w: img ? (img.naturalWidth || 0) : 0,
          px_h: img ? (img.naturalHeight || 0) : 0,
          min_w: parseFloat(el.getAttribute("data-min-w") || "") || null,
          lettered: el.getAttribute("data-lettered") === "true",
        };
      });
    },

    apply(id, cand) {
      const el = document.querySelector('[data-art="' + CSS.escape(id) + '"]');
      if (!el) throw new Error("no slot " + id);
      remember(el);
      const page = el.closest(".page");
      if (page) page.classList.add("fit");
      if (el.parentElement) el.parentElement.style.display = "flow-root";
      el.classList.remove("art--float", "art--gutter");
      el.style.display = "";
      el.style.visibility = "";
      el.style.cssFloat = "";
      if (cand.mode === "stack") {
        el.style.width = "100%";
        el.style.setProperty("--art-w", "100%");
        el.style.marginLeft = "0";
        el.style.marginRight = "0";
      } else if (cand.mode === "float") {
        el.classList.add("art--float");
        el.style.width = cand.width + "in";
        el.style.setProperty("--art-w", cand.width + "in");
        el.style.cssFloat = "left";
        el.style.marginRight = "9pt";
      } else if (cand.mode === "gutter") {
        el.classList.add("art--gutter");
        el.style.width = cand.width + "in";
        el.style.setProperty("--art-w", cand.width + "in");
        el.style.marginLeft = "0";
        el.style.marginRight = "auto";
      }
    },

    reset(id) {
      const el = document.querySelector('[data-art="' + CSS.escape(id) + '"]');
      if (el) reset(el);
    },

    collapse(id) {
      const el = document.querySelector('[data-art="' + CSS.escape(id) + '"]');
      if (!el) return;
      remember(el);
      el.style.display = "none";
    },

    measureSlot(id) {
      const el = document.querySelector('[data-art="' + CSS.escape(id) + '"]');
      const img = el && el.querySelector("img");
      const ir = img ? img.getBoundingClientRect() : { width: 0, height: 0 };
      const natW = img ? img.naturalWidth : 0;
      const natH = img ? img.naturalHeight : 0;
      const renderedAspect = ir.height ? ir.width / ir.height : 0;
      const naturalAspect = natH ? natW / natH : 0;
      const aspect_err = naturalAspect ? Math.abs(renderedAspect - naturalAspect) / naturalAspect : 0;
      const parent = el ? el.parentElement.getBoundingClientRect() : { width: 0 };
      const cs = el && el.parentElement ? getComputedStyle(el.parentElement) : null;
      const parentContent = parent.width - ((cs && (parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight))) || 0);
      const side_gutter_in = el && !el.classList.contains("art--float")
        ? inch(Math.max(0, parentContent - ir.width))
        : 0;
      const last = el ? lastWrappedBottom(el) : -Infinity;
      const fr = el ? el.getBoundingClientRect() : { bottom: 0 };
      const float_hole_in = (last > -Infinity) ? inch(fr.bottom - last) : 0;
      const interior_gap_in = el ? inch(Math.max(0, interiorGapPx(el))) : 0;
      const pageEl = el && el.closest(".page");
      const footer = pageEl && pageEl.querySelector(":scope > .footer");
      const ft = footer ? footer.getBoundingClientRect().top : 0;
      const cell = el ? el.parentElement : null;
      const cellInk = cell ? inkBottom(cell) : -Infinity;
      const region_gap_in = (ft && cellInk > -Infinity) ? +inch(ft - cellInk).toFixed(4) : null;
      const row = el && el.closest(SEL);
      let row_spread_in = null;
      if (row) {
        const bs = colBottoms(row);
        row_spread_in = bs.length > 1 ? +inch(Math.max(...bs) - Math.min(...bs)).toFixed(4) : 0;
      }
      const pageOverflowPx = pageEl
        ? Math.max(pageEl.scrollHeight - pageEl.clientHeight, pageEl.getBoundingClientRect().height - 10.1 * 96)
        : 0;
      return {
        img_w_in: +inch(ir.width).toFixed(4),
        img_h_in: +inch(ir.height).toFixed(4),
        region_w_in: el ? +regionWidthIn(el).toFixed(4) : 0,
        aspect_err: +aspect_err.toFixed(5),
        side_gutter_in: +side_gutter_in.toFixed(4),
        float_hole_in: +float_hole_in.toFixed(4),
        interior_gap_in: +interior_gap_in.toFixed(4),
        region_gap_in,
        row_spread_in,
        page_overflow_in: +inch(Math.max(pageOverflowPx, 0)).toFixed(4),
      };
    },
  };
  return true;
})()
