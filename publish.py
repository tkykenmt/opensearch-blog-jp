#!/usr/bin/env python3
"""Publish translated article to Zenn via Git."""
import argparse
import shutil
from pathlib import Path
from lib.state import get_work_dir, load_checkpoint, save_checkpoint, list_work_slugs
from lib.zenn import get_translated_path, get_article_path, get_images_dir, check_published
from lib.git import (get_current_branch, create_branch, checkout_branch, 
                     add_files, commit, push, has_changes, delete_local_branch)
from lib.github import create_pr, merge_pr

def main():
    parser = argparse.ArgumentParser(description="Publish article to Zenn")
    parser.add_argument("--slug", help="Article slug")
    parser.add_argument("--branch", help="Branch name (default: article/{slug})")
    parser.add_argument("--no-push", action="store_true", help="Don't push to remote")
    parser.add_argument("--no-merge", action="store_true", help="Create PR but don't merge")
    parser.add_argument("--merge-method", default="squash", choices=["squash", "merge", "rebase"],
                        help="PR merge method (default: squash)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()
    
    # Find slug
    slug = args.slug
    if not slug:
        slugs = list_work_slugs()
        if not slugs:
            print("❌ No work directories found")
            return
        slug = slugs[-1]
        print(f"Using latest: {slug}")
    
    work_dir = get_work_dir(slug)
    translated = get_translated_path(slug)
    
    if not translated.exists():
        print(f"❌ Translated file not found: {translated}")
        return
    
    checkpoint = load_checkpoint(slug)
    title = checkpoint.get("title", slug)
    
    # Paths
    article_path = get_article_path(slug)
    images_src = work_dir / "images"
    images_dst = get_images_dir(slug)
    branch = args.branch or f"article/{slug}"
    
    print(f"📤 Publishing: {title}")
    print(f"   Source: {translated}")
    print(f"   Target: {article_path}")
    
    if args.dry_run:
        print("\n[Dry run - no changes made]")
        print(f"   Would copy: {translated} → {article_path}")
        if images_src.exists():
            print(f"   Would copy: {images_src}/* → {images_dst}/")
        print(f"   Would create branch: {branch}")
        return
    
    # Copy files
    article_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(translated, article_path)
    print(f"   ✓ Copied article")
    
    if images_src.exists() and any(images_src.iterdir()):
        images_dst.mkdir(parents=True, exist_ok=True)
        for img in images_src.iterdir():
            shutil.copy(img, images_dst / img.name)
        print(f"   ✓ Copied {len(list(images_src.iterdir()))} images")
    
    # Git operations
    original_branch = get_current_branch()
    try:
        create_branch(branch)
        print(f"   ✓ Created branch: {branch}")
    except RuntimeError:
        checkout_branch(branch)
        print(f"   ✓ Switched to branch: {branch}")
    
    add_files(str(article_path))
    if images_dst.exists():
        add_files(str(images_dst))
    
    if not has_changes():
        print("   ℹ️  No changes to commit")
        checkout_branch(original_branch)
        return
    
    commit(f"Add article: {title}")
    print(f"   ✓ Committed")
    
    pr = None
    if not args.no_push:
        push(branch)
        print(f"   ✓ Pushed to origin/{branch}")
        
        # Create PR
        try:
            pr = create_pr(branch, f"Add article: {title}")
            print(f"   ✓ Created PR #{pr['number']}: {pr['url']}")
        except RuntimeError as e:
            print(f"   ⚠️  PR creation failed: {e}")
        
        # Merge PR
        merged = False
        if pr and not args.no_merge:
            try:
                merge_pr(branch, method=args.merge_method)
                print(f"   ✓ Merged PR #{pr['number']} ({args.merge_method})")
                merged = True
            except RuntimeError as e:
                print(f"   ⚠️  Merge failed: {e}")
        
        # Return to original branch and clean up
        checkout_branch(original_branch)
        if merged:
            try:
                delete_local_branch(branch)
            except RuntimeError:
                pass
            
            # Check Zenn publication
            print(f"\n🔍 Checking Zenn publication...")
            url = f"https://zenn.dev/opensearch/articles/{slug}"
            if check_published(slug, timeout=180, interval=10):
                print(f"   ✅ Published: {url}")
                checkpoint["status"] = "live"
            else:
                print(f"   ⚠️  Not yet accessible: {url}")
                print(f"      Zenn へのデプロイに時間がかかっている可能性があります")
                checkpoint["status"] = "merged"
        else:
            checkpoint["status"] = "pushed" if not pr else "pr_created"
    else:
        checkout_branch(original_branch)
        checkpoint["status"] = "committed"
    
    # Update checkpoint
    checkpoint["branch"] = branch
    checkpoint["article_path"] = str(article_path)
    save_checkpoint(slug, checkpoint)
    
    print(f"\n✅ Done: {article_path}")

if __name__ == "__main__":
    main()
