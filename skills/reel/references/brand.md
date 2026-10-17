# Brand: your settings for every reel

Fill this in once (the skill asks you on the first run and writes your answers here). Every reel reads it.
Anything still marked TODO triggers the setup questions.

## Who you are

- Name or handle on the end card and DM card: TODO (e.g. `@yourhandle`)
- What you help with, in one line: TODO
- Who the reels are for: TODO (e.g. "small business owners who are new to AI")

## Call to action

- Comment keyword: TODO (one word, caps on screen, e.g. `AGENT`)
- What people get when they comment it: TODO (e.g. "the free guide by DM")
- Who sends it: you, by hand, or your DM tool. The skill never sends anything.

## Look

The defaults below are a neutral palette (graphite, soft white, one cool-blue accent), the same one the worked example (`example/`) uses. Keep them, or replace them with your brand colours.

| Token | Default | Used for |
|---|---|---|
| ground | `#0E1116` | background (graphite) |
| ink | `#F5F5F2` | text, glass tint |
| accent | `#4C8DFF` | the AI glow and the CTA keyword only, one per frame |
| chip | `#34507A` | caption word highlight, chips |
| bloom 1 | `#34507A` | soft light upper left |
| bloom 2 | `#1E2A40` | soft light lower right |
| secondary text | `#A3ABB8` | small labels (use `rgb(200,206,216)` on glass for contrast) |
| near-black | `#07090C` | shadows, text on light chips |

Fonts (all free on Google Fonts; the skill downloads them as woff2 into `public/fonts/`):
- Headlines: Archivo Black, caps.
- One italic phrase per headline: EB Garamond Italic.
- Captions and UI: Poppins 400, 500, 700.

## Voice

- Provider: TODO (ElevenLabs, Higgsfield, OpenAI, or local Kokoro; see `voice.md`)
- Voice: TODO (name or id once you've picked one)
- Pace and pauses that worked for you: (filled in after the first reel)

## Never

- Copy: no em dashes, one ask per reel, no pricing unless you give it.
- Words you never want used: TODO (e.g. leverage, synergy, unlock, supercharge)
- Claims you never want made: TODO
