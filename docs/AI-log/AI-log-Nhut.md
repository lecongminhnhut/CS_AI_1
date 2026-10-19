# AI-LOG — Bloxorz Solver

## 1. Tổng hợp lịch sử sử dụng AI

| #   | Ngày       | Nội dung                                               | Nhóm                    |
| --- | ---------- | ------------------------------------------------------ | ----------------------- |
| 1   | 2026-10-19 | Hoàn thiện và đồng bộ bộ test cases cho Bloxorz Solver | Testing & Documentation |

---

## 2. Chi tiết lần sử dụng AI

### Entry 1 — Hoàn thiện bộ test cases

| Thông tin              | Chi tiết                                                     |
| ---------------------- | ------------------------------------------------------------ |
| Ngày                   | 2026-10-19                                                   |
| Người thực hiện        | Lê Công Minh Nhựt                                            |
| Feature/nhóm liên quan | Test Cases & Test Documentation                              |
| AI Tool                | OpenAI Codex                                                 |
| Mục đích               | Hoàn thiện coverage, chuẩn hóa và đồng bộ tài liệu test case |
| Git Branch             | Không ghi nhận                                               |

#### Prompt đã dùng

```
Hoàn thiện bộ test cases cho dự án Bloxorz Solver dựa trên đề bài, Proposal, `levels.json` và tài liệu test hiện có.

Phạm vi gồm:

- `test-case/TEST_SPECIFICATION.md`
- `test-case/test-cases.md`
- `test-case/levels-test-cases.json`
- `test-case/README.md`

Yêu cầu bao phủ luật di chuyển, orientation, goal, fragile tiles, switches, bridges, split/merge, validation và loader cho 33 levels, BFS, DFS/IDS, UCS, A\*, integration, GUI và benchmark. Giữ nguyên ID hiện có, bổ sung test khi thực sự thiếu coverage, đánh dấu `PENDING` cho luật chưa được xác nhận, đồng bộ nội dung giữa các file và không triển khai source code, automation hay chạy benchmark.
```

#### Tóm tắt phản hồi của AI

Codex hoàn thiện và đồng bộ bộ tài liệu test case, bổ sung coverage cho GUI, integration, level validation và benchmark. Các test được phân loại `READY` hoặc `PENDING` tùy mức độ xác định của expected result.

Kết quả được ghi nhận trong tài liệu:

- Tổng số test case: **78**.
- `READY`: **53**.
- `PENDING`: **25**.
- Có 13 nhóm test: ORI, MOV, GOAL, FRG, SWT, BRG, SPL, MRG, LV, SOL, INT, GUI và BEN.
- Bộ dữ liệu có 33 levels được kiểm kê về mặt cấu trúc.

#### Phần đã sử dụng / chỉnh sửa / bỏ

| Phần                                           | Quyết định      | Lý do                                                       |
| ---------------------------------------------- | --------------- | ----------------------------------------------------------- |
| Test specification                             | Sử dụng         | Là tài liệu đặc tả chính và traceability                    |
| Markdown test cases                            | Sử dụng         | Giúp nhóm đọc, review và triển khai test                    |
| JSON test cases                                | Sử dụng         | Phục vụ cấu trúc hóa dữ liệu và khả năng automation sau này |
| README                                         | Sử dụng         | Hướng dẫn ngắn gọn cách đọc và sử dụng bộ test              |
| Các luật chưa xác nhận                         | Giữ `PENDING`   | Tránh tự suy diễn expected result                           |
| Source code, test automation, GUI và benchmark | Không thực hiện | Nằm ngoài phạm vi prompt                                    |

#### Cách kiểm chứng

- Đối chiếu số lượng test case và trạng thái trong các tài liệu.
- Kiểm tra tính nhất quán giữa specification, Markdown và JSON.
- JSON được ghi nhận là parse hợp lệ và không có ID trùng lặp.
- Kiểm tra phạm vi nhóm test và các luật còn `PENDING`.

**Lưu ý:** `READY` chỉ có nghĩa là test đủ đặc tả để triển khai, không đồng nghĩa test đã chạy hoặc pass. Không thực hiện kiểm thử phần mềm hay benchmark trong lần sử dụng AI này.

#### Liên kết tệp đầu ra

| Tệp                                                          | Nội dung                       |
| ------------------------------------------------------------ | ------------------------------ |
| [`TEST_SPECIFICATION.md`](../../test-case/TEST_SPECIFICATION.md)   | Đặc tả và phạm vi kiểm thử     |
| [`test-cases.md`](../../test-case/test-cases.md)                   | Danh sách test case chi tiết   |
| [`levels-test-cases.json`](../../test-case/levels-test-cases.json) | Test case ở định dạng JSON     |
| [`README.md`](../../test-case/README.md)                           | Hướng dẫn sử dụng bộ test case |
