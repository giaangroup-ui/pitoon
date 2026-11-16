# PiToon Studio – 10 khâu, có Tổng kiểm duyệt

1 Biên kịch → 2 Kiểm duyệt nội dung trẻ em → 3 Nhân vật, bối cảnh (bible) → 4 Đạo diễn phân cảnh → 5 Hoạt hình/Video → 6 Lồng tiếng, khớp môi → 7 Âm thanh, nhạc → 8 Dựng phim → 9 Đóng gói đa nền tảng → **10 Tổng kiểm duyệt**.

Mỗi khâu có brief `NN_*.md` (checklist + ngưỡng đo được). Danh sách khâu và ngưỡng nằm ở `stages.py` (một chỗ duy nhất).
Tổng kiểm duyệt trả về **đúng khâu** có lỗi (cột "Khâu" trong qc.md); mỗi khâu tối đa 4 vòng, quá thì "Cần chủ xem".
Chỉ bản ĐẠT 100% mới thành "Chờ chủ duyệt". **Không bao giờ tự đăng.**

Lệnh:
```
python3 tools/safety_check.py scene.json                          # khâu 1–2
python3 tools/pitoon_pipeline.py scene.json --plan                # lệnh tạo ảnh/video từng shot (khâu 3–5)
python3 tools/pitoon_pipeline.py scene.json                       # ghép + âm thanh (khâu 6–8)
python3 tools/studio/qc.py scene.json film.mp4 --report qc.md --json qc.json
python3 tools/line/studio_runner.py check FILM_DIR [--publish]    # cả dây chuyền: QC → trả về / đóng gói → bảng Xưởng phim
```
