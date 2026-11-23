# thao_sisters v2: làm lại theo cách của v7 (CHƯA TẠO HÌNH)
- Chẩn đoán: /workspace/ref/pitoon_free/thao_vs_v7_diagnosis.md
- Kế hoạch: SHOT_PLAN_v2.json (35 shot, phần thân 108s, tổng khoảng 1:56), tạo lại bằng make_plan.py
- Thử giọng dự phòng (edge-tts, mỗi nhân vật một giọng riêng): voice_test/*.wav
- Dừng vì hạn mức tuần đã dùng 89,4% (16/11 khoảng 17:10, giờ Việt Nam), đúng ngưỡng dừng 90%. Hạn mức reset thứ Hai 23/11/2026 lúc 11:23 (giờ Việt Nam).
## Chạy sau khi reset
1. CheckSubscriptionUsage. Dừng khi gần 90%.
2. Mỗi shot: GenerateImage keyframe 16:9 với refs (lấy khung cuối của shot trước nếu cùng bối cảnh), rồi GenerateVideo 6s với video_prompt_en (nhân vật nói thoại ngay trong video), chỉ dùng use_s giây đẹp nhất.
3. QC theo 10 khâu (tools/studio, ngưỡng trong stages.py): hình ≥8/10, Whisper ≥80%, chuyển động cả phim ≥4,5 và mỗi cảnh ≥1,2, không đứng hình >0,8s, ≥0,3 tiếng động/giây (kế hoạch hiện 0,27 – thêm tiếng), đúng bảng nhân vật, an toàn. Làm lại tối đa 4 lần.
4. Ghép: không bao giờ kéo dài clip. Chuyển cảnh 0,25s, SFX theo từng shot, nhạc theo emo, ba câu dẫn ngắn, phụ đề, intro/outro từ ../thao_sisters/motion.
5. Mỗi lần tạo một clip 6s tốn nhiều hạn mức. 35 shot cộng các lần làm lại có thể cần gần hết hạn mức một tuần. Có thể làm theo từng lượt cảnh (S01–S04, rồi S05–S08, rồi S09–S12).
