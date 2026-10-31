# Bloxorz Solver

Game Bloxorz trên web với bàn chơi 3D bằng Three.js, engine Python và bốn thuật toán BFS, DFS, UCS, A*. Người chơi có thể tự điều khiển khối, tìm lời giải từ trạng thái hiện tại và phát lại từng nước đi.

## Yêu cầu

- Python 3.10 trở lên.
- Trình duyệt hỗ trợ WebGL2, ví dụ Chrome hoặc Edge.
- `matplotlib` để xuất biểu đồ benchmark.
- Node.js nếu muốn chạy các kiểm thử JavaScript.

Engine, server và các solver dùng thư viện chuẩn Python. Three.js được lưu sẵn trong `web/vendor/`, nên game không cần npm, bước build hoặc kết nối Internet khi chơi. `matplotlib` không bắt buộc nếu chỉ chơi game hoặc chạy benchmark với `--no-plots`.

## Cài đặt và chạy

Mở terminal tại thư mục chứa `main.py`, sau đó chạy:

```powershell
python -m pip install -r requirements.txt
python main.py
```

Server mở tại **http://127.0.0.1:8000/** và tự mở trình duyệt. Để chạy server mà không tự mở trình duyệt:

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
| Công tắc mềm | Kích hoạt khi bất kỳ phần nào của khối nhấn lên, kể cả khối con |
| Công tắc nặng | Chỉ kích hoạt bằng khối nguyên đứng |
| Cầu | Có thể đi qua khi mở; trạng thái do công tắc điều khiển |
| Công tắc tách `()` | Nhận khối nguyên đứng và đưa hai khối con tới các vị trí đã cấu hình |

Hai khối con ở hai ô liền cạnh sẽ tự ghép lại. Công tắc chỉ kích hoạt khi vừa được nhấn; giữ khối trên công tắc hoặc đổi khối điều khiển không kích hoạt lại.

**Số nước đi chỉ tính các lần lăn.** Chọn khối bằng `Space` hoặc click không tăng số nước đi và không cộng chi phí lời giải.

## Bộ giải

Chọn **BFS**, **DFS**, **UCS** hoặc **A*** để tìm lời giải từ trạng thái hiện tại. Khi tìm thấy, dùng **Phát lại** để chạy lời giải, **Từng bước** để thực hiện một lần lăn hoặc **Dừng lời giải** để dừng phát sau bước hiện tại.

| Thuật toán | Cách tìm kiếm và mục tiêu |
| --- | --- |
| BFS | Duyệt theo chiều rộng, tìm lời giải có ít lần lăn nhất |
| DFS | Duyệt theo chiều sâu bằng stack; không bảo đảm ít bước hoặc chi phí nhỏ nhất |
| UCS | Ưu tiên chi phí tích lũy nhỏ nhất, tìm lời giải có tổng chi phí nhỏ nhất |
| A* | Ưu tiên `f = g + h`, tìm lời giải có tổng chi phí nhỏ nhất với heuristic hiện tại |

Chi phí mỗi lần lăn là `1 + số ô sàn dễ vỡ mà khối chiếm sau lần lăn`. Vì vậy, lời giải ít bước nhất có thể khác lời giải có chi phí nhỏ nhất. UCS và A* không ưu tiên ít bước hơn khi hai đường đi có cùng tổng chi phí.

A* dùng mô hình point-object nới lỏng: bỏ qua tư thế, ô trống, sàn dễ vỡ và trạng thái cầu, nhưng giữ các liên kết dịch chuyển từ công tắc tách tới điểm đến. Floyd–Warshall chuẩn bị khoảng cách giữa các mốc một lần cho mỗi lượt tìm kiếm; các lần tính heuristic sau đó dùng lại bảng này. Heuristic lấy khoảng cách nhỏ nhất từ các ô khối chiếm tới đích, chia 2 và làm tròn lên.

`search_successors()` trong `bloxorz/solvers/common.py` sử dụng `Engine.successors()` để gộp chọn khối và lần lăn kế tiếp thành một cạnh tìm kiếm. Chuỗi hành động vẫn giữ `switch` để phát lại đúng khối, nhưng `length` và `cost` không tính thao tác chọn khối.

Giao diện ghi nhận thời gian, bộ nhớ đỉnh, số node mở rộng, độ dài và chi phí lời giải. Bộ nhớ đo bằng `tracemalloc`, chia cho 1024 để đổi sang KiB; không bao gồm trình duyệt, GPU hoặc toàn bộ bộ nhớ tiến trình.

Tìm kiếm trên giao diện hiện không giới hạn thời gian. Nút **Dừng lời giải** chỉ dừng phát lại; giới hạn thời gian cho thực nghiệm được thiết lập riêng trong lệnh benchmark.

## Màn chơi và testcase

Game nạp 43 màn từ `levels/testcases.json`, mặc định mở `B01`:

| Nhóm | ID | Số màn |
| --- | --- | --- |
| Cơ bản | B01 đến B10 | 10 |
| Sàn dễ vỡ | F01 đến F10 | 10 |
| Công tắc và cầu | S01 đến S10 | 10 |
| Kết hợp | M01 đến M10 | 10 |
| Không có đường đi | N01 đến N03 | 3 |

File có cấu trúc `groups` → `cases`; mỗi case chứa `id`, `name` và `board`. Cấu hình `board` gồm sơ đồ `rows` và các trường tùy chọn như `bridges`, `initially_open`, `switches`.

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

Tọa độ có dạng `[hàng, cột]`, bắt đầu từ 0. Các hàng phải dài bằng nhau, kể cả khoảng trắng cuối hàng. Ô cầu cần được khai báo trong `bridges`; mỗi công tắc cần có cấu hình tương ứng trong `switches`. Bộ đọc kiểm tra dữ liệu trước khi tạo bàn chơi.

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

Các chỉ số thời gian, bộ nhớ và node mở rộng dùng lượt `solved` hợp lệ hoặc `no_solution` hoàn tất. Độ dài và chi phí chỉ dùng lời giải đã phát lại hợp lệ qua engine. Summary và biểu đồ dùng cùng quy tắc lọc; biểu đồ dùng trung vị, summary có thêm thời gian trung bình. Lượt timeout, lỗi hoặc lời giải không hợp lệ được thống kê riêng.

## Kiểm thử

Chạy bộ kiểm thử Python sau khi cài thư viện trong `requirements.txt`:

```powershell
python -m unittest discover -s tests -v
```

Chạy các kiểm thử JavaScript bằng Node.js:

```powershell
node --test tests/motion.test.mjs tests/victory.test.mjs tests/progression.test.mjs tests/replay.test.mjs tests/grass.test.mjs tests/scenery.test.mjs tests/testcases.test.mjs
```

Các kiểm thử bao phủ luật engine, dữ liệu màn, trạng thái lặp, số nước đi sau khi tách khối, phát lại lời giải, API web, timeout và tổng hợp benchmark. Kiểm thử web tạo server tạm trên cổng được hệ điều hành cấp và đóng sau khi chạy.

## Cấu trúc mã nguồn

| Đường dẫn | Vai trò |
| --- | --- |
| `main.py` | Điểm chạy chương trình |
| `server.py` | HTTP server, phiên chơi và API |
| `bloxorz/models.py` | Kiểu hành động, trạng thái và công tắc |
| `bloxorz/board.py`, `bloxorz/levels.py` | Bàn chơi, đọc và kiểm tra JSON |
| `bloxorz/engine.py` | Phép lăn, sàn đỡ, công tắc, cầu, tách/ghép |
| `bloxorz/solver.py` | Gọi solver, đo thời gian và bộ nhớ |
| `bloxorz/solvers/` | BFS, DFS, UCS, A* và các hàm dùng chung |
| `web/` | Giao diện HTML/CSS, Three.js, hiệu ứng và phát lại |
| `levels/testcases.json` | Bộ màn chơi cố định |
| `benchmark/benchmark.py` | Chạy thực nghiệm và xuất kết quả |
| `tests/` | Kiểm thử Python và JavaScript |
| `requirements.txt` | Thư viện Python bên ngoài |

Python quyết định tính hợp lệ của mọi nước đi. Frontend nhận trạng thái và sự kiện từ engine để hiển thị; lời giải được phát lại qua cùng API di chuyển của người chơi. `State` giữ vị trí, cấu hình cầu, thông tin tách khối và khối đang được điều khiển để phân biệt các trạng thái tìm kiếm.

Three.js và giấy phép đi kèm nằm trong `web/vendor/`.
