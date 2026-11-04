#!/usr/bin/env python3
"""Batch runner skeleton. Bước tạo hình/video (GenerateImage/GenerateVideo) là công cụ của trợ lý, không gọi được từ script:
runner in ra 'job' cho trợ lý, trợ lý chạy rồi `queue.py mark`. Phần còn lại (âm thanh, dựng, QC, export, metadata) tự động."""
import json, os, subprocess as sp, sys
H = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(H)
def jobs(n=10):
    sys.path.insert(0, H); import queue as Qm
    out = []
    for s in Qm.load()["shots"]:
        if s["state"] in ("pending", "qc_fail") and len(out) < n: out.append(s["id"])
    return out
def finish(scene_dir):
    sc = os.path.join(scene_dir, "scene.json"); cfg = json.load(open(sc)); film = os.path.join(scene_dir, cfg["out"])
    sp.run([sys.executable, os.path.join(T, "pitoon_pipeline.py"), sc], check=True, cwd=scene_dir)
    ok = sp.run([sys.executable, os.path.join(T, "studio", "qc.py"), sc, film, "--report", os.path.join(scene_dir, "qc.md")], cwd=scene_dir).returncode == 0
    if not ok: print("QC TRẢ VỀ – không export"); return False
    sp.run([sys.executable, os.path.join(H, "export.py"), film, os.path.join(scene_dir, "export")], check=True)
    return True
if __name__ == "__main__":
    if sys.argv[1] == "jobs": print("\n".join(jobs()))
    elif sys.argv[1] == "finish": finish(sys.argv[2])
