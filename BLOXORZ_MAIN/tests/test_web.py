import http.cookiejar
import json
import threading
import time
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

from bloxorz import Action, Board, Engine, State
from bloxorz.solver import solve
from server import ROOT, Session, create_server


class SearchTests(unittest.TestCase):
    def test_missing_algorithm_has_a_clear_handoff_error(self):
        engine = Engine(Board(("S..G",), (0, 0), (0, 3)))
        for algorithm in ("bfs", "dfs", "ucs", "astar"):
            with self.subTest(algorithm=algorithm), patch("bloxorz.solver.import_module") as importer:
                module = f"bloxorz.solvers.{algorithm}"
                importer.side_effect = ModuleNotFoundError(name=module)
                with self.assertRaisesRegex(ValueError, f"bloxorz/solvers/{algorithm}.py"):
                    solve(engine, engine.initial_state(), algorithm)

    def test_missing_dependency_inside_algorithm_is_not_hidden(self):
        engine = Engine(Board(("S..G",), (0, 0), (0, 3)))
        with patch("bloxorz.solver.import_module", side_effect=ModuleNotFoundError(name="missing_dependency")):
            with self.assertRaises(ModuleNotFoundError):
                solve(engine, engine.initial_state(), "bfs")

    def test_time_limit_includes_waiting_for_another_solver(self):
        from bloxorz.solver import _measurement_lock
        engine = Engine(Board.load(ROOT / "levels/basic.json"))
        with _measurement_lock:
            started = time.perf_counter()
            result = solve(engine, engine.initial_state(), "dfs", seconds=.02)
            self.assertLess(time.perf_counter() - started, 1)
        self.assertEqual(result["status"], "timeout")
        self.assertEqual(result["actions"], [])
        self.assertEqual(solve(engine, engine.initial_state(), "dfs")["status"], "solved")

    def test_default_search_has_no_time_limit(self):
        engine = Engine(Board(("S..G",), (0, 0), (0, 3)))
        for algorithm in ("bfs", "dfs", "ucs", "astar"):
            for elapsed in (10.01, 1_000_000):
                with self.subTest(algorithm=algorithm, elapsed=elapsed):
                    with patch("bloxorz.solver.time.perf_counter", return_value=100):
                        with patch(f"bloxorz.solvers.{algorithm}.perf_counter", return_value=100 + elapsed):
                            result = solve(engine, engine.initial_state(), algorithm)
                    self.assertEqual(result["status"], "solved")

    def test_default_measurement_lock_has_no_wait_timeout(self):
        engine = Engine(Board(("S..G",), (0, 0), (0, 3)))
        with patch("bloxorz.solver._measurement_lock") as lock:
            self.assertEqual(solve(engine, engine.initial_state(), "bfs")["status"], "solved")
            lock.acquire.assert_called_once_with()
            lock.release.assert_called_once_with()

    def test_every_solver_produces_replayable_solutions(self):
        for level in ("basic", "courtyard", "advanced"):
            engine = Engine(Board.load(ROOT / "levels" / f"{level}.json"))
            minimum = solve(engine, engine.initial_state(), "bfs")["length"]
            for algorithm in ("bfs", "dfs", "ucs", "astar"):
                with self.subTest(level=level, algorithm=algorithm):
                    state = engine.initial_state()
                    result = solve(engine, state, algorithm)
                    self.assertEqual(result["status"], "solved")
                    cost = 0
                    for action in result["actions"]:
                        state = engine.step(state, action)
                        self.assertIsNotNone(state)
                        cost += 1 + sum(engine.board.tile(cell) == "F" for cell in state.cells)
                    self.assertTrue(engine.is_goal(state))
                    self.assertEqual(result["length"], len(result["actions"]))
                    self.assertEqual(result["cost"], cost)
                    if algorithm == "dfs":
                        self.assertEqual(result["length"], minimum)

    def test_dfs_revisits_states_reached_by_a_shorter_path(self):
        engine = Engine(Board(("S....G",), (0, 0), (0, 5)))
        start, a, b, c, shared, goal = [State(((0, i),)) for i in range(6)]
        graph = {start: [a, b], a: [c], c: [shared], b: [shared], shared: [start, goal]}
        with patch.object(engine, "successors", side_effect=lambda state:
                          iter((Action.RIGHT, child) for child in graph.get(state, []))):
            result = solve(engine, start, "dfs")
            self.assertEqual(result["status"], "solved")
            self.assertEqual(result["length"], 3)
            self.assertEqual(result["cost"], 3)

    def test_dfs_timeout_cycles_and_already_solved(self):
        engine = Engine(Board(("S.. G",), (0, 0), (0, 4)))
        self.assertEqual(solve(engine, engine.initial_state(), "dfs")["status"], "no_solution")
        result = solve(engine, engine.initial_state(), "dfs", seconds=0)
        self.assertEqual(result["status"], "timeout")
        self.assertIsNone(result["length"])
        result = solve(engine, State((engine.board.goal,)), "dfs")
        self.assertEqual(result["status"], "solved")
        self.assertEqual(result["actions"], [])
        self.assertEqual(result["cost"], 0)

    def test_weighted_search_agrees_and_timeout_is_explicit(self):
        engine = Engine(Board(("S..F..G", ".......", "......."), (0, 0), (0, 6)))
        ucs = solve(engine, engine.initial_state(), "ucs")
        astar = solve(engine, engine.initial_state(), "astar")
        self.assertEqual(ucs["status"], "solved")
        self.assertEqual(ucs["cost"], astar["cost"])
        self.assertEqual(solve(engine, engine.initial_state(), "bfs", seconds=0)["status"], "timeout")

    def test_no_solution(self):
        engine = Engine(Board(("S G",), (0, 0), (0, 2)))
        for algorithm in ("bfs", "dfs", "ucs", "astar"):
            result = solve(engine, engine.initial_state(), algorithm)
            self.assertEqual(result["status"], "no_solution")
            self.assertIsNone(result["length"])


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def request(self, route, data=None, origin=None):
        request = urllib.request.Request(self.url + route,
                    data=json.dumps(data).encode() if data is not None else None)
        if origin:
            request.add_header("Origin", origin)
        with self.client.open(request, timeout=15) as response:
            return json.load(response)

    def test_solver_routes_have_no_time_limit(self):
        self.request("/api/reset", {"level": "stage-01"})
        for route, data in (("/api/solve", {"algorithm": "dfs"}),
                            ("/api/testcase", {"level": "B01", "algorithm": "dfs"})):
            with self.subTest(route=route), patch("server.solve", wraps=solve) as search:
                self.assertEqual(self.request(route, data)["result"]["status"], "solved")
                self.assertEqual(len(search.call_args.args), 3)
                self.assertEqual(search.call_args.kwargs, {})

    def test_session_lock_has_no_wait_timeout(self):
        session = Session()
        with patch("server.Session", return_value=session):
            with patch.object(session, "lock") as lock:
                self.assertEqual(self.request("/api/solve", {"algorithm": "bfs"})["result"]["status"], "solved")
                lock.__enter__.assert_called_once_with()
                lock.__exit__.assert_called_once()

    def test_manual_play_and_solver_share_one_session(self):
        game = self.request("/api/reset", {"level": "basic"})
        self.assertEqual(game["moves"], 0)
        result = self.request("/api/solve", {"algorithm": "astar"})["result"]
        self.assertEqual(result["actions"], ["right", "right"])
        for action in result["actions"]:
            game = self.request("/api/move", {"action": action})
        self.assertEqual(game["status"], "won")
        self.request("/api/reset", {"level": "basic"})
        self.assertEqual(self.request("/api/move", {"action": "left"})["status"], "lost")

    def test_invalid_input_cross_origin_and_static_assets(self):
        for route, data, origin in (("/api/reset", {"level": "../secret"}, None),
                                     ("/api/move", {"action": "invalid"}, None),
                                     ("/api/solve", {"algorithm": "unknown"}, None),
                                     ("/api/testcase", {"level": "B01", "algorithm": "bfs"}, "http://example.com"),
                                     ("/api/reset", {}, "http://example.com")):
            with self.subTest(route=route, data=data, origin=origin):
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    self.request(route, data, origin)
                self.assertIn(caught.exception.code, (400, 403))
                caught.exception.close()
        for path in ("/", "/game.js", "/testcases.js", "/art.js", "/motion.js", "/progression.js", "/style.css", "/vendor/three.module.js"):
            with self.client.open(self.url + path) as response:
                self.assertEqual(response.status, 200)
                if path.endswith(".mjs"):
                    self.assertEqual(response.headers.get_content_type(), "application/javascript")
                self.assertTrue(response.read())

    def test_independent_tabs_and_switch_without_split(self):
        self.request("/api/reset", {"level": "basic"})
        self.request("/api/move", {"action": "right"})
        with urllib.request.urlopen(self.url + "/api/game") as response:
            other = json.load(response)
        self.assertEqual(other["level"], "stage-01")
        self.assertEqual(other["moves"], 0)
        session = Session()
        session.move("switch")
        self.assertEqual(session.status, "playing")
        self.assertEqual(session.moves, 0)

    def test_coolmath_pack_and_move_metadata_are_available(self):
        game = self.request("/api/reset", {"level": "stage-02"})
        self.assertEqual(sum(level["id"].startswith("stage-") for level in game["levels"]), 33)
        self.assertEqual(game["state"]["bridges"], [])
        game = self.request("/api/move", {"action": "right"})
        self.assertIsNotNone(game["transition"]["landing"])
        self.assertIn("support", game["transition"])

    def test_current_level_catalog_loads_every_advertised_board(self):
        pack = json.loads((ROOT / "levels/levels.json").read_text(encoding="utf-8"))
        groups = json.loads((ROOT / "levels/testcases.json").read_text(encoding="utf-8"))["groups"]
        expected = {f"stage-{i:02}": level for i, level in enumerate(pack, 1)}
        expected.update({case["id"]: case["board"] for group in groups for case in group["cases"]})
        game = self.request("/api/game")
        self.assertEqual({level["id"] for level in game["levels"]}, set(expected))
        for level, board in expected.items():
            with self.subTest(level=level):
                game = self.request("/api/reset", {"level": level})
                self.assertEqual(game["level"], level)
                self.assertEqual(game["rows"], board["rows"])
                self.assertEqual(game["moves"], 0)
                self.assertEqual(game["status"], "playing")
        for removed in ("basic", "courtyard", "advanced"):
            with self.subTest(removed=removed), self.assertRaises(urllib.error.HTTPError) as caught:
                self.request("/api/reset", {"level": removed})
            self.assertEqual(caught.exception.code, 400)
            caught.exception.close()

    def test_testcase_runs_from_start_without_changing_session(self):
        suite = self.request("/api/testcases")
        self.assertEqual([len(group["cases"]) for group in suite["groups"]], [10] * 4 + [3])
        self.request("/api/reset", {"level": "basic"})
        before = self.request("/api/move", {"action": "right"})
        case = suite["groups"][0]["cases"][0]
        for algorithm in ("bfs", "dfs", "ucs", "astar"):
            result = self.request("/api/testcase", {"level": case["id"], "algorithm": algorithm})["result"]
            self.assertEqual(result["status"], "solved")
            engine = Engine(Board.from_dict(case["board"]))
            state = engine.initial_state()
            for action in result["actions"]:
                state = engine.step(state, action)
                self.assertIsNotNone(state)
            self.assertTrue(engine.is_goal(state))
        self.assertEqual(self.request("/api/game"), before)
        self.assertEqual(self.request("/api/reset", {"level": case["id"]})["level"], case["id"])
        for payload in ({"level": "../secret", "algorithm": "bfs"},
                        {"level": case["id"], "algorithm": "unknown"},
                        {"level": [], "algorithm": "bfs"}):
            with self.assertRaises(urllib.error.HTTPError) as caught:
                self.request("/api/testcase", payload)
            self.assertEqual(caught.exception.code, 400)
            caught.exception.close()

    def test_unsolvable_testcases_run_without_changing_session(self):
        before = self.request("/api/game")
        group = self.request("/api/testcases")["groups"][-1]
        self.assertEqual(group["id"], "unsolvable")
        self.assertEqual(len(group["cases"]), 3)
        for case in group["cases"]:
            for algorithm in ("bfs", "dfs", "ucs", "astar"):
                with self.subTest(case=case["id"], algorithm=algorithm):
                    result = self.request("/api/testcase", {"level": case["id"], "algorithm": algorithm})["result"]
                    self.assertEqual(result["status"], "no_solution")
                    self.assertIsNone(result["length"])
                    self.assertIsNone(result["cost"])
        self.assertEqual(self.request("/api/game"), before)
