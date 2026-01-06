#!/usr/bin/env python3
"""
Cheddar Lint Runner

Orchestrates all Cheddar lint checks.

Runs:
    1. validate_artifact.py - Schema validation
    2. verify_lineage.py - Chain integrity

Usage:
    python run_all.py <directory>
    python run_all.py <directory> --recursive
    python run_all.py --examples  # Validate schema examples

Exit codes:
    0 - All checks passed
    1 - Validation errors found
    2 - Usage/configuration error
    3 - Internal error
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Import lint modules
from validate_artifact import validate_directory, validate_file
from verify_lineage import load_artifacts, verify_chain

# Exit codes
EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 1
EXIT_USAGE_ERROR = 2
EXIT_INTERNAL_ERROR = 3


def find_examples_dir() -> Path:
    """Locate the schemas/examples directory."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    examples_dir = repo_root / "schemas" / "examples"
    
    if not examples_dir.exists():
        raise FileNotFoundError(f"Examples directory not found: {examples_dir}")
    
    return examples_dir


def run_all_checks(
    paths: list[Path],
    recursive: bool = False,
    skip_chain: bool = False
) -> dict:
    """
    Run all lint checks on the specified paths.
    
    Returns combined result dict.
    """
    combined = {
        "passed": True,
        "checks": {},
        "summary": {
            "total_errors": 0,
            "total_warnings": 0,
        },
    }
    
    # 1. Schema validation
    validation_results = []
    for path in paths:
        if path.is_file():
            validation_results.append(validate_file(path))
        elif path.is_dir():
            validation_results.extend(validate_directory(path, recursive))
    
    validation_errors = sum(len(r["errors"]) for r in validation_results)
    validation_passed = all(r["passed"] for r in validation_results)
    
    combined["checks"]["validate_artifact"] = {
        "passed": validation_passed,
        "files_checked": len(validation_results),
        "errors": validation_errors,
        "results": validation_results,
    }
    
    if not validation_passed:
        combined["passed"] = False
    
    combined["summary"]["total_errors"] += validation_errors
    
    # 2. Lineage chain verification (only if validation passed or forced)
    if not skip_chain:
        artifacts = load_artifacts(paths, recursive)
        chain_result = verify_chain(artifacts, skip_hash_verify=True)
        
        combined["checks"]["verify_lineage"] = {
            "passed": chain_result["passed"],
            "artifacts_checked": chain_result["artifacts_checked"],
            "errors": len(chain_result["errors"]),
            "results": chain_result,
        }
        
        if not chain_result["passed"]:
            combined["passed"] = False
        
        combined["summary"]["total_errors"] += len(chain_result["errors"])
    
    return combined


def print_summary(result: dict, output_json: bool = False) -> int:
    """
    Print combined lint results.
    
    Returns appropriate exit code.
    """
    if output_json:
        print(json.dumps(result, indent=2))
        return EXIT_SUCCESS if result["passed"] else EXIT_VALIDATION_ERROR
    
    print("=" * 60)
    print("CHEDDAR LINT RESULTS")
    print("=" * 60)
    print()
    
    # Validation results
    if "validate_artifact" in result["checks"]:
        check = result["checks"]["validate_artifact"]
        status = "✓ PASSED" if check["passed"] else "✗ FAILED"
        print(f"Schema Validation: {status}")
        print(f"  Files checked: {check['files_checked']}")
        print(f"  Errors: {check['errors']}")
        
        if not check["passed"]:
            print()
            for file_result in check["results"]:
                if not file_result["passed"]:
                    print(f"  {file_result['file']}:")
                    for error in file_result["errors"]:
                        inv = f"[{error['invariant']}] " if error.get("invariant") else ""
                        print(f"    {inv}{error['field']}: {error['message']}")
        print()
    
    # Chain verification results
    if "verify_lineage" in result["checks"]:
        check = result["checks"]["verify_lineage"]
        status = "✓ PASSED" if check["passed"] else "✗ FAILED"
        print(f"Lineage Verification: {status}")
        print(f"  Artifacts checked: {check['artifacts_checked']}")
        print(f"  Errors: {check['errors']}")
        
        if not check["passed"]:
            print()
            for error in check["results"]["errors"]:
                inv = f"[{error['invariant']}] " if error.get("invariant") else ""
                print(f"  {inv}{error['artifact']}: {error['message']}")
        print()
    
    # Summary
    print("-" * 60)
    overall = "✓ ALL CHECKS PASSED" if result["passed"] else "✗ CHECKS FAILED"
    print(f"Overall: {overall}")
    print(f"Total errors: {result['summary']['total_errors']}")
    print()
    
    return EXIT_SUCCESS if result["passed"] else EXIT_VALIDATION_ERROR


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run all Cheddar lint checks."
    )
    parser.add_argument(
        "paths",
        type=Path,
        nargs="*",
        help="Artifact files or directories to check",
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Recursively process directories",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Validate schema examples (schemas/examples/)",
    )
    parser.add_argument(
        "--skip-chain",
        action="store_true",
        help="Skip lineage chain verification",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    args = parser.parse_args()
    
    # Determine paths to check
    if args.examples:
        try:
            paths = [find_examples_dir()]
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            return EXIT_USAGE_ERROR
    elif args.paths:
        paths = args.paths
    else:
        print("Error: Specify paths or use --examples", file=sys.stderr)
        parser.print_help()
        return EXIT_USAGE_ERROR
    
    # Validate paths exist
    for path in paths:
        if not path.exists():
            print(f"Error: Path not found: {path}", file=sys.stderr)
            return EXIT_USAGE_ERROR
    
    try:
        result = run_all_checks(
            paths,
            recursive=args.recursive,
            skip_chain=args.skip_chain,
        )
        return print_summary(result, args.json)
        
    except Exception as e:
        print(f"Internal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return EXIT_INTERNAL_ERROR


if __name__ == "__main__":
    sys.exit(main())
