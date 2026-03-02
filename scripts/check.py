#!/usr/bin/env python3
"""Run automated review checks on translated article."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import json
from pathlib import Path
from lib.state import get_work_dir, load_checkpoint, save_checkpoint, list_work_slugs
from lib.zenn import get_translated_path
from lib.review_checks import run_all_checks, format_issues


def main():
    parser = argparse.ArgumentParser(description="Run automated review checks")
    parser.add_argument("--slug", help="Article slug (default: latest)")
    args = parser.parse_args()

    slug = args.slug
    if not slug:
        slugs = list_work_slugs()
        if not slugs:
            print("❌ No work directories found")
            return
        slug = slugs[-1]

    translated = get_translated_path(slug)
    if not translated.exists():
        print(f"❌ {translated} not found")
        return

    content = translated.read_text()
    images_dir = get_work_dir(slug) / "images"

    issues = run_all_checks(content, images_dir, slug=slug)
    print(format_issues(issues))

    # Save results
    checks_path = get_work_dir(slug) / "review_checks.json"
    checks_data = [{"level": i.level, "check": i.check, "message": i.message,
                    "line": i.line, "suggestion": i.suggestion} for i in issues]
    checks_path.write_text(json.dumps(checks_data, ensure_ascii=False, indent=2))

    checkpoint = load_checkpoint(slug)
    checkpoint["review_errors"] = len([i for i in issues if i.level == "error"])
    checkpoint["review_warnings"] = len([i for i in issues if i.level == "warning"])
    save_checkpoint(slug, checkpoint)


if __name__ == "__main__":
    main()
