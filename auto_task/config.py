from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

TaskType = Literal["python_script", "python_callable", "shell"]
TriggerType = Literal["cron", "interval"]


@dataclass(frozen=True)
class Task:
    name: str
    type: TaskType
    # python_script
    script: str | None = None
    args: list[str] | None = None
    cwd: str | None = None

    # python_callable
    callable: str | None = None  # "module:function"
    callable_args: list[Any] | None = None
    callable_kwargs: dict[str, Any] | None = None

    # shell
    command: str | None = None
    shell: bool | None = None  # default True for shell tasks


@dataclass(frozen=True)
class Schedule:
    task: str
    trigger: TriggerType
    cron: str | None = None         # for trigger="cron" (5-field)
    seconds: int | None = None      # for trigger="interval"


@dataclass(frozen=True)
class Watcher:
    path: str
    task: str
    patterns: list[str] | None = None
    ignore_patterns: list[str] | None = None
    recursive: bool = True
    debounce_ms: int = 500


@dataclass(frozen=True)
class AppConfig:
    tasks: dict[str, Task]
    schedules: list[Schedule]
    watchers: list[Watcher]
    log_level: str = "INFO"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_config(raw: dict[str, Any]) -> AppConfig:
    log_level = raw.get("log_level", "INFO")

    raw_tasks = raw.get("tasks", {})
    _require(isinstance(raw_tasks, dict) and raw_tasks, "`tasks` must be a non-empty object")

    tasks: dict[str, Task] = {}
    for name, t in raw_tasks.items():
        _require(isinstance(name, str) and name.strip(), "task name must be a non-empty string")
        _require(isinstance(t, dict), f"task '{name}' must be an object")
        ttype = t.get("type")
        _require(ttype in ("python_script", "python_callable", "shell"), f"task '{name}': invalid type")

        task = Task(
            name=name,
            type=ttype,
            script=t.get("script"),
            args=t.get("args"),
            cwd=t.get("cwd"),
            callable=t.get("callable"),
            callable_args=t.get("callable_args"),
            callable_kwargs=t.get("callable_kwargs"),
            command=t.get("command"),
            shell=t.get("shell"),
        )

        # Validate by type
        if task.type == "python_script":
            _require(isinstance(task.script, str) and task.script.strip(), f"task '{name}': 'script' required")
        elif task.type == "python_callable":
            _require(isinstance(task.callable, str) and ":" in task.callable, f"task '{name}': 'callable' must be 'module:function'")
        elif task.type == "shell":
            _require(isinstance(task.command, str) and task.command.strip(), f"task '{name}': 'command' required")

        tasks[name] = task

    raw_schedules = raw.get("schedules", [])
    _require(isinstance(raw_schedules, list), "`schedules` must be a list")

    schedules: list[Schedule] = []
    for i, s in enumerate(raw_schedules):
        _require(isinstance(s, dict), f"schedule[{i}] must be an object")
        task_name = s.get("task")
        trigger = s.get("trigger")
        _require(task_name in tasks, f"schedule[{i}]: unknown task '{task_name}'")
        _require(trigger in ("cron", "interval"), f"schedule[{i}]: trigger must be 'cron' or 'interval'")

        sched = Schedule(
            task=task_name,
            trigger=trigger,
            cron=s.get("cron"),
            seconds=s.get("seconds"),
        )

        if sched.trigger == "cron":
            _require(isinstance(sched.cron, str) and sched.cron.strip(), f"schedule[{i}]: 'cron' required for cron trigger")
        if sched.trigger == "interval":
            _require(isinstance(sched.seconds, int) and sched.seconds > 0, f"schedule[{i}]: 'seconds' must be > 0 for interval trigger")

        schedules.append(sched)

    raw_watchers = raw.get("watchers", [])
    _require(isinstance(raw_watchers, list), "`watchers` must be a list")

    watchers: list[Watcher] = []
    for i, w in enumerate(raw_watchers):
        _require(isinstance(w, dict), f"watchers[{i}] must be an object")
        path = w.get("path")
        task_name = w.get("task")
        _require(isinstance(path, str) and path.strip(), f"watchers[{i}]: 'path' required")
        _require(task_name in tasks, f"watchers[{i}]: unknown task '{task_name}'")

        watcher = Watcher(
            path=path,
            task=task_name,
            patterns=w.get("patterns"),
            ignore_patterns=w.get("ignore_patterns"),
            recursive=bool(w.get("recursive", True)),
            debounce_ms=int(w.get("debounce_ms", 500)),
        )
        watchers.append(watcher)

    return AppConfig(
        tasks=tasks,
        schedules=schedules,
        watchers=watchers,
        log_level=log_level,
  )
