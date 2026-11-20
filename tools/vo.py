#!/usr/bin/env python3
"""Indonesian voice-over with Piper (id_ID-news_tts-medium).
usage: python3 tools/vo.py content/<slug>/vo.json --dur 21.2 out.wav
vo.json: [{"start": 0.05, "text": "Proyek di Jabodetabek? ..."}, ...]   (start = seconds in the video)
Pronunciation rules (agreed with user) are applied automatically, see FIX below.
Each line must END before the next line starts; the script warns if a line overruns."""
import argparse, io, json, os, re, sys, urllib.request, wave
import numpy as np
from scipy.signal import resample_poly
from scipy.io import wavfile

MODEL_DIR = os.path.expanduser("~/.cache/piper")
BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main/id/id_ID/news_tts/medium/id_ID-news_tts-medium"
FIX = [  # (regex, replacement) – user-approved pronunciations
    (r"\bHDPE\b", "ha-de-pe-e"),
    (r"\b[Ff]ree [Oo]ngkir\b", "gratis ongkir"),
    (r"\b[Ss]tok [Rr]eady\b", "stok tersedia"),
    (r"\b[Rr]eady\b", "tersedia"),
    (r"\bPVC\b", "pe-ve-ce"),
    (r"\bSNI\b", "es-en-i"),
    (r"\bTKDN\b", "te-ka-de-en"),
    (r"\bWA\b", "WhatsApp"),
]

def model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    for ext in (".onnx", ".onnx.json"):
        p = f"{MODEL_DIR}/id{ext}"
        if not os.path.exists(p):
            urllib.request.urlretrieve(BASE + ext, p)
    return f"{MODEL_DIR}/id.onnx"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("json"); ap.add_argument("--dur", type=float, required=True); ap.add_argument("out")
    a = ap.parse_args()
    from piper import PiperVoice
    from piper.config import SynthesisConfig
    v = PiperVoice.load(model())
    cfg = SynthesisConfig(length_scale=0.9, noise_scale=0.6, noise_w_scale=0.7)
    lines = json.load(open(a.json))
    SR = 44100; N = int(a.dur * SR); out = np.zeros(N)
    for k, ln in enumerate(lines):
        t = ln["text"]
        for pat, rep in FIX: t = re.sub(pat, rep, t)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w: v.synthesize_wav(t, w, syn_config=cfg)
        buf.seek(0); sr, x = wavfile.read(buf)
        x = resample_poly(x.astype(np.float64) / 32768, SR, sr)
        i = int(ln["start"] * SR); j = min(N, i + len(x)); out[i:j] += x[: j - i]
        end = ln["start"] + len(x) / SR
        nxt = lines[k + 1]["start"] if k + 1 < len(lines) else a.dur
        print(f"{ln['start']:.2f}-{end:.2f}s  {t}" + ("   <-- OVERRUNS next line, shorten text" if end > nxt + 0.05 else ""))
    out /= max(1e-9, np.max(np.abs(out))) / 0.9
    wavfile.write(a.out, SR, (out * 32767).astype(np.int16))

main()
