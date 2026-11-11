# Trạng thái sản xuất — Hai chị em Thảo Nguyên, Thảo My và người bạn ăn xin

**Kết quả: CHƯA CÓ PHIM HOÀN CHỈNH.** Dừng chủ động vì hạn mức tuần đã dùng **97,6%** (gói Cursor Free / SuperGrok). Reset: **thứ Hai 16/11/2026 lúc 11:23 (giờ Việt Nam / Asia/Saigon)**. Không mua, không bật chi trả theo nhu cầu.

Đã kiểm tra hạn mức trước khi làm. Với phần còn lại (~2,4%), không đủ để tạo master Khang/Mẹ rồi 12 cảnh (ảnh tĩnh + video, QC và làm lại tối đa 4 vòng). Không đốt hạn mức vào nửa chừng.

## Đã hoàn thành (miễn phí, không GenerateImage/GenerateVideo)
- Đọc đủ kịch bản 12 cảnh, SCENE_PLAN, hướng dẫn sản xuất, và 3 bảng nhân vật đã duyệt.
- Cắt bible từ bảng của chủ: chân dung, góc mặt, biểu cảm, xoay 360, bust từ master.
- `bible/bible.json` — khóa ngoại hình, luật trang phục, luật phẩm giá Khang, checklist QC.
- `scene.json` — 12 cảnh, thoại + lời dẫn đã canh nhịp (~2 phút 59 giây phần thân; cộng intro/title/outro khoảng 3 phút 10 giây, trong khung 2–3 phút).
- 39 file giọng tiếng Việt (edge-tts, formant trẻ em / mẹ / người dẫn), nhạc nền nhẹ, SFX, file nghe thử `audio/_mix_preview.mp3`.
- Motion: intro / thẻ tựa / outro 16:9 (Playwright + ffmpeg), tự chấm ≥ 8,04/10, đạt.
- `produce.py queue` — hàng đợi sẵn để làm tiếp khi hạn mức reset.
- Brief master Khang và Mẹ: `KHANG_MOM_BRIEFS.md`.

## Chưa làm (cần hạn mức tạo ảnh/video)
- Ảnh master Khang và Mẹ + QC
- 12 keyframe + 12 clip video (và làm lại nếu trượt QC)
- Phim ghép ` /workspace/ref/pitoon_free/thao_sisters_16x9.mp4 `, bản 9:16, contact sheet toàn phim, báo cáo qc.py

## Khi reset hạn mức
1. Kiểm tra lại hạn mức tuần.
2. Tạo master Khang rồi Mẹ, QC đạt mới vào S01.
3. Làm tuần tự S01→S12 theo `produce.py queue` và `SCENE_PLAN.json`.
4. Hết hạn mức thì dừng ở cảnh đã QC đạt, không làm dở.
5. `assemble_film.py` + motion + phụ đề + `qc.py`.
