"""Output formatting: human-readable text (Russian) and JSON."""

from __future__ import annotations
import json

from .model import PuzzleSpec, Solution
from .clues import Clue, ClueType


# ── Clue text templates ──────────────────────────────────────────────────────

def _val_name(spec: PuzzleSpec, cat: int, val: int) -> str:
    return spec.value_names[cat][val]


def _cat_name(spec: PuzzleSpec, cat: int) -> str:
    return spec.category_names[cat]


def clue_to_text(clue: Clue, spec: PuzzleSpec) -> str:
    """Convert a clue to a human-readable Russian text string."""
    a = _val_name(spec, clue.cat_a, clue.val_a)

    if clue.clue_type == ClueType.SAME:
        b = _val_name(spec, clue.cat_b, clue.val_b)
        return f"{a} и {b} — в одном доме."

    if clue.clue_type == ClueType.NEIGHBOR:
        b = _val_name(spec, clue.cat_b, clue.val_b)
        return f"{a} живёт рядом с {b}."

    if clue.clue_type == ClueType.LEFT_OF:
        b = _val_name(spec, clue.cat_b, clue.val_b)
        return f"{a} — непосредственно слева от {b}."

    if clue.clue_type == ClueType.POSITION:
        return f"{a} — в доме {clue.position + 1}."

    if clue.clue_type == ClueType.NOT_SAME:
        b = _val_name(spec, clue.cat_b, clue.val_b)
        return f"{a} и {b} — НЕ в одном доме."

    return str(clue)


# ── Text output ──────────────────────────────────────────────────────────────

def format_text(
    spec: PuzzleSpec,
    clues: list[Clue],
    solution: Solution | None = None,
) -> str:
    """Format the puzzle as human-readable Russian text."""
    lines: list[str] = []

    lines.append(f"=== Головоломка Эйнштейна ({spec.n}x{spec.m}) ===")
    lines.append("")
    lines.append(
        f"{spec.n} человек живут в {spec.n} домах, выстроенных в ряд."
    )
    lines.append("")

    # List categories and their values
    lines.append("Категории:")
    for i in range(spec.m):
        vals = ", ".join(spec.value_names[i])
        lines.append(f"  {spec.category_names[i]}: {vals}")
    lines.append("")

    # Clues
    lines.append("Подсказки:")
    for i, clue in enumerate(clues, 1):
        lines.append(f"  {i}. {clue_to_text(clue, spec)}")
    lines.append("")
    lines.append(f"Всего подсказок: {len(clues)}")

    # Solution (if provided)
    if solution is not None:
        lines.append("")
        lines.append("=== Решение ===")
        lines.append("")

        # Header
        header = "Дом".ljust(6)
        for pos in range(spec.n):
            header += f"  {pos + 1}".ljust(16)
        lines.append(header)
        lines.append("-" * len(header))

        # Each category row
        for cat in range(spec.m):
            row = _cat_name(spec, cat).ljust(6)[:6]
            for pos in range(spec.n):
                val = solution.value_at(cat, pos)
                name = _val_name(spec, cat, val)
                row += f"  {name}".ljust(16)
            lines.append(row)

    return "\n".join(lines)


# ── JSON output ──────────────────────────────────────────────────────────────

def _clue_to_dict(clue: Clue, spec: PuzzleSpec) -> dict:
    """Convert a clue to a JSON-serializable dict."""
    d: dict = {
        "type": clue.clue_type.name.lower(),
        "category_a": _cat_name(spec, clue.cat_a),
        "value_a": _val_name(spec, clue.cat_a, clue.val_a),
        "text": clue_to_text(clue, spec),
    }
    if clue.clue_type != ClueType.POSITION:
        d["category_b"] = _cat_name(spec, clue.cat_b)
        d["value_b"] = _val_name(spec, clue.cat_b, clue.val_b)
    if clue.clue_type == ClueType.POSITION:
        d["position"] = clue.position + 1
    return d


def format_json(
    spec: PuzzleSpec,
    clues: list[Clue],
    solution: Solution | None = None,
) -> str:
    """Format the puzzle as a JSON string."""
    data: dict = {
        "size": {"houses": spec.n, "categories": spec.m},
        "categories": [
            {
                "name": spec.category_names[i],
                "values": spec.value_names[i],
            }
            for i in range(spec.m)
        ],
        "clues": [_clue_to_dict(c, spec) for c in clues],
        "clue_count": len(clues),
    }

    if solution is not None:
        grid: dict[str, list[str]] = {}
        for cat in range(spec.m):
            cat_name = _cat_name(spec, cat)
            grid[cat_name] = [
                _val_name(spec, cat, solution.value_at(cat, pos))
                for pos in range(spec.n)
            ]
        data["solution"] = grid

    return json.dumps(data, ensure_ascii=False, indent=2)
