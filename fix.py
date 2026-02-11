#!/usr/bin/env python3
"""Fix translated article based on review results using Kiro fixer agent."""
import argparse
import subprocess
from pathlib import Path
from lib.state import get_work_dir, load_checkpoint, save_checkpoint, list_work_slugs
from lib.zenn import get_translated_path


def main():
    parser = argparse.ArgumentParser(description="Fix translated article based on review")
    parser.add_argument("--slug", help="Article slug (default: latest)")
    parser.add_argument("--list", action="store_true", help="List available slugs")
    args = parser.parse_args()

    if args.list:
        for s in list_work_slugs():
            cp = load_checkpoint(s)
            print(f"  {s} [{cp.get('status', 'unknown')}]")
        return

    slug = args.slug
    if not slug:
        slugs = list_work_slugs()
        if not slugs:
            print("❌ No work directories found.")
            return
        slug = slugs[-1]
        print(f"Using latest: {slug}")

    work = get_work_dir(slug)
    translated = get_translated_path(slug)
    checks = work / "review_checks.json"
    review = work / "review.md"

    if not translated.exists():
        print(f"❌ {translated} not found")
        return

    if not checks.exists() and not review.exists():
        print("❌ No review results found. Run: python review.py --save")
        return

    # Build prompt referencing the review files
    parts = [f"{translated} を以下のレビュー指摘に基づいて修正してください。\n"]
    if checks.exists():
        parts.append(f"自動チェック結果: {checks}")
    if review.exists():
        parts.append(f"AI レビュー結果: {review}")
    prompt = "\n".join(parts)

    print(f"🔧 Fixing {translated} ...")
    result = subprocess.run(
        ["kiro-cli", "chat", "--agent", "fixer", "--no-interactive", "-a", prompt],
        cwd=Path(__file__).parent,
    )

    if result.returncode != 0:
        print(f"❌ Fix failed (exit code: {result.returncode})")
        raise SystemExit(result.returncode)

    checkpoint = load_checkpoint(slug)
    checkpoint["status"] = "fixed"
    save_checkpoint(slug, checkpoint)
    print(f"\n✅ Fix complete. Re-review: python review.py --slug {slug}")


if __name__ == "__main__":
    main()
