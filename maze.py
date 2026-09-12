"""
Maze Generator + Solver — generates random mazes with a randomized
depth-first "recursive backtracker" carve (which always produces a
"perfect maze": a spanning tree over every cell, so there's exactly one
path between any two cells and every cell is reachable — solvability is a
structural guarantee of the generation algorithm, not something checked
after the fact). Solves with BFS for the shortest path, and renders both
as ASCII art.
"""

import argparse
import random
from collections import deque

DIRECTION_DELTAS = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}


class Maze:
    def __init__(self, width, height, passages, start=(0, 0), end=None):
        self.width = width
        self.height = height
        self.passages = passages  # {(row, col): set of open directions}
        self.start = start
        self.end = end or (height - 1, width - 1)

    def neighbors(self, cell):
        r, c = cell
        result = []
        for d in self.passages.get(cell, ()):
            dr, dc = DIRECTION_DELTAS[d]
            result.append((r + dr, c + dc))
        return result

    def edge_count(self):
        """Total undirected passages (each recorded on both endpoints, so
        divide by 2). For a perfect maze over width*height cells this
        should equal width*height - 1 (a spanning tree)."""
        return sum(len(dirs) for dirs in self.passages.values()) // 2


def generate_maze(width, height, rng=None, start=(0, 0), end=None):
    """Randomized depth-first backtracker: carves a spanning tree over the
    grid by repeatedly stepping to a random unvisited neighbor and
    backtracking on dead ends. Every generated maze is, by construction, a
    perfect maze — fully connected with no cycles."""
    if width < 1 or height < 1:
        raise ValueError("width and height must be at least 1")
    rng = rng or random.Random()

    passages = {(r, c): set() for r in range(height) for c in range(width)}
    visited = {start}
    stack = [start]

    while stack:
        r, c = stack[-1]
        candidates = []
        for d, (dr, dc) in DIRECTION_DELTAS.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < height and 0 <= nc < width and (nr, nc) not in visited:
                candidates.append((nr, nc, d))

        if not candidates:
            stack.pop()
            continue

        nr, nc, d = rng.choice(candidates)
        passages[(r, c)].add(d)
        passages[(nr, nc)].add(OPPOSITE[d])
        visited.add((nr, nc))
        stack.append((nr, nc))

    return Maze(width, height, passages, start=start, end=end)


def solve_bfs(maze):
    """Shortest path from maze.start to maze.end via BFS, following only
    open passages. Returns the path as a list of cells, or None if
    unreachable (works for ANY maze passed in, not just generated ones —
    so it correctly reports None for a deliberately disconnected maze,
    which is exercised in the tests)."""
    start, end = maze.start, maze.end
    if start not in maze.passages or end not in maze.passages:
        return None

    came_from = {start: None}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if current == end:
            break
        for neighbor in maze.neighbors(current):
            if neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)

    if end not in came_from:
        return None

    path = []
    node = end
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path


def render_maze(maze, path=None):
    path_cells = set(path or [])
    height, width = maze.height, maze.width
    grid = [["#"] * (2 * width + 1) for _ in range(2 * height + 1)]

    for (r, c), dirs in maze.passages.items():
        grid[2 * r + 1][2 * c + 1] = " "
        if "E" in dirs:
            grid[2 * r + 1][2 * c + 2] = " "
        if "S" in dirs:
            grid[2 * r + 2][2 * c + 1] = " "

    for (r, c) in path_cells:
        if (r, c) not in (maze.start, maze.end):
            grid[2 * r + 1][2 * c + 1] = "."

    sr, sc = maze.start
    er, ec = maze.end
    grid[2 * sr + 1][2 * sc + 1] = "S"
    grid[2 * er + 1][2 * ec + 1] = "E"

    return "\n".join("".join(row) for row in grid)


def main():
    parser = argparse.ArgumentParser(description="Maze Generator + Solver")
    parser.add_argument("--width", type=int, default=15)
    parser.add_argument("--height", type=int, default=10)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    maze = generate_maze(args.width, args.height, rng=rng)

    print(f"Generated {args.width}x{args.height} maze ({maze.edge_count()} passages):")
    print(render_maze(maze))
    print()

    path = solve_bfs(maze)
    if path is None:
        print("No solution found (unexpected for a generated maze!).")
    else:
        print(f"Solved — shortest path is {len(path) - 1} steps:")
        print(render_maze(maze, path=path))


if __name__ == "__main__":
    main()
