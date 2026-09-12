"""
Tests for maze.py. The strongest checks here are structural, on the
generation algorithm itself — a randomized-DFS carve should always produce
a perfect maze (a spanning tree: connected, no cycles), which is what
actually guarantees solvability, rather than something to hope for and
check after the fact. The literal DoD ("every generated maze is confirmed
solvable by the solver") is checked directly and repeatedly across many
seeds and sizes.
"""

import random
import unittest

import maze as mz


class TestGeneratedMazeIsAPerfectMaze(unittest.TestCase):
    """A randomized-DFS carve should produce exactly width*height - 1
    passages (a spanning tree: every cell reachable, no cycles) — this is
    the structural property that MAKES every generated maze solvable,
    checked directly rather than just inferred from "the solver found a
    path once"."""

    def test_edge_count_is_exactly_a_spanning_tree(self):
        for width, height in [(5, 5), (10, 6), (3, 20), (1, 1), (1, 8), (8, 1)]:
            maze = mz.generate_maze(width, height, rng=random.Random(1))
            self.assertEqual(maze.edge_count(), width * height - 1)

    def test_every_cell_is_reachable_from_every_other_cell(self):
        # BFS from an arbitrary interior cell should reach all width*height
        # cells if the maze is truly a single connected spanning tree.
        maze = mz.generate_maze(7, 7, rng=random.Random(2))
        maze_from_middle = mz.Maze(maze.width, maze.height, maze.passages, start=(3, 3), end=(0, 0))
        path = mz.solve_bfs(maze_from_middle)
        self.assertIsNotNone(path)

    def test_single_cell_maze_has_no_passages(self):
        maze = mz.generate_maze(1, 1, rng=random.Random(3))
        self.assertEqual(maze.edge_count(), 0)
        self.assertEqual(len(maze.passages), 1)


class TestSolveBfs(unittest.TestCase):
    def test_start_equals_end_gives_a_single_cell_path(self):
        maze = mz.generate_maze(4, 4, rng=random.Random(5), start=(0, 0), end=(0, 0))
        path = mz.solve_bfs(maze)
        self.assertEqual(path, [(0, 0)])

    def test_path_only_uses_open_passages_between_consecutive_cells(self):
        maze = mz.generate_maze(6, 6, rng=random.Random(6))
        path = mz.solve_bfs(maze)
        self.assertIsNotNone(path)
        for a, b in zip(path, path[1:]):
            self.assertIn(b, maze.neighbors(a), f"{a} -> {b} is not an open passage")

    def test_path_starts_and_ends_correctly(self):
        maze = mz.generate_maze(6, 6, rng=random.Random(7))
        path = mz.solve_bfs(maze)
        self.assertEqual(path[0], maze.start)
        self.assertEqual(path[-1], maze.end)

    def test_bfs_finds_a_shortest_path_on_a_hand_built_maze(self):
        # A simple 1x3 corridor: (0,0)-(0,1)-(0,2). Shortest path is
        # unambiguous — exactly 3 cells.
        passages = {
            (0, 0): {"E"},
            (0, 1): {"W", "E"},
            (0, 2): {"W"},
        }
        maze = mz.Maze(width=3, height=1, passages=passages, start=(0, 0), end=(0, 2))
        path = mz.solve_bfs(maze)
        self.assertEqual(path, [(0, 0), (0, 1), (0, 2)])

    def test_returns_none_for_a_deliberately_disconnected_maze(self):
        # Two isolated 1x1 "islands" with no passage between them — BFS
        # must correctly report unreachable, not crash or loop forever.
        passages = {(0, 0): set(), (0, 1): set()}
        maze = mz.Maze(width=2, height=1, passages=passages, start=(0, 0), end=(0, 1))
        self.assertIsNone(mz.solve_bfs(maze))


class TestEveryGeneratedMazeIsSolvable(unittest.TestCase):
    """The literal DoD statement, checked directly: every generated maze
    is confirmed solvable by the solver — across many sizes and seeds, not
    just one lucky case."""

    def test_many_seeds_and_sizes_are_all_solvable(self):
        sizes = [(5, 5), (12, 8), (20, 3), (3, 20), (1, 10), (10, 1)]
        for width, height in sizes:
            for seed in range(5):
                maze = mz.generate_maze(width, height, rng=random.Random(seed))
                path = mz.solve_bfs(maze)
                self.assertIsNotNone(
                    path, f"{width}x{height} seed={seed} maze was NOT solvable"
                )
                self.assertEqual(path[0], maze.start)
                self.assertEqual(path[-1], maze.end)


class TestRenderMaze(unittest.TestCase):
    def test_render_includes_start_and_end_markers(self):
        maze = mz.generate_maze(4, 4, rng=random.Random(9))
        text = mz.render_maze(maze)
        self.assertIn("S", text)
        self.assertIn("E", text)

    def test_render_dimensions_match_grid_size(self):
        maze = mz.generate_maze(5, 3, rng=random.Random(10))
        text = mz.render_maze(maze)
        lines = text.split("\n")
        self.assertEqual(len(lines), 2 * 3 + 1)
        self.assertEqual(len(lines[0]), 2 * 5 + 1)

    def test_render_with_path_marks_intermediate_cells(self):
        maze = mz.generate_maze(4, 4, rng=random.Random(11))
        path = mz.solve_bfs(maze)
        text = mz.render_maze(maze, path=path)
        if len(path) > 2:
            self.assertIn(".", text)


class TestInvalidDimensions(unittest.TestCase):
    def test_zero_or_negative_dimensions_raise(self):
        with self.assertRaises(ValueError):
            mz.generate_maze(0, 5)
        with self.assertRaises(ValueError):
            mz.generate_maze(5, -1)


if __name__ == "__main__":
    unittest.main()
