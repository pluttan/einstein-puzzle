"""Puzzle generation: solution, clue selection, uniqueness verification."""

from __future__ import annotations
import random
from typing import Callable

from .model import Solution, PuzzleSpec
from .clues import Clue, ClueType, ConstraintSet
from .solver import Solver


# ── Solution generation ──────────────────────────────────────────────────────

def generate_solution(n: int, m: int) -> Solution:
    """Generate a random valid solution: m random permutations of [0..n-1]."""
    grid = [random.sample(range(n), n) for _ in range(m)]
    return Solution(n=n, m=m, grid=grid)


# ── Spanning tree ────────────────────────────────────────────────────────────

def random_spanning_tree(m: int) -> list[tuple[int, int]]:
    """Random spanning tree on m nodes via randomized Prim's."""
    in_tree = {0}
    edges: list[tuple[int, int]] = []
    remaining = list(range(1, m))
    random.shuffle(remaining)
    for node in remaining:
        parent = random.choice(list(in_tree))
        edges.append((parent, node))
        in_tree.add(node)
    return edges


# ── Clue factories ──────────────────────────────────────────────────────────

def _make_same(sol: Solution, ca: int, cb: int, pos: int) -> Clue:
    return Clue(ClueType.SAME, ca, sol.value_at(ca, pos), cb, sol.value_at(cb, pos))


def _make_neighbor(sol: Solution, ca: int, cb: int, pos_a: int) -> Clue:
    return Clue(
        ClueType.NEIGHBOR, ca, sol.value_at(ca, pos_a),
        cb, sol.value_at(cb, pos_a + 1),
    )


def _make_leftof(sol: Solution, ca: int, cb: int, pos_a: int) -> Clue:
    return Clue(
        ClueType.LEFT_OF, ca, sol.value_at(ca, pos_a),
        cb, sol.value_at(cb, pos_a + 1),
    )


def _make_position(sol: Solution, cat: int, pos: int) -> Clue:
    return Clue(ClueType.POSITION, cat, sol.value_at(cat, pos), position=pos)


# ── Verification helpers ────────────────────────────────────────────────────

def _count_solutions(clues: list[Clue], n: int, m: int, limit: int = 2) -> int:
    cs = ConstraintSet(n=n, clues=list(clues))
    cs.build_watchers()
    return Solver(n, m, cs).count_solutions(limit=limit)


# ── Main generation pipeline ────────────────────────────────────────────────

def generate_puzzle(
    sol: Solution,
    spec: PuzzleSpec,
    difficulty: str = "medium",
    progress: Callable[[str], None] | None = None,
) -> list[Clue]:
    """Generate clues for the given solution ensuring unique solvability."""
    n, m = sol.n, sol.m

    def log(msg: str) -> None:
        if progress:
            progress(msg)

    if n > 10:
        return _generate_large(sol, n, m, difficulty, log)
    return _generate_small(sol, spec, n, m, difficulty, log)


# ── Large puzzle generation (N > 20) ────────────────────────────────────────
# Uses star topology: anchor category 0 with POSITION clues,
# all other categories linked to it via SAME clues.
# No minimization (too expensive).

def _generate_large(
    sol: Solution, n: int, m: int, difficulty: str,
    log: Callable[[str], None],
) -> list[Clue]:
    log("Large puzzle mode: star topology...")
    clues: list[Clue] = []

    # Anchor category 0 with N-1 position clues
    anchor_cat = 0
    positions = list(range(n))
    random.shuffle(positions)
    anchor_count = n - 1 if difficulty != "easy" else n
    for pos in positions[:anchor_count]:
        clues.append(_make_position(sol, anchor_cat, pos))

    # Link each other category to anchor via SAME clues
    clues_per_link = n - 1 if difficulty != "easy" else n
    if difficulty == "hard":
        clues_per_link = max(1, n - 2)

    for cat in range(1, m):
        positions = list(range(n))
        random.shuffle(positions)
        for pos in positions[:clues_per_link]:
            clues.append(_make_same(sol, anchor_cat, cat, pos))

    # Verify
    log("Verifying uniqueness...")
    count = _count_solutions(clues, n, m)

    if count == 1:
        log(f"Done! {len(clues)} clues generated.")
        return clues

    # If not unique, fill remaining SAME clues
    if count != 1:
        log(f"Not unique ({count}), filling remaining clues...")
        existing = set(clues)
        for cat in range(1, m):
            for pos in range(n):
                c = _make_same(sol, anchor_cat, cat, pos)
                if c not in existing:
                    clues.append(c)
                    existing.add(c)
        # Also fill remaining position clues
        for pos in range(n):
            c = _make_position(sol, anchor_cat, pos)
            if c not in existing:
                clues.append(c)
                existing.add(c)

    log(f"Done! {len(clues)} clues generated.")
    return clues


# ── Small puzzle generation (N <= 20) ───────────────────────────────────────
# Uses spanning tree, variety clues, and minimization.

def _generate_small(
    sol: Solution, spec: PuzzleSpec, n: int, m: int, difficulty: str,
    log: Callable[[str], None],
) -> list[Clue]:
    log("Building spanning tree...")
    tree_edges = random_spanning_tree(m)
    tree_edge_set = set(tree_edges) | {(b, a) for a, b in tree_edges}

    clues_per_edge = n - 1
    if difficulty == "easy":
        clues_per_edge = n
    elif difficulty == "hard":
        clues_per_edge = max(1, n - 2)

    clues: list[Clue] = []

    # SAME clues along spanning tree
    log("Generating SAME clues along spanning tree...")
    for ca, cb in tree_edges:
        positions = list(range(n))
        random.shuffle(positions)
        for p in positions[:clues_per_edge]:
            clues.append(_make_same(sol, ca, cb, p))

    # Positional anchors
    log("Adding positional anchors...")
    anchor_positions = random.sample(range(n), min(2, n))
    anchor_cats = random.sample(range(m), min(2, m))
    for i, pos in enumerate(anchor_positions):
        clues.append(_make_position(sol, anchor_cats[i % len(anchor_cats)], pos))

    # Variety: replace some SAME clues with NEIGHBOR/LEFT_OF
    if n >= 3:
        log("Adding variety clues...")
        clues = _add_variety(sol, clues, n)

    # Verify and fix
    log("Verifying uniqueness...")
    count = _count_solutions(clues, n, m)
    if count == 0:
        raise RuntimeError("Clues inconsistent with solution")

    if count != 1:
        # Add extra clues in larger batches
        batch = max(3, n // 2)
        attempt = 0
        while count != 1 and attempt < n * m:
            log(f"Not unique yet ({count}), adding extra clues...")
            clues = _add_extras(sol, clues, tree_edge_set, n, m, batch)
            count = _count_solutions(clues, n, m)
            attempt += 1

    if count != 1:
        log("Fallback: filling all spanning tree clues...")
        existing = set(clues)
        for ca, cb in tree_edges:
            for pos in range(n):
                c = _make_same(sol, ca, cb, pos)
                if c not in existing:
                    clues.append(c)
                    existing.add(c)
        count = _count_solutions(clues, n, m)
        if count != 1:
            raise RuntimeError(f"Could not achieve unique solution (got {count})")

    # Minimize only for very small puzzles (expensive operation)
    if n <= 8:
        log("Minimizing clue set...")
        clues = _minimize(clues, n, m)

    log(f"Done! {len(clues)} clues generated.")
    return clues


# ── Variety clue conversion ─────────────────────────────────────────────────

def _add_variety(sol: Solution, clues: list[Clue], n: int) -> list[Clue]:
    """Replace some SAME clues with NEIGHBOR or LEFT_OF."""
    same_indices = [
        i for i, c in enumerate(clues) if c.clue_type == ClueType.SAME
    ]
    if len(same_indices) < 4:
        return clues

    convert_count = max(1, len(same_indices) // 3)
    random.shuffle(same_indices)

    converted = 0
    for idx in same_indices:
        if converted >= convert_count:
            break
        old = clues[idx]
        pos = sol.position_of(old.cat_a, old.val_a)

        if pos < n - 1:
            if random.random() < 0.5:
                clues[idx] = _make_neighbor(sol, old.cat_a, old.cat_b, pos)
            else:
                clues[idx] = _make_leftof(sol, old.cat_a, old.cat_b, pos)
            converted += 1
        elif pos > 0:
            if random.random() < 0.5:
                clues[idx] = _make_neighbor(sol, old.cat_b, old.cat_a, pos - 1)
            else:
                clues[idx] = _make_leftof(sol, old.cat_b, old.cat_a, pos - 1)
            converted += 1

    return clues


# ── Extra clue insertion ─────────────────────────────────────────────────────

def _add_extras(
    sol: Solution, clues: list[Clue],
    tree_edge_set: set[tuple[int, int]], n: int, m: int,
    batch: int = 3,
) -> list[Clue]:
    """Add cross-link and position clues in batches."""
    existing = set(clues)
    added = 0

    pairs = [
        (i, j) for i in range(m) for j in range(i + 1, m)
        if (i, j) not in tree_edge_set
    ]
    random.shuffle(pairs)

    for ca, cb in pairs:
        pos = random.randint(0, n - 1)
        c = _make_same(sol, ca, cb, pos)
        if c not in existing:
            clues.append(c)
            existing.add(c)
            added += 1
            if added >= batch:
                break

    if added == 0:
        for _ in range(batch):
            pos = random.randint(0, n - 1)
            cat = random.randint(0, m - 1)
            c = _make_position(sol, cat, pos)
            if c not in existing:
                clues.append(c)
                existing.add(c)
    return clues


# ── Clue minimization ───────────────────────────────────────────────────────

def _minimize(clues: list[Clue], n: int, m: int) -> list[Clue]:
    """Remove redundant clues one at a time."""
    result = list(clues)
    order = list(range(len(result)))
    random.shuffle(order)

    i = 0
    while i < len(order):
        idx = order[i]
        if idx >= len(result):
            i += 1
            continue
        candidate = result[:idx] + result[idx + 1:]
        if _count_solutions(candidate, n, m) == 1:
            result = candidate
            order = [x if x < idx else x - 1 for x in order if x != idx]
        else:
            i += 1

    return result
