def edge_cost(engine, state):
    return 1 + sum(engine.board.tile(cell) == "F" for cell in state.cells)


def finish(found, parents, costs, expanded, status):
    actions = []
    current = found
    while current is not None and parents[current] is not None:
        current, action = parents[current]
        actions.append(action.value)
    actions.reverse()
    return {"status": status, "actions": actions, "expanded": expanded,
            "length": len(actions) if found is not None else None,
            "cost": costs[found] if found is not None else None}
