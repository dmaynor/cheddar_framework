#!/usr/bin/env python3
"""
Cheddar Artifact Validator

Validates Cheddar artifacts against JSON Schema definitions.
Enforces: INV-001, INV-002, INV-003, INV-020, INV-040

Usage:
    python validate_artifact.py <artifact.yaml> [--schema <schema.json>]
    python validate_artifact.py <directory> [--recursive]

Exit codes:
    0 - All validations passed
    1 - Validation errors found
    2 - Usage/configuration error
    3 - Internal error
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import yaml
from jsonschema import Draft7Validator, ValidationError

# Exit codes
EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 1
EXIT_USAGE_ERROR = 2
EXIT_INTERNAL_ERROR = 3

# Artifact level to schema mapping
LEVEL_TO_SCHEMA = {
    "mission": "mission_definition.schema.json",
    "flow_initiative": "flow_initiative.schema.json",
    "cheddar_track": "cheddar_track.schema.json",
    "automation_brief": "automation_brief.schema.json",
    "personal": "personal_artifact.schema.json",
}

# Special case for documentation logs (detected by structure, not level)
DOCUMENTATION_LOG_SCHEMA = "documentation_log.schema.json"


def find_schema_dir() -> Path:
    """Locate the schemas directory relative to this script."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    schema_dir = repo_root / "schemas"
    
    if not schema_dir.exists():
        raise FileNotFoundError(f"Schema directory not found: {schema_dir}")
    
    return schema_dir


def load_schema(schema_path: Path) -> dict:
    """Load a JSON Schema file."""
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_artifact(artifact_path: Path) -> dict:
    """Load a YAML artifact file."""
    with open(artifact_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def detect_artifact_type(artifact: dict) -> Optional[str]:
    """
    Detect artifact type from content.
    
    Returns schema filename or None if unrecognized.
    """
    # Check for documentation log (has 'documentation_log' key)
    if "documentation_log" in artifact:
        return DOCUMENTATION_LOG_SCHEMA
    
    # Check for standard artifacts (have 'level' field)
    level = artifact.get("level")
    if level in LEVEL_TO_SCHEMA:
        return LEVEL_TO_SCHEMA[level]
    
    return None


def validate_artifact(
    artifact: dict,
    schema: dict,
    artifact_path: str
) -> dict:
    """
    Validate an artifact against a schema.
    
    Returns a result dict with:
        - linter: str
        - file: str
        - passed: bool
        - errors: list[dict]
        - warnings: list[dict]
    """
    result = {
        "linter": "validate_artifact",
        "file": str(artifact_path),
        "passed": True,
        "errors": [],
        "warnings": [],
    }
    
    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(artifact))
    
    if errors:
        result["passed"] = False
        for error in errors:
            path = ".".join(str(p) for p in error.absolute_path) or "(root)"
            
            # Map to invariants where applicable
            invariant = map_error_to_invariant(error, path)
            
            result["errors"].append({
                "invariant": invariant,
                "field": path,
                "message": error.message,
            })
    
    # Additional semantic checks beyond JSON Schema
    semantic_errors = check_semantic_rules(artifact)
    if semantic_errors:
        result["passed"] = False
        result["errors"].extend(semantic_errors)
    
    return result


def map_error_to_invariant(error: ValidationError, path: str) -> Optional[str]:
    """Map a validation error to the relevant Cheddar invariant."""
    # INV-001: Every artifact MUST have a stable, unique id
    if path == "id" or "id" in path:
        return "INV-001"
    
    # INV-002: Every artifact MUST include a version
    if "_v" in str(error.instance) if error.instance else False:
        return "INV-002"
    
    # INV-003: Every non-mission artifact MUST reference exactly one upstream
    if "supports_upper_layer" in path:
        return "INV-003"
    
    # INV-020: Every automation MUST have an identified human owner
    if path == "owner" or "owner" in path:
        return "INV-020"
    
    # INV-040: cheddar_state MUST be valid
    if "cheddar_state" in path:
        return "INV-040"
    
    return None


def check_semantic_rules(artifact: dict) -> list:
    """
    Check semantic rules beyond JSON Schema validation.
    
    Returns list of error dicts.
    """
    errors = []
    
    # INV-001: ID must follow naming convention
    artifact_id = artifact.get("id", "")
    if artifact_id and "_v" not in artifact_id:
        errors.append({
            "invariant": "INV-002",
            "field": "id",
            "message": f"ID '{artifact_id}' missing version suffix (expected '_v<number>')",
        })
    
    # INV-003: Non-mission artifacts must have upstream reference
    level = artifact.get("level", "")
    if level and level != "mission":
        if not artifact.get("supports_upper_layer"):
            errors.append({
                "invariant": "INV-003",
                "field": "supports_upper_layer",
                "message": "Non-mission artifact must reference upstream artifact",
            })
    
    # Mission artifacts must have null upstream_hash
    if level == "mission":
        lineage = artifact.get("lineage", {})
        if lineage.get("upstream_hash") is not None:
            errors.append({
                "invariant": "INV-003",
                "field": "lineage.upstream_hash",
                "message": "Mission artifact upstream_hash must be null",
            })
    
    return errors


def validate_file(
    artifact_path: Path,
    schema_path: Optional[Path] = None
) -> dict:
    """
    Validate a single artifact file.
    
    If schema_path is None, auto-detect from artifact content.
    """
    try:
        artifact = load_artifact(artifact_path)
    except yaml.YAMLError as e:
        return {
            "linter": "validate_artifact",
            "file": str(artifact_path),
            "passed": False,
            "errors": [{
                "invariant": None,
                "field": "(file)",
                "message": f"Invalid YAML: {e}",
            }],
            "warnings": [],
        }
    except Exception as e:
        return {
            "linter": "validate_artifact",
            "file": str(artifact_path),
            "passed": False,
            "errors": [{
                "invariant": None,
                "field": "(file)",
                "message": f"Failed to load file: {e}",
            }],
            "warnings": [],
        }
    
    # Determine schema
    if schema_path:
        schema_file = schema_path
    else:
        schema_dir = find_schema_dir()
        schema_name = detect_artifact_type(artifact)
        
        if not schema_name:
            return {
                "linter": "validate_artifact",
                "file": str(artifact_path),
                "passed": False,
                "errors": [{
                    "invariant": None,
                    "field": "level",
                    "message": f"Cannot detect artifact type. Unknown level: {artifact.get('level')}",
                }],
                "warnings": [],
            }
        
        schema_file = schema_dir / schema_name
    
    try:
        schema = load_schema(schema_file)
    except Exception as e:
        return {
            "linter": "validate_artifact",
            "file": str(artifact_path),
            "passed": False,
            "errors": [{
                "invariant": None,
                "field": "(schema)",
                "message": f"Failed to load schema {schema_file}: {e}",
            }],
            "warnings": [],
        }
    
    return validate_artifact(artifact, schema, artifact_path)


def validate_directory(
    directory: Path,
    recursive: bool = False
) -> list:
    """
    Validate all YAML files in a directory.
    
    Returns list of result dicts.
    """
    results = []
    
    pattern = "**/*.yaml" if recursive else "*.yaml"
    for artifact_path in directory.glob(pattern):
        # Skip non-artifact files
        if artifact_path.name.startswith("."):
            continue
        
        result = validate_file(artifact_path)
        results.append(result)
    
    return results


def print_results(results: list, output_json: bool = False) -> int:
    """
    Print validation results.
    
    Returns appropriate exit code.
    """
    if output_json:
        print(json.dumps(results, indent=2))
    else:
        all_passed = True
        for result in results:
            status = "✓" if result["passed"] else "✗"
            print(f"{status} {result['file']}")
            
            if not result["passed"]:
                all_passed = False
                for error in result["errors"]:
                    inv = f"[{error['invariant']}] " if error["invariant"] else ""
                    print(f"  {inv}{error['field']}: {error['message']}")
            
            for warning in result.get("warnings", []):
                print(f"  ⚠ {warning['field']}: {warning['message']}")
        
        print()
        passed_count = sum(1 for r in results if r["passed"])
        total_count = len(results)
        print(f"Passed: {passed_count}/{total_count}")
        
        if not all_passed:
            return EXIT_VALIDATION_ERROR
    
    # Check if any failed
    if any(not r["passed"] for r in results):
        return EXIT_VALIDATION_ERROR
    
    return EXIT_SUCCESS


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Cheddar artifacts against JSON Schema definitions."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Artifact file or directory to validate",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        help="Explicit schema file (auto-detected if not specified)",
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Recursively validate directory",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    args = parser.parse_args()
    
    if not args.path.exists():
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    
    try:
        if args.path.is_file():
            results = [validate_file(args.path, args.schema)]
        elif args.path.is_dir():
            results = validate_directory(args.path, args.recursive)
        else:
            print(f"Error: Invalid path type: {args.path}", file=sys.stderr)
            return EXIT_USAGE_ERROR
        
        if not results:
            print("No artifacts found to validate.")
            return EXIT_SUCCESS
        
        return print_results(results, args.json)
        
    except Exception as e:
        print(f"Internal error: {e}", file=sys.stderr)
        return EXIT_INTERNAL_ERROR


if __name__ == "__main__":
    sys.exit(main())
