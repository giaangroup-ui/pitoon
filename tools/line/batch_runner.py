#!/usr/bin/env python3
"""Batch runner skeleton. Bước tạo hình/video (GenerateImage/GenerateVideo) là công cụ của trợ lý, không gọi được từ script:
runner in ra 'job' cho trợ lý, trợ lý chạy rồi `queue.py mark`. Phần còn lại (âm thanh, dựng, Tổng kiểm duyệt có vòng trả về, đóng gói, metadata) tự động qua studio_runner.py."""
import json, os, subprocess as sp, sys
H = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(H)
def jobs(n=10):
    sys.path.insert(0, H); import queue as Qm
    out = []
    for s in Qm.load()["shots"]:
        if s["state"] in ("pending", "qc_fail") and len(out) < n: out.append(s["id"])
    return out
def finish(scene_dir, publish=False):
    """Ghép âm thanh (khâu 6–8) rồi giao Tổng kiểm duyệt (studio_runner.check): trả về đúng khâu hoặc đóng gói NHÁP. Không tự đăng."""
    sc = os.path.join(scene_dir, "scene.json")
    sp.run([sys.executable, os.path.join(T, "pitoon_pipeline.py"), sc], check=True, cwd=scene_dir)
    sys.path.insert(0, H); import studio_runner as SR
    ok = SR.check(scene_dir)
    if publish: SR.publish()
    print("ĐẠT – chờ chủ duyệt" if ok else "QC TRẢ VỀ – xem qc.md, bảng Xưởng phim"); return ok
if __name__ == "__main__":
    if sys.argv[1] == "jobs": print("\n".join(jobs()))
    elif sys.argv[1] == "finish": finish(sys.argv[2], "--publish" in sys.argv)
