# Governance Directory

**Status:** `[REQUIRED]` — Structure defined, implementation pending

## Purpose

This directory contains **governance policy definitions** — the rules that govern how Cheddar artifacts are created, modified, approved, and enforced.

## Planned Structure

```
governance/
├── README.md                    # This file
├── policy.yaml                  # [PLANNED] Main policy configuration
├── policy_schema.yaml           # [PLANNED] Schema for policy files
└── policies/                    # [PLANNED] Additional policy modules
    ├── signing.yaml             # Signature requirements
    ├── freshness.yaml           # Staleness thresholds
    ├── ai_constraints.yaml      # AI permission boundaries
    └── escalation.yaml          # Escalation triggers
```

## Policy Schema (Draft)

```yaml
# policy.yaml - Main governance configuration
policy:
  version: "1.0"
  
  # Documentation freshness requirements
  freshness:
    default_days: 14
    by_artifact_type:
      mission_definition: 90
      flow_initiative: 30
      cheddar_track: 14
      automation_brief: 7
      personal_artifact: 3
  
  # Signature requirements by artifact type
  signatures:
    mission_definition:
      required_roles:
        - "board_of_directors"
      min_approvals: 1
    
    flow_initiative:
      required_roles:
        - "vp_of_engineering"
      min_approvals: 1
    
    automation_brief:
      required_roles:
        - "engineering_manager"
        - "qa_lead"
      min_approvals: 1
      any_of: true  # Any one of the listed roles
  
  # AI constraints
  ai_constraints:
    # What AI can do without human approval
    autonomous_actions:
      - "append_documentation_logs"
      - "suggest_tests"
      - "generate_reports"
    
    # What AI cannot do
    prohibited_actions:
      - "deploy_to_production"
      - "alter_signatures"
      - "modify_lineage"
      - "delete_artifacts"
      - "approve_artifacts"
    
    # Privacy requirements
    sentiment_privacy: true
    append_only: true
    audit_log_required: true
  
  # Violation handling
  violations:
    actions:
      - type: "revoke_ai_write_permissions"
        severity: ["critical", "high"]
      - type: "notify_compliance"
        severity: ["critical", "high", "medium"]
      - type: "log_warning"
        severity: ["low"]
    
    escalation:
      critical: "security_officer"
      high: "vp_of_engineering"
      medium: "engineering_manager"
```

## Policy Enforcement

The governance policy is enforced at multiple points:

| Enforcement Point | Mechanism |
|-------------------|-----------|
| Artifact creation | Schema validation + policy check |
| Artifact modification | Signature verification + policy check |
| AI session start | Permission scoping from policy |
| AI write action | Policy engine approval |
| Deployment gate | Required signatures verification |

## Invariants

- **INV-021:** AI MUST NOT deploy to production without explicit human signature
- **INV-022:** AI MUST NOT bypass governance policy

## Policy Evaluation (Planned)

```python
# Pseudocode for policy evaluation
def evaluate_action(action: Action, policy: Policy, context: Context) -> Decision:
    # Check if action is prohibited
    if action.type in policy.ai_constraints.prohibited_actions:
        return Decision.DENY
    
    # Check if action is autonomous
    if action.type in policy.ai_constraints.autonomous_actions:
        return Decision.ALLOW
    
    # Otherwise, require human approval
    return Decision.REQUIRE_APPROVAL
```

## Integration Points

- **Lint:** Policy validation during artifact checks
- **Runtime:** Policy engine evaluates actions in real-time
- **AI Audit:** Policy decisions logged in session records
- **Dashboards:** Policy compliance metrics

## Next Steps

1. Define policy schema in `policy_schema.yaml`
2. Create default `policy.yaml` configuration
3. Implement policy engine in `src/cheddar/governance/`
4. Integrate with lint and runtime systems
