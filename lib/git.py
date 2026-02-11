"""Git and GitHub operations."""
import subprocess
from pathlib import Path

def run_git(*args) -> str:
    """Run git command and return output."""
    result = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr}")
    return result.stdout.strip()

def get_current_branch() -> str:
    return run_git("branch", "--show-current")

def create_branch(name: str):
    run_git("checkout", "-b", name)

def checkout_branch(name: str):
    run_git("checkout", name)

def add_files(*paths: str):
    run_git("add", *paths)

def commit(message: str):
    run_git("commit", "-m", message)

def push(branch: str = None):
    if branch:
        run_git("push", "-u", "origin", branch)
    else:
        run_git("push")

def get_repo_info() -> dict:
    """Get repository info from git remote."""
    remote = run_git("remote", "get-url", "origin")
    # Parse github.com/owner/repo from various URL formats
    if "github.com" in remote:
        parts = remote.replace(".git", "").split("github.com")[-1].strip("/:")
        owner, repo = parts.split("/")[:2]
        return {"owner": owner, "repo": repo, "remote": remote}
    return {"remote": remote}

def delete_local_branch(name: str):
    """Delete a local branch."""
    run_git("branch", "-D", name)

def has_changes() -> bool:
    """Check if there are uncommitted changes."""
    status = run_git("status", "--porcelain")
    return bool(status)
