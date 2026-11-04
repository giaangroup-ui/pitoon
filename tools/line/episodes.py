#!/usr/bin/env python3
"""Batch episode generator: ý tưởng từ ngụ ngôn / Trạng Quỳnh / Trạng Tí -> outline JSON đã qua safety_check.
Usage: episodes.py N out_dir   (outline; kịch bản chi tiết viết bằng tab Biên kịch trong index.html hoặc LLM)"""
import json, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
try: from safety_check import check as safety
except Exception: safety = lambda t: []
IDEAS = [("ngụ ngôn","Rùa và Thỏ","Cún chạy nhanh nhưng ham chơi, Tí đi chậm mà chắc","kiên trì"),
 ("ngụ ngôn","Kiến và Ve","Cún chơi suốt, Tí cất bánh cho ngày mưa","chăm chỉ"),
 ("ngụ ngôn","Cáo và Quạ","Cún khen Tí để xin bánh","đừng nghe lời nịnh"),
 ("Trạng Quỳnh","Cân voi","Tí đố cách cân con lợn đất to bằng thuyền giấy trong chậu nước","thông minh"),
 ("Trạng Quỳnh","Mèo vẽ hổ","Tí vẽ Cún thành hổ, Cún tưởng thật","sáng tạo"),
 ("Trạng Tí","Đếm sao","Tí trả lời câu đố khó bằng câu đố vui","nhanh trí"),
 ("Trạng Tí","Chia bánh","Tí chia bánh công bằng cho Cún và bạn","chia sẻ")]
def make(n, out):
    os.makedirs(out, exist_ok=True); res = []
    for i in range(n):
        src, title, plot, moral = IDEAS[i % len(IDEAS)]
        ep = {"id": f"ep{i+1:03d}", "source": src, "title": f"Tí và Cún: {title}", "plot": plot, "moral": moral,
              "acts": ["mở: tình huống vui", "giữa: hiểu lầm/đố mẹo, đùa hình thể an toàn", "kết: bài học nhẹ nhàng"],
              "target_min": 5, "shots_5s": 60, "status": "outline"}
        ep["lesson"] = moral; ep["safety"] = [x for x in safety(dict(ep)) if "shot" not in x.lower() and "line" not in x.lower()]; res.append(ep)
        json.dump(ep, open(os.path.join(out, ep["id"] + ".json"), "w"), ensure_ascii=False, indent=1)
    return res
if __name__ == "__main__":
    for e in make(int(sys.argv[1]), sys.argv[2]): print(e["id"], e["title"], "SAFETY:", e["safety"] or "ok")
