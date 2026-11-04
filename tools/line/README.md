# Dây chuyền PiToon (line/)
1. series_bible.json – cast + set cố định (tái dùng → đồng bộ rẻ).
2. `episodes.py N dir` – outline tập từ ngụ ngôn/Trạng Quỳnh/Trạng Tí, chạy safety_check.
3. `queue.py add dir/ep001.json` – 60 shot 5s/tập; trạng thái pending→generated→qc_pass/qc_fail (≤4 lần)→rejected.
4. Trợ lý tạo hình/video (GenerateImage/GenerateVideo) theo `batch_runner.py jobs`, rồi `queue.py mark`.
5. `batch_runner.py finish scene_dir` – lồng tiếng/SFX/nhạc → qc.py → export (chỉ khi QC đạt).
6. `export.py` – 16:9 YouTube, 9:16 TikTok/Reels/Zalo, thumbnail. 7. `metadata.py` – nháp tiêu đề/mô tả/hashtag, YouTube made-for-kids.
Đăng: chỉ NHÁP/riêng tư, chủ duyệt rồi mới công khai.
