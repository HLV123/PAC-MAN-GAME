# PAC-MAN-GAME
Ứng dụng Alogorithm vào 4 ghost để tạo ra game AI

<img width="1005" height="860" alt="Image" src="https://github.com/user-attachments/assets/0b5c5001-0d42-44a3-af80-0d292a8cb987" />

<img width="1247" height="868" alt="Image" src="https://github.com/user-attachments/assets/9570d7e1-39ec-4695-9cd8-33b3269ec2c1" />

<img width="1247" height="856" alt="Image" src="https://github.com/user-attachments/assets/7981a780-759d-4c60-bf3e-172d7b5cf011" />

<img width="1250" height="857" alt="Image" src="https://github.com/user-attachments/assets/6c16fa3f-051b-4ac9-b364-6c303b7c5bbd" />

## Mô tả
Game Pac-Man được viết bằng Python với pygame, có hệ thống AI thông minh cho ma quái và nhiều tính năng đặc biệt.

## Tác giả
**Lê Văn Hưng** - AI Ghost Developer

## Tính năng chính

### 🎮 Gameplay Cơ bản
- Điều khiển Pac-Man ăn các chấm trắng nhỏ trong mê cung
- Tránh các con ma quái với AI thông minh
- Ăn viên năng lượng để biến ma quái thành trạng thái sợ hãi
- 5 level khác nhau với độ khó tăng dần

### 🤖 Hệ thống AI Ma quái
Game có 4 loại AI ma quái với tính cách khác nhau:
- **AGGRESSIVE** (Hung hăng): Luôn tấn công trực tiếp Pac-Man
- **AMBUSH** (Mai phục): Chờ đợi và tấn công khi Pac-Man đến gần
- **PATROL** (Tuần tra): Di chuyển theo các điểm cố định, tấn công khi cần
- **RANDOM** (Ngẫu nhiên): Kết hợp giữa tấn công và di chuyển ngẫu nhiên

### ⚡ Kỹ năng đặc biệt

#### POW! - Dịch chuyển ma quái
- **Cách sử dụng**: Nhấn phím `P` hoặc click nút POW!
- **Tác dụng**: Dịch chuyển ngẫu nhiên tất cả ma quái đến vị trí an toàn xa Pac-Man
- **Cooldown**: 5 giây
- **Điểm thưởng**: +100 điểm

#### WOW! - Tạo viên năng lượng
- **Cách sử dụng**: Nhấn phím `O` hoặc click nút WOW!
- **Tác dụng**: Tạo ra viên năng lượng gần Pac-Man
- **Cooldown**: 3 giây
- **Điểm thưởng**: +50 điểm
- **Lưu ý**: Không thể sử dụng khi đang ở chế độ power pellet

## Điều khiển

### Phím di chuyển
- `W` hoặc `↑`: Di chuyển lên
- `S` hoặc `↓`: Di chuyển xuống  
- `A` hoặc `←`: Di chuyển trái
- `D` hoặc `→`: Di chuyển phải

### Phím chức năng
- `P`: Kích hoạt kỹ năng POW!
- `O`: Kích hoạt kỹ năng WOW!
- `SPACE`: Tạm dừng game
- `ESC`: Trở về menu chính
- `R`: Khởi động lại (khi game over)
- `M`: Về menu (khi game over)
- `Q`: Thoát game (khi game over)

## Hệ thống điểm

| Hành động | Điểm |
|-----------|------|
| Ăn chấm nhỏ | 10 |
| Ăn viên năng lượng | 50 |
| Ăn ma quái (khi sợ hãi) | 200 |
| Sử dụng POW! | 100 |
| Sử dụng WOW! | 50 |
| Mạng thưởng | Mỗi 10,000 điểm |

## Cấu trúc dự án

```
pacman-game/
├── main.py          # File chính khởi động game
├── game.py          # Logic game chính
├── pacman.py        # Class Pac-Man
├── ghost.py         # Class ma quái với AI
├── map.py           # Xử lý bản đồ mê cung
├── menu.py          # Menu và giao diện
├── levels.py        # Dữ liệu các level
├── settings.py      # Cài đặt và hằng số
└── README.md        # File này
```

## Thông tin level

### Level 1: Mở đầu
- **Tốc độ ma quái**: 0.9
- **Tốc độ Pac-Man**: 1.0
- **Mô tả**: Mê cung mở với các hành lang rộng và khoảng cách chiến thuật

### Level 2: Trung cấp  
- **Tốc độ ma quái**: 1.0
- **Tốc độ Pac-Man**: 1.1
- **Mô tả**: Mê cung hình chữ T với không gian rộng cho di chuyển chiến thuật

### Level 3: Nâng cao
- **Tốc độ ma quái**: 1.1  
- **Tốc độ Pac-Man**: 1.2
- **Mô tả**: Mê cung cân bằng với nhiều lối thoát và đường đi chiến thuật

### Level 4: Chuyên gia
- **Tốc độ ma quái**: 1.2
- **Tốc độ Pac-Man**: 1.3  
- **Mô tả**: Bố cục pháo đài chiến thuật với hành lang mở và vị trí phòng thủ

### Level 5: Thách thức tối thượng
- **Tốc độ ma quái**: 1.3
- **Tốc độ Pac-Man**: 1.0
- **Mô tả**: Thử thách cuối cùng với mẫu hình nâng cao và khoảng mở chiến thuật

## Yêu cầu hệ thống

### Phần mềm cần thiết
- Python 3.7 trở lên
- pygame 2.0 trở lên

### Cài đặt
```bash
# Cài đặt pygame
pip install pygame
```

## Cách chạy game

```bash
# Chạy từ thư mục dự án
python main.py
```

## Tính năng kỹ thuật

### Hệ thống AI ma quái
- Pathfinding thông minh với thuật toán A*
- Đánh giá mức độ nguy hiểm động
- 4 tính cách AI khác nhau
- Chế độ sợ hãi khi Pac-Man ăn viên năng lượng

### Hệ thống animation
- Animation mở miệng Pac-Man
- Hiệu ứng ánh sáng và particle
- Ma quái với animation mắt theo hướng di chuyển
- Menu với hiệu ứng động đẹp mắt

### Lưu trữ dữ liệu
- Lưu điểm cao tự động
- Dữ liệu level có thể mở rộng
- Cài đặt game linh hoạt



---

**Chúc bạn chơi game vui vẻ! 🎮**
