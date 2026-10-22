#!/usr/bin/env python3
"""Apply approved source-time cuts. Previous outputs and cut maps are preserved.

python3 cut.py project 12.4-14.0 65.0-68.0
python3 cut.py project --clear
"""
import argparse
import json
import subprocess
from fractions import Fraction
from pathlib import Path
from projectlib import load_json, validate_cuts, write_text


def sec(value):
    parts = value.split(":")
    return sum(float(x) * 60 ** i for i, x in enumerate(reversed(parts)))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project"); ap.add_argument("ranges", nargs="*"); ap.add_argument("--clear", action="store_true")
    args = ap.parse_args(); root = Path(args.project).resolve()
    config = load_json(root / "project.json"); rate = float(Fraction(str(config["fps"])))
    if args.clear:
        write_text(root / "cuts.json", json.dumps({"cuts":[]}, indent=2) + "\n")
        print("The build will use the full prepared footage. All existing media is retained.")
        return
    if not args.ranges:
        ap.error("Provide approved cut ranges or --clear")
    cuts = validate_cuts([[round(sec(x) * rate) / rate for x in r.split("-")] for r in args.ranges], config["src_dur"])
    keep = []; pos = 0
    for a, b in cuts:
        if a > pos: keep.append((pos, a))
        pos = b
    if pos < config["src_dur"]: keep.append((pos, config["src_dur"]))
    index = 1
    while (root / f"public/footage-cut-v{index}.mp4").exists(): index += 1
    output = root / f"public/footage-cut-v{index}.mp4"
    filters = []; labels = ""
    for i, (a, b) in enumerate(keep):
        filters.append(f"[0:v]trim=start={a:.9f}:end={b:.9f},setpts=PTS-STARTPTS[v{i}]")
        audio = f"[0:a]atrim=start={a:.9f}:end={b:.9f},asetpts=PTS-STARTPTS"
        if i: audio += ",afade=t=in:st=0:d=0.02"
        if i < len(keep)-1: audio += f",afade=t=out:st={max(0,b-a-.02):.9f}:d=0.02"
        filters.append(audio + f"[a{i}]"); labels += f"[v{i}][a{i}]"
    graph = ";".join(filters) + f";{labels}concat=n={len(keep)}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-n", "-i", str(root / "public/footage.mp4"),
                    "-filter_complex", graph, "-map", "[v]", "-map", "[a]", "-c:v", "libx264",
                    "-preset", "fast", "-crf", "18", "-threads", "2", "-g", str(round(rate)), "-r", str(config["fps"]),
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(output)], check=True)
    write_text(root / "cuts.json", json.dumps({"cuts":cuts, "footage":output.name}, indent=2) + "\n")
    print(f"Saved {output.name}; source-time edit cues will be mapped through cuts.json. Rebuild after review.")


if __name__ == "__main__": main()
