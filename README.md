<div align="center">

# einstein_puzzle

**Procedural Einstein puzzle generator up to 100x100**

</div>

Generates Einstein's Riddle (Zebra Puzzle) style logic puzzles of arbitrary size -- from the classic 5x5 up to 100x100 and beyond. Every generated puzzle is guaranteed to have a unique solution, verified by a built-in CSP solver with bitmask-based constraint propagation and backtracking. No external dependencies.

## ■ Features

- ❖ **Arbitrary size** — NxM puzzles (N houses, M categories) from 2x2 up to 200x200
- ❖ **Multiple clue types** — same house, neighbor, left-of, absolute position
- ❖ **Guaranteed unique solution** — CSP solver verifies exactly one valid assignment
- ❖ **Bitmask solver** — constraint propagation with bitmask domains for performance at scale
- ❖ **Adaptive generation** — spanning-tree + minimization for small N, star topology for N > 10
- ❖ **Difficulty levels** — easy (more clues), medium, hard (minimal clue set)
- ❖ **Dual output** — human-readable text (Russian) for N ≤ 15, JSON for larger puzzles
- ❖ **Reproducible** — seed parameter for deterministic generation
- ❖ **Zero dependencies** — pure Python, no pip install required

## ■ Stack

<div align="center">

| Component | Technology |
|-----------|------------|
| Language | Python 3.12 |
| Solver | CSP (constraint propagation + backtracking) |
| Domains | Bitmask representation |
| Output | Text (Russian), JSON |

</div>

## ■ How It Works

```
1. User specifies puzzle size (N houses, M categories), difficulty, and optional seed.
2. Generator builds a clue graph — spanning-tree topology for N ≤ 10, star topology for N > 10.
3. Clue set is minimized according to difficulty level (easy keeps more clues, hard trims to minimal).
4. Built-in CSP solver propagates constraints using bitmask domains and backtracks to confirm exactly one valid solution.
5. Puzzle is rendered as human-readable text (Russian) for N ≤ 15, or as JSON for larger sizes.
```

## ■ Screenshots

<div align="center">

![Screenshot](screenshots/main.png)

*Main puzzle output — generated 5x5 Einstein puzzle in text format*

</div>

## ■ Usage

```bash
make install      # create venv (no dependencies needed)
make run          # generate default 5x5 puzzle
make test         # run solver / generator test suite

# Custom sizes
python3.12 -m src.main -n 5                          # classic 5x5
python3.12 -m src.main -n 10 --seed 42               # 10x10 with seed
python3.12 -m src.main -n 100 --format json          # 100x100 (JSON)
python3.12 -m src.main -n 5 --difficulty easy        # more clues
python3.12 -m src.main -n 8 -m 5                      # 8 houses, 5 categories
python3.12 -m src.main -n 5 --format both -o out.txt  # text + JSON to file
```

## ■ Project Structure

```
src/
├── main.py         — CLI entry point
├── model.py        — core data structures + bitmask utilities
├── clues.py        — clue types and constraint index
├── solver.py       — CSP solver (bitmask domains, propagation, backtracking)
├── generator.py    — puzzle generation (spanning tree / star topology)
├── vocabulary.py   — themed word lists and name generation
├── formatter.py    — text (Russian) and JSON output
├── test_solver.py  — solver / generator / round-trip tests
└── __init__.py
```

## ■ License

MIT © [pluttan](https://github.com/pluttan)
