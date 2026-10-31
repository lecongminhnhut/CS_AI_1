# Bloxorz Solver

Game Bloxorz trên web với bàn chơi 3D bằng Three.js, engine Python và bốn thuật toán BFS, DFS, UCS, A*. Người chơi có thể tự điều khiển khối, tìm lời giải từ trạng thái hiện tại và phát lại từng nước đi của lời giải.

## Yêu cầu

- Python 3.10 trở lên.
- Trình duyệt hỗ trợ WebGL2, ví dụ: Chrome hoặc Microsoft Edge.
- Thư viện `matplotlib` để xuất biểu đồ benchmark.
- Node.js nếu muốn chạy các kiểm thử JavaScript.

Engine, server và các solver dùng thư viện chuẩn Python. Three.js được lưu sẵn trong `web/vendor/`, nên game không cần npm, bước build hoặc kết nối Internet khi chơi. 

Thư viện `matplotlib` không bắt buộc nếu chỉ chơi game hoặc chạy benchmark với `--no-plots`.

## Cài đặt và chạy

Mở terminal tại thư mục chứa `main.py`, sau đó chạy:

```powershell
python -m pip install -r requirements.txt
python main.py
```

Server mở tại **http://127.0.0.1:8000/** và tự mở trình duyệt. 

Để chạy server mà không tự mở trình duyệt:

```powershell
python main.py --no-browser
```

Cổng mặc định là `8000`; có thể chỉ định bằng `--port`:

```powershell
python main.py --port 8000 --no-browser
```

Nhấn `Ctrl + C` trong terminal để dừng server. Ván chơi được lưu trong bộ nhớ theo cookie trình duyệt; các tab dùng chung cookie sẽ dùng chung ván chơi. Khởi động lại server sẽ đặt lại phiên chơi.

## Cách chơi

Lăn khối nguyên đứng thẳng vào giếng đích để hoàn thành màn. Khối nằm ngang hoặc nằm dọc qua đích chưa được tính là thắng. Rơi khỏi sàn sẽ thua.

| Điều khiển | Chức năng |
| --- | --- |
| Mũi tên hoặc `W A S D` | Lăn khối |
| `Space` hoặc click vào khối con | Chọn khối điều khiển sau khi tách |
| `R` | Chơi lại màn hiện tại |
| `N` / `P` | Chuyển sang màn sau / trước |
| Kéo chuột trên bàn chơi | Xoay góc nhìn, tối đa 45° mỗi bên |
| Cuộn chuột | Thu phóng |
| Nút **Góc nhìn** | Đặt lại camera |

Trên thiết bị cảm ứng, dùng các nút mũi tên trên giao diện. Rê chuột hoặc chạm vào ô đặc biệt để xem chú thích. Khối có màu tím nhạt; khi tách, khối đang chọn sáng hơn khối còn lại.

| Ô đặc biệt | Quy tắc |
| --- | --- |
| Giếng đích | Chỉ hoàn thành khi khối nguyên đứng thẳng tại đích |
| Sàn dễ vỡ | Đỡ khối nằm và khối con 1×1; sập khi khối nguyên đứng lên |
| Công tắc mềm `O` | Kích hoạt khi bất kỳ phần nào của khối nhấn lên, kể cả khối con |
| Công tắc nặng `X` | Chỉ kích hoạt bằng khối nguyên đứng |
| Cầu | Có thể đi qua khi mở; trạng thái do công tắc điều khiển |
| Công tắc tách `()` | Nhận khối nguyên đứng và đưa hai khối con tới các vị trí đã cấu hình |

**Số nước đi chỉ tính các lần lăn.** 

Các công tắc chỉ kích hoạt khi vừa được nhấn.

Khi khối bị tách, ta đổi khối bằng `Space` hoặc click chọn trên khối muốn chọn. Hai khối con ở hai ô liền cạnh sẽ tự ghép lại. 

## Bộ giải

Chọn **BFS**, **DFS**, **UCS** hoặc **A*** để tìm lời giải từ trạng thái hiện tại. Khi tìm thấy, dùng **Phát lại** để chạy lời giải, **Từng bước** để thực hiện một lần lăn hoặc **Dừng lời giải** để dừng phát sau bước hiện tại.

| Thuật toán | Cách tìm kiếm và mục tiêu |
| --- | --- |
| BFS | Duyệt theo chiều rộng, tìm lời giải có ít lần lăn nhất |
| DFS | Duyệt theo chiều sâu bằng stack; không bảo đảm ít bước hoặc chi phí nhỏ nhất |
| UCS | Ưu tiên chi phí tích lũy nhỏ nhất, tìm lời giải có tổng chi phí nhỏ nhất |
| A* | Ưu tiên `f = g + h`, tìm lời giải có tổng chi phí nhỏ nhất với hàm heuristic hiện tại có trong báo cáo |

## Màn chơi và testcase

Game nạp 43 màn từ `levels/testcases.json`, mặc định mở `B01`:

| Nhóm | ID | Số màn |
| --- | --- | --- |
| Cơ bản | B01 đến B10 | 10 |
| Sàn dễ vỡ | F01 đến F10 | 10 |
| Công tắc và cầu | S01 đến S10 | 10 |
| Kết hợp | M01 đến M10 | 10 |
| Không có đường đi | N01 đến N03 | 3 |

File JSON có cấu trúc `groups` -> `cases`; mỗi case chứa `id`, `name` và `board`. Cấu hình `board` gồm sơ đồ `rows` và các trường tùy chọn như `bridges`, `initially_open`, `switches`.

| Ký hiệu trong `rows` | Ý nghĩa |
| --- | --- |
| Khoảng trắng | Ô trống, không có sàn |
| `.` | Sàn thường |
| `S` | Vị trí bắt đầu |
| `G` | Giếng đích |
| `F` | Sàn dễ vỡ |
| `B` | Ô cầu |
| `o` | Công tắc mềm |
| `h` | Công tắc nặng |
| `x` | Công tắc tách |

Tọa độ có dạng `[hàng, cột]`, bắt đầu từ 0. Các hàng phải dài bằng nhau, kể cả khoảng trắng cuối hàng. Ô cầu được khai báo trong `bridges`; mỗi công tắc cần có cấu hình tương ứng trong `switches`.

## Chạy benchmark

Benchmark chạy từ trạng thái đầu của mỗi testcase cho cả bốn thuật toán. Lệnh sau dùng giới hạn 10 giây cho mỗi lượt và lặp ba lần:

```powershell
python benchmark/benchmark.py --timeout 10 --repeat 3
```

Chạy thử một số màn và bỏ qua biểu đồ:

```powershell
python benchmark/benchmark.py --cases B01,F01,S01,M01,N01 --timeout 10 --repeat 1 --no-plots
```

| Tham số | Ý nghĩa | Mặc định |
| --- | --- | --- |
| `--timeout` | Giới hạn mỗi lượt chạy, tính bằng giây | `30` |
| `--repeat` | Số lần lặp mỗi testcase/thuật toán | `1` |
| `--cases` | Các ID cách nhau bằng dấu phẩy | Tất cả testcase |
| `--testcases` | Đường dẫn bộ testcase JSON | `levels/testcases.json` |
| `--output` | Thư mục xuất kết quả | `benchmark/results` |
| `--no-plots` | Không tạo biểu đồ | Không bật |

Timeout bên ngoài worker bao gồm thời gian khởi tạo tiến trình. Lượt chạy quá hạn sẽ bị dừng. ID testcase không hợp lệ khiến chương trình báo lỗi và thoát với mã 2.

Kết quả gồm:

- `benchmark_raw.csv`: số liệu từng lượt chạy.
- `benchmark_summary.csv`: tổng hợp theo nhóm và thuật toán.
- `benchmark_results.json`: số liệu thô, tổng hợp và metadata môi trường.
- `search_time.png`, `peak_memory.png`, `expanded_nodes.png`, `solution_length.png`: biểu đồ khi có dữ liệu phù hợp và đã cài `matplotlib`.

## Cấu trúc mã nguồn
Three.js và giấy phép đi kèm nằm trong `web/vendor/`.

**Các file thuật toán được viết bằng Python và lưu bên trong thư mục `BLOXORZ_MAIN/bloxorz`:**

```
BLOXORZ_MAIN/
├── main.py                  # Chạy chương trình
├── server.py                # HTTP server, phiên chơi và API
├── requirements.txt         # Danh sách thư viện Python bên ngoài
├── README.md                # Hướng dẫn sử dụng
├── bloxorz/
│   ├── models.py            # Hành động, trạng thái và công tắc
│   ├── board.py             # Biểu diễn bàn chơi
│   ├── levels.py            # Đọc và kiểm tra JSON
│   ├── engine.py            # Luật lăn, công tắc, cầu và tách/ghép
│   ├── solver.py            # Gọi solver, đo thời gian và bộ nhớ
│   └── solvers/
│       ├── bfs.py           # Tìm kiếm theo chiều rộng
│       ├── dfs.py           # Tìm kiếm theo chiều sâu
│       ├── ucs.py           # Tìm kiếm theo chi phí
│       ├── astar.py         # Tìm kiếm A*
│       └── common.py        # Sinh nước đi, tính chi phí và truy vết
├── web/                     # Giao diện 3D, hiệu ứng và phát lại lời giải
├── levels/
│   └── testcases.json       # Bộ testcase các màn chơi
├── benchmark/
│   └── benchmark.py         # Chạy thực nghiệm và xuất kết quả
└── tests/                   # Kiểm thử Python và JavaScript
```
