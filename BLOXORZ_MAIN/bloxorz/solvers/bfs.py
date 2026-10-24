
from collections import deque  
from time import perf_counter  

from .common import edge_cost, finish  

def search(engine, start, deadline):
    queue = deque([start]) 
    parents = {start: None}  
    costs = {start: 0} 
    expanded = 0

    while queue:  
        if perf_counter() >= deadline: 
            return finish(None, parents, costs, expanded, "timeout")

        current = queue.popleft()  

        if engine.is_goal(current): 
            return finish(current, parents, costs, expanded, "solved")

        expanded += 1  
        for action, next_state in engine.successors(current): 
            if next_state in parents:  
                continue  

            parents[next_state] = (current, action)  
            costs[next_state] = costs[current] + edge_cost(engine, next_state)
            queue.append(next_state)  

    return finish(None, parents, costs, expanded, "no_solution")
