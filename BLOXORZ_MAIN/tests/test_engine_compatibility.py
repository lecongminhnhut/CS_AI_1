import hashlib
import json
import tempfile
import unittest
from collections import deque
from dataclasses import asdict
from pathlib import Path

from bloxorz import Action, Board, Engine, State, Switch

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
    def test_transitions_and_animation_events_match_reference(self):
        reference = json.loads((ROOT / "tests/engine_transition_reference.json").read_text())
        suite = json.loads((ROOT / "levels/testcases.json").read_text(encoding="utf-8"))
        boards = {case["id"]: Board.from_dict(case["board"])
                  for group in suite["groups"] for case in group["cases"]}
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
        suite = json.loads((ROOT / "levels/testcases.json").read_text(encoding="utf-8"))
        data = suite["groups"][2]["cases"][0]["board"]
        expected = Board.from_dict(data)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "level.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(Board.load(path), expected)
            self.assertEqual(load_board(path), expected)
        self.assertEqual(parse_board(data), expected)
