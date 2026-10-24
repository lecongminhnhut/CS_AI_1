import json
import hashlib
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

from bloxorz import Action, Board, Engine, State, Switch
from bloxorz.levels import load_levels
from bloxorz.solver import solve
from server import ROOT


class CoolmathTests(unittest.TestCase):
    def test_all_grids_keep_their_coordinates(self):
        pack = load_levels(ROOT / "levels/levels.json")
        source = json.loads((ROOT / "levels/levels.json").read_text())
        self.assertEqual(len(pack), 33)
        for level, stage in zip(pack, source):
            board = level.board
            self.assertEqual(level.name, stage["name"])
            self.assertEqual(level.passcode, stage["passcode"])
            self.assertEqual(board, Board.from_dict({k: v for k, v in stage.items() if k not in ("name", "passcode")}))
            self.assertEqual(len(board.rows), len(stage["rows"]))
            for r, row in enumerate(stage["rows"]):
                for c, tile in enumerate(row):
                    self.assertEqual(board.tile((r, c)), tile)
            self.assertEqual(board.initially_open, set(stage.get("initially_open", [])))
            for definition in stage.get("switches", []):
                switch = next(s for s in board.switches if s.cell == tuple(definition["cell"]))
                self.assertEqual(dict(switch.effects), definition.get("effects", {}))
                self.assertEqual(switch.destinations, tuple(map(tuple, definition.get("destinations", []))))
                self.assertEqual(switch.active_destination, definition.get("active", 0))

    def test_migration_preserves_original_33_boards(self):
        # Fingerprint captured from engine boards before converting the supplied pack.
        def plain(value):
            if isinstance(value, dict):
                return {key: plain(item) for key, item in value.items()}
            if isinstance(value, (tuple, list)):
                return [plain(item) for item in value]
            if isinstance(value, frozenset):
                return sorted(value)
            return value
        boards = [plain(asdict(level.board)) for level in load_levels(ROOT / "levels/levels.json")]
        serialized = json.dumps(boards, sort_keys=True, separators=(",", ":"))
        self.assertEqual(hashlib.sha256(serialized.encode()).hexdigest(),
                         "c83e344d235a53bfce8deb08f33efdf09a3cebcaeef9661e160d85c1509f2cdf")

    def test_pack_validation_and_optional_metadata(self):
        invalid = [[], {}, [None], [{"rows": ["S..G"]}],
                   [{"name": "Test", "rows": ["S..G"], "passcode": 123}],
                   [{"name": "Test", "grid": ["S..H"]}],
                   [{"name": "Test", "rows": ["S..G"], "typo": []}]]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pack.json"
            for data in invalid:
                with self.subTest(data=data):
                    path.write_text(json.dumps(data), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_levels(path)
            path.write_text(json.dumps([{"name": "Test", "rows": ["S..G"]}]), encoding="utf-8")
            level = load_levels(path)[0]
            self.assertEqual(level.passcode, "")
            self.assertEqual(level.board, Board(("S..G",), (0, 0), (0, 3)))

    def test_initial_stages_have_replayable_solutions(self):
        for level in load_levels(ROOT / "levels/levels.json")[:9]:
            with self.subTest(stage=level.name):
                engine = Engine(level.board)
                result = solve(engine, engine.initial_state(), "bfs")
                self.assertEqual(result["status"], "solved")
                state = engine.initial_state()
                for action in result["actions"]:
                    state = engine.step(state, action)
                    self.assertIsNotNone(state)
                self.assertTrue(engine.is_goal(state))

    def test_mixed_bridge_effects_and_vertical_soft_pressure(self):
        board = Board(("S.oBBG", "......", "......"), (0, 0), (0, 5),
                      (((0, 3), "a"), ((0, 4), "b")),
                      (Switch((0, 2), "soft", effects=(("a", "open"), ("b", "close"))),), frozenset({"b"}))
        engine = Engine(board)
        state, event = engine.transition(State(((1, 1), (2, 1)), frozenset({"b"})), "right")
        self.assertFalse(event["switches"])
        state, event = engine.transition(State(((1, 2), (2, 2)), frozenset({"b"})), "up")
        self.assertEqual(state.bridges, frozenset({"a"}))
        self.assertEqual(event["switches"], [{"cell": (0, 2), "kind": "soft"}])
        state, event = engine.transition(State(((0, 1), (1, 1)), frozenset({"b"})), "right")
        self.assertEqual(state.orientation, "vertical")
        self.assertEqual(state.bridges, frozenset({"a"}))

    def test_failure_metadata_and_legacy_step_agree(self):
        engine = Engine(Board(("S. G",), (0, 0), (0, 3)))
        state, info = engine.transition(engine.initial_state(), Action.RIGHT)
        self.assertIsNone(state)
        self.assertEqual(info["landing"]["cells"], ((0, 1), (0, 2)))
        self.assertEqual(info["support"], ((0, 1),))
        self.assertEqual(info["failure"], "edge")
        for action in Action:
            self.assertEqual(engine.step(engine.initial_state(), action), engine.transition(engine.initial_state(), action)[0])
