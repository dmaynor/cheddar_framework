# Canonical Serialization for Lineage Hashing

**Status:** Specification (Tier 0) — normative for `lineage.hash` computation.
**Applies to:** All Cheddar artifact types (mission, flow, track, brief, personal, documentation_log).
**Related invariants:** INV-004, INV-005, INV-023.

---

## Why This Exists

Cheddar's accountability chain depends on content hashes matching across authors, tools, and time. YAML is the authoring format, but YAML serialization is **not deterministic** — key order, quoting style, number formatting, and comments all vary across tools. Hashing the raw YAML bytes would produce different hashes for artifacts that are semantically identical.

This document specifies the one canonical form that MUST be used for computing `lineage.hash`.

> **Rule:** If two artifacts are semantically equal under this spec, their hashes MUST be equal. If they are not semantically equal, their hashes MUST differ.

---

## The Algorithm

To compute `lineage.hash` for an artifact:

1. **Load** the YAML file in safe mode (no custom tags, no code execution). Any YAML loader is acceptable so long as the [§ Type Rules](#type-rules) below are enforced after loading; differences between YAML 1.1 and 1.2 implicit-resolution behavior are absorbed there. Implementations MUST reject artifacts whose loaded value tree contains any disallowed type.
2. **Strip** the `lineage.hash` field (and only that field) from the tree. For `documentation_log` artifacts, strip `documentation_log.lineage.hash`.
3. **Normalize** the tree per the rules in [§ Type Rules](#type-rules) below.
4. **Serialize** the normalized tree to **canonical JSON** per [§ Canonical JSON](#canonical-json) below.
5. **Encode** the canonical JSON as UTF-8 bytes.
6. **Compute** `SHA-256` over those bytes.
7. **Format** the result as `sha256:<64 lowercase hex chars>`.

The result is the value of `lineage.hash`.

Verification is step-equivalent: recompute and compare.

---

## Type Rules

These are the only value types allowed in an artifact's content after normalization. Anything else is a spec violation and MUST cause the hash tool to exit non-zero.

| Type | Representation | Notes |
|---|---|---|
| **Object / mapping** | JSON object | Keys MUST be strings. |
| **Array / sequence** | JSON array | Order is preserved — arrays are ordered by author intent. |
| **String** | JSON string | See [§ String Normalization](#string-normalization). |
| **Integer** | JSON number with no decimal point or exponent | e.g. `24`, `-1`, `0`. |
| **Boolean** | `true` / `false` | |
| **Null** | `null` | Explicit nulls are preserved (they carry meaning, e.g. `upstream_hash: null` on missions). |

### Prohibited types

- **Floating-point numbers** (`1.0`, `0.95`, `1e3`).
  - Cheddar artifacts currently contain no floats. This spec **prohibits** them at the hashing boundary because JSON's float serialization is not deterministic across languages.
  - If a threshold needs a decimal, express it as a **string** (e.g. `target: ">0.95"` as already used in `schemas/examples/automation_brief.example.yaml`) or as a scaled integer (e.g. `basis_points: 9500`).
- **YAML timestamps / dates as native objects.** All timestamps and dates MUST be quoted strings that match the `iso8601_timestamp` / `iso8601_date` patterns in `schemas/common.schema.json`. (The YAML parser must not auto-convert them to `datetime` objects. Use `yaml.safe_load` — which respects quoting — and keep timestamps quoted in source.)
- **YAML tags** (`!!set`, `!!binary`, custom tags). Out of scope.
- **Non-string mapping keys** (integers, booleans as keys).
- **Anchors and aliases** (`&foo`, `*foo`). The parser MUST resolve them before hashing; authoring artifacts with anchors is discouraged because it makes diffs harder to review.
- **NaN, Infinity.** Would imply floats anyway; prohibited.
- **YAML 1.1 implicit booleans** (`yes`, `no`, `on`, `off`, `Y`, `N`). Only the literals `true` and `false` resolve to booleans. Authors MUST quote any string that looks like a YAML 1.1 boolean (e.g. `value: "no"`) so it remains a string regardless of loader version. Validators MUST reject unquoted occurrences.
- **YAML 1.1 octal / sexagesimal numerics** (`0o17`, `01:02:03`). Only base-10 integer literals are recognized as integers; anything else MUST be a quoted string.

### Loader-version safety

Different YAML loaders disagree on implicit scalar resolution (PyYAML's `safe_load` uses YAML 1.1 rules; some libraries default to 1.2). The Type Rules above are written so that any loader operating in safe mode produces the same in-memory tree *for conforming artifacts*: every value either falls in the allowed set unambiguously across versions, or the artifact MUST be rejected. Authors MUST quote scalars that resolve differently under YAML 1.1 vs 1.2; validators MUST refuse artifacts that would be ambiguous.

### String Normalization

All strings MUST be Unicode **NFC-normalized** before serialization. **This includes mapping keys**, not only values — keys are strings per the type table above, and inconsistent normalization of a key produces a different sort order and therefore a different hash. Rationale: two visually identical strings composed differently (e.g. precomposed `é` vs. `e` + combining acute) would otherwise hash differently.

Whitespace inside strings is preserved exactly as authored. Leading/trailing whitespace is not stripped.

### Hash Exclusion Rule

Only the `lineage.hash` field itself is excluded from the hash input. Every other field — including `lineage.upstream_hash`, `lineage.signed_by`, `lineage.timestamp`, `enables_lower_layer`, and `upward_feedback` — is part of the content hash.

Consequence: re-signing an artifact (changing `signed_by` or `timestamp`) produces a new hash and therefore a new version. This is intentional.

---

## Canonical JSON

Cheddar uses a narrow, Python-`json`-compatible subset of RFC 8785 JCS. For the value types permitted above, this subset is byte-for-byte interoperable with `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`.

Rules:

1. **UTF-8, no BOM.**
2. **Keys sorted ascending by Unicode code point** at every object level.
3. **No insignificant whitespace** — separators are exactly `,` and `:` (no spaces).
4. **Strings** use JSON string escapes. Non-ASCII characters are emitted as literal UTF-8 bytes (`ensure_ascii=False`), not `\uXXXX` escapes. Rationale: prevents hash drift when tools disagree on which characters need escaping.
5. **Integers** are emitted as their decimal representation without leading zeros or trailing `.0`.
6. **Booleans and null** are `true`, `false`, `null`.
7. **No trailing newline.**

### Why this subset instead of full RFC 8785

Full JCS requires IEEE-754 number serialization per ECMA-262, which is painful to implement and only matters if floats are in scope. By prohibiting floats at the schema boundary, the remaining rules collapse to what `json.dumps` already produces deterministically in any mainstream language.

If floats are ever introduced (see [§ Future Extensions](#future-extensions)), this spec MUST be upgraded to full JCS.

---

## Reference Implementation

This specification is the normative source for `lineage.hash` computation. The current reference implementation is `lint/compute_hash.py`; tooling in other languages MUST conform to this spec and match the canonical bytes produced for the [§ Test Vectors](#test-vectors) below. The current `lint/compute_hash.py` is not yet conformant — see [§ Gaps in the current `lint/compute_hash.py`](#gaps-in-the-current-lintcompute_hashpy) — and is being updated to match in Tier 1.

Minimal Python reference:

```python
import copy, hashlib, json, unicodedata
import yaml

def _normalize(node):
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if not isinstance(k, str):
                raise TypeError(
                    f"prohibited mapping-key type: {type(k).__name__}; "
                    "keys MUST be strings (see Type Rules)"
                )
            out[unicodedata.normalize("NFC", k)] = _normalize(v)
        return out
    if isinstance(node, list):
        return [_normalize(v) for v in node]
    if isinstance(node, str):
        return unicodedata.normalize("NFC", node)
    # bool is a subclass of int — check it first to avoid hashing True as 1
    if isinstance(node, bool) or node is None:
        return node
    if isinstance(node, int):
        return node
    raise TypeError(f"prohibited value type for hashing: {type(node).__name__}")

def compute_hash(artifact: dict) -> str:
    content = copy.deepcopy(artifact)
    # strip lineage.hash (standard artifacts)
    if "lineage" in content:
        content["lineage"].pop("hash", None)
    # strip documentation_log.lineage.hash (log wrapper)
    if "documentation_log" in content and "lineage" in content["documentation_log"]:
        content["documentation_log"]["lineage"].pop("hash", None)

    normalized = _normalize(content)
    canonical = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"

def load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
```

### Gaps in the current `lint/compute_hash.py`

The current implementation (at the time this spec was written) covers rules 1, 2, 3, 5, 6, 7 but does NOT yet enforce:

- **NFC string normalization** (rule in [§ String Normalization](#string-normalization)).
- **Prohibited-type rejection** — it will silently hash floats or YAML datetimes if they appear.
- **`ensure_ascii=False`** — it currently accepts the `json.dumps` default of `ensure_ascii=True`, which is deterministic but needs to be made explicit so non-ASCII strings hash identically across languages.

These MUST be fixed before `lineage.hash` is used as a trust boundary. Tracked as part of Tier 1 package work.

---

## Test Vectors

Reference artifacts and their expected hashes. Any implementation of this spec MUST reproduce these exactly.

> These vectors will be materialized as golden files under `tests/fixtures/hash_vectors/` when the Python package lands (Tier 1). Until then, they are illustrative; the canonical vectors will be generated from `schemas/examples/` by the reference implementation and checked in alongside.

### Vector A — minimal mission

Input (YAML):

```yaml
level: "mission_definition"
id: "mission_test_v1"
title: "test"
intent: "smoke test for hashing"
success_criteria:
  - "hash is stable"
authorized_roles:
  - "vp_of_engineering"
cheddar_state: "active"
lineage:
  upstream_hash: null
  signed_by: "vp_of_engineering"
  timestamp: "2026-01-06T00:00:00Z"
```

Canonical JSON (the bytes that get SHA-256'd):

```
{"authorized_roles":["vp_of_engineering"],"cheddar_state":"active","id":"mission_test_v1","intent":"smoke test for hashing","level":"mission_definition","lineage":{"signed_by":"vp_of_engineering","timestamp":"2026-01-06T00:00:00Z","upstream_hash":null},"success_criteria":["hash is stable"],"title":"test"}
```

### Vector B — NFC normalization

Two strings that MUST hash identically:

- `"café"` (`cafe` + U+0301 combining acute) → normalized to `"café"` (U+00E9)
- `"café"` (literal `é`)

Both MUST produce the same final hash when substituted for any string field. A conforming implementation MUST fail Vector A's hash if it does not perform NFC.

### Vector C — prohibited-type rejection

An artifact containing a YAML float (e.g. `canary_percentage: 0.05` instead of `canary_percentage: 5`) MUST cause `compute_hash` to raise and the CLI to exit non-zero with a clear error. No hash is emitted.

---

## Operational Rules

### Authoring

- Quote all timestamps and dates in YAML (`"2026-01-06T00:00:00Z"`, not `2026-01-06T00:00:00Z`) so the parser returns strings.
- Do not use YAML anchors (`&`, `*`) in artifact files.
- Use integers for counts and scaled fixed-point values; use strings for anything with a decimal point.
- Do not rely on key order for semantics — the canonical form re-sorts everything.

### Tooling

- `cheddar hash <file>` — compute and display.
- `cheddar hash <file> --update` — write the computed value back into `lineage.hash`.
- `cheddar hash <file> --verify` — fail non-zero if stored ≠ computed.
- Pre-commit hook MUST run `--verify` on every changed artifact.
- CI MUST run `cheddar verify-chain` on the full artifact tree.

### Version of this spec

This spec is **v1.0**. Breaking changes to the algorithm require a new version and a new hash prefix (e.g. `sha256-v2:`), plus a documented migration (see ADR-002).

---

## Future Extensions

These are **out of scope for v1.0** and listed only so authors don't accidentally rely on them:

- **Floats.** If a future schema needs native floats, this spec must be upgraded to full RFC 8785 JCS and tools must migrate in lockstep.
- **Binary blobs.** If artifacts need to reference binary content, they SHOULD reference a content-addressed URI (e.g. `sha256:...`) rather than inline base64; the URI is a string and fits the current rules.
- **Hash algorithm agility.** The `sha256:` prefix leaves room for future algorithms (`blake3:`, etc.). Adding a new algorithm is a v2 change; mixed-algorithm chains are prohibited.

---

## References

- `docs/invariants.md` — INV-004, INV-005, INV-023
- `docs/adr/ADR-002-lineage-evolution.md` — how hashes change across revisions and migrations
- `schemas/common.schema.json` — `sha256_hash`, `iso8601_timestamp`, `iso8601_date` definitions
- `lint/compute_hash.py` — reference implementation
- RFC 8785 — JSON Canonicalization Scheme (aspirational superset)
- Unicode Standard Annex #15 — Unicode Normalization Forms (NFC)

---

## Revision History

| Date | Change |
|------|--------|
| 2026-04-24 | Initial specification (v1.0). |
