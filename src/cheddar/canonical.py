"""Canonical artifact hashing utilities."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


def strip_runtime_metadata(value: Any) -> Any:
    """Return value with runtime-only metadata keys removed recursively."""
    if isinstance(value, dict):
        return {
            key: strip_runtime_metadata(item)
            for key, item in value.items()
            if not str(key).startswith("_")
        }

    if isinstance(value, list):
        return [strip_runtime_metadata(item) for item in value]

    return value


def canonicalize_for_hash(artifact: dict[str, Any]) -> dict[str, Any]:
    """Return the canonical artifact structure used as hash input."""
    content = strip_runtime_metadata(copy.deepcopy(artifact))

    if "lineage" in content and "hash" in content["lineage"]:
        del content["lineage"]["hash"]

    if "documentation_log" in content:
        log = content["documentation_log"]
        if "lineage" in log and "hash" in log["lineage"]:
            del log["lineage"]["hash"]

    return content


def compute_hash(artifact: dict[str, Any]) -> str:
    """Compute a Cheddar lineage hash for an artifact."""
    content = canonicalize_for_hash(artifact)
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def with_computed_hash(artifact: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of artifact with lineage.hash set to the computed hash."""
    result = copy.deepcopy(artifact)
    result.setdefault("lineage", {})["hash"] = compute_hash(result)
    return result
