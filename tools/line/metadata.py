#!/usr/bin/env python3
"""Tiêu đề/chú thích/hashtag tiếng Việt cho 6 nền tảng + YouTube 'dành cho trẻ em' + nhãn nội dung AI.
Chỉ tạo NHÁP để chủ duyệt – KHÔNG tự đăng. Usage: metadata.py EP_or_scene.json out.json"""
import json, sys
def gen(ep, files=None, dur=None):
    t = ep.get("title", "Phim PiToon"); m = ep.get("moral") or ep.get("lesson", "")
    tags = ["#PiToon", "#hoathinh", "#phimhoathinh3D", "#truyenthieunhi", "#beyeuhoc"]
    if "Tí" in t or "Cún" in t: tags.append("#TiVaCun")
    if "Quỳnh" in ep.get("source", "") or "Quỳnh" in t: tags.append("#TrangQuynh")
    if ep.get("source") == "ngụ ngôn": tags.append("#ngungon")
    d = f"{t} – phim hoạt hình 3D vui nhộn cho bé 3–10 tuổi." + (f" Bài học: {m}" if m else "") + " Ba mẹ xem cùng bé nhé!"
    ai = "Phim làm bằng công cụ AI, có người lớn kiểm duyệt."
    f = files or {"v": "vertical_9x16.mp4", "h": "youtube_16x9.mp4", "tv": "thumb_9x16.jpg", "th": "thumb_16x9.jpg", "srt": "subs.srt"}
    short_ok = dur is None or dur <= 180
    return {"status": "NHÁP – chờ chủ duyệt, KHÔNG tự đăng", "title": t, "lesson": m, "duration_s": dur, "hashtags": tags,
     "tiktok": {"caption": f"{t} 🐜 {m} " + " ".join(tags[:5]), "file": f["v"], "cover": f["tv"], "ai_generated_label": True, "visibility": "private"},
     "instagram_reels": {"caption": d + "\n" + ai + "\n" + " ".join(tags), "file": f["v"], "cover": f["tv"], "ai_label": True, "reach_new_audience": short_ok},
     "facebook": {"caption": d + "\n" + ai + "\n" + " ".join(tags[:4]), "file_reels": f["v"], "file_video": f["h"], "ai_label": True},
     "youtube_shorts": {"title": (t + " #Shorts")[:100], "description": d + "\n" + ai + "\n" + " ".join(tags), "file": f["v"], "eligible": short_ok,
                        "madeForKids": True, "selfDeclaredMadeForKids": True, "containsSyntheticMedia": True, "privacyStatus": "private"},
     "youtube": {"title": t[:100], "description": d + "\n" + ai + "\n" + " ".join(tags), "tags": [x[1:] for x in tags], "file": f["h"], "thumbnail": f["th"],
                 "captions": f["srt"], "madeForKids": True, "selfDeclaredMadeForKids": True, "privacyStatus": "private", "categoryId": "1",
                 "defaultLanguage": "vi", "containsSyntheticMedia": True},
     "zalo": {"caption": f"{t} – {m}".strip(" –"), "file": f["v"], "note": "Zalo chưa công bố thông số; dùng bản 9:16 như TikTok"}}
if __name__ == "__main__":
    json.dump(gen(json.load(open(sys.argv[1]))), open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
