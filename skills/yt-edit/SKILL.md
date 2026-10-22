---
name: yt-edit
description: Edit an existing narrated YouTube video with word-timed captions, section cards, callouts and supplied screen recordings, then deliver a verified MP4 and YouTube description.
---

# YT Edit

Turn a creator's rough cut into an edited long-form video. Preserve their voice, source framing and sequence unless they request a change. Use their supplied recordings for demonstrations. This skill adds designed overlays and edits; it does not generate realistic footage or publish videos.

The package is self-contained. Resolve `scripts/`, `assets/` and `references/` relative to this SKILL.md. New projects copy their runtime into `src/runtime`; they do not depend on where this skill is installed.

## Start with the actual project

For an existing project, read its `project.json`, `plan.md` and feedback first. Keep its runtime pin. For a new edit, establish the source, supplied screen recordings, title, aspect ratio and preferred look from the request. Ask only for missing decisions that matter. Default to the source aspect ratio and neutral theme; never crop a person's footage or add a permanent side bezel to change its aspect ratio without their choice.

The machine needs Python 3.9+, Node.js 22+, ffmpeg and ffprobe. The project launcher pins HyperFrames 0.8.139. GSAP 3.15.0 is materialized per project by `setup_runtime.py`; it is a separate licensed dependency. Transcription is local but its first use can download an engine and model. No paid generation is required.

## Prepare

Read [references/editing.md](references/editing.md) for helper signatures and project settings.

```bash
python3 <skill-dir>/scripts/prep.py input.mp4 video-project --title "Video title"
python3 <skill-dir>/scripts/setup_runtime.py video-project
python3 <skill-dir>/scripts/transcribe.py video-project --model base
```

If word times were supplied, give `prep.py --transcript words.json` and skip transcription. Inspect the prepared footage. Correct the working transcript while retaining `transcript.raw.json`. Read [references/timing.md](references/timing.md) before setting cues. Transcription estimates are not proof of speech alignment.

## Plan, frames, render

Default to three review gates, unless the user has already approved the relevant work or asks to proceed through them.

1. **Plan:** author `src/edit.py` against source time using `at("spoken phrase")`. `python3 src/edit.py` writes only the plan and storyboard. Show the table in finished-video time, proposed cuts, and missing recordings. Review before building.
2. **Frames:** after plan approval, run `python3 src/edit.py --build`, then `node src/hf.mjs check public`. Capture the actual composition at the changed moments with `node src/hf.mjs snapshot public --at 1,5,10 --no-end --describe false -o snapshots/v1`. Inspect overflow, faces, private screen content, cue timing and handoffs. Show frames and an audio-bearing review excerpt when timing changes. Review before the full render.
3. **Render:** follow [references/delivery.md](references/delivery.md). Deliver the verified full MP4 and the description together. Apply existing approval; do not reopen a gate the user has already passed.

Keep authored times in source time. Approved cuts are applied by `scripts/cut.py`; the engine maps cards and words to finished time. Feedback times from a rendered video are finished time: convert with `ytlib.py project --cut m:ss` before changing source cues.

## Editorial rules

- Use `full` for sections, `side` for steps, `tag` for one memorable line, `pip` for demonstrations, and `sidel` for a compact list. About 3–4 graphics a minute is a starting point, not a quota. Leave personal stories room to breathe.
- Words and rows appear on the spoken cue. Avoid stacked parent and child fades that delay legibility. Captions use native timed clips and direct highlight keyframes, not callback-driven DOM swaps.
- Use one continuous camera pose across adjacent screen inserts. Match cut length to narration; extend a real last frame or dissolve intentionally when needed. Inspect the handoff in motion.
- Use real facts and supplied media. Label illustrative reconstructions. Do not fabricate results, brands, testimonials or tool behavior. Get the needed context before capturing authenticated screens or using paid generators.
- Inspect recordings for account menus, notifications, names, paths, passwords and confidential content. A static mask can miss private text during scrolling; check the actual encoded result.
- Preserve sources, raw transcripts and previous output versions. These helpers version changed text outputs and retain render intermediates. Use new filenames for renders. No publishing, uploads, messages or scheduling are part of this skill.
- Description copy uses the creator's own voice, real links and optional channel bio. Do not insert an identity, business or testimonial from another project.

Save agreed preferences and dated corrections in the **project's** `EDIT-NOTES.md`. Keep project-specific rulings out of the installed skill unless the user explicitly wants a reusable default.
