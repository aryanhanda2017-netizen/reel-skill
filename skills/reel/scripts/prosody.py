"""Prosody meter: pitch range (semitones), pitch movement, speaking rate proxy, pauses.

usage: python3 prosody.py file1 [file2 ...]
Decodes with ffmpeg to 16 kHz mono, tracks F0 with a normalised autocorrelation (70-320 Hz),
reports: median F0, pitch spread (std, 5-95% range in semitones), mean absolute pitch movement
between voiced frames (st per 100 ms), voiced ratio, and pauses longer than 0.20 s.
"""
import subprocess, sys
import numpy as np

SR = 16000

def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()

def analyse(x):
    win, hop = int(0.040 * SR), int(0.010 * SR)
    n = 1 + max(0, (len(x) - win) // hop)
    rms = np.array([np.sqrt(np.mean(x[i*hop:i*hop+win] ** 2) + 1e-12) for i in range(n)])
    gate = max(np.percentile(rms, 95) * 0.12, 1e-4)
    lag_min, lag_max = int(SR / 320), int(SR / 70)
    f0 = np.full(n, np.nan)
    for i in range(n):
        if rms[i] < gate:
            continue
        fr = x[i*hop:i*hop+win] * np.hanning(win)
        fr = fr - fr.mean()
        ac = np.correlate(fr, fr, mode="full")[win-1:]
        if ac[0] <= 0:
            continue
        ac = ac / ac[0]
        seg = ac[lag_min:lag_max]
        k = int(np.argmax(seg))
        if seg[k] < 0.45:
            continue
        lag = k + lag_min
        if 1 <= k < len(seg) - 1:  # parabolic refine
            a, b, c = seg[k-1], seg[k], seg[k+1]
            den = a - 2*b + c
            if den != 0:
                lag = lag + 0.5 * (a - c) / den
        f0[i] = SR / lag
    voiced = ~np.isnan(f0)
    v = f0[voiced]
    out = {"dur_s": round(len(x) / SR, 2)}
    if len(v) < 20:
        out["note"] = "too little voiced audio"
        return out
    med = float(np.median(v))
    st = 12 * np.log2(v / med)
    st = st[np.abs(st) < 12]  # drop octave errors
    out["median_f0_hz"] = round(med, 1)
    out["pitch_std_st"] = round(float(np.std(st)), 2)
    out["pitch_range_5_95_st"] = round(float(np.percentile(st, 95) - np.percentile(st, 5)), 2)
    # movement: abs semitone change between consecutive voiced frames 100 ms apart
    idx = np.where(voiced)[0]
    stf = np.full(n, np.nan); stf[voiced] = 12 * np.log2(f0[voiced] / med)
    mv = []
    for i in idx:
        j = i + 10
        if j < n and voiced[j] and abs(stf[j] - stf[i]) < 7:
            mv.append(abs(stf[j] - stf[i]))
    out["movement_st_per_100ms"] = round(float(np.mean(mv)), 2) if mv else None
    out["voiced_ratio"] = round(float(voiced.mean()), 2)
    # pauses
    silent = rms < gate
    pauses, run = [], 0
    first = int(np.argmax(~silent)); last = n - int(np.argmax(~silent[::-1]))
    for i in range(first, last):
        if silent[i]:
            run += 1
        else:
            if run * 0.010 >= 0.20:
                pauses.append(round(run * 0.010, 2))
            run = 0
    out["pauses_over_0.2s"] = pauses
    out["speech_span_s"] = round((last - first) * 0.010, 2)
    return out

if __name__ == "__main__":
    for p in sys.argv[1:]:
        try:
            print(p.split("/")[-1], analyse(load(p)))
        except Exception as e:
            print(p, "ERROR", e)
