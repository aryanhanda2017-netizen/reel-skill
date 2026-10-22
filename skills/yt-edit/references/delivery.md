# Render, verify and deliver

Render only after the relevant approval, or an existing instruction to finish the edit. Stop only previews started for this project. Keep the tested CLI pin; do not upgrade it as part of an edit.

From the prepared project directory:

```bash
node src/hf.mjs render public --quality delivery --crf 16 --workers 1 --output renders/video-v1.mp4
python3 <skill-dir>/scripts/verify.py probe renders/video-v1.mp4 --project . --decode
python3 <skill-dir>/scripts/verify.py frames renders/video-v1.mp4 1,20,60 --out snapshots/render-v1
```

Choose frame times inside this video's duration. Verify width/height, frame rate, full duration and audio against the project, then inspect the actual exported frames. A passing decode or layout check does not prove speech alignment; listen to audio-bearing samples. For caption changes, compare early/middle/late moments. For edits/cuts, verify the joins and audio continuity.

Use a roomy output disk for long renders. Set `TMPDIR` and `--frames-cache-dir` there as needed. The preservation launcher retains cache/intermediate files; account for their storage. Filesystems with large allocation units can use much more physical disk than file sizes imply. No cleanup is performed by this workflow.

Always deliver:

- Full MP4 with version and exact local path. Label any smaller review copy as a preview.
- `youtube-description.md`: 2–3 lines explaining the video, the real resource links used/promised, optional creator-provided channel bio, and source credits as needed. Put copy in a fenced text block. Leave editorial notes outside it. Never invent a missing URL or another person's identity.
- Optional chapter list derived from actual finished-video times: start at 0:00, at least three chapters, each at least ten seconds. Treat short section-card labels as candidates rather than blindly publishing them.

Preserve the approved audio level. If a louder delivery is useful, offer it and make a separate version only on request. Inspect loudness and true peak after processing; do not confuse a louder file with a better edit. Publishing or creating a public download repository is a separate action.
