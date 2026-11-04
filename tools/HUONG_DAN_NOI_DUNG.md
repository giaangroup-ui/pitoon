# Hướng dẫn nội dung PiToon – An toàn & Hài cho trẻ 3–10 tuổi

## 1. Nguyên tắc vàng
- Trẻ **bắt chước** mọi thứ nhân vật làm. Không đưa vào phim hành động nào mà nếu bé làm theo ngoài đời có thể bị đau.
- Cái hài phải **có lý**: bé hiểu vì sao buồn cười (nguyên nhân → kết quả rõ ràng).
- Lời thoại **ngắn (≤ 12 từ), từ quen thuộc**, nói rõ, có thể lặp lại cho vui.
- Mỗi tập **kết thúc bằng một bài học dễ hiểu**, nói thành một câu đơn giản (ví dụ: "Chia sẻ thì vui hơn!").

## 2. CẤM tuyệt đối
| Nhóm | Ví dụ không được có |
|---|---|
| Trèo lên chỗ cao | trèo cây, leo chum/vại, đứng lên ghế, mái nhà, lan can, cửa sổ |
| Ngã, đập đầu | ngã sấp, ngã đập đầu, sao quay quanh đầu, choáng váng, rơi từ cao |
| Đánh người | đánh, đá, đẩy, ném đồ vào người, cắn, giật tóc, trêu chọc ác ý |
| Lửa | diêm, bật lửa, bếp lửa, nến, pháo, đốt lửa |
| Điện | ổ cắm, dây điện, cột điện, đồ điện |
| Nước sâu | ao, hồ, sông, giếng, bể nước, chum nước đầy, bơi một mình |
| Vật sắc nhọn | dao, kéo, kim, dao rựa, mảnh vỡ, que nhọn |
| Ăn vật lạ | ăn/ngậm đồ không phải thức ăn, nấm lạ, quả lạ, thuốc, hạt nhỏ |
| Hỗn với người lớn | cãi, chế giễu, lè lưỡi, nói trống không, lừa người lớn |
| Khác | túi ni-lông trùm đầu, chạy ra đường xe, bắt nạt con vật |

## 3. ĐƯỢC PHÉP – nguồn gây cười
- **Hiểu lầm vui**: nghe nhầm từ, nhìn nhầm đồ vật (tưởng quả bí là con mèo ngủ…).
- **Chơi chữ kiểu Trạng Quỳnh**: lém lỉnh, thông minh, lễ phép, không chế giễu ai.
- **Con vật nghịch ngợm**: cún giật khăn đội lên đầu, mèo đuổi đuôi mình, gà mổ nhầm bóng.
- **Biểu cảm khuôn mặt hài**: mắt tròn xoe, má phồng, nhăn mũi, ngáp to, hắt xì.
- **Slapstick nhẹ với đồ mềm**: gối, bóng bay, lá chuối, khăn, mũ, bong bóng xà phòng – rơi nhẹ, không ai đau.
- Rượt đuổi **trên mặt đất bằng phẳng, đi/chạy chậm**, cuối cùng mọi người cười vui.

## 4. Cấu trúc một tập
1. Mở đầu vui (giới thiệu nhân vật, nơi chốn).
2. Tình huống hài có lý (hiểu lầm / con vật nghịch).
3. Cao trào nhẹ nhàng, an toàn.
4. Giải quyết bằng sự tử tế, thông minh.
5. Bài học một câu, nhân vật hoặc người dẫn chuyện nói rõ.

## 5. Kiểm tra tự động
`python3 tools/safety_check.py scene.json` (và pipeline tự chạy) quét lời thoại, hành động, prompt video theo danh sách từ khoá cấm (Việt + Anh). Có cảnh báo → sửa kịch bản trước khi dựng. Máy chỉ bắt được từ khoá; **người lớn vẫn phải xem lại toàn bộ phim**.
