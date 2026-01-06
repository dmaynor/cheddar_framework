# AGENTS.md — Guidance for Codegen & Agent Tools

This repository holds the **Cheddar framework specification and tooling**. The domain model and schemas are stable; implementation is in progress.

Cheddar is a **cryptographically-linked, self-describing YAML/JSON artifact system** that captures the chain from:
> board-level mission → initiatives → tracks → automation briefs → personal artifacts → evidence

Your job as an agent is to **implement tooling that enforces the specification**.

---

## 1. Overall Intent

**Primary goal:**  
Help implement and evolve Cheddar as a framework for:
- Defining missions, goals, projects, and tasks as structured artifacts.
- Maintaining cryptographic lineage between those artifacts.
- Attaching evidence, metrics, and automation hooks in a way that is auditable and portable across tools.

**Current reality:**  
- The domain model is defined in `docs/domain-model.md` `[EXISTS]`
- Invariants are documented in `docs/invariants.md` `[EXISTS]`
- Canonical schemas exist in `schemas/examples/` `[EXISTS]`
- Tooling implementation is ready to begin `[PLANNED]`

---

## 2. Operating Principles for Agents

When working in this repo, follow these rules:

1. **Specification-first.**  
   - The domain model and invariants are authoritative.
   - Code must conform to specifications, not the other way around.
   - If spec is unclear, clarify in docs before implementing.

2. **Implement against schemas.**  
   - Use artifacts in `schemas/examples/` as test fixtures.
   - Validation must pass for all example artifacts.
   - New artifacts must conform to documented schemas.

3. **Preserve invariants.**  
   - Cheddar is about **alignment, traceability, and cryptographic lineage**.
   - All 20 invariants in `docs/invariants.md` must be respected.
   - Code that would violate invariants must not be merged.

4. **No hidden magic.**  
   - Avoid "black box" abstractions. All transformations should be explainable in English and traceable in the artifacts.
   - If a behavior can't be described plainly, document it first.

5. **Test against fixtures.**  
   - Use example artifacts from `schemas/examples/` as test cases.
   - Tests should verify invariant enforcement.

6. **Write to be read by humans first, agents second.**  
   - Anything you generate should be understandable by a human reading the repo with no prior context.

---

## 3. Current Repo Phase & Priorities

We are in **Phase 2: Stable Specification → Implementation Ready**.

### Completed

| Priority | Status | Location |
|----------|--------|----------|
| Domain model | ✓ `[EXISTS]` | `docs/domain-model.md` |
| Invariants | ✓ `[EXISTS]` | `docs/invariants.md` |
| Schema examples | ✓ `[EXISTS]` | `schemas/examples/` |
| Directory structure | ✓ `[EXISTS]` | All stub directories created |

### In Progress

| Priority | Status | Location |
|----------|--------|----------|
| Validation tooling | `[PLANNED]` | `lint/` |
| Hash computation | `[PLANNED]` | `lint/compute_hash.py` |
| Chain verification | `[PLANNED]` | `lint/verify_lineage.py` |
| CLI interface | `[PLANNED]` | `src/cheddar/cli.py` |
| Use-case documentation | `[PLANNED]` | `docs/use-cases.md` |
| End-to-end examples | `[PLANNED]` | `examples/` |

### Next Steps

1. Implement `lint/validate_artifact.py` — schema validation
2. Implement `lint/compute_hash.py` — lineage hash computation
3. Implement `lint/verify_lineage.py` — chain integrity verification
4. Create CLI wrapper in `src/cheddar/cli.py`
5. Add pytest tests in `tests/`

---

## 4. Languages, Style, and Coding Expectations

Code will eventually exist here. When you add code:

- **Default language:** Python 3.11+.
- **Style:** PEP 8, type-annotated, with full docstrings that explain:
  - What the function/module does.
  - Input/output types and formats.
  - Any assumptions or side effects.

- **Testing:**
  - Use `pytest`.
  - Prefer small, deterministic tests.
  - Drive tests with example Cheddar artifacts from `schemas/examples/`.

- **YAML/JSON artifacts:**
  - Be strict and predictable:
    - Avoid clever magic keys.
    - Make fields explicit (no implicit "magic default" behavior).
  - Fields must match `docs/domain-model.md`.

- **Interfaces:**
  - Prefer **pure functions and small CLIs** over complex frameworks at this stage.
  - Any CLIs should:
    - Accept input files/directories of artifacts.
    - Emit JSON/YAML or markdown reports, not opaque binary blobs.

---

## 5. Directory and File Conventions

The repository now has this structure. Status markers indicate implementation state:

### Core Documentation
- `docs/overview.md` — human-friendly intro to Cheddar. `[EXISTS]`
- `docs/domain-model.md` — entities, relationships, key fields. `[EXISTS]`
- `docs/invariants.md` — core guarantees Cheddar enforces. `[EXISTS]`
- `docs/use-cases.md` — example workflows. `[PLANNED]`
- `docs/roadmap.md` — phased implementation ideas. `[PLANNED]`

### Schemas
- `schemas/README.md` — schema directory documentation. `[EXISTS]`
- `schemas/examples/` — canonical artifact examples. `[EXISTS]`
  - `mission_definition.example.yaml` `[EXISTS]`
  - `flow_initiative.example.yaml` `[EXISTS]`
  - `cheddar_track.example.yaml` `[EXISTS]`
  - `automation_brief.example.yaml` `[EXISTS]`
  - `personal_artifact.example.yaml` `[EXISTS]`
  - `documentation_log.example.yaml` `[EXISTS]`

### Governance Infrastructure
- `roles/` — authority catalog. `[REQUIRED]` stub exists
- `artifacts/` — signed contracts. `[REQUIRED]` stub exists
- `governance/` — policy definitions. `[REQUIRED]` stub exists
- `ai_audit/` — AI session logs. `[REQUIRED]` stub exists

### Implementation
- `lint/` — verification scripts. `[REQUIRED]` stub exists
- `src/cheddar/` — Python package. `[PLANNED]` stub exists
- `tests/` — pytest tests. `[PLANNED]` stub exists
- `examples/` — end-to-end workflows. `[PLANNED]` stub exists

### Status Markers
- `[EXISTS]` — Present and functional
- `[REQUIRED]` — Must exist for v1.0; stub created, implementation pending
- `[PLANNED]` — Intended future capability; stub may exist

When modifying or creating files, **respect existing structure** and prefer extending it over inventing a conflicting pattern.

---

## 6. Agent Workflow Checklist

When invoked on this repo, follow this sequence:

1. **Scan & orient**
   - Read `README.md`, `docs/domain-model.md`, and `docs/invariants.md`.
   - Understand the artifact hierarchy and invariant requirements.

2. **Check existing schemas**
   - Review `schemas/examples/` for canonical artifact formats.
   - Ensure any new code validates against these examples.

3. **Implement incrementally**
   - Start with the smallest useful piece (e.g., single validator).
   - Add tests before expanding scope.
   - Each PR should be reviewable in isolation.

4. **Test against fixtures**
   - Use artifacts from `schemas/examples/` as test cases.
   - Verify both positive cases (valid artifacts) and negative cases (invalid artifacts).

5. **Update documentation**
   - If implementation reveals spec gaps, update docs first.
   - Keep README.md status table current.

6. **Leave the repo better than you found it**
   - Each change set should:
     - Reduce ambiguity.
     - Improve consistency.
     - Move Cheddar closer to being usable.

---

## 7. Things Agents Should NOT Do

- Do **not**:
  - Introduce heavy frameworks (Django, large ORMs, huge dependency trees).
  - Build complex web UIs in this repo at this stage.
  - Introduce vendor-specific integrations (Jira, GitHub, etc.) directly into the core model.
  - Invent opaque state machines without documenting the intent and transitions.
  - Violate invariants defined in `docs/invariants.md`.
  - Change schema field names without updating `docs/domain-model.md`.

- If you feel the urge to:
  - Stop, write a **short design note in `docs/` or a dedicated proposal file**, and keep the implementation small and reversible.

---

## 8. Success Criteria

You are "doing it right" in this repo if:

- A new human can read `docs/overview.md` + `docs/domain-model.md` and understand:
  - What Cheddar is.
  - What artifacts look like.
  - How those artifacts relate to each other.

- The artifact examples are:
  - Valid YAML/JSON.
  - Internally consistent.
  - Usable as fixtures for testing code.

- Any new code:
  - Is small, composable, and well-tested.
  - Operates *on* Cheddar artifacts, rather than redefining them.
  - Enforces invariants from `docs/invariants.md`.
  - Makes it easier to trust and adopt Cheddar, not harder.

- The status markers in docs accurately reflect reality:
  - `[EXISTS]` means it actually exists.
  - `[REQUIRED]` means stub exists, implementation pending.
  - `[PLANNED]` means intended but not yet started.

---

## 9. Key Files Reference

| File | Purpose |
|------|---------|
| `docs/domain-model.md` | **Authoritative** entity definitions |
| `docs/invariants.md` | **Authoritative** enforcement rules |
| `schemas/examples/*.yaml` | **Authoritative** artifact formats |
| `ground_truth_audit.yaml` | Phase 0 audit results |
| `pyproject.toml` | Python package configuration |

---
