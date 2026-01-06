# Lint Directory

**Status:** `[EXISTS]` — Core tools implemented

## Purpose

This directory contains **verification scripts** that enforce Cheddar invariants. These are the mechanical guarantees that make Cheddar trustworthy.

## Contents

```
lint/
├── README.md                    # This file
├── validate_artifact.py         # [EXISTS] Schema validation
├── compute_hash.py              # [EXISTS] Lineage hash computation
├── verify_lineage.py            # [EXISTS] Chain integrity verification
├── run_all.py                   # [EXISTS] Run all linters
├── verify_signature.py          # [PLANNED] Cryptographic signature validation
├── validate_log.py              # [PLANNED] Documentation log validation
├── check_freshness.py           # [PLANNED] Staleness detection
└── validate_state.py            # [PLANNED] State transition validation
```

## Invariant Enforcement Map

| Script | Enforces |
|--------|----------|
| `validate_artifact.py` | INV-001, INV-002, INV-003, INV-020, INV-040 |
| `compute_hash.py` | INV-004 |
| `verify_lineage.py` | INV-005 |
| `verify_signature.py` | INV-023 |
| `validate_log.py` | INV-010, INV-012 |
| `check_freshness.py` | INV-011 |
| `validate_state.py` | INV-041 |

## Usage

```bash
# Validate single artifact
python lint/validate_artifact.py path/to/artifact.yaml

# Validate directory of artifacts
python lint/validate_artifact.py schemas/examples/

# Validate recursively
python lint/validate_artifact.py artifacts/ --recursive

# Compute hash for an artifact
python lint/compute_hash.py path/to/artifact.yaml

# Update artifact with computed hash
python lint/compute_hash.py path/to/artifact.yaml --update

# Verify existing hash
python lint/compute_hash.py path/to/artifact.yaml --verify

# Verify lineage chain
python lint/verify_lineage.py schemas/examples/

# Skip hash verification (only check references)
python lint/verify_lineage.py schemas/examples/ --skip-hash

# Run all checks on examples
python lint/run_all.py --examples

# Run all checks on custom directory
python lint/run_all.py artifacts/ --recursive

# Output as JSON
python lint/validate_artifact.py artifact.yaml --json
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Validation errors found |
| 2 | Configuration/usage error |
| 3 | Internal error |

## Output Format

Linters output JSON for machine parsing:

```json
{
  "linter": "validate_artifact",
  "file": "artifacts/example/mission_qa_v1.yaml",
  "passed": false,
  "errors": [
    {
      "invariant": "INV-001",
      "field": "id",
      "message": "Missing required field 'id'"
    }
  ],
  "warnings": []
}
```

## Hash Computation

The `compute_hash.py` script computes `lineage.hash` using:

1. Serialize artifact to canonical JSON (sorted keys, no whitespace)
2. Exclude `lineage.hash` field from serialization
3. Compute SHA-256 of canonical representation
4. Prefix with `sha256:`

```python
# Pseudocode
def compute_hash(artifact: dict) -> str:
    content = copy.deepcopy(artifact)
    if 'lineage' in content and 'hash' in content['lineage']:
        del content['lineage']['hash']
    canonical = json.dumps(content, sort_keys=True, separators=(',', ':'))
    digest = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    return f"sha256:{digest}"
```

## Dependencies

- Python 3.11+
- PyYAML
- jsonschema (for schema validation)

## Next Steps

1. Implement `validate_artifact.py` with schema validation
2. Implement `compute_hash.py` for lineage hash computation
3. Implement `verify_lineage.py` for chain verification
4. Add pre-commit hook configuration
5. Integrate with CI/CD
