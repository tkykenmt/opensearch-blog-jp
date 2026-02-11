"""Automated review checks for translated articles."""
import re
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Issue:
    level: str  # "error" | "warning"
    check: str
    message: str
    line: int = None
    suggestion: str = None

def check_image_links(content: str, images_dir: Path) -> list[Issue]:
    """Check all image links exist."""
    issues = []
    for match in re.finditer(r'!\[.*?\]\((/images/[^)]+)\)', content):
        img_path = Path("." + match.group(1))
        if not img_path.exists() and not (images_dir / img_path.name).exists():
            issues.append(Issue("warning", "image", f"Image not found: {match.group(1)}"))
    return issues

def check_spacing(content: str) -> list[Issue]:
    """Check half/full-width spacing rules."""
    issues = []
    # 英数字と日本語の間にスペースがない
    for i, line in enumerate(content.split("\n"), 1):
        if re.search(r'[a-zA-Z0-9][ぁ-んァ-ン一-龥]|[ぁ-んァ-ン一-龥][a-zA-Z0-9]', line):
            issues.append(Issue("warning", "spacing", 
                "英数字と日本語の間にスペースを入れてください", line=i))
    return issues

def check_parentheses(content: str) -> list[Issue]:
    """Check parentheses are full-width in Japanese context."""
    issues = []
    for i, line in enumerate(content.split("\n"), 1):
        # 日本語文中の半角括弧
        if re.search(r'[ぁ-んァ-ン一-龥]\([^)]*\)|[ぁ-んァ-ン一-龥]\[[^\]]*\]', line):
            issues.append(Issue("warning", "parentheses",
                "日本語文中では全角括弧（）を使用してください", line=i))
    return issues

def check_front_matter(content: str) -> list[Issue]:
    """Check front matter requirements."""
    issues = []
    if not content.startswith("---"):
        issues.append(Issue("error", "front_matter", "Front matter が見つかりません"))
        return issues
    
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        issues.append(Issue("error", "front_matter", "Front matter が不正です"))
        return issues
    
    fm = match.group(1)
    required = ["title", "emoji", "type", "topics", "published"]
    for field in required:
        if f"{field}:" not in fm:
            issues.append(Issue("error", "front_matter", f"必須フィールド '{field}' がありません"))
    
    # Title length check (Zenn limit: 70 chars)
    title_match = re.search(r'title:\s*"([^"]*)"', fm)
    if title_match and len(title_match.group(1)) > 70:
        issues.append(Issue("warning", "front_matter", 
            f"タイトルが70文字を超えています ({len(title_match.group(1))}文字)"))
    return issues

def check_slug(slug: str) -> list[Issue]:
    """Check slug meets Zenn requirements (a-z0-9, hyphens, underscores, 12-50 chars)."""
    issues = []
    if not re.fullmatch(r'[a-z0-9_-]+', slug):
        issues.append(Issue("error", "slug", f"slug に使用できない文字が含まれています: {slug}"))
    if len(slug) < 12:
        issues.append(Issue("error", "slug", f"slug が短すぎます ({len(slug)}文字、12文字以上必要)"))
    if len(slug) > 50:
        issues.append(Issue("error", "slug", f"slug が長すぎます ({len(slug)}文字、50文字以下にしてください)"))
    return issues

def run_all_checks(content: str, images_dir: Path = None, slug: str = None) -> list[Issue]:
    """Run all review checks."""
    issues = []
    if slug:
        issues.extend(check_slug(slug))
    issues.extend(check_front_matter(content))
    issues.extend(check_spacing(content))
    issues.extend(check_parentheses(content))
    if images_dir:
        issues.extend(check_image_links(content, images_dir))
    return issues

def format_issues(issues: list[Issue]) -> str:
    """Format issues for display."""
    if not issues:
        return "✅ No issues found"
    
    lines = []
    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]
    
    if errors:
        lines.append(f"❌ {len(errors)} error(s):")
        for i in errors:
            loc = f" (line {i.line})" if i.line else ""
            lines.append(f"  [{i.check}]{loc} {i.message}")
    
    if warnings:
        lines.append(f"⚠️  {len(warnings)} warning(s):")
        for i in warnings:
            loc = f" (line {i.line})" if i.line else ""
            lines.append(f"  [{i.check}]{loc} {i.message}")
    
    return "\n".join(lines)
