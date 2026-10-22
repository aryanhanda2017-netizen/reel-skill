# Validation: version 1.0.0

Validated on 22 October 2026 with Python 3.9, Node.js and the pinned HyperFrames 0.8.139 runtime on macOS / Apple silicon.

- Skill frontmatter and references: passed the skill-creator validator.
- 12 standard-library unit tests: passed. They cover plan-only behavior, caption boundaries, source/finished time mapping, invalid cuts/times, Unicode phrase anchors, preserved text versions, 4:3 and 16:9 geometry, repeated initialization, repeated builds, theme validation and portable imports.
- Fresh 4:3 and 16:9 synthetic projects: built, passed HyperFrames checks with zero errors, rendered and fully decoded. Both are 16 seconds / 25 fps with AAC audio. Render sizes were 720x540 and 960x540 to limit test storage. Actual encoded frames were visually inspected for all five overlay types.
- A copied project rebuilt at a different path; two approved fixture cuts produced the expected 14-second result with intact audio/video streams.
- Variable-frame-rate recording: a three-frame red/green fixture was normalized and trimmed from 0.5 to 1.5 seconds. The result is exactly one second, with the correct colours before and after the source change. Preview frames were checked too.
- Screen-helper holds and speed changes ran successfully; inserts carry no audio. Existing render outputs and unresolved screen placeholders are protected by launcher checks.
- The default GSAP setup path downloaded the pinned npm artifact, verified SHA-512 integrity, and retained its licence notice. The matching-local-file setup path was also exercised.
- Public source scan: no original organization identity, private home/volume paths, client examples, original brand palette or original fonts. No runtime library, font, logo, model weights or private footage is bundled.

HyperFrames reports structural warnings for the single-file overlay/caption layout; there were no lint, runtime, layout or contrast errors in either test project. These are synthetic fixtures with a quiet tone. They do not establish the accuracy of real speech word timing. The optional Whisper/model-download path was not executed in this release test. Linux and Windows were not tested. The default example command can create full 1080-height projects; the exported smoke tests used 540-height canvases.
