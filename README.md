# Cheddar Framework

Cheddar is a PM/accountability framework for AI-augmented organizations. It aligns missions, initiatives, tasks, and automation through signed, traceable artifacts that humans and AI share.

## Quick Start

1. **Understand the model**: Read [`docs/domain-model.md`](docs/domain-model.md)
2. **Know the rules**: Review [`docs/invariants.md`](docs/invariants.md)
3. **See examples**: Browse [`schemas/examples/`](schemas/examples/)
4. **Explore docs**: Dive into `docs/`

## Validate (quick check)

Run:

```bash
python lint/run_all.py --examples --strict
```

Expected: all checks pass.

## Documentation Map

### Core Reference
- docs/domain-model.md
- docs/invariants.md
- schemas/

### Guides
- docs/overview.md
- docs/artifact-hierarchy.md
- docs/ai-integration.md

## Repository Status

| Component | Status |
|-----------|--------|
| Domain model | EXISTS |
| Invariants | EXISTS |
| Schemas | PARTIAL (SHA256 enforcement added) |
| Validation tooling | PARTIAL (strict mode added) |
| Examples | PARTIAL (lineage normalized) |
| Python package | PLANNED |

## Current Reality

- Deterministic hashing (metadata-safe)
- Strict linting (no silent bypass)
- Full SHA256 enforcement across schemas
- Example lineage chains use real hashes

## Meta-Rule

Cheddar must never claim reality it cannot enforce.
