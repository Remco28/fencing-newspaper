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
      // Floats need a BFC on their parent so wrapping prose closes around them.
      // Never set that on .page itself: the page is a flex column that pins the
      // footer (STYLE-GUIDE §13). display:flow-root overrides flex, shrink-wraps
      // the page in print, and leaves blank paper below the footer.
      if (el.parentElement && !el.parentElement.classList.contains("page")) {
        el.parentElement.style.display = "flow-root";
      }
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
      // When the art is a direct child of .page, inkBottom(page) would include
      // the footer itself and look like a ~0.16in overlap (footer height).
      let cellInk = -Infinity;
      if (cell) {
        if (cell.classList.contains("page")) {
          for (const kid of cell.children) {
            if (kid.classList.contains("footer")) continue;
            const b = inkBottom(kid);
            if (b > cellInk) cellInk = b;
          }
        } else {
          cellInk = inkBottom(cell);
        }
      }
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
      // Space below the footer to the expected 10.1in content-box bottom, measured
      // from the top of .page — not from the element's used height, which would
      // hide a shrink-wrapped page.
      let footer_drop_in = null;
      if (pageEl && footer) {
        const pr = pageEl.getBoundingClientRect();
        const fb = footer.getBoundingClientRect();
        footer_drop_in = +inch((pr.top + 10.1 * 96) - fb.bottom).toFixed(4);
      }
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
        footer_drop_in,
      };
    },

    // Row-balance helpers (STYLE-GUIDE §13). Stamp ids, list movable shorts,
    // move a short box into a shorter column/rail, unwrap a one-child split,
    // and retarget an art slot at a prepared crop.
    stampBalanceIds() {
      let n = 0, c = 0;
      const SEL = '[data-balance], .cols3, .page2-lower, .split, .board-split, .box-pair';
      const stamp = (el) => { el.setAttribute("data-bal-id", "i" + (++n)); };
      document.querySelectorAll(".page").forEach((page, pi) => {
        page.querySelectorAll(SEL).forEach((row) => {
          if (row.closest(".page") !== page) return;
          [...row.children].forEach((col) => {
            col.setAttribute("data-bal-col", "p" + (pi + 1) + "c" + (++c));
            const walk = (el) => {
              [...el.children].forEach((kid) => {
                if (kid.matches && kid.matches(SEL)) return; // nested row stamps itself
                if (kid.matches && kid.matches(".masthead, .dateline, .footer")) return;
                if (kid.matches && kid.matches("figure.art, .art")) { stamp(kid); return; }
                if (kid.matches && kid.matches(".lead, .rail-block, .slot-a, .slot-b, .box")) {
                  stamp(kid);
                  kid.querySelectorAll("figure.art, .art").forEach(stamp);
                  return;
                }
                stamp(kid);
                walk(kid);
              });
            };
            walk(col);
          });
        });
      });
      return { items: n, cols: c };
    },

    listMovable() {
      this.stampBalanceIds();
      const SEL = '[data-balance], .cols3, .page2-lower, .split, .board-split, .box-pair';
      const inch = (px) => +(px / 96).toFixed(4);
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
        el.querySelectorAll("img, svg, hr, td, th").forEach(e => take(e.getBoundingClientRect()));
        return b;
      };
      const isMovable = (el) => {
        if (el.matches(".lead, .masthead, .dateline, .footer, .w3")) return false;
        if (el.matches(".box, .rail-block, .slot-a, .slot-b")) return true;
        return false;
      };
      const itemKind = (el) => {
        if (el.matches("figure, .art")) return "art";
        if (el.matches(".lead")) return "lead";
        if (el.matches(".box")) return "box";
        if (el.matches(".rail-block, .slot-a, .slot-b")) return "short";
        return "other";
      };
      const itemLabel = (el) => {
        const h = el.querySelector("h1, h2, h3, h4, .board-head, .boxtitle, .rail-title");
        if (h && h.textContent.trim()) return h.textContent.trim().replace(/\s+/g, " ").slice(0, 80);
        return (el.getAttribute("data-art") || el.className || el.tagName).toString().split(" ")[0];
      };
      const pages = [...document.querySelectorAll(".page")].map((page, pi) => {
        const rows = [...page.querySelectorAll(SEL)].filter(r => r.closest(".page") === page).map((row, ri) => {
          const box = row.getBoundingClientRect();
          const rcs = getComputedStyle(row);
          const rowBottom = box.bottom - (parseFloat(rcs.paddingBottom) || 0);
          const cols = [...row.children].map((col) => {
            const ink = inkBottom(col);
            const items = [...col.querySelectorAll("[data-bal-id]")].map((el) => {
              const r = el.getBoundingClientRect();
              return {
                id: el.getAttribute("data-bal-id"),
                kind: itemKind(el),
                movable: isMovable(el),
                label: itemLabel(el),
                art_id: el.getAttribute("data-art") || (el.querySelector("[data-art]") && el.querySelector("[data-art]").getAttribute("data-art")) || "",
                photo: !!(el.matches("figure.art, .art") || el.querySelector("figure.art, .art")),
                lettered: el.getAttribute("data-lettered") === "true" || !!(el.querySelector && el.querySelector("[data-lettered='true']")),
                h_in: inch(r.height),
                src: (el.matches("img") ? el.getAttribute("src") : (el.querySelector && el.querySelector("img") && el.querySelector("img").getAttribute("src"))) || "",
              };
            });
            return {
              id: col.getAttribute("data-bal-col"),
              gap_in: inch(rowBottom - ink),
              h_in: inch(Math.max(ink - col.getBoundingClientRect().top, 0)),
              items,
            };
          });
          return { kind: (row.getAttribute("data-balance") || (row.className || "").split(" ")[0]), cols };
        });
        return { page: pi + 1, rows };
      });
      return { pages };
    },

    moveItem(itemId, destColId) {
      const el = document.querySelector('[data-bal-id="' + CSS.escape(itemId) + '"]');
      const dest = document.querySelector('[data-bal-col="' + CSS.escape(destColId) + '"]');
      if (!el || !dest) return { ok: false, reason: "missing item or dest" };
      dest.appendChild(el);
      this.unwrapLonelySplits();
      return { ok: true, item: itemId, dest: destColId };
    },

        unwrapLonelySplits() {
      const SEL = ".split, .board-split, .box-pair, [data-balance='split']";
      let n = 0;
      document.querySelectorAll(SEL).forEach((row) => {
        const isEmpty = (d) => !d.children.length && !(d.textContent || "").trim();
        const empties = [...row.children].filter(isEmpty);
        const remaining = [...row.children].filter((d) => !isEmpty(d));
        // Lock art widths while siblings still define the column width.
        // Removing an empty half first would let a flex:1 photo expand to
        // the full row, then overflow after unwrap.
        if (remaining.length === 1) {
          remaining[0].querySelectorAll("figure.art, .art").forEach((art) => {
            const w = art.getBoundingClientRect().width / 96;
            if (w > 0) {
              art.style.width = w.toFixed(4) + "in";
              art.style.maxWidth = w.toFixed(4) + "in";
              art.style.setProperty("--art-w", w.toFixed(4) + "in");
            }
          });
          if (remaining[0].matches && remaining[0].matches("figure.art, .art")) {
            const art = remaining[0];
            const w = art.getBoundingClientRect().width / 96;
            if (w > 0) {
              art.style.width = w.toFixed(4) + "in";
              art.style.maxWidth = w.toFixed(4) + "in";
              art.style.setProperty("--art-w", w.toFixed(4) + "in");
            }
          }
        }
        empties.forEach((d) => d.remove());
        const kids = [...row.children];
        if (kids.length !== 1) return;
        const parent = row.parentElement;
        if (!parent) return;
        let keep = kids[0];
        while (keep.children.length === 1 &&
               !keep.matches("figure, .art, .box, .lead, .rail-block, .slot-a, .slot-b, .w3")) {
          keep = keep.children[0];
        }
        parent.insertBefore(keep, row);
        row.remove();
        n++;
      });
      return n;
    },

    wrapInSplit(itemIds, flexes) {
      const els = (itemIds || []).map((id) =>
        document.querySelector('[data-bal-id="' + CSS.escape(id) + '"]'));
      if (!els.length || els.some((e) => !e)) return { ok: false, reason: "missing item" };
      flexes = flexes || els.map(() => 1);
      const split = document.createElement("div");
      split.className = "split";
      split.setAttribute("data-balance", "split");
      const lead = els[0].closest(".lead");
      if (lead && lead.parentElement) {
        lead.parentElement.insertBefore(split, lead.nextSibling);
      } else {
        els[0].parentElement.insertBefore(split, els[0]);
      }
      els.forEach((el, i) => {
        const artId = el.getAttribute("data-art");
        if (artId) this.clearArtMode(artId);
        const cell = document.createElement("div");
        cell.style.flex = String(flexes[i] || 1);
        split.appendChild(cell);
        cell.appendChild(el);
      });
      return { ok: true, ids: itemIds };
    },

    clearArtMode(id) {
      if (!id) return { ok: false };
      const el = document.querySelector('[data-art="' + CSS.escape(id) + '"]');
      if (!el) return { ok: false };
      el.classList.remove("art--float", "art--gutter");
      el.style.cssFloat = "";
      el.style.display = "";
      el.style.width = "100%";
      el.style.setProperty("--art-w", "100%");
      el.style.marginLeft = "0";
      el.style.marginRight = "0";
      return { ok: true };
    },

    floatIntoLead(id, widthIn) {
      const el = document.querySelector('[data-art="' + CSS.escape(id) + '"]');
      if (!el) return { ok: false, reason: "no slot " + id };
      const col = el.closest(".c, .span2") || el.parentElement;
      const lead = col && col.querySelector(".lead");
      if (!lead) return { ok: false, reason: "no lead in column" };
      const existing = lead.querySelector("figure.art, .art");
      if (existing && existing !== el) existing.after(el);
      else {
        const hook = lead.querySelector("p.dek, p, h1, h2");
        if (hook && hook.nextSibling) hook.parentNode.insertBefore(el, hook.nextSibling);
        else lead.appendChild(el);
      }
      el.classList.add("art--float");
      el.classList.remove("art--gutter");
      el.style.cssFloat = "left";
      el.style.display = "";
      const w = widthIn || (el.getBoundingClientRect().width / 96);
      el.style.width = w + "in";
      el.style.maxWidth = w + "in";
      el.style.setProperty("--art-w", w + "in");
      el.style.marginLeft = "0";
      if (el.parentElement && !el.parentElement.classList.contains("page")) {
        el.parentElement.style.display = "flow-root";
      }
      return { ok: true, id, width: w };
    },

    setArtSrc(id, src, creditSuffix) {
      const el = document.querySelector('[data-art="' + CSS.escape(id) + '"]');
      if (!el) return { ok: false, reason: "no slot " + id };
      const img = el.querySelector("img") || (el.tagName === "IMG" ? el : null);
      if (!img) return { ok: false, reason: "no img" };
      img.setAttribute("src", src);
      img.setAttribute("data-src", src);
      if (creditSuffix) {
        const cred = el.querySelector(".credit, p.credit") ||
          (el.parentElement && el.parentElement.querySelector(".credit"));
        if (cred && cred.textContent.indexOf(creditSuffix) < 0) {
          cred.textContent = cred.textContent.replace(/\.?\s*$/, "") + " " + creditSuffix;
        }
      }
      return { ok: true, id, src };
    },

    setArtWidth(id, widthIn) {
      const el = document.querySelector('[data-art="' + CSS.escape(id) + '"]');
      if (!el) return { ok: false };
      if (widthIn) {
        el.style.width = widthIn + "in";
        el.style.setProperty("--art-w", widthIn + "in");
      }
      return { ok: true };
    },
  };
  return true;
})()
