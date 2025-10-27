"""A* path finding for the maze grid.

This module implements a simple A* search over the grid produced by
`generate_maze`. It expects a grid where 1 means walkable and 0 means wall.
"""
from __future__ import annotations

import heapq
from typing import List, Tuple, Optional, Dict


Coord = Tuple[int, int]


def _neighbors(grid: List[List[int]], node: Coord) -> List[Coord]:
    rows = len(grid)
    cols = len(grid[0])
    r, c = node
    nbrs = []
    for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
            nbrs.append((nr, nc))
    return nbrs


def _heuristic(a: Coord, b: Coord) -> int:
    # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid: List[List[int]], start: Coord, goal: Coord) -> Optional[List[Coord]]:
    """Find a path from start to goal using A*.

    Args:
        grid: 2D grid where 1 is walkable and 0 is wall.
        start: (row, col) start coordinate.
        goal: (row, col) goal coordinate.

    Returns:
        A list of coordinates from start to goal (inclusive) if a path exists,
        otherwise None.
    """
    if grid[start[0]][start[1]] != 1 or grid[goal[0]][goal[1]] != 1:
        return None

    open_set: List[Tuple[int, Coord]] = []
    heapq.heappush(open_set, (0, start))

    came_from: Dict[Coord, Coord] = {}
    gscore: Dict[Coord, int] = {start: 0}
    fscore: Dict[Coord, int] = {start: _heuristic(start, goal)}

    closed = set()

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            # reconstruct path
            path = [current]
            while path[-1] != start:
                path.append(came_from[path[-1]])
            path.reverse()
            return path

        closed.add(current)

        for nbr in _neighbors(grid, current):
            if nbr in closed:
                continue
            tentative_g = gscore[current] + 1
            if tentative_g < gscore.get(nbr, 1_000_000):
                came_from[nbr] = current
                gscore[nbr] = tentative_g
                f = tentative_g + _heuristic(nbr, goal)
                fscore[nbr] = f
                heapq.heappush(open_set, (f, nbr))

    return None


if __name__ == "__main__":
    # quick smoke test
    from .generator import generate_maze

    g = generate_maze(5, 8, seed=2)
    start = (1, 1)
    goal = (len(g) - 2, len(g[0]) - 2)
    p = astar(g, start, goal)
    print("Path length:", len(p) if p else None)
