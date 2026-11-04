# PiToon – pipeline miễn phí (chạy trên máy)
1. Ảnh nhân vật / khung hình đầu: GenerateImage (prompt có mô tả KHAN – khăn xếp cứng, hình trụ thấp, nếp xếp song song, đỉnh phẳng, KHÔNG phải turban).
2. Clip: GenerateVideo (image-to-video, 15s, 720p). Trong prompt ghi rõ thời điểm nhân vật nói và câu thoại, ví dụ "0-4s: cậu bé nói với miệng cử động rõ: '...' rồi ngậm miệng".
3. `python3 tools/pitoon_pipeline.py scene.json` (cần ffmpeg, edge-tts, numpy):
   - giọng edge-tts tiếng Việt (NamMinh/HoaiMy) + cao độ/tốc độ/âm lượng theo vai (trẻ em, ông bà) và cảm xúc (`emo`);
   - tự dò đoạn miệng nói trong âm thanh gốc của clip (trong khung `win`), co giãn câu thoại (giữ cao độ) cho khớp miệng;
   - giữ tiếng động gốc (nước bắn, chó sủa), tắt tiếng nói gốc; nhạc nền vui tự tạo, tự hạ nhạc khi có thoại; chuẩn hoá âm lượng −16 LUFS.
Ví dụ: tools/scene_mau.json → /workspace/ref/pitoon_free/canh_mau_v2.mp4
