# Cheddar Framework

Cheddar is a PM/accountability framework for AI-augmented organizations. It aligns missions, initiatives, tasks, and automation through signed, traceable artifacts that humans and AI share.

## Repository Status

| Component | Status |
|-----------|--------|
| Domain model | EXISTS |
| Invariants | EXISTS |
| JSON Schemas | PARTIAL (now enforcing SHA256) |
| Validation tooling | PARTIAL (strict mode added) |
| Examples | PARTIAL (lineage normalized) |
| Python package | PLANNED |

## Current State

- Deterministic hashing (metadata-safe)
- Strict linting path (no silent bypass)
- Full SHA256 enforcement across schemas
- Example chain uses real lineage hashes

## Meta-Rule

Cheddar must never claim reality it cannot enforce.
