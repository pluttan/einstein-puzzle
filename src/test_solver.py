"""Tests for the puzzle generator: solver, generator, round-trip."""

from __future__ import annotations
import random
import time
import sys

from .model import Solution
from .clues import Clue, ClueType, ConstraintSet
from .solver import Solver
from .generator import generate_solution, generate_puzzle, _count_solutions
from .vocabulary import build_vocabulary


def test_solver_basic():
    """Test solver on a trivial 3x2 puzzle."""
    n, m = 3, 2
    clues = [
        Clue(ClueType.POSITION, 0, 0, position=0),
        Clue(ClueType.POSITION, 0, 1, position=1),
        Clue(ClueType.POSITION, 0, 2, position=2),
        Clue(ClueType.SAME, 0, 0, 1, 2),
        Clue(ClueType.SAME, 0, 1, 1, 0),
    ]
    cs = ConstraintSet(n=n, clues=clues)
    cs.build_watchers()
    solver = Solver(n, m, cs)
    assert solver.count_solutions(limit=2) == 1, "Should have exactly 1 solution"
    grid = solver.solve_one()
    assert grid is not None
    assert grid[0] == [0, 1, 2]
    assert grid[1] == [2, 0, 1]
    print("  PASS: test_solver_basic")


def test_solver_neighbor():
    """Test NEIGHBOR constraint."""
    n, m = 3, 2
    clues = [
        Clue(ClueType.POSITION, 0, 0, position=0),
        Clue(ClueType.POSITION, 0, 1, position=1),
        Clue(ClueType.POSITION, 0, 2, position=2),
        Clue(ClueType.NEIGHBOR, 0, 0, 1, 1),  # val0 next to val1 in cat1
        Clue(ClueType.SAME, 0, 2, 1, 2),       # val2 same pos in both cats
    ]
    cs = ConstraintSet(n=n, clues=clues)
    cs.build_watchers()
    solver = Solver(n, m, cs)
    count = solver.count_solutions(limit=5)
    assert count >= 1, "Should have at least 1 solution"
    print(f"  PASS: test_solver_neighbor (solutions={count})")


def test_solver_leftof():
    """Test LEFT_OF constraint."""
    n, m = 3, 1
    clues = [
        Clue(ClueType.LEFT_OF, 0, 0, 0, 1),  # val0 directly left of val1
    ]
    cs = ConstraintSet(n=n, clues=clues)
    cs.build_watchers()
    solver = Solver(n, m, cs)
    count = solver.count_solutions(limit=10)
    # val0 at pos 0 -> val1 at pos 1 -> val2 at pos 2 (1 solution)
    # val0 at pos 1 -> val1 at pos 2 -> val2 at pos 0 (1 solution)
    assert count == 2, f"Expected 2 solutions, got {count}"
    print("  PASS: test_solver_leftof")


def test_roundtrip():
    """Generate solution -> generate clues -> solve -> verify match."""
    for n in [3, 5, 8, 10]:
        random.seed(42 + n)
        m = n
        spec = build_vocabulary(n, m)
        sol = generate_solution(n, m)
        clues = generate_puzzle(sol, spec, progress=lambda x: None)

        # Verify uniqueness
        count = _count_solutions(clues, n, m, limit=2)
        assert count == 1, f"n={n}: Expected 1 solution, got {count}"

        # Solve and verify match
        cs = ConstraintSet(n=n, clues=clues)
        cs.build_watchers()
        solver = Solver(n, m, cs)
        grid = solver.solve_one()
        assert grid is not None, f"n={n}: Solver returned no solution"
        assert grid == sol.grid, f"n={n}: Solved grid doesn't match original"

        print(f"  PASS: test_roundtrip n={n} ({len(clues)} clues)")


def test_scaling():
    """Test generation performance at various scales."""
    sizes = [20, 50, 100]
    for n in sizes:
        random.seed(42)
        m = n
        spec = build_vocabulary(n, m)
        sol = generate_solution(n, m)

        t0 = time.time()
        clues = generate_puzzle(sol, spec, progress=lambda x: None)
        gen_time = time.time() - t0

        t0 = time.time()
        count = _count_solutions(clues, n, m, limit=2)
        verify_time = time.time() - t0

        assert count == 1, f"n={n}: Expected 1 solution, got {count}"
        assert gen_time < 10.0, f"n={n}: Generation took {gen_time:.1f}s (limit 10s)"
        assert verify_time < 10.0, f"n={n}: Verification took {verify_time:.1f}s (limit 10s)"

        print(
            f"  PASS: test_scaling n={n} "
            f"({len(clues)} clues, gen={gen_time:.3f}s, verify={verify_time:.3f}s)"
        )


def main():
    print("Running tests...")
    tests = [
        test_solver_basic,
        test_solver_neighbor,
        test_solver_leftof,
        test_roundtrip,
        test_scaling,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test.__name__}: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
