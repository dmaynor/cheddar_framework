# ADR-002: Lineage Evolution — Revisions, Forks, and Schema Migrations

**Status:** Accepted
**Date:** 2026-04-24
**Deciders:** Framework architects
**Related:** ADR-001, INV-001, INV-002, INV-004, INV-005, `docs/canonical-serialization.md`

---

## Context

ADR-001 established that the artifact hierarchy is canonical and that `supports_upper_layer` + `lineage.upstream_hash` together form the accountability chain. But the framework has not specified how the chain evolves over time. In practice, artifacts change:

1. **Revisions** — an owner fixes a typo in a mission's `intent`, tightens an acceptance criterion on a brief, or adds a new test. The artifact keeps the same conceptual ID stem, but its full versioned `id` (`_v1` → `_v2`) and its content both change.
2. **Forks** — one team copies another team's brief as a starting point for a different initiative. The two artifacts diverge from a shared ancestor but belong to different chains.
3. **Schema migrations** — the framework adds a required field (e.g. `risk_tier`) to a schema. Every existing artifact now has a different canonical serialization and therefore a different hash.
4. **Retirements** — a mission is superseded by a new mission. Downstream work continues under the new mission; the old chain must not silently rot.

Without a decision here, the first real edit orphans every descendant, the first schema migration invalidates every hash, and forks have no documented relationship to their origin.

---

## Decision

Adopt four well-defined lifecycle operations — **revise**, **fork**, **migrate**, **supersede** — and require artifacts to record the operation that produced them.

### Principles

1. **A signed `id` is immutable.** A specific versioned `id` (e.g. `brief_retrain_v2`) never changes once signed. A revision creates a *new* artifact with the same ID stem and a higher version suffix; the prior versioned `id` remains in the repository as history. Renaming a stem is not an operation — if the intent changes enough to want a new stem, the correct operation is `supersede`.
2. **Hashes are content-exact.** Any content change (per `docs/canonical-serialization.md`) produces a new hash. There is no "soft edit."
3. **Version suffixes encode revisions.** The `_v1` / `_v2` suffix in the `id` field (INV-002) is the one place where "same artifact, new content" is expressed.
4. **Chain continuity is preserved explicitly.** Every evolution operation leaves an explicit pointer so that a verifier can walk both forward and backward in time.

### The Four Operations

#### 1. Revision (`revise`)

A revision replaces an artifact with a new version that supersedes the prior version in-place. The ID increments (`_v1` → `_v2`). Descendants MUST re-point to the new version on the next edit; they are not required to re-point immediately.

**New fields (in `lineage`):**

- `supersedes: <prior_id>` — the previous version's full ID.
- `supersedes_hash: sha256:...` — the previous version's `lineage.hash`.

**Constraints:**

- The new artifact's `supports_upper_layer` MUST equal the prior version's `supports_upper_layer` (a revision cannot change parents — that would be a fork).
- The new `id` MUST have the same stem and a strictly greater version suffix.
- Both versions remain in the repository. The prior version is not deleted; its `cheddar_state` MAY be set to `resolved` or left as-is for historical queries.

**Descendant handling:**

Descendants of the prior version continue to validate against the prior version's hash until they themselves are revised. When a descendant revises, it MUST point to the newest live version of its parent. A lint rule (`cheddar verify-chain --stale-parents`) reports descendants pointing at superseded parents so teams can schedule the catch-up.

#### 2. Fork (`fork`)

A fork creates a new artifact seeded from another artifact's content but belonging to a different chain. Forks are the correct operation when another team wants a similar brief under their own initiative.

**New fields (in `lineage`):**

- `forked_from: <source_id>` — the source artifact's full ID.
- `forked_from_hash: sha256:...` — the source artifact's `lineage.hash` at the time of fork.

**Constraints:**

- The fork has a **different** `id` stem (not just a version bump).
- The fork's `supports_upper_layer` MUST point to the forker's chosen parent, which is typically different from the source's parent.
- `forked_from` is informational for lineage queries; it does NOT participate in hash-chain verification. The fork starts a fresh chain rooted at its own `supports_upper_layer`.

**Why forks don't participate in chain verification:** `lineage.upstream_hash` expresses "this work is accountable to that parent." A fork's work is accountable to its new parent, not to the source it was seeded from. Conflating the two would make the chain a graph and break ADR-001.

#### 3. Migration (`migrate`)

A migration rewrites an artifact's content to conform to a new schema version without changing its intent. Migrations happen in batches (when the framework ships a schema upgrade), not one-off.

**New fields (in `lineage`):**

- `migrated_from_hash: sha256:...` — the content hash before migration.
- `migrated_schema_version: "1.2"` — the schema version the artifact now conforms to.

**Constraints:**

- The `id` does NOT change. Migration is a content transformation, not a revision of intent. (If intent changes, use revise.)
- Migrations are performed by a named, checked-in script under `lint/migrations/<from>-<to>.py`. Ad-hoc migrations are prohibited.
- A migration script MUST be deterministic: running it twice on the same input produces identical output.
- After migration, descendants' `upstream_hash` fields are **stale by design**. A companion step of the migration script re-points each descendant to the migrated parent's new hash and records `migrated_from_hash` on each descendant too. The whole batch is one atomic commit.
- The migration commit message MUST reference the migration script and the schema version delta.

**Why migrations need special handling:** without this, a routine schema upgrade would appear to every verifier as a mass lineage-tampering event. The `migrated_from_hash` field lets verifiers confirm "yes, the old hash is the one the migration script expected to see."

#### 4. Supersede (`supersede`)

Supersede retires an artifact and replaces it with a different artifact (different `id` stem). Used when a mission pivots or an initiative is absorbed into another.

**New fields (in `lineage`):**

- `superseded_by: <successor_id>` on the retiring artifact.
- `supersedes: <predecessor_id>` on the successor (same field as revise, different usage).

**Constraints:**

- The retiring artifact's `cheddar_state` MUST be set to `resolved` (work concluded) or a new value `retired` if the work was abandoned (see [§ Open Questions](#open-questions)).
- The successor is a fresh artifact with no inherited hash chain. Descendants do NOT auto-migrate — each descendant must be explicitly revised to point at the successor.
- Supersede differs from revise in that the ID stem changes. It differs from fork in that the original is retired, not preserved as a parallel branch.

---

## Decision Matrix

| Scenario | Operation | ID changes? | Chain continuity? |
|---|---|---|---|
| Typo fix in `intent` | revise | `_v1` → `_v2` | Preserved via `supersedes` |
| Add a test to a brief | revise | `_v1` → `_v2` | Preserved via `supersedes` |
| Another team copies our brief | fork (by the other team) | Different stem | New chain |
| Schema adds a required field | migrate | Unchanged | Preserved via `migrated_from_hash` |
| Mission renamed | *not allowed as rename* — use supersede | Different stem | New chain; old one retired |
| Initiative absorbed into another | supersede | Different stem | Old chain retired |
| Work paused indefinitely | cheddar_state → `stinky` | Unchanged | Preserved |
| Work completed | cheddar_state → `resolved` | Unchanged | Preserved |

---

## Rationale

**Why four operations instead of one.** A single "edit" verb would either break chains (content changed, hash changed, descendants orphaned) or silently rehash everything (loses the audit trail). Splitting the verb by intent makes the verifier's job mechanical: given an artifact, it knows which sibling fields must be present and what invariants hold.

**Why revisions keep the same parent.** If a revision could change `supports_upper_layer`, there'd be no difference between revise and fork — both would be "new content, possibly new parent." Keeping parent stability orthogonal from content revision preserves ADR-001's single source of truth.

**Why forks don't hash-chain to their source.** Accountability is one-parent. A fork is accountable to its new chain; its source is historical context. Treating `forked_from` as informational keeps the chain a tree.

**Why migrations are batched and scripted.** One-off hand-migrations would be impossible to verify. A named script is a signed contract: "this transformation was applied to these artifacts at this time." A reviewer can replay it.

**Why supersede exists separately.** Revise handles same-identity edits; fork handles divergence without retirement; migrate handles schema-driven rewrites. Renaming or retiring an artifact is none of these, so it gets its own verb.

---

## Consequences

### Positive

- **First real edit doesn't orphan descendants.** Lint tooling can distinguish "stale parent" (OK until the descendant revises) from "broken chain" (never OK).
- **Schema evolution is a first-class concern.** Migrations are reviewable, replayable, and auditable.
- **Forks are documented without polluting the hash chain.** Lineage queries can follow `forked_from` for archaeology without ADR-001 fragmenting.
- **Renames are not a rabbit hole.** There is no rename; there is supersede. This keeps IDs stable per INV-001.

### Negative

- **Four operations is more surface area than one.** Tooling must know about all four. Authors must pick the right verb.
- **Descendant catch-up is deferred, not automatic.** A revised parent can coexist with descendants still pointing at its previous hash. Acceptable, but reports are required so teams see what's drifting.
- **Migration scripts become part of the repository's permanent history.** Deleting one breaks the audit trail for anything that went through it. Treat `lint/migrations/` as append-only.

### Mitigations

- `cheddar verify-chain` gains `--stale-parents` and `--broken-chain` as distinct failure modes.
- A `cheddar evolve <op>` CLI helper generates the correct `lineage` fields for each operation so authors don't hand-compose them.
- Migration scripts ship with a test harness under `tests/migrations/` that asserts idempotency and round-trip invariants.

---

## Implementation

### Schema changes

Extend `schemas/common.schema.json#/definitions/lineage` with optional fields. All new fields are **optional** on read to preserve backward compatibility; `cheddar validate` requires the appropriate combination based on the operation declared.

```yaml
lineage:
  # Existing fields
  upstream_hash: "sha256:..." | null
  hash: "sha256:..."
  signed_by: "role_id"
  timestamp: "2026-04-24T00:00:00Z"

  # Revision / supersede (choose at most one of supersedes / forked_from)
  supersedes: "brief_retrain_classifier_v1"          # optional
  supersedes_hash: "sha256:..."                       # required if supersedes is set

  # Fork
  forked_from: "brief_retrain_classifier_v1"          # optional
  forked_from_hash: "sha256:..."                      # required if forked_from is set

  # Migration
  migrated_from_hash: "sha256:..."                    # optional; set by migration scripts
  migrated_schema_version: "1.2"                      # required if migrated_from_hash is set

  # Supersede (on the retiring artifact)
  superseded_by: "brief_retrain_classifier_new_v1"    # optional
```

Exactly one of `{supersedes, forked_from, migrated_from_hash}` MAY be present per `lineage` block (or none, for a first-revision artifact). `superseded_by` is independent and appears on the retiring artifact, not the successor.

### Validation rules

- `supersedes` requires `supersedes_hash`; the hash MUST resolve to an artifact with ID `supersedes` that exists in the repository.
- `forked_from` requires `forked_from_hash`; same resolution rule.
- `migrated_from_hash` requires `migrated_schema_version` and a matching entry in `lint/migrations/` whose "from" schema version matches the artifact's previous state.
- `superseded_by` requires the referenced artifact to exist and to declare `supersedes` pointing back to this artifact (bidirectional integrity).

### Tooling

- `cheddar evolve revise <path>` — bump version, populate `supersedes` / `supersedes_hash`, compute new `hash`.
- `cheddar evolve fork <source_path> <new_id> <new_parent>` — create forked artifact with `forked_from` / `forked_from_hash`.
- `cheddar evolve supersede <path> <successor_path>` — set `superseded_by` on retiring, `supersedes` on successor.
- `cheddar migrate <from> <to>` — runs `lint/migrations/<from>-<to>.py` across the tree and produces one atomic commit.
- `cheddar verify-chain --stale-parents` — non-zero exit if any descendant points at a superseded parent.

### Rollout

- **Now (this ADR):** document the operations. Extend `common.schema.json` with optional fields. No existing artifact is affected because all new fields are optional.
- **Tier 1:** implement `cheddar evolve` subcommands in the package alongside basic CLI.
- **Tier 3:** implement `cheddar migrate` and land the first migration script (likely `1.0` → `1.1` when a schema changes).

---

## Alternatives Considered

### Alternative 1: "Rehash on every edit"

Every edit produces a new hash; descendants break until re-signed. Forces catch-up but is brutal at scale and provides no distinction between revisions, forks, and migrations.

**Rejected because:** conflates four operationally distinct scenarios, makes schema upgrades impossible without repo-wide stop-the-world events, and loses the audit trail.

### Alternative 2: "Mutable artifacts, external version store"

Keep artifact content editable, store versioned snapshots in a separate DB.

**Rejected because:** violates "YAML files are the system" (ADR-001 consequence), adds infrastructure, makes git history a misleading partial record.

### Alternative 3: "Hash a stable subset of fields"

Compute `lineage.hash` only over fields declared "substantive" (e.g. `intent`, `deliverables`) and ignore editorial fields (`title`, comments).

**Rejected because:** introduces an ambiguous boundary (what counts as substantive?), makes "same hash, different content" possible, and weakens tamper detection.

### Alternative 4: "No forks — always create from scratch"

Forbid `forked_from`; require that every artifact be authored fresh.

**Rejected because:** forks happen regardless — the question is whether we record them. Undocumented copies are worse than documented ones.

---

## Open Questions

- **Retired vs. resolved state.** `cheddar_state` currently supports `{active, resolved, stinky}`. Supersede implies a fourth state — `retired` (work abandoned, not completed). This ADR flags the need; actual schema change is deferred to an INV-040 update proposal.
- **Cross-chain dependency.** If Brief A depends on data produced by Brief B under a different initiative, there's no field to record that today. Out of scope for this ADR; see potential future `depends_on` proposal.
- **Migration script signing.** Should migration scripts themselves be signed artifacts? Probably yes, but adds complexity; deferred to Tier 3 when signature verification lands.

---

## References

- `docs/adr/ADR-001-hierarchy-is-canonical.md` — foundational hierarchy decision
- `docs/canonical-serialization.md` — hash algorithm (v1.0)
- `docs/invariants.md` — INV-001, INV-002, INV-004, INV-005, INV-040
- `schemas/common.schema.json` — lineage block definition

---

## Revision History

| Date | Change |
|------|--------|
| 2026-04-24 | Initial decision recorded. |
