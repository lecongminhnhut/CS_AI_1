"""So sánh với hành vi engine trước khi tách file, gồm cả sự kiện animation."""

import hashlib
import json
import unittest
from collections import deque
from dataclasses import asdict
from pathlib import Path

from bloxorz import Action, Board, Engine, State, Switch
from bloxorz.levels import load_levels

ROOT = Path(__file__).resolve().parents[1]


def transition_digest(board):
    engine = Engine(board)
    start = engine.initial_state()
    pending = deque([start])
    visited = {start}
    records = []
    examined = 0
    while pending and examined < 300:
        state = pending.popleft()
        examined += 1
        for action in Action:
            after, info = engine.transition(state, action)
            records.append([asdict(state), action.value, asdict(after) if after is not None else None, info])
            if after is not None and after not in visited:
                visited.add(after)
                pending.append(after)
    serialized = json.dumps(records, default=sorted, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode()).hexdigest()


class CompatibilityTests(unittest.TestCase):
    def test_transitions_and_animation_events_match_previous_engine(self):
        reference = json.loads((ROOT / "tests/engine_transition_reference.json").read_text())
        boards = {f"stage-{i:02}": level.board
                  for i, level in enumerate(load_levels(ROOT / "levels/levels.json"), 1)}
        boards.update({name: Board.load(ROOT / f"levels/{name}.json")
                       for name in ("basic", "courtyard", "advanced")})
        self.assertEqual(set(boards), set(reference))
        for name, board in boards.items():
            with self.subTest(level=name):
                self.assertEqual(transition_digest(board), reference[name])

    def test_existing_imports_and_board_loaders_remain_compatible(self):
        from bloxorz import engine
        from bloxorz.board import Board as BoardData
        from bloxorz.levels import load_board, parse_board
        from bloxorz.models import State as StateData
        self.assertIs(engine.Action, Action)
        self.assertIs(engine.Board, BoardData)
        self.assertIs(engine.State, StateData)
        self.assertIs(engine.Switch, Switch)
        path = ROOT / "levels/advanced.json"
        expected = Board.load(path)
        self.assertEqual(load_board(path), expected)
        data = json.loads(path.read_text())
        self.assertEqual(parse_board(data), expected)
        self.assertEqual(Board.from_dict(data), expected)
