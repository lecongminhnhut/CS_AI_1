from heapq import heappop, heappush
from itertools import count
from math import inf
from time import perf_counter

from .common import edge_cost, finish, search_successors


class PreparationTimeout(Exception):
    """Không dùng bảng khoảng cách đang dựng dở khi hết deadline."""


def _manhattan(first, second):
    """Khoảng cách hàng + khoảng cách cột giữa hai ô."""
    return abs(first[0] - second[0]) + abs(first[1] - second[1])


class PointObjectHeuristic:
    """Chuẩn bị khoảng cách một lần; sau đó dùng lại khi A* xét các trạng thái."""

    def __init__(self, engine, deadline=inf):

        def check_time():
            if perf_counter() >= deadline:
                raise PreparationTimeout

        check_time()
        goal = engine.board.goal

        teleports = []
        nodes = {goal}
        for switch in engine.board.switches:
            check_time()
            if switch.kind == "split":
                nodes.add(switch.cell)
                for destination in switch.destinations:
                    nodes.add(destination)
                    teleports.append((switch.cell, destination))
        nodes = tuple(sorted(nodes))
        self.state_count = len(nodes)
        indices = {cell: index for index, cell in enumerate(nodes)}
        goal_index = indices[goal]

        distances = []
        for first in nodes:
            check_time()
            distances.append([_manhattan(first, second) for second in nodes])
        for source, target in teleports:
            distances[indices[source]][indices[target]] = 0

        for middle in range(len(nodes)):
            check_time()
            for source in range(len(nodes)):
                check_time()
                for target in range(len(nodes)):
                    through_middle = distances[source][middle] + distances[middle][target]
                    if through_middle < distances[source][target]:
                        distances[source][target] = through_middle

        self.to_goal = []
        for index, cell in enumerate(nodes):
            self.to_goal.append((cell, distances[index][goal_index]))
        check_time()

    def point_distance(self, cell):
        """Thử đi tới từng mốc, rồi dùng khoảng cách đã tính từ mốc tới G."""
        shortest = inf
        for node, remaining in self.to_goal:
            distance = _manhattan(cell, node) + remaining
            shortest = min(shortest, distance)
        return shortest

    def __call__(self, state):
        """Lấy ô gần đích nhất trong các ô khối đang chiếm để tính h."""
        shortest = inf
        for cell in state.cells:
            shortest = min(shortest, self.point_distance(cell))

        return (shortest + 1) // 2


def heuristic(engine, state, prepared=None):
    """Trả h; truyền prepared để dùng lại phần đã chuẩn bị."""
    if engine.is_goal(state):
        return 0
    if prepared is None:
        prepared = PointObjectHeuristic(engine)
    return prepared(state)


def search(engine, start, deadline):
    """Tìm đường có tổng chi phí nhỏ nhất bằng A*."""
    parents = {start: None}  # Trạng thái trước và thao tác để đi tới mỗi trạng thái.
    costs = {start: 0}       # Chi phí g tốt nhất hiện biết đc.
    if perf_counter() >= deadline:
        return finish(None, parents, costs, 0, "timeout")
    if engine.is_goal(start):
        return finish(start, parents, costs, 0, "solved")

    # 1. Chuẩn bị heuristic cho lượt tìm này.
    prepared_at = perf_counter()
    try:
        prepared = PointObjectHeuristic(engine, deadline)
    except PreparationTimeout:
        return finish(None, parents, costs, 0, "timeout")
    preparation_ms = round((perf_counter() - prepared_at) * 1000, 2)

    def result(found, expanded, status):
        """Dựng lời giải và bổ sung số liệu của bước chuẩn bị."""
        output = finish(found, parents, costs, expanded, status)
        output.update(heuristic_states=prepared.state_count, heuristic_time_ms=preparation_ms)
        return output

    # 2. Heap ưu tiên f nhỏ nhất; nếu cùng f thì xét theo thứ tự đưa vào.
    h = heuristic(engine, start, prepared)
    sequence = count()
    # Mỗi mục: (f, số thứ tự, g, trạng thái).
    frontier = [(h, next(sequence), 0, start)]
    expanded = 0
    while frontier:
        if perf_counter() >= deadline:
            return result(None, expanded, "timeout")
        _f, _order, cost, current = heappop(frontier)

        # 3. Bỏ mục heap cũ nếu đã tìm được đường tốt hơn tới trạng thái đó.
        if cost != costs[current]:
            continue
        if engine.is_goal(current):
            return result(current, expanded, "solved")
        # 4. Sinh các nước đi hợp lệ bằng luật của engine.
        expanded += 1
        for action, next_state in search_successors(engine, current):
            if perf_counter() >= deadline:
                return result(None, expanded, "timeout")
            new_cost = cost + edge_cost(engine, next_state)

            # Chỉ cập nhật nếu tìm được đường có chi phí thấp hơn.
            if new_cost >= costs.get(next_state, inf):
                continue

            costs[next_state] = new_cost
            parents[next_state] = current, action

            h = heuristic(engine, next_state, prepared)
            f = new_cost + h
            heappush(frontier, (f, next(sequence), new_cost, next_state))

    # Không còn trạng thái để xét -> không có lời giải.
    return result(None, expanded, "no_solution")
