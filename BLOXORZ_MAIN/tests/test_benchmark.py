"""Kiểm thử độc lập benchmark; không gọi solver hay thuật toán tìm kiếm."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from benchmark.benchmark import (RAW_FIELDS, SUMMARY_FIELDS, load_cases, summarize, write_csv,
                                 write_plots)


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
        ]
        summary = summarize(rows)
        self.assertEqual(summary[0]["solved"], 1)
        self.assertEqual(summary[0]["timeout"], 1)
        self.assertEqual(summary[0]["median_search_time_ms"], 12)
        with tempfile.TemporaryDirectory() as directory:
            raw_path = Path(directory) / "raw.csv"
            summary_path = Path(directory) / "summary.csv"
            write_csv(raw_path, rows, RAW_FIELDS)
            write_csv(summary_path, summary, SUMMARY_FIELDS)
            with raw_path.open(encoding="utf-8-sig", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 2)
            with summary_path.open(encoding="utf-8-sig", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 1)
            json_path = Path(directory) / "results.json"
            json_path.write_text(json.dumps({"raw_results": rows, "summary": summary}), encoding="utf-8")
            self.assertEqual(len(json.loads(json_path.read_text(encoding="utf-8"))["raw_results"]), 2)

    def test_plot_export_with_isolated_sample_rows(self):
        rows = [{"group_id": "basic", "algorithm": "bfs", "status": "solved",
                 "valid_solution": True, "search_time_ms": 12, "peak_memory_kb": 3,
                 "expanded_nodes": 8, "solution_length": 4}]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_plots(rows, output)
            for name in ("search_time.png", "peak_memory.png", "expanded_nodes.png", "solution_length.png"):
                self.assertTrue((output / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
