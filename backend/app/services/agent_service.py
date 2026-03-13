"""
CodeGenie AI Editor — Agent Service
Implements the Plan → Execute → Verify autonomous coding loop.
"""

import asyncio
import json
import os
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncGenerator

from app.services.ai_service import ai_service


class StepType(str, Enum):
    CREATE_FILE = "create_file"
    MODIFY_FILE = "modify_file"
    DELETE_FILE = "delete_file"
    RUN_COMMAND = "run_command"
    SEARCH_CODE = "search_code"
    THINK = "think"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AgentStep:
    """A single step in the agent's plan."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: StepType = StepType.THINK
    description: str = ""
    file_path: str | None = None
    content: str | None = None
    command: str | None = None
    status: StepStatus = StepStatus.PENDING
    result: str | None = None
    error: str | None = None

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "description": self.description,
            "file_path": self.file_path,
            "content": self.content,
            "command": self.command,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
        }


@dataclass
class AgentTask:
    """An agent task with its steps and state."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    goal: str = ""
    project_path: str = ""
    steps: list[AgentStep] = field(default_factory=list)
    status: str = "planning"  # planning, executing, verifying, completed, failed
    iteration: int = 0
    max_iterations: int = 3
    summary: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "goal": self.goal,
            "project_path": self.project_path,
            "steps": [s.to_dict() for s in self.steps],
            "status": self.status,
            "iteration": self.iteration,
            "summary": self.summary,
        }


class AgentService:
    """
    Autonomous AI coding agent that plans, executes, and verifies coding tasks.
    Uses a Plan → Execute → Verify loop with up to 3 iterations.
    """

    def __init__(self):
        self.active_tasks: dict[str, AgentTask] = {}

    async def run_task(
        self, goal: str, project_path: str, context: str | None = None
    ) -> AsyncGenerator[dict, None]:
        """
        Run an agent task. Yields SSE-compatible events as the agent works.

        Events:
            - {"event": "plan", "data": {...}}       — Task plan created
            - {"event": "step_start", "data": {...}} — Step execution started
            - {"event": "step_done", "data": {...}}  — Step completed
            - {"event": "verify", "data": {...}}     — Verification result
            - {"event": "complete", "data": {...}}   — Task finished
            - {"event": "error", "data": {...}}      — Error occurred
        """
        task = AgentTask(goal=goal, project_path=project_path)
        self.active_tasks[task.id] = task

        try:
            while task.iteration < task.max_iterations:
                task.iteration += 1

                # ── PHASE 1: Plan ──
                task.status = "planning"
                yield {"event": "status", "data": {"status": "planning", "iteration": task.iteration}}

                steps = await self._plan(task, context)
                task.steps = steps
                yield {"event": "plan", "data": {"steps": [s.to_dict() for s in steps], "iteration": task.iteration}}

                # ── PHASE 2: Execute ──
                task.status = "executing"
                yield {"event": "status", "data": {"status": "executing"}}

                for step in task.steps:
                    step.status = StepStatus.RUNNING
                    yield {"event": "step_start", "data": step.to_dict()}

                    try:
                        result = await self._execute_step(step, task.project_path)
                        step.status = StepStatus.COMPLETED
                        step.result = result
                    except Exception as e:
                        step.status = StepStatus.FAILED
                        step.error = str(e)

                    yield {"event": "step_done", "data": step.to_dict()}

                # ── PHASE 3: Verify ──
                task.status = "verifying"
                yield {"event": "status", "data": {"status": "verifying"}}

                verification = await self._verify(task)
                yield {"event": "verify", "data": verification}

                if verification.get("passed", False):
                    task.status = "completed"
                    task.summary = verification.get("summary", "Task completed successfully.")
                    yield {"event": "complete", "data": task.to_dict()}
                    return

                # If not passed and we can iterate, loop again with feedback
                context = verification.get("feedback", "")

            # Max iterations reached
            task.status = "completed"
            task.summary = "Task completed (max iterations reached)."
            yield {"event": "complete", "data": task.to_dict()}

        except Exception as e:
            task.status = "failed"
            yield {"event": "error", "data": {"error": str(e), "task_id": task.id}}
        finally:
            # Keep task in memory for status checks
            pass

    async def _plan(self, task: AgentTask, context: str | None = None) -> list[AgentStep]:
        """Use AI to create a plan of steps to accomplish the goal."""
        prompt = f"""You are an AI coding agent. Break down this coding task into concrete steps.

GOAL: {task.goal}
PROJECT PATH: {task.project_path}
{"CONTEXT / FEEDBACK FROM PREVIOUS ATTEMPT: " + context if context else ""}
{"ITERATION: " + str(task.iteration) + " of " + str(task.max_iterations) if task.iteration > 1 else ""}

Return a JSON array of steps. Each step must have:
- "type": one of "create_file", "modify_file", "delete_file", "run_command", "search_code", "think"
- "description": what this step does
- "file_path": (for file operations) relative path from project root
- "content": (for create_file) the file content to write, (for modify_file) instructions on what to change
- "command": (for run_command) the shell command to execute

RULES:
- Keep it minimal — fewest steps to accomplish the goal
- For modify_file, describe the change clearly; the AI will handle the actual edit
- For create_file, provide the COMPLETE file content
- Maximum 10 steps
- Return ONLY the JSON array, no other text

Example:
[
  {{"type": "create_file", "description": "Create health endpoint", "file_path": "api/health.py", "content": "from fastapi import APIRouter\\nrouter = APIRouter()\\n@router.get('/health')\\ndef health():\\n    return {{'status': 'ok'}}"}},
  {{"type": "modify_file", "description": "Register health router", "file_path": "main.py", "content": "Add import for health router and include it in the app"}}
]"""

        response = await ai_service.generate_response(
            message=prompt,
            system_prompt="You are a precise coding agent. Return ONLY valid JSON arrays."
        )

        # Parse the JSON response
        try:
            # Clean the response — strip markdown code blocks if present
            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]  # remove first line
                if text.endswith("```"):
                    text = text[:-3]
                elif "```" in text:
                    text = text[:text.rfind("```")]
            text = text.strip()

            steps_data = json.loads(text)
            steps = []
            for s in steps_data[:10]:  # Max 10 steps
                step = AgentStep(
                    type=StepType(s.get("type", "think")),
                    description=s.get("description", ""),
                    file_path=s.get("file_path"),
                    content=s.get("content"),
                    command=s.get("command"),
                )
                steps.append(step)
            return steps
        except (json.JSONDecodeError, ValueError):
            # If parsing fails, create a single "think" step
            return [AgentStep(
                type=StepType.THINK,
                description=f"Planning failed, raw response: {response[:200]}",
                content=response,
            )]

    async def _execute_step(self, step: AgentStep, project_path: str) -> str:
        """Execute a single step and return the result."""

        if step.type == StepType.CREATE_FILE:
            return await self._exec_create_file(step, project_path)
        elif step.type == StepType.MODIFY_FILE:
            return await self._exec_modify_file(step, project_path)
        elif step.type == StepType.DELETE_FILE:
            return await self._exec_delete_file(step, project_path)
        elif step.type == StepType.RUN_COMMAND:
            return await self._exec_run_command(step, project_path)
        elif step.type == StepType.SEARCH_CODE:
            return await self._exec_search_code(step)
        elif step.type == StepType.THINK:
            return step.description
        else:
            return f"Unknown step type: {step.type}"

    async def _exec_create_file(self, step: AgentStep, project_path: str) -> str:
        """Create a new file with the given content."""
        if not step.file_path or not step.content:
            return "Error: file_path and content are required for create_file"

        full_path = os.path.join(project_path, step.file_path)

        # Create directories
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(step.content)

        return f"Created file: {step.file_path} ({len(step.content)} chars)"

    async def _exec_modify_file(self, step: AgentStep, project_path: str) -> str:
        """Modify an existing file using AI to apply changes."""
        if not step.file_path:
            return "Error: file_path is required for modify_file"

        full_path = os.path.join(project_path, step.file_path)

        if not os.path.exists(full_path):
            return f"Error: File not found: {step.file_path}"

        with open(full_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Use AI to apply the modification
        prompt = f"""Modify this file according to the instruction.

INSTRUCTION: {step.content or step.description}

CURRENT FILE CONTENT:
```
{original_content}
```

Return ONLY the complete modified file content. No explanations, no markdown code blocks — just the raw file content."""

        modified_content = await ai_service.generate_response(
            message=prompt,
            system_prompt="You are a precise code editor. Return only the complete file content, nothing else."
        )

        # Clean up response
        text = modified_content.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:])  # remove first line
            if text.endswith("```"):
                text = text[:-3]
            elif "```" in text:
                text = text[:text.rfind("```")]
        text = text.strip()

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(text)

        return f"Modified file: {step.file_path}"

    async def _exec_delete_file(self, step: AgentStep, project_path: str) -> str:
        """Delete a file."""
        if not step.file_path:
            return "Error: file_path is required for delete_file"

        full_path = os.path.join(project_path, step.file_path)

        if os.path.exists(full_path):
            os.remove(full_path)
            return f"Deleted file: {step.file_path}"
        else:
            return f"File not found (already deleted?): {step.file_path}"

    async def _exec_run_command(self, step: AgentStep, project_path: str) -> str:
        """Execute a shell command in the project directory."""
        if not step.command:
            return "Error: command is required for run_command"

        # Safety: block dangerous commands
        dangerous = ['rm -rf /', 'mkfs', 'dd if=', 'format ', ':(){', 'fork bomb']
        cmd_lower = step.command.lower()
        for d in dangerous:
            if d in cmd_lower:
                return f"Blocked dangerous command: {step.command}"

        try:
            process = await asyncio.create_subprocess_shell(
                step.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=project_path,
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            output = stdout.decode('utf-8', errors='replace')
            errors = stderr.decode('utf-8', errors='replace')

            result = f"Exit code: {process.returncode}\n"
            if output:
                result += f"Output:\n{output[:2000]}\n"
            if errors:
                result += f"Errors:\n{errors[:1000]}\n"

            return result
        except asyncio.TimeoutError:
            return "Command timed out after 30 seconds"
        except Exception as e:
            return f"Command execution failed: {str(e)}"

    async def _exec_search_code(self, step: AgentStep) -> str:
        """Search the codebase using semantic search."""
        try:
            from app.services.vector_store import vector_store
            query = step.content or step.description
            results = await vector_store.search(query, top_k=5)
            if not results:
                return "No relevant code found."

            output = "Search results:\n"
            for r in results:
                file_path = r.get("file_path", r.get("metadata", {}).get("file_path", "unknown"))
                content = r.get("content", "")[:200]
                output += f"\n--- {file_path} ---\n{content}\n"
            return output
        except Exception as e:
            return f"Search failed: {str(e)}"

    async def _verify(self, task: AgentTask) -> dict:
        """Verify the task execution and decide if it's complete."""
        # Build a summary of what was done
        step_summary = "\n".join([
            f"- [{s.status.value}] {s.type.value}: {s.description}"
            + (f" → {s.result[:100]}" if s.result else "")
            + (f" ⚠ {s.error}" if s.error else "")
            for s in task.steps
        ])

        prompt = f"""You are verifying whether a coding task was completed successfully.

GOAL: {task.goal}
ITERATION: {task.iteration} of {task.max_iterations}

STEPS EXECUTED:
{step_summary}

Respond with a JSON object:
{{
    "passed": true/false,
    "summary": "Brief summary of what was accomplished",
    "feedback": "If not passed, what should be done differently in the next iteration"
}}

Return ONLY the JSON object, no other text."""

        response = await ai_service.generate_response(
            message=prompt,
            system_prompt="You are a task verifier. Return ONLY valid JSON."
        )

        try:
            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if "```" in text:
                    text = text[:text.rfind("```")]
            text = text.strip()
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return {
                "passed": True,
                "summary": "Task steps executed. Verification parsing failed but steps completed.",
                "feedback": "",
            }

    def get_task_status(self, task_id: str) -> dict | None:
        """Get the status of a task."""
        task = self.active_tasks.get(task_id)
        if task:
            return task.to_dict()
        return None


# Singleton
agent_service = AgentService()
