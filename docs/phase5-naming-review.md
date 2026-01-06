# Phase 5: Naming Consistency Review

**Date:** 2026-01-06  
**Status:** Complete  

## Summary

Phase 5 reviewed all naming conventions across the repository. Most terminology issues identified in the Phase 0 audit were resolved in Phase 1. This phase made one fix and documented the naming decisions.

---

## Fix Applied

| File | Change |
|------|--------|
| `docs/domain-model.md` | Changed schema references from `.schema.yaml` to `.schema.json` |

---

## Naming Decisions (Documented)

### Artifact Type Names

The following artifact type names are **canonical**:

| Artifact Type | `level` Field Value | ID Prefix | File Naming |
|---------------|---------------------|-----------|-------------|
| Mission Definition | `"mission"` | `mission_` | `mission_*.yaml` |
| Flow Initiative | `"flow_initiative"` | `flow_` | `flow_*.yaml` |
| Cheddar Track | `"cheddar_track"` | `track_` | `track_*.yaml` |
| Automation Brief | `"automation_brief"` | `brief_` | `brief_*.yaml` |
| Personal Artifact | `"personal"` | `personal_` | `personal_*.yaml` |
| Documentation Log | N/A | N/A | `*_log.yaml` |

**Design Decision:** Short forms (`mission`, `personal`) used for `level` field to reduce verbosity in artifacts. Full names used in documentation for clarity.

### Terminology Disambiguation

Resolved in Phase 1 and documented in `docs/domain-model.md`:

| Term | Meaning | Context |
|------|---------|---------|
| Cheddar Framework | The complete methodology | System-level discussion |
| Cheddar Track | Artifact type for reproducible problems | `cheddar_track.yaml` files |
| Cheddar State | Status enumeration | `cheddar_state` field |
| Cheddar Stats | Problem detection metrics | `cheddar_stats` block |

### Field Naming Convention

All fields use **snake_case**:
- `supports_upper_layer` (not `supportsUpperLayer`)
- `cheddar_state` (not `cheddarState`)
- `upstream_hash` (not `upstreamHash`)

### ID Pattern

```
{artifact_type}_{descriptive_name}_v{version}
```

Examples:
- `mission_qa_excellence_v1`
- `flow_automated_regression_v2`
- `track_pr_coverage_gap_v1`
- `brief_prkin_v1`
- `personal_alice_implement_v1`

---

## Items Reviewed (No Changes Needed)

| Category | Status | Notes |
|----------|--------|-------|
| Example artifact field names | ✓ Consistent | All snake_case |
| Schema field names | ✓ Consistent | Match examples |
| ID patterns | ✓ Consistent | Follow `{type}_{name}_v{version}` |
| Documentation terminology | ✓ Consistent | Disambiguation applied |
| Status markers | ✓ Consistent | `[EXISTS]`, `[REQUIRED]`, `[PLANNED]` |

---

## Historical Note

The Phase 0 `ground_truth_audit.yaml` references old artifact type names (`cheddar_mission`, `cheddar_initiative`, `cheddar_task`, `cheddar_evidence`) that were **planned but never implemented**. These names were superseded by the canonical names above during Phase 1.

The audit file is preserved as a historical record of the repository state before the refactor began.

---

## Verification Commands

```bash
# Verify no camelCase fields in examples
grep -rE "[a-z][A-Z]" schemas/examples/*.yaml | grep -v "#"

# Verify consistent level values
grep "^level:" schemas/examples/*.yaml

# Verify ID patterns
grep "^id:" schemas/examples/*.yaml

# Verify schema file extensions
ls schemas/*.schema.json
```

All verifications pass.
