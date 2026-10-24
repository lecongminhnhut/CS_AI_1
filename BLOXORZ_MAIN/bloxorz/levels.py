"""Đọc JSON cho cả file màn riêng và danh sách màn; dùng chung parse_board()."""

import json
from dataclasses import dataclass
from pathlib import Path

from .board import Board
from .models import Switch


@dataclass(frozen=True)
class Level:
    name: str
    passcode: str
    board: Board


def load_levels(path: str | Path) -> list[Level]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("Level pack must be a nonempty list")
    levels = []
    for index, entry in enumerate(data, 1):
        try:
            if not isinstance(entry, dict):
                raise ValueError("Level must be an object")
            name, passcode = entry.get("name"), entry.get("passcode", "")
            if not isinstance(name, str) or not name.strip() or not isinstance(passcode, str):
                raise ValueError("name must be nonempty and passcode must be a string")
            board = parse_board({k: v for k, v in entry.items() if k not in ("name", "passcode")})
            levels.append(Level(name, passcode, board))
        except (TypeError, ValueError) as error:
            raise ValueError(f"Invalid level {index}: {error}") from error
    return levels


def load_board(path: str | Path) -> Board:
    """Đọc một file màn riêng, ví dụ levels/basic.json."""
    return parse_board(json.loads(Path(path).read_text(encoding="utf-8")))


def parse_board(data: dict) -> Board:
    """Đọc và kiểm tra một cấu hình bàn chơi từ JSON đã giải mã."""
    if not isinstance(data, dict) or set(data) - {"rows", "bridges", "switches", "initially_open"}:
        raise ValueError("Invalid level object or unknown fields")
    rows = data.get("rows")
    if (not isinstance(rows, list) or not rows or not all(isinstance(row, str) for row in rows)
            or not rows[0] or any(len(row) != len(rows[0]) for row in rows)):
        raise ValueError("rows must be a nonempty rectangle of strings")
    bridges_data = data.get("bridges", {})
    switches_data = data.get("switches", [])
    initial_data = data.get("initially_open", [])
    if (not isinstance(bridges_data, dict)
            or any(not isinstance(k, str) or not k or not isinstance(v, list) or not v
                   for k, v in bridges_data.items())):
        raise ValueError("bridges must map names to nonempty lists of coordinates")
    if not isinstance(initial_data, list) or any(not isinstance(v, str) for v in initial_data):
        raise ValueError("initially_open must be a list of bridge names")
    if not isinstance(switches_data, list):
        raise ValueError("switches must be a list")
    for s in switches_data:
        if not isinstance(s, dict) or set(s) - {"cell", "effects", "destinations", "active"}:
            raise ValueError("Invalid switch object or unknown fields")
        effects = s.get("effects", {})
        if not isinstance(effects, dict) or any(not isinstance(v, str) for v in effects.values()):
            raise ValueError("effects must map bridge names to toggle/open/close")
        if not isinstance(s.get("destinations", []), list):
            raise ValueError("destinations must be a list of coordinates")
        if type(s.get("active", 0)) is not int or s.get("active", 0) not in (0, 1):
            raise ValueError("active must be 0 or 1")

    def cell(value):
        if (not isinstance(value, list) or len(value) != 2 or any(type(v) is not int for v in value)
                or not 0 <= value[0] < len(rows) or not 0 <= value[1] < len(rows[0])):
            raise ValueError("Coordinates must be [row, column] integers inside the board")
        return tuple(value)

    def find(symbol):
        found = [(r, c) for r, row in enumerate(rows) for c, t in enumerate(row) if t == symbol]
        if len(found) != 1:
            raise ValueError(f"Expected exactly one {symbol}")
        return found[0]

    try:
        bridge_cells = tuple((cell(c), group) for group, cells in bridges_data.items() for c in cells)
        switches = []
        for s in switches_data:
            position = cell(s["cell"])
            kind = {"o": "soft", "h": "heavy", "x": "split"}.get(rows[position[0]][position[1]])
            if kind is None:
                raise ValueError("Switch definition must point to o, h or x")
            if kind != "split" and ("destinations" in s or "active" in s):
                raise ValueError("Only split switches have destinations or active")
            if kind == "split" and "effects" in s:
                raise ValueError("Split switches use destinations, not bridge effects")
            switches.append(Switch(position, kind,
                                   destinations=tuple(cell(c) for c in s.get("destinations", [])),
                                   effects=tuple(s.get("effects", {}).items()),
                                   active_destination=s.get("active", 0)))
        return Board(tuple(rows), find("S"), find("G"), bridge_cells, tuple(switches),
                   frozenset(initial_data))
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("Malformed level metadata") from error

