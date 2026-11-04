# PiToon – pipeline miễn phí (chạy trên máy)
1. Ảnh nhân vật / khung hình đầu: GenerateImage (prompt có mô tả KHAN – khăn xếp cứng, hình trụ thấp, nếp xếp song song, đỉnh phẳng, KHÔNG phải turban).
2. Clip: GenerateVideo (image-to-video, 15s, 720p). Trong prompt ghi rõ thời điểm nhân vật nói và câu thoại, ví dụ "0-4s: cậu bé nói với miệng cử động rõ: '...' rồi ngậm miệng".
3. `python3 tools/pitoon_pipeline.py scene.json` (cần ffmpeg, edge-tts, numpy):
   - giọng edge-tts tiếng Việt (NamMinh/HoaiMy) + cao độ/tốc độ/âm lượng theo vai (trẻ em, ông bà) và cảm xúc (`emo`);
   - tự dò đoạn miệng nói trong âm thanh gốc của clip (trong khung `win`), co giãn câu thoại (giữ cao độ) cho khớp miệng;
   - giữ tiếng động gốc (nước bắn, chó sủa), tắt tiếng nói gốc; nhạc nền vui tự tạo, tự hạ nhạc khi có thoại; chuẩn hoá âm lượng −16 LUFS.
Ví dụ: tools/scene_mau.json → /workspace/ref/pitoon_free/canh_mau_v2.mp4

## v3 (scene.json có lớp âm thanh)
- `lines[].src`: `native` (giữ giọng nói khớp môi do GenerateVideo tạo – khớp nhất, giọng hợp nhân vật), `edge` (edge-tts + đổi formant để thành giọng trẻ em/ông bà), `piper` (Piper vi_VN, đặt model vào tools/piper/).
- `sfx`: [{t, name, gain, len}] – file trong tools/sfx hoặc tiếng tổng hợp (whoosh, boing, slide_down/up, pop, thud, twinkle, zip).
- `ambience`: birds / wind / wind_synth / rain_synth, có from/to.
- `mood`: [{t, mood}] playful | chase | surprise | sad | happy | tense | sneaky – đổi nhạc đúng phách theo `bpm`.
- Prompt GenerateVideo nên ghi: squash-and-stretch, anticipation/overshoot, máy quay whip-pan/push-in, mốc thời gian từng hành động và câu thoại trong ngoặc kép.
Ví dụ: tools/scene_mau_v3.json → /workspace/ref/pitoon_free/canh_mau_v3.mp4

## v4 – An toàn cho trẻ em
- Đọc `tools/HUONG_DAN_NOI_DUNG.md` trước khi viết kịch bản.
- scene.json có thêm `title`, `lesson`, `look`, `beats` [{from,to,action}].
- `python3 tools/pitoon_pipeline.py scene.json --prompt` → in prompt GenerateVideo (tự gắn luật an toàn + câu thoại theo mốc thời gian).
- Pipeline tự chạy `tools/safety_check.py`; có hành động nguy hiểm / thiếu bài học / câu thoại > 12 từ → dừng (trừ khi `--force`).
Ví dụ: tools/scene_mau_v4.json → /workspace/ref/pitoon_free/canh_mau_v4.mp4
