#!/usr/bin/env python3
"""10 khâu của PiToon Studio (dùng chung cho qc.py, line/studio_runner.py và bảng 'Xưởng phim').
Mỗi hạng mục QC thuộc đúng một khâu; Tổng kiểm duyệt trả lỗi về khâu đó."""
STAGES = [
    (1, "bien_kich", "Biên kịch", "01_bien_kich.md"),
    (2, "kiem_duyet", "Kiểm duyệt nội dung trẻ em", "02_kiem_duyet_tre_em.md"),
    (3, "thiet_ke", "Nhân vật, bối cảnh", "03_thiet_ke.md"),
    (4, "phan_canh", "Đạo diễn phân cảnh", "04_phan_canh.md"),
    (5, "hoat_hinh", "Hoạt hình / Video", "05_hoat_hinh.md"),
    (6, "long_tieng", "Lồng tiếng, khớp môi", "06_long_tieng.md"),
    (7, "am_thanh", "Âm thanh, nhạc", "07_am_thanh.md"),
    (8, "dung_phim", "Dựng phim", "08_dung_phim.md"),
    (9, "dong_goi", "Đóng gói đa nền tảng", "09_dong_goi.md"),
    (10, "tong_kiem_duyet", "Tổng kiểm duyệt", "10_tong_kiem_duyet.md"),
]
NAME = {n: name for n, _, name, _ in STAGES}
MAX_ROUNDS = 4          # quá 4 vòng trả về ở một khâu -> báo chủ
# Ngưỡng (đã hiệu chỉnh trên clip mẫu Tí & Cún v7 = ĐẠT và Hai chị em v1 = TRẢ VỀ)
T = {
    "motion_film": 4.5,      # điểm chuyển động trung bình cả phim (v7 5.64, hai chị em v1 1.65)
    "motion_shot": 1.2,      # cảnh yên nhất cũng phải ≥ 1.2 (v7 thấp nhất 1.55 cảnh thoại; hai chị em v1 0.85)
    "static_pct": 5.0,       # % số giây gần như đứng yên (< 0.6) tối đa
    "freeze_s": 1.0,         # đứng hình tối đa (không cho nới)
    "shot_len": (2.5, 5.2),  # độ dài mỗi cảnh (giây)
    "whisper": 0.80,         # khớp lời từng câu
    "line_words": 10,        # số từ tối đa mỗi câu thoại (trừ người dẫn)
    "narration_max": 3,      # tối đa 3 câu dẫn
    "sfx_per_s": 0.3,        # mật độ tiếng động
    "duck_db": 4.0,
    "film_lufs": (-18, -14), # mix phim gốc
    "pkg_lufs": (-15, -13),  # bản đăng: −14 ±1 LUFS
    "pkg_tp": -1.0,          # đỉnh thật ≤ −1 dBTP
    "short_max_s": 180,      # Shorts / Reels tới người mới
}
NARRATOR = {"người dẫn", "người dẫn chuyện", "narrator", "dẫn chuyện"}
