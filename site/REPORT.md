# En Garde Gazette site, v4 rebuild

## What I built
- **One desk engine** (`js/desk-engine.js`). A small 2D rigid-body world in desk-photo pixels (1520×1012; about 14 units = 1 cm). The whole wooden top is the play area, frame included: `bounds` = 36–1504 × 33–996, measured from the alpha of `desk.webp`.
  - The scene is a single CSS-transformed layer (one scale + translation, never rotated). Phones get a zoomed-in landscape desk; see the v5 section below.
  - Pointer coordinates go through the inverse transform. Hit testing is done in world space, not with DOM targets.
- **Gestures (shared by all objects):**
  - *Drag:* the grab point stays under the finger.
  - *Towing:* grab off-centre and the object swings round to trail the finger, like a sheet pushed with one fingertip. Grabbing near the centre only translates. This is the main way to rotate with a mouse.
  - *Other rotation:* mouse wheel over an object; two-finger twist on touch (both fingers on the object, or a second finger anywhere).
  - *Flick:* release velocity, linear and angular, comes from the last ~100 ms of movement.
  - *Tap:* a press of under 7 px and under 550 ms. Papers open the reader, the tin spins, a pencil gets a roll.
  - *Keyboard:* papers are focusable buttons. Enter opens; arrows move; `[` and `]` rotate.
- **Physics:**
  - Friction and spin decay per kind.
  - Desk-rim bounce uses proper corner impulses, so the tin caroms and spins off the edge.
  - Solid bodies collide with each other (box-vs-box SAT plus impulses): pencils bump the tin and each other, and a held object shoves others.
  - Papers aren't solid. They stack, and props sit on top of them.
  - The loop sleeps when nothing moves.
- **Papers:** our real page-1 images (the 1200 px thumbs, or full size on very dense screens).
  - 7 copies (5 on small screens), with random positions and orientations on every load and on "Re-mess".
  - The newest issue is always the top sheet, near the middle, roughly upright on screen (also when the desk is turned).
  - The whole outline is kept on the wood. A held paper lifts slightly and its shadow grows.
- **Tin:** the existing photo, with a collision box that matches the tin. It's heavy and slides well, with low spin friction: a tap gives it a 10–15 rad/s spin (about 3 turns), and a corner flick spins and slides it.
- **Pencils (yellow hex HB with brass ferrule and eraser; blue round copy-editor's pencil):**
  - Drawn on a canvas from a lighting model of the barrel cross-section. The hex faces and the stamp visibly turn over as the pencil rolls, and the sharpened end has a scalloped paint edge.
  - Rolling is a real degree of freedom: low drag across the length, high drag along it. The hex pencil clacks from flat to flat and settles on a face. The round one keeps rolling, so it's the one that ends up on the floor.
  - **Falling off:**
    - Once the centre of mass passes the rim, the pencil pivots about the rim line under gravity (rod-on-pivot dynamics) and keeps sliding out, gathering speed.
    - It leaves the rim when its inner end clears it, then free-falls in 3D and is removed at floor depth (1150 units down).
    - It's rendered with a hand-built `matrix3d`. The perspective (camera height 2300) is folded into that matrix, so no CSS `perspective` or `preserve-3d` is involved.
    - While tipping, the part still over the wood is drawn above the desk. The overhang is a clipped copy drawn *under* the desk photo, so the desk edge really hides it as it drops.
    - You can catch a tipping pencil by grabbing it. Reload or Re-mess brings fallen pencils back.
- **Reader** (`js/common.js`):
  - **No page-turn animation.** The next page is pre-decoded and swapped in instantly.
  - Zoom: wheel or trackpad pinch (cursor-anchored), touch pinch, +/−/Fit, double-click and keys, from 1× to 8×.
  - Pan by dragging (mouse or touch) when zoomed. At fit, swipe left or right to change page.
  - **Sharp zoom:** past the image's own resolution, the *visible* part of the page is re-rendered from the PDF with pdf.js, vendored in `vendor/pdfjs/` (Apache-2.0) and lazy-loaded on first deep zoom. Type stays crisp at any zoom, and the canvas never exceeds the viewport size.
  - Download PDF is still there, saved as `en-garde-gazette-N.pdf`. `?read=N` deep links still work.
- **Archive:** unchanged simple list, with Read (opens the reader) and PDF. CNAME and `.nojekyll` are untouched.

## Discarded from v3
- `js/pencil3d.js` and the OGL/WebGL CDN dependency. Its pencil lived on a separate full-screen canvas: it couldn't interleave with papers, wasn't part of the shared drag system, and fell as a visual-only effect.
- The canvas "cylinder curl" page turn and its paper-colour flap.
- The inner-panel clamp (objects now use the whole wooden top).
- The separate phone list view (the turned desk works on phones).
- CSS coffee-ring and ink-blot doodles.
- Animation-based placement via `left`/`top` percentages.

## Adding a future prop
Each prop kind is one registry entry. The engine supplies everything else.
```js
// a photographed object: transparent image + the box (image px) that is the object itself + its width on the desk
EGG.Desk.register('stapler', EGG.Desk.imageProp({
  src: 'assets/stapler.webp', imageWidth: 1200, imageHeight: 800, box: [40, 60, 1160, 760], width: 220,
  density: 4, slide: 900, spin: 6, restitution: 0.2, edge: 'contain',   // or 'fall' to let it go over the edge
  onTap: function (b, desk) { /* optional */ }
}));
desk.add('stapler', { x: 400, y: 300, a: 0.3, drop: 0.5 });   // e.g. in js/desk.js mess()
```
- **Options** (defaults are in `BASE` in `desk-engine.js`):
  - `layer`: `'paper'` or `'prop'`
  - `solid`, `edge` (`'contain'` or `'fall'`), `rod` (for long thin things that fall)
  - `density`, `slide`, `spin`, `restitution`, `tow`
  - `hitPad`, `lift`, `focusable`, `shadow` (a soft blurred box)
- **Hooks:**
  - `build(b, opts, desk)` (required): set `b.w`/`b.h` and fill `b.face`
  - `friction(b, dt)`: custom motion, as the pencils' rolling does
  - `draw(b, desk)`: custom-drawn faces, e.g. a canvas or a WebGL model rendered into a canvas
  - `onScale`, `onDrag`, `onTap`, `onGone`
- **Boundaries:** use `desk.play` (the visible part of the wood), not `desk.bounds`. The engine already keeps every registered kind inside it (placement clamping, bounces, tipping, re-layout), so a new prop needs no edge code of its own.
- **Rotation** is planar on the desk. 3D only happens when something goes over the edge, and then the engine animates `b.face` itself.

## Verified (headless Chrome, `python -m http.server`)
- Desktop 1440×900 and 1280×800, portrait phone 390×844 (touch), landscape phone 844×390. No console errors.
- Corner tow rotates a paper (−35° in one test drag). A tin tap spins it. The round pencil flicked across its length rolls off the bottom edge and is removed. The hex pencil slid hard along its length tips over the left edge and falls. A gentler slide stops overhanging the rim without falling.
- Touch (CDP synthetic events): one-finger drag, two-finger twist, tap opens the reader, pinch zoom, pan. The pdf.js sharp overlay rendered.
- Reader: `?read=1`, arrow key to page 2, Escape closes. Re-mess restores all 10 objects.

## Remaining issues
- No real GPU, touch hardware, Safari or Firefox testing; touch was synthetic.
- Pencils are drawn top-down; the stamp and facets update while rolling. During a fall the canvas is frozen and only billboards about its own axis, which is fine at fall speed.
- A pencil rolling off parallel to an edge disappears in roughly 0.1–0.2 s. That's physically right for a camera above the desk, but quick.
- Papers don't drag the props lying on them.
- Shadows are soft boxes, not true silhouettes (the open-lid tin is close enough).
- Collisions are box-shaped. A held object pushing a body hard against the rim can overlap it briefly.
- Native browser pinch-zoom is off on the desk and inside the reader (`touch-action: none`); the custom gestures replace it.
- pdf.js needs ES-module dynamic `import()`. Without it the reader still works with images only, capped at image sharpness.
- Nothing is committed. `docs/` hasn't been synced.

## Which issues land on the desk (Frank, 2026-10-18)
`js/pick-issues.js` (`EGG.pickDeskIssues`): newest always on top (centred, near-upright); the next 2 issues (1 on small screens) always in the pile; remaining slots of 7 (5 small) sampled uniformly without replacement from all older issues; duplicates only when there are fewer issues than slots (older first, never a second newest on top). Tests: `node site/tests/pick-issues.test.js`.

## v5 mobile: landscape zoom + play area (2026-10-19)
- **No more 90° turn.** The desk is always landscape. `js/desk-view.js` (`EGG.deskView`, pure) maps the fixed world (desk.webp 1520×1012, `bounds` unchanged) to the screen with one scale plus a translation.
  - Wide screens fit the whole wood exactly as before (1440×900 and the 780×360 landscape phone are unchanged).
  - Portrait screens zoom until about 820 world units span the screen width. A small-screen paper (360 units) comes out at ~158 px on a 360 px phone, ~173 px on 393 and ~181 px on 412. The desk is centred and the left and right sides are cropped.
  - The zoom is capped so the whole wood height plus 40 units above and below always fits, so the real top and bottom rims are always on screen.
  - The zoom blends in between aspect 1.0 and 0.75, so tablets get part of it and a resize across square doesn't jump.
- **Play area.** `desk.play = {x0, y0, x1, y1, edges: {left, right, top, bottom}}` is the visible part of the wood, recomputed on every layout. Each edge is either:
  - `'rim'`: the real wood edge is on screen; `play` equals `bounds` on that side.
  - `'wall'`: the screen crops the wood there; `play` sits 6 screen px inside the screen edge.
  - When the whole wood is visible, `play == bounds` and every edge is a rim, so desktop behaves as before.
- **All boundary logic uses `desk.play`:**
  - placement in `mess()`
  - `constrain()` for every kind
  - rim bounces
  - tipping, including a pencil sliding along a rim while it tips: it can't pass a wall
- **Walls are invisible.** Everything bounces off them or stops there; nothing tips over them. Real rims work as before.
- **Re-layout.** On rotate, resize or header wrap (`resize` + `ResizeObserver`), every body that isn't falling is re-constrained into the new play area, so nothing is stranded off screen.
- **Behaviour change:** on phones, pencils only roll off the top and bottom edges. The side edges are walls.
- **Cropped edges fade.** A soft gradient covers each cropped side (`.desk-fade.crop-l` / `.crop-r`, `pointer-events: none`), so the crop reads as intentional.
- **`upright()` is 0 and the light is constant** (from the screen's upper left). `rot`, `screenVec` and `upright` remain as trivial API.
- **Placement (`js/desk.js`):** the top sheet's spot is picked first, and the others spread out around it.
  - On small screens the spread box is inset by half a paper.
  - A repair pass moves any lower sheet with less than 15% showing to the best of a few other spots.
  - The `pickDeskIssues` rule is unchanged: 5 papers on small screens, 7 on desktop.
- **Tests:** `node site/tests/desk-view.test.js` checks:
  - fit is unchanged on wide screens, with `play == bounds`;
  - phones get walls on the sides, rims on screen, and the paper size range;
  - a short window caps the zoom.

  `pick-issues.test.js` still passes.
- **Verified (headless Chromium):**
  - At 360×780, 393×852, 412×915, 780×360 and 1440×900, every paper was fully on screen and the top sheet ≥94% exposed after 30 Re-messes each. The least-exposed lower sheet was 10% (phone) to 54% (desktop), counting props lying on top. No console errors.
  - On the phone, sideways pencil and tin flicks stay on screen, and a downward pencil flick falls off the bottom rim. On desktop, pencils still fall off the left and right rims.
  - Rotating 780×360 → 360×780 → 412×915 → back, with objects parked at the far ends of the wood, leaves everything on screen.
  - Keyboard arrows stop at the wall. A touch tap opens the reader, and drag works.

