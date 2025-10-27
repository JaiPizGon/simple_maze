from src.simple_maze import generate_maze, astar, grid_to_ascii, save_images


def main(rows: int = 12, cols: int = 20, seed: int | None = None) -> None:
    """Generate a maze, solve it with A*, and emit ASCII and images.

    Args:
        rows: logical number of rows (rooms).
        cols: logical number of columns (rooms).
        seed: optional seed for reproducibility.
    """
    grid = generate_maze(rows, cols, seed=seed)
    start = (1, 1)
    end = (len(grid) - 2, len(grid[0]) - 2)
    path = astar(grid, start, end)

    print(grid_to_ascii(grid, path, start, end))

    no_path_fn, path_fn = save_images(grid, path, start, end, cell_size=16, out_prefix="maze_out")
    print(f"Saved images: {no_path_fn}, {path_fn}")


if __name__ == "__main__":
    main()
