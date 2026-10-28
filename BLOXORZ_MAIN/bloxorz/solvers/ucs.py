from heapq import heappop, heappush
from itertools import count
from time import perf_counter

from .common import edge_cost, finish


def search(engine, start, deadline=float("inf")):
    sequence = count()
    frontier = [(0, next(sequence), start)]
    parents = {start: None}
    costs = {start: 0}
    closed = set()
    expanded = 0

    while frontier:
        cost, _order, current = heappop(frontier)
        if perf_counter() >= deadline:
            return finish(None, parents, costs, expanded, "timeout")
        if current in closed or cost > costs[current]:
            continue
        if engine.is_goal(current):
            return finish(current, parents, costs, expanded, "solved")

        closed.add(current)
        expanded += 1
        for action, next_state in engine.successors(current):
            if next_state in closed:
                continue
            new_cost = cost + edge_cost(engine, next_state)
            if next_state not in costs or new_cost < costs[next_state]:
                costs[next_state] = new_cost
                parents[next_state] = current, action
                heappush(frontier, (new_cost, next(sequence), next_state))

    return finish(None, parents, costs, expanded, "no_solution")