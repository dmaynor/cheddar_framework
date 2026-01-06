# Cheddar Framework

Cheddar is a PM/accountability framework for AI-augmented organizations. It aligns missions, initiatives, tasks, and automation through signed, traceable artifacts that humans and AI share.

## Quick Start

1. **Understand the model**: Read [`docs/domain-model.md`](docs/domain-model.md) for entity definitions
2. **Know the rules**: Review [`docs/invariants.md`](docs/invariants.md) for non-negotiable guarantees
3. **See examples**: Browse [`schemas/examples/`](schemas/examples/) for canonical artifact formats
4. **Explore concepts**: Dive into the documentation below

## Documentation Map

### Core Reference (Start Here)
- [`docs/domain-model.md`](docs/domain-model.md) — **canonical entity definitions, terminology, and relationships**
- [`docs/invariants.md`](docs/invariants.md) — **non-negotiable rules and enforcement mechanisms**
- [`schemas/`](schemas/) — **canonical artifact schemas and examples**

### Conceptual Guides
- [`docs/overview.md`](docs/overview.md) — purpose, origin, and core philosophies
- [`docs/alignment-fabric.md`](docs/alignment-fabric.md) — how stacked artifacts merge into `combined_context.yaml`
- [`docs/artifact-hierarchy.md`](docs/artifact-hierarchy.md) — mission → initiative → track → automation → personal chain
- [`docs/documentation-governance.md`](docs/documentation-governance.md) — append-only logs, lineage, and dashboard signals
- [`docs/personal-artifacts.md`](docs/personal-artifacts.md) — applying the chain to individual and non-engineering work
- [`docs/ai-integration.md`](docs/ai-integration.md) — AI participation and safeguards across layers
- [`docs/governance-ethics.md`](docs/governance-ethics.md) — ethical guardrails and policy enforcement
- [`docs/intent-graphs.md`](docs/intent-graphs.md) — replacing tickets with intent graph workflows
- [`docs/embodiment.md`](docs/embodiment.md) — embodied QA and sensorimotor participation

### Architecture Decisions
- [`docs/adr/`](docs/adr/) — Architecture Decision Records
- [`docs/adr/ADR-001-hierarchy-is-canonical.md`](docs/adr/ADR-001-hierarchy-is-canonical.md) — **Artifact hierarchy is canonical; intent graphs are derived views**

## Repository Status

| Component | Status | Location |
|-----------|--------|----------|
| Domain model | `[EXISTS]` | `docs/domain-model.md` |
| Invariants | `[EXISTS]` | `docs/invariants.md` |
| Schema examples | `[EXISTS]` | `schemas/examples/` |
| JSON Schema definitions | `[EXISTS]` | `schemas/*.schema.json` |
| Conceptual docs | `[EXISTS]` | `docs/` |
| Architecture decisions | `[EXISTS]` | `docs/adr/` |
| Validation tooling | `[PLANNED]` | `lint/` |
| Example artifacts | `[PLANNED]` | `artifacts/` |
| Python package | `[PLANNED]` | `src/` |

**Status Markers:**
- `[EXISTS]` — Present and functional
- `[REQUIRED]` — Must exist for v1.0
- `[PLANNED]` — Intended future capability

## Meta-Rule

> **Cheddar must never claim reality it cannot enforce.**

See [`docs/invariants.md`](docs/invariants.md) for the complete set of guarantees.
