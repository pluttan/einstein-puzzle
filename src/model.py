"""Core data structures and bitmask utilities for the puzzle engine."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator


# ── Bitmask utilities ────────────────────────────────────────────────────────

def popcount(x: int) -> int:
    """Count set bits in a bitmask."""
    return x.bit_count()


def lowest_bit_pos(x: int) -> int:
    """Return index of the lowest set bit. Undefined for x == 0."""
    return (x & -x).bit_length() - 1


def iter_bits(x: int) -> Iterator[int]:
    """Yield indices of all set bits, lowest first."""
    while x:
        b = x & -x
        yield b.bit_length() - 1
        x ^= b


def single_bit(x: int) -> int | None:
    """If exactly one bit is set, return its index. Otherwise None."""
    if x and (x & (x - 1)) == 0:
        return x.bit_length() - 1
    return None


# ── Data types ───────────────────────────────────────────────────────────────

@dataclass
class PuzzleSpec:
    """Puzzle dimensions and category/value names."""
    n: int                        # number of houses (positions)
    m: int                        # number of categories
    category_names: list[str]     # length m
    value_names: list[list[str]]  # value_names[cat][val], each list length n


@dataclass
class Solution:
    """A complete puzzle assignment. grid[cat][pos] = value_id."""
    n: int
    m: int
    grid: list[list[int]]

    def position_of(self, cat: int, val: int) -> int:
        """Find position of value val in category cat."""
        return self.grid[cat].index(val)

    def value_at(self, cat: int, pos: int) -> int:
        """Get value at position pos in category cat."""
        return self.grid[cat][pos]

    def verify(self) -> bool:
        """Check that each category is a valid permutation of [0..n-1]."""
        for cat in range(self.m):
            if sorted(self.grid[cat]) != list(range(self.n)):
                return False
        return True
