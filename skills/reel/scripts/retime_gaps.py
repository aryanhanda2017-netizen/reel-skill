"""Re-time the pauses in a single voiceover take, then master it.

Why: TTS engines leave pauses of their own choosing, and uneven pauses are what make a voiceover sound
"off". So every gap between sentences is set to a planned length, and nothing inside a phrase is touched.

Step 1, list the pauses (and read them against the transcript to see which word each follows):
    python3 retime_gaps.py RAW.mp3 --list
Step 2, write a plan JSON mapping pause index -> target seconds (unlisted pauses stay as they are):
    {"1": 0.38, "4": 0.40, "6": 0.48, "9": 0.45, "12": 0.50}
Step 3, apply and master:
    python3 retime_gaps.py RAW.mp3 --plan plan.json --out voice.wav

Defaults: pauses >= 0.15 s at -42 dB; 35 ms of natural decay/onset kept at each edge; 0.12 s lead-in;
master = highpass 70 Hz, gentle 2.2:1 compression, loudnorm -16 LUFS / -1.5 dBTP, 48 kHz mono.
"""
import argparse, json, re, subprocess, sys, wave
import numpy as np

SR = 48000


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def silences(path, noise, mind):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=noise={noise}dB:d={mind}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", err)]
    ends = re.findall(r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", err)
    out = []
    for s, (e, d) in zip(starts, ends):
        out.append((s, float(e), float(d)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--plan")
    ap.add_argument("--out", default="voice.wav")
    ap.add_argument("--noise", type=float, default=-42)
    ap.add_argument("--min", type=float, default=0.15)
    ap.add_argument("--lead", type=float, default=0.12)
    ap.add_argument("--keep", type=float, default=0.035)
    ap.add_argument("--lufs", type=float, default=-16)
    a = ap.parse_args()

    sil = [x for x in silences(a.raw, a.noise, a.min) if x[0] > 0.05]  # ignore leading silence
    if a.list or not a.plan:
        print("idx  start   end     dur")
        for i, (s, e, d) in enumerate(sil):
            print(f"{i:>3}  {s:6.2f}  {e:6.2f}  {d:.2f}")
        if not a.plan:
            print("\nWrite a plan JSON {index: target_seconds} for the sentence-end pauses, then rerun with --plan.")
        return

    plan = {int(k): float(v) for k, v in json.load(open(a.plan)).items()}
    x = load(a.raw); keep = int(a.keep * SR); out = []; cur = 0
    for i, (s, e, d) in enumerate(sil):
        if i not in plan:
            continue
        ia, ib = int(s * SR), int(e * SR)
        out.append(x[cur:ia + keep])
        out.append(np.zeros(max(0, int(plan[i] * SR) - 2 * keep), dtype=np.float32))
        out.append(x[ib - keep:ib])
        cur = ib
    out.append(x[cur:])
    y = np.concatenate([np.zeros(int(a.lead * SR), dtype=np.float32)] + out)
    tmp = a.out.rsplit(".", 1)[0] + "-edit.wav"
    with wave.open(tmp, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af",
                    f"highpass=f=70,acompressor=threshold=-20dB:ratio=2.2:attack=8:release=120:makeup=1.5,loudnorm=I={a.lufs}:TP=-1.5:LRA=9",
                    "-ar", str(SR), a.out], check=True)
    print(f"edited {len(y)/SR:.2f} s (raw {len(x)/SR:.2f} s) -> {a.out} (unmastered edit kept at {tmp})")
    print("pauses after edit:")
    for s, e, d in [z for z in silences(a.out, a.noise, 0.12) if z[0] > 0.05]:
        print(f"  {s:6.2f}-{e:6.2f} ({d:.2f})")


if __name__ == "__main__":
    sys.exit(main())
