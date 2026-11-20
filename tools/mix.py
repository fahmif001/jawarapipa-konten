#!/usr/bin/env python3
"""Mix music (+ optional voice-over, with ducking) onto a silent reel video. Loudness -14 LUFS (Instagram).
usage: python3 tools/mix.py silent.mp4 music.wav [vo.wav] out.mp4"""
import subprocess, sys, os
args = sys.argv[1:]
video, music, out = args[0], args[1], args[-1]
vo = args[2] if len(args) == 4 else None
tmp = out + ".tmp.mp4"
if vo:
    fc = ("[1:a]aformat=channel_layouts=stereo,highpass=f=90,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=1.6,asplit=2[v1][v2];"
          "[0:a][v2]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[m];[m]volume=0.55[md];"
          "[md][v1]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1:LRA=11[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", music, "-i", vo, "-filter_complex", fc, "-map", "[a]", "-ar", "44100", out + ".mix.wav"], check=True)
else:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", music, "-af", "loudnorm=I=-14:TP=-1:LRA=11", "-ar", "44100", out + ".mix.wav"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", out + ".mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
os.replace(tmp, out); os.remove(out + ".mix.wav"); print(out)
