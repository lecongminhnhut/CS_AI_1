
from __future__ import annotations

import argparse
import csv
import json
import multiprocessing as mp
import math
import platform
from queue import Empty
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ALGORITHMS = ("bfs", "dfs", "ucs", "astar")
DEFAULT_TESTCASES = PROJECT_ROOT / "levels" / "testcases.json"
RAW_FIELDS = ["timestamp_utc", "run", "group_id", "group_name", "case_id", "case_name",
              "algorithm", "status", "search_time_ms", "peak_memory_kb", "expanded_nodes",
              "solution_length", "total_cost", "valid_solution", "error"]
SUMMARY_FIELDS = ["group_id", "group_name", "algorithm", "total_runs", "solved",
                  "no_solution", "timeout", "error", "invalid_solution", "success_rate_pct",
                  "median_search_time_ms", "mean_search_time_ms", "median_peak_memory_kb",
                  "median_expanded_nodes", "median_solution_length", "median_total_cost"]
METRICS = (("search_time_ms", "Search Time", "ms"),
           ("peak_memory_kb", "Peak Memory", "KB"),
           ("expanded_nodes", "Expanded Nodes", "nodes"),
           ("solution_length", "Solution Length", "moves"))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark solver Bloxorz trên bộ testcase cố định.")
    parser.add_argument("--timeout", type=float, default=30.0, help="giới hạn mỗi lượt (giây)")
    parser.add_argument("--repeat", type=int, default=1, help="số lượt lặp cho mỗi ca/thuật toán")
    parser.add_argument("--cases", default="", help="ID ca cách nhau bằng dấu phẩy")
    parser.add_argument("--testcases", type=Path, default=DEFAULT_TESTCASES)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "benchmark" / "results")
    parser.add_argument("--no-plots", action="store_true", help="bỏ qua tạo biểu đồ")
    return parser.parse_args(argv)


def load_cases(path: Path) -> list[tuple[str, str, dict[str, Any]]]:
    
    with path.open(encoding="utf-8") as stream:
        suite = json.load(stream)
    if not isinstance(suite, dict) or not isinstance(suite.get("groups"), list):
        raise ValueError("Testcase JSON cần có danh sách groups")
    cases: list[tuple[str, str, dict[str, Any]]] = []
    seen: set[str] = set()
    for group in suite["groups"]:
        if not isinstance(group, dict) or not isinstance(group.get("cases"), list):
            raise ValueError("Mỗi group cần là object có danh sách cases")
        group_id = str(group.get("id", ""))
        if not group_id:
            raise ValueError("Group thiếu id")
        group_name = str(group.get("name", group_id))
        for case in group["cases"]:
            if not isinstance(case, dict) or not isinstance(case.get("board"), dict):
                raise ValueError(f"Testcase trong group {group_id} thiếu board hợp lệ")
            case_id = str(case.get("id", ""))
            if not case_id or case_id in seen:
                raise ValueError(f"ID testcase thiếu hoặc trùng: {case_id!r}")
            seen.add(case_id)
            cases.append((group_id, group_name, case))
    if not cases:
        raise ValueError(f"Không có testcase trong {path}")
    return cases


def _worker(payload: dict[str, Any], output: Any, ready: Any) -> None:

    try:
        from bloxorz import Board, Engine
        from bloxorz.solver import solve
        from bloxorz.solvers.common import edge_cost

        board = Board.from_dict(payload["board"])
        engine = Engine(board)
        start = engine.initial_state()
        ready.set()
        result = solve(engine, start, payload["algorithm"], seconds=payload["timeout"])
        if not isinstance(result, dict):
            raise TypeError("solve() phải trả về dict")
        status = str(result.get("status", "error"))
        row: dict[str, Any] = {"status": status, "search_time_ms": result.get("time_ms"),
                               "peak_memory_kb": result.get("peak_kb"),
                               "expanded_nodes": result.get("expanded"),
                               "solution_length": result.get("length"), "total_cost": result.get("cost"),
                               "valid_solution": None, "error": ""}
        if status == "timeout":
            row["error"] = "Timeout nội bộ do solver kết thúc theo deadline"
        if status == "solved":
            actions = result.get("actions")
            if not isinstance(actions, list):
                valid, length, cost = False, None, None
            else:
                state, valid, cost, length = start, True, 0, 0
                for action in actions:
                    try:
                        next_state, _info = engine.transition(state, action)
                    except (TypeError, ValueError, KeyError):
                        valid = False
                        break
                    if next_state is None:
                        valid = False
                        break
                    if action != "switch":
                        length += 1
                        cost += edge_cost(engine, next_state)
                    state = next_state
                valid = valid and engine.is_goal(state)
            valid = valid and length == row["solution_length"] and cost == row["total_cost"]
            row["valid_solution"] = valid
            if not valid:
                row["status"] = "invalid_solution"
                row["error"] = "Lời giải không hợp lệ hoặc length/cost không khớp khi phát lại"
        output.put(row)
    except BaseException as exc:
        output.put({"status": "error", "search_time_ms": None, "peak_memory_kb": None,
                    "expanded_nodes": None, "solution_length": None, "total_cost": None,
                    "valid_solution": None, "error": f"{type(exc).__name__}: {exc}"})


def _number(value: Any) -> int | float | None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    return value if math.isfinite(value) else None


def _is_valid_solution(row: dict[str, Any]) -> bool:
    return row.get("status") == "solved" and row.get("valid_solution") is True


def _is_complete_run(row: dict[str, Any]) -> bool:
    return _is_valid_solution(row) or row.get("status") == "no_solution"


def _metric_rows(rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    if field in ("solution_length", "total_cost"):
        eligible = [row for row in rows if _is_valid_solution(row)]
    else:
        eligible = [row for row in rows if _is_complete_run(row)]
    return [row for row in eligible if _number(row.get(field)) is not None]


def run_one(group_id: str, group_name: str, case: dict[str, Any], algorithm: str,
            run_number: int, timeout: float) -> dict[str, Any]:
    row = {"timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "run": run_number, "group_id": group_id, "group_name": group_name,
           "case_id": case.get("id", ""), "case_name": case.get("name", ""),
           "algorithm": algorithm, "status": "error", "search_time_ms": None,
           "peak_memory_kb": None, "expanded_nodes": None, "solution_length": None,
           "total_cost": None, "valid_solution": None, "error": ""}
    context = mp.get_context("spawn")
    queue = context.Queue()
    ready = context.Event()
    process = context.Process(target=_worker, args=({"board": case.get("board"),
        "algorithm": algorithm, "timeout": timeout}, queue, ready))
    started = time.perf_counter()
    started_process = False
    try:
        process.start()
        started_process = True
        process.join(timeout)
        if process.is_alive():
            process.terminate()
            process.join(1)
            if process.is_alive():
                process.kill()
                process.join()
            phase = "sau khi worker khởi tạo" if ready.is_set() else "trước khi worker khởi tạo xong"
            row.update(status="timeout", search_time_ms=round((time.perf_counter() - started) * 1000, 3),
                       error=f"Timeout ngoài ({phase}), vượt {timeout:g}s; tiến trình đã dừng")
        else:
            try:
                result = queue.get(timeout=1)
            except Empty:
                result = None
            if result is None:
                row["error"] = f"Worker kết thúc bất thường (exit code {process.exitcode})"
            else:
                for key in ("status", "search_time_ms", "peak_memory_kb", "expanded_nodes",
                            "solution_length", "total_cost", "valid_solution", "error"):
                    row[key] = result.get(key)
    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if started_process and process.is_alive():
            process.terminate()
            process.join(1)
        ready.set()
        queue.cancel_join_thread()
        queue.close()
    return row


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault((str(row["group_id"]), str(row["group_name"]),
                           str(row["algorithm"])), []).append(row)
    summaries = []
    for (group_id, group_name, algorithm), items in sorted(groups.items()):
        def median(field: str) -> float | None:
            values = [float(item[field]) for item in _metric_rows(items, field)]
            return round(statistics.median(values), 3) if values else None
        solved = [item for item in items if _is_valid_solution(item)]
        times = [float(item["search_time_ms"]) for item in _metric_rows(items, "search_time_ms")]
        total = len(items)
        statuses = [item.get("status") for item in items]
        summaries.append({"group_id": group_id, "group_name": group_name,
            "algorithm": algorithm, "total_runs": total, "solved": len(solved),
            "no_solution": sum(s == "no_solution" for s in statuses),
            "timeout": sum(s == "timeout" for s in statuses), "error": sum(s == "error" for s in statuses),
            "invalid_solution": sum(s == "invalid_solution" for s in statuses),
            "success_rate_pct": round(100 * len(solved) / total, 2) if total else 0,
            "median_search_time_ms": median("search_time_ms"),
            "mean_search_time_ms": round(statistics.mean(times), 3) if times else None,
            "median_peak_memory_kb": median("peak_memory_kb"),
            "median_expanded_nodes": median("expanded_nodes"),
            "median_solution_length": median("solution_length"),
            "median_total_cost": median("total_cost")})
    return summaries


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_plots(rows: list[dict[str, Any]], output: Path) -> None:

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for field, title, unit in METRICS:
        groups = sorted({str(row["group_id"]) for row in rows})
        algorithms = [name for name in ALGORITHMS if any(row.get("algorithm") == name for row in rows)]
        series: dict[str, list[float]] = {}
        for algorithm in algorithms:
            values = []
            for group_id in groups:
                observed = [float(row[field]) for row in _metric_rows(
                    [row for row in rows if row.get("group_id") == group_id
                     and row.get("algorithm") == algorithm], field)]
                values.append(statistics.median(observed) if observed else float("nan"))
            series[algorithm.upper()] = values
        if not groups or not algorithms or not any(any(v == v for v in values) for values in series.values()):
            continue
        fig, axis = plt.subplots(figsize=(9, 5))
        for name, values in series.items():
            axis.plot(groups, values, marker="o", label=name)
        axis.set_title(title)
        axis.set_xlabel("Nhóm testcase")
        axis.set_ylabel(f"{title} ({unit})")
        axis.legend(title="Thuật toán")
        axis.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(output / {"search_time_ms": "search_time.png", "peak_memory_kb": "peak_memory.png",
                             "expanded_nodes": "expanded_nodes.png", "solution_length": "solution_length.png"}[field], dpi=160)
        plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.timeout <= 0 or args.repeat <= 0:
        print("--timeout và --repeat phải lớn hơn 0", file=sys.stderr)
        return 2
    try:
        cases = load_cases(args.testcases)
        requested = {value.strip() for value in args.cases.split(",") if value.strip()}
        if requested:
            available = {str(item[2]["id"]) for item in cases}
            missing = requested - available
            if missing:
                print("ID testcase không tồn tại: " + ", ".join(sorted(missing)), file=sys.stderr)
                return 2
            cases = [item for item in cases if str(item[2]["id"]) in requested]
    except Exception as exc:
        print(f"Không đọc được testcase: {exc}", file=sys.stderr)
        return 2
    args.output.mkdir(parents=True, exist_ok=True)
    raw = []
    total = len(cases) * len(ALGORITHMS) * args.repeat
    print(f"Cases: {len(cases)} | Algorithms: {len(ALGORITHMS)} | Rounds: {args.repeat} | Runs: {total}")
    for run_number in range(1, args.repeat + 1):
        for group_id, group_name, case in cases:
            for algorithm in ALGORITHMS:
                row = run_one(group_id, group_name, case, algorithm, run_number, args.timeout)
                raw.append(row)
                print(f"[{len(raw)}/{total}] {case['id']} {algorithm.upper()}: {row['status']}")
    summary = summarize(raw)
    write_csv(args.output / "benchmark_raw.csv", raw, RAW_FIELDS)
    write_csv(args.output / "benchmark_summary.csv", summary, SUMMARY_FIELDS)
    try:
        matplotlib_version = version("matplotlib")
    except PackageNotFoundError:
        matplotlib_version = None
    try:
        git_hash = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT,
                                  capture_output=True, text=True, check=True,
                                  timeout=2).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        git_hash = None
    metadata = {"generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "testcases_file": str(args.testcases.resolve()), "case_count": len(cases),
                "algorithms": list(ALGORITHMS), "repeat": args.repeat, "timeout_seconds": args.timeout,
                "python_version": sys.version, "python_executable": sys.executable,
                "operating_system": platform.platform(), "matplotlib_version": matplotlib_version,
                "git_commit": git_hash,
                "groups": sorted({group_id for group_id, _, _ in cases}),
                "note": "Metric hiệu năng gồm solved hợp lệ và no_solution hoàn tất; metric lời giải chỉ gồm solved hợp lệ. peak memory là tracemalloc của solver."}
    with (args.output / "benchmark_results.json").open("w", encoding="utf-8") as stream:
        json.dump({"metadata": metadata, "raw_results": raw, "summary": summary}, stream, ensure_ascii=False, indent=2)
    if not args.no_plots:
        try:
            write_plots(raw, args.output)
        except ImportError as exc:
            print(f"Không tạo được biểu đồ; cần matplotlib: {exc}", file=sys.stderr)
    print(f"Đã ghi kết quả vào {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
