import json
import tempfile
import unittest
from pathlib import Path

from bloxorz import Action, Board, Engine, State, Switch

ROOT = Path(__file__).resolve().parents[1]


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = Engine(Board(("S........",) + (".........",) * 7 + ("........G",), (0, 0), (8, 8)))

    def test_all_twelve_rolls(self):
        cases = [
            (((4, 4),), "up", ((2, 4), (3, 4))),
            (((4, 4),), "down", ((5, 4), (6, 4))),
            (((4, 4),), "left", ((4, 2), (4, 3))),
            (((4, 4),), "right", ((4, 5), (4, 6))),
            (((4, 4), (4, 5)), "up", ((3, 4), (3, 5))),
            (((4, 4), (4, 5)), "down", ((5, 4), (5, 5))),
            (((4, 4), (4, 5)), "left", ((4, 3),)),
            (((4, 4), (4, 5)), "right", ((4, 6),)),
            (((4, 4), (5, 4)), "up", ((3, 4),)),
            (((4, 4), (5, 4)), "down", ((6, 4),)),
            (((4, 4), (5, 4)), "left", ((4, 3), (5, 3))),
            (((4, 4), (5, 4)), "right", ((4, 5), (5, 5))),
        ]
        inverse = {"up": "down", "down": "up", "left": "right", "right": "left"}
        for cells, action, expected in cases:
            with self.subTest(cells=cells, action=action):
                original = State(cells)
                result = self.engine.step(original, action)
                self.assertEqual(result.cells, expected)
                self.assertEqual(self.engine.step(result, inverse[action]), original)

    def test_win_and_terminal_state(self):
        engine = Engine(Board.load(ROOT / "levels/basic.json"))
        first = engine.step(engine.initial_state(), "right")
        self.assertFalse(engine.is_goal(first))
        won = engine.step(first, "right")
        self.assertTrue(engine.is_goal(won))
        self.assertEqual(list(engine.successors(won)), [])
        self.assertFalse(engine.is_goal(State((engine.board.goal, (0, 4)), split=True)))

    def test_void_bounds_and_immutable_failure(self):
        engine = Engine(Board(("S. G",), (0, 0), (0, 3)))
        start = engine.initial_state()
        for action in ("up", "down", "left", "right", "switch"):
            self.assertIsNone(engine.step(start, action))
        self.assertEqual(start, engine.initial_state())

    def test_fragile(self):
        engine = Engine(Board(("S..F..G",), (0, 0), (0, 6)))
        after, info = engine.transition(State(((0, 1), (0, 2))), "right")
        self.assertIsNone(after)
        self.assertEqual(info["fallen"], [(0, 3)])
        self.assertEqual(info["failure"], "fragile")
        after, info = engine.transition(State(((0, 2),)), "right")
        self.assertIsNotNone(after)
        self.assertEqual(info["fallen"], [])

    def test_soft_toggle_reentry_and_pressure(self):
        engine = Engine(Board(("S.o.BG", "......"), (0, 0), (0, 5),
                              (((0, 4), "gate"),), (Switch((0, 2), "soft", ("gate",)),)))
        state = engine.step(engine.initial_state(), "right")
        self.assertEqual(state.bridges, frozenset({"gate"}))
        # Moving a second cube while the first holds a switch does not retrigger it.
        held = State(((0, 2), (1, 5)), state.bridges, True, 1)
        self.assertEqual(engine.step(held, "left").bridges, state.bridges)
        away = engine.step(state, "left")
        self.assertEqual(engine.step(away, "right").bridges, frozenset())

    def test_heavy_and_permanent_effects(self):
        for effect, initial, expected in (("open", frozenset(), frozenset({"g"})),
                                          ("close", frozenset({"g"}), frozenset())):
            engine = Engine(Board(("S..h.BG", "......."), (0, 0), (0, 6),
                                  (((0, 5), "g"),), (Switch((0, 3), "heavy", ("g",), effect),), initial))
            standing = engine.step(State(((0, 1), (0, 2)), initial), "right")
            self.assertEqual(standing.bridges, expected)
            lying = engine.step(State(((1, 2), (1, 3)), initial), "up")
            self.assertEqual(lying.bridges, initial)
            cube = engine.step(State(((0, 2), (1, 6)), initial, True), "right")
            self.assertEqual(cube.bridges, initial)

    def test_soft_switch_accepts_either_end_in_every_orientation(self):
        engine = Engine(Board(("S......", ".......", ".......", "...o...", ".......", ".......", ".....BG"),
                              (0, 0), (6, 6), (((6, 5), "gate"),),
                              (Switch((3, 3), "soft", ("gate",)),)))
        cases = [
            (State(((3, 1), (3, 2))), "right", "standing"),
            (State(((4, 3), (4, 4))), "up", "horizontal"),
            (State(((4, 2), (4, 3))), "up", "horizontal"),
            (State(((3, 2), (4, 2))), "right", "vertical"),
            (State(((2, 2), (3, 2))), "right", "vertical"),
            (State(((3, 2), (5, 5)), split=True), "right", "split"),
        ]
        for before, action, orientation in cases:
            with self.subTest(before=before, action=action):
                after, info = engine.transition(before, action)
                self.assertEqual(after.orientation, orientation)
                self.assertEqual(after.bridges, frozenset({"gate"}))
                self.assertEqual(info["switches"], [{"cell": (3, 3), "kind": "soft"}])
                self.assertEqual(info["fallen"], [])

    def test_closed_bridge_and_closing_under_block(self):
        engine = Engine(Board(("SoBG",), (0, 0), (0, 3), (((0, 2), "g"),),
                              (Switch((0, 1), "soft", ("g",)),)))
        self.assertIsNone(engine.step(engine.initial_state(), "right"))
        # Opening a bridge cannot rescue a move that was already unsupported.
        self.assertIsNone(engine.step(State(((0, 0),), frozenset({"g"})), "right"))

    def test_split_control_and_rejoin(self):
        engine = Engine(Board(("S..x..G", "......."), (0, 0), (0, 6), switches=(
            Switch((0, 3), "split", destinations=((1, 1), (1, 5))),)))
        split = engine.step(State(((0, 1), (0, 2))), "right")
        self.assertTrue(split.split)
        self.assertEqual(split.cells, ((1, 1), (1, 5)))
        switched = engine.step(split, Action.SWITCH)
        self.assertEqual(switched.active, 1)
        state = engine.step(switched, "left")
        state = engine.step(state, "left")
        state = engine.step(state, "left")
        self.assertEqual(state, State(((1, 1), (1, 2))))
        self.assertEqual(hash(split), hash(State(split.cells, split.bridges, True, 0)))
        self.assertNotEqual(split, switched)

    def test_teleport_landing_soft_switch(self):
        engine = Engine(Board(("S..x.BG", ".o....."), (0, 0), (0, 6), (((0, 5), "g"),), (
            Switch((0, 3), "split", destinations=((1, 1), (1, 5))),
            Switch((1, 1), "soft", ("g",)),)))
        self.assertEqual(engine.step(State(((0, 1), (0, 2))), "right").bridges, frozenset({"g"}))

    def test_level_validation_and_sample_loading(self):
        Board.load(ROOT / "levels/advanced.json")
        invalid = [
            {"rows": ["S.G", "."]}, {"rows": ["S?G"]}, {"rows": ["SSG"]},
            {"rows": ["SBG"]}, {"rows": ["SoG"]},
            {"rows": ["S.G"], "initially_open": ["unknown"]},
            {"rows": ["SoG"], "switches": [{"cell": [0, True]}]},
            {"rows": ["S.G"], "initially_open": "gate"},
            {"rows": ["SoG"], "switches": [{"cell": [0, 1], "typo": 1}]},
            {"rows": ["SoG"], "switches": [{"cell": [0, 1], "effects": "gate"}]},
            {"rows": ["SoG"], "switches": [{"cell": [0, 1], "effects": {"missing": "open"}}]},
            {"rows": ["SoBG"], "bridges": {"a": [[0, 2]]},
             "switches": [{"cell": [0, 1], "effects": {"a": "swap"}}]},
            {"rows": ["S.G"], "bridges": {"unused": []}},
            {"rows": ["SBG"], "bridges": {"a": [[-1, 1]]}},
            {"rows": ["S.G"], "switches": [{"cell": [0, 1]}]},
            {"rows": ["SoG"], "switches": [{"cell": [0, 1], "active": 0}]},
            {"rows": ["Sx..G"], "switches": [{"cell": [0, 1], "destinations": [[0, 0], [0, 3]], "active": True}]},
            {"rows": ["Sx..G"], "switches": [{"cell": [0, 1], "destinations": [[0, 0], [0, 3]], "active": 2}]},
            {"rows": ["Sx..G"], "switches": [{"cell": [0, 1], "destinations": [[0, 0], [0, 3]], "effects": {}}]},
            {"rows": ["SoG"], "switches": [{"cell": [0, 1], "destinations": []}]},
            {"rows": ["SoG"], "switches": [{"cell": [0, 1], "kind": "soft"}]},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "level.json"
            for data in invalid:
                with self.subTest(data=data):
                    path.write_text(json.dumps(data), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        Board.load(path)

    def test_shared_schema_preserves_mixed_effects_and_split_selection(self):
        board = Board.from_dict({
            "rows": ["S..oBBG", ".x....."],
            "bridges": {"a": [[0, 4]], "b": [[0, 5]]},
            "initially_open": ["b"],
            "switches": [{"cell": [0, 3], "effects": {"a": "open", "b": "close"}},
                         {"cell": [1, 1], "destinations": [[1, 0], [1, 5]], "active": 1}],
        })
        engine = Engine(board)
        after = engine.step(State(((0, 1), (0, 2)), board.initially_open), "right")
        self.assertEqual(after.bridges, frozenset({"a"}))
        split = engine.step(State(((1, 2), (1, 3))), "left")
        self.assertTrue(split.split)
        self.assertEqual(split.cells[split.active], (1, 5))


if __name__ == "__main__":
    unittest.main()
