# Project and helper reference

A prepared project has `project.json`, `public/footage.mp4`, `audio.wav`, a working transcript, `src/edit.py`, `src/template.html`, and a copied `src/runtime` engine. It can be moved after preparation.

`project.json` controls `width`, `height`, `fps`, `src_dur`, `title`, `transcript_file`, `theme` and `captions`. Defaults preserve the source aspect ratio and frame rate. `prep.py --height 1080` is the default resolution; this can upscale a smaller source. Use `--height 720` for a smaller project. `--crop W:H:X:Y` is an explicit pixel crop. `--aspect 4:3` or `--aspect 16:9` fits the whole image inside that chosen canvas; the default `source` adds no aspect-ratio padding. The supplied layout supports landscape canvases.

Theme keys (six-digit hex colours):

```json
{"theme":{"background":"#121722","surface":"#1C2432","text":"#F4F6FA","muted":"#B5C0D2","accent":"#98BEFF","highlight_text":"#111827","border":"#64748B"}}
```

The template uses system sans-serif and Georgia for an optional italic phrase. No fonts or logos are bundled. Add only assets you can use, as ordinary local files, and keep required attribution. The theme has no identity, handle, watermark or channel CTA.

Captions default to short phrases, at most five words / roughly 32 characters. `captions` may set `max_words`, `max_chars`, `pause`, `page_lead` and `word_lead`. The last two default to 0.08 and 0.04 seconds to cover acoustic/frame uncertainty; adjust after listening rather than treating these as a solution to bad word times.

## Authoring

All helper times below are **source seconds**. Content fields accept trusted HTML for simple formatting. Escape untrusted text before placing it in a card.

```python
init(ROOT)
t = at("a phrase in the transcript", after=0)
full(t, t+4, "PART 01", "A clear idea", "One short subline")
side(20, 28, "THE STEPS", "Start here", [
    row(20, "01", "First point", sub="One short explanation"),
    row(23, "02", "Second point"),
], foot=foot(26, "One useful takeaway"))
tag(30, 35, "KEEP THIS", [(30, "A single thought.")])
pip(40, 50, dict(broll="demo.mp4", label="The actual demo", media_start=0), [
    note(40, "FIRST", "What to notice"),
    note(45, "THEN", "What changes"),
])
sidel(52, 58, "YOUR TOOLS", [tool_card(52, "<b>01</b>", "First tool", "What it does")])
plan()  # plan.md and storyboard.json only
# build() after approval: public/index.html plus plan/storyboard
```

Also available: `chip`, `chips`, `chipnote`, `doc_mock`, `set_track`, `words_between`, `sh` (source → finished) and `unsh` (finished → source). Keep section headlines short; use a newline to split a long headline. A side card should hold at most 3–5 short rows. Inspect every layout after changing text or theme.

## Recordings and cuts

```bash
python3 <skill-dir>/scripts/broll.py screen.mov --frames 2,5,10 --project video-project
python3 <skill-dir>/scripts/broll.py screen.mov demo --project video-project --crop 1200:700:30:90 --segments "2-7,10-12:hold=3"
python3 <skill-dir>/scripts/cut.py video-project 12.4-14.0
```

`broll.py` decodes from the beginning, normalizes variable frame rate, then trims. It supports `:hold=seconds` and `:speed=number`, mutes the recording and inserts keyframes every second. It never guesses what is safe to reveal. Cut boundaries are quantized to the project's frames; cuts must not overlap. Each cut-media output gets a new version. `--clear` changes the active cut map and retains all media. Rebuild after cutting. Do not cut merely because a silence exists; propose it unless the user has authorized editorial cuts.
