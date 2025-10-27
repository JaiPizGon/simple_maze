"""Rendering utilities for the maze: ASCII and images.

The image functions use Pillow to create a visualization of the grid. Walls are
dark gray, walkable light gray, start green, end red, and path cells blue.
Thin black separators are drawn between cells.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from PIL import Image, ImageDraw

Coord = Tuple[int, int]


def grid_to_ascii(
    grid: List[List[int]],
    path: Optional[List[Coord]] = None,
    start: Optional[Coord] = None,
    end: Optional[Coord] = None,
    start_sym: str = "S",
    end_sym: str = "E",
    wall_sym: str = "█",
    path_sym: str = "*",
    walkable_sym: str = ".",
) -> str:
    """Return an ASCII representation of the maze using customizable symbols.

    The function renders the grid into a multiline string. By default the
    following symbols are used:
    - start: ``S``
    - end: ``E``
    - wall: ``█``
    - path (non start/end cells): ``*``
    - walkable cells: ``.``

    Args:
        grid: 2D grid where 1 is walkable and 0 is wall.
        path: optional list of coordinates that form the solution path.
        start: optional start coordinate to mark with ``start_sym``.
        end: optional end coordinate to mark with ``end_sym``.
        start_sym: symbol used for the start cell. Defaults to ``'S'``.
        end_sym: symbol used for the end cell. Defaults to ``'E'``.
        wall_sym: symbol used for walls. Defaults to ``'█'``.
        path_sym: symbol used for path cells (excluding start/end). Defaults to ``'*'``.
        walkable_sym: symbol used for ordinary walkable cells. Defaults to ``'.'``.

    Returns:
        A multiline string with characters representing the maze.
    """

    path_set = set(path) if path else set()
    lines: List[str] = []
    for r, row in enumerate(grid):
        line_chars: List[str] = []
        for c, cell in enumerate(row):
            coord = (r, c)
            if start is not None and coord == start:
                line_chars.append(start_sym)
            elif end is not None and coord == end:
                line_chars.append(end_sym)
            elif coord in path_set and coord != start and coord != end:
                line_chars.append(path_sym)
            elif cell == 0:
                line_chars.append(wall_sym)
            else:
                line_chars.append(walkable_sym)
        lines.append("".join(line_chars))
    return "\n".join(lines)


def save_images(grid: List[List[int]], path: Optional[List[Coord]] = None,
                start: Optional[Coord] = None, end: Optional[Coord] = None,
                cell_size: int = 16, out_prefix: str = "maze") -> Tuple[str, str]:
    """Save two PNG images: one without the path and one including the path.

    Args:
        grid: 2D grid where 1 is walkable and 0 is wall.
        path: optional solution path.
        start: optional start coordinate.
        end: optional end coordinate.
        cell_size: size in pixels of each cell.
        out_prefix: prefix for output filenames.

    Returns:
        Tuple of filenames (without_path_png, with_path_png).
    """
    rows = len(grid)
    cols = len(grid[0])
    # line thickness 1 pixel between cells
    img_w = cols * cell_size + (cols + 1)
    img_h = rows * cell_size + (rows + 1)

    def draw(with_path: bool) -> Image.Image:
        img = Image.new("RGB", (img_w, img_h), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        wall_color = (40, 40, 40)        # very dark gray
        floor_color = (211, 211, 211)    # lightgray
        start_color = (0, 200, 0)
        end_color = (200, 0, 0)
        path_color = (0, 0, 200)

        def cell_bbox(r: int, c: int):
            x0 = c * cell_size + (c + 1)
            y0 = r * cell_size + (r + 1)
            x1 = x0 + cell_size - 1
            y1 = y0 + cell_size - 1
            return x0, y0, x1, y1

        path_set = set(path) if path else set()

        for r in range(rows):
            for c in range(cols):
                bbox = cell_bbox(r, c)
                if grid[r][c] == 0:
                    draw.rectangle(bbox, fill=wall_color)
                else:
                    draw.rectangle(bbox, fill=floor_color)

        # draw path on top if requested
        if with_path and path:
            for (r, c) in path:
                if (r, c) == start or (r, c) == end:
                    continue
                bbox = cell_bbox(r, c)
                draw.rectangle(bbox, fill=path_color)

        # draw start and end
        if start:
            draw.rectangle(cell_bbox(*start), fill=start_color)
        if end:
            draw.rectangle(cell_bbox(*end), fill=end_color)

        # thin black separators already present as background; optionally draw outlines
        return img

    img_no = draw(False)
    img_yes = draw(True)

    fn_no = f"{out_prefix}.png"
    fn_yes = f"{out_prefix}_path.png"
    img_no.save(fn_no)
    img_yes.save(fn_yes)
    return fn_no, fn_yes


if __name__ == "__main__":
    from .generator import generate_maze
    from .solver import astar

    g = generate_maze(10, 16, seed=1)
    start = (1, 1)
    end = (len(g) - 2, len(g[0]) - 2)
    p = astar(g, start, end)
    print(grid_to_ascii(g, p, start, end))
    save_images(g, p, start, end, cell_size=12, out_prefix="demo_maze")
