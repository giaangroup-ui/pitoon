#!/usr/bin/env python3
"""Tiêu đề/mô tả/hashtag tiếng Việt cho từng nền tảng + cài đặt YouTube 'made for kids'. Chỉ tạo NHÁP để chủ duyệt.
Usage: metadata.py EP.json out.json"""
import json, sys
def gen(ep):
    t, m = ep["title"], ep.get("moral", "")
    tags = ["#hoathinh", "#truyenthieunhi", "#TiVaCun", "#phimhoathinh3D", "#beyeuhoc"] + (["#TrangQuynh"] if "Quỳnh" in ep.get("source", "") else []) + (["#ngungon"] if ep.get("source") == "ngụ ngôn" else [])
    d = f'{t} – phim hoạt hình 3D vui nhộn cho bé 3–10 tuổi. Bài học: {m}. Ba mẹ xem cùng bé nhé!'
    return {"status": "DRAFT – chờ chủ duyệt, KHÔNG tự đăng",
     "youtube": {"title": t[:100], "description": d + "\n" + " ".join(tags), "tags": [x[1:] for x in tags], "madeForKids": True,
                 "selfDeclaredMadeForKids": True, "privacyStatus": "private", "categoryId": "1", "defaultLanguage": "vi", "containsSyntheticMedia": True},
     "tiktok": {"caption": f"{t} 🐶 " + " ".join(tags[:5]), "ai_generated_label": True, "file": "vertical_9x16.mp4"},
     "facebook_reels": {"caption": d + " " + " ".join(tags[:4]), "file": "vertical_9x16.mp4"},
     "zalo_video": {"caption": f"{t} – {m}", "file": "vertical_9x16.mp4"}}
if __name__ == "__main__":
    json.dump(gen(json.load(open(sys.argv[1]))), open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
