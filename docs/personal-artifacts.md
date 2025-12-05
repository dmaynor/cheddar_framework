# Personal Artifacts & Context of Contribution

Personal artifacts extend the same alignment chain used by engineering to every department. They keep individual work linked to mission intent and policy.

## How the Chain Applies to People
```
board_of_directors
↓
ceo_mission_definition.yaml
↓
department_flow_initiatives.yaml
↓
team_cheddar_tracks.yaml
↓
automation_or_policy_briefs.yaml
↓
personal_artifacts.yaml
```

## Example: Operations & Compliance
```yaml
# mission_definition.yaml
title: "maintain_customer_trust_and_regulatory_compliance"
intent: "Ensure audit readiness and secure data handling."
success_criteria:
  - soc2_certification: "maintained"
  - employee_training_completion: "100_percent"

# flow_initiative_security_and_trust.yaml
title: "achieve_100_percent_security_training_completion"
supports_upper_layer: "maintain_customer_trust_and_regulatory_compliance"
objective: "Bring all staff to completion and certification."

automation_or_policy_brief.yaml:
  title: "training_completion_enforcement"
  controls:
    - "Weekly reminders via HRIS"
    - "Escalation to manager at day 21"
  tests:
    - "training_completion_rate == 100%"
    - "no_overdue_trainings > 0 triggers escalation"

personal_artifact_employee123.yaml:
  title: "complete_security_training"
  responsible_party: "employee123"
  acceptance_criteria:
    - "Quiz score >= 90%"
    - "Signed acknowledgement recorded"
  cheddar_state: "active"
```

## Alignment Rules
- Every personal artifact inherits upstream context and must be signed by the responsible party.
- Policy briefs define enforcement and tests; personal artifacts prove completion.
- Feedback (blockers, risks, sentiment) rolls upward to refine initiatives and mission goals.
