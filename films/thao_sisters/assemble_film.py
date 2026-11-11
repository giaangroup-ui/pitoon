#!/usr/bin/env python3
"""When all scene videos exist: concat body, mux prepared audio, add motion intro/title/outro, burn subs, export 16:9 (9:16 optional)."""
import json, os, subprocess as sp, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
cfg=json.load(open(ROOT/"scene.json"))
missing=[s["id"] for s in cfg["shots"] if not (ROOT/s["video"]).exists()]
if missing:
    print("Chưa đủ video, thiếu:", ", ".join(missing)); sys.exit(2)
# concat body video (xfade optional later)
lst=ROOT/"export"/"body.txt"
lst.parent.mkdir(exist_ok=True)
# normalize each then concat
parts=[]
for s in cfg["shots"]:
    n=ROOT/"export"/f"{s['id']}_n.mp4"
    sp.run(["ffmpeg","-loglevel","error","-y","-i",str(ROOT/s["video"]),
            "-r","24","-s","1920x1080","-c:v","libx264","-pix_fmt","yuv420p","-an",str(n)],check=True)
    parts.append(n)
lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
body=ROOT/"export"/"body.mp4"
sp.run(["ffmpeg","-loglevel","error","-y","-f","concat","-safe","0","-i",str(lst),"-c","copy",str(body)],check=True)
# mux prepared mix
body_a=ROOT/"export"/"body_a.mp4"
mix=ROOT/"audio"/"_mix_preview.wav"
sp.run(["ffmpeg","-loglevel","error","-y","-i",str(body),"-i",str(mix),"-map","0:v","-map","1:a",
        "-c:v","copy","-c:a","aac","-shortest",str(body_a)],check=True)
print("body+audio", body_a)
print("Tiếp: ráp intro/title/outro (export/*_16x9.mp4), đốt phụ đề bằng tools/motion/subs_burn.py, chạy qc.py")
