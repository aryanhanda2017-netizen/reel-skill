#!/usr/bin/env python3
"""Create a fresh, self-contained project. Requires ffmpeg and ffprobe.

python3 prep.py input.mp4 output-project --title "My video" [--transcript words.json]
Default framing preserves the source aspect ratio. Cropping is explicit.
"""
import argparse
import json
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path
from projectlib import validate_words

SKILL = Path(__file__).resolve().parents[1]


def probe(path):
    return json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ], text=True))


def prepare(source, output, title, fps=None, height=1080, aspect="source", crop=None, transcript=None):
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_file():
        raise ValueError("Source video does not exist")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Choose a new empty project directory; existing files are preserved")
    info = probe(source)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    if not any(s["codec_type"] == "audio" for s in info["streams"]):
        raise ValueError("Narrated footage needs an audio track")
    rate = str(fps or video["avg_frame_rate"])
    numeric_rate = float(Fraction(rate))
    if not 1 <= numeric_rate <= 120:
        raise ValueError("Frame rate must be between 1 and 120")
    width_in, height_in = video["width"], video["height"]
    crop_filter = ""
    if crop:
        cw, ch, x, y = map(int, crop.split(":"))
        if min(cw, ch) <= 0 or min(x, y) < 0 or x + cw > width_in or y + ch > height_in:
            raise ValueError("Crop lies outside source pixels")
        width_in, height_in = cw, ch
        crop_filter = f"crop={crop},"
    aspect_value = width_in / height_in if aspect == "source" else float(Fraction(aspect.replace(":", "/")))
    if aspect_value < 1.2 or aspect_value > 2.1:
        raise ValueError("This layout supports landscape footage. Choose 4:3 or 16:9 explicitly for other sources")
    height = int(height) // 2 * 2
    if not 240 <= height <= 2160:
        raise ValueError("Height must be between 240 and 2160")
    width = round(height * aspect_value / 2) * 2
    output.mkdir(parents=True, exist_ok=True)
    for name in ("public/broll", "public/vendor", "public/logos", "src/runtime", "renders", "snapshots", "broll-src"):
        (output / name).mkdir(parents=True, exist_ok=True)
    for name in ("ytlib.py", "projectlib.py"):
        shutil.copy2(SKILL / "scripts" / name, output / "src/runtime" / name)
    for name in ("hf.mjs", "preserve-files.mjs"):
        shutil.copy2(SKILL / "scripts" / name, output / "src" / name)
    shutil.copy2(SKILL / "assets/template.html", output / "src/template.html")
    shutil.copy2(SKILL / "assets/edit_starter.py", output / "src/edit.py")
    vf = crop_filter + f"scale={width}:{height}:force_original_aspect_ratio=decrease:flags=lanczos,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0x121722,setsar=1,fps={rate},format=yuv420p"
    subprocess.run([
        "ffmpeg", "-nostdin", "-v", "error", "-n", "-i", str(source), "-map", "0:v:0", "-map", "0:a:0",
        "-vf", vf, "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-threads", "2",
        "-g", str(round(numeric_rate)), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", str(output / "public/footage.mp4")
    ], check=True)
    prepared = probe(output / "public/footage.mp4")
    duration = float(prepared["format"]["duration"])
    cfg = dict(id=output.name, title=title, fps=rate, src_dur=duration, width=width, height=height,
               transcript_file="transcript.json", theme={}, captions={})
    (output / "project.json").write_text(json.dumps(cfg, indent=2) + "\n")
    (output / "metadata.json").write_text(json.dumps(prepared, indent=2) + "\n")
    (output / "package.json").write_text(json.dumps(dict(
        name="yt-edit-project", private=True, type="module", hyperframesVersion="0.8.139",
        scripts=dict(build="python3 src/edit.py --build", check="node src/hf.mjs check public",
                     preview="node src/hf.mjs preview public", render="node src/hf.mjs render public")
    ), indent=2) + "\n")
    (output / "public/hyperframes.json").write_text(json.dumps({"media":{"autoProxy":False},"authoringSkill":"talking-head-recut"}) + "\n")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-n", "-i", str(output / "public/footage.mp4"),
                    "-vn", "-c:a", "pcm_s16le", str(output / "audio.wav")], check=True)
    if transcript:
        words = validate_words(json.loads(Path(transcript).read_text()), duration)
        (output / "transcript.raw.json").write_text(json.dumps(words, indent=2) + "\n")
        (output / "transcript.json").write_text(json.dumps(words, indent=2) + "\n")
    print(f"Prepared {width}x{height}, {rate} fps, {duration:.3f}s. Source aspect preserved unless --aspect/--crop was selected.")
    print("Next: setup_runtime.py, transcription if needed, then src/edit.py for the plan.")
    return output


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source"); ap.add_argument("project"); ap.add_argument("--title", required=True)
    ap.add_argument("--fps"); ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--aspect", choices=("source", "4:3", "16:9"), default="source")
    ap.add_argument("--crop"); ap.add_argument("--transcript")
    a = ap.parse_args()
    prepare(a.source, a.project, a.title, a.fps, a.height, a.aspect, a.crop, a.transcript)


if __name__ == "__main__":
    main()
