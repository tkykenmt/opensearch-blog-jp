#!/usr/bin/env python3
"""Show work directory status."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import json
from lib.state import list_work_slugs, load_checkpoint


def main():
    parser = argparse.ArgumentParser(description="Show work status")
    parser.add_argument("--slug", help="Show detail for specific slug")
    args = parser.parse_args()

    if args.slug:
        cp = load_checkpoint(args.slug)
        print(json.dumps(cp, ensure_ascii=False, indent=2))
        return

    slugs = list_work_slugs()
    if not slugs:
        print("No work directories found")
        return

    for s in slugs:
        cp = load_checkpoint(s)
        status = cp.get("status", "unknown")
        title = cp.get("title", "")
        print(f"  {s}  [{status}]  {title}")


if __name__ == "__main__":
    main()
