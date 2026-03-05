"""CLI entry point for Einstein puzzle generator."""

from __future__ import annotations
import argparse
import random
import sys
import time

from .model import PuzzleSpec
from .generator import generate_solution, generate_puzzle
from .vocabulary import build_vocabulary
from .formatter import format_text, format_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Einstein's Riddle puzzle generator",
    )
    parser.add_argument(
        "-n", type=int, default=5,
        help="Number of houses / values per category (default: 5)",
    )
    parser.add_argument(
        "-m", type=int, default=0,
        help="Number of categories (default: same as -n)",
    )
    parser.add_argument(
        "--difficulty", choices=["easy", "medium", "hard"], default="medium",
        help="Puzzle difficulty (default: medium)",
    )
    parser.add_argument(
        "--format", choices=["text", "json", "both"], default="auto",
        dest="fmt",
        help="Output format (default: auto — text+json for N<=15, json for N>15)",
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--no-solution", action="store_true",
        help="Don't include solution in output",
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Suppress progress messages",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    n = args.n
    m = args.m if args.m > 0 else n

    if n < 2:
        print("Error: N must be at least 2", file=sys.stderr)
        sys.exit(1)
    if m < 2:
        print("Error: M must be at least 2", file=sys.stderr)
        sys.exit(1)
    if n > 200:
        print("Error: N > 200 is not supported", file=sys.stderr)
        sys.exit(1)

    # Determine output format
    fmt = args.fmt
    if fmt == "auto":
        fmt = "both" if n <= 15 else "json"

    # Seed
    if args.seed is not None:
        random.seed(args.seed)

    # Progress logger
    def progress(msg: str) -> None:
        if not args.quiet:
            print(f"  [{msg}]", file=sys.stderr)

    progress(f"Generating {n}x{m} puzzle...")
    t0 = time.time()

    # Build vocabulary
    spec = build_vocabulary(n, m)

    # Generate random solution
    sol = generate_solution(n, m)

    # Generate clues
    clues = generate_puzzle(sol, spec, difficulty=args.difficulty, progress=progress)

    elapsed = time.time() - t0
    progress(f"Generated in {elapsed:.2f}s")

    # Format output
    solution = None if args.no_solution else sol
    output_parts: list[str] = []

    if fmt in ("text", "both"):
        output_parts.append(format_text(spec, clues, solution))

    if fmt in ("json", "both"):
        if output_parts:
            output_parts.append("")
            output_parts.append("=== JSON ===")
        output_parts.append(format_json(spec, clues, solution))

    result = "\n".join(output_parts)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
            f.write("\n")
        progress(f"Written to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
