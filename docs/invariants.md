# Cheddar Invariants

This document defines the non-negotiable rules that Cheddar enforces. These invariants are mechanical guarantees, not guidelines. Violation of any invariant indicates a broken implementation.

---

## Meta-Invariant

> **Cheddar must never claim reality it cannot enforce.**

Aspirations are documented as `[PLANNED]`. Claims of existence are verified by implementation.

---

## Artifact Invariants

### INV-001: Stable Identity
Every artifact MUST have a stable, unique `id` that does not change across versions.

**Enforcement:** Schema validation on artifact creation.

### INV-002: Explicit Version
Every artifact MUST include a version indicator in its `id` (e.g., `_v1`, `_v2`).

**Enforcement:** ID pattern validation.

### INV-003: Upstream Traceability
Every non-mission artifact MUST reference exactly one upstream artifact via `supports_upper_layer`.

**Enforcement:** Reference resolution validation.

### INV-004: Lineage Hash Integrity
Every artifact MUST include a `lineage.hash` computed from its content (excluding the hash field).

**Enforcement:** Hash verification on load.

### INV-005: Lineage Chain Continuity
Every non-mission artifact's `lineage.upstream_hash` MUST match its parent's `lineage.hash`.

**Enforcement:** Chain verification on context assembly.

---

## Documentation Invariants

### INV-010: Append-Only Logs
Documentation log entries MUST NOT be modified after creation. New information is added as new entries.

**Enforcement:** Log entry immutability checks.

### INV-011: Freshness Enforcement
Documentation logs MUST be updated within the configured evaluation frequency. Stale logs trigger linting failures.

**Enforcement:** `last_updated` timestamp validation.

### INV-012: Author Attribution
Every documentation entry MUST identify its author (human or AI agent).

**Enforcement:** Required field validation.

---

## Governance Invariants

### INV-020: Human Ownership
Every automation MUST have an identified human owner (`principal_worker` or `owner` field).

**Enforcement:** Required field validation on automation artifacts.

### INV-021: Human Production Authority
AI MUST NOT deploy to production without explicit human signature.

**Enforcement:** Signature verification on deployment gates.

### INV-022: AI Policy Compliance
AI MUST NOT bypass governance policy. All AI actions are bounded by `policy.yaml` rules.

**Enforcement:** Policy evaluation before AI write operations.

### INV-023: Signature Verification
Artifacts with `signed_by` claims MUST have verifiable signatures.

**Enforcement:** Cryptographic signature validation.

---

## Session Invariants

### INV-030: Context Immutability
The assembled context (`combined_context.yaml`) MUST NOT change during an AI session.

**Enforcement:** Context hash verification at session boundaries.

### INV-031: Explicit Write Permissions
AI write operations MUST be explicitly enumerated in session configuration.

**Enforcement:** Permission checking before writes.

### INV-032: Audit Trail
All AI session operations MUST be logged to `ai_audit_log` with artifact hashes.

**Enforcement:** Mandatory logging middleware.

---

## State Invariants

### INV-040: Valid State Values
The `cheddar_state` field MUST be one of: `active`, `resolved`, `stinky`.

**Enforcement:** Enumeration validation.

### INV-041: State Transition Rules
State transitions MUST follow valid paths:
- `active` → `resolved` (completion)
- `active` → `stinky` (blocked/problematic)
- `stinky` → `active` (unblocked)
- `resolved` → `active` (reopened)

**Enforcement:** State machine validation.

---

## Hierarchy Invariants

### INV-050: Single Canonical Representation
The artifact hierarchy is the single source of truth. Intent graphs are derived views.

**Enforcement:** No direct intent graph persistence; computed on demand.

### INV-051: Downward Intent Flow
Intent (goals, constraints, success criteria) flows from mission toward personal artifacts.

**Enforcement:** Structural validation of artifact references.

### INV-052: Upward Evidence Flow
Evidence (telemetry, feedback, completion status) flows from execution toward mission.

**Enforcement:** Evidence attachment validation.

---

## Prohibited Actions

### PROHIBIT-001: Retroactive Edits
Modifying historical log entries is prohibited.

### PROHIBIT-002: Unsigned Production Changes
Deploying to production without human signature is prohibited.

### PROHIBIT-003: Policy Bypass
Circumventing governance rules via any mechanism is prohibited.

### PROHIBIT-004: Lineage Falsification
Creating artifacts with false upstream references is prohibited.

### PROHIBIT-005: Identity Spoofing
AI claiming to be a human signer is prohibited.

---

## Enforcement Mechanisms

| Invariant Class | Enforcement Point | Mechanism |
|-----------------|-------------------|-----------|
| Artifact (INV-001–005) | Artifact creation/load | Schema validation, hash verification |
| Documentation (INV-010–012) | Log operations | Append-only storage, field validation |
| Governance (INV-020–023) | Write operations | Policy engine, signature verification |
| Session (INV-030–032) | Session lifecycle | Context hashing, permission middleware |
| State (INV-040–041) | State transitions | State machine validator |
| Hierarchy (INV-050–052) | Context assembly | Reference resolver, structural checks |

---

## Implementation Status

| Invariant | Status | Enforcement Location |
|-----------|--------|---------------------|
| INV-001 | `[PLANNED]` | `lint/validate_artifact.py` |
| INV-002 | `[PLANNED]` | `lint/validate_artifact.py` |
| INV-003 | `[PLANNED]` | `lint/validate_artifact.py` |
| INV-004 | `[PLANNED]` | `lint/compute_hash.py` |
| INV-005 | `[PLANNED]` | `lint/verify_lineage.py` |
| INV-010 | `[PLANNED]` | `lint/validate_log.py` |
| INV-011 | `[PLANNED]` | `lint/check_freshness.py` |
| INV-012 | `[PLANNED]` | `lint/validate_log.py` |
| INV-020 | `[PLANNED]` | `lint/validate_artifact.py` |
| INV-021 | `[PLANNED]` | `governance/deploy_gate.py` |
| INV-022 | `[PLANNED]` | `governance/policy_engine.py` |
| INV-023 | `[PLANNED]` | `lint/verify_signature.py` |
| INV-030 | `[PLANNED]` | `runtime/session_manager.py` |
| INV-031 | `[PLANNED]` | `runtime/session_manager.py` |
| INV-032 | `[PLANNED]` | `runtime/audit_logger.py` |
| INV-040 | `[PLANNED]` | `lint/validate_artifact.py` |
| INV-041 | `[PLANNED]` | `lint/validate_state.py` |
| INV-050 | Documentation only | N/A |
| INV-051 | Documentation only | N/A |
| INV-052 | Documentation only | N/A |

---

## Adding New Invariants

New invariants MUST:
1. Have a unique ID following the pattern `INV-NNN` or `PROHIBIT-NNN`
2. State the rule in unambiguous terms
3. Specify the enforcement mechanism
4. Be added to the implementation status table
5. Not weaken existing invariants

Invariant changes require sign-off from `vp_of_engineering` role.
