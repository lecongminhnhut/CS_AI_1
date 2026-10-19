# Test Specification — Bloxorz Solver

## 1. Mục đích, phạm vi và traceability

Tài liệu này mô tả test cases, chưa phải test code. Mục tiêu là kiểm tra luật game, dữ liệu level, tích hợp solver và quy trình benchmark theo đề CSC14003. Các expected result được gắn nhãn:

- **[ĐỀ BÀI]**: được xác định trực tiếp trong PDF.
- **[JSON]**: quan hệ cấu trúc quan sát được trong `levels.json`; không tự suy rộng thành luật chơi.
- **[CẦN XÁC MINH]**: đề hoặc schema chưa quy định đủ để chốt expected result. Test cần được giữ ở trạng thái blocked/pending cho đến khi người phát triển xác nhận luật.
- **[ĐỀ XUẤT]**: tiêu chí kiểm tra dữ liệu/quality được đề xuất; không phải luật chơi do PDF quy định.

### Phạm vi

1. Unit test: chuyển tư thế, tính footprint, illegal move, goal, fragile, switches, bridges, split/merge và level validation.
2. Integration/acceptance test: level loader, shared game engine/transition model, solver, replay và GUI tối thiểu.
3. Benchmark/report artifact: cùng manifest, luật, điều kiện chạy và schema kết quả cho BFS, DFS hoặc IDS, UCS và A*; không chứa kết quả benchmark chưa đo.
4. GUI cases kiểm tra yêu cầu chức năng và deliverable trong đề; không đặt tiêu chí pixel-perfect.

Không có source code trong workspace tại thời điểm soạn. `test-case/` hiện có tài liệu đặc tả này; chưa có test automation. `levels.json` có 33 level; cấu trúc dùng `rows`, `bridges`, `switches`, `initially_open`; không có legend/schema độc lập. Không khẳng định glyph `o`/`h`/`x` ánh xạ tới loại switch nào; mọi test phụ thuộc mapping phải chờ nhóm xác nhận.

### Traceability

| Tham chiếu | Yêu cầu | Test IDs |
|---|---|---|
| PDF §2.1, tr. 2 | Bàn hữu hạn, start, floor/void/goal; mọi phần khối phải được đỡ | ORI, MOV, GOAL, LV |
| PDF §2.2, tr. 2 | Ba orientation và footprint | ORI |
| PDF §2.3, tr. 2 | Bốn hướng, chuyển tư thế/vị trí, move qua void/biên là illegal | ORI, MOV |
| PDF §2.4, tr. 2 | Chỉ đứng trên goal mới thắng | GOAL, SPL |
| PDF §2.5, tr. 3 | Fragile, bridge, soft/heavy/split, toggle/permanent, cube control và merge | FRG, SWT, BRG, SPL, MRG |
| PDF §3.1, tr. 4 | Game core, advanced tiles; solver cũng xử lý luật đặc biệt | Unit và INT |
| PDF §3.2, tr. 5 | BFS và bốn metrics | SOL-01, INT-02, BEN-02 |
| PDF §3.3, tr. 5 | DFS hoặc IDS; xử lý repeated states | SOL-02, INT-06, BEN-03 |
| PDF §3.4, tr. 5 | UCS; định nghĩa cost; cost đồng đều tương đương BFS | SOL-03, INT-02, BEN-04 |
| PDF §3.5, tr. 5–6 | A*, heuristic, admissibility/consistency theo cost | SOL-04, INT-02, BEN-05 |
| PDF §3.6, tr. 6 | Formalization, test set cố định, bốn metrics, bảng/biểu đồ/thảo luận | INT, BEN |
| PDF §3.7, tr. 7 | Video demo public gồm GUI, tile/orientation/controls, manual play, solver/replay và narration/subtitles | GUI-01…GUI-05 |
| Proposal §8.1–8.6, §10–11, §16 | State/transition dùng chung; state key phải chứa thông tin split ảnh hưởng hành động; level schema và nhóm test; metrics/integration | LV, INT, BEN |
| Proposal §12, FR-01/FR-18 | GUI hiển thị board/controls và gọi solver | GUI-01…GUI-04 |
| `levels.json` | 33 level; glyph map và metadata chưa có schema chính thức | LV-01…LV-12, LV-DATA-01, INT-07, BEN-01 |

PDF citations: [đề bài Project 1](../docs/AI%20-%20Project%201.pdf). Proposal: [Bloxorz Solver Proposal](../docs/Bloxorz_Solver_Proposal.md). Dataset: [`levels.json`](../levels.json). Báo cáo phân tích trước: [`a.md`](../a.md).

## 2. Quy ước fixture và định dạng test

### Board nhỏ tự thiết kế

Để cô lập luật, test có thể dùng board hẹp, tự thiết kế thay vì phụ thuộc một level lớn. Ký hiệu fixture đề xuất: `.` floor, `#` void, `S` start, `G` goal, `F` fragile, `B` bridge, `o` soft, `h` heavy, `x` split. Đây là notation của test, không tuyên bố rằng JSON đã công bố legend tương ứng.

Tọa độ minh họa dùng `(r,c)`, row/column bắt đầu từ 0 và anchor là ô đơn hoặc ô trên/trái của footprint. Đây là quy ước fixture cần được ánh xạ rõ sang state model trước khi test tích hợp; PDF định nghĩa footprint nhưng không quy định anchor nội bộ, và Proposal §8.1 yêu cầu nhóm thống nhất reference coordinate. Mọi ô không liệt kê là void; fixture chuyển động hợp lệ phải khai báo footprint ban đầu và đích là floor, trừ tile được test. `B` cần khai báo trạng thái mở/đóng riêng. Mọi test bắt đầu từ state mới, trừ khi steps yêu cầu chuỗi action.

Các bảng test bên dưới có đủ sáu trường bắt buộc. Khi một test dùng precondition/steps chung trong phần đầu bảng, nội dung chung đó áp dụng cho mọi ID trong bảng; expected result được ghi riêng từng dòng. Không chạy các case có expected result `[CẦN XÁC MINH]` như pass/fail cho đến khi có quyết định của người phát triển.

### ORI — Orientation transitions (12 unit cases)

**Preconditions chung:** State là block chuẩn được đỡ trên floor, không có tile đặc biệt. Mỗi fixture khai báo floor cho footprint nguồn và footprint đích ghi trong expected result; mọi ô khác void. **Input chung:** orientation/anchor trong cột Input; action trong cột Steps. **Steps chung:** gọi transition một lần, đọc orientation, anchor và toàn bộ occupied cells. Anchor top/left là quy ước của bảng này; mapping sang implementation phải được review. Các tọa độ dưới đây là phép suy ra của luật lăn, không phải bảng tọa độ được in nguyên văn trong PDF. **Nguồn chung:** PDF §2.2–2.3, tr. 2; Proposal §8.1.

| ID | Mục tiêu | Input | Steps | Expected result | Nguồn căn cứ |
|---|---|---|---|---|---|
| ORI-01 | Đứng → nằm dọc khi đi lên | `STANDING (3,2)` | `UP` | [ĐỀ BÀI] `VERTICAL`, footprint `{(1,2),(2,2)}` | PDF §2.2–2.3, tr. 2 |
| ORI-02 | Đứng → nằm dọc khi đi xuống | `STANDING (1,2)` | `DOWN` | [ĐỀ BÀI] `VERTICAL`, footprint `{(2,2),(3,2)}` | PDF §2.2–2.3, tr. 2 |
| ORI-03 | Đứng → nằm ngang khi đi trái | `STANDING (2,3)` | `LEFT` | [ĐỀ BÀI] `HORIZONTAL`, footprint `{(2,1),(2,2)}` | PDF §2.2–2.3, tr. 2 |
| ORI-04 | Đứng → nằm ngang khi đi phải | `STANDING (2,1)` | `RIGHT` | [ĐỀ BÀI] `HORIZONTAL`, footprint `{(2,2),(2,3)}` | PDF §2.2–2.3, tr. 2 |
| ORI-05 | Ngang → đứng khi đi trái | `HORIZONTAL (2,2)`, source cells `(2,2),(2,3)` floor | `LEFT` | [ĐỀ BÀI] `STANDING (2,1)`, occupied cells `{(2,1)}` | PDF §2.2–2.3, tr. 2 |
| ORI-06 | Ngang → đứng khi đi phải | `HORIZONTAL (2,1)`, source cells `(2,1),(2,2)` floor | `RIGHT` | [ĐỀ BÀI] `STANDING (2,3)`, occupied cells `{(2,3)}` | PDF §2.2–2.3, tr. 2 |
| ORI-07 | Ngang dịch lên | `HORIZONTAL (2,2)` | `UP` | [ĐỀ BÀI] `HORIZONTAL (1,2)`, footprint `{(1,2),(1,3)}` | PDF §2.2–2.3, tr. 2 |
| ORI-08 | Ngang dịch xuống | `HORIZONTAL (2,2)` | `DOWN` | [ĐỀ BÀI] `HORIZONTAL (3,2)`, footprint `{(3,2),(3,3)}` | PDF §2.2–2.3, tr. 2 |
| ORI-09 | Dọc → đứng khi đi lên | `VERTICAL (2,2)`, source cells `(2,2),(3,2)` floor | `UP` | [ĐỀ BÀI] `STANDING (1,2)`, occupied cells `{(1,2)}` | PDF §2.2–2.3, tr. 2 |
| ORI-10 | Dọc → đứng khi đi xuống | `VERTICAL (1,2)`, source cells `(1,2),(2,2)` floor | `DOWN` | [ĐỀ BÀI] `STANDING (3,2)`, occupied cells `{(3,2)}` | PDF §2.2–2.3, tr. 2 |
| ORI-11 | Dọc dịch trái | `VERTICAL (2,2)` | `LEFT` | [ĐỀ BÀI] `VERTICAL (2,1)`, footprint `{(2,1),(3,1)}` | PDF §2.2–2.3, tr. 2 |
| ORI-12 | Dọc dịch phải | `VERTICAL (2,1)` | `RIGHT` | [ĐỀ BÀI] `VERTICAL (2,2)`, footprint `{(2,2),(3,2)}` | PDF §2.2–2.3, tr. 2 |

### MOV — Illegal moves và tile support (4 unit cases)

**Preconditions chung:** Dùng board fixture có các ô test ghi rõ; các tile chưa nêu là void. Initial state nằm trên floor hợp lệ. **Steps chung:** thử một action; kiểm tra status, state trả về và không có hiệu ứng switch/bridge phụ ngoài quy định. **Nguồn chung:** PDF §2.1, §2.3, tr. 2.

| ID | Mục tiêu | Input | Steps | Expected result | Nguồn căn cứ |
|---|---|---|---|---|---|
| MOV-01 | Phát hiện vượt biên | Board hữu hạn có tọa độ rows `0..2`, cols `0..2`; standing `(0,1)` trên floor | `UP` | [ĐỀ BÀI] Successor footprint nằm ngoài board nên move illegal/fall; không tạo successor hợp lệ. Cách biểu diễn terminal/failure là chi tiết API. | PDF §2.1, §2.3, tr. 2 |
| MOV-02 | Một phần footprint qua void | Standing `(1,1)` là floor; `RIGHT` tạo `(1,2),(1,3)`; `(1,2)` floor, `(1,3)` void | `RIGHT` | [ĐỀ BÀI] Illegal vì một ô occupied là void. | PDF §2.1, §2.3, tr. 2 |
| MOV-03 | Cả hai ô footprint qua void | Horizontal `(1,1)`; source `(1,1),(1,2)` floor; target khi `UP` là `(0,1),(0,2)`, cả hai void | `UP` | [ĐỀ BÀI] Illegal; không trả state được đỡ một phần. | PDF §2.1, §2.3, tr. 2 |
| MOV-04 | Bridge đóng chặn successor | Standing `(1,1)` floor; `RIGHT` target `(1,2),(1,3)`; `(1,2)` floor, `(1,3)` bridge đóng; switch ở tile khác, không thuộc target footprint | `RIGHT` | [ĐỀ BÀI] Illegal như void vì bridge đóng. Không assert chi tiết rollback/side effect ngoài việc không có successor hợp lệ. | PDF §2.3, §2.5, tr. 2–3 |

### GOAL — Điều kiện thắng (2 unit cases)

**Preconditions chung:** Goal là một ô xác định; test không dựa vào solver. **Steps chung:** gọi goal test trên state tương ứng. **Nguồn chung:** PDF §2.1, §2.4, tr. 2.

| ID | Mục tiêu | Input | Steps | Expected result | Nguồn căn cứ |
|---|---|---|---|---|---|
| GOAL-01 | Đứng trên goal | `STANDING` footprint đúng ô `G` | Goal test | [ĐỀ BÀI] Won/goal true. | PDF §2.4, tr. 2 |
| GOAL-02 | Nằm qua goal không thắng | `HORIZONTAL` hoặc `VERTICAL`, một occupied cell là `G`, block không đứng | Goal test | [ĐỀ BÀI] Goal false. [CẦN XÁC MINH] Nếu cách đặt block khiến nó rơi vào lỗ thì terminal outcome phụ thuộc định nghĩa support của goal; không dùng case này để kiểm tra support. | PDF §2.4, tr. 2 |

### FRG — Fragile tiles (3 unit cases)

**Preconditions chung:** `F` là fragile; tile và footprint còn nguyên trước test. **Nguồn chung:** PDF §2.5, tr. 3.

| ID | Mục tiêu | Input | Steps | Expected result | Nguồn căn cứ |
|---|---|---|---|---|---|
| FRG-01 | Khối nằm được đỡ bởi fragile | Standing `(1,1)` floor; `RIGHT` tạo horizontal `(1,2),(1,3)`; `(1,2)` floor, `(1,3)` `F` | `RIGHT` | [ĐỀ BÀI] Được đỡ; không rơi chỉ vì nằm trên `F`. | PDF §2.5, tr. 3 |
| FRG-02 | Khối đứng trên fragile | Horizontal `(1,1)` với source `(1,1),(1,2)` floor; `(1,3)` là `F` | `RIGHT` làm block đứng tại `(1,3)` | [ĐỀ BÀI] Tile vỡ, block rơi, không phải state chơi hợp lệ tiếp tục. | PDF §2.5, tr. 3 |
| FRG-03 | Orientation còn lại chạm fragile | Standing `(1,1)` floor; `DOWN` tạo vertical `(2,1),(3,1)`; `(2,1)` `F`, `(3,1)` floor | `DOWN` | [ĐỀ BÀI] Vì block đang nằm, được hỗ trợ theo mô tả chung. [CẦN XÁC MINH] Persistence/trạng thái “tile đã vỡ” nếu tile từng bị đứng lên chưa được quy định. | PDF §2.5, tr. 3 |

### SWT — Soft, heavy và split switches (8 unit cases)

**Preconditions chung:** Các unit case này dùng switch object có type `soft`, `heavy` hoặc `split`, không cần parse glyph. Vì vậy có thể kiểm tra luật type độc lập với mapping `o/h/x`; mapping này vẫn cần xác nhận trong loader tests. Fixture transition chuẩn: (a) block chuẩn đứng `(1,1)`, floor `(1,1),(2,1),(3,1)`, action `DOWN` kết thúc standing `(3,1)`; hoặc (b) block chuẩn đứng `(1,1)`, floor `(1,1),(1,2),(1,3)`, action `RIGHT` kết thúc horizontal `(1,2),(1,3)`. Đặt switch tại ô kết thúc footprint được nêu ở từng row; mọi ô khác void. Với single cube, fixture gồm cube tại `(1,1)`, floor destination `(1,2)`, action `RIGHT`, switch tại `(1,2)`. Các test kiểm tra activation của một switch lần đầu khi block/cube đi từ ngoài vào; repeated activation được kiểm tra riêng ở BRG-03. **Nguồn chung:** PDF §2.5, tr. 3.

| ID | Mục tiêu | Input | Steps | Expected result | Nguồn căn cứ |
|---|---|---|---|---|---|
| SWT-01 | Soft kích hoạt khi đứng | Fixture (a), soft switch tại `(3,1)` | Từ standing `(1,1)`, đi `DOWN` | [ĐỀ BÀI] Switch được kích hoạt khi block đứng trên switch. | PDF §2.5, tr. 3 |
| SWT-02 | Soft kích hoạt khi nằm | Fixture (b), soft switch tại `(1,3)` | Từ standing `(1,1)`, đi `RIGHT` | [ĐỀ BÀI] Switch được kích hoạt vì một occupied cell đè lên switch dù block không đứng. | PDF §2.5, tr. 3 |
| SWT-03 | Cube đơn kích hoạt soft | Single-cube fixture, soft switch tại `(1,2)` | Cube đi `RIGHT` từ `(1,1)` | [ĐỀ BÀI] Cube đơn có thể kích hoạt soft. | PDF §2.5, tr. 3 |
| SWT-04 | Heavy chỉ kích hoạt khi đứng | Fixture (a), heavy switch tại `(3,1)` | Từ standing `(1,1)`, đi `DOWN` | [ĐỀ BÀI] Switch kích hoạt. | PDF §2.5, tr. 3 |
| SWT-05 | Heavy không kích hoạt khi nằm | Fixture (b), heavy switch tại `(1,3)` | Từ standing `(1,1)`, đi `RIGHT` | [ĐỀ BÀI] Switch không kích hoạt khi block nằm đè lên nó. | PDF §2.5, tr. 3 |
| SWT-06 | Cube đơn không kích hoạt heavy | Single-cube fixture, heavy switch tại `(1,2)` | Cube đi `RIGHT` từ `(1,1)` | [ĐỀ BÀI] Switch không kích hoạt. | PDF §2.5, tr. 3 |
| SWT-07 | Split switch kích hoạt khi block đứng | Fixture (a), split switch tại `(3,1)`, destinations `[(4,1),(4,3)]` đều là tile hỗ trợ | Từ standing `(1,1)`, đi `DOWN`; đọc hai vị trí cube | [ĐỀ BÀI] Split switch kích hoạt, teleport và tạo hai cube đơn. Expected là tập vị trí không thứ tự `{(4,1),(4,3)}`; chưa assert thứ tự cube hay active cube. Destination được chọn là fixture semantic, chưa khẳng định cách JSON ánh xạ `destinations`. | PDF §2.5, tr. 3 |
| SWT-08 | Split switch không kích hoạt khi nằm | Fixture (b), split switch tại `(1,3)` | Từ standing `(1,1)`, đi `RIGHT` | [ĐỀ BÀI] Không split vì block kết thúc ở orientation nằm. | PDF §2.5, tr. 3 |

Nguồn từng case SWT-01…08: PDF §2.5, tr. 3. Kết quả “bridge state theo effect” còn phụ thuộc các case BRG.

### BRG — Bridge state và effect (5 unit cases)

**Preconditions chung:** Bridge có ID, trạng thái ban đầu và switch link được chỉ rõ. Kiểm tra state trước/sau trigger. **Nguồn chung:** PDF §2.5, tr. 3; `levels.json` dùng effect `toggle`, `open`, `close`.

| ID | Mục tiêu | Input | Steps | Expected result | Nguồn căn cứ |
|---|---|---|---|---|---|
| BRG-01 | Bridge đóng như void | Standing `(1,1)` floor; RIGHT target `(1,2),(1,3)`; `(1,2)` floor, `(1,3)` bridge closed | Đi `RIGHT` | [ĐỀ BÀI] Move illegal như khi qua void. | PDF §2.5, tr. 3 |
| BRG-02 | Bridge mở như floor | Cùng fixture BRG-01, bridge `(1,3)` open | Đi `RIGHT` | [ĐỀ BÀI] Successor horizontal tại `(1,2),(1,3)` hợp lệ như floor thường. | PDF §2.5, tr. 3 |
| BRG-03 | Toggle đảo trạng thái | Bridge closed; effect function nhận `toggle` | Phát hai activation event rời nhau vào effect handler; đọc state sau mỗi event | [ĐỀ BÀI] Sau event 1 bridge open; sau event 2 bridge closed. Test này kiểm tra effect mapping, không kiểm tra điều kiện phát activation. | PDF §2.5, tr. 3; trigger semantics được kiểm riêng sau khi chốt |
| BRG-04 | Permanent open/close | Hai subcase: closed + effect `open`; open + effect `close` | Gọi effect handler hai lần với cùng effect mỗi subcase | [ĐỀ BÀI] Trạng thái được set theo fixed state tương ứng; cùng effect lặp lại không đảo trạng thái. [JSON] Effect values là `open`/`close`. Khả năng switch khác ghi đè vẫn cần xác minh. | PDF §2.5, tr. 3; `levels.json` |
| BRG-05 | Một switch đổi nhiều bridge được liên kết | Một switch semantic liên kết hai bridge tile/group đang đóng; bridge thứ ba không liên kết vẫn đóng | Gửi một activation event tới effect handler với toggle; đọc trạng thái ba bridge | [ĐỀ BÀI] Cả hai bridge được liên kết chuyển sang mở theo toggle; bridge không liên kết giữ nguyên đóng. Không kiểm tra cách JSON mã hóa liên kết hoặc trigger timing. | PDF §2.5, tr. 3 |

### SPL / MRG — Split, control, merge và goal constraint (7 unit cases)

**Preconditions chung:** Hai cube có tọa độ riêng; state lưu active cube; hành động chuyển control được chọn/định nghĩa. Cách encode hành động chưa có trong `levels.json`. **Nguồn chung:** PDF §2.5, tr. 3.

| ID | Mục tiêu | Input | Steps | Expected result | Nguồn căn cứ |
|---|---|---|---|---|---|
| SPL-01 | Tạo hai cube ở destination | Block đứng trên split switch; hai destination semantic là hai tile hỗ trợ phân biệt | Activate switch | [ĐỀ BÀI] Block split thành hai cube; tập vị trí cube sau split khớp tập hai predefined positions. Không assert thứ tự cube/active cube. | PDF §2.5, tr. 3 |
| SPL-02 | Chuyển active cube | Cube A ở `(1,1)`, cube B ở `(4,4)`, cả hai tile được hỗ trợ; active cube ban đầu là A; tile `(4,5)` được hỗ trợ | Gửi semantic control-switch action (PDF nêu Spacebar là ví dụ); sau đó di chuyển cube đang active sang phải; đọc vị trí A/B và active selection | [ĐỀ BÀI] Sau đổi điều khiển, người chơi điều khiển cube còn lại; chỉ cube đang điều khiển di chuyển, cube kia giữ nguyên vị trí. Không assert phím cụ thể, active index encoding, animation hay terminal-state policy. | PDF §2.5, tr. 3 |
| SPL-03 | Cube đơn không thắng | Một cube đứng trên goal, cube còn lại ở nơi khác | Goal test | [ĐỀ BÀI] Cube đơn không thể complete stage. | PDF §2.5, tr. 3 |
| SPL-04 | Active cube không di chuyển vào void | Hai cube đơn được hỗ trợ; active cube tại `(1,1)`, ô `(1,2)` là void, inactive cube tại `(4,4)` trên floor | Gửi semantic move-right cho active cube; đọc successor và vị trí hai cube | [ĐỀ BÀI] Không có successor hợp lệ vì cube sẽ chiếm void; nếu engine giữ state khi từ chối move thì cả hai vị trí không đổi. Không assert animation hoặc cách biểu diễn failure. | PDF §2.1–2.3, tr. 2–3 |
| MRG-01 | Merge khi hai cube kề ngang | Hai cube tại `(1,1)` và `(1,2)`, hai ô đều floor | Đưa state đã split có hai cube này qua bước “resolve merge” của engine | [ĐỀ BÀI] Kết quả là block chuẩn nằm ngang, footprint `{(1,1),(1,2)}`. [CẦN XÁC MINH] Khi nào engine gọi resolve merge, anchor nội bộ và active identity sau merge. | PDF §2.5, tr. 3; Proposal §8.1, §8.4 |
| MRG-02 | Merge khi hai cube kề dọc | Hai cube tại `(1,1)` và `(2,1)`, hai ô đều floor | Đưa state đã split có hai cube này qua bước “resolve merge” của engine | [ĐỀ BÀI] Kết quả là block chuẩn nằm dọc, footprint `{(1,1),(2,1)}`. [CẦN XÁC MINH] Khi nào engine gọi resolve merge, anchor nội bộ và active identity sau merge. | PDF §2.5, tr. 3; Proposal §8.1, §8.4 |
| MRG-03 | Không merge khi cube không kề nhau | Hai cube ở `(1,1)` và `(1,3)`, mọi ô đang bị chiếm được hỗ trợ; có một ô trống giữa chúng | Kiểm tra điều kiện/handler merge cho state này | [ĐỀ BÀI] Hai cube vẫn là hai cube vì chưa ở trên hai tile kề nhau. Case chỉ kiểm tra predicate không-kề; không quyết định thời điểm engine tự gọi merge. | PDF §2.5, tr. 3 |

### LV — Level validation (13 unit cases, including the full-dataset structural audit)

**Preconditions chung:** Dùng schema đọc được từ `levels.json`: danh sách level với `name`, `passcode`, `rows`, tùy chọn `bridges`, `switches`, `initially_open`. Việc từ chối input malformed là tiêu chí validator đề xuất, chưa phải quy định chi tiết của PDF. **Steps chung:** đưa fixture JSON tương ứng vào loader/validator; kiểm tra accept/reject và diagnostic. **Nguồn chung:** PDF §3.1 yêu cầu format tải stage đơn giản; Proposal §10.1 nói schema chính thức cần được chốt; `levels.json` là dữ liệu hiện tại.

| ID | Mục tiêu | Input | Steps | Expected result | Nguồn căn cứ |
|---|---|---|---|---|---|
| LV-01 | Tải một level hợp lệ | Một level theo shape hiện hành, một `S`, một `G`, rows đều string | Parse và validate | [JSON] Level hợp lệ được chuyển thành board/state; tọa độ start/goal khớp map. Legend và default behavior cần xác nhận. | PDF §3.1; `levels.json`; Proposal §10.1 |
| LV-02 | JSON sai cú pháp | JSON bị cắt/thiếu dấu phân cách | Gọi loader | [ĐỀ XUẤT] Reject có diagnostic, không crash không kiểm soát. | Proposal §10.1; policy đề xuất |
| LV-03 | Thiếu trường bắt buộc | Thiếu `rows`, hoặc level không phải object | Validate | [ĐỀ XUẤT] Reject với lỗi nêu trường/entry. | PDF §3.1; `levels.json`; Proposal §10.1 |
| LV-04 | Kiểu dữ liệu rows sai | `rows` không phải list string hoặc chứa phần tử không phải string | Validate | [ĐỀ XUẤT] Reject. | `levels.json`; Proposal §10.1 |
| LV-05 | Start/goal thiếu hoặc lặp | Map có 0 hoặc >1 `S`; lặp lại tương tự cho `G` | Validate | [ĐỀ XUẤT] Reject vì trạng thái/đích không đơn trị. PDF mô tả một start và một goal. | PDF §2.1, tr. 2 |
| LV-06 | Ký hiệu không biết | Thêm ký tự ngoài legend đã được thống nhất | Validate | [ĐỀ XUẤT] Reject hoặc cảnh báo theo policy được chốt; không âm thầm coi là floor. | `levels.json`; policy legend cần chốt |
| LV-07 | Tọa độ ngoài board/âm | Bridge, switch hoặc destination ngoài kích thước rows | Validate | [ĐỀ XUẤT] Reject với đường dẫn trường và tọa độ lỗi. | `levels.json`; Proposal §10.1 |
| LV-08 | Bridge metadata không nhất quán | Switch effect tham chiếu ID không có trong `bridges`; `initially_open` có ID lạ; bridge coordinate không tương ứng tile bridge | Validate | [ĐỀ XUẤT] Reject hoặc diagnostic theo policy. Cần chốt xem glyph `B` hay metadata là nguồn sự thật. | `levels.json`; Proposal §10.1 |
| LV-09 | Switch/effect malformed | Switch thiếu `cell`, vừa có `effects` và `destinations`, effect không thuộc enum hiện hành | Validate | [ĐỀ XUẤT] Reject; enum hiện hành quan sát được là `toggle/open/close`, chưa phải schema versioned. | `levels.json`; Proposal §10.1 |
| LV-10 | Split destination malformed | Destination sai dạng/không đủ hai tọa độ, hoặc ngoài board/trên void; `active` ngoài 0/1 | Validate | [ĐỀ XUẤT] Reject hoặc yêu cầu xác nhận policy; ý nghĩa `active`/destination chưa được định nghĩa. | `levels.json`; Proposal §10.1 |
| LV-11 | Hàng level không đồng nhất độ rộng | Level có `rows` là list string nhưng ít nhất một hàng ngắn/dài hơn các hàng còn lại | Validate fixture ragged rows | [ĐỀ XUẤT] Validator nên reject hoặc chuẩn hóa theo policy công bố; PDF không chỉ định cách xử lý ragged rows, nên assertion reject cụ thể giữ PENDING đến khi chốt schema. | PDF §2.1, tr. 2; Proposal §10.1 |
| LV-12 | Tọa độ bridge/switch bị lặp | Fixture có một bridge coordinate lặp trong metadata hoặc hai switch records cùng cell | Validate từng biến thể riêng; đọc diagnostic theo entry/coordinate | [ĐỀ XUẤT] Validator cần phát hiện duplication và áp dụng policy đã chốt. PDF không quy định duplicate metadata policy; expected reject cụ thể PENDING. | `levels.json`; Proposal §10.1 |

| LV-DATA-01 | Audit cấu trúc toàn bộ dataset | Toàn bộ `levels.json` gồm Stage 01–Stage 33 | Đọc từng level, kiểm tra parse/schema hình dạng, hàng chữ nhật trong từng stage, đúng một `S`/`G`, ký hiệu quan sát được, tọa độ bridge khớp ký hiệu `B`, switch/destination/reference tọa độ nội bộ hợp lệ | [JSON] Cả 33 level thỏa các invariant cấu trúc ghi trong test data. Case này không kiểm tra khả năng giải, tính hợp lệ theo luật chưa xác minh hay kết quả solver. | `levels.json` (audit dữ liệu); PDF §2.1, tr. 2 (single start/goal) |

### SOL — Solver correctness (4 unit cases)

Các case này cô lập thuật toán khỏi game rules bằng một successor graph nhỏ có thể kiểm tra bằng tay. Nếu implementation không cho inject graph/successor function, cần dùng board fixture nhỏ tương đương; không được thay đổi state/transition rules để làm test tiện hơn. Với A*, expected heuristic property chỉ chạy sau khi heuristic và cost function được công bố. **Nguồn chung:** PDF §3.2–3.5, tr. 5–6; Proposal §9, §16.2.

| ID | Mục tiêu | Preconditions | Input | Steps | Expected result | Nguồn căn cứ |
|---|---|---|---|---|---|---|
| SOL-01 | BFS trả path ít action nhất | BFS nhận được finite successor graph; mỗi edge cost bằng 1 | Directed graph: `S→A`, `A→G`, `S→G`; goal `G` | Run BFS; đếm path action | [ĐỀ BÀI] Path tìm được hợp lệ và `solution_length=1`; không chọn path 2 bước. | PDF §3.2, tr. 5 |
| SOL-02 | DFS/IDS dừng trên cycle | Biến thể DFS hoặc IDS được ghi rõ; graph hữu hạn | `S→A`, `A→S`; không có goal reachable | Run solver; quan sát termination/status | [ĐỀ BÀI] Không lặp vô hạn; trả not-found khi search kết thúc đầy đủ. Với IDS, cấu hình depth limit/điều kiện tăng phải được ghi. | PDF §3.3, tr. 5; Proposal §16.2 |
| SOL-03 | UCS tối ưu tổng cost | UCS nhận non-negative edge costs | `S→A (1)`, `A→G (8)`; `S→B (2)`, `B→C (1)`, `C→G (1)` | Run UCS; tính lại cost path | [ĐỀ BÀI] Chọn path `S→B→C→G` cost 4 thay path cost 9. Cost values là fixture test, không phải cost gameplay được mặc định. | PDF §3.4, tr. 5 |
| SOL-04 | A* và kiểm chứng heuristic theo cost | Cost và heuristic được chốt; finite graph; nếu test optimality thì heuristic admissible theo cost | Dùng graph SOL-03 và exact remaining costs `h*(G)=0`, `h*(C)=1`, `h*(B)=2`, `h*(A)=8`, `h*(S)=4` làm oracle. | Tính shortest remaining cost độc lập; kiểm tra `h(s)≤h*(s)` cho mọi state; kiểm tra consistency nếu implementation/report tuyên bố; chạy A*, tính lại path cost | [ĐỀ BÀI] Heuristic phải được giải thích và phân tích theo cost. [CẦN XÁC MINH] Chưa thể assert A* optimality với heuristic thật trước khi heuristic/cost được chọn; fixture oracle tự nó không chỉ định heuristic implementation. | PDF §3.5, tr. 5–6 |

## 3. Integration tests

Các fixture dưới đây là level nhỏ tự thiết kế, không phải Stage trong dataset. Không cần chạy solver để biết kết quả cấu trúc; chỉ test nào có đường đi được nêu rõ mới assert path tương ứng. **Preconditions chung:** loader, game engine/transition và solver nhận cùng state model; luật chưa xác minh được đánh dấu pending. **Nguồn:** PDF §3.1–3.6, tr. 4–6; Proposal §7–8, §16.

| ID | Mục tiêu | Preconditions | Input | Steps | Expected result | Nguồn căn cứ |
|---|---|---|---|---|---|---|
| INT-01 | Loader → engine | Schema fixture được validator chấp nhận | Mini level: floor line `(1,1)…(1,4)`, `S=(1,1)`, `G=(1,4)` | Load; tạo state ban đầu; đọc footprint/tile | Start là standing tại S; board và goal map đúng fixture. [ĐỀ BÀI] Start standing; [CẦN XÁC MINH] zero-based coordinate contract. | PDF §2.1, §3.1; Proposal §10.1 |
| INT-02 | Engine transition → solver path → replay | Mini level chỉ có một đường hợp lệ; fixture và shared transition đã được xác định; cùng state/goal API | Mini level: floor `(1,1)…(1,4)`, start `(1,1)`, goal `(1,4)`, mọi ô khác void | Chạy BFS, DFS hoặc IDS đã chọn, UCS và A*; replay mỗi path qua engine; ghi path length/cost | [ĐỀ BÀI] Mọi solver trả path hợp lệ theo luật fixture; replay kết thúc ở standing goal. Với fixture chỉ có một đường, path là `RIGHT, RIGHT`; đây không phải khẳng định về level trong dataset. | PDF §3.1–3.5, tr. 4–6; Proposal §8, §16.2 |
| INT-03 | Loader → switch/bridge → engine → solver replay | Switch activation/effect order và glyph/schema mapping đã được chốt | Mini board floor `(1,1),(1,2),(1,3)`; start `(1,1)`; semantic soft switch `(1,2)` mở bridge `(1,4)`; goal `(1,4)`; bridge initially closed | Load; chạy từng solver trên cùng mini level; replay path và đọc bridge state sau mỗi action | [CẦN XÁC MINH] Sau khi trigger semantics được chốt, solver phải tìm path hợp lệ qua bridge và replay đạt goal; không khẳng định thứ tự hiệu ứng trước quyết định. Fixture do test thiết kế, không phải dataset level. | PDF §2.5, §3.1; Proposal §8.4 |
| INT-04 | Solver dùng bridge state trong state key | Board một hàng: floor `(1,1),(1,2)`, bridge `(1,3)`, floor `(1,4),(1,5)`; goal `(1,5)`. Tạo hai input states standing `(1,2)`, một bridge closed và một open. Các ô khác void. | So state keys; chạy solver từ từng state. Từ open state, expected path `RIGHT, RIGHT`; từ closed state không có successor sang phải và không có đường khác tới goal. | [ĐỀ BÀI] Keys phải khác dù block placement giống nhau. Open state có path qua bridge; closed state không có path. Không khẳng định cụ thể state-key encoding. | PDF §3.1, tr. 4; fixture do test thiết kế |
| INT-05 | Split state/control/solver/replay | Semantic split fixture; solver action/control/merge rules đã được chốt trước khi chạy phần path | Board có floor/start `(1,1)`, floor `(2,1),(3,1)`, split trigger `(3,1)`, destination floor `(4,1),(4,3)`, goal `(5,3)`; mọi ô khác void. Destinations là semantic fixture, không phải claim về JSON field mapping. | Load; đi `DOWN` tới trigger; kiểm tra tập cube positions `{(4,1),(4,3)}`; sau khi control/merge actions được quyết định, chạy solver và replay path | [ĐỀ BÀI] Split tạo hai cube ở predefined positions; solver cần hỗ trợ split/rejoin. Phần loader/trigger có thể kiểm tra với tập destination không thứ tự. Solver/replay steps **pending**, vì control, merge và trạng thái goal cần hoàn tất trước khi xác định đường đi. | PDF §2.5, §3.1; Proposal §8.1–8.4 |
| INT-06 | No-solution/termination và repeated states | Board finite; floor square `{(0,0),(0,1),(1,0),(1,1)}` with start `(0,0)`; isolated goal `(4,4)`; all other cells void | Load fixture; run each solver using its documented duplicate/termination policy; inspect completion/status | [ĐỀ BÀI] Goal unreachable; DFS/IDS must handle repeated states. Search should terminate on this finite reachable component when duplicate handling is correct. Record `not found`, not “proved unsolvable” for a timeout. Exact timeout/resource policy remains open. | PDF §3.3, §3.6; Proposal §10.3, §16.2 |
| INT-07 | Level loader → game model cho toàn dataset | Đã chốt schema/legend/default state tương thích với file hiện tại | Tất cả 33 entry của `levels.json` | Load từng entry; so board dimensions, start/goal và metadata special tiles với dữ liệu gốc; ghi stage/field nếu lỗi | [CẦN XÁC MINH] Khi schema và glyph mapping được chốt, loader phải đọc được toàn bộ level theo contract đã công bố hoặc báo lỗi cụ thể; không chạy solver và không kết luận solvability. PENDING vì schema/mapping chưa chính thức. | PDF §3.1, tr. 4; Proposal §7.1, §10.1–10.3; `levels.json` |
| INT-08 | State key phân biệt split states ảnh hưởng hành động tương lai | Có state-key API; tạo split states trên cùng board với cùng bridge configuration: một cặp có cùng cube positions nhưng active cube khác nhau, một cặp có active selection giống nhau nhưng một cube ở vị trí khác | Tính semantic state key cho từng state và so sánh từng cặp | [ĐỀ XUẤT] Proposal requires state keys to include information that changes future actions; PDF says the split cubes are controlled one at a time. Therefore, states differing in active cube or cube position must have distinct keys when that information changes future actions. No particular key encoding or cube storage order is required. | Proposal §8.1, §8.3, §8.6; PDF §2.5, tr. 3 |

### GUI acceptance — GUI (5 cases; integration/manual acceptance)

**Preconditions chung:** GUI hiển thị state từ shared game engine. Dùng semantic fixtures nhỏ; không suy glyph mapping chưa xác nhận. Kiểm tra bằng UI automation khi ổn định, nếu không dùng checklist thủ công. **Nguồn chung:** PDF §3.1, tr. 4; PDF §3.7, tr. 7; Proposal §6.6, §12.

| ID | Mục tiêu | Preconditions | Input | Steps | Expected result | Nguồn căn cứ |
|---|---|---|---|---|---|---|
| GUI-01 | Hiển thị board, tile và block orientation | GUI đã mở một semantic fixture có floor, void, goal và các special tiles được xác định | Fixture có thể trình bày block ở standing/horizontal/vertical qua ba trạng thái hợp lệ | Load fixture; quan sát board, tile, block và orientation ở từng state | [ĐỀ BÀI] GUI thể hiện board/game và block; demo cần cho thấy các tile type và các orientation. Không đặt yêu cầu pixel-perfect. | PDF §3.1, tr. 4; PDF §3.7, tr. 7; Proposal §12 |
| GUI-02 | New Game và Restart | Level fixture có initial state xác định | Thực hiện ít nhất một move hợp lệ rồi gọi Restart; sau đó gọi New Game với level đã chọn | So initial state, board và special-tile state trước/sau | [ĐỀ XUẤT] Restart khôi phục chính xác initial state của stage hiện tại; New Game bắt đầu stage được chọn. Cần đối chiếu UX nếu implementation có menu chọn level. | Proposal §4.1, FR-18, §12 |
| GUI-03 | Điều khiển thủ công và phản hồi terminal | GUI nhận bốn hướng; có fixture cho legal move, illegal move và goal | Gửi Up/Down/Left/Right; thử một move illegal và một path tới goal | So state hiển thị sau action với engine; quan sát kết thúc lượt chơi | [ĐỀ BÀI] Bốn hướng áp dụng đúng luật; move illegal không thành state hợp lệ; chỉ đứng trên goal thắng. Nội dung/kiểu thông báo cụ thể do UI quyết định. | PDF §2.3–2.4, tr. 2; PDF §3.1, tr. 4 |
| GUI-04 | Gọi solver và replay path từ GUI | Các solver bắt buộc đã được tích hợp; fixture có path đã xác định | Gọi BFS, DFS hoặc IDS đã chọn, UCS và A* trên mini level INT-02 | Theo dõi trạng thái solver; yêu cầu replay với mỗi path trả về | [ĐỀ BÀI] Có controls gọi các solver; path replay hợp lệ qua engine và kết thúc tại goal. Không assert tốc độ/animation duration. | PDF §3.1, tr. 4; PDF §3.7, tr. 7; Proposal §12 |
| GUI-05 | Checklist chấp nhận video demo | Bản GUI và solver demo đã sẵn sàng; có link video public trong report | Video demo và URL được ghi trong report | Kiểm tra video/link/narration hoặc subtitles và các nội dung trình diễn | [ĐỀ BÀI] Video có GUI/layout/tile/orientation/controls; manual play gồm switch và win/lose; trình diễn solver và solution/replay; có narration/subtitles tiếng Anh hoặc Việt; link public được cung cấp. Đây là deliverable acceptance, không phải game-engine test. | PDF §3.7, tr. 7 |

## 4. Benchmark protocol chung

### 4.1 Manifest level

Tất cả thuật toán dùng cùng một manifest có version/hash, cùng dữ liệu level, cùng luật transition và cùng goal test. Không xếp độ khó theo số hàng/cột. Phân nhóm bằng cơ chế được quan sát trong dữ liệu, không gọi đó là độ khó đã đo.

Manifest ứng viên để nhóm xem xét (không khẳng định nghiệm):

| Level ứng viên | Lý do bao phủ |
|---|---|
| Stage 01, Stage 03 | Hai bản đồ không có ký hiệu cơ chế nâng cao trong rows; không tuyên bố thứ tự khó. |
| Stage 04 | Có `F` fragile. |
| Stage 02 | Hai bridge, `o`/`h` switch, toggle. |
| Stage 05 | Bridge và các effect toggle/open/close; có `initially_open`. |
| Stage 08 | Có `x`/`destinations`, ứng viên split theo suy luận schema. |
| Stage 15 | Bridge, nhiều switch và một `x`/destinations; không có fragile `F`. |
| Stage 23 | Có fragile, bridge, switch và `x`/destinations. |
| Stage 30 | Có fragile, bridge và switch; không có `x`/destinations. |

Đây chỉ là **manifest ứng viên để review**. Trước benchmark chính thức, validator phải chấp nhận các level; semantics glyph/schema phải được chốt; test solvability hoặc status tìm kiếm phải được chạy và lưu. Không được gắn nhãn “có nghiệm” trước bước đó. Nếu split chưa được hỗ trợ đầy đủ, phải loại các level split khỏi manifest **cho tất cả** thuật toán hoặc hoãn benchmark; không dùng tập khác nhau theo solver.

### 4.2 Quy trình chạy

1. Chốt state/transition/goal semantics, manifest version và cost function; lưu hash/commit của code và dataset.
2. Chạy loader validation một lần trước batch; ghi lỗi level, không lặng lẽ bỏ qua.
3. Mỗi solver nhận cùng level và cùng initial state đã chuẩn hóa. GUI/animation tắt trong đo search.
4. Dùng chung máy, runtime, phiên bản dependencies, giới hạn thời gian/bộ nhớ và cách đếm expanded node. Ghi DFS hay IDS là implementation được chọn; ghi thứ tự successor nếu ảnh hưởng đường đi.
5. Theo Proposal §11.1, đo search time bằng `time.perf_counter()` và peak allocated memory bằng `tracemalloc`; dùng cùng ranh giới đo cho mọi solver. Ghi rõ có/không tính load level, state initialization, replay và garbage collection. Nếu đổi công cụ đo memory, nêu lý do và không trộn hai cách đo trong một bảng so sánh.
6. Ghi mỗi run gồm: `level_id`, algorithm/version, `found/status`, `search_time`, `peak_memory`, `expanded_nodes`, `solution_length`, `path_cost` (nếu áp dụng), timeout/error và cấu hình chạy. Không có lời giải thì ghi `solution_length`/`path_cost` là null hoặc schema đã thống nhất, không ghi 0.
7. Với mỗi path tìm được, replay qua shared transition model và xác nhận mọi bước hợp lệ, goal đúng; tính lại path length/cost độc lập. Path không hợp lệ làm benchmark run fail.
8. Chạy lặp lại số lần đã định trước cho đo thời gian/bộ nhớ; báo cáo quy tắc tổng hợp (ví dụ median) và cả timeout/failure. Expanded nodes/solution length có thể thay đổi giữa run nếu thuật toán có tie-breaking không xác định; ghi cấu hình đó.
9. Dùng cùng cost cho UCS/A*. Nếu mọi action cost 1, nêu UCS≈BFS theo đề; nếu cost không đồng đều, công bố cost trước benchmark. A* heuristic phải được mô tả/đánh giá theo cost này.
10. Xuất bảng và biểu đồ cho cùng manifest; báo cáo kết quả không nghiệm/timeout, không chỉ các case thành công.

### 4.3 Benchmark/report artifact test records (7)

| ID | Mục tiêu | Preconditions | Input | Steps | Expected result | Nguồn căn cứ |
|---|---|---|---|---|---|---|
| BEN-01 | Khóa fixed set | Manifest được duyệt; loader/schema/semantics chốt | Danh sách ứng viên §4.1 hoặc manifest thay thế có lý do | Lưu manifest/version/hash; chạy preflight validation | [ĐỀ BÀI] Cùng fixed set cho các thuật toán. [CẦN XÁC MINH] Solvability được ghi nhận thực nghiệm; không được suy ra từ kích thước. | PDF §3.6, tr. 6 |
| BEN-02 | Run BFS | Common protocol §4.2 đã chốt | Từng level manifest | Chạy BFS; lưu từng run/result | Ghi đủ time, memory, expanded nodes, solution length; kiểm tra path nếu found. | PDF §3.2, §3.6 |
| BEN-03 | Run DFS hoặc IDS | Biến thể được chọn; cycle/termination policy công bố | Cùng manifest | Chạy biến thể; lưu run/result | Ghi cùng metrics/status; không yêu cầu path tối ưu cho DFS. Nếu IDS, ghi depth behavior. | PDF §3.3, §3.6 |
| BEN-04 | Run UCS | Cost function công bố trước batch | Cùng manifest và transition graph | Chạy UCS; lưu run/result/path cost | Path phải hợp lệ; cost tính lại khớp cost function. Tối ưu chỉ so theo cost. | PDF §3.4, §3.6 |
| BEN-05 | Run A* và đối chiếu | Heuristic/cost công bố; luận cứ admissible/consistent nêu rõ nếu tuyên bố tối ưu | Cùng manifest | Chạy A*; lưu run/result/path cost; replay path | Ghi cùng metrics; tính lại cost/path. Không tuyên bố tối ưu nếu heuristic/cost không bảo đảm. | PDF §3.5–3.6 |
| BEN-06 | Export benchmark metrics không mất dữ liệu | Dùng synthetic fixture records có level/algorithm/status và giá trị metric giả lập rõ là test data, không phải benchmark result | Một record found và một record not-found/timeout; bốn metric bắt buộc cùng null fields phù hợp | Export sang format đã chọn; đọc lại; đối chiếu field, kiểu và giá trị với fixture | [ĐỀ BÀI] Export phải giữ search time, peak memory, expanded nodes và solution length cho mỗi solver; status/failure không được ngụy thành kết quả đo. Các số trong fixture chỉ dùng kiểm serializer, không phải kết quả thực nghiệm. | PDF §3.2, §3.6–3.7; Proposal FR-16–17, §11 |
| BEN-07 | Kiểm tra tính đầy đủ của bảng/biểu đồ report | Có synthetic result fixture dùng để test pipeline trình bày; manifest/algorithm labels xác định | Bảng và biểu đồ được dựng từ fixture, không trình bày fixture như số liệu thật | Kiểm tra bảng tổng hợp, chart labels/units/legend và phần diễn giải | [ĐỀ BÀI] Report có bảng, charts so sánh algorithm và insight/discussion; hiển thị các metric bắt buộc trên cùng test set. Không yêu cầu một kết luận hiệu năng cụ thể. | PDF §3.6, tr. 6–7; Proposal §11.3–11.5 |

## 5. Câu hỏi chưa được xác minh

Các câu hỏi này không được giải quyết ngầm trong test spec. Người phát triển cần ghi quyết định và cập nhật expected results trước khi test tương ứng có thể pass/fail.

1. **Legend/schema:** Ý nghĩa chính thức của `.`, khoảng trắng, `S`, `G`, `F`, `B`, `o`, `h`, `x` là gì? `o/h/x` có chắc map sang soft/heavy/split không?
2. **Tọa độ:** Index bắt đầu từ 0 hay 1? Quy ước anchor của horizontal/vertical state là gì? Có padding hàng ngắn không?
3. **Start/goal/void:** Goal có thể đỡ block nằm không? Block nằm qua goal là supported-but-not-win hay rơi? Start có thể nằm trên tile đặc biệt không?
4. **Fragile:** Tile có đổi state/persist sau khi vỡ không? PDF gọi cả horizontal và vertical là các tư thế nằm nên FRG-01 và FRG-03 đều được xác định là block nằm; còn xử lý footprint nhiều ô nếu tile fragile bị đứng đè không áp dụng cho tư thế đứng chuẩn (footprint chỉ một ô).
5. **Switch activation:** “Presses” nghĩa là edge-trigger khi bước vào hay level-trigger mỗi state/lượt đang đè? Khi một move rời/đến switch đồng thời, switch nào kích hoạt và theo thứ tự nào? Một switch có thể kích hoạt lặp khi block không rời tile không?
6. **Bridge closure:** Nếu switch đóng bridge đang bị block chiếm, block rơi ngay, state được giữ, hay closure bị trì hoãn? Bridge không liệt kê trong `initially_open` mặc định đóng?
7. **Permanent:** PDF dùng “permanent”; JSON biểu diễn `open`/`close`. Có nghĩa set trạng thái idempotent vĩnh viễn hay trạng thái có thể bị switch khác đổi lại?
8. **Split destinations:** Hai tọa độ đại diện vị trí hai cube hay nguồn/đích teleport? Thứ tự cube nào ứng với điểm nào? Có yêu cầu hai destination phải kề nhau/được đỡ/khác nhau?
9. **`active`:** Index 0/1 trỏ tới cube, destination hay active switch? Giá trị mặc định khi không có field là gì?
10. **Control và merge:** Action đổi active cube chính xác là gì? Merge tự động hay thao tác riêng? Khi merge orientation/anchor/active identity thế nào? Điều gì xảy ra nếu cube active rơi hoặc nằm trên goal?
11. **Single cube và switches:** Single cube không kích hoạt heavy; split switch có thể kích hoạt bởi cube đơn không? Switch tách có thể split lần nữa không?
12. **Bước chuyển và side effects:** Kiểm tra support trước hay sau switch effects? Solver action set có action switch-control/merge không, và mỗi action tính là một move/cost?
13. **Loader validation policy:** Unknown glyph/effect/field là hard error hay warning? Có chấp nhận ragged rows, duplicate bridge coordinates, duplicate switch cells, `passcode` thiếu/không phải chuỗi không?
14. **Cost/heuristic:** Cost thực nghiệm là đồng đều hay không đồng đều? Switch/control/merge có cost riêng? A* heuristic nào được chọn và chứng minh theo cost nào?
15. **Metrics protocol:** Proposal §11.1 đã đề xuất `time.perf_counter()`, `tracemalloc`, expanded state count và số action trong path. Cần chốt implementation-level counting point (expanded lúc nào), ranh giới timing/memory, số lần lặp và timeout/resource limit. Nếu chọn process RSS thay `tracemalloc`, cần ghi rõ đó là thay đổi so với proposal.
16. **Benchmark membership:** Level nào được hỗ trợ đầy đủ và đã kiểm tra solvability bằng cách nào? Proposal §10.3 yêu cầu không coi timeout là chứng minh vô nghiệm; các level split có thể đưa vào chung benchmark khi engine/solver hỗ trợ đủ không?

### Trạng thái sẵn sàng implement

| Có thể implement ngay trên semantic fixture | Cần quyết định trước khi implement/assert |
|---|---|
| ORI-01…ORI-12 theo anchor fixture (adapter nếu state model khác); MOV-01…MOV-04; GOAL-01…GOAL-02; FRG-01…FRG-03; BRG-01…BRG-05 trên semantic effect event; SWT-01…SWT-08 dùng switch type semantic; SPL-01…04; MRG-03; SOL-01…03; INT-08 trên semantic state key; LV-DATA-01; GUI-01…05 theo manual/UI artifact oracle; BEN-06/07 trên synthetic data. | Mapping glyph `o/h/x`; switch trigger/retrigger/effect order; state khi đóng bridge dưới block; meaning của `active`; split destinations/control API; timing/identity của positive merge cases; heuristic/cost A* ở SOL-04; validator policy LV-01…12; loader compatibility toàn dataset INT-07; manifest/status nghiệm và runtime/resource policy benchmark. |
| INT-02 có fixture logic cho cả bốn solver nhưng cần API/module; INT-04/08 cần state construction/key API; GUI cases cần ứng dụng để chạy. SOL-01…03 cần solver harness. | INT-01/03/05/06/07 phụ thuộc loader/semantics/solver status; MRG-01/02 chờ merge invocation policy; SOL-04 chờ heuristic/cost; BEN-01…05 chờ benchmark preflight; tất cả case vẫn cần chạy trước khi được gọi là pass. |

“Có thể implement ngay” ở đây nghĩa là luật expected đã đủ rõ cho fixture unit độc lập; chưa khẳng định implementation hiện có hay các case đã chạy.

## 6. Acceptance criteria cho test case và specification

Một test case chỉ được chấp nhận để implement/run khi thỏa tất cả điều kiện sau:

1. Có ID duy nhất, ổn định, thuộc nhóm `ORI`, `MOV`, `GOAL`, `FRG`, `SWT`, `BRG`, `SPL`, `MRG`, `LV`, `SOL`, `INT`, `GUI` hoặc `BEN`.
2. Có đủ mục tiêu, preconditions, input/fixture, steps có thể thực hiện, expected result và nguồn căn cứ.
3. Fixture nhỏ, xác định, độc lập; mọi tile/state liên quan được ghi rõ. Test game rule không cần solver để suy expected result.
4. Mỗi expected result phân biệt rõ `[ĐỀ BÀI]`, `[JSON]`, `[ĐỀ XUẤT]` hoặc `[CẦN XÁC MINH]`; không biến suy luận glyph/schema thành fact.
5. Kết quả `[CẦN XÁC MINH]` có owner/decision được ghi lại trước khi case chuyển sang pass/fail; chưa chốt thì giữ pending, không tự giả định.
6. Illegal-move test nêu rõ toàn bộ footprint đích và tile support; state không bị cập nhật ngoài policy đã thống nhất.
7. Test solver xác nhận path bằng replay qua transition model; tối ưu chỉ được assert theo giả định cost/heuristic phù hợp.
8. Integration test chỉ khẳng định path/solvability cho fixture có lời giải được mô tả trực tiếp; không gán solvability cho level trong `levels.json` nếu chưa kiểm chứng.
9. Benchmark test dùng một manifest/version/cấu hình chung cho cả bốn solver; metrics, node counting, resource limits, timeout và failure representation được định nghĩa trước.
10. Test case không phụ thuộc thứ tự độ khó suy từ kích thước board; phân nhóm theo cơ chế được xác nhận và báo cáo thứ tự difficulty chỉ khi có dữ liệu đo.
11. Level validation tests ghi rõ chúng là policy đề xuất khi PDF không chỉ định hành vi validator; error message cụ thể có thể do implementation chọn nhưng phải nhất quán.
12. Mỗi test được review để đảm bảo không làm thay đổi `levels.json`/source và không chứa assertion mâu thuẫn với luật PDF.

## 7. Thống kê test cases

| Nhóm | Số test case |
|---|---:|
| Orientation transitions (`ORI`) | 12 |
| Illegal moves / support (`MOV`) | 4 |
| Goal (`GOAL`) | 2 |
| Fragile (`FRG`) | 3 |
| Soft/heavy/split switches (`SWT`) | 8 |
| Bridges/effects (`BRG`) | 5 |
| Split/control/goal constraint (`SPL`) | 4 |
| Merge (`MRG`) | 3 |
| Level validation (`LV`) | 13 |
| Solver correctness (`SOL`) | 4 |
| **Unit total** | **58** |
| Integration (`INT`) | 8 |
| GUI integration (`GUI-01…04`) | 4 |
| GUI/deliverable acceptance (`GUI-05`) | 1 |
| Benchmark/report artifact (`BEN`) | 7 |
| **Tổng đặc tả** | **78** |
| Trạng thái đặc tả `READY` | 53 |
| Trạng thái đặc tả `PENDING` | 25 |

Trong đó các case liên quan đến glyph mapping, switch activation timing, split destination/control, merge timing và policy loader được đánh dấu pending cho đến khi câu hỏi §5 được trả lời. Các benchmark levels ở §4.1 chỉ là ứng viên; chưa có kết luận nào về solvability hoặc độ khó thực nghiệm.
