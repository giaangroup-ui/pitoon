# HƯỚNG DẪN DÙNG GÓI TRONG APP TẠO HOẠT HÌNH AI

## A. Bắt đầu
1. Giải nén file ZIP vào máy tính.
2. Mở thư mục `01_CHARACTER_REFERENCES`.
3. Tạo nhân vật `THAO_NGUYEN_01`, nạp `THAO_NGUYEN/THAO_NGUYEN_MASTER_REFERENCE.jpg`.
4. Tạo nhân vật `THAO_MY_01`, nạp `THAO_MY/THAO_MY_MASTER_REFERENCE.jpg`.
5. Nạp thêm `TWO_SISTERS_APPROVED_MASTER.png` làm ảnh tham chiếu chung nếu app cho phép.
6. Dùng bảng góc nhìn và bảng trang phục trong `02_MODEL_SHEETS` làm tư liệu phụ.

## B. Tạo Khang một lần
1. Dùng mô tả Khang trong `01_CHARACTER_REFERENCES/CHARACTER_BIBLE_VI.md`.
2. Tạo một ảnh chân dung/turnaround đầu tiên cho Khang.
3. Lưu ảnh đó với tên `KHANG_MASTER_REFERENCE.png`.
4. Dùng cùng ảnh này cho tất cả cảnh có Khang. Khi cậu trở lại trường, chỉ đổi trang phục sang đồng phục; không đổi khuôn mặt, tóc hay vóc dáng.

## C. Tạo 12 cảnh
- Mở `04_SCENE_PROMPTS/SCENE_PLAN.json`.
- Làm theo thứ tự S01 đến S12.
- Với mỗi cảnh, nạp đúng ảnh tham chiếu của nhân vật xuất hiện.
- Ghép prompt cảnh (`image_prompt_en` hoặc `image_prompt_vi`) với `MASTER_PROMPTS_AND_NEGATIVE_PROMPTS.md`.
- Tạo ảnh tĩnh trước. Kiểm tra khuôn mặt, kính, tóc, trang phục và tay chân.
- Khi ảnh đã đúng, dùng ảnh đó làm đầu vào Image-to-Video và dùng `motion_prompt_en`.
- Mỗi cảnh khoảng 8–10 giây. Tổng thời lượng dự kiến khoảng 2 phút; có thể kéo dài theo nhịp thoại để đạt 2–3 phút.

## D. Đồng bộ trang phục
- 12 cảnh chính sử dụng trang phục mặc định trong character bible.
- Bảng váy/đầm là tủ đồ phụ cho cảnh sinh nhật, đi chơi, lễ hội, ảnh quảng bá hoặc ngoại truyện.
- Khi có cảnh đổi trang phục, ghi rõ tên bộ đồ trong prompt và giữ nguyên tóc, kính, khuôn mặt, phụ kiện nhận diện.
- Không để app tự chọn lại quần áo ngẫu nhiên giữa hai cảnh liên tục cùng ngày.

## E. Thiết lập khuyến nghị
- Khung hình ngang: 16:9.
- Độ phân giải: 2K hoặc mức cao nhất app hỗ trợ.
- Tốc độ: 24 fps nếu có.
- Clip mỗi cảnh: 8–10 giây; tạo từng cảnh riêng rồi ghép.
- Reference strength / Character consistency / Character ID: bật và giữ thiết lập đồng nhất.
- Nếu có seed, giữ seed ổn định cho cùng nhân vật.
- Nếu app chỉ hỗ trợ một ảnh tham chiếu: nạp ảnh riêng của nhân vật đó trước; nếu có nhiều nhân vật trong cảnh, tạo từng nhân vật riêng rồi bố trí cùng cảnh bằng công cụ hỗ trợ.

## F. Âm thanh và hậu kỳ
- Thu giọng theo file `05_AUDIO/VOICEOVER_AND_DIALOGUE_VI.md`.
- Thêm nhạc và âm thanh môi trường theo chỉ dẫn từng cảnh trong JSON.
- Thêm tiêu đề, phụ đề, tên nhân vật và thông điệp ở bước hậu kỳ. Không yêu cầu AI viết chữ tiếng Việt trực tiếp trong hình.
- Xem lại toàn phim để kiểm tra kính, tóc, độ tuổi, tỷ lệ và trang phục.

## G. Lưu ý tương thích
Gói có cấu trúc trung lập, dùng được làm tư liệu cho nhiều ứng dụng tạo ảnh/video. Tên nút và cách nạp ảnh khác nhau theo từng app. ZIP không phải lúc nào cũng nạp trực tiếp được: nếu app không nhận ZIP, cần giải nén và tải từng ảnh/prompt theo hướng dẫn của app.
