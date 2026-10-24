# Giao diện ngoài theo bloxorz_skeleton02

Tham chiếu: `Source/gui/app.py` do người dùng cung cấp. Dùng bảng màu nền
`#eef2f8` → `#e2e8f1`, thẻ trắng viền `#dde3ec`, chữ `#1c2534`, nút nhấn
`#4f68e6`, Segoe UI và khoảng cách 12–24 px.

- Bàn chơi là nội dung chính bên trái; tiêu đề nhỏ và nhãn màn ở trên,
  chú thích sáu loại ô ở dưới. Không đổi mô hình 3D, camera hay animation.
- Cột phải gồm Màn chơi, Trạng thái, Bộ giải và Phím tắt. Chuyển màn bằng
  mũi tên hoặc danh sách; Ván mới về màn đầu, Chơi lại đặt lại màn hiện tại.
- Bộ giải giữ bốn thuật toán hiện có. Số liệu chưa chạy hiển thị “—”; tách
  độ dài và chi phí. Chỉ hiện số liệu backend cung cấp, không tạo số node giả.
  Phát lại, dừng và từng bước dùng cùng lời giải; di chuyển tay hủy lời giải cũ.
- Trạng thái tải, đang giải, lỗi, hết thời gian, không có lời giải và hoàn thành
  phải rõ ràng. Khóa thao tác xung đột; màn cuối không có nút tiếp ở hộp thắng.
- Desktop dùng tỉ lệ khoảng 852:356 và khoảng cách 24 px; màn nhỏ xếp dọc,
  giữ điều khiển chạm. Không cố định chiều cao làm che nội dung.
- Chấp nhận khi không tràn ngang, nút chuyển màn và từng bước hoạt động,
  các chỉ số cập nhật từ kết quả thật, phím điều khiển và thắng/thua vẫn hoạt động.
