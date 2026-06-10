"""Shared test setup for the Cheddar test suite.

The lint scripts are not yet packaged under src/cheddar/ (see
docs/NEXT_STEPS.md Tier 1), so tests import them by adding lint/ to
sys.path. When the package refactor lands, these imports should move to
the cheddar package and this path shim should be deleted.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LINT_DIR = REPO_ROOT / "lint"
SRC_DIR = REPO_ROOT / "src"
EXAMPLES_DIR = REPO_ROOT / "schemas" / "examples"

if str(LINT_DIR) not in sys.path:
    sys.path.insert(0, str(LINT_DIR))

# Make src/cheddar importable without an editable install, so the
# cross-implementation equivalence test activates as soon as a package
# hashing module exists (see test_canonical_hash.py).
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
