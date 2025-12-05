# AI Integration & Governance Framework

AI in Cheddar is a participant—not a manager. It observes, correlates, and augments while remaining transparent and accountable.

## Responsibilities by Layer
| Layer | AI Responsibilities | Human Responsibilities |
|:--|:--|:--|
| Mission Definition | Aggregate market data and telemetry for KPI validation; generate trend summaries. | Define intent and approve KPI changes. |
| Flow Initiatives | Correlate telemetry signals to detect drift and emerging Cheddars. | Interpret and prioritize findings. |
| Cheddar Tracks | Parse logs, group patterns, and suggest reproducible recipes. | Confirm causality and document impact. |
| Automation Briefs | Generate code/tests; run sandbox simulations. | Review, approve, and sign for production. |
| Personal Artifacts | Assist with reminders and documentation summaries. | Perform actions and sign completion. |

> **AI amplifies cognition; humans own consequence.**

## Prompt & Context Governance
```yaml
ai_session:
  context_source: "./combined_context.yaml"   # immutable for session runtime
  prompt_scope:
    - "mission_definition"
    - "flow_initiative"
    - "cheddar_track"
    - "automation_brief"
  write_permissions:
    - "append_documentation_logs"
    - "suggest_tests"
  prohibited_actions:
    - "deploy_to_production"
    - "alter_signatures"
```

### Safeguards
- AI sessions are logged in `ai_audit_log` with hashes tied to artifacts used.
- Write permissions are explicit and scoped; production changes always require human signatures.
- Context is immutable for the duration of a session to prevent prompt drift.
