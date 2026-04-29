"""Minimal Cheddar command-line interface.

This module provides a thin package-backed wrapper around the existing lint
scripts and a small artifact generator. The lint command intentionally avoids
refactoring the existing lint implementation yet, so the package entrypoint
becomes useful without changing the framework model.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from cheddar.templates import BUILDERS


REPO_ROOT = Path(__file__).resolve().parents[2]
LINT_RUNNER = REPO_ROOT / "lint" / "run_all.py"
NON_MISSION_TYPES = {"flow", "track", "brief", "personal"}


def run_lint(args: argparse.Namespace) -> int:
    """Run Cheddar lint checks through the existing lint runner."""
    if not LINT_RUNNER.exists():
        print(
            "Error: lint/run_all.py was not found. "
            "The minimal cheddar CLI currently requires a repository checkout "
            "or editable install. Run `python lint/run_all.py ...` from the "
            "repository root, or install with `python -m pip install -e .`.",
            file=sys.stderr,
        )
        return 1

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


def run_new(args: argparse.Namespace) -> int:
    """Generate a starter artifact YAML file."""
    artifact_type = args.artifact_type

    if artifact_type in NON_MISSION_TYPES:
        if not args.parent:
            print(f"Error: {artifact_type} artifacts require --parent", file=sys.stderr)
            return 2
        if not args.upstream_hash:
            print(f"Error: {artifact_type} artifacts require --upstream-hash", file=sys.stderr)
            return 2
    elif args.parent or args.upstream_hash:
        print("Error: mission artifacts cannot use --parent or --upstream-hash", file=sys.stderr)
        return 2

    out_path = args.out
    if out_path.exists() and not args.force:
        print(f"Error: output file exists: {out_path}. Use --force to overwrite.", file=sys.stderr)
        return 2

    builder = BUILDERS[artifact_type]
    artifact: dict[str, Any]

    if artifact_type == "mission":
        artifact = builder(args.id, args.title, args.signed_by)
    else:
        artifact = builder(args.id, args.title, args.parent, args.upstream_hash, args.signed_by)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(artifact, handle, sort_keys=False, allow_unicode=True)

    print(f"Created {artifact_type} artifact: {out_path}")
    print(f"Artifact id: {artifact['id']}")
    print(f"Lineage hash: {artifact['lineage']['hash']}")
    return 0


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

    new_parser = subparsers.add_parser(
        "new",
        help="Generate a starter Cheddar artifact.",
    )
    new_parser.add_argument(
        "artifact_type",
        choices=sorted(BUILDERS),
        help="Artifact type to generate.",
    )
    new_parser.add_argument("--id", required=True, help="Artifact id.")
    new_parser.add_argument("--title", required=True, help="Artifact title.")
    new_parser.add_argument(
        "--signed-by",
        default="human_owner",
        help="Signer/owner identity to place in lineage.",
    )
    new_parser.add_argument("--parent", help="Parent artifact id for non-mission artifacts.")
    new_parser.add_argument(
        "--upstream-hash",
        help="Parent lineage hash for non-mission artifacts.",
    )
    new_parser.add_argument("--out", required=True, type=Path, help="Output YAML path.")
    new_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite output file if it already exists.",
    )
    new_parser.set_defaults(handler=run_new)

    return parser


def main() -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
