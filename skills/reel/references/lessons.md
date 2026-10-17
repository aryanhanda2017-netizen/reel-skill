# Lessons (newest first)

This file is how the skill learns your taste. Whenever you correct a reel ("the pauses feel awkward", "too many colours on the end card"), Claude adds a dated entry here: what you said, and what changed. Every new reel reads this file before it starts.

Template:

```
## YYYY-MM-DD: <reel slug>
- You said: "<your words>"
- Changed: <what the skill does differently from now on>
```

## Lessons that came with the skill

- **Voice:** generating the script line by line is the main cause of a flat voice. Always one continuous take, three takes, pick by measurement (`voice.md`).
- **Pauses:** uneven gaps between sentences read as "awkward". Re-time only the sentence-end gaps (`retime_gaps.py`), leave comma pauses alone.
- **Scripts marked "approved" in a plan still get a humanizer pass** before voicing. Show it as a before/after table plus two or three hook options.
- **Keep scripts to hook, proof, payoff, CTA.** Honest caveats ("it won't fool every detector") usually get cut; ask before keeping one.
- **Frame 0:** timeline sets at t=0 don't apply to the first rendered frame. Mirror every t=0 state in CSS and check frame 0 of every render.
- **"Be quick" / "it's just a demo":** skip the extra review gates, but still ship the caption and cover. If it's unclear what a "demo" means, ask before skipping gates.
- **Glass:** never fade or blur the wrapper of a glass card; it flattens the frost.
