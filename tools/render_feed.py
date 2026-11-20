#!/usr/bin/env python3
"""Render a feed design HTML to JPG.
usage: python3 tools/render_feed.py content/<slug>/design.html media/<slug>.jpg [--w 1080 --h 1350]
Multi-page carousel: give each page <section class="page"> ; pass --pages to export page-1.jpg, page-2.jpg ...
"""
import argparse, asyncio, os, pathlib
from playwright.async_api import async_playwright

CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")

async def main(a):
    url = pathlib.Path(a.html).resolve().as_uri()
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": a.w, "height": a.h})
        await pg.goto(url); await pg.wait_for_load_state("networkidle"); await pg.evaluate("document.fonts.ready")
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        if a.pages:
            n = await pg.evaluate("document.querySelectorAll('section.page').length")
            stem, ext = os.path.splitext(a.out)
            for i in range(n):
                await pg.evaluate(f"document.querySelectorAll('section.page').forEach((s,k)=>s.style.display=k=={i}?'block':'none')")
                await pg.screenshot(path=f"{stem}-{i+1}{ext}", type="jpeg", quality=95)
                print(f"{stem}-{i+1}{ext}")
        else:
            await pg.screenshot(path=a.out, type="jpeg", quality=95); print(a.out)
        await b.close()

ap = argparse.ArgumentParser()
ap.add_argument("html"); ap.add_argument("out")
ap.add_argument("--w", type=int, default=1080); ap.add_argument("--h", type=int, default=1350)
ap.add_argument("--pages", action="store_true")
asyncio.run(main(ap.parse_args()))
