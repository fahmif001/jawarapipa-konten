#!/usr/bin/env python3
"""Render a reel HTML (uses brand/reel-engine.js, window.SC) to a silent 1080x1920 30fps MP4.
usage: python3 tools/render_reel.py content/<slug>/reel.html /tmp/<slug>-silent.mp4
Prints the scene start times (needed by music.py and vo.py)."""
import asyncio, os, pathlib, subprocess, sys, tempfile, json
from playwright.async_api import async_playwright

CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")
FPS = 30

async def main(html, out):
    url = pathlib.Path(html).resolve().as_uri()
    tmpd = tempfile.mkdtemp(prefix="reel_")
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.goto(url); await pg.wait_for_load_state("networkidle"); await pg.evaluate("document.fonts.ready")
        sc = await pg.evaluate("window.SC")
        files = []
        for i, (_, dur) in enumerate(sc):
            n = round(dur * FPS); tmp = f"{tmpd}/s{i}.tmp.mp4"; fin = f"{tmpd}/s{i}.mp4"
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                                   "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
            for f in range(n):
                await pg.evaluate(f"show({i},{f / FPS},{dur})")
                ff.stdin.write(await pg.screenshot(type="jpeg", quality=92))
            ff.stdin.close(); assert ff.wait() == 0
            os.replace(tmp, fin); files.append(fin)
        await b.close()
    with open(f"{tmpd}/list.txt", "w") as fh:
        for f in files: fh.write(f"file '{f}'\n")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmpd}/list.txt", "-c", "copy", out + ".tmp.mp4"], check=True)
    os.replace(out + ".tmp.mp4", out)
    starts, t = [], 0.0
    for _, d in sc: starts.append(round(t, 3)); t += d
    print(json.dumps({"out": out, "scene_starts": starts, "duration": round(t, 3)}))

asyncio.run(main(sys.argv[1], sys.argv[2]))
