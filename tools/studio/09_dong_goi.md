# Khâu 9 – Đóng gói đa nền tảng (Packager)

**Nhiệm vụ:** Từ phim đã dựng, xuất đúng chuẩn từng nơi đăng. **Chỉ tạo NHÁP** – không bao giờ tự đăng; chủ duyệt rồi mới đăng.

**Lệnh:** `python3 tools/line/export.py scene.json film.mp4 out_dir` (tự chạy kiểm tra gói, ghi `out_dir/package_qc.json`)

**Giao ra (out_dir):**
| File | Dùng cho |
|---|---|
| `vertical_9x16.mp4` (1080×1920) | TikTok, Reels Instagram/Facebook, YouTube Shorts, Zalo |
| `youtube_16x9.mp4` (1920×1080) | YouTube, Facebook video |
| `subs.srt` | phụ đề rời cho YouTube/Facebook |
| `thumb_16x9.jpg` (1280×720), `thumb_9x16.jpg` (1080×1920) | ảnh bìa có tựa phim |
| `metadata.json` | tựa, chú thích, hashtag nháp cho 6 nền tảng; YouTube "dành cho trẻ em" + khai báo nội dung AI |

## Checklist / Ngưỡng ĐẠT (máy đo)
- [ ] H.264 High + AAC 48 kHz, MP4 faststart; đúng 1080×1920 và 1920×1080
- [ ] Âm lượng **−14 LUFS ±1**, đỉnh thật **≤ −1 dBTP** (chuẩn hoá 2 lượt bằng loudnorm)
- [ ] Phụ đề đốt vào hình nằm trong vùng an toàn chung 9:16: cách trên 288, dưới 672, trái 65, phải 192 px (khung 1080×1920); bản 16:9 cách dưới ≥ 60 px
- [ ] Bản 9:16 ≤ 180 giây để lên Shorts và tới người mới trên Reels (dài hơn: chỉ đăng YouTube/Facebook thường)
- [ ] 2 ảnh bìa đúng kích thước; metadata có `madeForKids`, nhãn nội dung AI, trạng thái NHÁP/riêng tư

| Nền tảng | File | Độ dài nên dùng | Ghi chú |
|---|---|---|---|
| TikTok | 9:16 | 1–2 phút | bật nhãn nội dung AI |
| Reels (IG/FB) | 9:16 | < 3 phút | IG tự đưa về ~−14 LUFS |
| YouTube Shorts | 9:16 | ≤ 3 phút | dành cho trẻ em, khai báo AI |
| YouTube | 16:9 | ≤ 15 phút (kênh chưa xác minh) | ảnh bìa 1280×720 |
| Facebook video | 16:9 hoặc 9:16 | 1–3 phút | |
| Zalo | 9:16 | 1–2 phút | chưa có thông số chính thức, dùng bản TikTok |

**Không đạt →** tự sửa (xuất lại). Lỗi do phim gốc (quá dài, thiếu thoại) → trả về khâu 1/8.
