# Worked example: "How an AI agent works"

A complete 34-second reel built with this skill. Read `compositions/reel.html` before building a new reel: it has every pattern from `references/motion-build.md` in working form.

- `index.html`: the host. One sub-composition for the whole reel, plus the voice and SFX tracks.
- `compositions/reel.html`: the reel. One camera world (`#cam`): a brain node, tools and memory nodes, a loop that lights up as the voice says "pick, do, look", Claude and OpenAI logos on glass, a comment box that types the keyword, a DM card, an end card.
- `compositions/words.json`: word times of the voiceover (the same data is inlined as `W` in the composition).
- `src/script.txt`: the script, with a `|` at every pause the voice took.
- `src/sfx-cues.json`: the sound-design cues for `scripts/sfx_synth.py`.

The CTA uses a placeholder keyword (AGENT) and handle (`@yourhandle`). Swap in yours from `references/brand.md`.

## Rendering it yourself

The media files aren't included. To render this example, add:

- `public/fonts/`: `archivo-black-400.woff2`, `poppins-400.woff2`, `poppins-500.woff2`, `poppins-700.woff2`, `eb-garamond-400-italic.woff2` (all free on Google Fonts).
- `public/logos/`: `claude.svg` and `openai.svg` (official marks, e.g. via `npx hyperframes media-use resolve --type logo`).
- `public/audio/voice.wav`: a voiceover of `src/script.txt` (see `references/voice.md`), then re-run `scripts/align_words.py` so `words.json` matches your voice.
- `public/audio/sfx.wav`: `python3 ../scripts/sfx_synth.py src/sfx-cues.json public/audio/sfx.wav --dur 34`.

Then, from this folder: `npx hyperframes check` and `npx hyperframes render -o renders/example.mp4`.

The easier way: ask Claude, "rebuild the example reel with my voice and my keyword".
