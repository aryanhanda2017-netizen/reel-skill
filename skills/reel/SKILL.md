---
name: reel
description: Make a faceless short-form video (Instagram Reel, TikTok, YouTube Short) end to end, in a premium motion style (9:16, one continuous camera world, frosted-glass cards with real app logos, kinetic headlines, glass captions with the spoken word highlighted, a measured AI voiceover, subtle sound design), always delivered with its caption and a 9:16 cover. Covers the script and copy passes, the voice pipeline, the HyperFrames build and the review gates where the user signs off. Use whenever the user asks for a reel, a short, an explainer video, a voiceover video, "a video like the last one", or wants to turn a topic, note, transcript or post into a short video, even if they don't say "reel". Also use for re-voicing, re-cutting, captioning or making a cover for an existing reel. Not for editing real talking-head footage, long-form video or text-only posts.
---

# Reel

Turns one idea into a finished short video the user can post. One reel is always three files: **the video, the caption and the cover.** A reel isn't delivered until all three exist, so never ask whether they want them.

Nothing is ever posted, uploaded or sent anywhere. The user posts it themselves.

Worked example: `example/` is a complete 34 s reel ("How an AI agent works"). Read `example/compositions/reel.html` before writing a new one; every pattern in `references/motion-build.md` is in it, working.

## Before the first reel: make it theirs

Read `references/brand.md`. If it still has `TODO` in it, run the setup interview first: ask the user, in one batch, for
- their name or handle (for the end card and the DM card),
- who the reels are for and what they help with,
- the call to action: the comment keyword and what they send people who comment it,
- their colours (or "keep the example palette") and fonts (or keep the defaults),
- their voice provider (see `references/voice.md`) and, if they have one, a preferred voice,
- words or claims they never want used.

Write the answers into `references/brand.md` and confirm. Every later reel reads it. Never invent their offer, numbers, clients or results: if something is unknown, ask.

## The order, and why

Each stage feeds the next, and people change their minds once they hear the voice or see motion. So each artefact gets the user's OK before the next is built on it. Show things early.

1. **Script.** Wait for their OK.
2. **Style frame.** One still of the signature beat, from the real renderer. Wait for their OK.
3. **Voice.** The mastered voice file. Wait for their OK.
4. **Full build.** Snapshots, then `check` passes, then the Studio preview. Wait for their OK.
5. **Render, caption and cover, delivered together.**

If the user says "go" or "don't stop to ask", build straight through, but still deliver all three files.

## 1. Script

Inputs vary: a topic, a transcript, a note, "one like the last one" plus a new topic. If the audience or angle is unclear, ask one question rather than guess.

**Shape:**
1. Hook: the problem in the viewer's words, stop-scroll in the first 3 s.
2. Make it concrete: real apps or objects the viewer recognises.
3. Why the obvious fix fails (or the one idea that explains it).
4. The turn: what to do.
5. The payoff in concrete terms ("anyone can pull up an invoice without asking you"), not "productivity".
6. CTA: one ask, and name the payoff ("Comment AGENT and I'll send you the guide"). Use the keyword and payoff from `brand.md`.

**Length:** 75 to 100 spoken words, about 28 to 33 s.

**Copy passes**, in this order (use the skills if installed, otherwise do the pass yourself):
1. `social`: hook and structure.
2. `humanizer`: spoken delivery. Contractions, connective words, varied sentence length, no lists of verbless fragments, no "it's not X, it's Y", no colon reveals.
3. `copywriting`: the persuasive and benefit lines.
4. `humanizer` again.

Show what each pass changed in a small before/after table.

**Truth:** source material is input, not a claim. Only say what the user really does. No invented numbers. On-screen data (invoice numbers, amounts, names) stays illustrative and generic. Default copy rules: no em dashes, one ask, no pricing unless the user gives it, nothing from the banned list in `brand.md`.

## 2. Look and the style frame

- **Real logos on glass cards.** Official app marks (HyperFrames `media-use`), in their own colours, never recoloured. Frosted glass over a dark ground with soft colour blooms.
- **One continuous camera world, not slides.** The camera glides between stations, pulls back to reveal the system, pushes in on the payoff. Depth of field carries meaning: blur what isn't in focus.
- **Story objects that act.** A cursor dragging a value between apps, a loop that lights up, cards flying into a hub, a comment box typing the keyword, a DM arriving.
- **Type:** one heavy caps headline line plus one italic phrase per beat. Clean sans for captions and UI. One accent colour per frame (the "AI" glow and the CTA keyword).
- **Glass caption pill** with the spoken word highlighted.
- **Sound design yes, music no.** Music gets added in the app.

Build the signature beat as a still in the real composition and send the snapshot. How: `references/motion-build.md`.

## 3. Voice

Follow `references/voice.md`. In short: one continuous take of the whole script (never line by line), three takes, pick by `scripts/prosody.py`, verify the words with Whisper, re-time the sentence gaps with `scripts/retime_gaps.py`, get word times with `scripts/align_words.py`. Before spending credits on any paid provider, say what it will cost and wait for a yes; afterwards, report what it cost.

## 4. Build

`references/motion-build.md` covers the setup, the seek-safe `I/G` helper, the camera, the glass CSS, the z-index ladder, headlines, captions, safe zones, and the errors already met. Key every cue to the word times in `words.json` so a new voice re-times the whole animation.

Sound effects: `scripts/sfx_synth.py` with a cue list taken from the word times (whooshes on camera moves, glass taps on cards, ticks on typing, a swell on the end card). The bed sits about 10 LU under the voice.

Snapshot every beat, fix, run `npx hyperframes check` until it passes, open the Studio preview, and ask: render, or what changes?

## 5. Render and deliver

`npx hyperframes render -o renders/<slug>.mp4`. Verify: 1080x1920, 30 fps, audio present, loudness about -13 to -14 LUFS, and look at frames pulled from the MP4 itself (including frame 0). Then make the caption and cover and deliver all three together.

## 6. Caption and cover (always, with every reel)

- **Caption** (`captions.md` in the project): a short hook line; one or two lines that add to the reel without repeating the voiceover; the CTA naming the same keyword and payoff as the voice; five hashtags; plus one alternative first line to test. No em dashes.
- **Cover:** a one-frame HyperFrames project at `<slug>-cover/`, 1080x1920, with the reel's signature line and shot in the same look. Keep the title and visual inside the profile grid's 3:4 crop (y 240 to 1680). Export PNG and JPG into the reel's `renders/`, and send a side-by-side of the full 9:16 and the grid crop.

## Project layout

`<slug>/`:
- `BRIEF.md`: source of truth (script version, voice, decisions, delivery).
- `SCRIPT.md`, `frame.md` (the design spec for this reel).
- `compositions/reel.html`, `compositions/words.json`.
- `public/`: fonts, logos, `audio/voice.wav`, `audio/sfx.wav`.
- `src/`: `script.txt` (with `|` at each pause), `sfx-cues.json`.
- `.media/audio/voice/`: every take and version.
- `renders/`: `<slug>.mp4`, `<slug>-cover.png` and `.jpg`, `<slug>-cover-views.png`.
- `captions.md`.

When the user corrects something, add a dated line to `references/lessons.md`, so the next reel starts from it.

## Scripts

| Script | Use |
|---|---|
| `scripts/prosody.py takes/*.mp3` | Pitch spread, pitch movement and pauses per take; pick the most expressive with no mid-phrase stall |
| `scripts/retime_gaps.py raw.mp3 --list`, then `--plan plan.json --out voice.wav` | Set sentence-gap lengths, master to -16 LUFS |
| `scripts/align_words.py voice.wav script.txt words.json` | Word times from measured silences (`\|` marks each pause in the script) |
| `scripts/sfx_synth.py cues.json sfx.wav --dur 35` | Local sound-design bed, no samples, no credits |

The scripts need Python 3 with numpy, and ffmpeg on the PATH.
