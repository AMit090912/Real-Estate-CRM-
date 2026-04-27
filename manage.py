#!/usr/bin/env python
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VENDOR = BASE_DIR / "vendor"
if VENDOR.exists():
    sys.path.insert(0, str(VENDOR))


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "estatecrm.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
