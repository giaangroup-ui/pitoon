#!/usr/bin/env python3
"""Self-review: sample frame grid, score 1–10 for overlap / text-clip / jerk / readability / off-brand.
Re-render recommended if mean < 8. Usage: score.py clip.mp4 [--report out.md]"""
import argparse, json, os, subprocess as sp, tempfile
from pathlib import Path
import numpy as np
try:
    from PIL import Image, ImageStat, ImageFilter
except ImportError:
    import subprocess; subprocess.check_call(["pip","install","-q","pillow"]); from PIL import Image, ImageStat, ImageFilter

PALETTE = np.array([[0x2B,0x3F,0xA0],[0xE2,0xB0,0x4A],[0x7E,0xC8,0xE3],[0xFF,0xE0,0x8A],[0xFF,0x6B,0x9A],[0x7E,0xD9,0x57],[255,255,255]], float)

def frames(path, n=12):
    with tempfile.TemporaryDirectory() as td:
        sp.run(["ffmpeg","-loglevel","error","-y","-i",path,"-vf",f"fps=3,scale=270:-1","-frames:v",str(n),f"{td}/f%03d.png"], check=True)
        return [Image.open(f"{td}/f{i:03d}.png").convert("RGB") for i in range(1, n+1) if os.path.exists(f"{td}/f{i:03d}.png")]

def score_clip(path):
    fr = frames(path)
    if not fr:
        return {"file":path,"scores":{k:1 for k in ("jerk","readability","text_clip","brand","overlap")},"mean":1,"pass":False,"grid":None,"raw":{}}
    arr = [np.asarray(im, float) for im in fr]
    # jerk: mean abs frame-to-frame (too high = jerky cut; too low across many = freeze)
    diffs = [np.abs(arr[i]-arr[i-1]).mean() for i in range(1,len(arr))]
    jerk = float(np.mean(diffs)) if diffs else 0
    # text-ish: high-contrast small regions near bottom third (subs) – crude edge density
    edge = []
    for im in fr:
        e = im.convert("L").filter(ImageFilter.FIND_EDGES)
        a = np.asarray(e, float); h=a.shape[0]; edge.append(a[int(h*.7):].mean())
    edge_m = float(np.mean(edge))
    # clipping proxy: bright/dark crush at borders
    border = []
    for a in arr:
        b = np.concatenate([a[:4].ravel(), a[-4:].ravel(), a[:,:4].ravel(), a[:,-4:].ravel()])
        border.append(((b<5)|(b>250)).mean())
    clip = float(np.mean(border))
    # brand palette distance (lower = more on-brand)
    brand = []
    for a in arr:
        s = a.reshape(-1,3)[::40]
        d = np.linalg.norm(s[:,None,:]-PALETTE[None,:,:], axis=2).min(axis=1).mean()
        brand.append(d)
    brand_d = float(np.mean(brand))
    # overlap proxy: saturated center mass vs edges (characters colliding with logo?)
    sat = []
    for a in arr:
        c = a[a.shape[0]//4:3*a.shape[0]//4, a.shape[1]//4:3*a.shape[1]//4]
        sat.append(c.std())
    # scores 1-10
    def clamp(x,lo,hi): return max(1,min(10,x))
    # calibrated on PiToon MG: holds after bounce are fine (low jerk OK if >0.3)
    s_jerk = clamp(10 - max(0, 0.4-jerk)*8 - max(0, jerk-25)/3, 1, 10)
    s_read = clamp(5 + edge_m/7, 1, 10)                   # logo/title edges
    s_clip = clamp(10 - clip*60, 1, 10)
    s_brand = clamp(10 - max(0, brand_d-30)/7, 1, 10)    # photo bg shifts baseline ~25-45
    s_overlap = clamp(10 - max(0, float(np.mean(sat))-45)/8, 1, 10)
    scores = {"jerk":round(s_jerk,1),"readability":round(s_read,1),"text_clip":round(s_clip,1),
              "brand":round(s_brand,1),"overlap":round(s_overlap,1)}
    mean = round(sum(scores.values())/len(scores), 2)
    # grid contact sheet
    sheet = Path(path).with_suffix("").as_posix()+"_scoregrid.jpg"
    sp.run(["ffmpeg","-loglevel","error","-y","-i",path,"-vf","fps=1,scale=240:-1,tile=4x3","-frames:v","1",sheet], check=False)
    return {"file":path,"scores":scores,"mean":mean,"pass":bool(mean>=8),"grid":sheet if os.path.exists(sheet) else None,
            "raw":{"jerk":float(jerk),"edge":float(edge_m),"clip":float(clip),"brand_d":float(brand_d)}}

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("clip"); ap.add_argument("--report")
    a=ap.parse_args(); r=score_clip(a.clip); print(json.dumps(r,ensure_ascii=False,indent=1))
    if a.report:
        lines=["# Motion score\n",f"**Mean {r['mean']}/10 – {'ĐẠT' if r['pass'] else 'TRẢ VỀ'}**\n",
               "| Hạng mục | Điểm |\n|---|---|\n"]+[f"| {k} | {v} |\n" for k,v in r["scores"].items()]
        open(a.report,"w").writelines(lines)
