"""GitHub operations via gh CLI."""
import subprocess
import json


def run_gh(*args) -> str:
    """Run gh command and return output."""
    result = subprocess.run(["gh"] + list(args), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr}")
    return result.stdout.strip()


def create_pr(branch: str, title: str, body: str = "", base: str = "main") -> dict:
    """Create a pull request, return PR info dict."""
    args = ["pr", "create", "--head", branch, "--base", base,
            "--title", title, "--body", body, "--json", "number,url"]
    return json.loads(run_gh(*args))


def merge_pr(branch: str, method: str = "squash", admin: bool = False):
    """Merge a pull request by branch name."""
    args = ["pr", "merge", branch, f"--{method}", "--delete-branch"]
    if admin:
        args.append("--admin")
    run_gh(*args)
