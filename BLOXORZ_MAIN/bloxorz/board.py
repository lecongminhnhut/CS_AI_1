"""Bản đồ cố định: ô sàn, cầu, công tắc và kiểm tra cấu hình."""

from dataclasses import dataclass
from pathlib import Path

from .models import Cell, Switch

@dataclass(frozen=True)
class Board:
    """Dữ liệu màn cố định; trạng thái cầu khi chơi nằm trong State."""

    rows: tuple[str, ...]
    start: Cell
    goal: Cell
    bridge_cells: tuple[tuple[Cell, str], ...] = ()
    switches: tuple[Switch, ...] = ()
    initially_open: frozenset[str] = frozenset()

    def tile(self, cell: Cell) -> str:
        r, c = cell
        if 0 <= r < len(self.rows) and 0 <= c < len(self.rows[0]):
            return self.rows[r][c]
        return " "

    def __post_init__(self):
        if not self.rows or not self.rows[0] or any(len(row) != len(self.rows[0]) for row in self.rows):
            raise ValueError("Board must be a nonempty rectangle")
        if any(tile not in " .SGBFohx" for row in self.rows for tile in row):
            raise ValueError("Unknown tile symbol")
        for symbol, cell in (("S", self.start), ("G", self.goal)):
            actual = {(r, c) for r, row in enumerate(self.rows) for c, t in enumerate(row) if t == symbol}
            if actual != {cell}:
                raise ValueError(f"Board must have exactly one {symbol}")
        bridges = dict(self.bridge_cells)
        expected = {(r, c) for r, row in enumerate(self.rows) for c, t in enumerate(row) if t == "B"}
        if len(bridges) != len(self.bridge_cells) or set(bridges) != expected:
            raise ValueError("Every bridge tile needs exactly one bridge group")
        groups = set(bridges.values())
        if any(not isinstance(group, str) or not group for group in groups):
            raise ValueError("Bridge group names must be nonempty strings")
        if not self.initially_open <= groups:
            raise ValueError("Unknown initially open bridge")
        expected_switches = {(r, c) for r, row in enumerate(self.rows) for c, t in enumerate(row) if t in "ohx"}
        if len({s.cell for s in self.switches}) != len(self.switches) or {s.cell for s in self.switches} != expected_switches:
            raise ValueError("Every switch tile needs exactly one definition")
        for switch in self.switches:
            if switch.kind not in ("soft", "heavy", "split"):
                raise ValueError("Unknown switch kind")
            if self.tile(switch.cell) != {"soft": "o", "heavy": "h", "split": "x"}[switch.kind]:
                raise ValueError("Switch kind does not match tile")
            if switch.effect not in ("toggle", "open", "close") or not set(switch.bridges) <= groups:
                raise ValueError("Invalid bridge effect or reference")
            if len(set(switch.bridges)) != len(switch.bridges):
                raise ValueError("Duplicate bridge target")
            if any(group not in groups or effect not in ("toggle", "open", "close") for group, effect in switch.effects):
                raise ValueError("Invalid per-bridge switch effect")
            if switch.active_destination not in (0, 1):
                raise ValueError("Invalid active teleport destination")
            if switch.kind == "split":
                if len(switch.destinations) != 2 or len(set(switch.destinations)) != 2:
                    raise ValueError("Split switch needs two distinct destinations")
                if any(self.tile(cell) in " B" for cell in switch.destinations):
                    raise ValueError("Split destinations must be fixed supporting tiles")
            elif switch.destinations:
                raise ValueError("Only split switches have destinations")

    @classmethod
    def load(cls, path: str | Path) -> "Board":
        """Giữ cách gọi Board.load(path); phần đọc file nằm trong levels.py."""
        from .levels import load_board
        return load_board(path)

    @classmethod
    def from_dict(cls, data: dict) -> "Board":
        """Pack level và file màn riêng dùng cùng một bộ đọc."""
        from .levels import parse_board
        return parse_board(data)
