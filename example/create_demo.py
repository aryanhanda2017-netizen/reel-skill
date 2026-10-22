#!/usr/bin/env python3
"""Make a synthetic 16-second project. Fixture times are not speech-alignment evidence."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
SCRIPTS=REPO/"skills/yt-edit/scripts"
sys.path.insert(0,str(SCRIPTS))
from prep import prepare


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("output");ap.add_argument("--aspect",choices=("4:3","16:9"),default="4:3")
    ap.add_argument("--height",type=int,default=1080)
    args=ap.parse_args();output=Path(args.output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists() and any(output.iterdir()):raise ValueError("Choose a new empty example directory")
    source=output.with_name(output.name+"-synthetic-source.mp4")
    width,height=(640,480) if args.aspect=="4:3" else (640,360)
    subprocess.run(["ffmpeg","-nostdin","-v","error","-n","-f","lavfi","-i",f"testsrc2=s={width}x{height}:r=25",
                    "-f","lavfi","-i","sine=frequency=440:sample_rate=48000","-t","16","-af","volume=0.025",
                    "-c:v","libx264","-preset","veryfast","-crf","23","-threads","2","-c:a","aac","-b:a","96k",str(source)],check=True)
    text="Start with your own recording. Pick a clear section. Show each point as you say it. Use a screen recording for the demonstration. Review the captions and the timing. Then render the full video and write the description."
    words=[dict(id=i,text=w,start=round(.2+i*.35,3),end=round(.48+i*.35,3)) for i,w in enumerate(text.split())]
    transcript=output.with_name(output.name+"-fixture-words.json")
    with transcript.open("x") as f:json.dump(words,f,indent=2)
    prepare(source,output,"Synthetic editing example",height=args.height,transcript=transcript)
    subprocess.run(["ffmpeg","-nostdin","-v","error","-n","-f","lavfi","-i","testsrc2=s=1280x720:r=25",
                    "-t","3.6","-an","-c:v","libx264","-crf","22","-threads","2","-g","25",str(output/"public/broll/demo.mp4")],check=True)
    edit='''"""Synthetic example: five overlay types. No real narrator or real application."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'runtime'))
from ytlib import init,full,side,sidel,row,tag,pip,note,tool_card,plan,build
init(HERE.parent)
tag(.2,2.2,'SYNTHETIC EXAMPLE',[(.2,'Your recording, your edit.')])
full(3,5,'PART 01','A clear story','A section card with a short subline.')
side(6,8.5,'THE STEPS','Keep it simple',[row(6,'01','One clear point'),row(7,'02','Then the next')])
pip(9,12.5,dict(broll='demo.mp4',label='Synthetic screen fixture'),[note(9,'EXAMPLE SCREEN','Look at this step'),note(10.7,'NEXT STEP','Then this detail')])
sidel(13,15.4,'YOUR TOOLS',[tool_card(13,'<b>01</b>','Editor','A generic example'),tool_card(14,'<b>02</b>','Preview','Review before export')])
if '--build' in sys.argv:build()
else:plan()
'''
    (output/"src/edit.py").write_text(edit)
    print(f"Created synthetic project at {output}. Run setup_runtime.py, plan, build, check, then render.")


if __name__=="__main__":main()
