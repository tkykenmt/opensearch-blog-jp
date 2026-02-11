"""Zenn article operations."""
import re
import time
import urllib.request
from pathlib import Path
from datetime import datetime
from lib import ARTICLES_DIR, IMAGES_DIR
from lib.state import get_work_dir

ZENN_BASE_URL = "https://zenn.dev/opensearch/articles"

def generate_front_matter(title: str, emoji: str = "📝", article_type: str = "tech", 
                          topics: list[str] = None, published: bool = False) -> str:
    """Generate Zenn front matter."""
    topics = topics or ["OpenSearch", "AWS"]
    return f'''---
title: "{title}"
emoji: "{emoji}"
type: "{article_type}"
topics: {topics}
published: {str(published).lower()}
---
'''

def extract_front_matter(content: str) -> tuple[dict, str]:
    """Extract front matter and body from markdown."""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return {}, content
    fm_text, body = match.groups()
    fm = {}
    for line in fm_text.strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm, body

def get_translated_path(slug: str) -> Path:
    """Get path to translated.md in work directory."""
    return get_work_dir(slug) / "translated.md"

def get_article_path(slug: str) -> Path:
    """Get path to article in articles directory."""
    return Path(ARTICLES_DIR) / f"{slug}.md"

def get_images_dir(slug: str) -> Path:
    """Get images directory for slug."""
    return Path(IMAGES_DIR) / slug


def check_published(slug: str, timeout: int = 180, interval: int = 10) -> bool:
    """Poll Zenn to check if article is published. Returns True if accessible."""
    url = f"{ZENN_BASE_URL}/{slug}"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(interval)
    return False
