"""Command-line interface for ssh-orchestrator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .engagement import EngagementError, load_engagement
from .modules import ModuleError, discover_modules, resolve_modules
from .orchestrator import execute
from .report import write_run


EXIT_OK = 0
EXIT_USAGE = 2
EXIT_AUTH = 3
EXIT_RUN_ERRORS = 4


def _module_dirs(args: argparse.Namespace) -> list[Path]:
    return [Path(p) for p in (args.module_dir or [])]


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        engagement = load_engagement(args.engagement)
    except (FileNotFoundError, EngagementError) as exc:
        print(f"engagement invalid: {exc}", file=sys.stderr)
        return EXIT_USAGE
    try:
        modules = resolve_modules(engagement.modules, _module_dirs(args))
        for module in modules:
            engagement.assert_module_risk_allowed(module.id, module.risk)
    except (ModuleError, EngagementError) as exc:
        print(f"modules invalid: {exc}", file=sys.stderr)
        return EXIT_USAGE
    print(
        f"OK: engagement {engagement.id!r} authorizes "
        f"{len(engagement.targets)} target(s) and "
        f"{len(modules)} module(s) at max_risk={engagement.max_risk}"
    )
    return EXIT_OK


def cmd_list_modules(args: argparse.Namespace) -> int:
    catalog = discover_modules(_module_dirs(args))
    if not catalog:
        print("No modules found.", file=sys.stderr)
        return EXIT_OK
    width = max(len(m.id) for m in catalog.values())
    for mid in sorted(catalog):
        m = catalog[mid]
        print(
            f"{m.id:<{width}}  risk={m.risk:<9} "
            f"platforms={','.join(m.platforms):<14} "
            f"checks={len(m.checks):<3} {m.name}"
        )
    return EXIT_OK


def cmd_run(args: argparse.Namespace) -> int:
    try:
        engagement = load_engagement(args.engagement)
    except (FileNotFoundError, EngagementError) as exc:
        print(f"engagement invalid: {exc}", file=sys.stderr)
        return EXIT_USAGE

    try:
        modules = resolve_modules(engagement.modules, _module_dirs(args))
    except ModuleError as exc:
        print(f"modules invalid: {exc}", file=sys.stderr)
        return EXIT_USAGE

    try:
        run = execute(
            engagement,
            modules,
            dry_run=args.dry_run,
            progress=lambda msg: print(msg, file=sys.stderr) if args.verbose else None,
        )
    except EngagementError as exc:
        print(f"authorization error: {exc}", file=sys.stderr)
        return EXIT_AUTH

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    run_path = write_run(run, output_dir)

    print(f"wrote {run_path}")
    totals = _summarize(run)
    print(
        f"hosts={totals['hosts']} checks={totals['checks']} "
        f"failed={totals['failed']} timed_out={totals['timed_out']} "
        f"skipped={totals['skipped']} unreachable={totals['unreachable']}"
    )
    if totals["failed"] or totals["unreachable"]:
        return EXIT_RUN_ERRORS
    return EXIT_OK


def _summarize(run) -> dict:
    failed = 0
    timed_out = 0
    skipped = 0
    checks = 0
    unreachable = 0
    for h in run.hosts:
        if h.error:
            unreachable += 1
        for c in h.checks:
            checks += 1
            if c.skipped_reason:
                skipped += 1
                continue
            if c.result.timed_out:
                timed_out += 1
            if c.result.exit_code != 0:
                failed += 1
    return {
        "hosts": len(run.hosts),
        "checks": checks,
        "failed": failed,
        "timed_out": timed_out,
        "skipped": skipped,
        "unreachable": unreachable,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ssh-orch",
        description=(
            "Orchestrate authorized remote security testing over SSH. "
            "Requires an engagement plan with explicit authorization and scope."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"ssh-orchestrator {__version__}"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Execute the engagement.")
    p_run.add_argument("engagement", type=Path, help="Path to engagement YAML.")
    p_run.add_argument(
        "-o", "--output", type=Path, default=Path("./ssh-orch-runs"),
        help="Directory to write run.json and evidence/ into.",
    )
    p_run.add_argument(
        "--module-dir", action="append",
        help="Additional directory of module YAMLs (repeatable).",
    )
    p_run.add_argument(
        "--dry-run", action="store_true",
        help="Plan and authorize but do not execute remote commands.",
    )
    p_run.add_argument(
        "-v", "--verbose", action="store_true",
        help="Stream per-check progress to stderr.",
    )
    p_run.set_defaults(handler=cmd_run)

    p_val = sub.add_parser("validate", help="Validate an engagement plan.")
    p_val.add_argument("engagement", type=Path)
    p_val.add_argument("--module-dir", action="append")
    p_val.set_defaults(handler=cmd_validate)

    p_list = sub.add_parser("list-modules", help="List available modules.")
    p_list.add_argument("--module-dir", action="append")
    p_list.set_defaults(handler=cmd_list_modules)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
