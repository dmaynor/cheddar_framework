# AI Audit Directory

**Status:** `[REQUIRED]` — Structure defined, implementation pending

## Purpose

This directory contains **AI session logs** — immutable records of AI interactions with Cheddar artifacts, providing transparency and accountability for AI-augmented decision-making.

## Planned Structure

```
ai_audit/
├── README.md                    # This file
├── session_schema.yaml          # [PLANNED] Schema for session logs
└── sessions/                    # [PLANNED] Session log storage
    └── {YYYY}/{MM}/{DD}/
        └── session_{uuid}.yaml
```

## Session Log Schema (Draft)

```yaml
ai_session:
  session_id: "uuid-here"
  timestamp_start: "2026-01-06T10:00:00Z"
  timestamp_end: "2026-01-06T10:15:00Z"
  
  # Context loaded at session start
  context:
    source: "./combined_context.yaml"
    hash: "sha256:abc123..."  # Immutable for session duration
    artifacts_loaded:
      - id: "mission_qa_excellence_v1"
        hash: "sha256:..."
      - id: "flow_automated_regression_v1"
        hash: "sha256:..."
  
  # Agent identity
  agent:
    model: "claude-3-opus"
    version: "2026-01-01"
    session_config:
      temperature: 0.7
      max_tokens: 4096
  
  # Permissions for this session
  permissions:
    read: ["*"]
    write:
      - "append_documentation_logs"
      - "suggest_tests"
    prohibited:
      - "deploy_to_production"
      - "alter_signatures"
      - "modify_lineage"
  
  # Actions taken
  actions:
    - timestamp: "2026-01-06T10:05:00Z"
      type: "read"
      target: "artifacts/missions/mission_qa_v1.yaml"
      
    - timestamp: "2026-01-06T10:10:00Z"
      type: "append"
      target: "documentation_log"
      content_hash: "sha256:..."
      approved_by: null  # AI action, no human approval
      
    - timestamp: "2026-01-06T10:12:00Z"
      type: "suggest"
      target: "tests"
      content_hash: "sha256:..."
      status: "pending_review"
  
  # Session outcome
  outcome:
    status: "completed"
    artifacts_modified: 1
    artifacts_created: 0
    human_approvals_pending: 1
```

## Invariants

- **INV-030:** The assembled context MUST NOT change during an AI session
- **INV-031:** AI write operations MUST be explicitly enumerated in session configuration
- **INV-032:** All AI session operations MUST be logged with artifact hashes

## Retention Policy

| Category | Retention |
|----------|-----------|
| Sessions with write actions | Permanent |
| Sessions with pending approvals | Until resolved + 90 days |
| Read-only sessions | 30 days |

## Query Examples (Planned)

```bash
# Find all sessions that modified a specific artifact
cheddar audit query --artifact "brief_prkin_v1" --action "write"

# List sessions with pending human approvals
cheddar audit query --status "pending_review"

# Verify session context integrity
cheddar audit verify-session sessions/2026/01/06/session_abc123.yaml
```

## Privacy Considerations

- Session logs contain AI interactions, not human conversations
- No PII should be stored in session logs
- Content hashes reference artifacts, not inline content
- Access to audit logs requires appropriate role permissions

## Integration Points

- **Runtime:** Session manager creates logs at session boundaries
- **Governance:** Policy engine checks permissions before AI actions
- **Reporting:** Dashboards aggregate audit data for compliance

## Next Steps

1. Define session log schema in `session_schema.yaml`
2. Implement session logging middleware
3. Create query tooling for audit analysis
4. Integrate with governance policy engine
