"""State management for work/{slug}/ checkpoint."""
import json
from pathlib import Path
from datetime import datetime
from lib import WORK_DIR

def get_work_dir(slug: str) -> Path:
    """Get work directory for slug, create if not exists."""
    path = Path(WORK_DIR) / slug
    path.mkdir(parents=True, exist_ok=True)
    return path

def load_checkpoint(slug: str) -> dict:
    """Load checkpoint.json for slug."""
    path = get_work_dir(slug) / "checkpoint.json"
    if path.exists():
        return json.loads(path.read_text())
    return {"slug": slug, "created_at": datetime.now().isoformat(), "status": "init"}

def save_checkpoint(slug: str, data: dict):
    """Save checkpoint.json for slug."""
    path = get_work_dir(slug) / "checkpoint.json"
    data["updated_at"] = datetime.now().isoformat()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def list_work_slugs() -> list[str]:
    """List all slugs in work directory."""
    work = Path(WORK_DIR)
    if not work.exists():
        return []
    return [d.name for d in work.iterdir() if d.is_dir() and (d / "checkpoint.json").exists()]
