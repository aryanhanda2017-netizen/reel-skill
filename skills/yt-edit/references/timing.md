# Speech timing and smooth handoffs

Use corrected words and actual audio as the timing reference. A second ASR pass is not independent evidence of accurate word onsets. Sample a short export early, midway and late; listen against the visible highlights.

When speech timing is visibly wrong, first distinguish a constant audio/container offset from per-word errors. Measure source and prepared/export audio alignment. A constant shift cannot repair different errors at different words. Prefer corrected-text acoustic alignment through an available local alignment engine; that is optional and may need substantial model downloads. Do not silently add a large dependency stack. Preserve the original transcript and save an aligned working file, for example `transcript.aligned.json`; select it with `project.json` → `transcript_file`.

Accepted transcript schema: a list of `{id, text, start, end}` objects, or `{words:[...]}`. `word` is accepted as an alias for `text`. Times are source seconds, sorted and inside the source duration. Validate the exact words and their alignment before building cards from phrase anchors. Overlapping word intervals should be inspected; they can come from speech or ASR ambiguity.

Caption pages are native HyperFrames clips on one caption track. Adjacent spoken phrases share a boundary, rather than inserting an artificial blank interval. Highlights are direct timeline keyframes. Do not add a fade or an entrance movement to captions. Keep the caption position stable as the speaker moves into a corner.

Card text is legible at its cue. Small positional settling is fine; a parent fade followed by delayed child fades causes late text. Annotation notes use independent time windows, so an old note cannot remain underneath the next one after a seek.

A screen recording does not share the talking-head clock merely because it was recorded during the same session. Match its content to the narration, then build explicit source ranges. Normalize variable-frame-rate recordings before seeking/trimming. Keep a continuous camera pose across neighboring proof scenes. Check the actual handoff and the end of every held frame.
