from time import perf_counter
from .common import edge_cost, finish


def search(engine, start, deadline=float("inf")):
    frontier = [start]
    parents = {start: None}
    costs = {start: 0}
    closed = set()
    expanded = 0

    while frontier:
        state = frontier.pop()
        
        if state in closed:
            continue
            
        if engine.is_goal(state):
            return finish(state, parents, costs, expanded, "solved")
            
        if perf_counter() >= deadline:
            return finish(None, parents, costs, expanded, "timeout")

        closed.add(state)
        expanded += 1
        
        for action, child in engine.successors(state):
            if child in closed:
                continue
                
            costs[child] = costs[state] + edge_cost(engine, child)
            parents[child] = (state, action)
            frontier.append(child)

    return finish(None, parents, costs, expanded, "no_solution")