# Thiết kế hộp Pomodoro Box: thông số để vẽ trên Fusion 360

Đây là bản xem trước. Kích thước linh kiện lấy theo loại phổ biến. Khi có linh kiện thật, nhóm đo lại rồi sửa số trong bảng.

## Chú thích hình cho mục 2.1 thuyết minh

- Hình 2.1a (`hinh_3d_1_ben_ngoai_truoc.png`): Hình dáng bên ngoài, nhìn từ phía trước.
- Hình 2.1b (`hinh_3d_2_ben_ngoai_sau.png`): Hình dáng bên ngoài, nhìn từ phía sau (cổng USB, jack DC, khe hút gió DHT22).
- Hình 2.1c (`hinh_3d_3_ben_trong_than_hop.png`): Bên trong thân hộp sau khi mở nắp.
- Hình 2.1d (`hinh_3d_4_ben_trong_mat_duoi_nap.png`): Mặt dưới nắp (lật ngửa), các linh kiện gắn trên nắp.
- Hình 2.1e (`hinh_3d_5_tach_nap.png`): Hình tách nắp, thấy toàn bộ linh kiện.
- Hình 2.1f (`hinh_3d_6_ban_ve_kich_thuoc.png`): Bản vẽ kích thước.

## Thân hộp và nắp

Gốc tọa độ (0, 0) ở góc trước bên trái. x: sang phải (0 đến 150). y: về phía sau (0 đến 100). Chiều cao tính từ mặt đáy.

| Phần | Thông số |
|---|---|
| Thân hộp | 150 × 100 × 47, thành dày 2.5, đáy dày 2.5, bo góc ngoài R6, bo góc trong R3.5 |
| Nắp | 150 × 100 × 3, bo góc R6 |
| Trụ vít | 4 trụ Ø9 tại (7, 7), (143, 7), (7, 93), (143, 93). Lỗ Ø2.5 cho vít M3 tự ren |
| Lỗ vít trên nắp | Ø3.4 tại 4 vị trí trên |
| Chân đế | 4 miếng cao su Ø10 tại (14, 12), (136, 12), (14, 88), (136, 88) |

## Các lỗ khoét

| ID | Vị trí | Lỗ khoét | Tâm |
|---|---|---|---|
| 6 | Nắp | Cửa sổ LCD 73 × 26, bo góc R1 | (52, 68) |
| 4 | Nắp | Nút nhấn Ø12.2 | (133, 76) |
| 4 | Nắp | LED Ø6 (đế giữ LED 5 mm) | (110, 76) |
| 3 | Nắp | 19 lỗ Ø2.2: 1 lỗ giữa, 6 lỗ trên vòng R4, 12 lỗ trên vòng R8 | (122, 48) |
| 2 | Nắp | Quang trở Ø5.6 | (134, 18) |
| 5 | Nắp | Không khoét. In hoặc khắc nổi 0.5 mm vùng "QUẸT THẺ" 52 × 34 | (42, 26) |
| Chung | Mặt sau | USB 13 × 9, bo góc R2 | x = 126, cao 23 |
| Chung | Mặt sau | Jack DC Ø8 | x = 30, cao 16 |
| 1 | Mặt trái | 5 khe 30 × 2.4 bo đầu tròn | cách mặt trước 67, cao 9; 13.5; 18; 22.5; 27 |
| Chung | Mặt phải | 3 khe thoát nhiệt 30 × 2.4 | cách mặt trước 72, cao 31; 35.5; 40 |

## Vị trí linh kiện bên trong

| ID | Linh kiện | Gắn ở | Vùng chiếm (x, y) |
|---|---|---|---|
| 6 | LCD 1602 + module I2C | Dưới nắp, 4 cột đỡ M3 dài 7 | x 12 đến 92, y 50 đến 86 |
| 5 | RC522 | Dán dưới nắp, cách nắp 1 mm | x 22 đến 82, y 6 đến 46 |
| 3 | Module buzzer | Dưới nắp, buzzer sát lưới loa | x 95 đến 128, y 41.5 đến 54.5 |
| 2 | Module quang trở | Dưới nắp, quang trở nhô lên lỗ | x 104 đến 136, y 11 đến 25 |
| 4 | Nút nhấn, LED | Bắt ren qua nắp | tâm (133, 76) và (110, 76) |
| Chung | Board đục lỗ 70 × 50 | Đáy, 4 cột đồng cao 5 | x 75 đến 145, y 46 đến 96 |
| Chung | ESP32 DevKit V1 | Cắm header cái trên board, USB quay ra sau | x 112 đến 140, y 45.5 đến 97 |
| 1 | DHT22 | Đáy, kẹp L sát thành trái, mặt lưới quay ra khe | y 59.5 đến 74.5, cao 5 đến 30 |
| Chung | Jack DC | Mặt sau | tâm x = 30, cao 16 |

Linh kiện dưới nắp và linh kiện ở đáy chồng lên nhau khi nhìn từ trên, nhưng khác độ cao. Mặt trên ESP32 cao khoảng 25 mm, phần thấp nhất dưới nắp nằm phía trên ESP32 (chân nút nhấn) cao khoảng 28 mm, nên không chạm nhau.

## Lý do bố trí (dùng khi trình bày)

- DHT22 ở góc trái, cách ESP32 khoảng 100 mm, để nhiệt của ESP32 không làm sai số đo.
- Khe hút gió đặt thấp bên trái, khe thoát nhiệt đặt cao bên phải. Không khí nóng nhẹ hơn nên đi lên và ra ở phía trên (đối lưu tự nhiên).
- Quang trở cách LED đỏ khoảng 60 mm để ánh sáng LED không làm sai số đo.
- RC522 dùng sóng 13.56 MHz, đọc được thẻ qua nắp nhựa dày 3 mm. Không đặt vật kim loại giữa thẻ và anten.
- Cổng USB thẳng với lỗ ở mặt sau nên nạp code không cần mở hộp.
