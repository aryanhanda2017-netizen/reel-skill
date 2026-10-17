"""Give every word of the approved script a start/end time on the mastered voice.

Why not whisper's timestamps: in testing Whisper ran up to 0.35 s late and once dropped the word
"Comment" entirely, which would have put captions and motion cues off the voice. Measured silences are exact.

SCRIPT_TXT is the approved script, verbatim, with a "|" at every pause the voice actually takes
(sentence ends and the commas where the speaker breathes). Each "|"-group must match one speech segment.

    python3 align_words.py voice.wav script.txt compositions/words.json [--min 0.18] [--noise -42]

--min is the shortest silence that counts as a pause (default 0.15). Raise it to ~0.18 when the
mismatch list shows 0.12-0.14 s gaps inside phrases: those are consonant stops, not pauses.

If the group count and the segment count differ, the script prints both lists and exits 1:
move, add or remove "|" until they line up (usually a comma the voice ran through, or a pause it added).
Within a segment, each word gets time in proportion to (letters + 2).
"""
import json, re, subprocess, sys


def segments(path, noise=-42, mind=0.12):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=noise={noise}dB:d={mind}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                               capture_output=True, text=True).stdout.strip())
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", err)]
    sil = list(zip(starts, ends + [dur] * (len(starts) - len(ends))))
    segs, t = [], 0.0
    for s, e in sil:
        if s - t > 0.05:
            segs.append((round(t, 3), round(s, 3)))
        t = e
    if dur - t > 0.05:
        segs.append((round(t, 3), round(dur, 3)))
    return segs


def main():
    args = sys.argv[1:]
    opts = {"--min": 0.15, "--noise": -42.0}
    for k in list(opts):
        if k in args:
            i = args.index(k); opts[k] = float(args[i + 1]); del args[i:i + 2]
    if len(args) < 3:
        print(__doc__); return 2
    wav, txt, out = args[:3]
    groups = [g.split() for g in open(txt).read().replace("\n", " ").split("|") if g.strip()]
    segs = segments(wav, opts["--noise"], opts["--min"])
    if len(groups) != len(segs):
        print(f"MISMATCH: {len(groups)} script groups vs {len(segs)} speech segments\n")
        for i, (a, b) in enumerate(segs):
            print(f"  seg {i:>2}  {a:6.2f}-{b:6.2f}  ({b-a:.2f}s)")
        print()
        for i, g in enumerate(groups):
            print(f"  grp {i:>2}  {len(g):>2} words  {' '.join(g)[:70]}")
        return 1
    words = []
    for (s0, s1), ws in zip(segs, groups):
        weights = [len(w.strip(".,?!")) + 2 for w in ws]; tot = sum(weights); t = s0
        for w, k in zip(ws, weights):
            d = (s1 - s0) * k / tot
            words.append({"t": w, "s": round(t, 3), "e": round(t + d, 3)}); t += d
    json.dump(words, open(out, "w"))
    print(f"{len(words)} words -> {out}")
    print(" ".join(f"{w['t']}@{w['s']:.2f}" for w in words))
    return 0


if __name__ == "__main__":
    sys.exit(main())
