"""Manifest & Asset Validation Utility (YVP-SYS-002).

Delegates to pipeline.intake.validator to validate a production's asset-manifest.json
and registered managed media copies.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.intake.cli import main  # noqa: E402

if __name__ == "__main__":
    argv = sys.argv[1:]
    if not argv or argv[0] not in {"intake", "validate", "list", "inspect", "report"}:
        argv = ["validate"] + argv
    sys.exit(main(argv))
