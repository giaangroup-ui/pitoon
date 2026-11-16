# Khâu 5 – Hoạt hình & video (Animation/Video)

**Nhiệm vụ:** Chạy --plan, gọi GenerateImage keyframe + GenerateVideo từng shot, nối bằng khung cuối

## Checklist (tiêu chí đạt)
- [ ] Luôn kèm 3 ảnh tham chiếu + mô tả khoá + luật an toàn
- [ ] Xem lưới khung hình mỗi shot: nhân vật đúng model sheet, đạo cụ đúng (ghế đẩu không thành băng ghế), không có người/vật lạ
- [ ] Chuyển động sống động, an toàn: lời mô tả là hành động cụ thể kiểu hoạt hình (rón rén, mắt tròn xoe, chạy vòng), KHÔNG ghi 'chỉ thở và chớp mắt'
- [ ] Nhân vật nói câu thoại ngay trong video (`src: native`, câu tiếng Việt trong prompt, 'big mouth movements')

**Ngưỡng máy (qc.py):** điểm chuyển động cả phim ≥ 4,5 (mẫu Tí & Cún 5,6) và mỗi cảnh ≥ 1,2 · 100% câu thoại do nhân vật nói trong video.
- [ ] Tối đa 4 lần làm lại/shot; giữ bản tốt nhất

**Đạt khi:** tất cả mục được tick. Không đạt → sửa và nộp lại cho QC.
