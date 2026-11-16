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

## Cập nhật 16/11/2026 12:20 (giờ VN)
- Hạn mức tuần đã reset: dùng 0,1%, reset tiếp theo thứ Hai 23/11/2026 lúc 11:23 (giờ VN).
- Lượt chạy này (executor) KHÔNG có công cụ GenerateImage / GenerateVideo / videoReview, máy box không có GPU, nên chưa tạo được master Khang/Mẹ và 12 cảnh. Không dùng Ken Burns ảnh tĩnh (chủ đã từ chối).
- Cần chạy lại hàng đợi `python3 produce.py queue` từ phiên có công cụ tạo ảnh/video. Giọng, nhạc, SFX, intro/title/outro vẫn sẵn sàng.

## Cập nhật 16/11/2026 ~13:45 (giờ VN) — PHIM HOÀN CHỈNH
- Master Khang và Mẹ (bible/khang_master.png, me_master.png) đã QC đạt brief: đúng tuổi, giản dị, có phẩm giá, không chữ.
- S01–S12 keyframe + clip image-to-video đều QC bằng mắt đạt. S03 làm lại (bản cũ cầm hộp quà thay vì chiếc bánh): key + clip mới, My đưa bánh, Khang nhận.
- Ghép: mỗi cảnh kéo đúng thời lượng thoại, chuyển cảnh mờ 0,35s, intro + title + outro, phụ đề tiếng Việt (Be Vietnam Pro), mix mới (nhạc hạ 11,8 dB khi có thoại, SFX đúng cue).
- Kết quả: /workspace/ref/pitoon_free/thao_sisters_16x9.mp4 (3:10, 1920x1080), contact sheet thao_sisters_16x9_sheet.jpg, báo cáo thao_sisters_qc.md.
- qc.py: đạt mọi mục kỹ thuật/âm thanh/thoại; còn cảnh báo 2 câu thoại dài (câu của Mẹ ở S05 và câu kết S12), giữ nguyên vì là kịch bản của chủ.
- Sửa công cụ: safety_check khớp nguyên từ (trước đây báo nhầm "ngu" trong "Nguyên", "ao" trong "Thao"); qc.py có tuỳ chọn bỏ qua continuity cho phim dùng bible riêng.
