# Cheddar Domain Model

This document defines the canonical entities, relationships, and terminology for the Cheddar framework. All other documentation defers to this file for authoritative definitions.

---

## Terminology

### Framework vs. Artifact Disambiguation

| Term | Meaning | Context |
|------|---------|---------|
| **Cheddar Framework** | The complete methodology for AI-augmented accountability | When referring to the system as a whole |
| **Cheddar Track** | A specific artifact type capturing reproducible problems | When referring to `cheddar_track.yaml` artifacts |
| **Cheddar State** | Status enumeration for artifacts: `active`, `resolved`, `stinky` | When referring to the `cheddar_state` field |
| **Cheddar Stats** | Metrics about detected problems in documentation logs | When referring to the `cheddar_stats` block |

### Core Concepts

- **Artifact**: A signed, versioned YAML/JSON file that captures intent, work, or evidence within the accountability chain.
- **Lineage**: The cryptographic chain linking artifacts to their upstream sources and downstream dependents.
- **Alignment Fabric**: The merged context (`combined_context.yaml`) assembled from stacked artifacts that humans and AI consult before acting.
- **Principal Worker**: The human accountable for an artifact's correctness and completion.

---

## Entity Definitions

### 1. Mission Definition

The highest-level artifact defining organizational intent and success criteria.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `level` | string | ✓ | Always `"mission"` |
| `id` | string | ✓ | Stable unique identifier (e.g., `mission_qa_excellence_v1`) |
| `title` | string | ✓ | Snake_case identifier for the mission |
| `intent` | string | ✓ | Natural language statement of organizational purpose |
| `success_criteria` | list | ✓ | Measurable outcomes that define success |
| `authorized_roles` | list | ✓ | Roles permitted to modify this artifact |
| `cheddar_state` | string | | One of: `active`, `resolved`, `stinky` |
| `lineage` | object | ✓ | Cryptographic provenance (see Lineage Block) |

**Relationships:**
- Has no upstream artifact (root of chain)
- Enables one or more `flow_initiative` artifacts

---

### 2. Flow Initiative

Translates mission intent into departmental or system-level objectives.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `level` | string | ✓ | Always `"flow_initiative"` |
| `id` | string | ✓ | Stable unique identifier |
| `title` | string | ✓ | Snake_case identifier |
| `supports_upper_layer` | string | ✓ | ID of parent `mission_definition` |
| `objective` | string | ✓ | Concrete goal statement |
| `constraints` | list | | Guardrails and limitations |
| `telemetry_signals` | list | | Metrics to track progress |
| `enables_lower_layer` | list | | What this initiative makes possible |
| `cheddar_state` | string | | One of: `active`, `resolved`, `stinky` |
| `lineage` | object | ✓ | Cryptographic provenance |

**Relationships:**
- Supports exactly one `mission_definition`
- Enables one or more `cheddar_track` artifacts

---

### 3. Cheddar Track

Captures reproducible problems, hypotheses, and candidate improvements.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `level` | string | ✓ | Always `"cheddar_track"` |
| `id` | string | ✓ | Stable unique identifier |
| `title` | string | ✓ | Snake_case identifier |
| `supports_upper_layer` | string | ✓ | ID of parent `flow_initiative` |
| `issue` | string | ✓ | Description of the problem |
| `hypotheses` | list | | Candidate explanations |
| `repro_steps` | list | | Steps to reproduce the issue |
| `upward_feedback` | string | | Conditions triggering escalation |
| `cheddar_state` | string | | One of: `active`, `resolved`, `stinky` |
| `lineage` | object | ✓ | Cryptographic provenance |

**Relationships:**
- Supports exactly one `flow_initiative`
- Enables one or more `automation_brief` artifacts

---

### 4. Automation Brief

Executable, testable contract binding human sign-off to automation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `level` | string | ✓ | Always `"automation_brief"` |
| `id` | string | ✓ | Stable unique identifier |
| `title` | string | ✓ | Snake_case identifier |
| `supports_upper_layer` | string | ✓ | ID of parent `cheddar_track` |
| `owner` | string | ✓ | Principal worker accountable |
| `deliverables` | list | ✓ | Concrete outputs |
| `tests` | list | ✓ | Validation criteria |
| `change_management` | object | | Approvals and rollback plan |
| `cheddar_state` | string | | One of: `active`, `resolved`, `stinky` |
| `lineage` | object | ✓ | Cryptographic provenance |

**Relationships:**
- Supports exactly one `cheddar_track`
- Enables one or more `personal_artifact` or `run_evidence` artifacts

---

### 5. Personal Artifact

Individual-level work contracts inheriting context from automation briefs or policies.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `level` | string | ✓ | Always `"personal"` |
| `id` | string | ✓ | Stable unique identifier |
| `title` | string | ✓ | Snake_case identifier |
| `supports_upper_layer` | string | ✓ | ID of parent artifact |
| `responsible_party` | string | ✓ | Individual accountable |
| `acceptance_criteria` | list | ✓ | Conditions for completion |
| `cheddar_state` | string | ✓ | One of: `active`, `resolved`, `stinky` |
| `lineage` | object | ✓ | Cryptographic provenance |

**Relationships:**
- Supports exactly one upstream artifact (typically `automation_brief`)
- Terminal node in hierarchy (no downstream artifacts)

---

### 6. Documentation Log

Append-only record of progress, blockers, and decisions.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `last_updated` | string | ✓ | ISO 8601 UTC timestamp |
| `author` | string | ✓ | Human or AI identifier |
| `entries` | list | ✓ | Ordered log entries |

**Entry Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | string | ✓ | ISO 8601 date |
| `summary` | string | ✓ | Brief description of progress |
| `what_we_are_doing` | string | | Current focus |
| `how_we_are_doing_it` | string | | Approach/methodology |
| `blockers` | list | | Current impediments |
| `cheddar_stats` | object | | Problem detection metrics |
| `cheddar_state` | string | | Current state |
| `next_steps` | list | | Planned actions |

---

### 7. Intent Node

Living statement of purpose replacing static tickets. Used in intent graph workflows.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Stable unique identifier |
| `description` | string | ✓ | Purpose statement |
| `dependencies` | list | | IDs of dependent nodes |
| `confidence` | float | | 0.0–1.0 certainty score |
| `entropy` | float | | Uncertainty measure |
| `owner` | string | ✓ | Accountable party |
| `updated_at` | string | ✓ | ISO 8601 timestamp |

**Note:** Intent nodes are a workflow pattern derived from the artifact hierarchy. The hierarchy remains canonical; intent graphs are computed views.

---

## Shared Structures

### Lineage Block

Every artifact includes a `lineage` block for cryptographic traceability.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `upstream_hash` | string | | SHA-256 hash of parent artifact (null for mission) |
| `hash` | string | ✓ | SHA-256 hash of this artifact's content |
| `signed_by` | string | | Role or identity that signed |
| `timestamp` | string | ✓ | ISO 8601 signing timestamp |

### Cheddar Stats Block

Metrics block for documentation logs.

| Field | Type | Description |
|-------|------|-------------|
| `total_cheddars_detected` | int | Total problems identified |
| `aligned_cheddars` | int | Problems with clear upstream traceability |
| `stinky_cheddars` | int | Problems without resolution path |

### Cheddar State Enumeration

| Value | Meaning |
|-------|---------|
| `active` | Work in progress |
| `resolved` | Completed successfully |
| `stinky` | Blocked, stale, or problematic |

---

## Relationship Hierarchy

```
mission_definition
    │
    └──► flow_initiative (1:N)
              │
              └──► cheddar_track (1:N)
                        │
                        └──► automation_brief (1:N)
                                  │
                                  └──► personal_artifact (1:N)
                                  │
                                  └──► run_evidence (1:N)
```

**Canonical Direction:**
- **Downward:** Intent flows from mission to personal artifacts
- **Upward:** Evidence and feedback flow from execution to mission

**Invariant:** The artifact hierarchy is canonical. Intent graphs are derived views computed from artifact relationships, not a separate data structure.

---

## ID Conventions

Artifact IDs follow this pattern:

```
{artifact_type}_{descriptive_name}_v{version}
```

Examples:
- `mission_qa_excellence_v1`
- `flow_automated_regression_v2`
- `track_pr_coverage_gap_v1`
- `brief_prkin_v1`

Version numbers increment on semantic changes to the artifact's intent or contract.

---

## Field Naming Conventions

| Convention | Example | Usage |
|------------|---------|-------|
| Snake_case | `supports_upper_layer` | All field names |
| Snake_case | `reduce_false_positives` | Titles and IDs |
| ISO 8601 | `2026-01-06T00:00:00Z` | All timestamps |
| SHA-256 hex | `sha256:a1b2c3...` | All hashes |

---

## Validation Rules

1. Every artifact MUST have `level`, `id`, `title`, and `lineage` fields
2. Every non-mission artifact MUST have `supports_upper_layer` referencing a valid upstream ID
3. The `lineage.hash` MUST be computed from artifact content excluding the hash field itself
4. The `lineage.upstream_hash` MUST match the parent artifact's `lineage.hash`
5. The `cheddar_state` field, when present, MUST be one of: `active`, `resolved`, `stinky`

---

## Schema Files

Canonical schemas are defined in `/schemas/`:
- `mission_definition.schema.yaml`
- `flow_initiative.schema.yaml`
- `cheddar_track.schema.yaml`
- `automation_brief.schema.yaml`
- `personal_artifact.schema.yaml`
- `documentation_log.schema.yaml`

Example artifacts are in `/schemas/examples/`.
