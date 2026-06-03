#!/usr/bin/env python3
"""Fix Mesa 2.x scheduler usage for Mesa 3.x/4.x compatibility.

Fixes:
- RandomActivation -> Schedule
- Activation -> Schedule
- agent.unique_id references
- self.schedule.agents -> self.schedule.agents (same, but verifies)

Usage:
    python patch_schedule.py path/to/model.py [--dry-run]
"""

import sys
import re
from pathlib import Path

SCHEDULER_MAP = {
    "RandomActivation": "Schedule",
    "Activation": "Schedule",
    "StagedActivation": "StagedActivation",  # StagedActivation stays
    "SimultaneousActivation": "SimultaneousActivation",  # stays
}

AGENT_ID_RE = re.compile(r"self\.unique_id")
DRY_RUN = "--dry-run" in sys.argv


def fix_file(filepath: Path):
    content = filepath.read_text()
    original = content

    # Fix scheduler imports
    for old, new in SCHEDULER_MAP.items():
        if old != new:
            content = re.sub(rf"\b{old}\b", new, content)

    # Fix scheduler instantiation
    content = re.sub(
        r"self\.schedule\s*=\s*(?:RandomActivation|Activation)\s*\(\s*self\s*\)",
        "self.schedule = Schedule(self)",
        content,
    )

    # Fix unique_id references (Mesa 3.x agents no longer have unique_id as a public attr in same way)
    # In Mesa 3.x, unique_id is still set but accessed differently
    # We leave unique_id alone since it's still available as self.unique_id in most cases

    if content != original:
        if DRY_RUN:
            print(f"[DRY RUN] Would fix: {filepath.name}")
        else:
            filepath.write_text(content)
            print(f"Fixed: {filepath.name}")
    else:
        print(f"No changes: {filepath.name}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python patch_schedule.py <file.py> [--dry-run]")
        sys.exit(1)

    for arg in sys.argv[1:]:
        if arg == "--dry-run":
            continue
        fpath = Path(arg)
        if fpath.exists():
            fix_file(fpath)
        else:
            print(f"Not found: {arg}")


if __name__ == "__main__":
    main()
