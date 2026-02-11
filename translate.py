#!/usr/bin/env python3
"""Fetch OpenSearch blog article and translate."""
import argparse
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path
from lib.state import get_work_dir, load_checkpoint, save_checkpoint
from lib.image import extract_images_from_html, download_images
from lib.review_checks import check_slug

def extract_slug(url: str) -> str:
    """Extract slug from OpenSearch blog URL."""
    # https://opensearch.org/blog/some-article-title/
    match = re.search(r'/blog/([^/]+)/?', url)
    return match.group(1) if match else url.split("/")[-1].replace("/", "")

def generate_slug(title: str, original_slug: str) -> str | None:
    """Use LLM to generate a Zenn-compatible slug from article title."""
    prompt = (
        f"Generate a Zenn article slug from the following blog title.\n"
        f"Rules: lowercase a-z, 0-9, hyphens, underscores only. 12-50 chars.\n"
        f"Keep it concise and meaningful. Output ONLY the slug, nothing else.\n"
        f"Original slug: {original_slug}\n"
        f"Title: {title}"
    )
    result = subprocess.run(
        ["kiro-cli", "chat", "--no-interactive", "--trust-tools=", prompt],
        capture_output=True, text=True,
        cwd=Path(__file__).parent,
    )
    if result.returncode != 0:
        return None
    # Extract slug from output (last non-empty line)
    for line in reversed(result.stdout.strip().splitlines()):
        candidate = line.strip().strip("`").strip()
        if candidate and re.fullmatch(r'[a-z0-9_-]+', candidate):
            return candidate
    return None

def fetch_article(url: str) -> str:
    """Fetch article HTML from URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")

def extract_content(html: str) -> tuple[str, str]:
    """Extract title and main content from HTML."""
    title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    title = title_match.group(1).strip() if title_match else "Untitled"
    
    # Try to find article content
    content_match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    if content_match:
        content = content_match.group(1)
    else:
        # Fallback: find main content area
        content_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
        content = content_match.group(1) if content_match else html
    
    return title, content

def main():
    parser = argparse.ArgumentParser(description="Fetch OpenSearch blog for translation")
    parser.add_argument("-u", "--url", required=True, help="OpenSearch blog URL")
    parser.add_argument("--slug", help="Override slug (default: extracted from URL)")
    parser.add_argument("--no-translate", action="store_true", help="Fetch only, skip translation")
    args = parser.parse_args()
    
    slug = args.slug or extract_slug(args.url)
    original_slug = slug
    print(f"📥 Fetching article: {args.url}")
    
    # Fetch and save HTML (use original slug as temp work dir)
    html = fetch_article(args.url)
    work_dir = get_work_dir(original_slug)
    (work_dir / "content.html").write_text(html)
    
    # Extract content
    title, content = extract_content(html)
    print(f"📝 Title: {title}")
    
    # Generate slug via LLM if original is invalid
    if not args.slug and check_slug(slug):
        print(f"🤖 Generating slug (original invalid: {len(slug)} chars)...")
        generated = generate_slug(title, slug)
        if generated and not check_slug(generated):
            slug = generated
            print(f"   Generated: {slug} ({len(slug)} chars)")
            # Rename work dir
            new_dir = get_work_dir(slug)
            if new_dir != work_dir:
                if new_dir.exists():
                    shutil.rmtree(new_dir)
                work_dir.rename(new_dir)
                work_dir = new_dir
        else:
            print(f"   ⚠️  LLM slug generation failed, using original")
    
    # Final validation
    issues = check_slug(slug)
    if issues:
        for i in issues:
            print(f"❌ {i.message}")
        print(f"   --slug オプションで有効な slug を指定してください")
        return
    
    print(f"📁 Work directory: work/{slug}/")
    
    # Download images
    img_urls = extract_images_from_html(content)
    if img_urls:
        print(f"🖼️  Downloading {len(img_urls)} images...")
        mapping = download_images(slug, img_urls)
        print(f"   Downloaded {len(mapping)} images")
    else:
        mapping = {}
    
    # Save checkpoint
    checkpoint = load_checkpoint(slug)
    checkpoint.update({
        "status": "fetched",
        "url": args.url,
        "title": title,
        "image_count": len(mapping),
        "image_mapping": mapping
    })
    save_checkpoint(slug, checkpoint)
    
    print(f"\n✅ Ready for translation")
    print(f"   Next: Run Kiro with translator agent to translate work/{slug}/content.html")
    print(f"   Output: work/{slug}/translated.md")

    if args.no_translate:
        return

    print(f"\n🤖 Starting Kiro translation...")
    prompt = f"work/{slug}/content.html を翻訳して work/{slug}/translated.md を作成してください"
    result = subprocess.run(
        ["kiro-cli", "chat", "--agent", "translator",
         "--no-interactive", "-a", prompt],
        cwd=Path(__file__).parent,
    )
    if result.returncode == 0:
        print(f"\n✅ Translation complete: work/{slug}/translated.md")
    else:
        print(f"\n❌ Translation failed (exit code: {result.returncode})")
        raise SystemExit(result.returncode)

if __name__ == "__main__":
    main()
