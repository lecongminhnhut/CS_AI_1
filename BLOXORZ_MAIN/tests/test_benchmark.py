"""Kiểm thử độc lập benchmark; không gọi solver hay thuật toán tìm kiếm."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from benchmark import benchmark as benchmark_module
from benchmark.benchmark import (RAW_FIELDS, SUMMARY_FIELDS, load_cases, main, summarize,
                                 write_csv, write_plots)


class BenchmarkUtilityTests(unittest.TestCase):
    def test_loads_all_fixed_cases_and_preserves_group_identity(self):
        root = Path(__file__).resolve().parents[1]
        cases = load_cases(root / "levels" / "testcases.json")
        self.assertEqual(len(cases), 43)
        self.assertEqual(cases[0][0:2], ("basic", "01 · Cơ bản"))
        self.assertEqual(cases[0][2]["id"], "B01")
        self.assertEqual(cases[-1][0], "unsolvable")

    def test_summary_and_csv_export_with_isolated_sample_rows(self):
        rows = [
            {"group_id": "basic", "group_name": "Cơ bản", "algorithm": "bfs", "status": "solved",
             "valid_solution": True, "search_time_ms": 12, "peak_memory_kb": 3,
             "expanded_nodes": 8, "solution_length": 4, "total_cost": 4},
            {"group_id": "basic", "group_name": "Cơ bản", "algorithm": "bfs", "status": "timeout",
             "valid_solution": None, "search_time_ms": 50, "peak_memory_kb": None,
             "expanded_nodes": None, "solution_length": None, "total_cost": None},
            {"group_id": "basic", "group_name": "Cơ bản", "algorithm": "bfs", "status": "no_solution",
             "valid_solution": None, "search_time_ms": 20, "peak_memory_kb": 5,
             "expanded_nodes": 10, "solution_length": None, "total_cost": None},
            {"group_id": "basic", "group_name": "Cơ bản", "algorithm": "bfs", "status": "invalid_solution",
             "valid_solution": False, "search_time_ms": 99, "peak_memory_kb": 99,
             "expanded_nodes": 99, "solution_length": 99, "total_cost": 99},
        ]
        summary = summarize(rows)
        self.assertEqual(summary[0]["solved"], 1)
        self.assertEqual(summary[0]["timeout"], 1)
        self.assertEqual(summary[0]["no_solution"], 1)
        self.assertEqual(summary[0]["median_search_time_ms"], 16)
        self.assertEqual(summary[0]["mean_search_time_ms"], 16)
        self.assertEqual(summary[0]["median_peak_memory_kb"], 4)
        self.assertEqual(summary[0]["median_expanded_nodes"], 9)
        self.assertEqual(summary[0]["median_solution_length"], 4)
        self.assertEqual(summary[0]["median_total_cost"], 4)
        with tempfile.TemporaryDirectory() as directory:
            raw_path = Path(directory) / "raw.csv"
            summary_path = Path(directory) / "summary.csv"
            write_csv(raw_path, rows, RAW_FIELDS)
            write_csv(summary_path, summary, SUMMARY_FIELDS)
            with raw_path.open(encoding="utf-8-sig", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 4)
            with summary_path.open(encoding="utf-8-sig", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 1)
            json_path = Path(directory) / "results.json"
            json_path.write_text(json.dumps({"raw_results": rows, "summary": summary}), encoding="utf-8")
            self.assertEqual(len(json.loads(json_path.read_text(encoding="utf-8"))["raw_results"]), 4)

    def test_plot_export_with_isolated_sample_rows(self):
        rows = [{"group_id": "basic", "algorithm": "bfs", "status": "solved",
                 "valid_solution": True, "search_time_ms": 12, "peak_memory_kb": 3,
                 "expanded_nodes": 8, "solution_length": 4}]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_plots(rows, output)
            for name in ("search_time.png", "peak_memory.png", "expanded_nodes.png", "solution_length.png"):
                self.assertTrue((output / name).is_file(), name)

    def test_plot_uses_no_solution_for_performance_but_not_solution_length(self):
        rows = [
            {"group_id": "basic", "algorithm": "bfs", "status": "no_solution",
             "valid_solution": None, "search_time_ms": 20, "peak_memory_kb": 5,
             "expanded_nodes": 10, "solution_length": None},
            {"group_id": "basic", "algorithm": "bfs", "status": "invalid_solution",
             "valid_solution": False, "search_time_ms": 99, "peak_memory_kb": 99,
             "expanded_nodes": 99, "solution_length": 99},
        ]
        with tempfile.TemporaryDirectory() as directory:
            write_plots(rows, Path(directory))
            self.assertTrue((Path(directory) / "search_time.png").is_file())
            self.assertFalse((Path(directory) / "solution_length.png").exists())

    def test_cases_are_validated_before_running_and_duplicates_are_collapsed(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "results"
            result = {"group_id": "basic", "group_name": "Cơ bản", "algorithm": "bfs",
                      "status": "no_solution", "valid_solution": None,
                      "search_time_ms": 1, "peak_memory_kb": 1, "expanded_nodes": 1,
                      "solution_length": None, "total_cost": None}
            with patch.object(benchmark_module, "run_one", return_value=result) as run:
                self.assertEqual(main(["--cases", " B01, B01 ", "--output", str(output), "--no-plots"]), 0)
            self.assertEqual(run.call_count, 4)
            self.assertTrue((output / "benchmark_results.json").is_file())

            invalid_output = Path(directory) / "invalid"
            self.assertEqual(main(["--cases", "B01, MISSING", "--output", str(invalid_output), "--no-plots"]), 2)
            self.assertFalse(invalid_output.exists())

    def test_external_timeout_is_reported_and_worker_is_stopped(self):
        root = Path(__file__).resolve().parents[1]
        case = load_cases(root / "levels" / "testcases.json")[0][2]
        row = benchmark_module.run_one("basic", "Cơ bản", case, "bfs", 1, 0.001)
        self.assertEqual(row["status"], "timeout")
        self.assertIn("Timeout ngoài", row["error"])


if __name__ == "__main__":
    unittest.main()
