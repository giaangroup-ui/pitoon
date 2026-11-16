# Dây chuyền PiToon (line/)
1. series_bible.json – cast + set cố định (tái dùng → đồng bộ rẻ).
2. `episodes.py N dir` – outline tập từ ngụ ngôn/Trạng Quỳnh/Trạng Tí, chạy safety_check.
3. `queue.py add dir/ep001.json` – 60 shot 5s/tập; trạng thái pending→generated→qc_pass/qc_fail (≤4 lần)→rejected.
4. Trợ lý tạo hình/video (GenerateImage/GenerateVideo) theo `batch_runner.py jobs`, rồi `queue.py mark`.
5. `batch_runner.py finish scene_dir [--publish]` – lồng tiếng/SFX/nhạc → `studio_runner.py check` (Tổng kiểm duyệt: lỗi trả về đúng khâu, mỗi khâu ≤ 4 vòng rồi báo chủ) → đóng gói khi đạt.
   `studio_runner.py script|set|check|approve|publish` cập nhật bảng công khai `studio/status.json` → trang `xuongphim.html`.
6. `export.py scene.json film.mp4 out` – 9:16 + 16:9, −14 LUFS/≤ −1 dBTP, phụ đề vùng an toàn, 2 ảnh bìa, kiểm tra gói. 7. `metadata.py` – nháp tiêu đề/mô tả/hashtag, YouTube made-for-kids.
Đăng: chỉ NHÁP/riêng tư, chủ duyệt rồi mới công khai.
