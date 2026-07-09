#!/usr/bin/env python3
"""Print the tools needed by the vibe project installer."""

from __future__ import annotations

import sys

from system_dependencies import check_system_dependencies, format_dependency_report


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    checks = check_system_dependencies()
    print(format_dependency_report(checks))
    return 1 if any(check.required and not check.found for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
