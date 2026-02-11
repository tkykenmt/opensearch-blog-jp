"""Image download and processing."""
import re
import hashlib
import urllib.request
from pathlib import Path
from lib.state import get_work_dir

def extract_images_from_html(html: str) -> list[str]:
    """Extract image URLs from HTML content."""
    return re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)

def download_images(slug: str, urls: list[str]) -> dict[str, str]:
    """Download images to work/{slug}/images/, return url->local path mapping."""
    img_dir = get_work_dir(slug) / "images"
    img_dir.mkdir(exist_ok=True)
    mapping = {}
    for url in urls:
        if not url.startswith("http"):
            continue
        ext = Path(url.split("?")[0]).suffix or ".png"
        name = hashlib.md5(url.encode()).hexdigest()[:12] + ext
        local = img_dir / name
        if not local.exists():
            try:
                urllib.request.urlretrieve(url, local)
            except Exception as e:
                print(f"Warning: Failed to download {url}: {e}")
                continue
        mapping[url] = f"/images/{slug}/{name}"
    return mapping

def replace_image_urls(content: str, mapping: dict[str, str]) -> str:
    """Replace image URLs in content with local paths."""
    for old, new in mapping.items():
        content = content.replace(old, new)
    return content
