import json
import tempfile
import unittest
from pathlib import Path

from bloxorz import Action, Board, Engine, State, Switch
from bloxorz.levels import load_levels
from bloxorz.solver import solve
from server import ROOT


class LevelTests(unittest.TestCase):
    def setUp(self):
        suite = json.loads((ROOT / "levels/testcases.json").read_text(encoding="utf-8"))
        self.cases = [case for group in suite["groups"] for case in group["cases"]]

    def test_all_testcase_grids_keep_their_coordinates(self):
        self.assertEqual(len(self.cases), 43)
        for case in self.cases:
            with self.subTest(case=case["id"]):
                source = case["board"]
                board = Board.from_dict(source)
                self.assertEqual(board.rows, tuple(source["rows"]))
                for r, row in enumerate(source["rows"]):
                    for c, tile in enumerate(row):
                        self.assertEqual(board.tile((r, c)), tile)
                self.assertEqual(board.initially_open, set(source.get("initially_open", [])))
                for definition in source.get("switches", []):
                    switch = next(s for s in board.switches if s.cell == tuple(definition["cell"]))
                    self.assertEqual(dict(switch.effects), definition.get("effects", {}))
                    self.assertEqual(switch.destinations, tuple(map(tuple, definition.get("destinations", []))))
                    self.assertEqual(switch.active_destination, definition.get("active", 0))

    def test_pack_loader_accepts_testcase_boards(self):
        data = [{"name": case["name"], **case["board"]} for case in self.cases]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pack.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            levels = load_levels(path)
        self.assertEqual(len(levels), len(self.cases))
        for level, case in zip(levels, self.cases):
            self.assertEqual(level.name, case["name"])
            self.assertEqual(level.board, Board.from_dict(case["board"]))

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

    def test_initial_testcases_have_replayable_solutions(self):
        for case in self.cases[:9]:
            with self.subTest(case=case["id"]):
                engine = Engine(Board.from_dict(case["board"]))
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
