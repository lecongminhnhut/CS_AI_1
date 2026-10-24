"""Luật Bloxorz: mỗi nước đi tạo State mới, không sửa State đầu vào.

Solver dùng initial_state(), successors() và is_goal().
Giao diện dùng transition() để lấy thêm thông tin cho animation.
"""

from .board import Board
from .models import Action, Cell, State, Switch  # Giữ các import cũ từ bloxorz.engine.

DIRECTIONS = {
    Action.UP: (-1, 0), Action.DOWN: (1, 0),
    Action.LEFT: (0, -1), Action.RIGHT: (0, 1),
}


class Engine:
    def __init__(self, board: Board):
        self.board = board
        self._bridge_cells = dict(board.bridge_cells)

    def initial_state(self) -> State:
        """Khối nguyên đứng ở điểm S, cầu theo cấu hình ban đầu."""
        return State((self.board.start,), self.board.initially_open)

    def is_goal(self, state: State) -> bool:
        """Chỉ thắng khi khối nguyên đứng vào đúng ô G."""
        return not state.split and state.cells == (self.board.goal,)

    def step(self, state: State, action: Action | str) -> State | None:
        """Thực hiện một thao tác; trả None nếu rơi hoặc không thể thao tác."""
        return self.transition(state, action)[0]

    def successors(self, state: State):
        """Sinh (thao tác, trạng thái mới) hợp lệ để bốn solver duyệt."""
        for action in Action:
            next_state = self.step(state, action)
            if next_state is not None:
                yield action, next_state

    def transition(self, state: State, action: Action | str):
        """Xử lý nước đi theo thứ tự: lăn → sàn đỡ → công tắc → sàn đỡ."""
        info = {"landing": None, "support": [], "switches": [], "bridges": [],
                "teleport": False, "failure": None, "fallen": []}

        # 1. Tính vị trí đáp xuống, chưa kích hoạt công tắc.
        candidate = self.landing(state, action)
        if candidate is None:
            return None, info
        info["landing"] = {"cells": candidate.cells, "orientation": candidate.orientation,
                           "split": candidate.split, "active": candidate.active}
        info["support"] = self.supporting_cells(candidate)

        # 2. Cần có sàn đỡ trước khi công tắc có thể mở cầu.
        if not self._supported(candidate):
            fragile = candidate.orientation == "standing" and any(
                self.board.tile(cell) == "F" for cell in candidate.cells)
            info["failure"] = "fragile" if fragile else "edge"
            if fragile:
                info["fallen"] = [cell for cell in candidate.cells if self.board.tile(cell) == "F"]
            return None, info

        # 3. Đổi khối điều khiển không nhấn lại công tắc.
        if Action(action) == Action.SWITCH:
            return candidate, info

        # 4. Nhấn công tắc mới, đổi cầu và xử lý tách khối nếu có.
        candidate = self._activate_switches(state, candidate, info)
        info["bridges"] = [{"group": group, "open": group in candidate.bridges}
                           for group in sorted(state.bridges ^ candidate.bridges)]

        # 5. Công tắc có thể vừa đóng cầu ngay dưới khối.
        if not self._supported(candidate):
            info["support"] = self.supporting_cells(candidate)
            info["failure"] = "bridge"
            return None, info
        return candidate, info

    def landing(self, state: State, action: Action | str) -> State | None:
        """Chỉ tính hình học: khối sẽ nằm ở đâu sau thao tác?"""
        action = Action(action)
        if self.is_goal(state):
            return None
        if action == Action.SWITCH:
            if not state.split:
                return None
            return State(state.cells, state.bridges, True, 1 - state.active)
        row_delta, column_delta = DIRECTIONS[action]
        if state.split:
            return self._move_cube(state, row_delta, column_delta)
        return self._roll_block(state, row_delta, column_delta)

    def _roll_block(self, state: State, row_delta: int, column_delta: int) -> State:
        """Lăn khối nguyên theo tư thế đứng, nằm ngang hoặc nằm dọc."""
        row, column = state.cells[0]  # Ô trên cùng hoặc bên trái của khối.
        if state.orientation == "standing":
            cells = ((row + row_delta, column + column_delta),
                     (row + 2 * row_delta, column + 2 * column_delta))
        elif state.orientation == "horizontal" and column_delta:
            cells = ((row, column - 1 if column_delta < 0 else column + 2),)
        elif state.orientation == "vertical" and row_delta:
            cells = ((row - 1 if row_delta < 0 else row + 2, column),)
        else:
            # Lăn ngang cạnh dài: khối vẫn nằm, dịch cả hai ô một bước.
            cells = tuple((r + row_delta, c + column_delta) for r, c in state.cells)
        return self._place_block(cells, state.bridges)

    def _move_cube(self, state: State, row_delta: int, column_delta: int) -> State | None:
        """Khối đã tách: chỉ dịch khối đang chọn một ô."""
        row, column = state.cells[state.active]
        target = (row + row_delta, column + column_delta)
        other = state.cells[1 - state.active]
        if target == other:
            return None
        return self._place_block((target, other), state.bridges, active_cell=target)

    @staticmethod
    def _place_block(cells: tuple[Cell, ...], bridges: frozenset[str],
                     active_cell: Cell | None = None) -> State:
        """Sắp xếp tọa độ; hai khối con liền cạnh tự ghép thành khối nằm."""
        cells = tuple(sorted(cells))
        if active_cell is not None:
            first, second = cells
            distance = abs(first[0] - second[0]) + abs(first[1] - second[1])
            if distance != 1:
                return State(cells, bridges, True, cells.index(active_cell))
        return State(cells, bridges)

    def _cell_supports(self, cell: Cell, state: State) -> bool:
        """Ô trống, cầu đóng hoặc sàn yếu dưới khối đứng đều không đỡ được."""
        tile = self.board.tile(cell)
        if tile == " ":
            return False
        if tile == "B" and self._bridge_cells[cell] not in state.bridges:
            return False
        if tile == "F" and state.orientation == "standing":
            return False
        return True

    def _supported(self, state: State) -> bool:
        return all(self._cell_supports(cell, state) for cell in state.cells)

    def supporting_cells(self, state: State) -> tuple[Cell, ...]:
        """Các ô thực sự đỡ khối, giúp giao diện chọn kiểu animation rơi."""
        return tuple(cell for cell in state.cells if self._cell_supports(cell, state))

    def _pressed_switches(self, state: State) -> set[Cell]:
        """Mềm nhận mọi tư thế; nặng/tách chỉ nhận khối nguyên đứng."""
        return {switch.cell for switch in self.board.switches
                if switch.cell in state.cells
                and (switch.kind == "soft" or state.orientation == "standing")}

    def _activate_switches(self, before: State, candidate: State, info: dict) -> State:
        pressed_before = self._pressed_switches(before)
        activated = self._pressed_switches(candidate) - pressed_before
        open_bridges = set(before.bridges)
        self._apply_bridge_effects(activated, open_bridges, info)

        for switch in self.board.switches:
            if switch.kind != "split" or switch.cell not in activated:
                continue
            active_cell = switch.destinations[switch.active_destination]
            candidate = self._place_block(switch.destinations, frozenset(open_bridges), active_cell)
            info["teleport"] = True
            # Khối đáp xuống một công tắc mềm cũng nhấn công tắc đó.
            newly_pressed = self._pressed_switches(candidate) - activated - pressed_before
            self._apply_bridge_effects(newly_pressed, open_bridges, info)
            break
        return State(candidate.cells, frozenset(open_bridges), candidate.split, candidate.active)

    def _apply_bridge_effects(self, activated: set[Cell], open_bridges: set[str], info: dict):
        """Áp dụng công tắc theo thứ tự trong level; chỉ sửa tập cầu tạm thời."""
        for switch in self.board.switches:
            if switch.cell not in activated:
                continue
            info["switches"].append({"cell": switch.cell, "kind": switch.kind})
            effects = tuple((group, switch.effect) for group in switch.bridges) + switch.effects
            for group, effect in effects:
                if effect == "toggle":
                    open_bridges.symmetric_difference_update({group})
                elif effect == "open":
                    open_bridges.add(group)
                else:
                    open_bridges.discard(group)
