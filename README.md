# Maze Generator + Solver

Generates random mazes with a randomized depth-first "recursive
backtracker" carve, solves them with BFS for the shortest path, and
renders both as ASCII art.

Real output — a generated 15x10 maze, then the same maze solved:

```
Generated 15x10 maze (149 passages):
###############################
#S#   #   #             #     #
# # # # # # ### ####### # ### #
# # # # # # # # #     # #   # #
# # # # # # # # ### ### ##### #
#   #   # #   #   #     #     #
######### # ##### ### ### ### #
#     #   # #   #   #   # #   #
# ##### ##### # ### ### # # ###
#       #     #     # #   # # #
# ####### ########### ##### # #
# #       #         #     # # #
# ##### # # ####### # # ### # #
#     # #       #   # # #   # #
##### # ######### ### # # ### #
#   # # #   #     #   # # #   #
# # # ### # # ##### ##### # # #
# # # #   #   #   #     # # # #
# ### # ####### ### ### # # # #
#       #             #     #E#
###############################

Solved — shortest path is 91 steps:
###############################
#S#. .#. .#    . . . . .#     #
# # # # # # ### ####### # ### #
#.#.#.#.#.# # #.#     #.#   # #
...
#    . .#             #  . .#E#
###############################
```

(full output truncated here for length — see the repo for the complete
solved render)

## Features

- **Generation**: randomized depth-first backtracker — carves passages by
  repeatedly stepping to a random unvisited neighbor and backing up on dead
  ends. This always produces a *perfect maze*: a spanning tree over every
  cell, so there's exactly one path between any two cells and every cell is
  reachable. Solvability is a structural guarantee of how the maze is
  built, not something hoped for and checked afterward
- **Solving**: BFS finds the guaranteed-shortest path from start to end,
  and works correctly on *any* maze handed to it — including a
  deliberately disconnected one, where it correctly reports "no path"
  instead of crashing or looping
- ASCII rendering marks the start (`S`), end (`E`), and — when a solved
  path is given — every intermediate cell on the shortest route (`.`)

## Tech Stack

Python 3, standard library only

## Getting Started

```bash
git clone https://github.com/Kazenubis/maze-generator-solver.git
cd maze-generator-solver
python3 maze.py --width 15 --height 10 --seed 42
```

Run the tests:

```bash
python3 -m unittest test_maze.py -v
```

## What I Learned

The strongest test here isn't "solve one maze and check it worked" — it's
a structural check on the *generator*: a perfect maze over `width * height`
cells must have exactly `width * height - 1` passages (a spanning tree —
every cell connected, zero cycles). `test_edge_count_is_exactly_a_spanning_tree`
checks that directly across several grid shapes, including degenerate ones
(1x1, a 1-wide corridor). That single structural property is *why*
"every generated maze is solvable" — it's not a coincidence the generator
happens to produce solvable output, it's mathematically guaranteed by
carving a spanning tree, and the edge-count test is what actually proves
the carve is doing that correctly rather than leaving stray disconnected
pockets or accidental cycles.

Testing the solver itself needed the opposite kind of case: a maze that's
*not* a spanning tree, built by hand with two isolated 1x1 islands and no
passage between them, to confirm BFS correctly returns "no path" instead
of assuming every maze it's ever handed must be solvable just because the
generator's mazes always are.
