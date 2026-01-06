#!/usr/bin/env python3
"""
Cheddar Lineage Chain Verification

Verifies the integrity of artifact lineage chains.
Enforces: INV-005 (Every non-mission artifact's upstream_hash MUST match parent's hash)

Checks:
    1. Each artifact's lineage.hash matches computed hash (INV-004)
    2. Each non-mission artifact has supports_upper_layer reference (INV-003)
    3. Each upstream_hash matches the referenced parent's hash (INV-005)
    4. Mission artifacts have null upstream_hash
    5. No orphaned artifacts (all parents exist)
    6. No circular references

Usage:
    python verify_lineage.py <directory>             # Verify all artifacts in directory
    python verify_lineage.py <directory> --recursive # Include subdirectories
    python verify_lineage.py <file1> <file2> ...     # Verify specific files

Exit codes:
    0 - All chains verified
    1 - Chain verification errors found
    2 - Usage/configuration error
    3 - Internal error
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import yaml

from compute_hash import compute_hash

# Exit codes
EXIT_SUCCESS = 0
EXIT_VERIFICATION_ERROR = 1
EXIT_USAGE_ERROR = 2
EXIT_INTERNAL_ERROR = 3


def load_artifact(path: Path) -> dict:
    """Load a YAML artifact file."""
    with open(path, "r", encoding="utf-8") as f:
        content = yaml.safe_load(f)
        content["_source_path"] = str(path)
        return content


def get_artifact_id(artifact: dict) -> Optional[str]:
    """Extract artifact ID."""
    return artifact.get("id")


def get_artifact_level(artifact: dict) -> Optional[str]:
    """Extract artifact level/type."""
    return artifact.get("level")


def get_lineage(artifact: dict) -> dict:
    """Extract lineage block from artifact."""
    return artifact.get("lineage", {})


def get_upstream_ref(artifact: dict) -> Optional[str]:
    """Extract supports_upper_layer reference."""
    return artifact.get("supports_upper_layer")


def load_artifacts(paths: list[Path], recursive: bool = False) -> list[dict]:
    """
    Load all artifacts from paths.
    
    Paths can be files or directories.
    """
    artifacts = []
    
    for path in paths:
        if path.is_file() and path.suffix in (".yaml", ".yml"):
            try:
                artifacts.append(load_artifact(path))
            except Exception as e:
                print(f"Warning: Failed to load {path}: {e}", file=sys.stderr)
        
        elif path.is_dir():
            pattern = "**/*.yaml" if recursive else "*.yaml"
            for file_path in path.glob(pattern):
                if file_path.name.startswith("."):
                    continue
                try:
                    artifact = load_artifact(file_path)
                    # Skip non-artifact YAML files
                    if artifact.get("level") or artifact.get("documentation_log"):
                        artifacts.append(artifact)
                except Exception as e:
                    print(f"Warning: Failed to load {file_path}: {e}", file=sys.stderr)
    
    return artifacts


def build_artifact_index(artifacts: list[dict]) -> dict[str, dict]:
    """Build index of artifacts by ID."""
    index = {}
    for artifact in artifacts:
        artifact_id = get_artifact_id(artifact)
        if artifact_id:
            index[artifact_id] = artifact
    return index


def verify_artifact_hash(artifact: dict) -> list[dict]:
    """
    Verify an artifact's own hash.
    
    Returns list of error dicts.
    """
    errors = []
    artifact_id = get_artifact_id(artifact) or "(unknown)"
    source = artifact.get("_source_path", "(unknown)")
    
    lineage = get_lineage(artifact)
    existing_hash = lineage.get("hash")
    
    if not existing_hash:
        errors.append({
            "invariant": "INV-004",
            "artifact": artifact_id,
            "file": source,
            "message": "Missing lineage.hash field",
        })
        return errors
    
    # Skip hash verification for example hashes (placeholder format)
    if existing_hash.endswith("..."):
        # Example hashes like "sha256:a1b2c3d4e5f6..." are placeholders
        return []
    
    computed = compute_hash(artifact)
    
    if existing_hash != computed:
        errors.append({
            "invariant": "INV-004",
            "artifact": artifact_id,
            "file": source,
            "message": f"Hash mismatch: stored={existing_hash}, computed={computed}",
        })
    
    return errors


def verify_upstream_reference(
    artifact: dict,
    artifact_index: dict[str, dict]
) -> list[dict]:
    """
    Verify an artifact's upstream reference.
    
    Returns list of error dicts.
    """
    errors = []
    artifact_id = get_artifact_id(artifact) or "(unknown)"
    source = artifact.get("_source_path", "(unknown)")
    level = get_artifact_level(artifact)
    
    lineage = get_lineage(artifact)
    upstream_hash = lineage.get("upstream_hash")
    upstream_ref = get_upstream_ref(artifact)
    
    # Mission artifacts: must have null upstream_hash
    if level == "mission":
        if upstream_hash is not None:
            errors.append({
                "invariant": "INV-003",
                "artifact": artifact_id,
                "file": source,
                "message": "Mission artifact must have null upstream_hash",
            })
        return errors
    
    # Non-mission artifacts: must have upstream reference
    if not upstream_ref:
        errors.append({
            "invariant": "INV-003",
            "artifact": artifact_id,
            "file": source,
            "message": "Non-mission artifact missing supports_upper_layer",
        })
        return errors
    
    # Check parent exists
    parent = artifact_index.get(upstream_ref)
    if not parent:
        errors.append({
            "invariant": "INV-005",
            "artifact": artifact_id,
            "file": source,
            "message": f"Parent artifact not found: {upstream_ref}",
        })
        return errors
    
    # Check upstream_hash matches parent's hash
    parent_lineage = get_lineage(parent)
    parent_hash = parent_lineage.get("hash")
    
    if not upstream_hash:
        errors.append({
            "invariant": "INV-005",
            "artifact": artifact_id,
            "file": source,
            "message": "Missing upstream_hash in lineage",
        })
    elif parent_hash:
        # Skip verification for placeholder hashes
        if not upstream_hash.endswith("...") and not parent_hash.endswith("..."):
            if upstream_hash != parent_hash:
                errors.append({
                    "invariant": "INV-005",
                    "artifact": artifact_id,
                    "file": source,
                    "message": f"upstream_hash mismatch: stored={upstream_hash}, parent={parent_hash}",
                })
    
    return errors


def detect_cycles(
    artifacts: list[dict],
    artifact_index: dict[str, dict]
) -> list[dict]:
    """
    Detect circular references in artifact chain.
    
    Returns list of error dicts.
    """
    errors = []
    
    for artifact in artifacts:
        artifact_id = get_artifact_id(artifact)
        if not artifact_id:
            continue
        
        # Walk up the chain, tracking visited nodes
        visited = set()
        current_id = artifact_id
        
        while current_id:
            if current_id in visited:
                errors.append({
                    "invariant": "INV-005",
                    "artifact": artifact_id,
                    "file": artifact.get("_source_path", "(unknown)"),
                    "message": f"Circular reference detected involving: {current_id}",
                })
                break
            
            visited.add(current_id)
            current = artifact_index.get(current_id)
            
            if not current:
                break
            
            current_id = get_upstream_ref(current)
    
    return errors


def verify_chain(
    artifacts: list[dict],
    skip_hash_verify: bool = False
) -> dict:
    """
    Verify complete artifact chain integrity.
    
    Returns result dict with:
        - passed: bool
        - artifacts_checked: int
        - errors: list[dict]
        - warnings: list[dict]
    """
    result = {
        "linter": "verify_lineage",
        "passed": True,
        "artifacts_checked": len(artifacts),
        "errors": [],
        "warnings": [],
    }
    
    # Build index
    artifact_index = build_artifact_index(artifacts)
    
    # Check each artifact
    for artifact in artifacts:
        # Skip documentation logs (no lineage chain)
        if "documentation_log" in artifact:
            continue
        
        # Verify own hash
        if not skip_hash_verify:
            hash_errors = verify_artifact_hash(artifact)
            result["errors"].extend(hash_errors)
        
        # Verify upstream reference
        upstream_errors = verify_upstream_reference(artifact, artifact_index)
        result["errors"].extend(upstream_errors)
    
    # Check for cycles
    cycle_errors = detect_cycles(artifacts, artifact_index)
    result["errors"].extend(cycle_errors)
    
    if result["errors"]:
        result["passed"] = False
    
    return result


def print_results(result: dict, output_json: bool = False) -> int:
    """
    Print verification results.
    
    Returns appropriate exit code.
    """
    if output_json:
        print(json.dumps(result, indent=2))
    else:
        if result["passed"]:
            print(f"✓ Chain verification passed ({result['artifacts_checked']} artifacts)")
        else:
            print(f"✗ Chain verification failed ({result['artifacts_checked']} artifacts)")
            print()
            
            for error in result["errors"]:
                inv = f"[{error['invariant']}] " if error.get("invariant") else ""
                print(f"  {inv}{error['artifact']}")
                print(f"    File: {error['file']}")
                print(f"    {error['message']}")
                print()
        
        for warning in result.get("warnings", []):
            print(f"  ⚠ {warning.get('artifact', '?')}: {warning['message']}")
    
    return EXIT_SUCCESS if result["passed"] else EXIT_VERIFICATION_ERROR


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify Cheddar artifact lineage chain integrity."
    )
    parser.add_argument(
        "paths",
        type=Path,
        nargs="+",
        help="Artifact files or directories to verify",
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Recursively process directories",
    )
    parser.add_argument(
        "--skip-hash",
        action="store_true",
        help="Skip individual hash verification (only check chain links)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    args = parser.parse_args()
    
    # Validate paths exist
    for path in args.paths:
        if not path.exists():
            print(f"Error: Path not found: {path}", file=sys.stderr)
            return EXIT_USAGE_ERROR
    
    try:
        artifacts = load_artifacts(args.paths, args.recursive)
        
        if not artifacts:
            print("No artifacts found to verify.")
            return EXIT_SUCCESS
        
        result = verify_chain(artifacts, skip_hash_verify=args.skip_hash)
        return print_results(result, args.json)
        
    except Exception as e:
        print(f"Internal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return EXIT_INTERNAL_ERROR


if __name__ == "__main__":
    sys.exit(main())
