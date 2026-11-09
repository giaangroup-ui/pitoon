#!/usr/bin/env python3
"""Build full short: intro + title + film(with subs) + outro. Score each MG piece; re-render if <8.
Usage: assemble.py scene.json film.mp4 out_9x16.mp4 [--also-16x9 out_16x9.mp4]"""
import argparse, json, os, subprocess as sp, sys, shutil
from urllib.parse import quote
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from render import render
from score import score_clip
from beats import load_wav, onset_beats, snap
import subs_burn

ASSETS = HERE / "assets"
TEMPL = HERE / "templates"
MAX_TRIES = 3

def scored_render(html, out, audio=None, qs="", w=1080, h=1920, dur=None, label="clip"):
    best = None
    for attempt in range(1, MAX_TRIES + 1):
        # slightly stronger spring feel on retry by qs flag (templates ignore unknown)
        info = render(html, out, w=w, h=h, fps=24, dur=dur, audio=audio, qs=qs)
        sc = score_clip(str(out))
        print(f"  [{label}] try{attempt}: mean={sc['mean']} {sc['scores']}")
        if best is None or sc["mean"] > best["mean"]:
            best = sc; shutil.copy(out, str(out) + ".best")
        if sc["pass"]:
            return sc
        # soften brand miss: nothing to tweak automatically besides re-render (stochastic fonts)
    shutil.copy(str(out) + ".best", out)
    print(f"  [{label}] kept best mean={best['mean']}")
    return best

def concat(clips, out, audio_from=None):
    # xfade-ish soft joins: for simplicity concat demuxer (cuts already on beats)
    lst = Path(str(out) + ".txt")
    lst.write_text("".join(f"file '{Path(c).resolve()}'\n" for c in clips))
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
           "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", str(out)]
    sp.run(cmd, check=True)

def to_aspect(src, dst, aspect):
    if aspect == "9x16":
        vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    else:
        vf = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#7EC8E3"
    sp.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-vf", vf, "-c:a", "aac", "-b:a", "160k",
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(dst)], check=True)

def assemble(scene, film, out_9x16, out_16x9=None):
    cfg = json.load(open(scene))
    work = Path(out_9x16).resolve().parent / "_motion_work"
    work.mkdir(parents=True, exist_ok=True)
    title = cfg.get("title", "Tí và Cún")
    lesson = cfg.get("lesson", "")
    print("== intro ==")
    intro = work / "intro_9x16.mp4"
    scored_render(TEMPL / "intro.html", intro, audio=ASSETS / "jingle.wav", dur=3.6, label="intro")
    print("== title ==")
    title_c = work / "title_9x16.mp4"
    qs = f"title={quote(title)}&lesson={quote(lesson)}&ep={quote("Tập mới")}"
    scored_render(TEMPL / "title.html", title_c, audio=ASSETS / "pop.wav", dur=2.8, qs=qs, label="title")
    print("== body + subs ==")
    body = work / "body_9x16.mp4"
    # snap body internal cuts to beats of mood stem if present
    film_p = Path(film)
    stem = film_p.parent / "_stem_music.wav"
    cuts = [s["to"] for s in cfg.get("shots", [])][:-1]
    if stem.exists() and cuts:
        y, sr = load_wav(str(stem))
        beats, _ = onset_beats(y, sr)
        snapped = snap(cuts, beats)
        print("  beat-snap cuts", cuts, "→", snapped)
        # rewrite a temp scene for qc awareness only; body film already edited — optional re-edit skipped if deltas tiny
        cfg["_snapped_cuts"] = snapped
        json.dump(cfg, open(work / "scene_snapped.json", "w"), ensure_ascii=False, indent=1)
    subs_burn.burn(scene, str(film), str(body), aspect="9x16")
    print("== outro ==")
    outro = work / "outro_9x16.mp4"
    scored_render(TEMPL / "outro.html", outro, audio=ASSETS / "outro_jingle.wav", dur=3.2,
                  qs=f"lesson={quote(lesson)}", label="outro")
    print("== concat ==")
    # normalize audio sample rates before concat
    parts = []
    for p in (intro, title_c, body, outro):
        n = work / (p.stem + "_n.mp4")
        sp.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(p), "-ar", "48000", "-ac", "2",
                "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", str(n)], check=True)
        parts.append(n)
    concat(parts, out_9x16)
    if out_16x9:
        # re-render MG at 16:9 + body 16:9
        print("== 16:9 variants ==")
        intro16 = work / "intro_16x9.mp4"
        scored_render(TEMPL / "intro.html", intro16, audio=ASSETS / "jingle.wav", dur=3.6, w=1920, h=1080, label="intro16")
        title16 = work / "title_16x9.mp4"
        scored_render(TEMPL / "title.html", title16, audio=ASSETS / "pop.wav", dur=2.8, qs=qs, w=1920, h=1080, label="title16")
        body16 = work / "body_16x9.mp4"
        subs_burn.burn(scene, str(film), str(body16), aspect="16x9")
        outro16 = work / "outro_16x9.mp4"
        scored_render(TEMPL / "outro.html", outro16, audio=ASSETS / "outro_jingle.wav", dur=3.2,
                      qs=f"lesson={quote(lesson)}", w=1920, h=1080, label="outro16")
        parts16 = []
        for p in (intro16, title16, body16, outro16):
            n = work / (p.stem + "_n.mp4")
            sp.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(p), "-ar", "48000", "-ac", "2",
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", str(n)], check=True)
            parts16.append(n)
        concat(parts16, out_16x9)
    return str(out_9x16)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("scene"); ap.add_argument("film"); ap.add_argument("out")
    ap.add_argument("--also-16x9"); a = ap.parse_args()
    assemble(a.scene, a.film, a.out, a.also_16x9)
