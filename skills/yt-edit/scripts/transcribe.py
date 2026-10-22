#!/usr/bin/env python3
"""Run the pinned local Whisper transcription path on a fresh transcript.

Model downloads may be substantial. Choose a model for the available memory.
"""
import argparse
import json
import subprocess
from pathlib import Path
from projectlib import load_json, validate_words, write_text


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project"); ap.add_argument("--model", default="base")
    args = ap.parse_args(); root = Path(args.project).resolve()
    if (root / "transcript.json").exists() or (root / "transcript.raw.json").exists():
        raise ValueError("Existing transcripts are preserved. Use a new transcript filename for a new transcription pass")
    with (root / "transcribe.log").open("x") as log:
        subprocess.run(["node", "src/hf.mjs", "transcribe", "audio.wav", "-d", ".", "--json", "--model", args.model,
                        "--engine", "whisper"], cwd=root, stdout=log, stderr=subprocess.STDOUT, check=True)
    result = load_json(root / "transcript.json")
    # Preserve the tool's actual raw output, before normalizing its schema.
    (root / "transcript.raw.json").write_text(json.dumps(result,indent=2)+"\n")
    words = validate_words(result, load_json(root / "project.json")["src_dur"])
    write_text(root / "transcript.json", json.dumps(words,indent=2)+"\n")
    lines = ["# Transcript", "", "Source time; inspect names and word timing against the audio.", ""]
    group = []
    for word in words:
        group.append(word)
        if word["text"].endswith((".","?","!")) or len(group)>=30:
            start=group[0]["start"]; lines.append(f"[{int(start//60)}:{int(start%60):02d}] "+" ".join(w["text"] for w in group));group=[]
    if group:
        start=group[0]["start"];lines.append(f"[{int(start//60)}:{int(start%60):02d}] "+" ".join(w["text"] for w in group))
    write_text(root / "transcript.md", "\n".join(lines)+"\n")
    print(f"Saved {len(words)} words. Check timing before cueing cards.")


if __name__ == "__main__": main()
