# Motion build: one camera world in HyperFrames

Worked example to copy from: `example/compositions/reel.html` ("How an AI agent works", 34 s). It holds every pattern below in working form. Read it before writing a new reel.

## Contents
1. Project setup
2. File structure
3. Style frame first
4. Seek-safe timeline helper
5. Camera
6. Glass, layering and depth
7. Headlines and captions
8. Cue timing
9. Snapshot, check, preview, render
10. Errors already met and their fixes

## 1. Project setup

- Start at the `hyperframes` skill (its intent step is mandatory for a fresh video), but route to **general-video, `flow: companion`**. A scene-per-frame pipeline can't hold one continuous camera world.
- `npx hyperframes@latest init "<slug>" --non-interactive --example=blank --skill=general-video` pins the CLI version in `package.json`; use that same version for every later command (`npx --yes hyperframes@<pin> …`). Write `BRIEF.md` right after init.
- Fonts: download the fonts named in `references/brand.md` from Google Fonts as woff2 into `public/fonts/` (fetch the `https://fonts.googleapis.com/css2?family=…` CSS and download the woff2 files it lists). The example expects `archivo-black-400.woff2`, `poppins-400.woff2`, `poppins-500.woff2`, `poppins-700.woff2` and `eb-garamond-400-italic.woff2`.
- Real app logos: `npx hyperframes media-use resolve --type logo --entity <name> --intent "<Name> logo" --project .`, then copy to `public/logos/<name>.svg`. Look at every logo before use (a wrong entity or a monochrome mark happens). Logos stay in their own colours, never recoloured. A black mark (OpenAI, GitHub) needs a light chip behind it on a dark ground.
- Write `frame.md` (the design spec for this reel) from `references/brand.md`: colours, glass, type ramp, safe zones.
- Skip registry "liquid glass" blocks that depend on experimental browser APIs. Hand-rolled CSS glass (below) renders reliably.

## 2. File structure

- `index.html` (host): one sub-composition clip for the whole reel, plus `<audio id="vo" src="public/audio/voice.wav">` and `<audio id="sfx" src="public/audio/sfx.wav" data-volume="0.6">`, plus an empty paused `main` timeline. Every `<audio>` needs an `id` or it plays silent.
- `compositions/reel.html`: a `<template>` wrapping style + `#root` + script. Style the root by `#root`. Timeline key = host `data-composition-id` = `reel`.
- Asset URLs inside the sub-composition are relative to the **project root** (`public/fonts/…`, `public/logos/…`), because its content is cloned into `index.html`.
- One long sub-composition triggers a `composition_file_too_large` lint warning; accept it. Splitting it would break the single camera.

## 3. Style frame first

Build the signature beat (the moment that carries the idea) as a static state of the real composition, snapshot it with `npx hyperframes snapshot --at <t>`, and send that PNG for the user's OK before animating anything. It catches broken headlines and proves the glass renders in the real renderer.

## 4. Seek-safe timeline helper

HyperFrames seeks frame by frame in any order, so every tween must be a `fromTo` whose from-state is the previous to-state. This helper does the bookkeeping. Add tweens per element in time order:

```js
var tl = gsap.timeline({ paused: true });
var ST = new Map();
function st(el) { if (!ST.has(el)) ST.set(el, {}); return ST.get(el); }
function I(el, props) { Object.assign(st(el), props); tl.set(el, Object.assign({}, props), 0); }      // initial state at t=0
function G(el, to, at, dur, ease) {                                                                     // tween from last known state
  var s = st(el), from = {}; for (var k in to) from[k] = s[k];
  tl.fromTo(el, from, Object.assign({}, to, { duration: dur, ease: ease || "power2.inOut", immediateRender: false }), at);
  Object.assign(s, to);
}
// … build everything …
window.__timelines["reel"] = tl;   // register last, after all tweens exist
```

Initialise every animated property with `I()` before its first `G()`. **Also put every t=0 state in the CSS**: timeline sets at t=0 are not applied to the very first rendered frame, so frame 0 can show the end card. SVG stroke draws use `tl.fromTo(path, {attr:{"stroke-dashoffset":len}}, {attr:{"stroke-dashoffset":0}, …, immediateRender:true}, at)`. Moving a dot along a path: precompute ~100 points with `getPointAtLength` at build time, then drive them from one `fromTo` on a proxy object with an `onUpdate`. No `Math.random`; use index-derived offsets.

## 5. Camera

Everything in the world sits in `#cam` (`transform-origin: 0 0`). To put world point (px,py) at screen point (sx,sy) at scale S:

```js
function F(px, py, S, sx, sy) { return { x: sx - px * S, y: sy - py * S, scale: S }; }
G(cam, F(232, 700, 1.7, 540, 880), 3.62, 0.72, "power3.inOut");   // glide to one card
```

Moves that read well: a slow push during the hook (1.0 → 1.05), focus glides of 0.6 to 0.7 s (`power3.inOut`) between stations, a pull-back to show the whole system, a slow push toward the payoff. Before a push that moves the world upward, fade out world elements that would slide under the headline. Under a 1.3x push, keep side elements within about x 175 to 900 or they clip at the frame edge.

## 6. Glass, layering and depth

```css
.glass {
  background: linear-gradient(150deg, rgba(244,239,226,0.27) 0%, rgba(244,239,226,0.09) 55%, rgba(244,239,226,0.15) 100%);
  -webkit-backdrop-filter: blur(22px) saturate(135%); backdrop-filter: blur(22px) saturate(135%);
  border: 1.5px solid rgba(244,239,226,0.36);
  box-shadow: inset 1.5px 1.5px 0 rgba(255,255,255,0.40), inset -1px -1px 0 rgba(4,13,9,0.25), 0 34px 70px rgba(4,13,9,0.60);
}
```

- Glass needs something behind it to frost: radial blooms, a faint grid, and grain. Never use full-screen linear gradients on dark grounds (they band in H.264).
- **Give every world layer an explicit `z-index`.** Elements with a positive z-index paint above `z-index:auto` ones regardless of DOM order, so a cursor or a dragged item can vanish behind cards. Example ladder: lines 0 · hubs 1 · connectors 2 · card slots 3 · avatars 5 · chips/cards 6 · glow 7 · drag ghost 8 · cursor 9.
- `opacity` below 1, `filter`, `mask` or `clip-path` on an **ancestor** of a glass element creates a backdrop root and flattens the frost. Fade or blur the glass element itself, never its wrapper. Fading the whole world for the outro is the one acceptable exception (it lasts under half a second).
- Depth of field is meaning: blur and dim what isn't in focus (`filter: blur(5px)`, `opacity: 0.42`), sharpen what is.
- SVG lines with `stroke-linecap: round` and a full dash offset still paint a dot at the start. Keep a not-yet-drawn line layer at `opacity: 0` until its draw begins.
- Cards whose content arrives in steps (a DM card) reveal with a `clipPath: inset(… round 40px)` tween, not with empty reserved space.

## 7. Headlines and captions

- **One headline per beat**, screen space, top-left at (64, 250), ending above ~y 480: one caps line (88 to 120 px) plus one italic phrase (90 to 160 px). Give the italic line `margin-top: 16px; line-height: 1.0`, or `check` flags `content_overlap`. In: y 36 → 0, opacity, blur 10 → 0, 0.42 s `power3.out`. Out: 0.26 s before the next. Keep the words short and true to the voice line.
- **Captions:** glass pill at top 1376 px, 600-weight sans at 50 px, at most two lines of 3 to 5 words. Build pages as arrays of word indices; highlight the spoken word with the chip colour. Only the CTA keyword gets the accent colour. Pages switch on the first word's start time.
- **Safe zones** (Instagram UI): foreground inside x 64 to 960, y 250 to 1270; captions y ~1376 to 1560; nothing important below that.
- Small grey text on glass fails contrast; use `rgb(198,208,196)` (or your equivalent) for 20 px labels.
- `check` counts text hidden by a mask as overlapping; hard-cut `visibility` around each headline's on-screen window if needed.

## 8. Cue timing

Key every motion cue to the voice. Build `W` from `words.json` (inject the JSON into the script) and write cues as `T(i)` = `W[i].s` (in the example, the Claude logo lands on `T(17)`, the word "Claude"). A regenerated voice then re-times the whole animation. Derive the `sfx_synth.py` cue times the same way.

## 9. Snapshot, check, preview, render

- Snapshot the key moment of every beat in one call: `npx hyperframes snapshot --at 0.9,4.6,9.6,…`. Read the contact sheet, then crop and zoom anything small (a cursor, a caption) before believing it.
- `npx hyperframes check` must pass (lint, runtime, layout, motion, contrast). Camera and bloom overflow show up as info; that's expected.
- Preview for the user: `npx hyperframes preview --background`, read the URL from its log, open it in a browser. Stop it later with `npx hyperframes preview --stop`.
- Render only on the user's OK: `npx hyperframes render -o renders/<slug>.mp4` (a 35 s reel takes a minute or two). Verify with `ffprobe` (1080x1920, 30 fps, H.264 + AAC), `ffmpeg -af ebur128` (about -13 to -14 LUFS), and frames pulled from the MP4 itself, frame 0 included (`ffmpeg -vf "select=eq(n\,0)"`).

## 10. Errors already met and their fixes

| Symptom | Cause | Fix |
|---|---|---|
| Frame 0 of the MP4 shows the end card | t=0 timeline sets aren't applied to the first frame | put every t=0 state in CSS too; check frame 0 |
| Cursor and drag ghost invisible | slots had a positive z-index | explicit z-index ladder (section 6) |
| Small dots under cards before lines draw | round line caps on undrawn dashes | hide the SVG layer until the draw starts |
| `content_overlap` on two-line headlines | italic glyph box overlapping the caps line | italic `margin-top: 16px; line-height: 1.0` |
| Contrast 3.8:1 on card subtitles | grey on glass | `rgb(198,208,196)` |
| Items under the headline after a camera push | the world moved up | fade them out before the push |
| A node sliding under the headline while the camera is away | focus far from it | fade it out while away, back in on the pull-back |
| End card showing under a fading DM card | overlapping fades | start the DM fade 0.3 s before the end card |
| Three accent colours on the CTA frame | send button + headline + caption chip | send button in ink; accent only on the keyword |
| Empty block inside a card | space reserved for later rows | clip-path progressive reveal |
| Exact-string edits on tags fail while the Studio preview runs | the preview writes `data-hf-id` attributes into the source | match tags with a regex that allows extra attributes |
