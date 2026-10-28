# AI Log

## Prompt

Rà soát và sửa `benchmark.py` cho dự án Bloxorz Solver. Yêu cầu chính:

- Kiểm tra benchmark, solver, các thuật toán BFS/DFS/UCS/A* và test hiện có trước khi sửa.
- Sửa cách tổng hợp metric để bao gồm các lượt `no_solution` hoàn tất trong metric hiệu năng.
- Chỉ dùng lời giải hợp lệ cho `solution_length` và `total_cost`.
- Sửa biểu đồ để dùng cùng quy tắc lọc dữ liệu với summary.
- Làm cho `--cases` báo lỗi và thoát mã khác 0 nếu có bất kỳ ID không hợp lệ nào.
- Rà soát timeout, vòng đời worker multiprocessing và khả năng tương thích Windows/spawn.
- Bổ sung metadata phục vụ tái lập benchmark.
- Bổ sung/cập nhật test và báo cáo kết quả kiểm thử.
- Không thay đổi logic solver, không commit, không push và không xóa thay đổi hiện có.

## Tóm tắt nội dung AI phản hồi

AI đã kiểm tra `benchmark/benchmark.py`, `bloxorz/solver.py`, các solver BFS/DFS/UCS/A* và test benchmark hiện có.

Các thay đổi đã thực hiện:

1. Thêm các helper dùng chung để xác định:
   - Lời giải hợp lệ (`solved` và `valid_solution == True`).
   - Lượt chạy hoàn tất (`solved` hợp lệ hoặc `no_solution`).
   - Giá trị metric hợp lệ, loại bỏ `None`, `NaN`, `inf` và kiểu boolean.
2. Sửa `summarize()`:
   - Metric thời gian, bộ nhớ và node mở rộng gồm `solved` hợp lệ và `no_solution` hoàn tất.
   - Độ dài lời giải và tổng chi phí chỉ gồm `solved` hợp lệ.
   - Các lượt `timeout`, `error`, `invalid_solution` không được đưa vào metric hiệu năng hoàn tất.
3. Sửa `write_plots()` để dùng cùng quy tắc lọc dữ liệu với `summarize()`.
4. Sửa `--cases`:
   - Chuẩn hóa khoảng trắng và tự loại ID trùng bằng tập hợp.
   - Kiểm tra toàn bộ ID trước khi chạy benchmark.
   - Nếu có ID không tồn tại, in lỗi ra `stderr`, trả mã `2` và không tạo output.
5. Cải thiện timeout worker:
   - Worker gửi tín hiệu đã khởi tạo xong.
   - Timeout ngoài ghi rõ xảy ra trước hay sau khi worker khởi tạo.
   - Timeout nội bộ của solver được ghi rõ trong trường `error`.
   - Worker được `terminate`, rồi `kill` nếu cần; queue được đóng và giải phóng.
6. Bổ sung metadata hệ điều hành, phiên bản matplotlib và Git commit hash nếu lấy được.
7. Cập nhật ghi chú metadata về quy tắc tính metric.
8. Bổ sung test cho summary, biểu đồ, `--cases` và timeout ngoài.

Không thay đổi các thuật toán BFS, DFS, UCS hoặc A*.

## Bảng nội dung giữ/sửa/xóa lập

| Nội dung | Hành động | Chi tiết |
|---|---|---|
| Kiến trúc thư mục và tên file | Giữ | Không đổi cấu trúc dự án hoặc CLI hiện có. |
| Các thuật toán BFS/DFS/UCS/A* | Giữ | Không sửa logic tìm kiếm. |
| Schema CSV/JSON hiện có | Giữ | Không thêm cột bắt buộc mới. |
| Status `solved`, `no_solution`, `timeout`, `error`, `invalid_solution` | Giữ | Chỉ sửa cách phân loại khi tính metric. |
| Hàm `summarize()` | Sửa | Bổ sung `no_solution` vào metric hiệu năng; lọc riêng metric lời giải. |
| Hàm `write_plots()` | Sửa | Đồng bộ quy tắc lọc với summary. |
| Xử lý `--cases` | Sửa | Dừng ngay với mã lỗi `2` khi có ID không hợp lệ. |
| `run_one()` và worker | Sửa | Phân biệt timeout ngoài/nội bộ và dọn dẹp tiến trình, queue. |
| Metadata benchmark | Sửa | Bổ sung OS, matplotlib và Git hash; giữ metadata cũ. |
| Test benchmark | Sửa/bổ sung | Thêm kiểm thử metric, plot, `--cases` và timeout. |
| Logic solver | Xóa khỏi phạm vi sửa | Không xóa hoặc thay đổi mã solver. |
| Kết quả benchmark thực nghiệm hiện có | Giữ | Smoke test ghi vào thư mục tạm, không ghi đè dữ liệu thực nghiệm. |

## Cách kiểm chứng

### Kiểm tra cú pháp

```powershell
python -m py_compile benchmark\benchmark.py
```

Kết quả: pass.

### Test benchmark

```powershell
python -m unittest tests.test_benchmark -v
```

Kết quả: 6/6 test pass.


### Smoke benchmark có lời giải

```powershell
python -m benchmark.benchmark --cases " B01, B01 " --timeout 5 --repeat 1 --no-plots --output <thu-muc-tam>
```

Kết quả: BFS, DFS, UCS và A* đều chạy thành công với trạng thái `solved`.

### Smoke benchmark không có lời giải

```powershell
python -m benchmark.benchmark --cases N01 --timeout 5 --repeat 1 --no-plots --output <thu-muc-tam>
```

Kết quả: cả bốn thuật toán trả `no_solution`; summary vẫn có thời gian tìm kiếm, peak memory và số node mở rộng.

### Kiểm tra ID testcase không hợp lệ

```powershell
python -m benchmark.benchmark --cases "B01, MISSING" --no-plots --output <thu-muc-tam>
```

Kết quả: in lỗi ra `stderr`, trả mã `2` và không tạo thư mục output mới.

### Giới hạn còn lại

Timeout ngoài vẫn bao gồm một phần thời gian khởi tạo/import worker vì multiprocessing `spawn` cần tạo tiến trình con. Tín hiệu worker-ready giúp nhận biết giai đoạn timeout nhưng không thể loại bỏ hoàn toàn chi phí khởi tạo đó.

