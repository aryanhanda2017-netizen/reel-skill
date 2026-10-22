#!/usr/bin/env python3
"""Inspect the actual exported media. Standard library plus ffmpeg/ffprobe.

python3 verify.py probe renders/video-v1.mp4 --project project [--decode]
python3 verify.py frames renders/video-v1.mp4 1,5,10 --out new-frame-directory
"""
import argparse
import json
import subprocess
from fractions import Fraction
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command",choices=("probe","frames"));ap.add_argument("video");ap.add_argument("times",nargs="?")
    ap.add_argument("--project");ap.add_argument("--out");ap.add_argument("--decode",action="store_true")
    args=ap.parse_args()
    data=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",args.video],text=True))
    video=next(s for s in data["streams"] if s["codec_type"]=="video")
    audio=[s for s in data["streams"] if s["codec_type"]=="audio"]
    if args.command=="frames":
        if not args.times or not args.out:ap.error("frames needs times and a new --out directory")
        output=Path(args.out);output.mkdir(parents=True,exist_ok=False)
        for i,t in enumerate(map(float,args.times.split(","))):
            if not 0<=t<float(data["format"]["duration"]):raise ValueError("Frame time outside video")
            subprocess.run(["ffmpeg","-nostdin","-v","error","-n","-ss",str(t),"-i",args.video,"-frames:v","1","-q:v","2",str(output/f"{i:02d}-{t:.3f}.jpg")],check=True)
        print(output);return
    if not audio:raise ValueError("No narration audio stream")
    summary={"width":video["width"],"height":video["height"],"fps":video["avg_frame_rate"],"duration":float(data["format"]["duration"]),"bytes":int(data["format"]["size"]),"audio_codec":audio[0]["codec_name"]}
    if args.project:
        root=Path(args.project);cfg=json.loads((root/"project.json").read_text())
        storyboard=json.loads((root/"storyboard.json").read_text())
        assert [summary["width"],summary["height"]]==[cfg["width"],cfg["height"]],"Canvas mismatch"
        assert Fraction(summary["fps"])==Fraction(str(cfg["fps"])),"Frame rate mismatch"
        assert abs(summary["duration"]-storyboard["dur"])<=2/float(Fraction(str(cfg["fps"]))),"Duration mismatch"
    if args.decode:
        decoded=subprocess.run(["ffmpeg","-nostdin","-v","error","-i",args.video,"-f","null","-"],capture_output=True,text=True)
        assert decoded.returncode==0 and not decoded.stderr.strip(),decoded.stderr
        summary["full_decode"]="passed"
    print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
