# /yt-edit

A portable skill for editing narrated YouTube videos with captions, section cards, callouts and screen recordings. Use `/yt-edit` in Claude Code or `$yt-edit` in Codex. It delivers a local MP4 and a YouTube description. You publish the video yourself.

The skill begins with your rough cut. You still choose your good takes, record the demonstrations and review the edit. It can propose trims and silence cuts, but does not change the source sequence without the relevant instruction.

## Install

Copy the **entire** `skills/yt-edit` folder to an empty skill location:

- Claude Code: `~/.claude/skills/yt-edit` or your project's `.claude/skills/yt-edit`.
- Codex: `~/.codex/skills/yt-edit` or your project's `.agents/skills/yt-edit`.

Start a new session if the skill list has already loaded. Do not overwrite a customized existing skill; use a fresh location or preserve it first.

Install just the YouTube editing skill from this repository:

```bash
npx skills add aryanhanda2017-netizen/reel-skill --skill yt-edit
```

This repository also includes `/reel` for faceless vertical videos. See [the repository README](README.md) for that workflow.

You need **Python 3.9+, Node.js 22+, ffmpeg and ffprobe** (including the libx264 encoder). The project uses HyperFrames **0.8.139** and GSAP **3.15.0**. First use can download the CLI/browser and GSAP. Local transcription can also download a Whisper engine and model; choose one suitable for the machine. No paid API account is required for the core workflow.

## Use

```text
/yt-edit Edit this rough cut and these screen recordings. Keep the original aspect ratio. Show me a plan, then frames, before rendering. Deliver the MP4 and YouTube description.
```

In Codex, use `$yt-edit` with the same request. You can supply colours, a style reference and your channel bio, or keep the neutral defaults. The package has no built-in identity, logo, handle, business pitch, custom fonts or watermark.

The review flow is **plan → real frames → full render**. Existing approvals and instructions to work through the gates carry forward. You can give revisions in plain language, such as “make the captions larger” or “bring this card in on this word.” Corrections are saved in that video's own notes.

## What is included

- A self-contained `SKILL.md` and editing, timing and delivery references.
- Python helpers for preparation, local transcription, cuts, screen inserts and output verification.
- A declarative editing engine with `full`, `side`, `tag`, `pip`, `sidel`, rows, notes and chips.
- Native timed captions and seekable word highlights, with no caption callback clock.
- Source-aspect framing by default, explicit crop/aspect controls, configurable neutral colours and system fonts.
- A project-local, pinned CLI launcher and versioned text writes. Sources and old outputs remain preserved. Render caches/intermediates are retained, so plan disk space accordingly.
- A reproducible synthetic example and standard-library unit tests. No private footage, personal screens or production project files are included.

Generated projects carry their own engine and template. You can move the project or reinstall the skill without breaking existing source imports.

## Run the example

From this repository, choose a new output folder:

```bash
python3 example/create_demo.py ./demo-project --aspect 4:3
python3 skills/yt-edit/scripts/setup_runtime.py ./demo-project
cd demo-project
python3 src/edit.py
python3 src/edit.py --build
node src/hf.mjs check public
node src/hf.mjs render public --output renders/demo-v1.mp4 --workers 1
```

The fixture is **synthetic**, with a test-pattern background and quiet tone. Its caption times are fixture data, not a claim of real speech-alignment quality. Use your own footage and check actual speech timing for production. `--aspect 16:9` exercises the wide layout. Example generation needs only ffmpeg, ffprobe and Python; runtime setup needs internet unless `--gsap-file` supplies an existing matching runtime.

```bash
python3 -m unittest discover -s tests -v
```

## Dependencies and licence

The skill code and documentation are MIT licensed. [HyperFrames](https://github.com/heygen-com/hyperframes) and [GSAP](https://gsap.com/standard-license/) are separate dependencies under their own terms. Their runtime code, fonts, logos and model weights are not bundled in this repository. The GSAP setup helper verifies the pinned npm download's SHA-512 integrity and retains its notices.
