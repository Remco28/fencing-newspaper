# Site revision report

## What changed
- **Desk bounds (`js/desk.js`)**: papers and the paperclip tin are clamped so their *rotated bounding box* stays inside the inner wood panel of `desk.webp` (`PANEL` = 8.4–93.4 % × 10.8–88.6 % of the stage, measured from the 1520×1012 image). The clamp applies at initial placement and during drag. Papers stay 2D and the same size, and the `page-N.webp` / `page-N-1200.webp` srcset is untouched.
- **3D pencils (`js/pencil3d.js`, new; SVG pencil code and `.pencil` CSS removed)**:
  - One fixed, click-through WebGL canvas. The camera is set so the desk plane maps 1:1 to CSS px, so pencils line up with the photo.
  - Geometry is a lathe: hex barrel (6.5 mm flat-to-flat, 190.5 mm long, about 29:1), sharpened cone with scalloped paint, graphite tip, brass ferrule with ridges, pink eraser. The barrel texture has stamped text and a dipped end.
  - Roll angle is real: dragging or sliding perpendicular to the axis rolls the hex barrel. Sliding along the axis grips quickly. A soft contact shadow follows the pencil.
  - Flick or drag. Dragging is clamped to the desk edge; a flick or a small nudge near the rim tips it over.
  - Past a desk edge it falls with gravity along -z, tumbles about the edge axis, darkens into the backdrop, and is removed. **Re-mess only re-scatters survivors** (checked: after a pencil fell and Re-mess was clicked, 1 pencil remained).
  - Pencil length is 25 % of desk width, a little longer than a letter page is wide.
  - Test hook: `window.__pencils3d` has `list` (alive), `all`, `fallen`, `ready`, `whenReady`, `flick(i,vx,vy)`, `setPose(i,x,y,thDeg)`, `project(i)` and `render()`.
  - Coffee ring and ink blot are unchanged (2D).
- **Tin**: still the 2D photo. It now twists slightly when pushed sideways. No thumbtack references exist.
- **Reader (`js/common.js`, `css/style.css`)**:
  - Wheel and trackpad-pinch zoom is continuous (1×–5×) and centred on the cursor. +/−/Fit/dblclick/keys use the same anchored zoom.
  - Pointer-based pan for mouse, touch and pen when zoomed (`touch-action: none` on the view).
  - Two-finger pinch is implemented explicitly around the midpoint, because it replaces browser-native pinch inside the reader.
  - New page turn (below).

## 3D library: OGL (not three.js)
- OGL is a thin WebGL2 wrapper, about 40 kB gzipped as one jsDelivr `+esm` bundle. three.js is roughly 150 kB gzipped or more.
- One pencil needs a few meshes, one small shader pair, a texture and a perspective camera. Physics is hand-written, so none of three's scene graph, materials or loaders would be used.
- The cost is writing the ~20-line lighting shader and the lathe geometry by hand. If you want PBR, shadows or loading a modelled `.glb`, three.js is the better tool.
- The library is lazy-loaded (dynamic `import()`) on the first desk build only. Phones and the mobile list never download it.
- If the CDN or WebGL is unavailable, the desk still works without pencils (a console warning is logged).

## Page turn: custom canvas "cylinder curl"
- The outgoing sheet (or the incoming one when going back) is drawn as 2 px vertical strips wrapped around a small cylinder that rolls across the page.
- The free edge lifts, curls over, and shows a paper-coloured underside with faint show-through. It has per-strip shading and a cast shadow on the page below. About 720 ms, eased. Back-turn is the same render in reverse.
- It is skipped while zoomed, and under `prefers-reduced-motion`.
- Alternatives considered:
  - **StPageFlip (`page-flip`)** is a good book-spread engine, but it owns layout and sizing and fights the custom zoom/pan viewer.
  - **turn.js** needs jQuery and has licensing friction.

## Tin recommendation
- Keep it 2D with the nudge-twist. A 3D rebuild isn't worth it: it's a static photographed prop with baked lighting, and a 3D tin would add little at this size.
- If you ever want it, a simple extruded rounded box built the same way as the pencil, with the photo as lid and base textures, would be enough.

## Known remaining issues
- The pencil canvas always draws **above** the DOM papers and tin (it cannot interleave), so pencils always lie on top of the pile. The old SVG pencils could be buried under a later-dragged paper.
- Pencils can lie on the outer frame; only papers and the tin are limited to the inner panel.
- Falling is visual only: the pencil is never hidden under the desk. Frame time is capped, so on a slow GPU the fall plays in slow motion.
- Tested in headless Chromium with SwiftShader only (no physical GPU, no touch hardware, no Safari/Firefox). Touch pan and pinch were checked with synthetic CDP events.
- Hex rolling is smooth; there is no "clack" or height bob from the barrel corners.
- Native browser pinch-zoom is disabled inside the reader (`touch-action: none`), replaced by the custom pinch.
- Nothing has been committed.
