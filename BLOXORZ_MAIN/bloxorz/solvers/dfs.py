
"""Depth-First Search (DFS) solver for Bloxorz."""

import math
import time

from .common import edge_cost, finish


def search(engine, start, deadline=None):
    stack = [start]

    visited = {start}

    parents = {start: None}

    costs = {start: 0}

    expanded = 0

    while stack:
        if deadline is not None and time.monotonic() >= deadline:
            return finish(
                None, parents, costs, expanded, "timeout"
            )

        state = stack.pop()

        if engine.is_goal(state):
            return finish(
                state, parents, costs, expanded, "solved"
            )

        expanded += 1

        for action, next_state in engine.successors(state):
            if next_state in visited:
                continue

            visited.add(next_state)

            parents[next_state] = (state, action)

            costs[next_state] = (
                costs[state] + edge_cost(engine, next_state)
            )

            stack.append(next_state)

    return finish(
        None, parents, costs, expanded, "no_solution"
    )
