"""Maze generation utilities.

This module implements a randomized depth-first search (recursive backtracker)
to carve a perfect maze into a grid that includes walls as cells. The
public function `generate_maze` accepts the number of logical rows and columns
and returns a grid of size (2*rows+1) x (2*cols+1) where 1 indicates a
walkable cell and 0 indicates a wall.

The grid layout uses odd indices for rooms/cells and even indices for walls.
This makes it simple to carve passages by stepping two cells at a time and
clearing the intermediate wall.

All functions follow Google style docstrings and minimal external deps.
"""
from __future__ import annotations

import random
from typing import List, Optional, Tuple, Set, Callable


def _make_grid(rows: int, cols: int) -> List[List[int]]:
    """Create a grid initialized with walls (0).

    Args:
        rows: number of logical rows (rooms).
        cols: number of logical columns (rooms).

    Returns:
        A list of lists representing the grid with shape (2*rows+1) x (2*cols+1).
    """
    height = 2 * rows + 1
    width = 2 * cols + 1
    return [[0 for _ in range(width)] for _ in range(height)]


def generate_maze(rows: int, cols: int, seed: Optional[int] = None) -> List[List[int]]:
    """Generate a perfect maze using recursive backtracker.

    The returned grid is (2*rows+1) x (2*cols+1) with:
    - 1: walkable cell
    - 0: wall

    Args:
        rows: number of logical rows (rooms).
        cols: number of logical columns (rooms).
        seed: optional random seed for reproducibility.

    Returns:
        A 2D grid of ints (1 walkable, 0 wall).

    Raises:
        ValueError: if rows or cols are less than 1.
    """
    if rows < 1 or cols < 1:
        raise ValueError("rows and cols must be >= 1")

    rng = random.Random(seed)
    grid = _make_grid(rows, cols)

    # Helper to convert room coordinates (r,c) in [0,rows) to grid coords
    def to_grid(rc: Tuple[int, int]) -> Tuple[int, int]:
        r, c = rc
        return 2 * r + 1, 2 * c + 1

    visited = [[False for _ in range(cols)] for _ in range(rows)]

    # Neighbor deltas in room coordinates (4-connectivity)
    deltas = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def carve(r: int, c: int) -> None:
        """Recursively carve passages starting from room (r,c)."""
        visited[r][c] = True
        gr, gc = to_grid((r, c))
        grid[gr][gc] = 1

        # randomize neighbor order
        rng.shuffle(deltas)
        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                # remove wall between (r,c) and (nr,nc)
                gr2, gc2 = to_grid((nr, nc))
                wall_r, wall_c = (gr + gr2) // 2, (gc + gc2) // 2
                grid[wall_r][wall_c] = 1
                carve(nr, nc)

    carve(0, 0)

    return grid


def find_valid_cell(grid: List[List[int]], exclude: Optional[Set[Tuple[int, int]]] = None,
                    seed: Optional[int] = None) -> Tuple[int, int]:
    """Return a random valid (walkable) cell coordinate from the grid.

    The function scans the provided `grid` (where 1 means walkable and 0 means
    wall) and returns a randomly chosen coordinate (row, col) such that the
    cell is walkable and not in the optional `exclude` set.

    Args:
        grid: 2D grid produced by :func:`generate_maze` where 1 is walkable.
        exclude: optional set of coordinates to avoid (for example the start
            when choosing an end cell).
        seed: optional integer seed for reproducible selection. If omitted a
            default random source is used.

    Returns:
        A tuple (row, col) pointing to a walkable cell in the grid.

    Raises:
        ValueError: if no valid cell can be found (for example a grid with no
            walkable cells or all walkable cells are excluded).
    """
    rng = random.Random(seed)
    rows = len(grid)
    if rows == 0:
        raise ValueError("grid must be non-empty")
    cols = len(grid[0])

    exclude = exclude or set()

    # collect all walkable cells not in exclude
    candidates: List[Tuple[int, int]] = [
        (r, c)
        for r in range(rows)
        for c in range(cols)
        if grid[r][c] == 1 and (r, c) not in exclude
    ]

    if not candidates:
        raise ValueError("no valid walkable cells available to choose from")

    return rng.choice(candidates)


def make_multiple_solutions(
    grid: List[List[int]],
    start: Tuple[int, int],
    end: Tuple[int, int],
    astar_fn: Callable,
    max_tries: int = 200,
    seed: Optional[int] = None,
) -> bool:
    """Modify ``grid`` by breaking walls until the maze has multiple solutions.

    This function attempts to create an alternate path between ``start`` and
    ``end`` by turning wall cells (0) into walkable cells (1). After each
    candidate wall removal it calls ``astar_fn(grid, start, end)`` to check if
    the returned path differs from the original one. The grid is modified in
    place and the function returns True on success.

    Args:
        grid: 2D grid where 1 is walkable and 0 is wall.
        start: start coordinate (row, col).
        end: end coordinate (row, col).
        astar_fn: function implementing A* search with signature
            ``astar_fn(grid, start, end) -> Optional[List[Tuple[int,int]]]``.
        max_tries: maximum number of candidate walls to try.
        seed: optional seed for reproducibility.

    Returns:
        True if the grid was modified to produce multiple distinct solutions
        between start and end, False otherwise.

    Raises:
        ValueError: if start or end are not walkable.
    """
    rng = random.Random(seed)

    if grid[start[0]][start[1]] != 1 or grid[end[0]][end[1]] != 1:
        raise ValueError("start and end must be walkable cells (grid value 1)")

    orig_path = astar_fn(grid, start, end)
    if not orig_path:
        # nothing to make multiple if they are not connected
        return False

    rows = len(grid)
    cols = len(grid[0])

    # candidate wall cells that when removed connect two or more walkable neighbors
    candidates: List[Tuple[int, int]] = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                continue
            neighs = 0
            for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    neighs += 1
            if neighs >= 2:
                candidates.append((r, c))

    rng.shuffle(candidates)

    tries = 0
    for (r, c) in candidates:
        if tries >= max_tries:
            break
        tries += 1
        # try removing this wall
        grid[r][c] = 1
        new_path = astar_fn(grid, start, end)
        if new_path and new_path != orig_path:
            return True
        # revert
        grid[r][c] = 0

    return False


def make_unsolvable(
    grid: List[List[int]],
    start: Tuple[int, int],
    end: Tuple[int, int],
    astar_fn: Callable,
    seed: Optional[int] = None,
    max_tries: int = 100,
) -> bool:
    """Modify ``grid`` to make the maze unsolvable between ``start`` and
    ``end``.

    The function finds an existing path between ``start`` and ``end`` and
    then blocks one or more intermediate cells along that path (not start or
    end) to disconnect the endpoints. Returns True if the grid was modified
    and the two points are no longer connected.

    Args:
        grid: 2D grid where 1 is walkable and 0 is wall.
        start: start coordinate (row, col).
        end: end coordinate (row, col).
        astar_fn: function implementing A* search with signature
            ``astar_fn(grid, start, end) -> Optional[List[Tuple[int,int]]]``.
        seed: optional seed for reproducibility.
        max_tries: maximum attempts to block different intermediate cells.

    Returns:
        True if the grid was modified so that no path exists between start and end,
        False if unsuccessful.

    Raises:
        ValueError: if start or end are not walkable.
    """
    rng = random.Random(seed)

    if grid[start[0]][start[1]] != 1 or grid[end[0]][end[1]] != 1:
        raise ValueError("start and end must be walkable cells (grid value 1)")

    path = astar_fn(grid, start, end)
    if not path:
        # already unsolvable
        return True

    # consider intermediate path cells (exclude start/end)
    intermediates = [p for p in path[1:-1]]
    if not intermediates:
        # direct neighbors — blocking one neighbor should work though
        intermediates = [path[1]] if len(path) > 1 else []

    rng.shuffle(intermediates)
    tries = 0
    for cell in intermediates:
        if tries >= max_tries:
            break
        tries += 1
        r, c = cell
        saved = grid[r][c]
        grid[r][c] = 0
        if not astar_fn(grid, start, end):
            return True
        # revert and try next
        grid[r][c] = saved

    # as a fallback, try blocking additional nearby walkable cells
    rows = len(grid)
    cols = len(grid[0])
    all_walkables = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 1 and (r, c) not in (start, end)]
    rng.shuffle(all_walkables)
    for (r, c) in all_walkables[:max_tries]:
        saved = grid[r][c]
        grid[r][c] = 0
        if not astar_fn(grid, start, end):
            return True
        grid[r][c] = saved

    return False


if __name__ == "__main__":
    g = generate_maze(5, 10, seed=1)
    for row in g:
        print(''.join(['.' if c else '#' for c in row]))
