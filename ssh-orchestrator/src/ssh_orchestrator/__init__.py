"""ssh-orchestrator: remote security testing orchestrator over SSH.

Loads a signed engagement plan describing authorized targets and modules,
executes commands against those targets over SSH, and writes evidence
artifacts (JSON + raw output, with SHA256 hashes) for every check.

Designed for authorized security testing only: every run requires an
engagement plan with an explicit authorizer, scope expiry, and target
allowlist. Targets not present in the plan are refused.
"""

from __future__ import annotations

__version__ = "0.1.0"
