# Einstein Puzzle Generator

Generates Einstein's Riddle (Zebra Puzzle) style logic puzzles of arbitrary size — from classic 5x5 up to 100x100.

## Features

- Arbitrary puzzle size (NxN, up to 100x100)
- Multiple clue types: same house, neighbor, left-of, position
- Guaranteed unique solution (verified by CSP solver)
- Bitmask-based solver for performance at scale
- Human-readable output (Russian) for small puzzles
- JSON output for any size
- Reproducible generation via seed

## Quick Start

```bash
make install
make all
```

## Usage

```bash
# Classic 5x5 puzzle
python3.12 -m src.main -n 5

# 10x10 puzzle with seed
python3.12 -m src.main -n 10 --seed 42

# Large 100x100 puzzle (JSON only)
python3.12 -m src.main -n 100 --format json

# Custom categories count
python3.12 -m src.main -n 8 -m 5

# Easy difficulty (more clues)
python3.12 -m src.main -n 5 --difficulty easy
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `-n N` | Number of houses / values per category | 5 |
| `-m M` | Number of categories | same as N |
| `--difficulty` | easy / medium / hard | medium |
| `--format` | text, json, both | auto |
| `--seed` | Random seed for reproducibility | random |
| `--no-solution` | Hide solution from output | false |

## How It Works

1. Generate a random valid solution (N permutations)
2. Build a spanning tree linking categories
3. Select clues from the solution ensuring unique solvability
4. Verify uniqueness with a CSP solver (constraint propagation + backtracking)
5. Optionally minimize clue set (for small puzzles)

## Project Structure

```
src/
├── main.py        — CLI entry point
├── model.py       — Core data structures
├── clues.py       — Clue type definitions
├── solver.py      — CSP solver (bitmask domains)
├── generator.py   — Puzzle generation logic
├── vocabulary.py  — Word lists and name generation
└── formatter.py   — Output formatting
```
