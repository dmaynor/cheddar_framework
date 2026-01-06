# Roles Directory

**Status:** `[REQUIRED]` — Structure defined, implementation pending

## Purpose

This directory contains the **authority catalog** — definitions of roles that can sign artifacts and approve changes.

## Planned Contents

```
roles/
├── README.md                    # This file
├── role_schema.yaml             # [PLANNED] Schema for role definitions
└── catalog/                     # [PLANNED] Role definitions
    ├── board_of_directors.yaml
    ├── ceo.yaml
    ├── vp_of_engineering.yaml
    ├── security_officer.yaml
    ├── qa_lead.yaml
    └── ...
```

## Role Definition Schema (Draft)

```yaml
role:
  id: "vp_of_engineering"
  display_name: "VP of Engineering"
  
  # What this role can sign
  signing_authority:
    - artifact_type: "mission_definition"
      permission: "approve"
    - artifact_type: "flow_initiative"
      permission: "create"
    - artifact_type: "automation_brief"
      permission: "approve"
  
  # What this role can delegate
  delegation:
    - to_role: "engineering_manager"
      artifact_types: ["cheddar_track", "automation_brief"]
  
  # Governance constraints
  constraints:
    requires_mfa: true
    max_delegation_depth: 2
```

## Integration Points

- **Artifact Signing:** Artifacts reference roles in `lineage.signed_by`
- **Policy Enforcement:** `governance/policy.yaml` references roles for approval requirements
- **Audit Trail:** `ai_audit/` logs which role authorized AI actions

## Invariants

- **INV-020:** Every automation MUST have an identified human owner
- **INV-023:** Artifacts with `signed_by` claims MUST have verifiable signatures

## Next Steps

1. Define role schema in `role_schema.yaml`
2. Create initial role catalog for common organizational roles
3. Implement signature verification in `lint/verify_signature.py`
