import json
import unittest
from pathlib import Path

from bloxorz import Board, Engine
from bloxorz.solver import solve


class TestcaseTests(unittest.TestCase):
    def test_groups_are_distinct_solvable_and_increasing_in_length(self):
        suite = json.loads((Path(__file__).resolve().parents[1] / "levels/testcases.json").read_text(encoding="utf-8"))
        self.assertEqual(len(suite["groups"]), 5)
        ids, boards, previous_max = set(), set(), 0
        for index, group in enumerate(suite["groups"][:4]):
            self.assertEqual(len(group["cases"]), 10)
            lengths = []
            for case in group["cases"]:
                with self.subTest(case=case["id"]):
                    self.assertNotIn(case["id"], ids)
                    ids.add(case["id"])
                    board = Board.from_dict(case["board"])
                    self.assertNotIn(board, boards)
                    boards.add(board)
                    engine = Engine(board)
                    state = engine.initial_state()
                    result = solve(engine, state, "bfs")
                    self.assertEqual(result["status"], "solved")
                    kinds, bridges, fragile = set(), set(), False
                    cost = 0
                    for action in result["actions"]:
                        state, info = engine.transition(state, action)
                        self.assertIsNotNone(state)
                        kinds.update(s["kind"] for s in info["switches"])
                        bridges.update(cell for cell in state.cells if board.tile(cell) == "B")
                        count = sum(board.tile(cell) == "F" for cell in state.cells)
                        fragile |= count > 0
                        cost += 1 + count
                    self.assertTrue(engine.is_goal(state))
                    self.assertEqual(result["cost"], cost)
                    if index == 0:
                        self.assertFalse(board.switches or board.bridge_cells or "F" in "".join(board.rows))
                    if index in (1, 3):
                        self.assertTrue(fragile)
                    if index >= 2:
                        self.assertTrue({"soft", "heavy"} <= kinds)
                        self.assertEqual(len(bridges), len(board.bridge_cells))
                    if index == 3:
                        self.assertIn("split", kinds)
                    lengths.append(result["length"])
            self.assertEqual(lengths, sorted(lengths))
            self.assertGreater(min(lengths), previous_max)
            previous_max = max(lengths)

    def test_unsolvable_group_has_three_cases_rejected_by_every_solver(self):
        suite = json.loads((Path(__file__).resolve().parents[1] / "levels/testcases.json").read_text(encoding="utf-8"))
        ids = [case["id"] for group in suite["groups"] for case in group["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        group = suite["groups"][-1]
        self.assertEqual(group["id"], "unsolvable")
        self.assertEqual(len(group["cases"]), 3)
        for case in group["cases"]:
            engine = Engine(Board.from_dict(case["board"]))
            for algorithm in ("bfs", "dfs", "ucs", "astar"):
                with self.subTest(case=case["id"], algorithm=algorithm):
                    result = solve(engine, engine.initial_state(), algorithm)
                    self.assertEqual(result["status"], "no_solution")
                    self.assertEqual(result["actions"], [])
                    self.assertIsNone(result["length"])
                    self.assertIsNone(result["cost"])
