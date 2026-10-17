# Voice pipeline (script → mastered voice → word times)

A flat, robotic voiceover usually has two causes: the script was generated line by line, and the engine's own pauses were left in. This pipeline fixes both. It's half text, half audio.

## 1. Write the TTS text for the ear

- The approved script goes in word for word; only punctuation is tuned. Commas where a person breathes, periods at sentence ends. No ellipses (they make long stalls), no em dashes.
- Write the comment keyword in lowercase in the TTS text ("Comment agent, and…"). In caps, some engines spell it out letter by letter. On screen and in captions it stays in caps.
- **One continuous paragraph for the whole script.** Never generate line by line: each line restarts cold and flat.

## 2. Generate three takes

Use the provider in `brand.md`. Takes vary run to run, so make three identical requests and pick the best by measurement. Before spending credits, say what three takes will cost and wait for a yes; afterwards, report the cost.

| Provider | How | Notes |
|---|---|---|
| ElevenLabs | their API or MCP, with the user's own key | Expressive preset voices |
| Higgsfield | its MCP (`generate_audio`, an ElevenLabs-backed TTS model) | Uses Higgsfield credits; check the cost first with a cost preflight |
| OpenAI | the speech API, with the user's key | Cheap and clean, a little less expressive |
| Kokoro (local) | Python, runs on the user's machine | Free and private; needs Python 3.12 and `espeak-ng` installed |

If a provider has public voice previews, download a few and run them through `prosody.py` before spending anything (trust only previews longer than ~15 s).

Most TTS tools are **speech only**. Don't use them for music or sound effects; sound design comes from `scripts/sfx_synth.py`.

## 3. Pick the take by measurement

```bash
python3 scripts/prosody.py takes/*.mp3
```

Read `pitch_std_st` (expressiveness; aim for about 4.5 to 5 semitones), `movement_st_per_100ms` (how much the pitch moves; higher is livelier) and the pause list (no stall in the middle of a phrase). When only one line changed (often the CTA), cut that stretch out of each take and compare just that.

Then confirm every word with a large Whisper model (small ones drop words like "Comment"):

```bash
npx hyperframes transcribe take.mp3 -d <scratch> --model medium.en --json
```

Whisper word times can run ~0.35 s late. Trust `ffmpeg silencedetect` for where silence really is.

## 4. Re-time the pauses and master

```bash
python3 scripts/retime_gaps.py raw.mp3 --list                       # numbered pauses
python3 scripts/retime_gaps.py raw.mp3 --plan plan.json --out .media/audio/voice/voice.wav
```

Plan only sentence-end pauses; leave comma pauses as spoken. Targets that work:
- after the hook line: 0.38 s
- between problem sentences: 0.40 s
- before the turn: 0.48 s
- after the turn, into the payoff: 0.45 s
- before the CTA: 0.50 s
- small re-times within a section: 0.30 to 0.34 s

The script keeps 35 ms of natural decay at each edge, adds a 0.12 s lead-in, and masters to -16 LUFS. Copy the result to `public/audio/voice.wav`. Keep every raw take beside it in `.media/audio/voice/`.

**Send the voice file to the user before building motion.** Every motion cue hangs off it.

## 5. Word times for captions and cues

Put a `|` in the script text at each real pause (list the silences first: `ffmpeg -i voice.wav -af silencedetect=noise=-38dB:d=0.12 -f null -`), then:

```bash
python3 scripts/align_words.py public/audio/voice.wav src/script.txt compositions/words.json
```

If it reports a mismatch, it prints the speech segments and the `|` groups side by side: move the `|` until they line up (usually a comma the voice ran through, or one it paused on). If the extra segments are 0.12 to 0.14 s gaps inside phrases (consonant stops, not pauses), add `--min 0.18` instead.

## 6. When the script changes after the voice is approved

1. Re-run the copy passes on the changed lines only.
2. Regenerate the **whole** script as new takes. Splicing a new line onto an old take leaves a tonal seam.
3. Re-measure, re-time, re-align, re-run `sfx_synth.py` with the shifted cue times, and update `BRIEF.md` and `SCRIPT.md`.
4. If the motion cues are keyed to word indices (see `motion-build.md`), the animation follows the new voice by itself.
