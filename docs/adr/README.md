# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the Cheddar framework.

## What Are ADRs?

ADRs document significant architectural decisions along with their context and consequences. They provide a historical record of why the framework is designed the way it is.

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](ADR-001-hierarchy-is-canonical.md) | Artifact Hierarchy is Canonical | Accepted | 2026-01-06 |

## ADR Template

When creating a new ADR, use this structure:

```markdown
# ADR-NNN: Title

**Status:** Proposed | Accepted | Deprecated | Superseded  
**Date:** YYYY-MM-DD  
**Deciders:** Who made this decision  

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Rationale
Why is this decision being made?

## Consequences
What becomes easier or more difficult because of this change?

## Alternatives Considered
What other options were evaluated?

## References
Links to related documents, issues, or discussions.
```

## Statuses

- **Proposed:** Under discussion, not yet accepted
- **Accepted:** Decision has been made and is in effect
- **Deprecated:** Decision is no longer relevant
- **Superseded:** Replaced by a newer ADR (link to replacement)

## Contributing

To propose a new ADR:

1. Copy the template above
2. Assign the next sequential number
3. Fill in all sections
4. Submit for review
5. Update this index when accepted
