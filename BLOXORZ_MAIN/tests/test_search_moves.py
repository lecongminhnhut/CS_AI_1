import json
import unittest
from heapq import heappop, heappush
from itertools import count
from importlib import import_module
from time import perf_counter
from pathlib import Path
from queue import Queue
from threading import Event
from unittest.mock import patch

from bloxorz import Action, Board, Engine, State
from bloxorz.solver import solve
from bloxorz.solvers.common import edge_cost, finish, search_successors
from benchmark.benchmark import _worker
from server import Session


ROOT = Path(__file__).resolve().parents[1]


def reference_cost(engine, weighted):
    start = engine.initial_state()
    sequence = count()
    heap = [(0, next(sequence), start)]
    costs = {start: 0}
    while heap:
        cost, _, state = heappop(heap)
        if cost != costs[state]:
            continue
        if engine.is_goal(state):
            return cost
        for action, child in engine.successors(state):
            step_cost = 0 if action == Action.SWITCH else edge_cost(engine, child) if weighted else 1
            candidate = cost + step_cost
            if candidate < costs.get(child, float('inf')):
                costs[child] = candidate
                heappush(heap, (candidate, next(sequence), child))
    return None


class SearchMoveTests(unittest.TestCase):
    def setUp(self):
        self.engine = Engine(Board(('S.....G', '.......', '.......', '.......', '.......'), (0, 0), (0, 6)))
        self.split = State(((2, 1), (2, 5)), split=True)

    def test_grouped_successors_use_engine_and_replay_to_the_same_state(self):
        with patch.object(self.engine, 'successors', wraps=self.engine.successors) as successors:
            edges = list(search_successors(self.engine, self.split))
        self.assertEqual(successors.call_count, 2)
        self.assertEqual(len(edges), 8)
        for actions, target in edges:
            self.assertEqual(sum(action != Action.SWITCH for action in actions), 1)
            state = self.split
            for action in actions:
                state = self.engine.step(state, action)
            self.assertEqual(state, target)
        self.assertEqual(list(search_successors(self.engine, State((self.engine.board.goal,)))), [])

    def test_other_cube_can_merge_without_an_extra_search_step(self):
        start = State(((2, 1), (2, 3)), split=True)
        edges = dict(search_successors(self.engine, start))
        merged = edges[(Action.SWITCH, Action.LEFT)]
        self.assertFalse(merged.split)
        self.assertEqual(merged.cells, ((2, 1), (2, 2)))

    def test_finish_keeps_switches_in_order_but_only_counts_rolls(self):
        middle = State(((1, 1), (1, 5)), split=True)
        goal = State((self.engine.board.goal,))
        parents = {self.split: None, middle: (self.split, (Action.SWITCH, Action.UP)),
                   goal: (middle, (Action.SWITCH, Action.RIGHT))}
        result = finish(goal, parents, {goal: 2}, 2, 'solved')
        self.assertEqual(result['actions'], ['switch', 'up', 'switch', 'right'])
        self.assertEqual(result['length'], 2)
        self.assertEqual(result['cost'], 2)

    def test_bfs_minimizes_rolls_instead_of_control_actions(self):
        selected = self.engine.step(self.split, Action.SWITCH)
        first = State(((1, 1),))
        second = State(((1, 2),))
        goal = State((self.engine.board.goal,))
        graph = {self.split: [(Action.RIGHT, first), (Action.SWITCH, selected)],
                 selected: [(Action.SWITCH, self.split), (Action.UP, goal)],
                 first: [(Action.RIGHT, second)], second: [(Action.RIGHT, goal)]}
        with patch.object(self.engine, 'successors', side_effect=lambda state: iter(graph.get(state, []))):
            result = solve(self.engine, self.split, 'bfs')
        self.assertEqual(result['actions'], ['switch', 'up'])
        self.assertEqual(result['length'], 1)
        self.assertEqual(result['cost'], 1)

    def test_manual_cube_selection_does_not_increment_moves(self):
        session = Session()
        session.engine = self.engine
        session.state = self.split
        session.move('switch')
        self.assertEqual(session.moves, 0)
        self.assertEqual(session.state.active, 1)
        session.move('switch')
        self.assertEqual(session.moves, 0)
        session.move('right')
        self.assertEqual(session.moves, 1)

    def test_benchmark_replays_free_switches_without_charging_fragile_tiles(self):
        suite = json.loads((ROOT / 'levels/testcases.json').read_text(encoding='utf-8'))
        case = next(case for group in suite['groups'] for case in group['cases'] if case['id'] == 'M01')
        engine = Engine(Board.from_dict(case['board']))
        result = solve(engine, engine.initial_state(), 'astar', seconds=30)
        state = engine.initial_state()
        actions = []
        inserted = False
        for action in result['actions']:
            if state.split and not inserted:
                actions.extend(['switch', 'switch'])
                inserted = True
            actions.append(action)
            state = engine.step(state, action)
        self.assertTrue(inserted)
        result['actions'] = actions
        output = Queue()
        with patch('bloxorz.solver.solve', return_value=result):
            _worker({'board': case['board'], 'algorithm': 'astar', 'timeout': 30}, output, Event())
        row = output.get_nowait()
        self.assertEqual(row['status'], 'solved')
        self.assertTrue(row['valid_solution'])
        self.assertLess(row['solution_length'], len(actions))

    def test_all_fixed_cases_match_independent_free_switch_search(self):
        suite = json.loads((ROOT / 'levels/testcases.json').read_text(encoding='utf-8'))
        for group in suite['groups']:
            for case in group['cases']:
                engine = Engine(Board.from_dict(case['board']))
                minimum_rolls = reference_cost(engine, False)
                minimum_cost = reference_cost(engine, True)
                for algorithm in ('bfs', 'dfs', 'ucs', 'astar'):
                    with self.subTest(case=case['id'], algorithm=algorithm):
                        result = import_module(f'bloxorz.solvers.{algorithm}').search(
                            engine, engine.initial_state(), perf_counter() + 30)
                        if minimum_rolls is None:
                            self.assertEqual(result['status'], 'no_solution')
                            self.assertIsNone(result['length'])
                            self.assertIsNone(result['cost'])
                            continue
                        self.assertEqual(result['status'], 'solved')
                        state, total_cost = engine.initial_state(), 0
                        for action in result['actions']:
                            state = engine.step(state, action)
                            self.assertIsNotNone(state)
                            if action != 'switch':
                                total_cost += edge_cost(engine, state)
                        self.assertTrue(engine.is_goal(state))
                        self.assertEqual(result['length'], sum(action != 'switch' for action in result['actions']))
                        self.assertEqual(result['cost'], total_cost)
                        if algorithm == 'bfs':
                            self.assertEqual(result['length'], minimum_rolls)
                        if algorithm in ('ucs', 'astar'):
                            self.assertEqual(result['cost'], minimum_cost)


if __name__ == '__main__':
    unittest.main()
