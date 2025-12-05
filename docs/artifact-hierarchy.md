# Artifact Hierarchy

Cheddar aligns organizations with a chain of signed artifacts. Context flows downward; evidence and feedback flow upward.

```
board_of_directors
  ↓
mission_definition.yaml        # company intent + KPIs
  ↓
flow_initiative.yaml           # departmental / system objectives
  ↓
cheddar_track.yaml             # reproducible problems + improvement ideas
  ↓
automation_brief.yaml          # executable, testable automation contracts
  ↓
personal_artifact.yaml         # individual tasks / compliance / learning
```

## Mission Definition
Defines organizational intent and measurable success.

```yaml
level: "mission"
title: "develop_best_vulnerability_scanner"
intent: "Deliver a best-of-breed scanner with superior accuracy and minimal false positives."
success_criteria:
  - market_share: "maintain_or_grow"
  - false_positive_rate: "<2_percent"
authorized_roles:
  - role_name: "board_of_directors"
```

## Flow Initiative
Translates mission into system or departmental objectives with clear guardrails.

```yaml
level: "flow_initiative"
title: "reduce_false_positives"
supports_upper_layer: "develop_best_vulnerability_scanner"
objective: "Lower false-positive rate below 2%."
constraints:
  - "Maintain detection precision > 95%"
  - "No additional licensing costs"
telemetry_signals: ["false_positive_rate", "precision", "mean_time_to_triage"]
```

## Cheddar Track
Captures reproducible problems, hypotheses, and candidate improvements.

```yaml
level: "cheddar_track"
title: "classifier_threshold_adjustment"
issue: "Model threshold drift detected"
hypotheses:
  - "Threshold too aggressive on new dataset"
repro_steps:
  - "Replay telemetry window 2025-10-01–2025-10-07"
  - "Compare ROC curves against baseline"
upward_feedback: "Escalate if drift persists across 3 releases"
```

## Automation Brief
Executable, testable contract that binds human sign-off to automation.

```yaml
level: "automation_brief"
title: "retrain_model_with_recent_telemetry"
owner: "ml_platform_lead"
deliverables:
  - "Updated model weights"
  - "Passing regression tests"
tests:
  - "false_positive_rate_below_2_percent"
  - "precision_above_95_percent"
change_management:
  approvals_required: ["vp_of_engineering"]
  rollback_plan: "Revert to prior model if precision drops"
```

## Personal Artifact
Individual-level work contracts that inherit context from automation briefs or policies.

```yaml
level: "personal"
title: "complete_security_training"
supports_upper_layer: "maintain_customer_trust_and_regulatory_compliance"
responsible_party: "employee_123"
acceptance_criteria:
  - "Training quiz score >= 90%"
  - "Signed acknowledgement recorded"
cheddar_state: "active"
```

Each artifact layer contributes to a closed accountability loop that makes intent, execution, and evidence mechanically traceable.
