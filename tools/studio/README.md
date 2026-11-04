# PiToon Studio – quy trình nhà sản xuất

Biên kịch → Thiết kế (bible) → Phân cảnh/liên tục → Dựng hình (video) → Lồng tiếng → Âm thanh & nhạc → Dựng phim → **QC đạo diễn**.
QC trả về đúng khâu khi có mục ❌; lặp lại đến khi tất cả ✅ (tối đa ~4 vòng/shot). Chỉ bản ĐẠT mới giao chủ.

Lệnh:
```
python3 tools/safety_check.py scene.json
python3 tools/pitoon_pipeline.py scene.json --plan      # lệnh tạo ảnh/video từng shot
python3 tools/pitoon_pipeline.py scene.json             # ghép + âm thanh
python3 tools/studio/qc.py scene.json film.mp4 --report qc.md
```
