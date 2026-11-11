#!/usr/bin/env python3
"""Resume production after weekly usage resets.
Does NOT call GenerateImage/GenerateVideo (those are assistant tools).
Prints the exact queue: masters first, then S01..S12 keyframe → video → QC.
When videos exist, assemble with pitoon_pipeline + motion intro/title/outro + subs.
"""
import json, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BIBLE=ROOT/"bible"
cfg=json.load(open(ROOT/"scene.json"))

def status():
    kh=BIBLE/"khang_master.png"; me=BIBLE/"me_master.png"
    print("Khang master:", "CÓ" if kh.exists() else "THIẾU")
    print("Mẹ master:   ", "CÓ" if me.exists() else "THIẾU")
    for s in cfg["shots"]:
        key=ROOT/s["key"]; vid=ROOT/s["video"]
        print(f"  {s['id']} key={'OK' if key.exists() else '—'}  vid={'OK' if vid.exists() else '—'}  {s['title']} ({s['to']-s['from']:.1f}s)")

def queue():
    print("# Hàng đợi (bám SCENE_PLAN + bible)")
    print("1. GenerateImage Khang master (xem KHANG_MOM_BRIEFS.md). QC rồi lưu bible/khang_master.png")
    print("2. GenerateImage Mẹ master. QC rồi lưu bible/me_master.png")
    print("3. Mỗi cảnh S01–S12:")
    print("   - GenerateImage 16:9 với image_prompt_en + ref: TWO_SISTERS_APPROVED_MASTER + chân dung/360 + Khang/Mẹ nếu có trong cảnh")
    print("   - QC mặt, kính, tóc, đồ, tay, tuổi (xem bible.qc_checklist). Làm lại tối đa 4 vòng.")
    print("   - GenerateVideo từ keyframe + motion_prompt_en, 16:9, ~5–10s (nếu tool giới hạn 5s: ghép 2 clip hoặc giữ khung cuối dưới thoại)")
    print("   - QC chuyển động, đồng bộ, phẩm giá Khang.")
    print("4. python3 assemble_film.py  → intro+title+body+subs+outro, qc.py, contact sheet")
    print("Không mua, không bật gói trả phí. Hết hạn mức thì dừng ở cảnh đã QC đạt.")

if __name__=="__main__":
    cmd=sys.argv[1] if len(sys.argv)>1 else "status"
    {"status":status, "queue":queue}[cmd]()
