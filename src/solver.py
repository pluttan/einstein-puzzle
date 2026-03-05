"""CSP solver with bitmask domains, constraint propagation, and backtracking.

Optimized for large puzzles (up to 100x100):
- Python int bitmask domains (arbitrary precision)
- Hybrid propagation: initial clue pass + queue-based cascade
- Fast AllDifferent with assigned-mask tracking
"""

from __future__ import annotations
from collections import deque

from .model import iter_bits, single_bit
from .clues import Clue, ClueType, ConstraintSet


class Solver:
    """Constraint-satisfaction solver for Einstein-style puzzles."""

    def __init__(self, n: int, m: int, constraints: ConstraintSet):
        self.n = n
        self.m = m
        self.constraints = constraints
        self.full_mask = (1 << n) - 1

    # ── Public API ───────────────────────────────────────────────────────

    def make_initial_domains(self) -> list[list[int]]:
        return [[self.full_mask] * self.n for _ in range(self.m)]

    def count_solutions(self, limit: int = 2) -> int:
        domains = self.make_initial_domains()
        return self._count(domains, limit)

    def solve_one(self) -> list[list[int]] | None:
        domains = self.make_initial_domains()
        if self._solve_first(domains):
            return self._extract_grid(domains)
        return None

    # ── Core solving ─────────────────────────────────────────────────────

    def _count(self, domains: list[list[int]], limit: int) -> int:
        if not self._propagate(domains):
            return 0
        if self._is_solved(domains):
            return 1
        bv = self._pick_branch_var(domains)
        if bv is None:
            return 0
        cat, val = bv
        total = 0
        for pos in iter_bits(domains[cat][val]):
            clone = _clone(domains)
            clone[cat][val] = 1 << pos
            total += self._count(clone, limit - total)
            if total >= limit:
                break
        return total

    def _solve_first(self, domains: list[list[int]]) -> bool:
        if not self._propagate(domains):
            return False
        if self._is_solved(domains):
            return True
        bv = self._pick_branch_var(domains)
        if bv is None:
            return False
        cat, val = bv
        for pos in iter_bits(domains[cat][val]):
            clone = _clone(domains)
            clone[cat][val] = 1 << pos
            if self._solve_first(clone):
                for c in range(self.m):
                    domains[c][:] = clone[c]
                return True
        return False

    # ── Hybrid propagation ───────────────────────────────────────────────
    # Phase 1: Apply all clues once, collect dirty vars.
    # Phase 2: AllDifferent for all dirty categories.
    # Phase 3: Queue-based cascade for remaining changes.

    def _propagate(self, domains: list[list[int]]) -> bool:
        watchers = self.constraints.watchers
        clues = self.constraints.clues
        m, n = self.m, self.n

        # Phase 1: apply every clue once
        dirty: set[tuple[int, int]] = set()
        for clue in clues:
            result = _apply(domains, clue, self.full_mask)
            if result is None:
                return False
            dirty.update(result)

        # Phase 2: AllDifferent for dirty categories
        dirty_cats = {c for c, _ in dirty}
        for cat in dirty_cats:
            result = _alldiff(domains, cat, n)
            if result is None:
                return False
            dirty.update(result)

        # Phase 3: queue-based propagation for cascading changes
        queue: deque[tuple[int, int]] = deque(dirty)
        in_queue = set(dirty)
        alldiff_pending: set[int] = set()

        while queue:
            c, v = queue.popleft()
            in_queue.discard((c, v))

            if domains[c][v] == 0:
                return False

            # Re-apply watched clues
            for ci in watchers.get((c, v), ()):
                result = _apply(domains, clues[ci], self.full_mask)
                if result is None:
                    return False
                for key in result:
                    alldiff_pending.add(key[0])
                    if key not in in_queue:
                        queue.append(key)
                        in_queue.add(key)

            alldiff_pending.add(c)

            # Batch AllDifferent when queue drains for one "wave"
            if not queue and alldiff_pending:
                for cat in alldiff_pending:
                    result = _alldiff(domains, cat, n)
                    if result is None:
                        return False
                    for key in result:
                        if key not in in_queue:
                            queue.append(key)
                            in_queue.add(key)
                alldiff_pending.clear()

        return True

    # ── Helpers ──────────────────────────────────────────────────────────

    def _is_solved(self, domains: list[list[int]]) -> bool:
        for c in range(self.m):
            for v in range(self.n):
                d = domains[c][v]
                if d == 0 or d & (d - 1) != 0:
                    return False
        return True

    def _pick_branch_var(self, domains: list[list[int]]) -> tuple[int, int] | None:
        best_c, best_v, best_s = -1, -1, self.n + 1
        for c in range(self.m):
            for v in range(self.n):
                d = domains[c][v]
                if d & (d - 1) != 0:
                    s = d.bit_count()
                    if s < best_s:
                        best_c, best_v, best_s = c, v, s
        if best_c == -1:
            return None
        return best_c, best_v

    def _extract_grid(self, domains: list[list[int]]) -> list[list[int]]:
        grid: list[list[int]] = [[0] * self.n for _ in range(self.m)]
        for c in range(self.m):
            for v in range(self.n):
                pos = single_bit(domains[c][v])
                if pos is not None:
                    grid[c][pos] = v
        return grid


# ── Module-level functions (avoid method call overhead) ──────────────────

def _clone(domains: list[list[int]]) -> list[list[int]]:
    return [row[:] for row in domains]


def _apply(
    domains: list[list[int]], clue: Clue, full_mask: int
) -> list[tuple[int, int]] | None:
    """Apply one clue. Returns list of changed (cat, val) or None on contradiction."""
    ct = clue.clue_type
    ca, va, cb, vb = clue.cat_a, clue.val_a, clue.cat_b, clue.val_b
    changed: list[tuple[int, int]] = []

    if ct == ClueType.SAME:
        da = domains[ca][va]
        db = domains[cb][vb]
        new = da & db
        if new == 0:
            return None
        if new != da:
            domains[ca][va] = new
            changed.append((ca, va))
        if new != db:
            domains[cb][vb] = new
            changed.append((cb, vb))

    elif ct == ClueType.NEIGHBOR:
        da = domains[ca][va]
        db = domains[cb][vb]
        nb = ((db << 1) | (db >> 1)) & full_mask
        na = ((da << 1) | (da >> 1)) & full_mask
        new_a = da & nb
        new_b = db & na
        if new_a == 0 or new_b == 0:
            return None
        if new_a != da:
            domains[ca][va] = new_a
            changed.append((ca, va))
        if new_b != db:
            domains[cb][vb] = new_b
            changed.append((cb, vb))

    elif ct == ClueType.LEFT_OF:
        da = domains[ca][va]
        db = domains[cb][vb]
        new_a = da & (db >> 1)
        new_b = db & (da << 1)
        if new_a == 0 or new_b == 0:
            return None
        if new_a != da:
            domains[ca][va] = new_a
            changed.append((ca, va))
        if new_b != db:
            domains[cb][vb] = new_b
            changed.append((cb, vb))

    elif ct == ClueType.POSITION:
        bit = 1 << clue.position
        old = domains[ca][va]
        new = old & bit
        if new == 0:
            return None
        if new != old:
            domains[ca][va] = new
            changed.append((ca, va))

    elif ct == ClueType.NOT_SAME:
        da = domains[ca][va]
        db = domains[cb][vb]
        if da & (da - 1) == 0 and da:
            new_b = db & ~da
            if new_b == 0:
                return None
            if new_b != db:
                domains[cb][vb] = new_b
                changed.append((cb, vb))
                db = new_b
        if db & (db - 1) == 0 and db:
            new_a = da & ~db
            if new_a == 0:
                return None
            if new_a != da:
                domains[ca][va] = new_a
                changed.append((ca, va))

    return changed


def _alldiff(
    domains: list[list[int]], cat: int, n: int
) -> list[tuple[int, int]] | None:
    """AllDifferent propagation: naked singles + hidden singles.
    Returns changed vars or None on contradiction."""
    row = domains[cat]
    changed: list[tuple[int, int]] = []

    # Build mask of positions taken by assigned (single-bit) values
    assigned = 0
    for v in range(n):
        d = row[v]
        if d == 0:
            return None
        if d & (d - 1) == 0:
            assigned |= d

    # Naked singles: strip assigned positions from unassigned values
    if assigned:
        inv = ~assigned
        for v in range(n):
            d = row[v]
            if d & (d - 1) == 0:
                continue
            new = d & inv
            if new == 0:
                return None
            if new != d:
                row[v] = new
                changed.append((cat, v))
                if new & (new - 1) == 0:
                    assigned |= new
                    inv = ~assigned

    # Hidden singles: position in only one value's domain -> assign
    for pos in range(n):
        bit = 1 << pos
        if assigned & bit:
            continue
        count = 0
        last_v = -1
        for v in range(n):
            if row[v] & bit:
                count += 1
                last_v = v
                if count > 1:
                    break
        if count == 0:
            return None
        if count == 1:
            row[last_v] = bit
            changed.append((cat, last_v))

    return changed
