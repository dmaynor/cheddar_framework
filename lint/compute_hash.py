#!/usr/bin/env python3
"""
Cheddar Lineage Hash Computation

Computes and optionally updates the lineage.hash field for Cheddar artifacts.
Enforces: INV-004 (Every artifact MUST include a lineage.hash computed from content)

Algorithm:
    1. Deep copy artifact
    2. Remove lineage.hash field (if present)
    3. Serialize to canonical JSON (sorted keys, no whitespace)
    4. Compute SHA-256 of UTF-8 encoded canonical form
    5. Prefix with "sha256:"

Usage:
    python compute_hash.py <artifact.yaml>           # Display computed hash
    python compute_hash.py <artifact.yaml> --update  # Update file in place
    python compute_hash.py <artifact.yaml> --verify  # Verify existing hash

Exit codes:
    0 - Success (hash computed/verified/updated)
    1 - Hash mismatch (--verify mode)
    2 - Usage/configuration error
    3 - Internal error
"""

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

import yaml

# Exit codes
EXIT_SUCCESS = 0
EXIT_HASH_MISMATCH = 1
EXIT_USAGE_ERROR = 2
EXIT_INTERNAL_ERROR = 3


def compute_hash(artifact: dict) -> str:
    """
    Compute the lineage hash for an artifact.
    
    The hash is computed from a canonical JSON representation with:
    - lineage.hash field excluded
    - Keys sorted alphabetically at all levels
    - No whitespace (compact separators)
    - UTF-8 encoding
    
    Returns:
        Hash string in format "sha256:<64 hex chars>"
    """
    # Deep copy to avoid modifying original
    content = copy.deepcopy(artifact)
    
    # Remove lineage.hash if present
    if "lineage" in content and "hash" in content["lineage"]:
        del content["lineage"]["hash"]
    
    # Handle documentation_log wrapper
    if "documentation_log" in content:
        log = content["documentation_log"]
        if "lineage" in log and "hash" in log["lineage"]:
            del log["lineage"]["hash"]
    
    # Serialize to canonical JSON
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"))
    
    # Compute SHA-256
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    
    return f"sha256:{digest}"


def load_artifact(path: Path) -> dict:
    """Load a YAML artifact file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_artifact(path: Path, artifact: dict) -> None:
    """
    Save an artifact back to YAML, preserving comments where possible.
    
    Note: PyYAML does not preserve comments. For production use,
    consider ruamel.yaml for round-trip preservation.
    """
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(artifact, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def get_existing_hash(artifact: dict) -> str | None:
    """Extract existing lineage.hash from artifact."""
    # Standard artifacts
    if "lineage" in artifact and "hash" in artifact["lineage"]:
        return artifact["lineage"]["hash"]
    
    # Documentation logs
    if "documentation_log" in artifact:
        log = artifact["documentation_log"]
        if "lineage" in log and "hash" in log["lineage"]:
            return log["lineage"]["hash"]
    
    return None


def set_hash(artifact: dict, hash_value: str) -> dict:
    """Set lineage.hash in artifact and return modified artifact."""
    result = copy.deepcopy(artifact)
    
    # Standard artifacts
    if "lineage" in result:
        result["lineage"]["hash"] = hash_value
    elif "documentation_log" in result and "lineage" in result["documentation_log"]:
        result["documentation_log"]["lineage"]["hash"] = hash_value
    else:
        # Create lineage block if missing
        result["lineage"] = {"hash": hash_value}
    
    return result


def format_output(
    path: Path,
    computed_hash: str,
    existing_hash: str | None,
    mode: str
) -> dict:
    """
    Format output for display or JSON.
    
    Returns dict with:
        - file: str
        - computed_hash: str
        - existing_hash: str | None
        - match: bool | None
        - action: str
    """
    result = {
        "file": str(path),
        "computed_hash": computed_hash,
        "existing_hash": existing_hash,
        "match": None,
        "action": mode,
    }
    
    if existing_hash:
        result["match"] = (computed_hash == existing_hash)
    
    return result


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compute and manage Cheddar artifact lineage hashes."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Artifact file to process",
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--update", "-u",
        action="store_true",
        help="Update artifact file with computed hash",
    )
    mode_group.add_argument(
        "--verify", "-v",
        action="store_true",
        help="Verify existing hash matches computed hash",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    args = parser.parse_args()
    
    if not args.path.exists():
        print(f"Error: File not found: {args.path}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    
    if not args.path.is_file():
        print(f"Error: Not a file: {args.path}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    
    try:
        artifact = load_artifact(args.path)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML: {e}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    except Exception as e:
        print(f"Error: Failed to load file: {e}", file=sys.stderr)
        return EXIT_INTERNAL_ERROR
    
    try:
        computed_hash = compute_hash(artifact)
        existing_hash = get_existing_hash(artifact)
        
        # Determine mode
        if args.update:
            mode = "update"
        elif args.verify:
            mode = "verify"
        else:
            mode = "compute"
        
        result = format_output(args.path, computed_hash, existing_hash, mode)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if mode == "compute":
                print(f"File: {args.path}")
                print(f"Computed hash: {computed_hash}")
                if existing_hash:
                    match_str = "✓" if result["match"] else "✗"
                    print(f"Existing hash: {existing_hash} {match_str}")
                else:
                    print("Existing hash: (none)")
            
            elif mode == "verify":
                if not existing_hash:
                    print(f"✗ {args.path}: No existing hash to verify")
                    return EXIT_HASH_MISMATCH
                
                if result["match"]:
                    print(f"✓ {args.path}: Hash verified")
                else:
                    print(f"✗ {args.path}: Hash mismatch")
                    print(f"  Expected: {existing_hash}")
                    print(f"  Computed: {computed_hash}")
                    return EXIT_HASH_MISMATCH
            
            elif mode == "update":
                updated = set_hash(artifact, computed_hash)
                save_artifact(args.path, updated)
                print(f"✓ {args.path}: Hash updated to {computed_hash}")
        
        return EXIT_SUCCESS
        
    except Exception as e:
        print(f"Internal error: {e}", file=sys.stderr)
        return EXIT_INTERNAL_ERROR


if __name__ == "__main__":
    sys.exit(main())
