# Khâu 10 – Tổng kiểm duyệt (QC cuối) – KHÔNG ĐẠT THÌ TRẢ VỀ

**Nhiệm vụ:** Chạy `studio/qc.py` (phim) + kiểm tra gói của khâu 9 + duyệt bằng mắt `qc_grid_*.jpg`. Trả lỗi về **đúng khâu** chịu trách nhiệm (cột "Khâu" trong qc.md). Runner: `python3 tools/line/studio_runner.py check FILM_DIR`.

## Tự động (qc.py + package_qc)
| Hạng mục | Ngưỡng | Khâu |
|---|---|---|
| An toàn trẻ em | 0 lỗi | 2 |
| Câu thoại / lời dẫn | ≤ 10 từ / ≤ 3 câu dẫn | 1 |
| Mỗi nhân vật một giọng | không trùng | 3 |
| Liên tục, cảm xúc từng câu, độ dài cảnh | continuity ✅, ≥ 2 loại cảm xúc, 2,5–5 giây/cảnh | 4 |
| Chuyển động | cả phim ≥ 4,5; mỗi cảnh ≥ 1,2 | 5 |
| Nhân vật tự nói trong video | 100% câu thoại `src: native` | 5 |
| Whisper khớp lời, thời điểm nói, giọng lạ | ≥ 80% mỗi câu | 6 |
| Âm lượng phim, nhạc hạ khi thoại, tiếng động | −18…−14 LUFS, ≥ 4 dB, ≥ 0,3 tiếng/giây | 7 |
| Độ phân giải, độ dài, khung đen, đứng hình, giây đứng yên, chuyển cảnh | ≥ 1280×720, 0 khung đen, đứng hình ≤ 1s, ≤ 5% giây đứng yên, Δ nối ≤ 18 | 8 |
| Gói đăng | −14 LUFS ±1, ≤ −1 dBTP, đúng kích thước, phụ đề trong vùng an toàn | 9 |

Ngưỡng hiệu chỉnh 16/11/2026: clip mẫu Tí & Cún v7 ĐẠT, phim Hai chị em v1 TRẢ VỀ.

## Bằng mắt
- [ ] Nhân vật & bối cảnh khớp bible; luật một đạo cụ; đạo cụ phụ không đổi
- [ ] Nét mặt khớp cảm xúc từng câu; có lúc vui, buồn, xúc động (chấm ≥ 8/10)
- [ ] Không hành động nguy hiểm trong hình; không kém hơn phim mẫu Tí & Cún

## Vòng trả về
- Bất kỳ ❌ → trả về khâu ghi trong cột "Khâu", làm lại, QC lại. Mỗi khâu tối đa **4 vòng**; quá → trạng thái "Cần chủ xem".
- Chỉ khi TẤT CẢ ✅ → "Chờ chủ duyệt". **Không bao giờ tự đăng.** Ghi qc_vN.md.
