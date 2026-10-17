"""Deterministic sound-design bed, synthesized locally (no samples, no credits, fixed seed).

Why local: most TTS tools are speech-only, and stock SFX catalogs need an account. A quiet synthesized
bed (whooshes on camera moves, glass taps on cards) is enough for a faceless reel; add music in the app.

    python3 sfx_synth.py cues.json public/audio/sfx.wav --dur 35

cues.json is a list; times come from compositions/words.json so effects land on the words:
  [{"t": 0.12, "type": "thump", "gain": 0.55},
   {"t": 3.62, "type": "whoosh", "gain": 0.30, "dur": 0.55, "f0": 500, "f1": 2600},
   {"t": 21.15, "type": "glass", "gain": 0.14, "f": 1900, "dur": 0.25, "n": 5, "every": 0.08, "fstep": 180}]

Types and their knobs (defaults in brackets):
  whoosh  dur[0.55] f0[500] f1[2600]   camera moves (swap f0/f1 for a falling whoosh)
  glass   f[2400] dur[0.35]             cards/chips landing, pops, chimes
  tick    f[3200] dur[0.06]             cursor drops, typing, clock ticks
  thump   f[58] dur[0.55]               hook slam
  bloop   f0[520] f1[180] dur[0.32]     drop into liquid / plug-in (f0<f1 rises)
  shimmer dur[0.7] f0[700] f1[2800]     light racing, reveals
  flow    dur[1.5]                      liquid/data flow with bubble pops
  swell   dur[1.6] f[110]               end-card swell
Repeat a cue with n / every (seconds) / fstep (Hz added per repeat).
Gains around 0.15-0.5; the bed should sit ~10 LU under the voice (voice -16 LUFS, bed about -26 LUFS).
"""
import argparse, json, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(20261007)


def env(n, a, d, shape=4.0):
    t = np.arange(n) / SR
    return np.minimum(1.0, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) * shape / max(d, 1e-4))


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for k in range(len(x)):
        s = (1 - a) * x[k] + a * s; y[k] = s
    return y


def whoosh(dur=0.55, f0=500, f1=2600):
    n = int(dur * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n); ch = 480
    for c in range(0, n, ch):
        f = f0 + (f1 - f0) * (c / n); seg = x[c:c + ch]
        out[c:c + ch] = lp(seg, f * 1.6) - lp(seg, f * 0.6)
    out /= (np.max(np.abs(out)) + 1e-9)
    return out * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.6


def glass(f=2400, dur=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2*np.pi*f*t) + 0.55*np.sin(2*np.pi*f*2.76*t) + 0.3*np.sin(2*np.pi*f*5.4*t)
    return s * env(n, 0.002, dur, 5.5) / 1.85


def tick(f=3200, dur=0.06):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2*np.pi*f*t) * 0.6 + rng.standard_normal(n) * 0.4) * env(n, 0.001, dur, 9)


def thump(f=58, dur=0.55):
    n = int(dur * SR); t = np.arange(n) / SR; fr = f * (1 + 1.2 * np.exp(-t * 18))
    return np.sin(2*np.pi*np.cumsum(fr)/SR) * env(n, 0.003, dur, 6)


def bloop(f0=520, f1=180, dur=0.32):
    n = int(dur * SR); t = np.arange(n) / SR; fr = f1 + (f0 - f1) * np.exp(-t * 14)
    return np.sin(2*np.pi*np.cumsum(fr)/SR) * env(n, 0.004, dur, 5)


def shimmer(dur=0.7, f0=700, f1=2800):
    n = int(dur * SR); t = np.arange(n) / SR; fr = f0 * (f1 / f0) ** (t / dur)
    s = np.sin(2*np.pi*np.cumsum(fr)/SR) * (0.6 + 0.4*np.sin(2*np.pi*14*t))
    return s * np.sin(np.pi * np.clip(t/dur, 0, 1)) ** 1.2


def flow(dur=1.5):
    n = int(dur * SR); t = np.arange(n) / SR
    x = lp(rng.standard_normal(n), 420); x /= (np.max(np.abs(x)) + 1e-9)
    s = x * (0.55 + 0.45*np.sin(2*np.pi*3.1*t)*np.sin(2*np.pi*0.7*t + 1)) * np.sin(np.pi*np.clip(t/dur, 0, 1)) ** 0.8
    for k in range(9):
        b = bloop(900 + 140 * (k % 4), 420, 0.09) * 0.35; i = int((0.1 + k * dur / 9.5) * SR)
        s[i:i + len(b)] += b[:max(0, min(len(b), n - i))]
    return s


def swell(dur=1.6, f=110):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2*np.pi*f*t)*0.6 + np.sin(2*np.pi*f*1.5*t)*0.3 + np.sin(2*np.pi*f*2*t)*0.2
    return s * np.sin(np.pi * np.clip(t/dur, 0, 1)) ** 2


GEN = {"whoosh": whoosh, "glass": glass, "tick": tick, "thump": thump, "bloop": bloop, "shimmer": shimmer, "flow": flow, "swell": swell}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cues"); ap.add_argument("out"); ap.add_argument("--dur", type=float, required=True)
    a = ap.parse_args()
    bed = np.zeros(int(SR * a.dur))
    for c in json.load(open(a.cues)):
        kind = c["type"]; gain = c.get("gain", 0.25)
        params = {k: v for k, v in c.items() if k not in ("t", "type", "gain", "n", "every", "fstep")}
        for r in range(int(c.get("n", 1))):
            p = dict(params)
            if "fstep" in c:
                key = "f" if "f" in GEN[kind].__code__.co_varnames else "f0"
                p[key] = p.get(key, GEN[kind].__defaults__[GEN[kind].__code__.co_varnames.index(key)]) + c["fstep"] * r
            sig = GEN[kind](**p); i = int((c["t"] + r * c.get("every", 0)) * SR); j = min(len(bed), i + len(sig))
            if j > i: bed[i:j] += sig[:j - i] * gain
    peak = np.max(np.abs(bed))
    if peak > 0.89: bed = bed / peak * 0.89
    f = int(0.3 * SR); bed[-f:] *= np.linspace(1, 0, f)
    with wave.open(a.out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((bed * 32767).astype(np.int16).tobytes())
    print(f"sfx {a.dur:.1f} s -> {a.out}")


if __name__ == "__main__":
    main()
