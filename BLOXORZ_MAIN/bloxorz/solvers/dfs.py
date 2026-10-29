from time import perf_counter
from .common import edge_cost, finish, search_successors


def search(engine, start, deadline=float("inf")):
    frontier = [start]
    parents = {start: None}
    costs = {start: 0}
    closed = set()
    expanded = 0

    while frontier:
        if perf_counter() >= deadline:
            return finish(None, parents, costs, expanded, "timeout")
        state = frontier.pop()

        if state in closed:
            continue

        if engine.is_goal(state):
            return finish(state, parents, costs, expanded, "solved")

        closed.add(state)
        expanded += 1

        for actions, child in search_successors(engine, state):
            if perf_counter() >= deadline:
                return finish(None, parents, costs, expanded, "timeout")
            if child in closed:
                continue

            costs[child] = costs[state] + edge_cost(engine, child)
            parents[child] = (state, actions)
            frontier.append(child)

    return finish(None, parents, costs, expanded, "no_solution")
