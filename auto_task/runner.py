from __future__ import annotations

import importlib
import logging
import subprocess
import sys
from typing import Any

from .config import Task
from .utils import abspath

log = logging.getLogger("auto_task.runner")


def _run_python_script(task: Task) -> int:
    assert task.script is not None
    script_path = abspath(task.script)
    args = task.args or []
    cmd = [sys.executable, script_path, *args]
    log.info("Running python_script task '%s': %s", task.name, cmd)
    p = subprocess.run(cmd, cwd=abspath(task.cwd) if task.cwd else None)
    return int(p.returncode)


def _run_python_callable(task: Task) -> int:
    assert task.callable is not None
    module_name, func_name = task.callable.split(":", 1)
    log.info("Running python_callable task '%s': %s", task.name, task.callable)

    mod = importlib.import_module(module_name)
    fn = getattr(mod, func_name)

    args: list[Any] = task.callable_args or []
    kwargs: dict[str, Any] = task.callable_kwargs or {}

    result = fn(*args, **kwargs)
    if result is None:
        return 0
    if isinstance(result, int):
        return result
    log.info("Task '%s' returned %r (treated as success)", task.name, result)
    return 0


def _run_shell(task: Task) -> int:
    assert task.command is not None
    use_shell = True if task.shell is None else bool(task.shell)
    log.info("Running shell task '%s': %s", task.name, task.command)
    p = subprocess.run(task.command, shell=use_shell, cwd=abspath(task.cwd) if task.cwd else None)
    return int(p.returncode)


def run_task(task: Task) -> int:
    try:
        if task.type == "python_script":
            return _run_python_script(task)
        if task.type == "python_callable":
            return _run_python_callable(task)
        if task.type == "shell":
            return _run_shell(task)
        raise ValueError(f"Unknown task type: {task.type}")
    except Exception:
        log.exception("Task '%s' failed", task.name)
        return 1
