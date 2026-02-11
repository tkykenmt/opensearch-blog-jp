#!/usr/bin/env python3
"""Review translated article with automated checks and AI review."""
import argparse
import json
import subprocess
from pathlib import Path
from lib.state import get_work_dir, load_checkpoint, save_checkpoint, list_work_slugs
from lib.zenn import get_translated_path
from lib.review_checks import run_all_checks, format_issues

def run_ai_review(slug: str, save: bool = False) -> tuple[int, str]:
    """Run Kiro reviewer agent on translated article. Returns (returncode, output)."""
    translated = get_translated_path(slug)
    prompt = f"{translated} をレビューしてください"
    print(f"\n🤖 Starting Kiro AI review...")
    result = subprocess.run(
        ["kiro-cli", "chat", "--agent", "reviewer",
         "--no-interactive", "-a", prompt],
        cwd=Path(__file__).parent,
        capture_output=save, text=save,
    )
    output = result.stdout or "" if save else ""
    if save and output:
        review_path = get_work_dir(slug) / "review.md"
        review_path.write_text(output)
        print(f"📝 AI review saved to {review_path}")
    return result.returncode, output

def main():
    parser = argparse.ArgumentParser(description="Review translated article")
    parser.add_argument("--slug", help="Article slug (default: latest)")
    parser.add_argument("--list", action="store_true", help="List available slugs")
    parser.add_argument("--no-ai", action="store_true", help="Skip AI review")
    parser.add_argument("--no-save", action="store_true", help="Don't save review results")
    args = parser.parse_args()
    
    if args.list:
        slugs = list_work_slugs()
        if slugs:
            print("Available slugs:")
            for s in slugs:
                cp = load_checkpoint(s)
                print(f"  {s} [{cp.get('status', 'unknown')}]")
        else:
            print("No work directories found")
        return
    
    # Find slug
    slug = args.slug
    if not slug:
        slugs = list_work_slugs()
        if not slugs:
            print("❌ No work directories found. Run translate.py first.")
            return
        slug = slugs[-1]  # Latest
        print(f"Using latest: {slug}")
    
    # Check translated file exists
    translated = get_translated_path(slug)
    if not translated.exists():
        print(f"❌ Translated file not found: {translated}")
        print("   Run Kiro translator agent first to create translated.md")
        return
    
    content = translated.read_text()
    images_dir = get_work_dir(slug) / "images"
    
    # Step 1: Automated checks
    print(f"🔍 Reviewing: {translated}")
    issues = run_all_checks(content, images_dir, slug=slug)
    print(format_issues(issues))
    
    # Save check results
    save = not args.no_save
    if save:
        checks_path = get_work_dir(slug) / "review_checks.json"
        checks_data = [{"level": i.level, "check": i.check, "message": i.message,
                        "line": i.line, "suggestion": i.suggestion} for i in issues]
        checks_path.write_text(json.dumps(checks_data, ensure_ascii=False, indent=2))
        print(f"📝 Check results saved to {checks_path}")
    
    # Step 2: AI review
    if not args.no_ai:
        rc, _ = run_ai_review(slug, save=save)
        if rc != 0:
            print(f"\n❌ AI review failed (exit code: {rc})")
            raise SystemExit(rc)
    
    # Update checkpoint
    checkpoint = load_checkpoint(slug)
    checkpoint["status"] = "reviewed"
    checkpoint["review_errors"] = len([i for i in issues if i.level == "error"])
    checkpoint["review_warnings"] = len([i for i in issues if i.level == "warning"])
    save_checkpoint(slug, checkpoint)
    
    if not any(i.level == "error" for i in issues):
        print(f"\n✅ Ready for publish")
        print(f"   Next: python publish.py --slug {slug}")
    else:
        print(f"\n❌ Fix errors before publishing")

if __name__ == "__main__":
    main()
