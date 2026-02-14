#!/usr/bin/env python3
"""Copy article to articles/ and images/, then git commit and push."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import shutil
from lib.state import get_work_dir, load_checkpoint, save_checkpoint, list_work_slugs
from lib.zenn import get_translated_path, get_article_path, get_images_dir
from lib.git import (create_branch, checkout_branch, get_current_branch,
                     add_files, commit, push, has_changes, delete_local_branch)


def main():
    parser = argparse.ArgumentParser(description="Copy files, commit and push")
    parser.add_argument("--slug", help="Article slug (default: latest)")
    parser.add_argument("--no-push", action="store_true", help="Commit only, don't push")
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

    checkpoint = load_checkpoint(slug)
    title = checkpoint.get("title", slug)
    article_path = get_article_path(slug)
    images_src = get_work_dir(slug) / "images"
    images_dst = get_images_dir(slug)
    branch = f"article/{slug}"

    # Branch
    original_branch = get_current_branch()
    try:
        create_branch(branch)
    except RuntimeError:
        checkout_branch(branch)

    # Copy article
    article_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(translated, article_path)
    print(f"✓ {article_path}")

    # Copy images
    if images_src.exists() and any(images_src.iterdir()):
        images_dst.mkdir(parents=True, exist_ok=True)
        for img in images_src.iterdir():
            shutil.copy(img, images_dst / img.name)
        print(f"✓ {len(list(images_src.iterdir()))} images → {images_dst}")

    add_files(str(article_path))
    if images_dst.exists():
        add_files(str(images_dst))

    if not has_changes():
        print("ℹ️  No changes")
        checkout_branch(original_branch)
        return

    commit(f"Add article: {title}")
    print(f"✓ Committed on {branch}")

    if not args.no_push:
        push(branch)
        print(f"✓ Pushed to origin/{branch}")

    # Return to original branch
    checkout_branch(original_branch)
    print(f"✓ Returned to {original_branch}")

    checkpoint["status"] = "pushed"
    checkpoint["branch"] = branch
    checkpoint["article_path"] = str(article_path)
    save_checkpoint(slug, checkpoint)


if __name__ == "__main__":
    main()
