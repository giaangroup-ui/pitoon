#!/usr/bin/env python3
"""Burn bouncy Vietnamese word-pop subtitles onto a film using per-line HTML renders, timed from scene.json.
Usage: subs_burn.py scene.json film.mp4 out.mp4 [--aspect 9x16|16x9]"""
import json, os, subprocess as sp, sys, tempfile
from urllib.parse import quote
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from render import render

def burn(scene, film, out, aspect="9x16"):
    cfg=json.load(open(scene)); lines=cfg.get("lines",[])
    w,h=(1080,1920) if aspect=="9x16" else (1920,1080)
    # prepare base: letterbox/pillarbox film into target aspect
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); base=td/"base.mp4"
        if aspect=="9x16":
            vf="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
        else:
            vf="scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
        sp.run(["ffmpeg","-loglevel","error","-y","-i",film,"-vf",vf,"-c:a","copy",str(base)],check=True)
        # render each line as transparent-ish clip then overlay
        # Chromium screenshots are opaque; we chroma-key near-white bg → use dark-clear trick:
        # render on green screen then colorkey.
        overlays=[]
        for i,l in enumerate(lines):
            html=HERE/"templates"/"subs.html"
            # temporarily make body green for key
            # pass via qs; modify: write a keyed variant
            start,end=l["win"]; text=l["text"]
            clip=td/f"sub{i}.mp4"
            # green-screen version of subs.html via data URL params — patch body bg
            keyed=td/f"subs{i}.html"
            src=(HERE/"templates"/"subs.html").read_text()
            src=src.replace("background:transparent","background:#00FF00")
            keyed.write_text(src)
            # copy deps
            for dep in ("base.css",):
                if not (td/dep).exists(): (td/dep).write_text((HERE/"templates"/dep).read_text())
            qs=f"text={quote(text)}&start=0&end={end-start:.2f}"
            # use file url with qs
            render(keyed, clip, w=w, h=h, fps=24, dur=end-start+.15, qs=qs)
            overlays.append((clip, start, end-start+.15))
        # build filter
        # [0] base; overlay each with enable
        inputs=["-i",str(base)]
        fc=[]; last="0:v"
        for i,(clip,start,dur) in enumerate(overlays):
            inputs+=["-i",str(clip)]
            # colorkey green then overlay
            fc.append(f"[{i+1}:v]colorkey=0x00FF00:0.3:0.2,format=rgba[s{i}]")
            outl=f"v{i}"
            fc.append(f"[{last}][s{i}]overlay=0:0:enable='between(t,{start:.3f},{start+dur:.3f})'[{outl}]")
            last=outl
        filt=";".join(fc)
        cmd=["ffmpeg","-loglevel","error","-y",*inputs,"-filter_complex",filt,"-map",f"[{last}]",
             "-map","0:a?","-c:v","libx264","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-shortest",str(out)]
        sp.run(cmd,check=True)
    return str(out)

if __name__=="__main__":
    burn(sys.argv[1],sys.argv[2],sys.argv[3], sys.argv[4] if len(sys.argv)>4 else "9x16")
