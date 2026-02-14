"""
CodeGenie AI Editor — Git Service
Provides Git operations using subprocess calls to the git CLI.
"""

import asyncio
import os
from dataclasses import dataclass, field
from app.services.ai_service import ai_service


@dataclass
class GitFileStatus:
    """Represents a single file's git status."""
    path: str
    status: str  # 'modified', 'added', 'deleted', 'untracked', 'renamed', 'staged'
    staged: bool = False


@dataclass
class GitCommit:
    """Represents a git commit."""
    hash: str
    short_hash: str
    author: str
    date: str
    message: str


@dataclass
class GitBranch:
    """Represents a git branch."""
    name: str
    is_current: bool = False


class GitService:
    """Service for performing Git operations on a project repository."""

    def __init__(self):
        self._project_path: str | None = None

    def set_project_path(self, path: str):
        """Set the current project root path."""
        self._project_path = path

    @property
    def project_path(self) -> str:
        if not self._project_path:
            raise ValueError("No project path set. Call set_project_path() first.")
        return self._project_path

    async def _run_git(self, *args: str, cwd: str | None = None) -> tuple[str, str, int]:
        """Run a git command and return (stdout, stderr, returncode)."""
        work_dir = cwd or self.project_path
        process = await asyncio.create_subprocess_exec(
            'git', *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=work_dir,
        )
        stdout, stderr = await process.communicate()
        return stdout.decode('utf-8', errors='replace'), stderr.decode('utf-8', errors='replace'), process.returncode

    async def is_git_repo(self, path: str | None = None) -> bool:
        """Check if the given path is inside a git repository."""
        try:
            _, _, code = await self._run_git('rev-parse', '--is-inside-work-tree', cwd=path or self.project_path)
            return code == 0
        except Exception:
            return False

    async def get_status(self) -> list[dict]:
        """Get the working tree status (modified, staged, untracked files)."""
        stdout, _, code = await self._run_git('status', '--porcelain=v1', '-uall')
        if code != 0:
            return []

        files = []
        for line in stdout.strip().split('\n'):
            if not line.strip():
                continue

            index_status = line[0]
            worktree_status = line[1]
            file_path = line[3:].strip()

            # Handle renames (e.g., "R  old -> new")
            if ' -> ' in file_path:
                file_path = file_path.split(' -> ')[-1]

            # Determine status
            if index_status == '?' and worktree_status == '?':
                status = 'untracked'
                staged = False
            elif index_status == 'A':
                status = 'added'
                staged = True
            elif index_status == 'D' or worktree_status == 'D':
                status = 'deleted'
                staged = index_status == 'D'
            elif index_status == 'R':
                status = 'renamed'
                staged = True
            elif index_status == 'M' or worktree_status == 'M':
                status = 'modified'
                staged = index_status == 'M'
            else:
                status = 'modified'
                staged = index_status != ' '

            files.append({
                'path': file_path,
                'status': status,
                'staged': staged,
            })

        return files

    async def get_diff(self, file_path: str | None = None, staged: bool = False) -> str:
        """Get the diff for the working tree or a specific file."""
        args = ['diff', '--color=never']
        if staged:
            args.append('--cached')
        if file_path:
            args.extend(['--', file_path])

        stdout, _, _ = await self._run_git(*args)
        return stdout

    async def get_log(self, count: int = 20) -> list[dict]:
        """Get recent commit history."""
        fmt = '%H|%h|%an|%ar|%s'
        stdout, _, code = await self._run_git(
            'log', f'-{count}', f'--pretty=format:{fmt}', '--no-merges'
        )
        if code != 0:
            return []

        commits = []
        for line in stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split('|', 4)
            if len(parts) == 5:
                commits.append({
                    'hash': parts[0],
                    'short_hash': parts[1],
                    'author': parts[2],
                    'date': parts[3],
                    'message': parts[4],
                })

        return commits

    async def get_branches(self) -> list[dict]:
        """Get list of branches with current branch marked."""
        stdout, _, code = await self._run_git('branch', '--no-color')
        if code != 0:
            return []

        branches = []
        for line in stdout.strip().split('\n'):
            if not line.strip():
                continue
            is_current = line.startswith('* ')
            name = line.lstrip('* ').strip()
            branches.append({
                'name': name,
                'is_current': is_current,
            })

        return branches

    async def stage_all(self):
        """Stage all changes."""
        await self._run_git('add', '-A')

    async def stage_file(self, file_path: str):
        """Stage a specific file."""
        await self._run_git('add', '--', file_path)

    async def unstage_file(self, file_path: str):
        """Unstage a specific file."""
        await self._run_git('reset', 'HEAD', '--', file_path)

    async def commit(self, message: str) -> dict:
        """Commit staged changes with the given message."""
        # Stage all if nothing is staged
        status = await self.get_status()
        has_staged = any(f['staged'] for f in status)
        if not has_staged:
            await self.stage_all()

        stdout, stderr, code = await self._run_git('commit', '-m', message)
        if code != 0:
            raise RuntimeError(f"Git commit failed: {stderr}")

        return {'message': message, 'output': stdout.strip()}

    async def checkout(self, branch: str) -> dict:
        """Switch to a different branch."""
        stdout, stderr, code = await self._run_git('checkout', branch)
        if code != 0:
            raise RuntimeError(f"Git checkout failed: {stderr}")
        return {'branch': branch, 'output': (stdout or stderr).strip()}

    async def ai_commit_message(self) -> str:
        """Generate an AI commit message from the current diff."""
        diff = await self.get_diff()
        if not diff.strip():
            diff = await self.get_diff(staged=True)
        if not diff.strip():
            return "chore: minor updates"

        # Truncate very long diffs
        if len(diff) > 4000:
            diff = diff[:4000] + "\n... (diff truncated)"

        prompt = (
            "Generate a concise, conventional git commit message for the following diff. "
            "Use the format: <type>: <description>\n"
            "Types: feat, fix, docs, style, refactor, test, chore\n"
            "Return ONLY the commit message, nothing else. No quotes.\n\n"
            f"Diff:\n```\n{diff}\n```"
        )

        response = await ai_service.generate_response(
            message=prompt,
            system_prompt="You are a git commit message generator. Return only the commit message."
        )

        # Clean up the response
        msg = response.strip().strip('"').strip("'").strip('`')
        # Take only the first line
        msg = msg.split('\n')[0].strip()
        return msg


# Singleton
git_service = GitService()
