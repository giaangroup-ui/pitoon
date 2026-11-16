# Khâu 2 – Kiểm duyệt nội dung trẻ em (Child-safety reviewer)

**Nhiệm vụ:** Đọc kịch bản như một cô giáo mẫu giáo. Chặn mọi hành động bé có thể bắt chước mà bị đau, mọi cảnh làm bé sợ, mọi câu hỗn. Khâu này đứng **trước** mọi khâu tạo hình/video để không tốn hạn mức cho kịch bản không an toàn.

**Nhận vào:** scene.json của khâu 1 · **Giao ra:** phiếu duyệt `review_02.md` (ĐẠT hoặc danh sách câu phải sửa + gợi ý thay thế)

## Checklist (tiêu chí đạt)
- [ ] `python3 tools/safety_check.py scene.json` ✅ (máy quét từ khoá Việt + Anh)
- [ ] Trên app: `safety.js` (kiểm tra ngay khi bé gõ) không còn mục chặn
- [ ] AI đọc lại toàn bộ hành động + lời thoại + prompt video theo HUONG_DAN_NOI_DUNG.md mục 2 (CẤM) – không chỉ từ khoá
- [ ] Không cảnh làm bé sợ: bóng tối đáng sợ, la hét, quái vật, bị bỏ rơi, máu
- [ ] Không thu tên thật, ảnh thật của bé; nhân vật người thật phải có sự đồng ý của phụ huynh
- [ ] Cái hài từ: hiểu lầm vui, chơi chữ lễ phép, con vật nghịch, mặt hài, đồ mềm rơi nhẹ (mục 3)
- [ ] Bài học tích cực, nói thành một câu đơn giản

## Ngưỡng ĐẠT
- 0 lỗi luật cấm (máy) **và** AI đọc lại chấm an toàn 10/10 (bất kỳ nghi ngờ nào = chưa đạt)

**Không đạt →** trả về khâu 1 Biên kịch kèm gợi ý thay thế (ví dụ: "trèo cây hái quả" → "nhờ người lớn hái giúp / hái quả ở cành thấp"). Tối đa 4 vòng, quá thì báo chủ.
