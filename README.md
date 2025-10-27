# simple_maze

Tiny Python package to generate grid mazes, solve them with A* and render
ASCII and PNG visualizations. The project includes utilities to pick valid
start/end cells, force a maze to become unsolvable, or introduce additional
solutions by breaking walls.

Features
- Generate perfect mazes (recursive backtracker) as a grid where `1` is
	walkable and `0` is a wall.
- Solve with A* (`src/maze/solver.py`).
- Render ASCII (`grid_to_ascii`) with customizable symbols.
- Render PNG images (Pillow) with start (green), end (red), path (blue),
	walls (dark gray) and floors (light gray).
- Helpers: `find_valid_cell`, `make_unsolvable`, `make_multiple_solutions`.

Quick install

This project requires Python 3.8+ and Pillow for image output. Install the
dependency into your environment:

```bash
pip install pillow
```

Running the example notebook

Open the example notebook `examples/maze_example.ipynb` with Jupyter or run it
in a supported environment (VS Code/Jupyter Lab). The notebook demonstrates:
- generating and solving a maze
- saving two images (with and without the path)
- creating an unsolvable variant
- creating a variant with multiple distinct solutions

If running the notebook from the repository you may need to add the project
`src` folder to `PYTHONPATH`. From the repository root you can run a small
script or open a Python REPL like this:

```bash
python3 -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('src').resolve())); from simple_maze import generate_maze, astar, grid_to_ascii; g=generate_maze(12,20,seed=42); print(grid_to_ascii(g, None))"
```

Basic usage (script)

```python
from simple_maze import (
		generate_maze,
		astar,
		grid_to_ascii,
		save_images,
		find_valid_cell,
)

# generate
grid = generate_maze(12, 20, seed=42)
start = find_valid_cell(grid, seed=1)
end = find_valid_cell(grid, exclude={start}, seed=2)
path = astar(grid, start, end)

print(grid_to_ascii(grid, path, start, end))
save_images(grid, path, start, end, cell_size=24, out_prefix='maze_out')
```

API (key functions)
- `generate_maze(rows, cols, seed=None)` -> grid
- `astar(grid, start, end)` -> list of coordinates or `None`
- `grid_to_ascii(grid, path=None, start=None, end=None, ...)` -> str (customizable symbols)
- `save_images(grid, path=None, start=None, end=None, cell_size=16, out_prefix='maze')` -> (fn_no, fn_yes)
- `find_valid_cell(grid, exclude=None, seed=None)` -> (row, col)
- `make_unsolvable(grid, start, end, astar_fn, ...)` -> bool (modifies grid)
- `make_multiple_solutions(grid, start, end, astar_fn, ...)` -> bool (modifies grid)

Notes
- The generator produces a perfect maze (a spanning tree). That means there
	is exactly one path between any two room cells until you deliberately
	break walls (e.g. with `make_multiple_solutions`). Use `find_valid_cell`
	to pick valid walkable start/end cells.
- Images are saved to the working directory. Filenames are returned by
	`save_images`.

Contributing
- Small, self-contained patches are welcome. Please keep docstrings and
	code PEP8-compatible and add a short test if you change core behaviour.

License
- This repository does not include an explicit license file. Add one if you
	intend to publish or share the code.
