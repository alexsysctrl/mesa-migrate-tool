#!/usr/bin/env python3
"""Fix Mesa 2.x agent constructors for Mesa 3.x/4.x compatibility.

Mesa 3.x changed Agent constructor:
  2.x: Agent(unique_id, model)
  3.x: Agent(model, ...)  - unique_id is auto-generated

This script converts old patterns to new ones.

Usage:
    python patch_agent_init.py path/to/agents.py [--dry-run]
"""

import sys
import re
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv

# Pattern: super().__init__(unique_id, model) or cls.__init__(unique_id, model)
SUPER_INIT_RE = re.compile(
    r"(self\.|cls\.)__init__\(\s*(\w+)\s*,\s*(\w+)\s*(,\s*.+)?\s*\)"
)

# Pattern: Agent.__init__(self, unique_id, model, ...) in class definitions
AGENT_INIT_RE = re.compile(
    r"def __init__\(\s*self\s*,\s*(unique_id|_id)\s*,\s*(model|_model)\s*(,\s*.+)?\s*\)"
)


def fix_file(filepath: Path):
    content = filepath.read_text()
    original = content

    # Fix super().__init__(unique_id, model, ...) -> super().__init__(model, ...)
    def replace_super_init(match):
        prefix = match.group(1)
        first_arg = match.group(2)
        second_arg = match.group(3)
        rest = match.group(4) or ""
        # If first arg is unique_id/_id and second is model, drop unique_id
        if first_arg in ("unique_id", "_id") and second_arg in ("model", "_model"):
            return f"{prefix}__init__({second_arg}{rest})"
        return match.group(0)

    content = SUPER_INIT_RE.sub(replace_super_init, content)

    # Fix def __init__(self, unique_id, model, ...) -> def __init__(self, model, ...)
    def replace_def_init(match):
        first_arg = match.group(1)
        second_arg = match.group(2)
        rest = match.group(3) or ""
        if first_arg in ("unique_id", "_id") and second_arg in ("model", "_model"):
            return f"def __init__(self, {second_arg}{rest})"
        return match.group(0)

    content = AGENT_INIT_RE.sub(replace_def_init, content)

    # Remove unique_id assignment in __init__ if present
    content = re.sub(r"\s*self\.unique_id\s*=\s*unique_id\n", "\n", content)
    content = re.sub(r"\s*self\.unique_id\s*=\s*_id\n", "\n", content)

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
        print("Usage: python patch_agent_init.py <file.py> [--dry-run]")
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
