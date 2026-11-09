# PiToon motion graphics (HTML → Playwright → ffmpeg)
Miễn phí, không API trả phí.

- `templates/intro.html` – intro 3.6s logo + series + Tí/Cún (spring physics)
- `templates/title.html` – thẻ tựa tập
- `templates/subs.html` – phụ đề tiếng Việt word-pop (vùng an toàn 9:16)
- `templates/outro.html` – "Nhớ follow PiToon nhé!" + bài học
- `render.py` – render từng khung bằng Chromium headless
- `score.py` – chấm 1–10 (overlap, text clip, jerk, readability, brand); <8 → làm lại
- `beats.py` – bắt beat nhạc, snap điểm cắt
- `subs_burn.py` – đốt phụ đề lên phim theo `scene.json`
- `assemble.py` – intro + title + body+subs + outro → 9:16 và 16:9

Ví dụ:
```
python3 assemble.py ../../ref/pitoon_free/v7/scene.json \
  ../../ref/pitoon_free/canh_mau_v7.mp4 \
  ../../ref/pitoon_free/canh_mau_v8_9x16.mp4 \
  --also-16x9 ../../ref/pitoon_free/canh_mau_v8_16x9.mp4
```
