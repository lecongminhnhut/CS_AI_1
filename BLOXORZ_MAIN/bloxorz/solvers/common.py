from ..models import Action


def search_successors(engine, state):
    for action, next_state in engine.successors(state):
        if action != Action.SWITCH:
            yield (action,), next_state
            continue
        for direction, target in engine.successors(next_state):
            if direction != Action.SWITCH:
                yield (Action.SWITCH, direction), target


def edge_cost(engine, state):
    return 1 + sum(engine.board.tile(cell) == "F" for cell in state.cells)


def finish(found, parents, costs, expanded, status):
    groups = []
    current = found
    while current is not None and parents[current] is not None:
        current, actions = parents[current]
        groups.append(actions)
    groups.reverse()
    actions = [action.value for group in groups for action in group]
    return {"status": status, "actions": actions, "expanded": expanded,
            "length": sum(action != "switch" for action in actions) if found is not None else None,
            "cost": costs[found] if found is not None else None}
