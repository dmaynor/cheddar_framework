# Artifacts Directory

**Status:** `[REQUIRED]` — Structure defined, implementation pending

## Purpose

This directory contains **signed contract artifacts** — the actual mission definitions, initiatives, tracks, briefs, and personal artifacts that form the accountability chain.

## Planned Structure

```
artifacts/
├── README.md                    # This file
├── .gitkeep                     # Preserve directory in git
└── {organization}/              # Namespace by org or project
    ├── missions/
    │   └── mission_*.yaml
    ├── initiatives/
    │   └── flow_*.yaml
    ├── tracks/
    │   └── track_*.yaml
    ├── briefs/
    │   └── brief_*.yaml
    └── personal/
    │   └── personal_*.yaml
```

## Artifact Lifecycle

```
1. DRAFT      → Author creates artifact, no signature
2. PROPOSED   → Author requests approval, pending signature
3. ACTIVE     → Signed by authorized role, in effect
4. RESOLVED   → Work complete, archived with evidence
5. STINKY     → Blocked or problematic, needs attention
```

## Naming Convention

```
{artifact_type}_{descriptive_name}_v{version}.yaml
```

Examples:
- `mission_qa_excellence_v1.yaml`
- `flow_automated_regression_v2.yaml`
- `track_pr_coverage_gap_v1.yaml`
- `brief_prkin_v1.yaml`

## Validation

Artifacts in this directory:

1. **MUST** conform to schemas in `/schemas/`
2. **MUST** have valid `lineage` block with computed hash
3. **MUST** have `supports_upper_layer` referencing valid parent (except missions)
4. **SHOULD** have `signed_by` referencing role from `/roles/`

## Invariants

- **INV-001:** Every artifact MUST have a stable, unique `id`
- **INV-003:** Every non-mission artifact MUST reference exactly one upstream artifact
- **INV-004:** Every artifact MUST include a `lineage.hash` computed from its content
- **INV-005:** Every non-mission artifact's `lineage.upstream_hash` MUST match its parent's `lineage.hash`

## Tooling (Planned)

```bash
# Validate an artifact
cheddar validate artifacts/example/missions/mission_qa_v1.yaml

# Compute and update lineage hash
cheddar hash artifacts/example/briefs/brief_prkin_v1.yaml

# Verify chain integrity
cheddar verify-chain artifacts/example/
```

## Example Artifacts

See `/schemas/examples/` for canonical artifact examples that can be copied as templates.

## Next Steps

1. Create example artifact chain demonstrating full hierarchy
2. Implement validation tooling in `lint/`
3. Add pre-commit hooks for artifact validation
