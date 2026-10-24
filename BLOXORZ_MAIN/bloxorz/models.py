"""Các kiểu dữ liệu bất biến dùng chung cho game và bốn solver.

Tọa độ luôn là (hàng, cột). State có thể dùng làm khóa trong set/dict.
"""

from dataclasses import dataclass
from enum import Enum

Cell = tuple[int, int]


class Action(str, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    SWITCH = "switch"


@dataclass(frozen=True)
class State:
    """Vị trí khối và cầu hiện tại; active là chỉ số khối con đang chọn."""

    cells: tuple[Cell, ...]
    bridges: frozenset[str] = frozenset()
    split: bool = False
    active: int = 0

    @property
    def orientation(self) -> str:
        if self.split:
            return "split"
        if len(self.cells) == 1:
            return "standing"
        return "horizontal" if self.cells[0][0] == self.cells[1][0] else "vertical"


@dataclass(frozen=True)
class Switch:
    """Công tắc: tác động cầu hoặc đưa hai khối con đến các điểm tách."""

    cell: Cell
    kind: str
    bridges: tuple[str, ...] = ()
    effect: str = "toggle"
    destinations: tuple[Cell, ...] = ()
    effects: tuple[tuple[str, str], ...] = ()
    active_destination: int = 0


