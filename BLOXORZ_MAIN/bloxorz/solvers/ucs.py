import heapq
from itertools import count
from time import perf_counter

from .common import edge_cost, finish


def search(engine, start, deadline=float("inf")):
    order = count()                        
    frontier = [(0, next(order), start)]
    parents = {start: None}              
    costs = {start: 0}                     
    closed = set()
    expanded = 0

    while frontier:
        cost, _, state = heapq.heappop(frontier)
        if perf_counter() >= deadline:
            return finish(None, parents, costs, expanded, "timeout")
        if state in closed or cost > costs[state]:
            continue                      
        if engine.is_goal(state):
            return finish(state, parents, costs, expanded, "solved")

        closed.add(state)
        expanded += 1
        for action, child in engine.successors(state):
            if child in closed:
                continue
            new_cost = cost + edge_cost(engine, child)
            if child not in costs or new_cost < costs[child]:
                costs[child] = new_cost
                parents[child] = (state, action)
                heapq.heappush(frontier, (new_cost, next(order), child))

    return finish(None, parents, costs, expanded, "no_solution")