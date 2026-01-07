# Cheddar Framework — Next Steps Plan

**Date:** 2026-01-07  
**Status:** Post-Refactor Planning  
**Author:** Claude + Violator Actual  

---

## Executive Summary

Phases 0-6 established the Cheddar Framework's foundation: domain model, invariants, schemas, and validation tooling. The framework is now **specification-complete** and **mechanically verifiable**.

This plan outlines the path from specification to production-ready implementation.

---

## What's Done

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 0 | Ground truth audit | ✓ Complete |
| 1 | Domain model + invariants | ✓ Complete |
| 2 | Directory structure | ✓ Complete |
| 3 | JSON Schemas (7 files) | ✓ Complete |
| 4 | ADR-001 (hierarchy canonical) | ✓ Complete |
| 5 | Naming consistency | ✓ Complete |
| 6 | Lint tooling (4 scripts) | ✓ Complete |

**Current Capabilities:**
- Validate any artifact against JSON Schema
- Compute and verify lineage hashes
- Verify chain integrity across artifact sets
- Detect orphaned artifacts and circular references

---

## What Remains

### Tier 1: Core Infrastructure (Blocks Everything Else)

#### 1.1 Python Package Structure
**Priority:** P0  
**Effort:** 2-3 hours  
**Blocks:** CLI, tests, integrations

Create proper Python package in `src/cheddar/`:

```
src/cheddar/
├── __init__.py
├── cli.py              # Click-based CLI
├── core/
│   ├── __init__.py
│   ├── artifact.py     # Artifact dataclasses
│   ├── lineage.py      # Hash/chain utilities
│   └── schema.py       # Schema loading
├── lint/
│   ├── __init__.py
│   ├── validate.py     # Refactored from lint/
│   ├── hash.py
│   └── chain.py
└── py.typed            # PEP 561 marker
```

**Acceptance Criteria:**
- [ ] `pip install -e .` works from repo root
- [ ] `cheddar validate <file>` works from CLI
- [ ] `cheddar hash <file>` works from CLI
- [ ] `cheddar verify-chain <dir>` works from CLI
- [ ] 100% type annotations on public APIs

#### 1.2 Test Suite Foundation
**Priority:** P0  
**Effort:** 2-3 hours  
**Blocks:** CI/CD, confidence in changes

```
tests/
├── conftest.py         # Fixtures loading schemas/examples/
├── test_validate.py    # Schema validation tests
├── test_hash.py        # Hash computation tests
├── test_chain.py       # Chain verification tests
└── fixtures/
    ├── valid/          # Known-good artifacts
    └── invalid/        # Known-bad artifacts (for negative tests)
```

**Acceptance Criteria:**
- [ ] `pytest` runs green
- [ ] Coverage > 80% on lint modules
- [ ] Negative test cases for each invariant
- [ ] CI runs tests on every push

---

### Tier 2: Developer Experience

#### 2.1 Pre-commit Hooks
**Priority:** P1  
**Effort:** 1 hour  
**Depends on:** 1.1

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: cheddar-validate
        name: Validate Cheddar artifacts
        entry: cheddar validate
        language: python
        files: '\.yaml$'
        types: [yaml]
```

**Acceptance Criteria:**
- [ ] `pre-commit install` works
- [ ] Invalid artifacts block commits
- [ ] Hash mismatches block commits

#### 2.2 GitHub Actions CI
**Priority:** P1  
**Effort:** 1-2 hours  
**Depends on:** 1.2

Create `.github/workflows/ci.yml`:

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - run: pytest --cov=cheddar
      - run: cheddar validate schemas/examples/
```

**Acceptance Criteria:**
- [ ] CI badge in README
- [ ] Tests run on every PR
- [ ] Example validation runs on every PR

#### 2.3 Documentation Site
**Priority:** P2  
**Effort:** 2-3 hours  
**Depends on:** 1.1

Options:
- MkDocs with Material theme
- Sphinx with autodoc
- Simple GitHub Pages from `docs/`

**Acceptance Criteria:**
- [ ] API reference generated from docstrings
- [ ] Getting started guide
- [ ] Hosted at GitHub Pages or similar

---

### Tier 3: Production Features

#### 3.1 Signature Verification
**Priority:** P1  
**Effort:** 4-6 hours  
**Enforces:** INV-023

Implement `lint/verify_signature.py`:

```python
def verify_signature(artifact: dict, keyring: Path) -> bool:
    """Verify artifact signature against public keys in keyring."""
    ...
```

**Design Decisions Needed:**
- Key format (GPG, age, minisign?)
- Keyring structure
- Signature embedding format

**Acceptance Criteria:**
- [ ] Can verify signed artifacts
- [ ] Rejects unsigned artifacts when policy requires signature
- [ ] Integrates with `run_all.py`

#### 3.2 Freshness Checking
**Priority:** P2  
**Effort:** 2-3 hours  
**Enforces:** INV-011

Implement `lint/check_freshness.py`:

```python
def check_freshness(artifact: dict, policy: dict) -> bool:
    """Check if artifact was updated within policy threshold."""
    ...
```

**Policy Example:**
```yaml
freshness:
  mission_definition: 90  # days
  flow_initiative: 30
  cheddar_track: 14
  automation_brief: 7
  personal_artifact: 3
```

**Acceptance Criteria:**
- [ ] Detects stale artifacts based on lineage.timestamp
- [ ] Configurable thresholds per artifact type
- [ ] Outputs warnings vs errors based on severity

#### 3.3 State Transition Validation
**Priority:** P2  
**Effort:** 2-3 hours  
**Enforces:** INV-041

Implement `lint/validate_state.py`:

```python
VALID_TRANSITIONS = {
    "active": ["resolved", "stinky"],
    "resolved": ["active"],  # Can reopen
    "stinky": ["active", "resolved"],
}

def validate_transition(old_state: str, new_state: str) -> bool:
    ...
```

**Acceptance Criteria:**
- [ ] Validates state transitions are legal
- [ ] Requires explicit state in all artifacts
- [ ] Integrates with `run_all.py`

---

### Tier 4: Integration & Ecosystem

#### 4.1 PRkin Integration
**Priority:** P1  
**Effort:** 4-6 hours  
**Depends on:** 1.1

Connect PRkin output to Cheddar artifacts:

```yaml
# PRkin run manifest (Cheddar format)
level: "run_evidence"
id: "run_prkin_2026_01_07_v1"
supports_upper_layer: "brief_prkin_v1"
execution:
  timestamp: "2026-01-07T10:00:00Z"
  duration_sec: 45
  exit_code: 0
outputs:
  - path: "features/login.feature"
    hash: "sha256:..."
lineage:
  upstream_hash: "sha256:..."
  hash: "sha256:..."
  timestamp: "2026-01-07T10:00:45Z"
```

**Acceptance Criteria:**
- [ ] PRkin emits Cheddar-format run manifest
- [ ] Run manifest links to automation_brief
- [ ] Lineage chain verifiable from mission to evidence

#### 4.2 Jira/GitHub Issue Bridge
**Priority:** P3  
**Effort:** 6-8 hours  
**Depends on:** 1.1, 3.1

Bidirectional sync between Cheddar artifacts and external trackers:

```
cheddar_track.yaml <---> Jira Issue
automation_brief.yaml <---> GitHub Issue
personal_artifact.yaml <---> Jira Subtask
```

**Design Decisions Needed:**
- Sync direction (one-way vs bidirectional)
- Conflict resolution strategy
- Field mapping

**Acceptance Criteria:**
- [ ] Can create Jira issue from cheddar_track
- [ ] Can update artifact from Jira changes
- [ ] Lineage preserved across sync

#### 4.3 Dashboard / Visualization
**Priority:** P3  
**Effort:** 8-12 hours  
**Depends on:** 1.1

Web UI showing:
- Artifact hierarchy visualization
- Lineage chain explorer
- Freshness/staleness heatmap
- Cheddar stats aggregation

**Options:**
- Streamlit (fastest)
- FastAPI + React (most flexible)
- Static site generator (simplest deployment)

---

### Tier 5: Documentation & Examples

#### 5.1 Use Cases Document
**Priority:** P1  
**Effort:** 2-3 hours  

Create `docs/use-cases.md` with workflows for:
- Board member reviewing mission alignment
- VP Engineering creating initiative
- QA Lead tracking a problem
- Engineer accepting a personal artifact
- AI agent proposing changes

**Acceptance Criteria:**
- [ ] Each persona has concrete workflow
- [ ] Workflows reference actual artifact examples
- [ ] Shows CLI commands for each step

#### 5.2 End-to-End Example
**Priority:** P1  
**Effort:** 3-4 hours  
**Depends on:** 6.0 complete

Create `examples/qa_excellence/`:

```
examples/qa_excellence/
├── README.md                    # Narrative walkthrough
├── artifacts/
│   ├── mission_qa_excellence_v1.yaml
│   ├── flow_automated_regression_v1.yaml
│   ├── track_pr_coverage_gap_v1.yaml
│   ├── brief_prkin_v1.yaml
│   └── personal_alice_implement_v1.yaml
├── evidence/
│   └── run_prkin_2026_01_07_v1.yaml
└── verify.sh                    # Script to validate entire chain
```

**Acceptance Criteria:**
- [ ] Complete chain from mission to evidence
- [ ] All hashes computed and valid
- [ ] `verify.sh` passes
- [ ] README tells the story

#### 5.3 Video Walkthrough
**Priority:** P3  
**Effort:** 2-3 hours  

Record:
- 5-minute "What is Cheddar?"
- 10-minute "Creating your first artifact chain"
- 15-minute "Integrating Cheddar with your workflow"

---

## Recommended Sequence

```
Week 1: Foundation
├── Day 1-2: Python package (1.1)
├── Day 3-4: Test suite (1.2)
└── Day 5: Pre-commit + CI (2.1, 2.2)

Week 2: Documentation & Examples
├── Day 1-2: Use cases document (5.1)
├── Day 3-4: End-to-end example (5.2)
└── Day 5: Update all READMEs

Week 3: Production Features
├── Day 1-2: Signature verification (3.1)
├── Day 3: Freshness checking (3.2)
├── Day 4: State transition validation (3.3)
└── Day 5: Integration testing

Week 4: Integration
├── Day 1-3: PRkin integration (4.1)
├── Day 4-5: Documentation site (2.3)
```

---

## Quick Wins (< 1 hour each)

1. **Add CI badge to README** — visibility
2. **Create `examples/minimal/`** — simplest possible chain (2 artifacts)
3. **Add `--verbose` flag to lint tools** — better debugging
4. **Create `CONTRIBUTING.md`** — community guidelines
5. **Add `make lint` target** — convenience wrapper

---

## Deferred / Out of Scope

| Item | Reason |
|------|--------|
| Web UI dashboard | Premature; CLI-first |
| Jira integration | Needs design decisions |
| Multi-repo support | Complexity; single-repo first |
| Real-time sync | Polling sufficient initially |
| Role-based access control | Needs auth infrastructure |

---

## Success Metrics

| Milestone | Metric |
|-----------|--------|
| Package installable | `pip install` works |
| Tests passing | `pytest` green, >80% coverage |
| CI operational | Badge shows passing |
| Examples complete | Full chain validates |
| PRkin integrated | Run manifests link to briefs |

---

## Files to Create

```
.github/workflows/ci.yml
.pre-commit-config.yaml
CONTRIBUTING.md
Makefile
docs/use-cases.md
examples/qa_excellence/README.md
examples/qa_excellence/artifacts/*.yaml
examples/qa_excellence/verify.sh
examples/minimal/README.md
examples/minimal/mission.yaml
examples/minimal/brief.yaml
src/cheddar/__init__.py
src/cheddar/cli.py
src/cheddar/core/__init__.py
src/cheddar/core/artifact.py
src/cheddar/core/lineage.py
src/cheddar/core/schema.py
src/cheddar/lint/__init__.py
tests/conftest.py
tests/test_validate.py
tests/test_hash.py
tests/test_chain.py
tests/fixtures/valid/*.yaml
tests/fixtures/invalid/*.yaml
```

---

## Appendix: Invariant Coverage

| Invariant | Enforced By | Status |
|-----------|-------------|--------|
| INV-001 (stable ID) | `validate_artifact.py` | ✓ |
| INV-002 (versioning) | `validate_artifact.py` | ✓ |
| INV-003 (upstream ref) | `validate_artifact.py`, `verify_lineage.py` | ✓ |
| INV-004 (hash) | `compute_hash.py` | ✓ |
| INV-005 (chain) | `verify_lineage.py` | ✓ |
| INV-010 (append-only) | `validate_log.py` | Planned |
| INV-011 (freshness) | `check_freshness.py` | Planned |
| INV-012 (author) | `validate_log.py` | Planned |
| INV-020 (human owner) | `validate_artifact.py` | ✓ |
| INV-021 (no AI deploy) | Policy engine | Planned |
| INV-022 (no bypass) | Policy engine | Planned |
| INV-023 (signatures) | `verify_signature.py` | Planned |
| INV-030 (context immutable) | Runtime | Planned |
| INV-031 (AI write perms) | Runtime | Planned |
| INV-032 (audit log) | Runtime | Planned |
| INV-040 (valid state) | `validate_artifact.py` | ✓ |
| INV-041 (transitions) | `validate_state.py` | Planned |
| INV-050 (single canonical) | ADR-001 | ✓ (by design) |
| INV-051 (intent flows down) | Architecture | ✓ (by design) |
| INV-052 (evidence flows up) | Architecture | ✓ (by design) |

---

## Next Action

**Recommended:** Start with 1.1 (Python Package Structure) — it unblocks everything else and gives you a proper `cheddar` CLI command.

```bash
# First command to run
mkdir -p src/cheddar/core src/cheddar/lint
touch src/cheddar/__init__.py src/cheddar/py.typed
```
