"""Original background track for Jawara Pipa Reels (generated, royalty-free).
120 BPM industrial-corporate groove; whoosh at every scene cut, impact hits at given times.
usage: python3 tools/music.py --dur 21.2 --cuts 3.6,6.6,9.6,12.6,16.6 --hits 0.45,13.0,16.65 out.wav"""
import argparse
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
ap=argparse.ArgumentParser(); ap.add_argument("--dur",type=float,required=True); ap.add_argument("--cuts",default=""); ap.add_argument("--hits",default=""); ap.add_argument("out")
A=ap.parse_args()
DUR = A.dur
BPM = 120
BEAT = 60 / BPM
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N: return
    s = sig[: j - i] * gain
    L[i:j] += s * (1 - max(0, pan)); R[i:j] += s * (1 + min(0, pan))

def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.exp(-t / d)
    return e

def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, 0.001, 0.16) * 1.0 + np.tanh(np.sin(ph) * 3) * env(n, 0.001, 0.03) * 0.3

def snare():
    n = int(0.3 * SR); t = np.arange(n) / SR
    noise = sosfilt(butter(2, [1500, 8000], 'band', fs=SR, output='sos'), rng.standard_normal(n))
    tone = np.sin(2 * np.pi * 190 * t) * env(n, 0.001, 0.05)
    return noise * env(n, 0.001, 0.09) * 0.55 + tone * 0.35

def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    noise = sosfilt(butter(4, 7000, 'high', fs=SR, output='sos'), rng.standard_normal(n))
    return noise * env(n, 0.001, 0.06 if open_ else 0.015)

def saw(freq, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = 2 * ((t * freq) % 1) - 1
    s += 2 * ((t * freq * 1.005) % 1) - 1
    return s / 2

def lp(x, fc):
    return sosfilt(butter(2, fc, 'low', fs=SR, output='sos'), x)

def bass(freq, dur):
    n = int(dur * SR)
    s = lp(saw(freq, dur), 600) * env(n, 0.005, dur * 0.8)
    return np.tanh(s * 2) * 0.5

def pad(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(lp(saw(f, dur), 1800) for f in freqs) / len(freqs)
    a = np.minimum(1, t / 0.3) * np.minimum(1, (dur - t) / 0.3)
    return s * a

def whoosh(dur=0.6, up=True):
    n = int(dur * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n); seg = 256
    for k in range(0, n, seg):
        p = k / n; fc = (400 + 7000 * (p if up else 1 - p) ** 2)
        out[k:k+seg] = lp(noise[k:k+seg], fc)
    a = np.sin(np.pi * t / dur) ** 2
    return out * a

def impact():
    n = int(1.2 * SR); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (40 + 60 * np.exp(-t * 12)) * t) * env(n, 0.001, 0.45)
    crash = sosfilt(butter(2, 3000, 'high', fs=SR, output='sos'), rng.standard_normal(n)) * env(n, 0.001, 0.35)
    return boom * 0.9 + crash * 0.25

K, S = kick(), snare()
# chord roots per bar (A minor: Am F C G), bar = 2s
prog = [(55.0, [220, 261.6, 329.6]), (43.65, [174.6, 220, 261.6]), (65.41, [261.6, 329.6, 392]), (49.0, [196, 246.9, 293.7])]
bars = int(np.ceil(DUR / (4 * BEAT)))
for b in range(bars):
    t0 = b * 4 * BEAT
    root, chord = prog[b % 4]
    add(pad(chord, 4 * BEAT), t0, 0.10, 0.0)
    for k in range(8):  # 8th-note bass
        add(bass(root, BEAT / 2 * 0.9), t0 + k * BEAT / 2, 0.55 if k % 2 == 0 else 0.4)
    if t0 < 0.4:  # intro bar: light, no drums until hook lands
        continue
    for k in range(4):
        tb = t0 + k * BEAT
        if tb > DUR - 1.2: break
        add(K, tb, 0.9)
        if k in (1, 3): add(S, tb, 0.5, 0.1)
    for k in range(8):
        th = t0 + k * BEAT / 2
        if th > DUR - 1.2: break
        add(hat(k % 2 == 1 and k == 7), th, 0.18 if k % 2 else 0.12, -0.3)

# scene sync
cuts = [float(x) for x in A.cuts.split(",") if x]
for c in cuts:
    add(whoosh(0.55), c - 0.45, 0.35)
for k, h in enumerate(float(x) for x in A.hits.split(",") if x):
    add(impact(), h, 0.8 if k == 0 else 0.6)
# final sustain + fade
t = np.arange(N) / SR
fade = np.clip((DUR - t) / 1.5, 0, 1)
fadein = np.clip(t / 0.05, 0, 1)
L *= fade * fadein; R *= fade * fadein
mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
mix /= np.max(np.abs(mix)) / 0.89
wavfile.write(A.out, SR, (mix * 32767).astype(np.int16))
print("ok", mix.shape)
