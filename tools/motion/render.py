#!/usr/bin/env python3
"""Render HTML/CSS/JS motion template → mp4 (Playwright headless + ffmpeg).
Injects a fake clock so every frame is deterministic and fast.
Usage: render.py templates/intro.html out.mp4 [--w 1080 --h 1920 --fps 30 --dur 3.6 --audio jingle.wav --qs 'title=...']"""
import argparse, os, subprocess as sp, tempfile, time
from pathlib import Path
from playwright.sync_api import sync_playwright

INJECT = """
(() => {
  window.__t = 0;
  window.__rafCbs = [];
  const origin = 0;
  performance.now = () => window.__t;
  Date.now = () => origin + window.__t;
  window.requestAnimationFrame = (cb) => { window.__rafCbs.push(cb); return window.__rafCbs.length; };
  window.cancelAnimationFrame = () => {};
  window.__tick = (ms) => {
    window.__t = ms;
    const cbs = window.__rafCbs.splice(0);
    cbs.forEach(cb => { try { cb(ms); } catch(e){} });
    // one more drain in case callbacks scheduled new ones
    const cbs2 = window.__rafCbs.splice(0);
    cbs2.forEach(cb => { try { cb(ms); } catch(e){} });
  };
})();
"""

def render(html, out, w=1080, h=1920, fps=30, dur=None, audio=None, qs=""):
    html = Path(html).resolve(); out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    url = html.as_uri()
    if qs:
        url += ("&" if "?" in url else "?") + qs.lstrip("?&")
    with tempfile.TemporaryDirectory(prefix="pitoon_fr_") as td:
        td = Path(td)
        with sync_playwright() as p:
            args=["--disable-dev-shm-usage", "--no-sandbox", "--font-render-hinting=none"]
            try:
                browser = p.chromium.launch(headless=True, args=args)
            except Exception:
                browser = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome", args=args)
            page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            page.add_init_script(INJECT)
            page.goto(url, wait_until="networkidle", timeout=90000)
            page.wait_for_function("() => window.__READY === true", timeout=15000)
            if dur is None:
                dur = page.evaluate("() => window.__DURATION || 3")
            n = max(1, int(round(float(dur) * fps)))
            t0 = time.time()
            for i in range(n):
                ms = i * (1000.0 / fps)
                page.evaluate("(ms) => window.__tick(ms)", ms)
                page.screenshot(path=str(td / f"f{i:05d}.png"), type="png", animations="disabled")
            browser.close()
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(fps), "-i", str(td / "f%05d.png")]
        if audio and Path(audio).exists():
            # pad/trim audio to exact video duration (avoid -shortest cutting a long visual to a short SFX)
            cmd += ["-i", str(audio), "-af", f"apad,atrim=0:{float(dur):.3f}", "-c:a", "aac", "-b:a", "160k"]
        else:
            cmd += ["-an"]
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-t", f"{float(dur):.3f}", "-movflags", "+faststart", str(out)]
        sp.run(cmd, check=True)
        return {"frames": n, "dur": float(dur), "out": str(out), "elapsed": round(time.time() - t0, 2)}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("html"); ap.add_argument("out")
    ap.add_argument("--w", type=int, default=1080); ap.add_argument("--h", type=int, default=1920)
    ap.add_argument("--fps", type=int, default=30); ap.add_argument("--dur", type=float)
    ap.add_argument("--audio"); ap.add_argument("--qs", default="")
    a = ap.parse_args(); print(render(a.html, a.out, a.w, a.h, a.fps, a.dur, a.audio, a.qs))
