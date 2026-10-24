"""Dispatch and measure searches; implementations live in solvers/*.py."""

import time
import tracemalloc
from importlib import import_module
from threading import Lock

from .engine import Engine, State
from .solvers.common import finish

_measurement_lock = Lock()
_ALGORITHMS = ("bfs", "dfs", "ucs", "astar")


def solve(engine: Engine, start: State, algorithm: str, seconds: float | None = None) -> dict:
    if algorithm not in _ALGORITHMS:
        raise ValueError("Unknown search algorithm")
    module_name = f"{__package__}.solvers.{algorithm}"
    try:
        search = import_module(module_name).search
    except ModuleNotFoundError as error:
        if error.name != module_name:
            raise
        raise ValueError(f"Thuật toán {algorithm.upper()} chưa được cài đặt. "
                         f"Cần tạo bloxorz/solvers/{algorithm}.py với hàm search(engine, start, deadline).") from error
    started = time.perf_counter()
    acquired = _measurement_lock.acquire() if seconds is None else _measurement_lock.acquire(timeout=max(0, seconds))
    if not acquired:
        result = finish(None, {}, {}, 0, "timeout")
        result.update(algorithm=algorithm, time_ms=round((time.perf_counter() - started) * 1000, 2), peak_kb=0)
        return result
    try:
        tracemalloc.start()
        try:
            deadline = float("inf") if seconds is None else started + seconds
            result = search(engine, start, deadline)
            result.update(algorithm=algorithm, time_ms=round((time.perf_counter() - started) * 1000, 2),
                          peak_kb=round(tracemalloc.get_traced_memory()[1] / 1024, 2))
            return result
        finally:
            tracemalloc.stop()
    finally:
        _measurement_lock.release()
