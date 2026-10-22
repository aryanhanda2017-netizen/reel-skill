#!/usr/bin/env python3
"""Create a muted screen insert from a source recording, using source timestamps.

python3 broll.py recording.mov demo --project project --segments "2-5,8-10:hold=2"
python3 broll.py recording.mov --frames 2,5,10 --project project

Decode from the beginning and normalize variable frame rate before trimming.
"""
import argparse
import json
import math
import subprocess
from fractions import Fraction
from pathlib import Path


def probe(path):
    return json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], text=True))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("raw"); ap.add_argument("name", nargs="?"); ap.add_argument("--project", required=True)
    ap.add_argument("--segments"); ap.add_argument("--crop"); ap.add_argument("--frames"); ap.add_argument("--width", type=int, default=1440)
    args = ap.parse_args(); root = Path(args.project).resolve(); info = probe(args.raw)
    config = json.loads((root / "project.json").read_text()); rate = str(config["fps"]); fps = float(Fraction(rate))
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    duration = float(info["format"]["duration"])
    cw, ch = video["width"], video["height"]
    if args.crop:
        cw, ch, x, y = map(int, args.crop.split(":"))
        if min(cw,ch)<=0 or min(x,y)<0 or x+cw>video["width"] or y+ch>video["height"]:
            raise ValueError("Crop lies outside recording")
    if not 128 <= args.width <= 3840: raise ValueError("Invalid output width")
    crop = f"crop={args.crop}," if args.crop else ""
    if args.frames:
        output = root / "broll-src" / (Path(args.raw).stem + "-frames")
        output.mkdir(parents=True, exist_ok=False)
        times = [float(x) for x in args.frames.split(",")]
        for i, t in enumerate(times):
            if not 0 <= t < duration: raise ValueError("Frame time outside recording")
            vf = f"fps={rate},select=eq(n\\,{round(t*fps)})," + crop + "scale=640:-2"
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-n", "-i", args.raw,
                            "-vf", vf, "-frames:v", "1", str(output / f"{i:02d}-{t:.3f}.png")], check=True)
        print(output); return
    if not args.name: ap.error("Provide a clip name or --frames")
    if Path(args.name).name != args.name: raise ValueError("Clip name must be a filename")
    scale = min(args.width/cw,1080/ch); width = round(cw*scale/2)*2; height = round(ch*scale/2)*2
    filters = []; labels = ""
    ranges = (args.segments or f"0-{duration}").split(",")
    for i, item in enumerate(ranges):
        rng, *options = item.strip().split(":"); a,b = map(float,rng.split("-"))
        settings = dict(x.split("=") for x in options); speed = float(settings.get("speed",1)); hold = float(settings.get("hold",0))
        if set(settings)-{"speed","hold"} or not 0<=a<b<=duration+.001 or not math.isfinite(speed) or not 0<speed<=8 or not math.isfinite(hold) or not 0<=hold<=300:
            raise ValueError("Invalid segment, speed or hold")
        chain = f"[0:v]fps={rate},trim=start={a}:end={b},setpts=(PTS-STARTPTS)/{speed}," + crop + f"scale={width}:{height}:flags=lanczos,setsar=1,fps={rate},format=yuv420p"
        if hold: chain += f",tpad=stop_mode=clone:stop_duration={hold}"
        filters.append(chain + f"[s{i}]"); labels += f"[s{i}]"
    graph = ";".join(filters) + f";{labels}concat=n={len(ranges)}:v=1:a=0[v]"
    output = root / "public/broll" / (args.name if args.name.endswith(".mp4") else args.name+".mp4")
    output.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-n", "-i", args.raw, "-an", "-filter_complex", graph,
                    "-map", "[v]", "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-threads", "2",
                    "-g", str(round(fps)), "-movflags", "+faststart", str(output)], check=True)
    print(f"{output}: {width}x{height}, no audio")


if __name__ == "__main__": main()
