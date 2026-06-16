"""Context Manager — tracks the user's current work context.

Maintains a rolling window of active files, recent actions, current
language/framework, and task metadata that agents use for grounding.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class FileContext:
    path: str
    language: str
    last_edited: float = 0.0
    cursor_line: int = 0


@dataclass
class ActionRecord:
    action: str
    timestamp: float
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class WorkContext:
    """Snapshot of what the user is currently doing."""

    active_file: FileContext | None = None
    recent_files: list[FileContext] = field(default_factory=list)
    recent_actions: list[ActionRecord] = field(default_factory=list)
    current_language: str = "unknown"
    current_framework: str = "unknown"
    project_root: str = ""
    task_description: str = ""
    session_duration_sec: float = 0.0


class ContextManager:
    """Accumulates editor / IDE events and exposes a ``WorkContext``."""

    def __init__(self, max_files: int = 20, max_actions: int = 100) -> None:
        self._files: deque[FileContext] = deque(maxlen=max_files)
        self._actions: deque[ActionRecord] = deque(maxlen=max_actions)
        self._active: FileContext | None = None
        self._session_start = time.monotonic()
        self._project_root = ""
        self._task_description = ""

    def set_project(self, root: str, task: str = "") -> None:
        self._project_root = root
        self._task_description = task

    def open_file(self, path: str, language: str = "unknown") -> None:
        fc = FileContext(
            path=path,
            language=language,
            last_edited=time.monotonic(),
        )
        self._active = fc
        # Deduplicate by path
        self._files = deque(
            (f for f in self._files if f.path != path),
            maxlen=self._files.maxlen,
        )
        self._files.append(fc)

    def update_cursor(self, line: int) -> None:
        if self._active:
            self._active.cursor_line = line

    def record_action(self, action: str, **meta: str) -> None:
        self._actions.append(
            ActionRecord(
                action=action,
                timestamp=time.monotonic(),
                metadata=meta,
            )
        )

    def snapshot(self) -> WorkContext:
        lang = self._active.language if self._active else "unknown"
        return WorkContext(
            active_file=self._active,
            recent_files=list(self._files),
            recent_actions=list(self._actions),
            current_language=lang,
            current_framework=self._detect_framework(),
            project_root=self._project_root,
            task_description=self._task_description,
            session_duration_sec=time.monotonic() - self._session_start,
        )

    def _detect_framework(self) -> str:
        paths = {f.path for f in self._files}
        if any("next.config" in p for p in paths):
            return "nextjs"
        if any("fastapi" in p.lower() for p in paths):
            return "fastapi"
        if any("django" in p.lower() for p in paths):
            return "django"
        if any("package.json" in p for p in paths):
            return "node"
        return "unknown"
