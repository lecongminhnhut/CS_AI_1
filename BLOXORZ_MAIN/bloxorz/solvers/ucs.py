from heapq import heappop, heappush
from itertools import count
from time import perf_counter

from .common import edge_cost, finish, search_successors


def search(engine, start, deadline=float("inf")):
    sequence = count()
    frontier = [(0, next(sequence), start)]
    parents = {start: None}
    costs = {start: 0}
    closed = set()
    expanded = 0

    while frontier:
        if perf_counter() >= deadline:
            return finish(None, parents, costs, expanded, "timeout")
        cost, _order, current = heappop(frontier)
        if current in closed or cost > costs[current]:
            continue
        if engine.is_goal(current):
            return finish(current, parents, costs, expanded, "solved")

        closed.add(current)
        expanded += 1
        for actions, next_state in search_successors(engine, current):
            if perf_counter() >= deadline:
                return finish(None, parents, costs, expanded, "timeout")
            if next_state in closed:
                continue
            new_cost = cost + edge_cost(engine, next_state)
            if next_state not in costs or new_cost < costs[next_state]:
                costs[next_state] = new_cost
                parents[next_state] = current, actions
                heappush(frontier, (new_cost, next(sequence), next_state))

    return finish(None, parents, costs, expanded, "no_solution")