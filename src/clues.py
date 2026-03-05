"""Clue type definitions and constraint indexing."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto


class ClueType(Enum):
    SAME = auto()       # A and B are in the same house
    NEIGHBOR = auto()   # A and B are in adjacent houses
    LEFT_OF = auto()    # A is directly to the left of B
    POSITION = auto()   # A is at a specific position
    NOT_SAME = auto()   # A and B are NOT in the same house


@dataclass(frozen=True)
class Clue:
    """A single puzzle clue (hint)."""
    clue_type: ClueType
    cat_a: int
    val_a: int
    cat_b: int = -1         # unused for POSITION
    val_b: int = -1         # unused for POSITION
    position: int = -1      # only for POSITION

    def participants(self) -> list[tuple[int, int]]:
        """Return list of (category, value) pairs involved in this clue."""
        result = [(self.cat_a, self.val_a)]
        if self.clue_type != ClueType.POSITION:
            result.append((self.cat_b, self.val_b))
        return result


@dataclass
class ConstraintSet:
    """Collection of clues with watcher index for efficient propagation."""
    n: int
    clues: list[Clue] = field(default_factory=list)
    # watchers[(cat, val)] -> list of clue indices that reference this (cat, val)
    watchers: dict[tuple[int, int], list[int]] = field(default_factory=dict)

    def build_watchers(self) -> None:
        """Build the watcher index from the current clue list."""
        self.watchers.clear()
        for idx, clue in enumerate(self.clues):
            for cat, val in clue.participants():
                key = (cat, val)
                if key not in self.watchers:
                    self.watchers[key] = []
                self.watchers[key].append(idx)

    def add_clue(self, clue: Clue) -> None:
        """Add a clue and update the watcher index."""
        idx = len(self.clues)
        self.clues.append(clue)
        for cat, val in clue.participants():
            key = (cat, val)
            if key not in self.watchers:
                self.watchers[key] = []
            self.watchers[key].append(idx)
