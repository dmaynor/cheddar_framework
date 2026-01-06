# Examples Directory

**Status:** `[PLANNED]` — Structure defined, initial example pending

## Purpose

This directory contains **end-to-end examples** demonstrating complete Cheddar workflows — from mission definition through execution and evidence capture.

## Planned Structure

```
examples/
├── README.md                    # This file
├── qa_excellence/               # Example: QA transformation story
│   ├── README.md                # Narrative walkthrough
│   ├── artifacts/               # Complete artifact chain
│   │   ├── mission_qa_excellence.yaml
│   │   ├── flow_automated_regression.yaml
│   │   ├── track_pr_coverage_gap.yaml
│   │   ├── brief_prkin.yaml
│   │   └── personal_alice_implement.yaml
│   ├── evidence/                # Execution evidence
│   │   ├── run_2026_01_06.yaml
│   │   └── metrics.yaml
│   └── logs/                    # Documentation logs
│       └── documentation_log.yaml
└── compliance_training/         # Example: Non-engineering workflow
    ├── README.md
    ├── artifacts/
    └── evidence/
```

## Example: QA Excellence Story

This example demonstrates a complete Cheddar workflow for implementing automated regression testing with PRkin.

### Narrative

1. **Mission**: Board defines QA excellence as strategic priority
2. **Initiative**: VP Engineering commits to automated regression coverage
3. **Track**: QA Lead identifies PR coverage gap as key problem
4. **Brief**: ML Platform Lead defines PRkin automation contract
5. **Personal**: Engineer implements and validates the tool
6. **Evidence**: Execution metrics prove success criteria met

### Artifact Chain

```
mission_qa_excellence.yaml
    │
    └── flow_automated_regression.yaml
            │
            └── track_pr_coverage_gap.yaml
                    │
                    └── brief_prkin.yaml
                            │
                            └── personal_alice_implement.yaml
```

### Lineage Verification

Each artifact's `lineage.upstream_hash` matches its parent's `lineage.hash`, creating an unbroken chain of accountability.

```bash
# Verify chain integrity
cheddar verify-chain examples/qa_excellence/artifacts/
```

## Using Examples

### As Templates

Copy example artifacts and modify for your use case:

```bash
cp -r examples/qa_excellence/artifacts/ my_project/
# Edit artifacts to match your context
```

### As Test Fixtures

Load examples in tests:

```python
from pathlib import Path
import yaml

example_dir = Path("examples/qa_excellence/artifacts")
mission = yaml.safe_load((example_dir / "mission_qa_excellence.yaml").read_text())
```

### As Documentation

Read the README.md in each example for a narrative walkthrough of the workflow.

## Creating New Examples

1. Create a new directory under `examples/`
2. Add `README.md` with narrative walkthrough
3. Create `artifacts/` with complete chain
4. Add `evidence/` with execution results
5. Verify chain integrity with lint tools

## Example Checklist

- [ ] README.md explains the story
- [ ] All artifact types represented
- [ ] Lineage chain is valid
- [ ] Evidence demonstrates success criteria
- [ ] Documentation log shows progress

## Next Steps

1. Complete `qa_excellence` example with full artifacts
2. Add `compliance_training` non-engineering example
3. Create walkthrough videos/documentation
