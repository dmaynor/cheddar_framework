"""Minimal Cheddar command-line interface.

This module provides a thin package-backed wrapper around the existing lint
scripts. It intentionally avoids refactoring the lint implementation yet, so the
package entrypoint declared in pyproject.toml becomes real without changing the
framework model.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LINT_RUNNER = REPO_ROOT / "lint" / "run_all.py"


def run_lint(args: argparse.Namespace) -> int:
    """Run Cheddar lint checks through the existing lint runner."""
    command = [sys.executable, str(LINT_RUNNER)]

    if args.examples:
        command.append("--examples")

    if args.recursive:
        command.append("--recursive")

    if args.strict:
        command.append("--strict")

    if args.skip_chain:
        command.append("--skip-chain")

    if args.skip_hash:
        command.append("--skip-hash")

    if args.json:
        command.append("--json")

    command.extend(str(path) for path in args.paths)

    completed = subprocess.run(command, check=False)
    return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level Cheddar CLI parser."""
    parser = argparse.ArgumentParser(
        prog="cheddar",
        description="Cheddar Framework command-line tools.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    lint_parser = subparsers.add_parser(
        "lint",
        help="Run schema, lineage, and hash validation.",
    )
    lint_parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Artifact files or directories to validate.",
    )
    lint_parser.add_argument(
        "--examples",
        action="store_true",
        help="Validate schemas/examples/.",
    )
    lint_parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Recursively process directories.",
    )
    lint_parser.add_argument(
        "--strict",
        action="store_true",
        help="Require schema validation, lineage links, and artifact hashes.",
    )
    lint_parser.add_argument(
        "--skip-chain",
        action="store_true",
        help="Skip lineage verification.",
    )
    lint_parser.add_argument(
        "--skip-hash",
        action="store_true",
        help="Skip individual hash verification while checking chain links.",
    )
    lint_parser.add_argument(
        "--json",
        action="store_true",
        help="Output lint results as JSON.",
    )
    lint_parser.set_defaults(handler=run_lint)

    return parser


def main() -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
