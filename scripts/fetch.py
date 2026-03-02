#!/usr/bin/env python3
"""Fetch OpenSearch blog article HTML and download images."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import re
import shutil
import urllib.request
from lib import WORK_DIR
from lib.state import get_work_dir, load_checkpoint, save_checkpoint
from lib.image import extract_images_from_html, download_images
from lib.review_checks import check_slug


def extract_slug(url: str) -> str:
    match = re.search(r'/blog/([^/]+)/?', url)
    return match.group(1) if match else url.split("/")[-1].replace("/", "")


def truncate_slug(slug: str, max_len: int = 50) -> str:
    if len(slug) <= max_len:
        return slug
    truncated = slug[:max_len]
    last_sep = max(truncated.rfind("-"), truncated.rfind("_"))
    if last_sep >= 12:
        truncated = truncated[:last_sep]
    return truncated


def fetch_article(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def extract_content(html: str) -> tuple[str, str]:
    title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    title = title_match.group(1).strip() if title_match else "Untitled"
    content_match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    if not content_match:
        content_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
    content = content_match.group(1) if content_match else html
    return title, content


def main():
    parser = argparse.ArgumentParser(description="Fetch blog article and download images")
    parser.add_argument("-u", "--url", required=True, help="OpenSearch blog URL")
    parser.add_argument("--slug", help="Override slug")
    args = parser.parse_args()

    slug = args.slug or extract_slug(args.url)

    # Truncate if too long
    if not args.slug and check_slug(slug):
        slug = truncate_slug(slug)

    issues = check_slug(slug)
    if issues:
        for i in issues:
            print(f"❌ {i.message}")
        return

    print(f"📥 Fetching: {args.url}")
    html = fetch_article(args.url)
    work_dir = get_work_dir(slug)
    (work_dir / "content.html").write_text(html)

    title, content = extract_content(html)
    print(f"📝 Title: {title}")

    img_urls = extract_images_from_html(content)
    mapping = {}
    if img_urls:
        print(f"🖼️  Downloading {len(img_urls)} images...")
        mapping = download_images(slug, img_urls)

    checkpoint = load_checkpoint(slug)
    checkpoint.update({
        "status": "fetched",
        "url": args.url,
        "title": title,
        "image_count": len(mapping),
        "image_mapping": mapping,
    })
    save_checkpoint(slug, checkpoint)

    print(f"✅ work/{slug}/ ready (slug: {slug})")


if __name__ == "__main__":
    main()
