# Bloxorz Solver — Test Cases

Detailed case catalog derived from [TEST_SPECIFICATION.md](TEST_SPECIFICATION.md). Documentation only; no test code or results. `READY` means the oracle is sufficiently specified for implementation, not that the case was implemented or passed. `PENDING` means a decision remains open.

## Summary

| Group | Count | READY | PENDING |
|---|---:|---:|---:|
| ORI | 12 | 12 | 0 |
| MOV | 4 | 4 | 0 |
| GOAL | 2 | 2 | 0 |
| FRG | 3 | 3 | 0 |
| SWT | 8 | 8 | 0 |
| BRG | 5 | 5 | 0 |
| SPL | 4 | 4 | 0 |
| MRG | 3 | 1 | 2 |
| LV | 13 | 1 | 12 |
| SOL | 4 | 3 | 1 |
| INT | 8 | 3 | 5 |
| GUI | 5 | 5 | 0 |
| BEN | 7 | 2 | 5 |
| **Total** | **78** | **53** | **25** |

## Case details

### ORI

#### ORI-01 — Đứng → nằm dọc khi đi lên

- **Objective:** Đứng → nằm dọc khi đi lên
- **Preconditions:** Supported standard block on ordinary floor; specification anchor convention; destination cells are floor unless specified.
- **Input/fixture:** `STANDING (3,2)`
- **Steps:** `UP`
- **Expected result:** [ĐỀ BÀI] `VERTICAL`, footprint `{(1,2),(2,2)}`
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.2–2.3, tr. 2

#### ORI-02 — Đứng → nằm dọc khi đi xuống

- **Objective:** Đứng → nằm dọc khi đi xuống
- **Preconditions:** Supported standard block on ordinary floor; specification anchor convention; destination cells are floor unless specified.
- **Input/fixture:** `STANDING (1,2)`
- **Steps:** `DOWN`
- **Expected result:** [ĐỀ BÀI] `VERTICAL`, footprint `{(2,2),(3,2)}`
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.2–2.3, tr. 2

#### ORI-03 — Đứng → nằm ngang khi đi trái

- **Objective:** Đứng → nằm ngang khi đi trái
- **Preconditions:** Supported standard block on ordinary floor; specification anchor convention; destination cells are floor unless specified.
- **Input/fixture:** `STANDING (2,3)`
- **Steps:** `LEFT`
- **Expected result:** [ĐỀ BÀI] `HORIZONTAL`, footprint `{(2,1),(2,2)}`
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.2–2.3, tr. 2

#### ORI-04 — Đứng → nằm ngang khi đi phải

- **Objective:** Đứng → nằm ngang khi đi phải
- **Preconditions:** Supported standard block on ordinary floor; specification anchor convention; destination cells are floor unless specified.
- **Input/fixture:** `STANDING (2,1)`
- **Steps:** `RIGHT`
- **Expected result:** [ĐỀ BÀI] `HORIZONTAL`, footprint `{(2,2),(2,3)}`
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.2–2.3, tr. 2

#### ORI-05 — Ngang → đứng khi đi trái

- **Objective:** Ngang → đứng khi đi trái
- **Preconditions:** Supported standard block on ordinary floor; specification anchor convention; destination cells are floor unless specified.
- **Input/fixture:** `HORIZONTAL (2,2)`, source cells `(2,2),(2,3)` floor
- **Steps:** `LEFT`
- **Expected result:** [ĐỀ BÀI] `STANDING (2,1)`, occupied cells `{(2,1)}`
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.2–2.3, tr. 2

#### ORI-06 — Ngang → đứng khi đi phải

- **Objective:** Ngang → đứng khi đi phải
- **Preconditions:** Supported standard block on ordinary floor; specification anchor convention; destination cells are floor unless specified.
- **Input/fixture:** `HORIZONTAL (2,1)`, source cells `(2,1),(2,2)` floor
- **Steps:** `RIGHT`
- **Expected result:** [ĐỀ BÀI] `STANDING (2,3)`, occupied cells `{(2,3)}`
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.2–2.3, tr. 2

#### ORI-07 — Ngang dịch lên

- **Objective:** Ngang dịch lên
- **Preconditions:** Supported standard block on ordinary floor; specification anchor convention; destination cells are floor unless specified.
- **Input/fixture:** `HORIZONTAL (2,2)`
- **Steps:** `UP`
- **Expected result:** [ĐỀ BÀI] `HORIZONTAL (1,2)`, footprint `{(1,2),(1,3)}`
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.2–2.3, tr. 2

#### ORI-08 — Ngang dịch xuống

- **Objective:** Ngang dịch xuống
- **Preconditions:** Supported standard block on ordinary floor; specification anchor convention; destination cells are floor unless specified.
- **Input/fixture:** `HORIZONTAL (2,2)`
- **Steps:** `DOWN`
- **Expected result:** [ĐỀ BÀI] `HORIZONTAL (3,2)`, footprint `{(3,2),(3,3)}`
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.2–2.3, tr. 2

#### ORI-09 — Dọc → đứng khi đi lên

- **Objective:** Dọc → đứng khi đi lên
- **Preconditions:** Supported standard block on ordinary floor; specification anchor convention; destination cells are floor unless specified.
- **Input/fixture:** `VERTICAL (2,2)`, source cells `(2,2),(3,2)` floor
- **Steps:** `UP`
- **Expected result:** [ĐỀ BÀI] `STANDING (1,2)`, occupied cells `{(1,2)}`
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.2–2.3, tr. 2

#### ORI-10 — Dọc → đứng khi đi xuống

- **Objective:** Dọc → đứng khi đi xuống
- **Preconditions:** Supported standard block on ordinary floor; specification anchor convention; destination cells are floor unless specified.
- **Input/fixture:** `VERTICAL (1,2)`, source cells `(1,2),(2,2)` floor
- **Steps:** `DOWN`
- **Expected result:** [ĐỀ BÀI] `STANDING (3,2)`, occupied cells `{(3,2)}`
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.2–2.3, tr. 2

#### ORI-11 — Dọc dịch trái

- **Objective:** Dọc dịch trái
- **Preconditions:** Supported standard block on ordinary floor; specification anchor convention; destination cells are floor unless specified.
- **Input/fixture:** `VERTICAL (2,2)`
- **Steps:** `LEFT`
- **Expected result:** [ĐỀ BÀI] `VERTICAL (2,1)`, footprint `{(2,1),(3,1)}`
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.2–2.3, tr. 2

#### ORI-12 — Dọc dịch phải

- **Objective:** Dọc dịch phải
- **Preconditions:** Supported standard block on ordinary floor; specification anchor convention; destination cells are floor unless specified.
- **Input/fixture:** `VERTICAL (2,1)`
- **Steps:** `RIGHT`
- **Expected result:** [ĐỀ BÀI] `VERTICAL (2,2)`, footprint `{(2,2),(3,2)}`
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.2–2.3, tr. 2

### MOV

#### MOV-01 — Phát hiện vượt biên

- **Objective:** Phát hiện vượt biên
- **Preconditions:** Board, orientation, and occupied cells are as stated; unlisted cells are void.
- **Input/fixture:** Board hữu hạn có tọa độ rows `0..2`, cols `0..2`; standing `(0,1)` trên floor
- **Steps:** `UP`
- **Expected result:** [ĐỀ BÀI] Successor footprint nằm ngoài board nên move illegal/fall; không tạo successor hợp lệ. Cách biểu diễn terminal/failure là chi tiết API.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.1, §2.3, tr. 2

#### MOV-02 — Một phần footprint qua void

- **Objective:** Một phần footprint qua void
- **Preconditions:** Board, orientation, and occupied cells are as stated; unlisted cells are void.
- **Input/fixture:** Standing `(1,1)` là floor; `RIGHT` tạo `(1,2),(1,3)`; `(1,2)` floor, `(1,3)` void
- **Steps:** `RIGHT`
- **Expected result:** [ĐỀ BÀI] Illegal vì một ô occupied là void.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.1, §2.3, tr. 2

#### MOV-03 — Cả hai ô footprint qua void

- **Objective:** Cả hai ô footprint qua void
- **Preconditions:** Board, orientation, and occupied cells are as stated; unlisted cells are void.
- **Input/fixture:** Horizontal `(1,1)`; source `(1,1),(1,2)` floor; target khi `UP` là `(0,1),(0,2)`, cả hai void
- **Steps:** `UP`
- **Expected result:** [ĐỀ BÀI] Illegal; không trả state được đỡ một phần.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.1, §2.3, tr. 2

#### MOV-04 — Bridge đóng chặn successor

- **Objective:** Bridge đóng chặn successor
- **Preconditions:** Board, orientation, and occupied cells are as stated; unlisted cells are void.
- **Input/fixture:** Standing `(1,1)` floor; `RIGHT` target `(1,2),(1,3)`; `(1,2)` floor, `(1,3)` bridge đóng; switch ở tile khác, không thuộc target footprint
- **Steps:** `RIGHT`
- **Expected result:** [ĐỀ BÀI] Illegal như void vì bridge đóng. Không assert chi tiết rollback/side effect ngoài việc không có successor hợp lệ.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.3, §2.5, tr. 2–3

### GOAL

#### GOAL-01 — Đứng trên goal

- **Objective:** Đứng trên goal
- **Preconditions:** Goal predicate receives the stated block/cube state.
- **Input/fixture:** `STANDING` footprint đúng ô `G`
- **Steps:** Goal test
- **Expected result:** [ĐỀ BÀI] Won/goal true.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.4, tr. 2

#### GOAL-02 — Nằm qua goal không thắng

- **Objective:** Nằm qua goal không thắng
- **Preconditions:** Goal predicate receives the stated block/cube state.
- **Input/fixture:** `HORIZONTAL` hoặc `VERTICAL`, một occupied cell là `G`, block không đứng
- **Steps:** Goal test
- **Expected result:** [ĐỀ BÀI] Goal false. [CẦN XÁC MINH] Nếu cách đặt block khiến nó rơi vào lỗ thì terminal outcome phụ thuộc định nghĩa support của goal; không dùng case này để kiểm tra support.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.4, tr. 2

### FRG

#### FRG-01 — Khối nằm được đỡ bởi fragile

- **Objective:** Khối nằm được đỡ bởi fragile
- **Preconditions:** Semantic fragile tile fixture; unlisted cells are void.
- **Input/fixture:** Standing `(1,1)` floor; `RIGHT` tạo horizontal `(1,2),(1,3)`; `(1,2)` floor, `(1,3)` `F`
- **Steps:** `RIGHT`
- **Expected result:** [ĐỀ BÀI] Được đỡ; không rơi chỉ vì nằm trên `F`.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

#### FRG-02 — Khối đứng trên fragile

- **Objective:** Khối đứng trên fragile
- **Preconditions:** Semantic fragile tile fixture; unlisted cells are void.
- **Input/fixture:** Horizontal `(1,1)` với source `(1,1),(1,2)` floor; `(1,3)` là `F`
- **Steps:** `RIGHT` làm block đứng tại `(1,3)`
- **Expected result:** [ĐỀ BÀI] Tile vỡ, block rơi, không phải state chơi hợp lệ tiếp tục.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

#### FRG-03 — Orientation còn lại chạm fragile

- **Objective:** Orientation còn lại chạm fragile
- **Preconditions:** Semantic fragile tile fixture; unlisted cells are void.
- **Input/fixture:** Standing `(1,1)` floor; `DOWN` tạo vertical `(2,1),(3,1)`; `(2,1)` `F`, `(3,1)` floor
- **Steps:** `DOWN`
- **Expected result:** [ĐỀ BÀI] Vì block đang nằm, được hỗ trợ theo mô tả chung. [CẦN XÁC MINH] Persistence/trạng thái “tile đã vỡ” nếu tile từng bị đứng lên chưa được quy định.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

### SWT

#### SWT-01 — Soft kích hoạt khi đứng

- **Objective:** Soft kích hoạt khi đứng
- **Preconditions:** Switch type is semantic; no JSON glyph mapping is inferred.
- **Input/fixture:** Fixture (a), soft switch tại `(3,1)`
- **Steps:** Từ standing `(1,1)`, đi `DOWN`
- **Expected result:** [ĐỀ BÀI] Switch được kích hoạt khi block đứng trên switch.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

#### SWT-02 — Soft kích hoạt khi nằm

- **Objective:** Soft kích hoạt khi nằm
- **Preconditions:** Switch type is semantic; no JSON glyph mapping is inferred.
- **Input/fixture:** Fixture (b), soft switch tại `(1,3)`
- **Steps:** Từ standing `(1,1)`, đi `RIGHT`
- **Expected result:** [ĐỀ BÀI] Switch được kích hoạt vì một occupied cell đè lên switch dù block không đứng.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

#### SWT-03 — Cube đơn kích hoạt soft

- **Objective:** Cube đơn kích hoạt soft
- **Preconditions:** Switch type is semantic; no JSON glyph mapping is inferred.
- **Input/fixture:** Single-cube fixture, soft switch tại `(1,2)`
- **Steps:** Cube đi `RIGHT` từ `(1,1)`
- **Expected result:** [ĐỀ BÀI] Cube đơn có thể kích hoạt soft.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

#### SWT-04 — Heavy chỉ kích hoạt khi đứng

- **Objective:** Heavy chỉ kích hoạt khi đứng
- **Preconditions:** Switch type is semantic; no JSON glyph mapping is inferred.
- **Input/fixture:** Fixture (a), heavy switch tại `(3,1)`
- **Steps:** Từ standing `(1,1)`, đi `DOWN`
- **Expected result:** [ĐỀ BÀI] Switch kích hoạt.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

#### SWT-05 — Heavy không kích hoạt khi nằm

- **Objective:** Heavy không kích hoạt khi nằm
- **Preconditions:** Switch type is semantic; no JSON glyph mapping is inferred.
- **Input/fixture:** Fixture (b), heavy switch tại `(1,3)`
- **Steps:** Từ standing `(1,1)`, đi `RIGHT`
- **Expected result:** [ĐỀ BÀI] Switch không kích hoạt khi block nằm đè lên nó.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

#### SWT-06 — Cube đơn không kích hoạt heavy

- **Objective:** Cube đơn không kích hoạt heavy
- **Preconditions:** Switch type is semantic; no JSON glyph mapping is inferred.
- **Input/fixture:** Single-cube fixture, heavy switch tại `(1,2)`
- **Steps:** Cube đi `RIGHT` từ `(1,1)`
- **Expected result:** [ĐỀ BÀI] Switch không kích hoạt.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

#### SWT-07 — Split switch kích hoạt khi block đứng

- **Objective:** Split switch kích hoạt khi block đứng
- **Preconditions:** Switch type is semantic; no JSON glyph mapping is inferred.
- **Input/fixture:** Fixture (a), split switch tại `(3,1)`, destinations `[(4,1),(4,3)]` đều là tile hỗ trợ
- **Steps:** Từ standing `(1,1)`, đi `DOWN`; đọc hai vị trí cube
- **Expected result:** [ĐỀ BÀI] Split switch kích hoạt, teleport và tạo hai cube đơn. Expected là tập vị trí không thứ tự `{(4,1),(4,3)}`; chưa assert thứ tự cube hay active cube. Destination được chọn là fixture semantic, chưa khẳng định cách JSON ánh xạ `destinations`.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

#### SWT-08 — Split switch không kích hoạt khi nằm

- **Objective:** Split switch không kích hoạt khi nằm
- **Preconditions:** Switch type is semantic; no JSON glyph mapping is inferred.
- **Input/fixture:** Fixture (b), split switch tại `(1,3)`
- **Steps:** Từ standing `(1,1)`, đi `RIGHT`
- **Expected result:** [ĐỀ BÀI] Không split vì block kết thúc ở orientation nằm.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

### BRG

#### BRG-01 — Bridge đóng như void

- **Objective:** Bridge đóng như void
- **Preconditions:** Bridge state/effect are semantic fixture inputs.
- **Input/fixture:** Standing `(1,1)` floor; RIGHT target `(1,2),(1,3)`; `(1,2)` floor, `(1,3)` bridge closed
- **Steps:** Đi `RIGHT`
- **Expected result:** [ĐỀ BÀI] Move illegal như khi qua void.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

#### BRG-02 — Bridge mở như floor

- **Objective:** Bridge mở như floor
- **Preconditions:** Bridge state/effect are semantic fixture inputs.
- **Input/fixture:** Cùng fixture BRG-01, bridge `(1,3)` open
- **Steps:** Đi `RIGHT`
- **Expected result:** [ĐỀ BÀI] Successor horizontal tại `(1,2),(1,3)` hợp lệ như floor thường.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

#### BRG-03 — Toggle đảo trạng thái

- **Objective:** Toggle đảo trạng thái
- **Preconditions:** Bridge state/effect are semantic fixture inputs.
- **Input/fixture:** Bridge closed; effect function nhận `toggle`
- **Steps:** Phát hai activation event rời nhau vào effect handler; đọc state sau mỗi event
- **Expected result:** [ĐỀ BÀI] Sau event 1 bridge open; sau event 2 bridge closed. Test này kiểm tra effect mapping, không kiểm tra điều kiện phát activation.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3; trigger semantics được kiểm riêng sau khi chốt

#### BRG-04 — Permanent open/close

- **Objective:** Permanent open/close
- **Preconditions:** Bridge state/effect are semantic fixture inputs.
- **Input/fixture:** Hai subcase: closed + effect `open`; open + effect `close`
- **Steps:** Gọi effect handler hai lần với cùng effect mỗi subcase
- **Expected result:** [ĐỀ BÀI] Trạng thái được set theo fixed state tương ứng; cùng effect lặp lại không đảo trạng thái. [JSON] Effect values là `open`/`close`. Khả năng switch khác ghi đè vẫn cần xác minh.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3; `levels.json`

#### BRG-05 — Một switch đổi nhiều bridge được liên kết

- **Objective:** Một switch đổi nhiều bridge được liên kết
- **Preconditions:** Semantic effect-handler fixture; three bridges closed; one switch links Bridge A and Bridge B, not Bridge C.
- **Input/fixture:** Switch S1 has toggle effect on {A,B}; all three bridges start closed.
- **Steps:** Send one activation event to the effect handler; inspect A, B, and C.
- **Expected result:** [ĐỀ BÀI] A and B become open; unrelated C remains closed. This tests linked-effect application only, not switch trigger timing.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

### SPL

#### SPL-01 — Tạo hai cube ở destination

- **Objective:** Tạo hai cube ở destination
- **Preconditions:** Semantic split state and destinations; unresolved rules remain pending.
- **Input/fixture:** Block đứng trên split switch; hai destination semantic là hai tile hỗ trợ phân biệt
- **Steps:** Activate switch
- **Expected result:** [ĐỀ BÀI] Block split thành hai cube; tập vị trí cube sau split khớp tập hai predefined positions. Không assert thứ tự cube/active cube.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

#### SPL-02 — Chuyển active cube

- **Objective:** Chuyển active cube
- **Preconditions:** Semantic split state and destinations; unresolved rules remain pending.
- **Input/fixture:** Two supported single cubes: A at (1,1), B at (4,4); active cube is A; (4,5) is supported floor.
- **Steps:** Issue the semantic control-switch action (Spacebar is an example in the PDF).; Move the newly active cube one tile right.; Inspect both cube positions and active selection.
- **Expected result:** [ĐỀ BÀI] Control switches to the other cube; only the active cube moves and the inactive cube remains at its original coordinate. No key encoding, animation, or terminal-state policy is asserted.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

#### SPL-03 — Cube đơn không thắng

- **Objective:** Cube đơn không thắng
- **Preconditions:** Semantic split state and destinations; unresolved rules remain pending.
- **Input/fixture:** Một cube đứng trên goal, cube còn lại ở nơi khác
- **Steps:** Goal test
- **Expected result:** [ĐỀ BÀI] Cube đơn không thể complete stage.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

#### SPL-04 — Active cube không di chuyển vào void

- **Objective:** Active cube không di chuyển vào void
- **Preconditions:** Both single cubes are supported; the active cube is at (1,1), the inactive cube at (4,4), and the active cube's target cell (1,2) is void.
- **Input/fixture:** Hai cube đơn được hỗ trợ; active cube tại (1,1), ô (1,2) là void, inactive cube tại (4,4) trên floor.
- **Steps:** Gửi semantic move-right cho active cube; đọc successor và vị trí hai cube.
- **Expected result:** [ĐỀ BÀI] Không có successor hợp lệ vì cube sẽ chiếm void; nếu engine giữ state khi từ chối move thì cả hai vị trí không đổi. Không assert animation hoặc cách biểu diễn failure.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.1–2.3, tr. 2–3

### MRG

#### MRG-01 — Merge khi hai cube kề ngang

- **Objective:** Merge khi hai cube kề ngang
- **Preconditions:** Two supported single cubes occupy the stated cells; merge invocation policy is unresolved.
- **Input/fixture:** Hai cube tại `(1,1)` và `(1,2)`, hai ô đều floor
- **Steps:** Đưa state đã split có hai cube này qua bước “resolve merge” của engine
- **Expected result:** [ĐỀ BÀI] Kết quả là block chuẩn nằm ngang, footprint `{(1,1),(1,2)}`. [CẦN XÁC MINH] Khi nào engine gọi resolve merge, anchor nội bộ và active identity sau merge.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** PDF §2.5, tr. 3; Proposal §8.1, §8.4
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### MRG-02 — Merge khi hai cube kề dọc

- **Objective:** Merge khi hai cube kề dọc
- **Preconditions:** Two supported single cubes occupy the stated cells; merge invocation policy is unresolved.
- **Input/fixture:** Hai cube tại `(1,1)` và `(2,1)`, hai ô đều floor
- **Steps:** Đưa state đã split có hai cube này qua bước “resolve merge” của engine
- **Expected result:** [ĐỀ BÀI] Kết quả là block chuẩn nằm dọc, footprint `{(1,1),(2,1)}`. [CẦN XÁC MINH] Khi nào engine gọi resolve merge, anchor nội bộ và active identity sau merge.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** PDF §2.5, tr. 3; Proposal §8.1, §8.4
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### MRG-03 — Không merge khi cube không kề nhau

- **Objective:** Không merge khi cube không kề nhau
- **Preconditions:** Two supported single cubes occupy distinct cells with one cell between them; invoke the semantic merge-eligibility check.
- **Input/fixture:** Cube A at (1,1), cube B at (1,3); both occupied tiles are supported; (1,2) is between them.
- **Steps:** Evaluate merge eligibility/state normalization.
- **Expected result:** [ĐỀ BÀI] The cubes remain separate because they are not on adjacent tiles. Does not specify when the engine checks for merging.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §2.5, tr. 3

### LV

#### LV-01 — Tải một level hợp lệ

- **Objective:** Tải một level hợp lệ
- **Preconditions:** Validator receives the stated fixture or complete dataset.
- **Input/fixture:** Một level theo shape hiện hành, một `S`, một `G`, rows đều string
- **Steps:** Parse và validate
- **Expected result:** [JSON] Level hợp lệ được chuyển thành board/state; tọa độ start/goal khớp map. Legend và default behavior cần xác nhận.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** PDF §3.1; `levels.json`; Proposal §10.1
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### LV-DATA-01 — Audit cấu trúc toàn bộ dataset

- **Objective:** Audit cấu trúc toàn bộ dataset
- **Preconditions:** Validator receives the stated fixture or complete dataset.
- **Input/fixture:** All 33 entries of levels.json; the complete structural inventory is in levels-test-cases.json.
- **Steps:** Đọc từng level, kiểm tra parse/schema hình dạng, hàng chữ nhật trong từng stage, đúng một `S`/`G`, ký hiệu quan sát được, tọa độ bridge khớp ký hiệu `B`, switch/destination/reference tọa độ nội bộ hợp lệ
- **Expected result:** [JSON] Cả 33 level thỏa các invariant cấu trúc ghi trong test data. Case này không kiểm tra khả năng giải, tính hợp lệ theo luật chưa xác minh hay kết quả solver.
- **Type:** unit
- **Status:** READY
- **Source basis:** `levels.json` (audit dữ liệu); PDF §2.1, tr. 2 (single start/goal)

#### LV-02 — JSON sai cú pháp

- **Objective:** JSON sai cú pháp
- **Preconditions:** Validator receives the stated fixture or complete dataset.
- **Input/fixture:** JSON bị cắt/thiếu dấu phân cách
- **Steps:** Gọi loader
- **Expected result:** [ĐỀ XUẤT] Reject có diagnostic, không crash không kiểm soát.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** Proposal §10.1; policy đề xuất
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### LV-03 — Thiếu trường bắt buộc

- **Objective:** Thiếu trường bắt buộc
- **Preconditions:** Validator receives the stated fixture or complete dataset.
- **Input/fixture:** Thiếu `rows`, hoặc level không phải object
- **Steps:** Validate
- **Expected result:** [ĐỀ XUẤT] Reject với lỗi nêu trường/entry.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** PDF §3.1; `levels.json`; Proposal §10.1
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### LV-04 — Kiểu dữ liệu rows sai

- **Objective:** Kiểu dữ liệu rows sai
- **Preconditions:** Validator receives the stated fixture or complete dataset.
- **Input/fixture:** `rows` không phải list string hoặc chứa phần tử không phải string
- **Steps:** Validate
- **Expected result:** [ĐỀ XUẤT] Reject.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** `levels.json`; Proposal §10.1
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### LV-05 — Start/goal thiếu hoặc lặp

- **Objective:** Start/goal thiếu hoặc lặp
- **Preconditions:** Validator receives the stated fixture or complete dataset.
- **Input/fixture:** Map có 0 hoặc >1 `S`; lặp lại tương tự cho `G`
- **Steps:** Validate
- **Expected result:** [ĐỀ XUẤT] Reject vì trạng thái/đích không đơn trị. PDF mô tả một start và một goal.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** PDF §2.1, tr. 2
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### LV-06 — Ký hiệu không biết

- **Objective:** Ký hiệu không biết
- **Preconditions:** Validator receives the stated fixture or complete dataset.
- **Input/fixture:** Thêm ký tự ngoài legend đã được thống nhất
- **Steps:** Validate
- **Expected result:** [ĐỀ XUẤT] Reject hoặc cảnh báo theo policy được chốt; không âm thầm coi là floor.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** `levels.json`; policy legend cần chốt
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### LV-07 — Tọa độ ngoài board/âm

- **Objective:** Tọa độ ngoài board/âm
- **Preconditions:** Validator receives the stated fixture or complete dataset.
- **Input/fixture:** Bridge, switch hoặc destination ngoài kích thước rows
- **Steps:** Validate
- **Expected result:** [ĐỀ XUẤT] Reject với đường dẫn trường và tọa độ lỗi.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** `levels.json`; Proposal §10.1
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### LV-08 — Bridge metadata không nhất quán

- **Objective:** Bridge metadata không nhất quán
- **Preconditions:** Validator receives the stated fixture or complete dataset.
- **Input/fixture:** Switch effect tham chiếu ID không có trong `bridges`; `initially_open` có ID lạ; bridge coordinate không tương ứng tile bridge
- **Steps:** Validate
- **Expected result:** [ĐỀ XUẤT] Reject hoặc diagnostic theo policy. Cần chốt xem glyph `B` hay metadata là nguồn sự thật.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** `levels.json`; Proposal §10.1
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### LV-09 — Switch/effect malformed

- **Objective:** Switch/effect malformed
- **Preconditions:** Validator receives the stated fixture or complete dataset.
- **Input/fixture:** Switch thiếu `cell`, vừa có `effects` và `destinations`, effect không thuộc enum hiện hành
- **Steps:** Validate
- **Expected result:** [ĐỀ XUẤT] Reject; enum hiện hành quan sát được là `toggle/open/close`, chưa phải schema versioned.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** `levels.json`; Proposal §10.1
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### LV-10 — Split destination malformed

- **Objective:** Split destination malformed
- **Preconditions:** Validator receives the stated fixture or complete dataset.
- **Input/fixture:** Destination sai dạng/không đủ hai tọa độ, hoặc ngoài board/trên void; `active` ngoài 0/1
- **Steps:** Validate
- **Expected result:** [ĐỀ XUẤT] Reject hoặc yêu cầu xác nhận policy; ý nghĩa `active`/destination chưa được định nghĩa.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** `levels.json`; Proposal §10.1
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### LV-11 — Hàng level không đồng nhất độ rộng

- **Objective:** Hàng level không đồng nhất độ rộng
- **Preconditions:** Validator receives a syntactically valid level object; row-shape policy is not yet finalized.
- **Input/fixture:** Rows contain strings of unequal lengths, e.g. ["S..", "..G "].
- **Steps:** Validate and record outcome/diagnostic.
- **Expected result:** [ĐỀ XUẤT] A rectangular-grid validator should reject or explicitly normalize ragged rows. Exact policy and diagnostic are not stated in PDF; no pass/fail oracle until policy is chosen.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** PDF §2.1, tr. 2; Proposal §10.1
- **Pending reason:** The official level schema and ragged-row validation policy are not defined.

#### LV-12 — Tọa độ bridge/switch bị lặp

- **Objective:** Tọa độ bridge/switch bị lặp
- **Preconditions:** Validator receives a level with otherwise valid rows and references; duplicate-coordinate policy is not finalized.
- **Input/fixture:** Subcase A: a coordinate occurs twice in bridge metadata. Subcase B: two switch records use the same cell.
- **Steps:** Validate each subcase independently; record field/coordinate diagnostic.
- **Expected result:** [ĐỀ XUẤT] Detect duplicate coordinates and apply the documented policy. PDF does not define duplicate metadata handling; exact reject/warn result is pending.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** `levels.json`; Proposal §10.1
- **Pending reason:** The level schema does not state whether duplicate metadata coordinates are errors or warnings.

### SOL

#### SOL-01 — BFS trả path ít action nhất

- **Objective:** BFS trả path ít action nhất
- **Preconditions:** BFS nhận được finite successor graph; mỗi edge cost bằng 1
- **Input/fixture:** Directed graph: `S→A`, `A→G`, `S→G`; goal `G`
- **Steps:** Run BFS; đếm path action
- **Expected result:** [ĐỀ BÀI] Path tìm được hợp lệ và `solution_length=1`; không chọn path 2 bước.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §3.2, tr. 5

#### SOL-02 — DFS/IDS dừng trên cycle

- **Objective:** DFS/IDS dừng trên cycle
- **Preconditions:** Biến thể DFS hoặc IDS được ghi rõ; graph hữu hạn
- **Input/fixture:** `S→A`, `A→S`; không có goal reachable
- **Steps:** Run solver; quan sát termination/status
- **Expected result:** [ĐỀ BÀI] Không lặp vô hạn; trả not-found khi search kết thúc đầy đủ. Với IDS, cấu hình depth limit/điều kiện tăng phải được ghi.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §3.3, tr. 5; Proposal §16.2

#### SOL-03 — UCS tối ưu tổng cost

- **Objective:** UCS tối ưu tổng cost
- **Preconditions:** UCS nhận non-negative edge costs
- **Input/fixture:** `S→A (1)`, `A→G (8)`; `S→B (2)`, `B→C (1)`, `C→G (1)`
- **Steps:** Run UCS; tính lại cost path
- **Expected result:** [ĐỀ BÀI] Chọn path `S→B→C→G` cost 4 thay path cost 9. Cost values là fixture test, không phải cost gameplay được mặc định.
- **Type:** unit
- **Status:** READY
- **Source basis:** PDF §3.4, tr. 5

#### SOL-04 — A* và kiểm chứng heuristic theo cost

- **Objective:** A* và kiểm chứng heuristic theo cost
- **Preconditions:** Cost và heuristic được chốt; finite graph; nếu test optimality thì heuristic admissible theo cost
- **Input/fixture:** Dùng graph SOL-03 và exact remaining costs `h*(G)=0`, `h*(C)=1`, `h*(B)=2`, `h*(A)=8`, `h*(S)=4` làm oracle.
- **Steps:** Tính shortest remaining cost độc lập; kiểm tra `h(s)≤h*(s)` cho mọi state; kiểm tra consistency nếu implementation/report tuyên bố; chạy A*, tính lại path cost
- **Expected result:** [ĐỀ BÀI] Heuristic phải được giải thích và phân tích theo cost. [CẦN XÁC MINH] Chưa thể assert A* optimality với heuristic thật trước khi heuristic/cost được chọn; fixture oracle tự nó không chỉ định heuristic implementation.
- **Type:** unit
- **Status:** PENDING
- **Source basis:** PDF §3.5, tr. 5–6
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

### INT

#### INT-01 — Loader → engine

- **Objective:** Loader → engine
- **Preconditions:** Schema fixture được validator chấp nhận
- **Input/fixture:** Mini level: floor line `(1,1)…(1,4)`, `S=(1,1)`, `G=(1,4)`
- **Steps:** Load; tạo state ban đầu; đọc footprint/tile
- **Expected result:** Start là standing tại S; board và goal map đúng fixture. [ĐỀ BÀI] Start standing; [CẦN XÁC MINH] zero-based coordinate contract.
- **Type:** integration
- **Status:** PENDING
- **Source basis:** PDF §2.1, §3.1; Proposal §10.1
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### INT-02 — Engine transition → solver path → replay

- **Objective:** Engine transition → solver path → replay
- **Preconditions:** One-path mini board with agreed shared state/goal API; same fixture supplied to BFS, chosen DFS/IDS, UCS, and A*.
- **Input/fixture:** Semantic board: floor cells (1,1), (1,2), (1,3), (1,4); start standing at (1,1); goal at (1,4); all other cells void; no special tiles.
- **Steps:** Run each required solver on the identical fixture.; Replay each returned path through the shared engine and record length/cost.
- **Expected result:** [ĐỀ BÀI] Every solver returns a legal path that replays to the standing goal. This fixture has the unique path RIGHT, RIGHT; this says nothing about dataset levels.
- **Type:** integration
- **Status:** READY
- **Source basis:** PDF §3.1–3.5, tr. 4–6; Proposal §8, §16.2

#### INT-03 — Loader → switch/bridge → engine → solver replay

- **Objective:** Loader → switch/bridge → engine → solver replay
- **Preconditions:** Switch activation/effect order and glyph/schema mapping have been decided.
- **Input/fixture:** Mini board floor `(1,1),(1,2),(1,3)`; start `(1,1)`; soft switch `(1,2)` có effect `open` lên `bridge-0`; goal là bridge `(1,4)`, initially closed
- **Steps:** Load the semantic fixture.; Run each solver on the same fixture.; Replay the returned path and inspect bridge state after each transition.
- **Expected result:** [CẦN XÁC MINH] After trigger semantics are decided, each solver must return a legal path through the opened bridge and replay to the goal. No effect ordering is assumed here.
- **Type:** integration
- **Status:** PENDING
- **Source basis:** PDF §2.5, §3.1; Proposal §8.4
- **Pending reason:** Pending until switch trigger, effect order, and loader mapping are confirmed; see TEST_SPECIFICATION.md §5.

#### INT-04 — Solver dùng bridge state trong state key

- **Objective:** Solver dùng bridge state trong state key
- **Preconditions:** Integration components and fixture are as stated.
- **Input/fixture:** Board một hàng: floor `(1,1),(1,2)`, bridge `(1,3)`, floor `(1,4),(1,5)`; goal `(1,5)`. Tạo hai input states standing `(1,2)`, một bridge closed và một open. Các ô khác void.
- **Steps:** So state keys; chạy solver từ từng state. Từ open state, expected path `RIGHT, RIGHT`; từ closed state không có successor sang phải và không có đường khác tới goal.
- **Expected result:** [ĐỀ BÀI] Keys phải khác dù block placement giống nhau. Open state có path qua bridge; closed state không có path. Không khẳng định cụ thể state-key encoding.
- **Type:** integration
- **Status:** READY
- **Source basis:** PDF §3.1, tr. 4; fixture do test thiết kế

#### INT-05 — Split state/control/solver/replay

- **Objective:** Split state/control/solver/replay
- **Preconditions:** Semantic split fixture; solver action/control/merge rules đã được chốt trước khi chạy phần path
- **Input/fixture:** Board có floor/start `(1,1)`, floor `(2,1),(3,1)`, split trigger `(3,1)`, destination floor `(4,1),(4,3)`, goal `(5,3)`; mọi ô khác void. Destinations là semantic fixture, không phải claim về JSON field mapping.
- **Steps:** Load; đi `DOWN` tới trigger; kiểm tra tập cube positions `{(4,1),(4,3)}`; sau khi control/merge actions được quyết định, chạy solver và replay path
- **Expected result:** [ĐỀ BÀI] Split tạo hai cube ở predefined positions; solver cần hỗ trợ split/rejoin. Phần loader/trigger có thể kiểm tra với tập destination không thứ tự. Solver/replay steps **pending**, vì control, merge và trạng thái goal cần hoàn tất trước khi xác định đường đi.
- **Type:** integration
- **Status:** PENDING
- **Source basis:** PDF §2.5, §3.1; Proposal §8.1–8.4
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### INT-06 — No-solution/termination và repeated states

- **Objective:** No-solution/termination và repeated states
- **Preconditions:** Integration components and fixture are as stated.
- **Input/fixture:** Board finite; floor square `{(0,0),(0,1),(1,0),(1,1)}` with start `(0,0)`; isolated goal `(4,4)`; all other cells void
- **Steps:** Load fixture; run each solver using its documented duplicate/termination policy; inspect completion/status
- **Expected result:** [ĐỀ BÀI] Goal unreachable; DFS/IDS must handle repeated states. Search should terminate on this finite reachable component when duplicate handling is correct. Record `not found`, not “proved unsolvable” for a timeout. Exact timeout/resource policy remains open.
- **Type:** integration
- **Status:** PENDING
- **Source basis:** PDF §3.3, §3.6; Proposal §10.3, §16.2
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.

#### INT-07 — Level loader → game model cho toàn dataset

- **Objective:** Level loader → game model cho toàn dataset
- **Preconditions:** Official project schema, glyph mapping, and default bridge semantics have been agreed.
- **Input/fixture:** All 33 entries from levels.json.
- **Steps:** Load each entry; compare dimensions, start/goal, special-tile metadata, and bridge references with the source record; collect failures by stage and field.
- **Expected result:** [CẦN XÁC MINH] Once the schema/mapping is approved, all entries intended for reuse must load according to that contract or produce a specific diagnostic. Do not run a solver or claim solvability.
- **Type:** integration
- **Status:** PENDING
- **Source basis:** PDF §3.1, tr. 4; Proposal §7.1, §10.1–10.3; `levels.json`
- **Pending reason:** Loader schema and glyph/default-state mappings are not finalized; this is separate from the raw structural audit LV-DATA-01.

#### INT-08 — State key phân biệt split states ảnh hưởng hành động tương lai

- **Objective:** State key phân biệt split states ảnh hưởng hành động tương lai
- **Preconditions:** A semantic state-key API is available. All compared states use the same board and bridge configuration. Cube identities are fixture labels only; no implementation encoding is assumed.
- **Input/fixture:** Pair A: same two cube positions with different active cube. Pair B: same active cube selection with one cube at a different supported coordinate.
- **Steps:** Compute the semantic state key for each state in both pairs and compare each pair.
- **Expected result:** [ĐỀ XUẤT] Proposal requires state keys to include information that changes future actions; PDF says the split cubes are controlled one at a time. Therefore, states differing in active cube or cube position must have distinct keys when that information changes future actions. No particular key encoding or cube storage order is required.
- **Type:** integration
- **Status:** READY
- **Source basis:** Proposal §8.1, §8.3, §8.6; PDF §2.5, tr. 3

### GUI

#### GUI-01 — Hiển thị board, tile và block orientation

- **Objective:** Hiển thị board, tile và block orientation
- **Preconditions:** GUI loads a semantic fixture; visual acceptance can be manual if UI automation is unsuitable.
- **Input/fixture:** Fixture contains floor, void, goal, fragile, bridge, switches, and legal states showing standing, horizontal, and vertical block orientations.
- **Steps:** Load fixture; inspect tile categories, block placement, and each orientation state.
- **Expected result:** [ĐỀ BÀI] GUI displays the board/game; demo presents the different tile types and block orientations. No pixel-perfect assertion.
- **Type:** integration
- **Status:** READY
- **Source basis:** PDF §3.1, tr. 4; PDF §3.7, tr. 7; Proposal §12

#### GUI-02 — New Game và Restart

- **Objective:** New Game và Restart
- **Preconditions:** A level fixture has a known initial state and at least one legal move.
- **Input/fixture:** Use New Game to start the selected stage; make a move; use Restart.
- **Steps:** Compare stage and full game state before and after each control.
- **Expected result:** [ĐỀ BÀI] New Game and Restart controls are available; Restart restores the initial state of the current stage, and New Game starts the selected stage.
- **Type:** integration
- **Status:** READY
- **Source basis:** Proposal §4.1, FR-18, §12

#### GUI-03 — Điều khiển thủ công và phản hồi terminal

- **Objective:** Điều khiển thủ công và phản hồi terminal
- **Preconditions:** GUI uses the shared engine; semantic fixture has legal, illegal, and winning states.
- **Input/fixture:** Send Up, Down, Left, Right inputs; exercise one illegal action and a path to the standing goal.
- **Steps:** Compare the displayed state to engine state after each action; inspect terminal status.
- **Expected result:** [ĐỀ BÀI] Four directions follow the movement rules; an illegal move does not become a valid successor; standing on the goal wins. Exact visual wording is a UI decision.
- **Type:** integration
- **Status:** READY
- **Source basis:** PDF §2.3–2.4, tr. 2; PDF §3.1, tr. 4

#### GUI-04 — Gọi solver và replay path từ GUI

- **Objective:** Gọi solver và replay path từ GUI
- **Preconditions:** All four required solver options are integrated; use the deterministic mini-level in INT-02.
- **Input/fixture:** Run BFS, the selected DFS or IDS, UCS, and A* through their GUI controls.
- **Steps:** For each solver, observe run status and request playback of the returned path.
- **Expected result:** [ĐỀ BÀI] Controls invoke the solvers; every displayed/replayed path is legal in the shared engine and ends at the standing goal. Do not assert runtime or animation duration.
- **Type:** integration
- **Status:** READY
- **Source basis:** PDF §3.1, tr. 4; PDF §3.7, tr. 7; Proposal §12

#### GUI-05 — Checklist chấp nhận video demo

- **Objective:** Checklist chấp nhận video demo
- **Preconditions:** A build and demo recording are available; public URL is included in the report.
- **Input/fixture:** Video and report URL.
- **Steps:** Review the video and open the submitted link.
- **Expected result:** [ĐỀ BÀI] Video demonstrates GUI layout/tile types/orientations/controls, manual play including switch and win/loss, solver execution and solution/replay; it has English or Vietnamese narration/subtitles and a public link in the report.
- **Type:** acceptance
- **Status:** READY
- **Source basis:** PDF §3.7, tr. 7

### BEN

#### BEN-01 — Khóa fixed set

- **Objective:** Khóa fixed set
- **Preconditions:** Manifest được duyệt; loader/schema/semantics chốt
- **Input/fixture:** Danh sách ứng viên §4.1 hoặc manifest thay thế có lý do
- **Steps:** Lưu manifest/version/hash; chạy preflight validation
- **Expected result:** [ĐỀ BÀI] Cùng fixed set cho các thuật toán. [CẦN XÁC MINH] Solvability được ghi nhận thực nghiệm; không được suy ra từ kích thước.
- **Type:** benchmark
- **Status:** PENDING
- **Source basis:** PDF §3.6, tr. 6
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.
- **Algorithms:** BFS, DFS or IDS, UCS, A*
- **Metrics:** search_time_seconds, peak_memory_bytes, expanded_nodes, solution_length_actions, status, path_cost_if_applicable
- **Candidate levels:** Stage 01, Stage 03, Stage 04, Stage 02, Stage 05, Stage 08, Stage 15, Stage 23, Stage 30; candidates only; no solvability claim.
- **Evaluation:** Use one manifest, dataset version, rules, cost definition, configuration and resource limits across algorithms; replay returned paths; do not enter results before execution.

#### BEN-02 — Run BFS

- **Objective:** Run BFS
- **Preconditions:** Common protocol §4.2 đã chốt
- **Input/fixture:** Từng level manifest
- **Steps:** Chạy BFS; lưu từng run/result
- **Expected result:** Ghi đủ time, memory, expanded nodes, solution length; kiểm tra path nếu found.
- **Type:** benchmark
- **Status:** PENDING
- **Source basis:** PDF §3.2, §3.6
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.
- **Algorithms:** BFS, DFS or IDS, UCS, A*
- **Metrics:** search_time_seconds, peak_memory_bytes, expanded_nodes, solution_length_actions, status, path_cost_if_applicable
- **Candidate levels:** Stage 01, Stage 03, Stage 04, Stage 02, Stage 05, Stage 08, Stage 15, Stage 23, Stage 30; candidates only; no solvability claim.
- **Evaluation:** Use one manifest, dataset version, rules, cost definition, configuration and resource limits across algorithms; replay returned paths; do not enter results before execution.

#### BEN-03 — Run DFS hoặc IDS

- **Objective:** Run DFS hoặc IDS
- **Preconditions:** Biến thể được chọn; cycle/termination policy công bố
- **Input/fixture:** Cùng manifest
- **Steps:** Chạy biến thể; lưu run/result
- **Expected result:** Ghi cùng metrics/status; không yêu cầu path tối ưu cho DFS. Nếu IDS, ghi depth behavior.
- **Type:** benchmark
- **Status:** PENDING
- **Source basis:** PDF §3.3, §3.6
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.
- **Algorithms:** BFS, DFS or IDS, UCS, A*
- **Metrics:** search_time_seconds, peak_memory_bytes, expanded_nodes, solution_length_actions, status, path_cost_if_applicable
- **Candidate levels:** Stage 01, Stage 03, Stage 04, Stage 02, Stage 05, Stage 08, Stage 15, Stage 23, Stage 30; candidates only; no solvability claim.
- **Evaluation:** Use one manifest, dataset version, rules, cost definition, configuration and resource limits across algorithms; replay returned paths; do not enter results before execution.

#### BEN-04 — Run UCS

- **Objective:** Run UCS
- **Preconditions:** Cost function công bố trước batch
- **Input/fixture:** Cùng manifest và transition graph
- **Steps:** Chạy UCS; lưu run/result/path cost
- **Expected result:** Path phải hợp lệ; cost tính lại khớp cost function. Tối ưu chỉ so theo cost.
- **Type:** benchmark
- **Status:** PENDING
- **Source basis:** PDF §3.4, §3.6
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.
- **Algorithms:** BFS, DFS or IDS, UCS, A*
- **Metrics:** search_time_seconds, peak_memory_bytes, expanded_nodes, solution_length_actions, status, path_cost_if_applicable
- **Candidate levels:** Stage 01, Stage 03, Stage 04, Stage 02, Stage 05, Stage 08, Stage 15, Stage 23, Stage 30; candidates only; no solvability claim.
- **Evaluation:** Use one manifest, dataset version, rules, cost definition, configuration and resource limits across algorithms; replay returned paths; do not enter results before execution.

#### BEN-05 — Run A* và đối chiếu

- **Objective:** Run A* và đối chiếu
- **Preconditions:** Heuristic/cost công bố; luận cứ admissible/consistent nêu rõ nếu tuyên bố tối ưu
- **Input/fixture:** Cùng manifest
- **Steps:** Chạy A*; lưu run/result/path cost; replay path
- **Expected result:** Ghi cùng metrics; tính lại cost/path. Không tuyên bố tối ưu nếu heuristic/cost không bảo đảm.
- **Type:** benchmark
- **Status:** PENDING
- **Source basis:** PDF §3.5–3.6
- **Pending reason:** The expected behavior or execution policy depends on an open game-rule, schema, solver, or benchmark decision; see TEST_SPECIFICATION.md §5 and readiness table.
- **Algorithms:** BFS, DFS or IDS, UCS, A*
- **Metrics:** search_time_seconds, peak_memory_bytes, expanded_nodes, solution_length_actions, status, path_cost_if_applicable
- **Candidate levels:** Stage 01, Stage 03, Stage 04, Stage 02, Stage 05, Stage 08, Stage 15, Stage 23, Stage 30; candidates only; no solvability claim.
- **Evaluation:** Use one manifest, dataset version, rules, cost definition, configuration and resource limits across algorithms; replay returned paths; do not enter results before execution.

#### BEN-06 — Export benchmark metrics không mất dữ liệu

- **Objective:** Export benchmark metrics không mất dữ liệu
- **Preconditions:** Serializer format and metric field names are documented; fixture values are synthetic sentinels, not measurements.
- **Input/fixture:** Synthetic records cover a found run and a not-found/timeout run; include algorithm, level, all four required metrics, status, and null solution length where no path exists.
- **Steps:** Export to the supported JSON/CSV format; parse it back; compare each field to the synthetic fixture.
- **Expected result:** [ĐỀ BÀI] Export retains search time, peak memory, expanded nodes, and solution length/status; unavailable solution length is represented as missing/null, not a measured zero. No fixture value is a benchmark result.
- **Type:** benchmark
- **Status:** READY
- **Source basis:** PDF §3.2, §3.6–3.7; Proposal FR-16–17, §11
- **Algorithms:** BFS, DFS or IDS, UCS, A*
- **Metrics:** search_time, peak_memory, expanded_nodes, solution_length

#### BEN-07 — Kiểm tra tính đầy đủ của bảng/biểu đồ report

- **Objective:** Kiểm tra tính đầy đủ của bảng/biểu đồ report
- **Preconditions:** A synthetic result matrix is used only to test report generation; manifest and algorithm labels are known.
- **Input/fixture:** Synthetic records for each manifest/algorithm pair with required metrics and status.
- **Steps:** Generate/check summary table, comparison charts, labels/units/legend, and written discussion.
- **Expected result:** [ĐỀ BÀI] Report presents measurement tables, comparison charts, and discussion of strengths/weaknesses for the common test set. This case asserts artifact completeness, not a specific performance conclusion.
- **Type:** benchmark
- **Status:** READY
- **Source basis:** PDF §3.6, tr. 6–7; Proposal §11.3–11.5
- **Algorithms:** BFS, DFS or IDS, UCS, A*
- **Metrics:** search_time, peak_memory, expanded_nodes, solution_length


## Inventory of all 33 levels

Structural dataset inventory only; it is not a difficulty ranking and contains no solver outcomes.

| Level | Rows × columns | Glyph counts (non-space) | Switch records | Bridge groups | Initially open |
|---|---:|---|---:|---:|---|
| Stage 01 | 6 × 10 | `.`=33, `S`=1, `G`=1 | 0 | 0 | none |
| Stage 02 | 6 × 15 | `.`=55, `S`=1, `G`=1, `B`=4, `o`=1, `h`=1 | 2 | 2 | none |
| Stage 03 | 6 × 15 | `.`=42, `S`=1, `G`=1 | 0 | 0 | none |
| Stage 04 | 9 × 14 | `.`=36, `S`=1, `G`=1, `F`=31 | 0 | 0 | none |
| Stage 05 | 10 × 15 | `.`=61, `S`=1, `G`=1, `B`=6, `o`=4 | 4 | 3 | bridge-0, bridge-1, bridge-2 |
| Stage 06 | 10 × 15 | `.`=53, `S`=1, `G`=1 | 0 | 0 | none |
| Stage 07 | 8 × 15 | `.`=52, `S`=1, `G`=1, `B`=1, `h`=1 | 1 | 1 | none |
| Stage 08 | 9 × 15 | `.`=51, `S`=1, `G`=1, `x`=1 | 1 | 0 | none |
| Stage 09 | 5 × 15 | `.`=36, `S`=1, `G`=1, `x`=1 | 1 | 0 | none |
| Stage 10 | 10 × 14 | `.`=44, `S`=1, `G`=1, `B`=6, `o`=1, `h`=1, `x`=1 | 3 | 3 | none |
| Stage 11 | 10 × 12 | `.`=46, `S`=1, `G`=1, `B`=2, `o`=1 | 1 | 1 | bridge-0 |
| Stage 12 | 10 × 13 | `.`=54, `S`=1, `G`=1, `B`=2, `h`=2 | 2 | 2 | none |
| Stage 13 | 10 × 14 | `.`=58, `S`=1, `G`=1, `F`=22 | 0 | 0 | none |
| Stage 14 | 10 × 14 | `.`=60, `S`=1, `G`=1, `B`=4, `h`=2 | 2 | 2 | none |
| Stage 15 | 10 × 15 | `.`=57, `S`=1, `G`=1, `B`=8, `o`=3, `h`=1, `x`=1 | 5 | 4 | bridge-0, bridge-3 |
| Stage 16 | 8 × 13 | `.`=29, `S`=1, `G`=1, `B`=4, `h`=2, `x`=5 | 7 | 2 | none |
| Stage 17 | 10 × 15 | `.`=59, `S`=1, `G`=1, `B`=4, `o`=1, `h`=4 | 5 | 4 | none |
| Stage 18 | 9 × 15 | `.`=44, `S`=1, `G`=1, `B`=7, `o`=5, `h`=1 | 6 | 4 | none |
| Stage 19 | 10 × 15 | `.`=57, `S`=1, `G`=1, `B`=4, `o`=3 | 3 | 2 | bridge-1 |
| Stage 20 | 10 × 15 | `.`=52, `S`=1, `G`=1, `B`=6, `o`=5, `x`=1 | 6 | 3 | bridge-0 |
| Stage 21 | 10 × 15 | `.`=55, `S`=1, `G`=1, `B`=2, `h`=2 | 2 | 2 | none |
| Stage 22 | 10 × 14 | `.`=50, `S`=1, `G`=1, `B`=3, `o`=2, `h`=2 | 4 | 3 | bridge-2 |
| Stage 23 | 10 × 15 | `.`=56, `S`=1, `G`=1, `F`=18, `B`=8, `o`=3, `h`=1, `x`=1 | 5 | 6 | bridge-0, bridge-4 |
| Stage 24 | 8 × 14 | `.`=46, `S`=1, `G`=1, `B`=6, `h`=4, `x`=1 | 5 | 4 | none |
| Stage 25 | 10 × 14 | `.`=48, `S`=1, `G`=1, `B`=9, `o`=2, `h`=1 | 3 | 5 | bridge-3, bridge-4 |
| Stage 26 | 9 × 14 | `.`=47, `S`=1, `G`=1, `B`=4, `o`=1, `h`=1, `x`=1 | 3 | 3 | bridge-0 |
| Stage 27 | 10 × 15 | `.`=54, `S`=1, `G`=1, `F`=27, `B`=2, `o`=2, `h`=1 | 3 | 2 | bridge-0, bridge-1 |
| Stage 28 | 10 × 15 | `.`=54, `S`=1, `G`=1, `F`=7, `B`=4, `o`=1, `x`=1 | 2 | 2 | bridge-0, bridge-1 |
| Stage 29 | 10 × 15 | `.`=40, `S`=1, `G`=1, `B`=17, `o`=3, `h`=3 | 6 | 9 | bridge-0, bridge-5, bridge-8 |
| Stage 30 | 10 × 15 | `.`=37, `S`=1, `G`=1, `F`=40, `B`=5, `h`=3 | 3 | 4 | bridge-0 |
| Stage 31 | 10 × 15 | `.`=51, `S`=1, `G`=1, `F`=8, `B`=14, `o`=2, `h`=3 | 5 | 6 | bridge-1, bridge-3, bridge-5 |
| Stage 32 | 9 × 14 | `.`=50, `S`=1, `G`=1, `B`=8, `h`=3 | 3 | 4 | bridge-0 |
| Stage 33 | 10 × 15 | `.`=79, `S`=1, `G`=1, `B`=5, `o`=12, `h`=1 | 13 | 3 | bridge-1, bridge-2 |

## Benchmark protocol

All algorithms use the same approved manifest, dataset version, rules, transition model, cost definition, configuration, and resource limits. Collect search time, peak memory, expanded nodes, solution length, status, and applicable path cost. Replay each found path. A timeout is not proof of unsolvability. Candidate levels are not assigned results or presumed difficulty.
